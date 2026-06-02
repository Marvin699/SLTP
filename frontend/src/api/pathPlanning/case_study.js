import axios from 'axios'

const api = axios.create({
  baseURL: '/api/path-planning',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

/** 获取所有案例 */
export function getCaseStudies() {
  return api.get('/case/studies')
}

/** 获取单个案例 */
export function getCaseStudy(caseId) {
  return api.get(`/case/studies/${caseId}`)
}

/** 创建案例 */
export function createCaseStudy(caseData) {
  return api.post('/case/studies', caseData)
}

/** 更新案例 */
export function updateCaseStudy(caseId, caseData) {
  return api.put(`/case/studies/${caseId}`, caseData)
}

/** 删除案例 */
export function deleteCaseStudy(caseId) {
  return api.delete(`/case/studies/${caseId}`)
}

/** 设置为默认案例 */
export function setDefaultCase(caseId) {
  return api.post(`/case/studies/${caseId}/set-default`)
}

/** 初始化默认案例 */
export function initDefaultCase() {
  return api.post('/case/init-default')
}