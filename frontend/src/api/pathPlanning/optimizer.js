import axios from 'axios'

const api = axios.create({
  baseURL: '/api/path-planning',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

/** 运行路径优化 */
export function runOptimizer(task, acoParams) {
  return api.post('/optimizer/run', { task, aco_params: acoParams })
}

/** 获取默认 ACO 参数 */
export function getDefaultParams(task) {
  return api.post('/optimizer/params/default', { task })
}

/** 导出 Excel 运输汇总 */
export function exportExcel(task, acoParams) {
  return api.post('/optimizer/export/excel', { task, aco_params: acoParams }, {
    responseType: 'blob',
  })
}

/** 获取优化历史记录 */
export function getOptimizationHistory(limit = 20) {
  return api.get('/optimizer/history', { params: { limit } })
}

/** 获取单个优化记录详情 */
export function getOptimizationDetail(recordId) {
  return api.get(`/optimizer/${recordId}`)
}

/** 删除优化记录 */
export function deleteOptimization(recordId) {
  return api.delete(`/optimizer/${recordId}`)
}
