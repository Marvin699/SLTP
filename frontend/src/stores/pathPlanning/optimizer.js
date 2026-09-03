import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  runOptimizer as apiRun,
  getDefaultParams as apiDefaults,
  exportExcel as apiExportExcel,
  getOptimizationHistory as apiHistory,
  getOptimizationDetail as apiDetail,
  deleteOptimization as apiDelete,
  manualAdjust as apiManual,
} from '@/api/pathPlanning/optimizer'
import { usePointsStore } from './points'
import { useMaterialsStore } from './materials'
import { useUavsStore } from './uavs'

const PRIORITY_MAP = { 1: 'urgent', 2: 'high', 3: 'medium', 4: 'low', 5: 'normal' }

export const useOptimizerStore = defineStore('optimizer', () => {
  // ─── State ───
  const loading = ref(false)
  const error = ref(null)
  const result = ref(null)
  const acoParams = ref(null)
  const defaultParams = ref(null)
  const history = ref([])
  const historyLoading = ref(false)
  const selectedDroneId = ref(null) // 当前选中查看路线的无人机ID
  const regenHints = ref(null)      // 合规核验回填的提示（{hints:[], params:{}}），Module4 展示后清除
  const originalResult = ref(null)  // ACO 算法原始结果快照（手动调序后可回退）
  const manualActive = ref(false)   // 当前结果是否为手动调序版本

  // ─── Getters ───
  const summary = computed(() => result.value?.summary || {})
  const routeTable = computed(() => result.value?.route_table || [])
  const villageTable = computed(() => result.value?.village_table || [])
  const droneTable = computed(() => result.value?.drone_table || [])
  const geojson = computed(() => result.value?.geojson || null)
  const elapsed = computed(() => result.value?.elapsed_seconds || 0)

  // 兼容旧 getter
  const routes = computed(() => result.value?.solution?.trips || [])
  const totalDistance = computed(() => summary.value?.total_distance || 0)
  const totalTime = computed(() => summary.value?.total_time || 0)
  const totalTrips = computed(() => summary.value?.total_trips || 0)
  const droneCount = computed(() => summary.value?.drone_count || 0)
  const villageCount = computed(() => summary.value?.village_count || 0)
  const allCovered = computed(() => summary.value?.feasible || false)

  // 可行性校验
  const feasibility = computed(() => result.value?.feasibility || null)
  const feasible = computed(() => feasibility.value?.feasible ?? false)
  const feasibleText = computed(() => feasibility.value?.feasible_text || '')
  const feasibilityIssues = computed(() => feasibility.value?.issues || [])
  const feasibilityWarnings = computed(() => feasibility.value?.warnings || [])
  const demandCoverage = computed(() => feasibility.value?.demand_coverage || {})
  const tripChecks = computed(() => feasibility.value?.trip_checks || {})

  // ─── Actions ───

  /** 从 stores 构建 task JSON */
  function buildTaskJson() {
    const ptsStore = usePointsStore()
    const matStore = useMaterialsStore()
    const uavStore = useUavsStore()

    if (!ptsStore.center) throw new Error('请先设置配送中心')
    if (ptsStore.demands.length === 0) throw new Error('请先添加需求点')
    if (uavStore.selections.length === 0) throw new Error('请先选择无人机')

    const depot = {
      id: ptsStore.center.id || 'depot',
      name: ptsStore.center.name,
      longitude: ptsStore.center.longitude,
      latitude: ptsStore.center.latitude,
    }

    const demand_points = ptsStore.demands.map((pt) => {
      const assignment = matStore.getAssignment(pt.id)
      const materials = []
      if (assignment?.items) {
        for (const item of assignment.items) {
          const w = item.subtotal ?? (item.unit_weight ?? item.weight ?? 0) * (item.qty ?? item.quantity ?? 1)
          materials.push({
            type: item.name || item.category || '物资',
            weight: w || 0,
          })
        }
      }
      if (materials.length === 0 && assignment?.total_weight) {
        materials.push({ type: '物资', weight: assignment.total_weight })
      }
      return {
        id: pt.id,
        name: pt.name,
        longitude: pt.longitude,
        latitude: pt.latitude,
        priority: PRIORITY_MAP[assignment?.priority] || 'medium',
        delivery_mode: assignment?.delivery_mode || 'optional',
        materials,
      }
    })

    const distance_matrix = ptsStore.distMatrix.length > 0 ? ptsStore.distMatrix : []

    const uavs = []
    for (const sel of uavStore.selectedDetails) {
      const m = sel.model
      console.log('[Optimizer] UAV Model:', m.id, m.model, m.range_points)
      for (let i = 0; i < sel.quantity; i++) {
        uavs.push({
          id: `${m.id}-${i + 1}`,
          name: m.model || m.name,
          max_payload: m.max_payload,
          max_range: m.range_km || m.max_range,
          battery_capacity: 100,
          max_speed: m.max_speed || 60,
          range_points: m.range_points || [],
        })
      }
    }
    console.log('[Optimizer] Task JSON UAVs:', uavs)

    return { depot, demand_points, distance_matrix, uavs }
  }

  /** 获取默认参数 */
  async function fetchDefaultParams() {
    try {
      const task = buildTaskJson()
      const res = await apiDefaults(task)
      defaultParams.value = res.data
      acoParams.value = { ...res.data }
      return res.data
    } catch (e) {
      error.value = e.message
      return null
    }
  }

  /** 运行优化 */
  async function runOptimization(customParams = null) {
    loading.value = true
    error.value = null
    result.value = null
    try {
      const task = buildTaskJson()
      const params = customParams || acoParams.value
      const res = await apiRun(task, params)
      result.value = res.data
      // 保存算法原始结果快照，供手动调序后回退
      originalResult.value = res.data
      manualActive.value = false
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 手动调整某航次的配送顺序并重算
   * @param {number} tripId 目标航次 id（solution.trips 中的 trip_id）
   * @param {number[]} newRoute 重排后的节点序列（0 开头结尾）
   */
  async function adjustTripOrder(tripId, newRoute) {
    const trips = (result.value?.solution?.trips || []).map((t) =>
      t.trip_id === tripId ? { ...t, route: newRoute } : t
    )
    loading.value = true
    error.value = null
    try {
      const task = buildTaskJson()
      const res = await apiManual(task, trips)
      result.value = res.data
      manualActive.value = true
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 回退到 ACO 算法原始结果 */
  function revertToAlgorithm() {
    if (originalResult.value) {
      result.value = originalResult.value
      manualActive.value = false
    }
  }

  /** 导出 Excel */
  async function downloadExcel() {
    try {
      const task = buildTaskJson()
      const params = acoParams.value
      const res = await apiExportExcel(task, params)
      const blob = new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `运输方案_${Date.now()}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      error.value = e.message
    }
  }

  /** 重置结果 */
  function resetResult() {
    result.value = null
    error.value = null
    originalResult.value = null
    manualActive.value = false
  }

  /** 加载历史记录 */
  async function loadHistory(limit = 20) {
    historyLoading.value = true
    try {
      const res = await apiHistory(limit)
      history.value = res.data.records || []
      return history.value
    } catch (e) {
      console.error('加载优化历史失败:', e)
      return []
    } finally {
      historyLoading.value = false
    }
  }

  /** 查看历史记录详情 */
  async function viewHistoryDetail(recordId) {
    try {
      const res = await apiDetail(recordId)
      const data = res.data
      if (data.solution_data) {
        result.value = data.solution_data
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

  /** 设置选中的无人机ID（用于地图高亮） */
  function setSelectedDroneId(droneId) {
    selectedDroneId.value = droneId
  }

  /** 清除核验回填提示 */
  function clearRegenHints() {
    regenHints.value = null
  }

  return {
    loading,
    error,
    result,
    acoParams,
    defaultParams,
    history,
    historyLoading,
    selectedDroneId,
    regenHints,
    manualActive,
    summary,
    routeTable,
    villageTable,
    droneTable,
    geojson,
    elapsed,
    routes,
    totalDistance,
    totalTime,
    totalTrips,
    droneCount,
    villageCount,
    allCovered,
    feasibility,
    feasible,
    feasibleText,
    feasibilityIssues,
    feasibilityWarnings,
    demandCoverage,
    tripChecks,
    buildTaskJson,
    fetchDefaultParams,
    runOptimization,
    adjustTripOrder,
    revertToAlgorithm,
    downloadExcel,
    resetResult,
    loadHistory,
    viewHistoryDetail,
    deleteRecord,
    setSelectedDroneId,
    clearRegenHints,
  }
})
