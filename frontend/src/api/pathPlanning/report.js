import axios from 'axios'

const api = axios.create({
  baseURL: '/api/path-planning',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

// 自动携带登录 token（报告归属 + 择优日志需要）
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sltp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** 生成报告 */
export function generateReport(task, solution, diagnosis = null, schemeType = '运输方案', acoParams = null) {
  return api.post('/report/generate', { task, solution, diagnosis, scheme_type: schemeType, aco_params: acoParams })
}

/** 择优决策：选定最终方案（全局唯一），记录决策理由 */
export function chooseReport(reportId, reason = '') {
  return api.post(`/report/${reportId}/choose`, { reason })
}

/** 获取报告历史 */
export function getReportHistory(limit = 20) {
  return api.get('/report/history', { params: { limit } })
}

/** 获取报告详情 */
export function getReportDetail(reportId) {
  return api.get(`/report/${reportId}`)
}

/** 更新报告 */
export function updateReport(reportId, reportData) {
  return api.put(`/report/${reportId}`, { report_data: reportData })
}

/** 删除报告 */
export function deleteReport(reportId) {
  return api.delete(`/report/${reportId}`)
}

/** 下载Word */
export function downloadWordUrl(reportId) {
  return `/api/path-planning/report/download/${reportId}/word`
}

/** 下载PDF */
export function downloadPdfUrl(reportId) {
  return `/api/path-planning/report/download/${reportId}/pdf`
}
