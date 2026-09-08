<template>
  <div>
    <!-- 下滑导航栏 -->
    <transition name="agentnav">
      <div v-show="visible" class="agent-topnav" @mouseenter="cancelHide" @mouseleave="scheduleHide">
        <span class="brand">
          <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="1.8" stroke-linecap="round">
            <circle cx="5" cy="5" r="2.6"/><circle cx="19" cy="5" r="2.6"/>
            <circle cx="5" cy="19" r="2.6"/><circle cx="19" cy="19" r="2.6"/>
            <path d="M7 7l3.2 3.2M17 7l-3.2 3.2M7 17l3.2-3.2M17 17l-3.2-3.2"/>
          </svg>
          智慧低空应急运输教学平台
        </span>
        <nav class="nav-menu">
          <router-link
            v-for="item in items"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: route.path === item.path }"
            @click="hide"
          >
            <span class="nav-item-text">{{ item.title }}</span>
          </router-link>
        </nav>
      </div>
    </transition>

    <!-- 顶部中央把手：视觉提示 + 点击兜底 -->
    <button v-show="!visible" class="nav-handle" @click="show" title="展开导航">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 9l6 6 6-6"/>
      </svg>
      导航
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { navItemsFor } from '@/constants/navigation'

const route = useRoute()
const userStore = useUserStore()
const items = computed(() => navItemsFor(userStore.role))

const visible = ref(false)
let hideTimer = null

function show() {
  clearTimeout(hideTimer)
  visible.value = true
}

function hide() {
  clearTimeout(hideTimer)
  visible.value = false
}

// 鼠标移出导航栏 1.5s 后自动收起
function scheduleHide() {
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => { visible.value = false }, 1500)
}

function cancelHide() {
  clearTimeout(hideTimer)
}

// 鼠标接近屏幕顶部边缘（≤8px）自动滑出
function onMouseMove(e) {
  if (e.clientY <= 8 && !visible.value) show()
}

// 路由变化后立即收起
watch(() => route.fullPath, () => hide())

onMounted(() => document.addEventListener('mousemove', onMouseMove))
onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onMouseMove)
  clearTimeout(hideTimer)
})
</script>

<style scoped>
.agent-topnav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  gap: 24px;
  height: 56px;
  padding: 0 clamp(16px, 2vw, 32px);
  background: rgba(4, 9, 18, 0.72);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #eafcff;
  white-space: nowrap;
}

.brand-icon {
  width: 22px;
  height: 22px;
}

.nav-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

/* 与 MainLayout 一致的斜切导航语言 */
.nav-item {
  padding: 8px 16px;
  font-size: 15px;
  color: rgba(242, 246, 250, 0.55);
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
  color: #f2f6fa;
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.16);
}

.nav-item.active {
  color: #eafcff;
  background: rgba(34, 211, 238, 0.12);
  border-color: rgba(34, 211, 238, 0.45);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.15), inset 0 0 10px rgba(34, 211, 238, 0.06);
}

/* 顶部中央把手 */
.nav-handle {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2990;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 14px 6px;
  font-size: 12px;
  color: #7dd3fc;
  background: rgba(4, 9, 18, 0.55);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-top: none;
  border-radius: 0 0 10px 10px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.nav-handle svg {
  width: 12px;
  height: 12px;
}

.nav-handle:hover {
  color: #eafcff;
  background: rgba(34, 211, 238, 0.15);
  border-color: rgba(34, 211, 238, 0.55);
  padding-top: 6px;
}

/* 下滑/上收动画 */
.agentnav-enter-active,
.agentnav-leave-active {
  transition: transform 0.28s ease, opacity 0.28s ease;
}

.agentnav-enter-from,
.agentnav-leave-to {
  transform: translateY(-100%);
  opacity: 0.6;
}
</style>
