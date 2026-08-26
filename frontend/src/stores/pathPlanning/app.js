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
    { id: 12, label: '反向质询', icon: '🎭' },
    { id: 6, label: '方案优出', icon: '📊' },
    { id: 10, label: '方案审阅', icon: '👨‍🏫' },
    { id: 7, label: '案例管理', icon: '📚' },
    { id: 8, label: '系统设置', icon: '⚙' },
    { id: 11, label: '方案看板', icon: '🖼' },
  ]

  // ─── 向导模式：四步教学流程 + 管理工具收纳 ───
  const wizardSteps = [
    { id: 1, title: '案例与配送点', icon: '📍', desc: '加载灾情案例，配置配送中心与需求点', modules: [1] },
    { id: 2, title: '物资与选型', icon: '📦', desc: '配置物资需求，完成无人机选型', modules: [2, 3] },
    { id: 3, title: '规划与诊断', icon: '🗺', desc: '蚁群算法路径规划，规则+AI双诊断', modules: [4, 9, 5] },
    { id: 4, title: '辩论与优出', icon: '🎭', desc: '反向质询辩论，生成最优方案报告', modules: [12, 6, 10] },
  ]

  const adminTools = [
    { id: 7, label: '案例管理', icon: '📚' },
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
  }

  function gotoStep(stepId) {
    activeAdmin.value = null
    activeStep.value = stepId
    activeModule.value = wizardSteps.find(s => s.id === stepId)?.modules[0] || 1
  }

  function openAdmin(id) {
    activeAdmin.value = id
    activeModule.value = id
  }

  function backToWizard() {
    activeAdmin.value = null
    gotoStep(activeStep.value || 1)
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

  return {
    activeModule, modules, setModule,
    wizardSteps, adminTools, activeStep, activeAdmin,
    stepStatus, gotoStep, openAdmin, backToWizard,
  }
})
