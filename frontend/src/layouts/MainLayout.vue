<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">✈</span>
          <span class="logo-text">智慧低空应急运输教学平台</span>
        </div>
        <nav class="nav-menu">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            {{ item.title }}
          </router-link>
        </nav>
      </div>
      <div class="header-right">
        <el-badge :value="3" class="notification-badge">
          <el-icon :size="20"><Bell /></el-icon>
        </el-badge>
        <div class="user-info">
          <el-avatar :size="32" :style="{ background: avatarBg }">{{ avatarInitial }}</el-avatar>
          <div class="user-text">
            <span class="username">欢迎您，{{ userStore.greeting }}</span>
            <el-tag :type="userStore.role === 'teacher' ? 'warning' : 'success'" size="small" effect="dark" class="role-tag">
              {{ userStore.roleLabel }}
            </el-tag>
          </div>
        </div>
        <el-button type="danger" text size="small" @click="handleLogout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-button>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- AI小翼全局悬浮球 -->
    <AiAssistantFloat />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import AiAssistantFloat from '@/components/AiAssistantFloat.vue'

const router = useRouter()
const userStore = useUserStore()

const navItems = [
  { path: '/home', title: '首页' },
  { path: '/courses', title: '课程中心' },
  { path: '/training', title: '实训任务' },
  { path: '/evaluation', title: '教学智评' },
  { path: '/resources', title: '学习资源' },
  { path: '/system', title: '系统管理' }
]

const avatarInitial = computed(() => {
  return userStore.role === 'teacher' ? '教' : '学'
})

const avatarBg = computed(() => {
  return userStore.role === 'teacher'
    ? 'linear-gradient(135deg, #e6a23c, #d48806)'
    : 'linear-gradient(135deg, #67c23a, #45a720)'
})

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: #0a1628;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 clamp(16px, 2vw, 32px);
  height: 60px;
  background: linear-gradient(90deg, #0d2137 0%, #1a3a5c 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(90deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  padding: 8px 16px;
  color: #c0c8d4;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-item:hover,
.nav-item.active {
  color: #fff;
  background: rgba(64, 158, 255, 0.2);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-badge {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  color: #c0c8d4;
  font-size: 14px;
}

.role-tag {
  font-size: 11px;
}

.logout-btn {
  margin-left: 4px;
}

.main-content {
  padding: clamp(12px, 1.5vw, 24px);
  min-height: calc(100vh - 60px);
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 1024px) {
  .header-left {
    gap: 16px;
  }
  .nav-menu {
    gap: 2px;
  }
  .nav-item {
    padding: 6px 10px;
    font-size: 13px;
  }
  .logo-text {
    font-size: 14px;
  }
  .username {
    display: none;
  }
}
</style>
