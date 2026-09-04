import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usePointsStore } from './points'
import { useMaterialsStore } from './materials'
import { useUavsStore } from './uavs'
import { useOptimizerStore } from './optimizer'

export const useAppStore = defineStore('app', () => {
  const activeModule = ref(1)

  // ─── 旧模块清单（保留：Modules 内部仍按 id 渲染） ───
  const modules = [
    { id: 1, label: '配送点设置', icon: '📍' },
    { id: 2, label: '物资需求', icon: '📦' },
    { id: 3, label: '无人机选型', icon: '🚁' },
    { id: 4, label: '路径规划', icon: '🗺' },
    { id: 9, label: '航线详情', icon: '🛰️' },
    { id: 5, label: '方案诊断', icon: '🔍' },
    { id: 13, label: '合规核验', icon: '✅' },
    { id: 12, label: '反向质询', icon: '🎭' },
    { id: 6, label: '方案优出', icon: '📊' },
    { id: 10, label: '方案审阅', icon: '👨‍🏫' },
    { id: 7, label: '信息管理', icon: '🗂' },
    { id: 8, label: '系统设置', icon: '⚙' },
    { id: 11, label: '方案看板', icon: '🖼' },
  ]

  // ─── 向导模式：四步教学流程 + 管理工具收纳 ───
  const wizardSteps = [
    { id: 1, title: '案例与配送点', icon: '📍', desc: '加载灾情案例，配置配送中心与需求点', modules: [1] },
    { id: 2, title: '物资与选型', icon: '📦', desc: '配置物资需求，完成无人机选型', modules: [2, 3] },
    { id: 3, title: '规划与诊断', icon: '🗺', desc: '蚁群算法路径规划，诊断与合规核验', modules: [4, 9, 5, 13] },
    { id: 4, title: '辩论与优出', icon: '🎭', desc: '反向质询辩论，生成最优方案报告', modules: [12, 6, 10, 14] },
  ]

  const adminTools = [
    { id: 7, label: '信息管理', icon: '🗂' },
    { id: 8, label: '系统设置', icon: '⚙' },
    { id: 11, label: '方案看板', icon: '🖼' },
  ]

  // 当前展开的向导步骤（默认 1）
  const activeStep = ref(1)
  // 是否处于管理工具页面（null = 向导流程）
  const activeAdmin = ref(null)

  function setModule(id) {
    // 清除管理工具态，回到向导流程并定位到对应步骤
    activeAdmin.value = null
    const step = wizardSteps.find(s => s.modules.includes(id))
    // 教学闸口：未提交前序步骤时禁止跳入后续步骤
    if (step && stepLocked(step.id)) return false
    if (step) {
      activeStep.value = step.id
      activeModule.value = step.modules.includes(id) ? id : step.modules[0]
      // 该步包含多个模块时，切到用户点的那一个
      activeModule.value = id
    } else {
      // 管理工具
      activeAdmin.value = id
      activeModule.value = id
    }
    return true
  }

  function gotoStep(stepId) {
    if (stepLocked(stepId)) return false
    activeAdmin.value = null
    activeStep.value = stepId
    activeModule.value = wizardSteps.find(s => s.id === stepId)?.modules[0] || 1
    return true
  }

  function openAdmin(id) {
    activeAdmin.value = id
    activeModule.value = id
  }

  function backToWizard() {
    activeAdmin.value = null
    gotoStep(activeStep.value || 1)
  }

  // ─── 灾情参数卡（T1）：推算物资需求的教学输入，localStorage 持久化 ───
  const DISASTER_KEY = 'sltp_disaster_params'
  const _loadDisaster = () => {
    try { return JSON.parse(localStorage.getItem(DISASTER_KEY)) || {} } catch { return {} }
  }
  const disasterParams = ref({
    population: null,      // 受灾人口（人）
    coefficient: 1.0,      // 人均日消耗（kg/人·日）
    duration: 3,           // 保障时长（天）
    coldShelfHours: 24,    // 冷链物资时限（小时）
    windSpeed: 3,          // 风速（m/s）
    precipitation: 0,      // 降水（mm/h）
    ..._loadDisaster(),
  })

  /** 气象是否超限（教学约束：风速 >8 m/s 或降水 >10 mm/h 建议停飞） */
  const weatherExceeded = computed(() => {
    const d = disasterParams.value
    return (d.windSpeed || 0) > 8 || (d.precipitation || 0) > 10
  })

  /** 灾情总物资需求（kg）= 人口 × 人均日消耗 × 保障时长 */
  const totalDemandKg = computed(() => {
    const d = disasterParams.value
    if (!d.population || !d.coefficient || !d.duration) return 0
    return d.population * d.coefficient * d.duration
  })

  function saveDisasterParams() {
    localStorage.setItem(DISASTER_KEY, JSON.stringify(disasterParams.value))
  }

  // ─── 各步骤完成状态（依据业务数据自动判定） ───
  const stepStatus = computed(() => {
    const pts = usePointsStore()
    const mat = useMaterialsStore()
    const uav = useUavsStore()
    const opt = useOptimizerStore()
    return {
      // 步骤1完成：有配送中心 + 有需求点
      1: !!pts.center && pts.demands.length > 0,
      // 步骤2完成：物资已分配 + 无人机已选型
      2: mat.assignedCount > 0 && uav.totalCount > 0,
      // 步骤3完成：已有路径规划结果
      3: !!opt.result,
      // 步骤4完成：已有规划历史（生成过方案）
      4: opt.history?.length > 0,
    }
  })

  // ─── 步骤提交闸口（提交本步后才能进入下一步；案例切换时重置） ───
  const STEP_SUBMIT_KEY = 'sltp_step_submitted'
  const _loadSubmits = () => {
    try { return JSON.parse(localStorage.getItem(STEP_SUBMIT_KEY)) || {} } catch { return {} }
  }
  const stepSubmitted = ref({ ..._loadSubmits() })

  function _persistSubmits() {
    localStorage.setItem(STEP_SUBMIT_KEY, JSON.stringify(stepSubmitted.value))
  }

  /** 重置提交记录（切换案例时调用） */
  function resetSubmissions() {
    stepSubmitted.value = {}
    _persistSubmits()
  }

  /** 步骤是否被锁定：前序步骤存在未提交的则锁 */
  function stepLocked(stepId) {
    const idx = wizardSteps.findIndex(s => s.id === stepId)
    if (idx <= 0) return false
    return wizardSteps.slice(0, idx).some(s => !stepSubmitted.value[s.id])
  }

  const STEP_BLOCK_MSGS = {
    1: '请先配置配送中心与需求点，再提交本步',
    2: '请先完成物资分配并选择无人机，再提交本步',
    3: '请先完成路径规划，再提交本步',
    4: '请先生成方案报告，再提交本步',
  }

  /** 提交当前步骤：校验通过则标记已提交并自动进入下一步 */
  function submitStep(stepId) {
    if (!stepStatus.value[stepId]) {
      alert(STEP_BLOCK_MSGS[stepId] || '当前步骤尚未完成')
      return false
    }
    stepSubmitted.value = { ...stepSubmitted.value, [stepId]: true }
    _persistSubmits()
    // 自动进入下一步
    const idx = wizardSteps.findIndex(s => s.id === stepId)
    const next = wizardSteps[idx + 1]
    if (next) gotoStep(next.id)
    return true
  }

  return {
    activeModule, modules, setModule,
    wizardSteps, adminTools, activeStep, activeAdmin,
    stepStatus, gotoStep, openAdmin, backToWizard,
    disasterParams, totalDemandKg, saveDisasterParams, weatherExceeded,
    stepSubmitted, submitStep, stepLocked, resetSubmissions,
  }
})
