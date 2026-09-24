import { createApi } from '@/utils/request'

const api = createApi({
  baseURL: '/api/path-planning',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

// 自动携带登录 token（报告归属 + 择优日志需要）

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

/** 下载报告文件（word/pdf，带 token 的 blob 下载） */
export function downloadReportFile(reportId, ext) {
  return api.get(`/report/download/${reportId}/${ext}`, {
    responseType: 'blob',
    timeout: 300000,
  }).then(res => {
    // 从 Content-Disposition 解析服务端文件名，失败则用默认名
    const disposition = res.headers['content-disposition'] || ''
    const match = disposition.match(/filename\*=UTF-8''([^;]+)/)
    let name = `运输方案报告.${ext === 'word' ? 'docx' : 'pdf'}`
    if (match) {
      try { name = decodeURIComponent(match[1]) } catch { /* 保留默认名 */ }
    }
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    URL.revokeObjectURL(url)
  })
}
