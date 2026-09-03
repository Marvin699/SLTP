<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
    </div>

    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <span class="logo-icon">📝</span>
        </div>
        <h1 class="login-title">学生注册</h1>
        <p class="login-subtitle">Student Registration</p>
      </div>

      <el-form class="login-form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="姓名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.student_no"
            placeholder="学号"
            size="large"
            prefix-icon="Postcard"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.class_name"
            placeholder="班级（选填，如：物流2024-1班）"
            size="large"
            prefix-icon="School"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.group_no"
            placeholder="小组（选填，如：逐日组）"
            size="large"
            prefix-icon="UserFilled"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.invite_code"
            placeholder="教师邀请码（选填，向指导老师索取）"
            size="large"
            prefix-icon="Key"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="设置密码（至少 6 位）"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <div class="login-error" v-if="errorMsg">{{ errorMsg }}</div>

        <el-button
          type="primary"
          size="large"
          class="login-btn"
          :loading="loading"
          @click="handleRegister"
        >
          注 册
        </el-button>

        <el-button
          text
          size="small"
          class="back-login-btn"
          @click="$router.push('/login')"
        >
          ← 已有账号？返回登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Postcard, School, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  username: '',
  student_no: '',
  class_name: '',
  group_no: '',
  invite_code: '',
  password: '',
  confirmPassword: '',
})
const loading = ref(false)
const errorMsg = ref('')

async function handleRegister() {
  errorMsg.value = ''

  if (!form.username.trim()) {
    errorMsg.value = '请输入姓名'
    return
  }
  if (!form.student_no.trim()) {
    errorMsg.value = '请输入学号'
    return
  }
  if (!form.password) {
    errorMsg.value = '请设置密码'
    return
  }
  if (form.password.length < 6) {
    errorMsg.value = '密码长度不能少于 6 位'
    return
  }
  if (form.password !== form.confirmPassword) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  const result = await userStore.register({
    username: form.username.trim(),
    student_no: form.student_no.trim(),
    password: form.password,
    class_name: form.class_name.trim() || null,
    group_no: form.group_no.trim() || null,
    invite_code: form.invite_code.trim() || null,
  })
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
.login-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}
.bg-circle.c1 {
  width: 400px; height: 400px;
  background: rgba(103, 194, 58, 0.12);
  top: -100px; right: -100px;
  animation: float1 8s ease-in-out infinite;
}
.bg-circle.c2 {
  width: 300px; height: 300px;
  background: rgba(64, 158, 255, 0.1);
  bottom: -80px; left: -80px;
  animation: float2 10s ease-in-out infinite;
}
@keyframes float1 { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-30px, 30px); } }
@keyframes float2 { 0%,100% { transform: translate(0,0); } 50% { transform: translate(20px, -20px); } }

.login-card {
  width: 420px;
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 22, 40, 0.98) 100%);
  border: 1px solid rgba(103, 194, 58, 0.25);
  border-radius: 16px;
  padding: 36px 36px 28px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  position: relative;
  z-index: 10;
}
.login-header { text-align: center; margin-bottom: 24px; }
.login-logo {
  width: 64px; height: 64px;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2), rgba(64, 158, 255, 0.2));
  border: 1px solid rgba(103, 194, 58, 0.3);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 30px;
}
.login-title {
  font-size: 22px; font-weight: 800;
  background: linear-gradient(90deg, #67c23a, #409eff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}
.login-subtitle { font-size: 12px; color: rgba(255, 255, 255, 0.4); letter-spacing: 1px; }

.login-form { margin-bottom: 16px; }
.login-form :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(103, 194, 58, 0.2) !important;
  border-radius: 10px !important;
  padding: 4px 12px;
}
.login-form :deep(.el-input__wrapper:focus-within) {
  border-color: rgba(103, 194, 58, 0.5) !important;
  box-shadow: 0 0 12px rgba(103, 194, 58, 0.15) !important;
}
.login-form :deep(.el-input__inner) { color: #e2e8f0 !important; height: 38px; }
.login-form :deep(.el-input__prefix .el-icon) { color: rgba(255, 255, 255, 0.5); }

.login-error {
  color: #f56c6c; font-size: 13px;
  margin-bottom: 12px; text-align: center;
}
.login-btn {
  width: 100%; height: 44px;
  font-size: 16px; font-weight: 600;
  border-radius: 10px; margin-top: 4px;
}
.back-login-btn {
  width: 100%; margin-top: 12px;
  color: rgba(255, 255, 255, 0.5);
}
.back-login-btn:hover { color: #67c23a; }

@media (max-width: 480px) {
  .login-card { width: calc(100% - 32px); padding: 24px 20px 20px; margin: 0 16px; }
  .login-title { font-size: 18px; }
}
</style>
