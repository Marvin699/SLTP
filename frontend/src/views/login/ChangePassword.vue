<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-circle c1"></div>
    </div>

    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <span class="logo-icon">🔐</span>
        </div>
        <h1 class="login-title">修改密码</h1>
        <p class="login-subtitle" v-if="userStore.mustChangePassword">
          首次登录或教师重置密码后，请修改为您的专属密码
        </p>
      </div>

      <el-form class="login-form" @submit.prevent="handleSubmit">
        <el-form-item>
          <el-input
            v-model="form.oldPassword"
            type="password"
            placeholder="当前密码（默认：123456）"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.newPassword"
            type="password"
            placeholder="新密码（至少 6 位）"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认新密码"
            size="large"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <div class="login-error" v-if="errorMsg">{{ errorMsg }}</div>
        <div class="login-success" v-if="successMsg">{{ successMsg }}</div>

        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleSubmit"
        >
          确认修改
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!form.oldPassword) {
    errorMsg.value = '请输入当前密码'
    return
  }
  if (!form.newPassword) {
    errorMsg.value = '请输入新密码'
    return
  }
  if (form.newPassword.length < 6) {
    errorMsg.value = '新密码长度不能少于 6 位'
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    errorMsg.value = '两次输入的新密码不一致'
    return
  }
  if (form.newPassword === form.oldPassword) {
    errorMsg.value = '新密码不能与原密码相同'
    return
  }

  loading.value = true
  const result = await userStore.changePassword(form.oldPassword, form.newPassword)
  loading.value = false

  if (result.success) {
    successMsg.value = '密码修改成功，正在跳转首页...'
    setTimeout(() => router.push('/home'), 1000)
  } else {
    errorMsg.value = result.message
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: #0a1628; position: relative; overflow: hidden;
}
.login-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-circle {
  position: absolute; border-radius: 50%; filter: blur(80px);
  width: 400px; height: 400px;
  background: rgba(230, 162, 60, 0.12);
  top: -100px; right: -100px;
  animation: float1 8s ease-in-out infinite;
}
@keyframes float1 { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-30px, 30px); } }

.login-card {
  width: 420px;
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 22, 40, 0.98) 100%);
  border: 1px solid rgba(230, 162, 60, 0.25);
  border-radius: 16px; padding: 40px 36px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  position: relative; z-index: 10;
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-logo {
  width: 64px; height: 64px; margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(64, 158, 255, 0.2));
  border: 1px solid rgba(230, 162, 60, 0.3);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 30px;
}
.login-title {
  font-size: 22px; font-weight: 800;
  background: linear-gradient(90deg, #e6a23c, #409eff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}
.login-subtitle { font-size: 13px; color: rgba(255, 255, 255, 0.5); }

.login-form { margin-bottom: 16px; }
.login-form :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(230, 162, 60, 0.2) !important;
  border-radius: 10px !important; padding: 4px 12px;
}
.login-form :deep(.el-input__wrapper:focus-within) {
  border-color: rgba(230, 162, 60, 0.5) !important;
  box-shadow: 0 0 12px rgba(230, 162, 60, 0.15) !important;
}
.login-form :deep(.el-input__inner) { color: #e2e8f0 !important; height: 40px; }

.login-error { color: #f56c6c; font-size: 13px; margin-bottom: 12px; text-align: center; }
.login-success { color: #67c23a; font-size: 13px; margin-bottom: 12px; text-align: center; }
.login-btn {
  width: 100%; height: 44px;
  font-size: 16px; font-weight: 600;
  border-radius: 10px; margin-top: 4px;
}
</style>
