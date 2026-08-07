<template>
  <div class="profile-page">
    <div class="profile-header">
      <h1>个人中心</h1>
      <p class="subtitle">查看和编辑您的账户信息</p>
    </div>

    <div class="profile-content">
      <!-- 左侧：头像展示 -->
      <div class="avatar-section">
        <div class="avatar-display" :style="{ background: avatarBg }">
          <span v-if="userStore.avatar" class="avatar-emoji">{{ userStore.avatar }}</span>
          <span v-else class="avatar-text">{{ avatarInitial }}</span>
        </div>
        <div class="avatar-name">{{ userStore.username }}</div>
        <el-tag :type="userStore.role === 'teacher' ? 'warning' : 'success'" effect="dark" size="large">
          {{ userStore.roleLabel }}
        </el-tag>
        <div class="register-time" v-if="userStore.user?.created_at">
          注册时间：{{ userStore.user.created_at }}
        </div>
      </div>

      <!-- 右侧：信息编辑 -->
      <div class="info-section">
        <!-- 头像选择 -->
        <div class="info-card">
          <div class="card-title">
            <el-icon><Avatar /></el-icon>
            <span>选择头像图标</span>
          </div>
          <p class="card-desc">点击下方图标选择您喜欢的头像，后面有需要可再加上传图片功能</p>
          <div class="emoji-grid">
            <div
              v-for="emoji in emojiList"
              :key="emoji"
              class="emoji-item"
              :class="{ active: userStore.avatar === emoji }"
              @click="selectEmoji(emoji)"
            >
              {{ emoji }}
            </div>
          </div>
          <el-button
            v-if="userStore.avatar"
            text
            size="small"
            class="clear-avatar-btn"
            @click="selectEmoji('')"
          >
            清除头像（使用姓名首字）
          </el-button>
        </div>

        <!-- 基本信息 -->
        <div class="info-card">
          <div class="card-title">
            <el-icon><EditPen /></el-icon>
            <span>基本信息</span>
          </div>
          <el-form :model="form" label-width="90px" class="info-form">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="账号角色">
              <el-input :value="userStore.roleLabel" disabled />
            </el-form-item>
            <el-form-item label="学号" v-if="userStore.isStudent">
              <el-input :value="userStore.user?.student_no || '未设置'" disabled />
            </el-form-item>
            <el-form-item label="班级" v-if="userStore.isStudent">
              <el-input v-model="form.class_name" placeholder="请输入班级" />
            </el-form-item>
            <el-form-item label="小组" v-if="userStore.isStudent">
              <el-input v-model="form.group_no" placeholder="请输入小组" />
            </el-form-item>
          </el-form>
          <div class="form-actions">
            <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
            <el-button @click="handleReset">重置</el-button>
          </div>
        </div>

        <!-- 安全设置 -->
        <div class="info-card">
          <div class="card-title">
            <el-icon><Lock /></el-icon>
            <span>安全设置</span>
          </div>
          <div class="security-row">
            <div class="security-info">
              <div class="security-label">登录密码</div>
              <div class="security-desc">建议定期更换密码，保障账户安全</div>
            </div>
            <el-button @click="$router.push('/change-password')">修改密码</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Avatar, EditPen, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 预设 emoji 头像列表（动物 + 自然 + 符号）
const emojiList = [
  '🦊', '🐼', '🦁', '🐯', '🐨', '🐸', '🐧', '🦅',
  '🐺', '🐙', '🦋', '🐝', '🐞', '🐢', '🐬', '🐳',
  '🌸', '🌺', '🌻', '🌷', '🌹', '🍀', '🌟', '🌈',
  '⚡', '🔥', '❄️', '☀️', '🌙', '⭐', '💎', '🎯',
  '🚀', '✈️', '🛸', '🎁', '🎨', '🎸', '📚', '⚽'
]

const form = reactive({
  username: '',
  class_name: '',
  group_no: '',
})

const saving = ref(false)

const avatarInitial = computed(() => {
  return userStore.username?.charAt(0) || (userStore.role === 'teacher' ? '教' : '学')
})

const avatarBg = computed(() => {
  return userStore.role === 'teacher'
    ? 'linear-gradient(135deg, #e6a23c, #d48806)'
    : 'linear-gradient(135deg, #67c23a, #45a720)'
})

function selectEmoji(emoji) {
  saving.value = true
  // 立即更新头像
  userStore.updateProfile({ avatar: emoji }).then(res => {
    saving.value = false
    if (res.success) {
      ElMessage.success(emoji ? '头像已更新' : '已清除头像')
    } else {
      ElMessage.error(res.message || '头像更新失败')
    }
  })
}

async function handleSave() {
  if (!form.username.trim()) {
    ElMessage.warning('用户名不能为空')
    return
  }
  saving.value = true
  const payload = { username: form.username.trim() }
  if (userStore.isStudent) {
    payload.class_name = form.class_name.trim()
    payload.group_no = form.group_no.trim()
  }
  const res = await userStore.updateProfile(payload)
  saving.value = false
  if (res.success) {
    ElMessage.success('资料保存成功')
  } else {
    ElMessage.error(res.message || '保存失败')
  }
}

function handleReset() {
  form.username = userStore.username
  form.class_name = userStore.user?.class_name || ''
  form.group_no = userStore.user?.group_no || ''
}

onMounted(() => {
  handleReset()
})
</script>

<style scoped>
.profile-page {
  padding: 24px;
  color: #e2e8f0;
  max-width: 1100px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 24px;
}
.profile-header h1 {
  font-size: 24px;
  margin: 0 0 6px;
  color: #fff;
}
.subtitle {
  font-size: 14px;
  color: #8b96a8;
  margin: 0;
}

.profile-content {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}

/* 左侧头像区 */
.avatar-section {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 32px 20px;
  text-align: center;
  height: fit-content;
}
.avatar-display {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
.avatar-emoji {
  font-size: 56px;
  line-height: 1;
}
.avatar-text {
  font-size: 40px;
}
.avatar-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 12px;
}
.register-time {
  font-size: 12px;
  color: #8b96a8;
  margin-top: 16px;
}

/* 右侧信息区 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.info-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 22px 24px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}
.card-title .el-icon {
  color: #409eff;
}
.card-desc {
  font-size: 13px;
  color: #8b96a8;
  margin: 0 0 16px;
}

/* emoji 选择网格 */
.emoji-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}
.emoji-item {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.emoji-item:hover {
  background: rgba(64, 158, 255, 0.15);
  transform: scale(1.1);
}
.emoji-item.active {
  background: rgba(103, 194, 58, 0.2);
  border-color: rgba(103, 194, 58, 0.5);
  box-shadow: 0 0 12px rgba(103, 194, 58, 0.3);
}
.clear-avatar-btn {
  color: #8b96a8 !important;
  margin-top: 4px;
}

/* 表单 */
.info-form {
  margin-top: 12px;
}
.info-form :deep(.el-form-item__label) {
  color: #c0c8d4;
}
.info-form :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.info-form :deep(.el-input__inner) {
  color: #e2e8f0;
}
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

/* 安全设置 */
.security-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}
.security-label {
  font-size: 15px;
  color: #fff;
  margin-bottom: 4px;
}
.security-desc {
  font-size: 13px;
  color: #8b96a8;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  .emoji-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}
</style>
