import axios from 'axios'

/** 反向质询辩论 API（需登录，自动携带 token） */
const api = axios.create({
  baseURL: '/api/debate',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sltp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** 创建辩论会话 */
export function createSession(data) {
  return api.post('/session', data)
}

/** 我的会话列表 */
export function listSessions(limit = 20) {
  return api.get('/sessions', { params: { limit } })
}

/** 会话详情（含全部消息） */
export function getSessionDetail(sessionId) {
  return api.get(`/session/${sessionId}`)
}

/** 学生提交陈述 → AI 追问 */
export function challenge(sessionId, data) {
  return api.post(`/session/${sessionId}/challenge`, data)
}

/** 结束会话（记录最终结论） */
export function completeSession(sessionId, finalVerdict) {
  return api.post(`/session/${sessionId}/complete`, { final_verdict: finalVerdict })
}

/** 删除会话（连同全部消息） */
export function deleteSession(sessionId) {
  return api.delete(`/session/${sessionId}`)
}
