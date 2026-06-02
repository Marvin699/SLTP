<script setup>
defineProps({
  title: { type: String, default: '' },
  width: { type: Number, default: 460 },
})

const emit = defineEmits(['close'])
</script>

<template>
  <div class="right-panel" :style="{ width: width + 'px' }">
    <div class="rp-header">
      <span class="rp-title">{{ title }}</span>
      <div class="rp-actions">
        <slot name="header-actions" />
        <button class="rp-close" @click="emit('close')">✕</button>
      </div>
    </div>
    <div class="rp-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.right-panel {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  background: var(--navy2);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 500;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
}

.rp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--navy3);
  flex-shrink: 0;
}

.rp-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
  font-family: var(--mono);
}

.rp-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rp-close {
  background: none;
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text3);
  cursor: pointer;
  padding: 2px 8px;
  font-size: 12px;
  transition: all 0.2s;
}

.rp-close:hover {
  border-color: var(--red);
  color: var(--red);
}

.rp-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}
</style>
