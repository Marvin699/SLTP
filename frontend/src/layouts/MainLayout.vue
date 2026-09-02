<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="url(#logoGrad)" stroke-width="1.8" stroke-linecap="round">
          <defs>
            <linearGradient id="logoGrad" x1="0" y1="0" x2="24" y2="24">
              <stop offset="0" stop-color="#22d3ee"/>
              <stop offset="1" stop-color="#3b82f6"/>
            </linearGradient>
          </defs>
          <!-- 四旋翼无人机：四个旋翼 + X 机身 + 中央舱 -->
          <circle cx="5" cy="5" r="2.6"/>
          <circle cx="19" cy="5" r="2.6"/>
          <circle cx="5" cy="19" r="2.6"/>
          <circle cx="19" cy="19" r="2.6"/>
          <path d="M7 7l3.2 3.2M17 7l-3.2 3.2M7 17l3.2-3.2M17 17l-3.2-3.2"/>
          <rect x="9.4" y="9.4" width="5.2" height="5.2" rx="1.6" fill="rgba(34,211,238,0.18)" stroke="none"/>
        </svg>
        <span class="logo-text">智慧低空应急运输教学平台</span>
      </div>
      <nav class="nav-menu">
          <router-link
            v-for="item in visibleNavItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            <span class="nav-item-text">{{ item.title }}</span>
          </router-link>
        </nav>
      <div class="header-right">
        <el-badge :value="3" class="notification-badge">
          <el-icon :size="20"><Bell /></el-icon>
        </el-badge>
        <div class="user-info" @click="$router.push('/profile')" style="cursor: pointer;">
          <el-avatar :size="32" :style="{ background: avatarBg }">
            <span v-if="userStore.avatar" style="font-size: 18px; line-height: 1;">{{ userStore.avatar }}</span>
            <span v-else>{{ avatarInitial }}</span>
          </el-avatar>
          <div class="user-text">
            <el-tag :type="userStore.role === 'teacher' ? 'warning' : 'success'" size="small" effect="dark" class="role-tag">
              {{ userStore.roleLabel }}
            </el-tag>
          </div>
        </div>
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button text size="small" class="logout-btn">
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon> 个人中心
              </el-dropdown-item>
              <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
              <el-dropdown-item divided command="logout" style="color: #f56c6c;">
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
import { Bell, SwitchButton, ArrowDown, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import AiAssistantFloat from '@/components/AiAssistantFloat.vue'

const router = useRouter()
const userStore = useUserStore()

// 教师端导航：完整功能
const teacherNavItems = [
  { path: '/home', title: '首页' },
  { path: '/courses', title: '我的课程' },
  { path: '/training', title: '实训任务' },
  { path: '/evaluation', title: '教学智评' },
  { path: '/teacher/monitor', title: '教学监控' },
  { path: '/resources', title: '学习资源' },
  { path: '/system', title: '系统管理' }
]

// 学生端导航：去掉「系统管理」（无权限）
const studentNavItems = [
  { path: '/home', title: '首页' },
  { path: '/courses', title: '我的课程' },
  { path: '/training', title: '实训任务' },
  { path: '/evaluation', title: '教学智评' },
  { path: '/resources', title: '学习资源' }
]

const visibleNavItems = computed(() => {
  return userStore.role === 'teacher' ? teacherNavItems : studentNavItems
})

const avatarInitial = computed(() => {
  return userStore.role === 'teacher' ? '教' : userStore.username?.charAt(0) || '学'
})

const avatarBg = computed(() => {
  return userStore.role === 'teacher'
    ? 'linear-gradient(135deg, #e6a23c, #d48806)'
    : 'linear-gradient(135deg, #67c23a, #45a720)'
})

function handleCommand(command) {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'changePassword') {
    router.push('/change-password')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: transparent;
  color: #fff;
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0 clamp(16px, 2vw, 32px);
  height: 60px;
  background: rgba(4, 9, 18, 0.45);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-self: start;
}

.logo-icon {
  width: 26px;
  height: 26px;
  display: block;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(90deg, #f2f6fa, #7dd3fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-menu {
  display: flex;
  gap: 6px;
  justify-self: center;
}

/* 斜切导航：平行四边形 tab，内容反向倾斜保持文字水平 */
.nav-item {
  padding: 7px 14px;
  font-size: 13.5px;
  color: var(--brand-text-dim, rgba(242, 246, 250, 0.55));
  text-decoration: none;
  white-space: nowrap;
  transform: skewX(-12deg);
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
  transition: all 0.25s ease;
}

.nav-item-text {
  display: inline-block;
  transform: skewX(12deg);
}

.nav-item:hover {
  color: var(--brand-text, #f2f6fa);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.16);
}

.nav-item.active {
  color: #eafcff;
  background: rgba(34, 211, 238, 0.12);
  border-color: rgba(34, 211, 238, 0.45);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.15), inset 0 0 10px rgba(34, 211, 238, 0.06);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  justify-self: end;
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
  width: 100%;
}

@media (min-width: 2560px) {
  .main-content {
    padding-left: clamp(32px, 3vw, 64px);
    padding-right: clamp(32px, 3vw, 64px);
  }
}

@media (max-width: 1024px) {
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
}
</style>
