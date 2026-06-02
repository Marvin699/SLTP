import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchModels, assessUAVs, assessUAVsAI, fetchLLMStatus, updateUAVModel, fetchAIResults, deleteAIResult as deleteAIResultApi } from '@/api/pathPlanning/uavs'
import { usePointsStore } from './points'
import { useMaterialsStore } from './materials'

export const useUavsStore = defineStore('uavs', () => {
  const models = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 用户选择: [{ model_id, quantity }]
  const selections = ref([])

  // 规则评估结果
  const assessment = ref(null)

  // AI评估结果
  const aiResult = ref(null)

  // AI 历史记录
  const aiResults = ref([])

  // LLM状态
  const llmConfigured = ref(false)

  async function loadModels() {
    loading.value = true
    try {
      const [modelsRes, llmRes] = await Promise.all([
        fetchModels(),
        fetchLLMStatus(),
      ])
      models.value = modelsRes.data
      llmConfigured.value = llmRes.data.configured
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  // 按品牌分组
  const brands = computed(() => {
    const map = {}
    for (const m of models.value) {
      if (!map[m.brand]) {
        map[m.brand] = { name: m.brand, name_en: m.brand_en, models: [] }
      }
      map[m.brand].models.push(m)
    }
    return Object.values(map)
  })

  // 获取已选型号数量
  function getQuantity(modelId) {
    const sel = selections.value.find((s) => s.model_id === modelId)
    return sel ? sel.quantity : 0
  }

  // 设置某型号数量
  function setQuantity(modelId, quantity) {
    const idx = selections.value.findIndex((s) => s.model_id === modelId)
    if (quantity <= 0) {
      if (idx >= 0) selections.value.splice(idx, 1)
    } else {
      if (idx >= 0) {
        selections.value[idx] = { ...selections.value[idx], quantity }
      } else {
        selections.value.push({ model_id: modelId, quantity })
      }
    }
    selections.value = [...selections.value]
    // 清除旧评估
    assessment.value = null
  }

  // 增减数量
  function increment(modelId) {
    setQuantity(modelId, getQuantity(modelId) + 1)
  }

  function decrement(modelId) {
    setQuantity(modelId, getQuantity(modelId) - 1)
  }

  // 已选无人机详情
  const selectedDetails = computed(() => {
    return selections.value.map((sel) => {
      const model = models.value.find((m) => m.id === sel.model_id)
      return { ...sel, model }
    }).filter((d) => d.model)
  })

  // 总载重能力
  const totalPayload = computed(() => {
    return selectedDetails.value.reduce((sum, d) => sum + d.model.max_payload * d.quantity, 0)
  })

  // 总数量
  const totalCount = computed(() => {
    return selections.value.reduce((sum, s) => sum + s.quantity, 0)
  })

  /** 更新无人机型号参数（实时保存到数据库，同时更新本地数据） */
  async function updateModelParam(modelId, data) {
    try {
      const res = await updateUAVModel(modelId, data)
      // 更新本地 models 列表
      const idx = models.value.findIndex(m => m.id === modelId)
      if (idx >= 0) {
        models.value[idx] = { ...models.value[idx], ...res.data }
        models.value = [...models.value]
      }
      // 清除旧评估
      assessment.value = null
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    }
  }

  // 执行评估
  async function runAssessment() {
    const ptsStore = usePointsStore()
    const matStore = useMaterialsStore()

    if (selections.value.length === 0) {
      error.value = '请至少选择一种无人机'
      return null
    }

    // 构建需求点数据
    const demands = ptsStore.demands.map((pt) => {
      const assignment = matStore.getAssignment(pt.id)
      return {
        name: pt.name,
        total_weight: assignment ? assignment.total_weight : 0,
        priority: assignment ? assignment.priority : 3,
        special_requirements: assignment ? assignment.special_requirements : '',
        distance_km: ptsStore.distReturn.length > 0
          ? ptsStore.distReturn[ptsStore.distLabels.indexOf(pt.name)] || 0
          : 0,
      }
    })

    if (demands.every((d) => d.total_weight === 0)) {
      error.value = '请先在模块二设置需求点物资信息'
      return null
    }

    loading.value = true
    error.value = null
    try {
      const payload = {
        selections: selections.value,
        demands,
      }
      const res = await assessUAVs(payload)
      assessment.value = res.data
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  // AI大模型评估
  async function runAIAssessment() {
    loading.value = true
    error.value = null
    aiResult.value = null
    try {
      const res = await assessUAVsAI()
      aiResult.value = res.data
      // 自动刷新历史列表
      loadAIResults()
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  // 加载 AI 历史记录
  async function loadAIResults() {
    try {
      const res = await fetchAIResults()
      aiResults.value = res.data
    } catch (e) {
      console.warn('[UAVs] 加载AI历史记录失败:', e.message)
    }
  }

  // 删除单条 AI 历史记录
  async function removeAIResult(id) {
    try {
      await deleteAIResultApi(id)
      aiResults.value = aiResults.value.filter(r => r.id !== id)
      if (aiResult.value && aiResult.value.saved_id === id) {
        aiResult.value = null
      }
    } catch (e) {
      error.value = e.message
    }
  }

  // 清空选择
  function clearSelections() {
    selections.value = []
    assessment.value = null
    aiResult.value = null
  }

  return {
    models,
    brands,
    loading,
    error,
    selections,
    assessment,
    aiResult,
    aiResults,
    llmConfigured,
    selectedDetails,
    totalPayload,
    totalCount,
    loadModels,
    getQuantity,
    setQuantity,
    increment,
    decrement,
    updateModelParam,
    runAssessment,
    runAIAssessment,
    loadAIResults,
    removeAIResult,
    clearSelections,
  }
})
