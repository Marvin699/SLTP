<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/pathPlanning/app'
import { usePointsStore } from '@/stores/pathPlanning/points'
import { useMaterialsStore } from '@/stores/pathPlanning/materials'
import { useUavsStore } from '@/stores/pathPlanning/uavs'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import TopBar from '@/components/pathPlanning/TopBar.vue'
import MapView from '@/components/pathPlanning/MapView.vue'
import Module1 from '@/views/agents/pathPlanning/Module1.vue'
import Module2 from '@/views/agents/pathPlanning/Module2.vue'
import Module3 from '@/views/agents/pathPlanning/Module3.vue'
import Module4 from '@/views/agents/pathPlanning/Module4.vue'
import Module5 from '@/views/agents/pathPlanning/Module5.vue'
import Module6 from '@/views/agents/pathPlanning/Module6.vue'
import Module7 from '@/views/agents/pathPlanning/Module7.vue'
import Module8 from '@/views/agents/pathPlanning/Module8.vue'
import RoutesDetail from '@/views/agents/RoutesDetail.vue'

const router = useRouter()
const app = useAppStore()
const store = usePointsStore()
const matStore = useMaterialsStore()
const uavStore = useUavsStore()
const optStore = useOptimizerStore()

const isLoading = computed(() => store.loading || matStore.loading || uavStore.loading)
const isDayMode = ref(false)
const toggleTheme = () => { isDayMode.value = !isDayMode.value }

const goBack = () => {
  router.push('/home')
}

onMounted(() => {
  store.loadPoints()
})
</script>

<template>
  <div class="path-planning-agent-page" :class="{ 'day-mode': isDayMode }">
    <!-- Top header with back button -->
    <header class="agent-top-header">
      <div class="header-left">
        <el-button @click="goBack" type="primary" plain size="small">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <h1 class="page-title">低空应急智能体</h1>
        <el-tag type="info" size="small">v1.2</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="toggleTheme" circle size="small" class="theme-toggle-btn">
          <el-icon :size="16">
            <Sunny v-if="!isDayMode" />
            <Moon v-else />
          </el-icon>
        </el-button>
      </div>
    </header>

    <!-- TopBar for module switching -->
    <TopBar />

    <!-- Main area -->
    <div class="main-area routes-mode" v-if="app.activeModule === 9">
      <RoutesDetail embedded-full />
    </div>
    <div class="main-area" v-else>
      <!-- Left side panel -->
      <div class="side-panel">
        <div class="panel-body">
          <!-- Module 1: Delivery Points -->
          <Module1 v-if="app.activeModule === 1" />

          <!-- Module 2: Material Requirements -->
          <Module2 v-else-if="app.activeModule === 2" />

          <!-- Module 3: UAV Selection -->
          <Module3 v-else-if="app.activeModule === 3" />

          <!-- Module 4: Path Planning -->
          <Module4 v-else-if="app.activeModule === 4" />

          <!-- Module 5: Plan Diagnosis -->
          <Module5 v-else-if="app.activeModule === 5" />

          <!-- Module 6: Plan Output -->
          <Module6 v-else-if="app.activeModule === 6" />

          <!-- Module 7: Case Management -->
          <Module7 v-else-if="app.activeModule === 7" />

          <!-- Module 8: System Settings -->
          <Module8 v-else-if="app.activeModule === 8" />

          <!-- Placeholder for other modules -->
          <div
            v-else
            class="placeholder"
          >
            <div class="placeholder-icon">
              {{ app.modules.find(m => m.id === app.activeModule)?.icon }}
            </div>
            <div class="placeholder-text">
              {{ app.modules.find(m => m.id === app.activeModule)?.label }}
            </div>
            <div class="placeholder-sub">
              模块开发中...
            </div>
          </div>
        </div>
      </div>

      <!-- Right side map -->
      <MapView :selected-drone-id="optStore.selectedDroneId" />
    </div>

    <!-- Global loading overlay -->
    <Teleport to="body">
      <div
        v-if="isLoading"
        class="loading-veil"
      >
        <div class="spinner" />
        <div class="loading-msg">数据处理中...</div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.path-planning-agent-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #060d1a;
  color: #cdd9f0;
  font-family: 'Noto Sans SC', sans-serif;
}

/* CSS Variables for path planning agent theme */
.path-planning-agent-page {
  --navy: #060d1a;
  --navy2: #0b1628;
  --navy3: #112040;
  --navy4: #1a2e50;
  --teal: #00e5ff;
  --teal2: #00b4cc;
  --amber: #ffb300;
  --red: #ff3d57;
  --green: #00e676;
  --purple: #aa80ff;
  --text: #cdd9f0;
  --text2: #7a93bb;
  --text3: #3d5a80;
  --border: #162540;
  --border2: #1e3560;
  --glow-teal: 0 0 20px rgba(0, 229, 255, 0.25);
  --glow-amber: 0 0 20px rgba(255, 179, 0, 0.25);
  --mono: 'JetBrains Mono', monospace;
  --sans: 'Noto Sans SC', sans-serif;
}

/* 白天模式 - 柔光色系 */
.path-planning-agent-page.day-mode {
  --navy: #f5f0e8;
  --navy2: #ebe4d8;
  --navy3: #e0d8cc;
  --navy4: #d5ccc0;
  --teal: #1a7a7a;
  --teal2: #155e5e;
  --amber: #b8860b;
  --red: #c0392b;
  --green: #27ae60;
  --purple: #7d3c98;
  --text: #3a3530;
  --text2: #6b6560;
  --text3: #9a9590;
  --border: #d0c8bc;
  --border2: #c0b8ac;
  --glow-teal: 0 0 15px rgba(26, 122, 122, 0.15);
  --glow-amber: 0 0 15px rgba(184, 134, 11, 0.15);
}

.day-mode {
  color: var(--text);
}

.agent-top-header {
  min-height: 48px;
  height: 48px;
  background: var(--navy2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  z-index: 200;
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-toggle-btn {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text2) !important;
  transition: all 0.3s;
}

.theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: var(--teal) !important;
  border-color: var(--teal) !important;
}

.page-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--teal);
  margin: 0;
}

.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Left side panel */
.side-panel {
  width: 380px;
  flex-shrink: 0;
  background: var(--navy2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

/* Placeholder module */
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 8px;
}

.placeholder-icon {
  font-size: 40px;
  opacity: 0.3;
}

.placeholder-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--text2);
}

.placeholder-sub {
  font-size: 11px;
  color: var(--text3);
}

/* Loading overlay */
.loading-veil {
  position: fixed;
  inset: 0;
  background: rgba(6, 13, 26, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  flex-direction: column;
  gap: 16px;
}

.spinner {
  width: 44px;
  height: 44px;
  border: 2px solid var(--border);
  border-top-color: var(--teal);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-msg {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--teal);
  letter-spacing: 2px;
}
</style>
