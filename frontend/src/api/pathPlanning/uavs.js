import axios from 'axios'

const api = axios.create({
  baseURL: '/api/path-planning',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

const apiLLM = axios.create({
  baseURL: '/api/path-planning',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

/** 获取所有无人机品牌 */
export function fetchBrands() {
  return api.get('/uavs/brands')
}

/** 获取所有无人机型号 */
export function fetchModels() {
  return api.get('/uavs/models')
}

/** 获取单个型号详情 */
export function fetchModel(modelId) {
  return api.get(`/uavs/models/${modelId}`)
}

/** 更新无人机型号参数（实时保存到数据库） */
export function updateUAVModel(modelId, data) {
  return api.put(`/uavs/models/${modelId}`, data)
}

/** 规则引擎评估 */
export function assessUAVs(payload) {
  return api.post('/uavs/assess', payload)
}

/** AI大模型评估 */
export function assessUAVsAI() {
  return apiLLM.post('/uavs/assess-ai')
}

/** 检查大模型是否已配置 */
export function fetchLLMStatus() {
  return api.get('/uavs/llm-status')
}

/** 获取所有已保存的 AI 选型结果 */
export function fetchAIResults() {
  return api.get('/uavs/ai-results')
}

/** 删除单条 AI 选型结果 */
export function deleteAIResult(id) {
  return api.delete(`/uavs/ai-results/${id}`)
}
