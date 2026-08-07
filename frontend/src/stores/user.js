import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// 后端 API 基础地址（前端通过 Vite 代理 /api → http://127.0.0.1:8000）
// 生产环境打包后，前端与后端同源，相对路径也能工作
const API_BASE = import.meta.env.VITE_API_BASE || ''

// 创建专用 axios 实例
const authApi = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
})

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 恢复登录状态
  const savedToken = localStorage.getItem('sltp_token') || ''
  const savedUser = JSON.parse(localStorage.getItem('sltp_user') || 'null')

  const token = ref(savedToken)
  const user = ref(savedUser)  // { id, username, role, student_no, class_name, group_no, must_change_password }

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const role = computed(() => user.value?.role || '')
  const username = computed(() => user.value?.username || '')
  const avatar = computed(() => user.value?.avatar || '')
  const mustChangePassword = computed(() => !!user.value?.must_change_password)
  const isTeacher = computed(() => role.value === 'teacher')
  const isStudent = computed(() => role.value === 'student')

  // 角色显示标签
  const roleLabel = computed(() => {
    if (role.value === 'teacher') return '教师'
    if (role.value === 'student') return '学生'
    return '用户'
  })

  // 问候语
  const greeting = computed(() => {
    if (!username.value) return ''
    if (role.value === 'teacher') return `${username.value}老师`
    return `${username.value}同学`
  })

  /**
   * 登录（调用后端 /api/auth/login）
   */
  async function login(account, password) {
    try {
      const res = await authApi.post('/api/auth/login', {
        username: account.trim(),
        password: password,
      })
      if (res.data.success) {
        token.value = res.data.token
        user.value = res.data.user
        localStorage.setItem('sltp_token', res.data.token)
        localStorage.setItem('sltp_user', JSON.stringify(res.data.user))
        return { success: true }
      }
      return { success: false, message: res.data.message || '登录失败' }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || '登录失败，请检查网络'
      return { success: false, message: msg }
    }
  }

  /**
   * 注册（学生自助注册）
   */
  async function register({ username, student_no, password, class_name, group_no }) {
    try {
      const res = await authApi.post('/api/auth/register', {
        username,
        student_no,
        password,
        class_name,
        group_no,
      })
      if (res.data.success) {
        token.value = res.data.token
        user.value = res.data.user
        localStorage.setItem('sltp_token', res.data.token)
        localStorage.setItem('sltp_user', JSON.stringify(res.data.user))
        return { success: true }
      }
      return { success: false, message: res.data.message || '注册失败' }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || '注册失败，请检查网络'
      return { success: false, message: msg }
    }
  }

  /**
   * 修改密码
   */
  async function changePassword(oldPassword, newPassword) {
    try {
      const res = await authApi.post('/api/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      }, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      if (res.data.success) {
        // 清除强制改密标记
        if (user.value) {
          user.value.must_change_password = false
          localStorage.setItem('sltp_user', JSON.stringify(user.value))
        }
        return { success: true, message: res.data.message }
      }
      return { success: false, message: res.data.message }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || '修改密码失败'
      return { success: false, message: msg }
    }
  }

  /**
   * 刷新当前用户信息（从后端拉取最新）
   */
  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await authApi.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      if (res.data.success) {
        user.value = res.data.user
        localStorage.setItem('sltp_user', JSON.stringify(res.data.user))
      }
    } catch (err) {
      // Token 失效，清除登录状态
      if (err.response?.status === 401) {
        logout()
      }
    }
  }

  /**
   * 更新个人资料（用户名、头像、班级、小组）
   */
  async function updateProfile({ username, avatar, class_name, group_no }) {
    try {
      const payload = {}
      if (username !== undefined) payload.username = username
      if (avatar !== undefined) payload.avatar = avatar
      if (class_name !== undefined) payload.class_name = class_name
      if (group_no !== undefined) payload.group_no = group_no

      const res = await authApi.put('/api/auth/profile', payload, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      if (res.data.success) {
        user.value = res.data.user
        localStorage.setItem('sltp_user', JSON.stringify(res.data.user))
        return { success: true, message: res.data.message }
      }
      return { success: false, message: res.data.message || '更新失败' }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || '更新失败'
      return { success: false, message: msg }
    }
  }

  /**
   * 退出登录
   */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('sltp_token')
    localStorage.removeItem('sltp_user')
  }

  return {
    token, user, isLoggedIn, role, username, avatar, roleLabel, greeting,
    mustChangePassword, isTeacher, isStudent,
    login, register, changePassword, fetchMe, updateProfile, logout,
  }
})
