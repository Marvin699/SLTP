import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usePointsStore } from './points'
import {
  fetchCategories as apiLoadCategories,
  saveAssignment as apiSaveAssignment,
  fetchDefaultCase,
  loadSavedAssignments,
  deleteSavedAssignment as apiDeleteAssignment,
  deleteAllSavedAssignments as apiDeleteAllAssignments,
} from '../api/materials'

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
        const pointsStore = usePointsStore()
        const remapped = {}
        const unmatchedIds = []
        const unmatchedNames = []
        
        // 规范化 risk_warnings 字段，并尝试按 point_name 重新映射
        for (const key of Object.keys(res.data)) {
          const a = res.data[key]
          if (typeof a.risk_warnings === 'string') {
            a.risk_warnings = a.risk_warnings ? a.risk_warnings.split('；').filter(Boolean) : []
          }
          
          // 确保 point_id 是数字类型（如果可能）
          const pointId = Number(a.point_id) || a.point_id
          
          // 检查 point_id 是否在当前需求点中存在
          const existingPt = pointsStore.demands.find(p => p.id === pointId || String(p.id) === String(a.point_id))
          if (existingPt) {
            // point_id 匹配，直接使用（使用 pt.id 作为 key，确保类型一致）
            remapped[existingPt.id] = a
            a.point_id = existingPt.id  // 确保 point_id 字段也一致
          } else {
            // point_id 不匹配，尝试按 point_name 查找
            const ptByName = pointsStore.demands.find(p => p.name === a.point_name)
            if (ptByName) {
              // 保存旧的 point_id
              const oldPointId = a.point_id
              // 用新的 point_id 保存（使用 ptByName.id 作为 key）
              a.point_id = ptByName.id
              remapped[ptByName.id] = a
              // 清理旧的 point_id 数据
              cleanupOldAssignment(oldPointId, ptByName.id)
            } else {
              unmatchedIds.push(a.point_id)
              unmatchedNames.push(a.point_name)
            }
          }
        }
        
        assignments.value = remapped
        
        // 清理不匹配的数据
        if (unmatchedIds.length > 0) {
          console.warn(`[materials] 发现 ${unmatchedIds.length} 条无效物资数据，正在清理...`)
          cleanupInvalidAssignments(unmatchedIds)
        }
        
        console.log(`[materials] 从数据库加载 ${Object.keys(remapped).length} 条物资数据`)
        console.log(`[materials] remapped keys 类型: ${Object.keys(remapped).map(k => typeof k)}`)
      }
    } catch (e) {
      console.error('[materials] 加载数据库物资数据失败:', e)
      assignments.value = {}
    }
  }

  // 清理旧的 point_id 数据
  async function cleanupOldAssignment(oldPointId, newPointId) {
    try {
      // 只有当 oldPointId != newPointId 时才清理
      if (oldPointId !== newPointId) {
        await apiDeleteAssignment(oldPointId)
        console.log(`[materials] 清理旧的物资数据: point_id=${oldPointId}`)
      }
    } catch (e) {
      console.warn('[materials] 清理旧物资数据失败:', e.message)
    }
  }

  // 批量清理无效数据
  async function cleanupInvalidAssignments(pointIds) {
    for (const pointId of pointIds) {
      try {
        await apiDeleteAssignment(pointId)
      } catch (e) {
        // 忽略错误，可能数据已经被删除
      }
    }
    console.log(`[materials] 已清理 ${pointIds.length} 条无效物资数据`)
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
    const assignment = getAssignment(pointId)
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
    const assignment = getAssignment(pointId)
    if (assignment && assignment.items[itemIndex]) {
      assignment.items[itemIndex][field] = value
      if (field === 'qty' || field === 'unit_weight') {
        assignment.items[itemIndex].subtotal = (assignment.items[itemIndex].unit_weight || 0) * (assignment.items[itemIndex].qty || 0)
        _recalculateTotal(pointId)
      }
    }
  }

  function addItem(pointId) {
    const assignment = getAssignment(pointId)
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
    const assignment = getAssignment(pointId)
    if (assignment && assignment.items[itemIndex]) {
      assignment.items.splice(itemIndex, 1)
      assignment.custom_items = assignment.items
      _recalculateTotal(pointId)
    }
  }

  function _recalculateTotal(pointId) {
    const assignment = getAssignment(pointId)
    if (assignment) {
      assignment.total_weight = assignment.items.reduce((sum, item) => {
        return sum + ((item.unit_weight || 0) * (item.qty || 0))
      }, 0)
    }
  }

  function getAssignment(pointId) {
    // 尝试多种类型匹配（字符串或数字）
    const strId = String(pointId)
    const numId = Number(pointId)
    
    // 先直接用原始类型查找
    if (assignments.value[pointId]) {
      return assignments.value[pointId]
    }
    // 再用字符串类型查找
    if (assignments.value[strId]) {
      return assignments.value[strId]
    }
    // 最后用数字类型查找（如果可能）
    if (!isNaN(numId) && assignments.value[numId]) {
      return assignments.value[numId]
    }
    
    return null
  }

  function isCategorySelected(pointId, categoryId) {
    const assignment = getAssignment(pointId)
    return assignment && assignment.category_ids && assignment.category_ids.includes(categoryId)
  }

  async function _saveToDb(pointId) {
    const assignment = getAssignment(pointId)
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
    const assignment = getAssignment(pointId)
    if (assignment) {
      assignment.priority = priority
      await _saveToDb(pointId)
    }
  }

  async function updateDeliveryMode(pointId, mode) {
    const assignment = getAssignment(pointId)
    if (assignment) {
      assignment.supply_types = mode
      await _saveToDb(pointId)
    }
  }

  function clearAssignments() {
    assignments.value = {}
  }

  async function clearAllFromDb() {
    assignments.value = {}
    try {
      await apiDeleteAllAssignments()
      console.log('[materials] 已清空所有物资数据')
    } catch (e) {
      console.warn('[materials] 清空物资数据失败:', e.message)
    }
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

    // 检查案例物资数据是否存在
    if (!caseMaterials || Object.keys(caseMaterials).length === 0) {
      console.warn('[materials] 案例物资数据为空，跳过加载')
      assignments.value = {}
      return
    }

    console.log('[materials] 案例物资数据keys:', Object.keys(caseMaterials))
    console.log('[materials] 当前需求点:', pointsStore.demands.map(p => ({ id: p.id, name: p.name })))

    let loadedCount = 0
    const missingPoints = []

    // 为每个需求点加载案例中的物资数据
    for (const pt of pointsStore.demands) {
      // 尝试多种方式匹配：先按id匹配，再按name匹配
      const byId = caseMaterials[pt.id]
      const byName = caseMaterials[pt.name]
      const byFuzzy = findCaseMaterialByName(caseMaterials, pt.name)
      const info = byId || byName || byFuzzy
      
      console.log(`[materials] 需求点 ${pt.name}(id=${pt.id}): byId=${!!byId}, byName=${!!byName}, byFuzzy=${!!byFuzzy}`)
      
      if (info) {
        try {
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

          // 保存到数据库
          await _saveToDb(pt.id)
          loadedCount++
        } catch (e) {
          console.error(`[materials] 加载需求点 ${pt.name} 物资数据失败:`, e)
          missingPoints.push(pt.name)
        }
      } else {
        missingPoints.push(pt.name)
      }
    }

    // 触发响应式更新
    assignments.value = { ...assignments.value }

    // 验证结果
    const totalCount = pointsStore.demands.length
    if (loadedCount === 0) {
      console.warn('[materials] 未加载任何物资数据！可能是案例数据为空或名称不匹配')
    } else if (loadedCount < totalCount) {
      console.warn(`[materials] 部分需求点物资数据缺失: ${missingPoints.join(', ')}`)
    } else {
      console.log(`[materials] 成功加载 ${loadedCount}/${totalCount} 个需求点的物资数据`)
    }
  }

  // 辅助函数：按名称模糊查找案例物资
  function findCaseMaterialByName(caseMaterials, name) {
    // 精确匹配
    if (caseMaterials[name]) return caseMaterials[name]
    // 去除空格后匹配
    const cleanName = name.trim()
    for (const key of Object.keys(caseMaterials)) {
      if (key.trim() === cleanName) {
        return caseMaterials[key]
      }
    }
    return null
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
    clearAllFromDb,
  }
})