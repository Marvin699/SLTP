import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 预设账号（纯前端，不依赖后端）
const ACCOUNTS = {
  teacher: { password: '123456', role: 'teacher', label: '教师', greeting: '教师' },
  student: { password: '123456', role: 'student', label: '学生', greeting: '同学' }
}

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 恢复登录状态
  const saved = JSON.parse(localStorage.getItem('sltp_user') || 'null')
  const username = ref(saved?.username || '')
  const role = ref(saved?.role || '')
  const label = ref(saved?.label || '')

  const isLoggedIn = computed(() => !!username.value)
  const greeting = computed(() => {
    if (!username.value) return ''
    return ACCOUNTS[username.value]?.greeting || username.value
  })
  const roleLabel = computed(() => label.value || '用户')

  function login(account, password) {
    const accountInfo = ACCOUNTS[account]
    if (!accountInfo || accountInfo.password !== password) {
      return { success: false, message: '账号或密码错误' }
    }
    username.value = account
    role.value = accountInfo.role
    label.value = accountInfo.label
    localStorage.setItem('sltp_user', JSON.stringify({
      username: account,
      role: accountInfo.role,
      label: accountInfo.label
    }))
    return { success: true }
  }

  function logout() {
    username.value = ''
    role.value = ''
    label.value = ''
    localStorage.removeItem('sltp_user')
  }

  return { username, role, label, isLoggedIn, greeting, roleLabel, login, logout }
})
