<template>
  <Teleport to="body">
    <Transition name="sim-fade">
      <div v-if="modelValue" class="sim-player-mask" @click.self="close">
        <div class="sim-player-head">
          <span class="sim-title">🛰 {{ video?.title || '虚拟仿真' }}</span>
          <span v-if="video?.group_no" class="sim-group">{{ video.group_no }} 组</span>
          <button class="sim-close-btn" title="关闭 (ESC)" @click="close">✕</button>
        </div>

        <div class="sim-player-body" @click.self="close">
          <video
            v-if="modelValue && video"
            ref="videoEl"
            class="sim-video"
            :src="video.url"
            controls
            autoplay
            playsinline
            @ended="onEnded"
          ></video>
          <p class="sim-tip">视频结束或按 ESC / 点击空白处退出</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  video: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'ended'])

const videoEl = ref(null)

function close() {
  emit('update:modelValue', false)
}

function onEnded() {
  emit('ended')
  close()
}

function onEsc(e) {
  if (e.key === 'Escape' && props.modelValue) close()
}

// 关闭时暂停并清空，避免后台继续拉流占用带宽
watch(() => props.modelValue, (open) => {
  if (!open && videoEl.value) {
    videoEl.value.pause()
  }
})

onMounted(() => document.addEventListener('keydown', onEsc))
onUnmounted(() => document.removeEventListener('keydown', onEsc))
</script>

<style scoped>
.sim-player-mask {
  position: fixed;
  inset: 0;
  z-index: 4000;
  background: rgba(2, 6, 16, 0.94);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(6px);
}
.sim-player-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 22px;
  flex-shrink: 0;
}
.sim-title {
  color: #e6edf5;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.sim-group {
  color: #22d3ee;
  font-size: 12px;
  border: 1px solid rgba(34, 211, 238, 0.4);
  border-radius: 999px;
  padding: 1px 10px;
}
.sim-close-btn {
  margin-left: auto;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
  color: #c9d4e2;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}
.sim-close-btn:hover {
  color: #fff;
  border-color: rgba(34, 211, 238, 0.6);
  background: rgba(34, 211, 238, 0.12);
}
.sim-player-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 3vw 18px;
}
.sim-video {
  width: 100%;
  max-height: 86vh;
  border-radius: 12px;
  background: #000;
  outline: none;
  box-shadow: 0 20px 80px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(34, 211, 238, 0.15);
}
.sim-tip {
  margin-top: 12px;
  color: rgba(200, 212, 226, 0.45);
  font-size: 12px;
  letter-spacing: 0.5px;
}
.sim-fade-enter-active,
.sim-fade-leave-active {
  transition: opacity 0.25s ease;
}
.sim-fade-enter-from,
.sim-fade-leave-to {
  opacity: 0;
}
</style>
