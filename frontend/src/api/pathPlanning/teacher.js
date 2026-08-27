import axios from 'axios'

/** 教师端监控 API（需教师登录，自动携带 token） */
const api = axios.create({
  baseURL: '/api/path-planning/teacher',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sltp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** 全班总览：学生列表 + 参与度/质量聚合 */
export function getDashboard() {
  return api.get('/dashboard')
}

/** 某学生的核验记录（含完整清单） */
export function getStudentVerifications(userId) {
  return api.get(`/student/${userId}/verifications`)
}

/** 某学生的辩论会话列表 */
export function getStudentDebateSessions(userId) {
  return api.get(`/student/${userId}/debate-sessions`)
}

/** 辩论时间线回放 */
export function getDebateReplay(sessionId) {
  return api.get(`/debate-session/${sessionId}`)
}

/** 教师介入留言（复用辩论模块接口） */
export function sendTeacherNote(sessionId, content) {
  return axios.post(
    `/api/debate/session/${sessionId}/teacher-note`,
    { content },
    {
      timeout: 30000,
      headers: (() => {
        const h = { 'Content-Type': 'application/json' }
        const token = localStorage.getItem('sltp_token')
        if (token) h.Authorization = `Bearer ${token}`
        return h
      })(),
    }
  )
}
