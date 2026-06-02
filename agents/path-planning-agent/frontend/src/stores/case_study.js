import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getCaseStudies,
  getCaseStudy,
  createCaseStudy,
  updateCaseStudy,
  deleteCaseStudy,
  setDefaultCase,
  initDefaultCase,
} from '../api/case_study'

export const useCaseStudyStore = defineStore('caseStudy', () => {
  // ─── State ───
  const cases = ref([])
  const loading = ref(false)
  const error = ref(null)
  const currentCase = ref(null)

  // ─── Getters ───
  const hasCases = computed(() => cases.value.length > 0)
  const defaultCase = computed(() => cases.value.find(c => c.is_default))

  // ─── Actions ───
  /** 加载所有案例 */
  async function loadCases() {
    loading.value = true
    error.value = null
    try {
      const res = await getCaseStudies()
      cases.value = res.data || []
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value = false
    }
  }

  /** 获取单个案例 */
  async function loadCase(caseId) {
    loading.value = true
    error.value = null
    try {
      const res = await getCaseStudy(caseId)
      currentCase.value = res.data
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 创建案例 */
  async function addCase(caseData) {
    loading.value = true
    error.value = null
    try {
      const res = await createCaseStudy(caseData)
      cases.value.unshift(res.data)
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 更新案例 */
  async function updateCase(caseId, caseData) {
    loading.value = true
    error.value = null
    try {
      const res = await updateCaseStudy(caseId, caseData)
      const index = cases.value.findIndex(c => c.id === caseId)
      if (index > -1) {
        cases.value[index] = res.data
      }
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 删除案例 */
  async function removeCase(caseId) {
    loading.value = true
    error.value = null
    try {
      await deleteCaseStudy(caseId)
      cases.value = cases.value.filter(c => c.id !== caseId)
      if (currentCase.value?.id === caseId) {
        currentCase.value = null
      }
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return false
    } finally {
      loading.value = false
    }
  }

  /** 设置为默认案例 */
  async function makeDefault(caseId) {
    loading.value = true
    error.value = null
    try {
      await setDefaultCase(caseId)
      cases.value.forEach(c => {
        c.is_default = (c.id === caseId)
      })
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return false
    } finally {
      loading.value = false
    }
  }

  /** 初始化默认案例 */
  async function initDefault() {
    try {
      const res = await initDefaultCase()
      await loadCases()
      return res.data
    } catch (e) {
      console.error('初始化默认案例失败:', e)
      return null
    }
  }

  /** 应用案例到当前数据 */
  async function applyCase(caseData) {
    const pointsStoreModule = await import('./points')
    const materialsStoreModule = await import('./materials')
    const pointsStore = pointsStoreModule.usePointsStore()
    const materialsStore = materialsStoreModule.useMaterialsStore()

    // 先清除旧的物资分配
    materialsStore.clearAssignments()

    // 应用配送中心和需求点（第一个参数是需求点列表，第二个参数是配送中心）
    await pointsStore.submitBatch(
      caseData.demand_points.map(d => ({
        name: d.name,
        longitude: d.longitude,
        latitude: d.latitude,
      })),
      {
        name: caseData.center_data.name,
        longitude: caseData.center_data.longitude,
        latitude: caseData.center_data.latitude,
      }
    )

    // 等待一下让模块二的watch触发完成
    await new Promise(resolve => setTimeout(resolve, 100))

    // 应用物资分配（在watch之后，避免被覆盖）
    if (caseData.material_data) {
      await materialsStore.loadAssignmentFromCase(caseData.material_data)
    }

    // 如果案例包含预设路线方案，加载到优化器（教学示范用）
    if (caseData.solution_data) {
      // 加载无人机选型
      if (caseData.solution_data.uav_selections) {
        const uavsStoreModule = await import('./uavs')
        const uavsStore = uavsStoreModule.useUavsStore()
        uavsStore.selections = caseData.solution_data.uav_selections
      }
      // 加载预设路线结果
      const optimizerStoreModule = await import('./optimizer')
      const optimizerStore = optimizerStoreModule.useOptimizerStore()

      // 从 trips 生成 GeoJSON 供地图展示
      const solution = caseData.solution_data.solution
      if (solution?.solution?.trips) {
        const depot = caseData.center_data
        const villageMap = {}
        for (const dp of caseData.demand_points) {
          villageMap[dp.name] = [dp.longitude, dp.latitude]
        }

        const features = []
        // 配送中心点
        features.push({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [depot.longitude, depot.latitude] },
          properties: { name: depot.name, feature_type: 'depot', marker_color: '#ff3d57' },
        })
        // 需求点
        for (const dp of caseData.demand_points) {
          features.push({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [dp.longitude, dp.latitude] },
            properties: { name: dp.name, feature_type: 'demand', marker_color: '#00e5ff' },
          })
        }
        // 航次路径
        const trips = solution.solution.trips
        for (let i = 0; i < trips.length; i++) {
          const trip = trips[i]
          const depotCoord = [depot.longitude, depot.latitude]

          // 构建路径坐标：depot → 各村庄 → depot
          let coords = [depotCoord]
          if (trip.villages && trip.villages.length > 0) {
            // 多村庄趟次
            for (const v of trip.villages) {
              coords.push([v.longitude, v.latitude])
            }
          } else {
            // 单村庄趟次
            const vCoords = villageMap[trip.village_name]
            if (!vCoords) continue
            coords.push(vCoords)
          }
          coords.push(depotCoord)

          features.push({
            type: 'Feature',
            geometry: { type: 'LineString', coordinates: coords },
            properties: {
              feature_type: 'route',
              trip_index: i,
              uav_id: trip.drone_id,
              distance: trip.total_distance,
              load: trip.load,
              village_name: trip.village_name,
            },
          })
        }

        solution.geojson = { type: 'FeatureCollection', features }
      }

      optimizerStore.result = solution
    }
  }

  return {
    cases,
    loading,
    error,
    currentCase,
    hasCases,
    defaultCase,
    loadCases,
    loadCase,
    addCase,
    updateCase,
    removeCase,
    makeDefault,
    initDefault,
    applyCase,
  }
})