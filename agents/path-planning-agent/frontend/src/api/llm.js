import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

/** 获取所有大模型配置 */
export function getLLMConfigs() {
  return api.get('/llm/configs')
}

/** 添加大模型配置 */
export function createLLMConfig(config) {
  return api.post('/llm/configs', config)
}

/** 更新大模型配置 */
export function updateLLMConfig(id, config) {
  return api.put(`/llm/configs/${id}`, config)
}

/** 删除大模型配置 */
export function deleteLLMConfig(id) {
  return api.delete(`/llm/configs/${id}`)
}

/** 激活大模型配置 */
export function activateLLMConfig(id) {
  return api.post(`/llm/configs/${id}/activate`)
}

/** 获取当前激活的配置 */
export function getActiveLLMConfig() {
  return api.get('/llm/active')
}

/** 测试大模型连接 */
export function testLLMConnection(id) {
  return api.post('/llm/test', null, { params: { config_id: id } })
}

/** 初始化默认配置 */
export function initDefaultLLMConfig() {
  return api.post('/llm/init-default')
}