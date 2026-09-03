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
        <button class="icon-btn" title="使用手册" aria-label="使用手册" @click="showManual = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4a1 1 0 0 0-1-1H6.5A2.5 2.5 0 0 0 4 5.5v14z"/>
            <path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>
            <path d="M9 7h6M9 10.5h4"/>
          </svg>
        </button>
        <button class="icon-btn bell-btn" title="通知" aria-label="通知">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.7 21a2 2 0 0 1-3.4 0"/>
          </svg>
          <span class="notif-dot"></span>
        </button>
        <div class="user-info" @click="$router.push('/profile')" title="个人中心">
          <span class="avatar-ring" :class="userStore.role">
            <span v-if="userStore.avatar" class="avatar-face">{{ userStore.avatar }}</span>
            <span v-else class="avatar-face">{{ avatarInitial }}</span>
          </span>
          <span class="role-chip" :class="userStore.role">
            <i class="role-dot"></i>{{ userStore.roleLabel }}
          </span>
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

    <!-- 使用手册弹窗（师生切换） -->
    <UserManualDialog v-model="showManual" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { SwitchButton, ArrowDown, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import AiAssistantFloat from '@/components/AiAssistantFloat.vue'
import UserManualDialog from '@/components/UserManualDialog.vue'

const router = useRouter()
const userStore = useUserStore()
const showManual = ref(false)

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

/* ── 顶栏图标钮（书本 / 铃铛共用语言） ── */
.icon-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  background: rgba(34, 211, 238, 0.07);
  color: #7dd3fc;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.icon-btn svg {
  width: 17px;
  height: 17px;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.icon-btn:hover {
  border-color: rgba(34, 211, 238, 0.55);
  background: rgba(34, 211, 238, 0.14);
  color: #a5f3fc;
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.3), inset 0 0 8px rgba(34, 211, 238, 0.08);
}
.icon-btn:hover svg {
  transform: translateY(-1px) rotate(-4deg);
}
.icon-btn:active {
  transform: scale(0.94);
}

/* 通知呼吸光点（替代数字角标） */
.notif-dot {
  position: absolute;
  top: 6px;
  right: 7px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22d3ee;
  box-shadow: 0 0 6px rgba(34, 211, 238, 0.9);
  animation: notif-pulse 2.6s ease-in-out infinite;
}
@keyframes notif-pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px rgba(34, 211, 238, 0.9); }
  50% { opacity: 0.45; box-shadow: 0 0 2px rgba(34, 211, 238, 0.4); }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 4px 12px 4px 5px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(10, 18, 32, 0.45);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.user-info:hover {
  border-color: rgba(34, 211, 238, 0.45);
  background: rgba(34, 211, 238, 0.08);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.22);
}

/* 渐变光环头像：外环师生双色，内芯深空底 + 首字 */
.avatar-ring {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  padding: 2px;
}
.avatar-ring.teacher {
  background: linear-gradient(135deg, #f59e0b, #92400e);
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.35);
}
.avatar-ring.student {
  background: linear-gradient(135deg, #22d3ee, #3b82f6);
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.35);
}
.avatar-face {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(6, 14, 26, 0.92);
  color: #f0f9ff;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
}

/* 身份徽章：发光圆点 + 文字药丸 */
.role-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 1px;
  white-space: nowrap;
}
.role-chip .role-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.role-chip.teacher {
  color: #fbbf24;
}
.role-chip.teacher .role-dot {
  background: #fbbf24;
  box-shadow: 0 0 6px rgba(251, 191, 36, 0.8);
}
.role-chip.student {
  color: #67e8f9;
}
.role-chip.student .role-dot {
  background: #22d3ee;
  box-shadow: 0 0 6px rgba(34, 211, 238, 0.8);
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
