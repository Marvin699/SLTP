<template>
  <div class="login-page page-aurora">
    <div class="login-card fade-up">
      <div class="login-header">
        <div class="login-logo">
          <span class="logo-icon">✈</span>
        </div>
        <h1 class="login-title glow-text">智慧低空应急运输教学平台</h1>
        <p class="login-subtitle">Smart Low-Altitude Emergency Transportation</p>
      </div>

      <el-form class="login-form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="请输入账号"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            type="password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <div class="login-error" v-if="errorMsg">{{ errorMsg }}</div>
        <el-button
          type="primary"
          size="large"
          class="login-btn btn-glow"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>

      <div class="login-footer">
        <div class="register-link" @click="goRegister">
          <span>没有账号？</span>
          <span class="link-text">学生注册 →</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

function goRegister() {
  router.push('/register')
}

async function handleLogin() {
  errorMsg.value = ''
  if (!form.username.trim()) {
    errorMsg.value = '请输入账号'
    return
  }
  if (!form.password) {
    errorMsg.value = '请输入密码'
    return
  }

  loading.value = true
  const result = await userStore.login(form.username.trim(), form.password)
  loading.value = false

  if (result.success) {
    if (userStore.mustChangePassword) {
      router.push('/change-password')
    } else {
      router.push('/home')
    }
  } else {
    errorMsg.value = result.message
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 登录卡片：哑光暗面板 */
.login-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 40px 36px 32px;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55);
  position: relative;
  z-index: 10;
}

/* 头部 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: rgba(34, 211, 238, 0.06);
  border: 1px solid rgba(34, 211, 238, 0.25);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: #22d3ee;
}

.login-title {
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(90deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}

.login-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 1px;
}

/* 表单 */
.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 10px !important;
  padding: 4px 12px;
}

.login-form :deep(.el-input__wrapper:focus-within) {
  border-color: rgba(34, 211, 238, 0.5) !important;
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.12) !important;
}

.login-form :deep(.el-input__inner) {
  color: #e2e8f0 !important;
  height: 40px;
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: rgba(255, 255, 255, 0.5);
}

.login-error {
  color: #f56c6c;
  font-size: 13px;
  margin-bottom: 12px;
  text-align: center;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  margin-top: 4px;
}

/* 底部提示 */
.login-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 20px;
  text-align: center;
}

.register-link {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: color 0.2s;
  padding: 8px;
}

.register-link:hover .link-text {
  color: #67e8f9;
}

.link-text {
  color: #22d3ee;
  font-weight: 500;
  transition: color 0.2s;
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    width: calc(100% - 32px);
    padding: 28px 20px 24px;
    margin: 0 16px;
  }

  .login-title {
    font-size: 18px;
  }
}
</style>
