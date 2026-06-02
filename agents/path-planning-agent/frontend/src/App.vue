<script setup>
import { onMounted, computed } from 'vue'
import { useAppStore } from './stores/app'
import { usePointsStore } from './stores/points'
import { useMaterialsStore } from './stores/materials'
import { useUavsStore } from './stores/uavs'
import { useOptimizerStore } from './stores/optimizer'
import TopBar from './components/TopBar.vue'
import MapView from './components/MapView.vue'
import Module1 from './views/Module1.vue'
import Module2 from './views/Module2.vue'
import Module3 from './views/Module3.vue'
import Module4 from './views/Module4.vue'
import Module5 from './views/Module5.vue'
import Module6 from './views/Module6.vue'
import Module7 from './views/Module7.vue'
import Module8 from './views/Module8.vue'

const app = useAppStore()
const store = usePointsStore()
const matStore = useMaterialsStore()
const uavStore = useUavsStore()
const optStore = useOptimizerStore()

const isLoading = computed(() => store.loading || matStore.loading || uavStore.loading)

onMounted(() => {
  store.loadPoints()
})
</script>

<template>
  <div class="app-root">
    <!-- 顶部导航栏 -->
    <TopBar />

    <!-- 主体区域 -->
    <div class="main-area">
      <!-- 左侧固定面板 -->
      <div class="side-panel">
        <div class="panel-body">
          <!-- 模块1：配送点设置 -->
          <Module1 v-if="app.activeModule === 1" />

          <!-- 模块2：物资需求 -->
          <Module2 v-else-if="app.activeModule === 2" />

          <!-- 模块3：无人机选型 -->
          <Module3 v-else-if="app.activeModule === 3" />

          <!-- 模块4：路径规划 -->
          <Module4 v-else-if="app.activeModule === 4" />

          <!-- 模块5：方案诊断 -->
          <Module5 v-else-if="app.activeModule === 5" />

          <!-- 模块6：方案优出 -->
          <Module6 v-else-if="app.activeModule === 6" />

          <!-- 模块7：教学管理 -->
          <Module7 v-else-if="app.activeModule === 7" />

          <!-- 模块8：系统设置 -->
          <Module8 v-else-if="app.activeModule === 8" />

          <!-- 其他模块占位 -->
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

      <!-- 右侧地图 -->
      <MapView :selected-drone-id="optStore.selectedDroneId" />
    </div>

    <!-- 全局加载状态 -->
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
.app-root {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧固定面板 */
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

/* 占位模块 */
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

/* Loading */
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