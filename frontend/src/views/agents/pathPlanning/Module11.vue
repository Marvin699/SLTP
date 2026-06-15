<script setup>
import { reactive } from 'vue'

const groups = reactive([
  { id: 1, name: '小组 1' },
  { id: 2, name: '小组 2' },
  { id: 3, name: '小组 3' },
  { id: 4, name: '小组 4' },
  { id: 5, name: '小组 5' },
  { id: 6, name: '小组 6' },
])

const imageData = reactive({
  1: {
    slot1: { imageUrl: null, alpha: '0.5', beta: '0.3', rho: '0.8' },
    slot2: { imageUrl: null, alpha: '0.6', beta: '0.35', rho: '0.75' },
  },
  2: {
    slot1: { imageUrl: null, alpha: '0.6', beta: '0.4', rho: '0.7' },
    slot2: { imageUrl: null, alpha: '0.55', beta: '0.45', rho: '0.65' },
  },
  3: {
    slot1: { imageUrl: null, alpha: '0.45', beta: '0.3', rho: '0.8' },
    slot2: { imageUrl: null, alpha: '0.55', beta: '0.65', rho: '0.6' },
  },
  4: {
    slot1: { imageUrl: null, alpha: '0.7', beta: '0.25', rho: '0.9' },
    slot2: { imageUrl: null, alpha: '0.65', beta: '0.3', rho: '0.85' },
  },
  5: {
    slot1: { imageUrl: null, alpha: '0.35', beta: '0.6', rho: '0.4' },
    slot2: { imageUrl: null, alpha: '0.55', beta: '0.55', rho: '0.55' },
  },
  6: {
    slot1: { imageUrl: null, alpha: '0.55', beta: '0.45', rho: '0.75' },
    slot2: { imageUrl: null, alpha: '0.55', beta: '0.4', rho: '0.8' },
  },
})

function handleFileUpload(groupId, slot, event) {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imageData[groupId][slot].imageUrl = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

function clearImage(groupId, slot) {
  imageData[groupId][slot].imageUrl = null
}
</script>

<template>
  <div class="module11">
    <div class="content-wrapper">
      <div class="header">
        <div class="title-row">
          <h1 class="page-title">应急调度智能体看板</h1>
        </div>
        <p class="page-desc">管理六组图片与参数配置</p>
      </div>

      <div class="groups-grid">
        <div v-for="g in groups" :key="g.id" class="group-card">
          <div class="group-title">{{ g.name }}</div>

          <div class="slots-row">
            <div v-for="slotNum in [1, 2]" :key="slotNum" class="slot">
              <div v-if="!imageData[g.id][`slot${slotNum}`].imageUrl" class="upload-box">
                <label class="upload-label">
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleFileUpload(g.id, `slot${slotNum}`, $event)"
                    style="display: none"
                  />
                  <span class="upload-icon">↑</span>
                  <span class="upload-text">点击上传图片</span>
                </label>
              </div>
              <div v-else class="preview-box">
                <img :src="imageData[g.id][`slot${slotNum}`].imageUrl" class="preview-img" alt="预览" />
                <button class="clear-btn" @click="clearImage(g.id, `slot${slotNum}`)">×</button>
              </div>

              <div class="params">
                <div class="param-row">
                  <span class="param-label">α</span>
                  <input v-model="imageData[g.id][`slot${slotNum}`].alpha" type="text" class="param-input" />
                </div>
                <div class="param-row">
                  <span class="param-label">β</span>
                  <input v-model="imageData[g.id][`slot${slotNum}`].beta" type="text" class="param-input" />
                </div>
                <div class="param-row">
                  <span class="param-label">ρ</span>
                  <input v-model="imageData[g.id][`slot${slotNum}`].rho" type="text" class="param-input" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.module11 {
  background: linear-gradient(135deg, #0a1628 0%, #0d1f35 100%);
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #cdd9f0;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  overflow-y: auto;
}

.content-wrapper {
  width: 100%;
  max-width: 1400px;
  padding: 40px 60px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  width: 100%;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.title-icon {
  font-size: 36px;
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  margin: 0;
  letter-spacing: 2px;
}

.page-desc {
  font-size: 16px;
  color: #7a8ba8;
  margin: 0;
  letter-spacing: 1px;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  width: 100%;
}

.group-card {
  background: #1a2942;
  border: 1px solid #2a3f5f;
  border-radius: 14px;
  padding: 28px;
}

.group-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
  padding-left: 4px;
}

.slots-row {
  display: flex;
  gap: 16px;
}

.slot {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.upload-box {
  width: 100%;
  height: 140px;
  border: 1.5px dashed #3a5070;
  border-radius: 10px;
  background: #0f1a2e;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.upload-box:hover {
  border-color: #4a6080;
  background: #152340;
}

.upload-label {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  gap: 10px;
}

.upload-icon {
  font-size: 26px;
  color: #5a7a9a;
}

.upload-text {
  font-size: 14px;
  color: #5a7a9a;
}

.preview-box {
  position: relative;
  width: 100%;
  height: 140px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 16px;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.clear-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 26px;
  height: 26px;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.clear-btn:hover {
  background: rgba(255, 77, 79, 0.9);
}

.params {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.param-label {
  font-size: 15px;
  font-weight: 600;
  color: #6a8aaa;
  min-width: 18px;
}

.param-input {
  flex: 1;
  height: 38px;
  background: #0f1a2e;
  border: 1px solid #2a3f5f;
  border-radius: 5px;
  padding: 0 12px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.param-input:focus {
  border-color: #4a6080;
}

.param-input::placeholder {
  color: #4a5a78;
}
</style>
