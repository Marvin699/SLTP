import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 统一 API 实例工厂
 * - 自动注入 Authorization: Bearer <token>（存在时，匿名页不注入）
 * - 401 统一处理：清除登录态、提示并跳转登录页
 * - skipAuth=true 用于登录/注册等公开接口（跳过拦截器，行为与裸 axios 一致）
 *
 * 用法：把原来 `axios.create({...})` 换成 `createApi({...})` 即可，
 * baseURL/timeout/headers 等原有配置全部保留。
 */
let last401At = 0

export function createApi(config = {}, { skipAuth = false } = {}) {
  const instance = axios.create({ timeout: 30000, ...config })

  if (!skipAuth) {
    // 请求拦截：注入登录态
    instance.interceptors.request.use((cfg) => {
      const token = localStorage.getItem('sltp_token')
      if (token) cfg.headers.Authorization = `Bearer ${token}`
      return cfg
    })

    // 响应拦截：401 统一登出
    instance.interceptors.response.use(
      (res) => res,
      (err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem('sltp_token')
          localStorage.removeItem('sltp_user')
          // 3 秒内多个请求同时 401 只提示一次
          if (Date.now() - last401At > 3000) {
            last401At = Date.now()
            ElMessage.error('登录已过期，请重新登录')
          }
          // 用整页跳转避免 utils 与 router 循环依赖；登录/评分页不跳
          if (!location.pathname.startsWith('/login') && !location.pathname.startsWith('/score')) {
            location.href = '/login'
          }
        }
        return Promise.reject(err)
      }
    )
  }
  return instance
}

/** localStorage JSON 安全解析：数据损坏时返回默认值，防止启动白屏 */
export function safeParse(key, fallback = null) {
  try {
    const raw = localStorage.getItem(key)
    return raw === null ? fallback : (JSON.parse(raw) ?? fallback)
  } catch {
    return fallback
  }
}

/** 无 baseURL 的全局实例（请求路径请写全，如 /api/xxx），带统一鉴权 */
export const apiRoot = createApi({})

/**
 * 带登录态的 fetch：自动注入 Authorization 头。
 * 项目里部分组件用原生 fetch 调后端（大屏轮询、workspace 保存等），
 * 必须统一走它，否则后端开启接口鉴权后会 401。
 */
export async function authFetch(url, options = {}) {
  const token = localStorage.getItem('sltp_token')
  const headers = new Headers(options.headers || {})
  if (token) headers.set('Authorization', `Bearer ${token}`)
  return fetch(url, { ...options, headers })
}
