import axios from 'axios'

/** 合规性核验 API（需登录，自动携带 token） */
const api = axios.create({
  baseURL: '/api/path-planning/verification',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sltp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** 获取标准核验模板（7 组指标） */
export function getTemplate() {
  return api.get('/template')
}

/**
 * 提交核验（服务端规则引擎交叉复核）
 * @param {object} task 任务配置
 * @param {object} solution 方案数据
 * @param {Array<{id:string, student_judgment:string, remark?:string}>} checklist 学生判定
 * @param {number|null} planRecordId 关联方案库记录
 */
export function submitCheck(task, solution, checklist, planRecordId = null) {
  return api.post('/check', {
    task,
    solution,
    checklist,
    plan_record_id: planRecordId,
  })
}

/** 我的核验历史 */
export function listRecords(limit = 10) {
  return api.get('/records', { params: { limit } })
}

/** 删除核验记录 */
export function deleteRecord(recordId) {
  return api.delete(`/${recordId}`)
}
