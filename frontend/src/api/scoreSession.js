import axios from 'axios'

const api = axios.create({
  baseURL: '/api/score',
  timeout: 10000,
})

// 获取三个环节的配置信息
export function fetchSections() {
  return api.get('/sections')
}

// 获取所有会话（可按环节筛选）
export function fetchSessions(sectionId) {
  const params = sectionId ? { section_id: sectionId } : {}
  return api.get('/sessions', { params })
}

// 创建会话（根据环节自动填充维度）
export function createSession(data) {
  return api.post('/sessions', data)
}

// 删除会话
export function deleteSession(id) {
  return api.delete(`/sessions/${id}`)
}

// 通过token获取会话信息
export function fetchSessionByToken(token) {
  return api.get(`/session/${token}`)
}

// 提交打分
export function submitScores(data) {
  return api.post('/submit', data)
}

// 获取评分汇总
export function fetchSummary(token) {
  return api.get(`/summary/${token}`)
}

// 获取打分人状态
export function fetchScorerStatus(token) {
  return api.get(`/scorer-status/${token}`)
}

// 获取某环节的全组仪表盘数据
export function fetchDashboard(sectionId) {
  return api.get(`/dashboard/${sectionId}`)
}

// 清空某环节所有打分记录
export function clearSectionScores(sectionId) {
  return api.delete(`/clear/${sectionId}`)
}

// 获取整体概览（仪表盘用）
export function fetchOverview() {
  return api.get('/overview')
}
