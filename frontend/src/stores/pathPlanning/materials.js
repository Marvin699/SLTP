import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usePointsStore } from './points'
import {
  fetchCategories as apiLoadCategories,
  saveAssignment as apiSaveAssignment,
  fetchDefaultCase,
  loadSavedAssignments,
} from '@/api/pathPlanning/materials'

export const useMaterialsStore = defineStore('materials', () => {
  const categories = ref([])
  const assignments = ref({})
  const loading = ref(false)
  const error = ref(null)

  const totalWeight = computed(() => {
    let sum = 0
    for (const a of Object.values(assignments.value)) {
      sum += a.total_weight || 0
    }
    return sum
  })

  const highestPriority = computed(() => {
    let min = 5
    for (const a of Object.values(assignments.value)) {
      if (a.priority < min) min = a.priority
    }
    return min
  })

  const assignedCount = computed(() => Object.keys(assignments.value).length)

  async function loadCategories() {
    loading.value = true
    error.value = null
    try {
      const res = await apiLoadCategories()
      categories.value = res.data
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function loadFromDb() {
    try {
      const res = await loadSavedAssignments()
      if (res.data) {
        // 规范化 risk_warnings 字段（后端存的是字符串，前端需要数组）
        for (const key of Object.keys(res.data)) {
          const a = res.data[key]
          if (typeof a.risk_warnings === 'string') {
            a.risk_warnings = a.risk_warnings ? a.risk_warnings.split('；').filter(Boolean) : []
          }
        }
        assignments.value = { ...res.data }
      }
    } catch {
      assignments.value = {}
    }
  }

  async function assignMaterials(pointId, categoryIds) {
    const pointsStore = usePointsStore()
    const pt = pointsStore.demands.find((p) => p.id === pointId)
    if (!pt) return

    const selectedCategories = categories.value.filter((c) => categoryIds.includes(c.id))
    const items = []
    let totalWeight = 0

    for (const cat of selectedCategories) {
      for (const item of cat.items) {
        items.push({
          name: item.name,
          unit: item.unit,
          unit_weight: item.weight,
          qty: 1,
          subtotal: item.weight,
          category_id: cat.id,
        })
        totalWeight += item.weight
      }
    }

    assignments.value[pointId] = {
      point_id: pointId,
      point_name: pt.name,
      category_ids: categoryIds,
      custom_items: items,
      total_weight: totalWeight,
      priority: 3,
      delivery_mode: 'optional',
      special_requirements: '',
      risk_warnings: [],
      supply_types: ['常规'],
      items,
    }

    await _saveToDb(pointId)
  }

  function toggleCategory(pointId, categoryId) {
    const assignment = assignments.value[pointId]
    if (!assignment) {
      const pointsStore = usePointsStore()
      const pt = pointsStore.demands.find(p => p.id === pointId)
      const cat = categories.value.find(c => c.id === categoryId)
      const items = cat ? cat.items.map(item => ({
        name: item.name,
        unit: 'kg',
        unit_weight: item.unit_weight,
        qty: item.qty || 1,
        subtotal: item.unit_weight * (item.qty || 1),
        category_id: categoryId,
      })) : []
      const totalWeight = items.reduce((s, i) => s + i.subtotal, 0)
      assignments.value[pointId] = {
        point_id: pointId,
        point_name: pt ? pt.name : '',
        category_ids: [categoryId],
        custom_items: items,
        total_weight: totalWeight,
        priority: 3,
        special_requirements: '',
        risk_warnings: [],
        supply_types: ['常规'],
        items,
      }
    } else {
      const idx = assignment.category_ids.indexOf(categoryId)
      if (idx > -1) {
        assignment.category_ids.splice(idx, 1)
        assignment.items = assignment.items.filter(i => i.category_id !== categoryId)
        assignment.custom_items = assignment.items
      } else {
        assignment.category_ids.push(categoryId)
        const cat = categories.value.find(c => c.id === categoryId)
        if (cat) {
          for (const item of cat.items) {
            assignment.items.push({
              name: item.name,
              unit: 'kg',
              unit_weight: item.unit_weight,
              qty: item.qty || 1,
              subtotal: item.unit_weight * (item.qty || 1),
              category_id: categoryId,
            })
          }
          assignment.custom_items = assignment.items
        }
      }
      _recalculateTotal(pointId)
    }
  }

  function updateItem(pointId, itemIndex, field, value) {
    const assignment = assignments.value[pointId]
    if (assignment && assignment.items[itemIndex]) {
      assignment.items[itemIndex][field] = value
      if (field === 'qty' || field === 'unit_weight') {
        assignment.items[itemIndex].subtotal = (assignment.items[itemIndex].unit_weight || 0) * (assignment.items[itemIndex].qty || 0)
        _recalculateTotal(pointId)
      }
    }
  }

  function addItem(pointId) {
    const assignment = assignments.value[pointId]
    if (assignment) {
      assignment.items.push({
        name: '',
        unit: 'kg',
        unit_weight: 0,
        qty: 1,
        subtotal: 0,
        category_id: null,
      })
      assignment.custom_items = assignment.items
    }
  }

  function removeItem(pointId, itemIndex) {
    const assignment = assignments.value[pointId]
    if (assignment && assignment.items[itemIndex]) {
      assignment.items.splice(itemIndex, 1)
      assignment.custom_items = assignment.items
      _recalculateTotal(pointId)
    }
  }

  function _recalculateTotal(pointId) {
    const assignment = assignments.value[pointId]
    if (assignment) {
      assignment.total_weight = assignment.items.reduce((sum, item) => {
        return sum + ((item.unit_weight || 0) * (item.qty || 0))
      }, 0)
    }
  }

  function getAssignment(pointId) {
    return assignments.value[pointId] || null
  }

  function isCategorySelected(pointId, categoryId) {
    const assignment = assignments.value[pointId]
    return assignment && assignment.category_ids && assignment.category_ids.includes(categoryId)
  }

  async function _saveToDb(pointId) {
    const assignment = assignments.value[pointId]
    if (assignment) {
      try {
        await apiSaveAssignment({
          point_id: pointId,
          point_name: assignment.point_name || '',
          category_ids: assignment.category_ids,
          items: assignment.items,
          total_weight: assignment.total_weight,
          priority: assignment.priority,
          special_requirements: assignment.special_requirements || '',
          risk_warnings: Array.isArray(assignment.risk_warnings) ? assignment.risk_warnings.join('；') : (assignment.risk_warnings || ''),
          supply_types: Array.isArray(assignment.supply_types) ? assignment.supply_types : ['常规'],
        })
      } catch (e) {
        console.error('保存分配失败:', e)
      }
    }
  }

  async function updatePriority(pointId, priority) {
    const assignment = assignments.value[pointId]
    if (assignment) {
      assignment.priority = priority
      await _saveToDb(pointId)
    }
  }

  async function updateDeliveryMode(pointId, mode) {
    const assignment = assignments.value[pointId]
    if (assignment) {
      assignment.supply_types = mode
      await _saveToDb(pointId)
    }
  }

  function clearAssignments() {
    assignments.value = {}
  }

  async function loadDefaultCase() {
    loading.value = true
    error.value = null
    try {
      const res = await fetchDefaultCase()
      const result = res.data
      await loadAssignmentFromCase(result)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  // supply_type 英文 key → 类别 ID 映射（与后端 5 大类别一致）
  const SUPPLY_TYPE_TO_CATEGORY = {
    repair: 'repair',
    life: 'life',
    medical: 'medical',
    cold: 'cold',
    settle: 'settle',
    // 兼容旧数据
    medicine: 'medical',
    food: 'life',
    water: 'life',
    daily: 'life',
    equipment: 'repair',
  }

  async function loadAssignmentFromCase(caseMaterials) {
    const pointsStore = usePointsStore()

    // 清除所有现有的物资分配
    assignments.value = {}

    // 为每个需求点加载案例中的物资数据
    for (const pt of pointsStore.demands) {
      if (caseMaterials[pt.name]) {
        const info = caseMaterials[pt.name]
        const convertedItems = (info.items || []).map(item => {
          const uw = item.unit_weight || item.weight || 0
          const q = item.qty || item.quantity || 1
          return {
            name: item.name || '',
            unit: 'kg',
            unit_weight: uw,
            qty: q,
            subtotal: uw * q,
            category_id: null,
          }
        })

        let supplyTypes = []
        if (info.supply_types) {
          if (Array.isArray(info.supply_types)) {
            supplyTypes = info.supply_types
          } else if (typeof info.supply_types === 'string') {
            supplyTypes = [info.supply_types]
          }
        }

        // 从 supply_types 推导 category_ids（去重）
        const categoryIds = [...new Set(
          supplyTypes.map(t => SUPPLY_TYPE_TO_CATEGORY[t]).filter(Boolean)
        )]

        assignments.value[pt.id] = {
          point_id: pt.id,
          point_name: pt.name,
          category_ids: info.category_ids || categoryIds,
          custom_items: convertedItems,
          total_weight: info.weight || info.total_weight || 0,
          priority: info.priority || 3,
          special_requirements: info.special_requirements || '',
          risk_warnings: Array.isArray(info.risk_warnings) ? info.risk_warnings : (info.risk_warnings ? [info.risk_warnings] : []),
          supply_types: supplyTypes,
          items: convertedItems,
        }

        await _saveToDb(pt.id)
      }
    }

    // 触发响应式更新
    assignments.value = { ...assignments.value }
  }

  return {
    categories,
    loading,
    error,
    assignments,
    totalWeight,
    highestPriority,
    assignedCount,
    loadCategories,
    loadFromDb,
    assignMaterials,
    toggleCategory,
    updateItem,
    addItem,
    removeItem,
    getAssignment,
    isCategorySelected,
    loadDefaultCase,
    loadAssignmentFromCase,
    updatePriority,
    updateDeliveryMode,
    clearAssignments,
  }
})