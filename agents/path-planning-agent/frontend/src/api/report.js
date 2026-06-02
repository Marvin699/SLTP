import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

/** 生成报告 */
export function generateReport(task, solution, diagnosis = null, schemeType = '运输方案') {
  return api.post('/report/generate', { task, solution, diagnosis, scheme_type: schemeType })
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
  return `/api/report/download/${reportId}/word`
}

/** 下载PDF */
export function downloadPdfUrl(reportId) {
  return `/api/report/download/${reportId}/pdf`
}
