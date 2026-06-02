import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  runDiagnosis as apiRun,
  runRuleDiagnosis as apiRule,
  runAiDiagnosis as apiAi,
  getDiagnosisHistory as apiHistory,
  getDiagnosisDetail as apiDetail,
  deleteDiagnosis as apiDelete,
} from '@/api/pathPlanning/diagnosis'
import { useOptimizerStore } from './optimizer'

export const useDiagnosisStore = defineStore('diagnosis', () => {
  // ─── State ───
  const loading = ref(false)
  const error = ref(null)
  const result = ref(null)
  const history = ref([])
  const activeTab = ref('rule') // 'rule' | 'ai'
  const diagnosisMode = ref(null) // 'rule' | 'ai' | 'both'

  // ─── Getters ───
  const feasible = computed(() => result.value?.feasible ?? false)
  const score = computed(() => result.value?.score ?? 0)
  const issues = computed(() => result.value?.issues ?? [])
  const warnings = computed(() => result.value?.warnings ?? [])
  const suggestions = computed(() => result.value?.suggestions ?? [])
  const ruleReport = computed(() => result.value?.rule_report ?? {})
  const aiReport = computed(() => result.value?.ai_report ?? '')
  const taskSummary = computed(() => result.value?.task_summary ?? {})
  
  // 四维评分
  const fourDimensionalScores = computed(() => {
    const scores = result.value?.four_dimensional_scores ?? {}
    return {
      safety: scores.safety ?? 0,
      timeliness: scores.timeliness ?? 0,
      economy: scores.economy ?? 0,
      feasibility: scores.feasibility ?? 0
    }
  })

  const hasResult = computed(() => !!result.value)
  const hasIssues = computed(() => issues.value.length > 0)
  const hasWarnings = computed(() => warnings.value.length > 0)
  const hasSuggestions = computed(() => suggestions.value.length > 0)
  
  // 是否有规则诊断结果
  const hasRuleReport = computed(() => !!result.value?.rule_report)
  // 是否有AI诊断结果
  const hasAiReport = computed(() => !!result.value?.ai_report)

  // ─── Actions ───
  async function runDiagnosis(mode = 'both') {
    loading.value = true
    error.value = null

    try {
      const optStore = useOptimizerStore()
      
      if (!optStore.result) {
        throw new Error('请先运行路径规划')
      }

      const task = optStore.buildTaskJson()
      const solution = optStore.result

      let res
      if (mode === 'rule') {
        res = await apiRule(task, solution)
      } else if (mode === 'ai') {
        res = await apiAi(task, solution)
      } else {
        res = await apiRun(task, solution)
      }
      
      console.log('[Diagnosis] API Response:', res.data)
      console.log('[Diagnosis] Four Dimensional Scores:', res.data.four_dimensional_scores)
      
      result.value = res.data
      diagnosisMode.value = mode
      // 根据诊断模式自动切换到对应 tab
      activeTab.value = mode === 'ai' ? 'ai' : 'rule'

      await loadHistory()
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function runRuleDiagnosis() {
    return await runDiagnosis('rule')
  }
  
  async function runAiDiagnosis() {
    return await runDiagnosis('ai')
  }

  async function loadHistory() {
    try {
      const res = await apiHistory(10)
      history.value = res.data.records || []
    } catch (e) {
      console.error('加载诊断历史失败:', e)
    }
  }

  function resetResult() {
    result.value = null
    error.value = null
    activeTab.value = 'rule'
  }

  function setActiveTab(tab) {
    activeTab.value = tab
  }

  /** 查看历史记录详情 */
  async function viewHistoryDetail(recordId) {
    try {
      const res = await apiDetail(recordId)
      const data = res.data
      // 解析报告数据
      if (data.report) {
        try {
          const report = typeof data.report === 'string' ? JSON.parse(data.report.replace(/'/g, '"')) : data.report
          // 确保四维评分存在
          if (!report.four_dimensional_scores) {
            report.four_dimensional_scores = {
              safety: report.safety_score ?? report.rule_report?.four_dimensional_scores?.safety ?? 0,
              timeliness: report.timeliness_score ?? report.rule_report?.four_dimensional_scores?.timeliness ?? 0,
              economy: report.economy_score ?? report.rule_report?.four_dimensional_scores?.economy ?? 0,
              feasibility: report.feasibility_score ?? report.rule_report?.four_dimensional_scores?.feasibility ?? 0,
            }
          }
          result.value = report
          diagnosisMode.value = report.diagnosis_mode || 'rule'
        } catch (e) {
          // 如果解析失败，创建一个基本的结果对象
          result.value = {
            feasible: data.issues_count === 0,
            score: data.score,
            issues: [],
            warnings: [],
            suggestions: [],
            rule_report: {},
            ai_report: data.report,
            task_summary: {},
            four_dimensional_scores: {
              safety: data.safety_score ?? 0,
              timeliness: data.timeliness_score ?? 0,
              economy: data.economy_score ?? 0,
              feasibility: data.feasibility_score ?? 0
            },
            diagnosis_mode: data.diagnosis_mode || 'rule'
          }
        }
      } else {
        // 如果没有report字段，使用数据库中的数据
        result.value = {
          feasible: data.issues_count === 0,
          score: data.score,
          issues: [],
          warnings: [],
          suggestions: [],
          rule_report: {},
          ai_report: '',
          task_summary: {},
          four_dimensional_scores: {
            safety: data.safety_score ?? 0,
            timeliness: data.timeliness_score ?? 0,
            economy: data.economy_score ?? 0,
            feasibility: data.feasibility_score ?? 0
          },
          diagnosis_mode: data.diagnosis_mode || 'rule'
        }
      }
      return data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    }
  }

  /** 删除历史记录 */
  async function deleteRecord(recordId) {
    try {
      await apiDelete(recordId)
      // 从本地列表中移除
      history.value = history.value.filter(r => r.id !== recordId)
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return false
    }
  }

  return {
    loading,
    error,
    result,
    history,
    activeTab,
    diagnosisMode,
    feasible,
    score,
    issues,
    warnings,
    suggestions,
    ruleReport,
    aiReport,
    taskSummary,
    fourDimensionalScores,
    hasResult,
    hasIssues,
    hasWarnings,
    hasSuggestions,
    hasRuleReport,
    hasAiReport,
    runDiagnosis,
    runRuleDiagnosis,
    runAiDiagnosis,
    loadHistory,
    resetResult,
    setActiveTab,
    viewHistoryDetail,
    deleteRecord,
  }
})
