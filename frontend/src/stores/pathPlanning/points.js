import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  fetchAllPoints,
  createPoint as apiCreate,
  batchCreatePoints as apiBatchCreate,
  updatePoint as apiUpdate,
  deletePoint as apiDelete,
  fetchDistanceMatrix as apiFetchMatrix,
  exportGeoJSON as apiExportGeoJSON,
} from '@/api/pathPlanning/points'

export const usePointsStore = defineStore('points', () => {
  // ─── State ───
  const points = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 距离矩阵
  const distLabels = ref([])
  const distMatrix = ref([])
  const distReturn = ref([])

  // 地图点击模式: null | 'center' | 'demand'
  const clickMode = ref(null)

  // 默认案例数据（渠洋镇应急物资配送案例）
  const DEFAULT_CENTER = { name: '渠洋村', longitude: 106.317264, latitude: 23.310533 }
  const DEFAULT_DEMANDS = [
    { name: '怀渠村', longitude: 106.285000, latitude: 23.345000 },
    { name: '塘麻村', longitude: 106.425000, latitude: 23.085000 },
    { name: '坡乐村', longitude: 106.380000, latitude: 23.075000 },
    { name: '东风村', longitude: 106.320150, latitude: 23.309040 },
    { name: '古桥村', longitude: 106.350000, latitude: 23.200000 },
    { name: '新和村', longitude: 106.335000, latitude: 23.295000 },
    { name: '怀书村', longitude: 106.278670, latitude: 23.339030 },
    { name: '雅力村', longitude: 106.380000, latitude: 23.250000 },
  ]

  // ─── Getters ───
  const center = computed(() =>
    points.value.find((p) => p.point_type === 'center') || null
  )

  const demands = computed(() =>
    points.value.filter((p) => p.point_type === 'demand')
  )

  const geojson = computed(() => ({
    type: 'FeatureCollection',
    features: points.value.map((p) => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [p.longitude, p.latitude],
      },
      properties: {
        id: p.id,
        name: p.name,
        type: p.point_type,
        longitude: p.longitude,
        latitude: p.latitude,
      },
    })),
  }))

  // ─── Actions ───
  async function setCenter(data) {
    loading.value = true
    error.value = null
    try {
      // 删除旧的配送中心
      const oldCenter = center.value
      if (oldCenter && oldCenter.id) {
        await apiDelete(oldCenter.id)
        points.value = points.value.filter((p) => p.id !== oldCenter.id)
      }
      // 创建新的
      const res = await apiCreate({ ...data, point_type: 'center' })
      points.value.push(res.data)
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function addDemand(data) {
    loading.value = true
    error.value = null
    try {
      const res = await apiCreate({ ...data, point_type: 'demand' })
      points.value.push(res.data)
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadPoints() {
    loading.value = true
    error.value = null
    try {
      const res = await fetchAllPoints()
      points.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value = false
    }
  }

  async function loadDefaultCase() {
    const caseStudyModule = await import('./case_study')
    const caseStore = caseStudyModule.useCaseStudyStore()
    
    await caseStore.loadCases()
    
    const defaultCase = caseStore.cases.find(c => c.is_default) || caseStore.cases[0]
    
    if (defaultCase) {
      return submitBatch(
        defaultCase.demand_points.map(d => ({
          name: d.name,
          longitude: d.longitude,
          latitude: d.latitude,
        })),
        {
          name: defaultCase.center_data.name,
          longitude: defaultCase.center_data.longitude,
          latitude: defaultCase.center_data.latitude,
        }
      )
    } else {
      return submitBatch(DEFAULT_DEMANDS.map((d) => ({
        name: d.name,
        longitude: d.longitude,
        latitude: d.latitude,
      })))
    }
  }

  function parseInputText(text) {
    const lines = text.trim().split('\n').filter((l) => l.trim())
    const parsed = []
    for (const line of lines) {
      const parts = line.trim().split(/\s+/)
      if (parts.length >= 3) {
        const name = parts[0]
        const lng = parseFloat(parts[1])
        const lat = parseFloat(parts[2])
        if (!isNaN(lng) && !isNaN(lat)) {
          parsed.push({ name, longitude: lng, latitude: lat })
        }
      }
    }
    return parsed
  }

  async function submitBatch(villageData, centerData = null) {
    loading.value = true
    error.value = null
    try {
      const center = centerData || DEFAULT_CENTER
      const batchData = [
        {
          name: center.name,
          point_type: 'center',
          longitude: center.longitude,
          latitude: center.latitude,
        },
        ...villageData.map((d) => ({
          name: d.name,
          point_type: 'demand',
          longitude: d.longitude,
          latitude: d.latitude,
        })),
      ]
      const res = await apiBatchCreate(batchData)
      points.value = res.data
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function removePoint(id) {
    loading.value = true
    error.value = null
    try {
      await apiDelete(id)
      points.value = points.value.filter((p) => p.id !== id)
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updatePoint(id, data) {
    loading.value = true
    error.value = null
    try {
      const res = await apiUpdate(id, data)
      const idx = points.value.findIndex((p) => p.id === id)
      if (idx !== -1) {
        points.value[idx] = res.data
      }
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadDistanceMatrix() {
    loading.value = true
    error.value = null
    try {
      const res = await apiFetchMatrix()
      distLabels.value = res.data.labels
      distMatrix.value = res.data.matrix
      distReturn.value = res.data.return_distances
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function saveGeoJSON() {
    loading.value = true
    error.value = null
    try {
      const res = await apiExportGeoJSON()
      const blob = new Blob([JSON.stringify(res.data, null, 2)], {
        type: 'application/geo+json',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `delivery_points_${Date.now()}.geojson`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function setClickMode(mode) {
    clickMode.value = mode
  }

  function handleMapClick(lat, lng) {
    if (clickMode.value === 'center') {
      setCenter({ name: '配送中心', longitude: lng, latitude: lat })
      clickMode.value = null
    } else if (clickMode.value === 'demand') {
      const idx = demands.value.length + 1
      addDemand({ name: `需求点${idx}`, longitude: lng, latitude: lat })
    }
  }

  return {
    points,
    loading,
    error,
    distLabels,
    distMatrix,
    distReturn,
    center,
    demands,
    geojson,
    DEFAULT_CENTER,
    DEFAULT_DEMANDS,
    loadPoints,
    setCenter,
    addDemand,
    loadDefaultCase,
    parseInputText,
    submitBatch,
    removePoint,
    updatePoint,
    loadDistanceMatrix,
    saveGeoJSON,
    clickMode,
    setClickMode,
    handleMapClick,
  }
})
