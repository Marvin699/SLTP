<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
    </div>

    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <span class="logo-icon">✈</span>
        </div>
        <h1 class="login-title">智慧低空应急运输教学平台</h1>
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
          class="login-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>

      <div class="login-footer">
        <div class="account-hint">
          <span class="hint-label">测试账号</span>
          <div class="hint-accounts">
            <div class="hint-account" @click="fillAccount('teacher')">
              <span class="account-icon">👨‍🏫</span>
              <span>教师端：teacher / 123456</span>
            </div>
            <div class="hint-account" @click="fillAccount('student')">
              <span class="account-icon">👨‍🎓</span>
              <span>学生端：student / 123456</span>
            </div>
          </div>
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

function fillAccount(type) {
  form.username = type
  form.password = '123456'
  errorMsg.value = ''
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
  // 模拟网络延迟
  await new Promise(r => setTimeout(r, 500))

  const result = userStore.login(form.username.trim(), form.password)
  loading.value = false

  if (result.success) {
    router.push('/home')
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
  background: #0a1628;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.bg-circle.c1 {
  width: 400px;
  height: 400px;
  background: rgba(64, 158, 255, 0.12);
  top: -100px;
  right: -100px;
  animation: float1 8s ease-in-out infinite;
}

.bg-circle.c2 {
  width: 300px;
  height: 300px;
  background: rgba(0, 229, 255, 0.1);
  bottom: -80px;
  left: -80px;
  animation: float2 10s ease-in-out infinite;
}

.bg-circle.c3 {
  width: 200px;
  height: 200px;
  background: rgba(103, 194, 58, 0.08);
  top: 50%;
  left: 60%;
  animation: float3 12s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, 30px); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

@keyframes float3 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-15px, 15px); }
}

/* 登录卡片 */
.login-card {
  width: 420px;
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 22, 40, 0.98) 100%);
  border: 1px solid rgba(64, 158, 255, 0.25);
  border-radius: 16px;
  padding: 40px 36px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
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
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(103, 194, 58, 0.2));
  border: 1px solid rgba(64, 158, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
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
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
  border-radius: 10px !important;
  padding: 4px 12px;
}

.login-form :deep(.el-input__wrapper:focus-within) {
  border-color: rgba(64, 158, 255, 0.5) !important;
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.15) !important;
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
  border-top: 1px solid rgba(64, 158, 255, 0.12);
  padding-top: 20px;
}

.account-hint {
  text-align: center;
}

.hint-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  display: block;
  margin-bottom: 10px;
}

.hint-accounts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hint-account {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
  transition: all 0.2s;
}

.hint-account:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.25);
  color: rgba(255, 255, 255, 0.9);
}

.account-icon {
  font-size: 16px;
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
