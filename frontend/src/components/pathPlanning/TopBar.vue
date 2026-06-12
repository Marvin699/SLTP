<script setup>
import { useAppStore } from '@/stores/pathPlanning/app'

const app = useAppStore()
</script>

<template>
  <div class="topbar">
    <div class="topbar-logo">
      <span class="logo-icon">◈</span>
      <span class="logo-text">无人机应急调度智能体</span>
    </div>

    <nav class="topbar-tabs">
      <button
        v-for="m in app.modules"
        :key="m.id"
        class="tab-btn"
        :class="{ active: app.activeModule === m.id }"
        @click="app.setModule(m.id)"
      >
        <span class="tab-icon">{{ m.icon }}</span>
        <span class="tab-label">{{ m.label }}</span>
      </button>
    </nav>

    <div class="topbar-right">
      <span class="ver-tag">v1.2</span>
    </div>
  </div>
</template>

<style scoped>
.topbar {
  min-height: 62px;
  height: 62px;
  background: var(--navy2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 16px;
  flex-shrink: 0;
  z-index: 100;
  position: relative;
}

.topbar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 22px;
  color: var(--teal);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.logo-text {
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--teal);
  letter-spacing: 1px;
  white-space: nowrap;
}

.topbar-tabs {
  display: flex;
  gap: 4px;
  flex: 1;
  justify-content: center;
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: none;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text3);
  font-family: var(--sans);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--text2);
  background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
  background: rgba(0, 229, 255, 0.1);
  color: var(--teal);
  border-color: rgba(0, 229, 255, 0.25);
}

.tab-icon {
  font-size: 16px;
}

.tab-label {
  font-size: 13px;
}

.topbar-right {
  flex-shrink: 0;
}

.ver-tag {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text3);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: 4px;
  letter-spacing: 1px;
}
</style>
