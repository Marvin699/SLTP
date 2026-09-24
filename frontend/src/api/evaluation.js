/**
 * T5 课前课中贯通 API
 * 课中环节引用课前方案库 + 基于真实方案数据的 AI 点评
 */
import { createApi } from '@/utils/request'

const api = createApi({
  baseURL: '/api/evaluation',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

// 自动携带登录 token（与平台其他模块一致）

/**
 * 课前方案库列表（含学生姓名、四维评分、辩论概况）
 * @param {Object} params { limit, user_id }
 */
export function fetchPlanLibrary(params = {}) {
  return api.get('/plans', { params })
}

/**
 * 基于真实方案数据生成 AI 点评（词云/风险/综合点评）
 * @param {number[]} planIds 参与点评的方案 ID（1-2个）
 */
export function fetchAiComment(planIds) {
  return api.post('/ai-comment', { plan_ids: planIds })
}
