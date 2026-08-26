import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  createSession as apiCreate,
  listSessions as apiList,
  getSessionDetail as apiDetail,
  challenge as apiChallenge,
  completeSession as apiComplete,
  deleteSession as apiDelete,
} from '@/api/pathPlanning/debate'

export const useDebateStore = defineStore('debate', () => {
  // ─── State ───
  const sessions = ref([])          // 会话列表
  const currentSession = ref(null)  // 当前会话
  const messages = ref([])          // 当前会话的消息流
  const loading = ref(false)        // 发送中（等待 AI 追问）
  const listLoading = ref(false)
  const error = ref(null)

  // ─── Getters ───
  const stage = computed(() => currentSession.value?.stage || 'hypothesis')
  const isCompleted = computed(() => currentSession.value?.status === 'completed')
  /** 学生评判维度统计（评判逻辑记录的汇总） */
  const judgmentStats = computed(() => {
    const stat = {}
    messages.value
      .filter(m => m.role === 'student' && m.judgment_dimensions?.length)
      .forEach(m => m.judgment_dimensions.forEach(d => { stat[d] = (stat[d] || 0) + 1 }))
    return stat
  })

  // ─── Actions ───

  /** 加载会话列表 */
  async function loadSessions() {
    listLoading.value = true
    try {
      const res = await apiList(20)
      sessions.value = res.data.sessions || []
    } catch (e) {
      console.error('加载辩论会话列表失败:', e)
    } finally {
      listLoading.value = false
    }
  }

  /** 新建会话 */
  async function createSession(planSummary, planRecordId = null, groupName = '') {
    error.value = null
    try {
      const res = await apiCreate({
        plan_summary: planSummary,
        plan_record_id: planRecordId,
        group_name: groupName || null,
      })
      currentSession.value = res.data.session
      messages.value = []
      await loadSessions()
      // 加载 AI 开场白
      await loadSession(res.data.session.id)
      return res.data.session
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    }
  }

  /** 加载某个会话（回放） */
  async function loadSession(sessionId) {
    error.value = null
    try {
      const res = await apiDetail(sessionId)
      currentSession.value = res.data.session
      messages.value = res.data.messages || []
      return res.data.session
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    }
  }

  /**
   * 学生提交陈述 → AI 追问
   * @param {string} content 陈述内容
   * @param {object} opts { stage, judgment_dimensions, judgment_confidence }
   */
  async function submitStatement(content, opts = {}) {
    if (!currentSession.value || loading.value) return null
    loading.value = true
    error.value = null
    try {
      const res = await apiChallenge(currentSession.value.id, {
        content,
        stage: opts.stage || currentSession.value.stage,
        judgment_dimensions: opts.judgment_dimensions || [],
        judgment_confidence: opts.judgment_confidence ?? 50,
      })
      messages.value.push(res.data.student_message)
      messages.value.push(res.data.ai_message)
      currentSession.value.stage = res.data.stage
      currentSession.value.stage_name = res.data.stage === 'completed' ? '闭环完成' : ({ hypothesis: '假设提出', verify: '验证分析', rebut: '反驳交锋', rebuild: '重构优化' })[res.data.stage]
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 删除会话（连同消息）；若删除的是当前会话则清空右侧辩论区 */
  async function deleteSession(sessionId) {
    try {
      await apiDelete(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return false
    }
  }

  /** 结束会话 */
  async function completeSession(finalVerdict) {
    if (!currentSession.value) return null
    try {
      const res = await apiComplete(currentSession.value.id, finalVerdict)
      currentSession.value = res.data.session
      await loadSessions()
      return res.data.session
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    }
  }

  /** 重置到无会话状态 */
  function reset() {
    currentSession.value = null
    messages.value = []
    error.value = null
  }

  return {
    sessions, currentSession, messages, loading, listLoading, error,
    stage, isCompleted, judgmentStats,
    loadSessions, createSession, loadSession, submitStatement, deleteSession, completeSession, reset,
  }
})
