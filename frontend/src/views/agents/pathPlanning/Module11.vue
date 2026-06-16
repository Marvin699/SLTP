<script setup>
import { reactive, onMounted } from 'vue'

const groups = reactive([
  { id: 1, name: '逐日组' },
  { id: 2, name: '长空组' },
  { id: 3, name: '揽星组' },
  { id: 4, name: '御风组' },
  { id: 5, name: '巡天组' },
  { id: 6, name: '凌云组' },
])

const imageData = reactive({
  1: { slot1: { imageUrl: '/images/group_images/1_1.png', alpha: '1.1', beta: '7', rho: '0.05' }, slot2: { imageUrl: '/images/group_images/1_2.png', alpha: '1.2', beta: '6', rho: '0.3' } },
  2: { slot1: { imageUrl: '/images/group_images/2_1.png', alpha: '1.1', beta: '7', rho: '0.2' }, slot2: { imageUrl: '/images/group_images/2_2.png', alpha: '1.1', beta: '6', rho: '0.3' } },
  3: { slot1: { imageUrl: '/images/group_images/3_1.png', alpha: '1.5', beta: '8', rho: '0.21' }, slot2: { imageUrl: '/images/group_images/3_2.png', alpha: '1.4', beta: '7', rho: '0.25' } },
  4: { slot1: { imageUrl: '/images/group_images/4_1.png', alpha: '1.6', beta: '6', rho: '0.23' }, slot2: { imageUrl: '/images/group_images/4_2.png', alpha: '1.7', beta: '8', rho: '0.2' } },
  5: { slot1: { imageUrl: '/images/group_images/5_1.png', alpha: '1.5', beta: '8', rho: '0.21' }, slot2: { imageUrl: '/images/group_images/5_2.png', alpha: '1.1', beta: '6', rho: '0.3' } },
  6: { slot1: { imageUrl: '/images/group_images/6_1.png', alpha: '1.6', beta: '6', rho: '0.23' }, slot2: { imageUrl: '/images/group_images/6_2.png', alpha: '1.7', beta: '8', rho: '0.2' } },
})

onMounted(() => {
  console.log('[Module11] 图片管理看板已加载')
})
</script>

<template>
  <div class="module11">
    <div class="content-wrapper">
      <div class="header">
        <div class="title-row">
          <h1 class="page-title">应急调度智能体看板</h1>
        </div>
      </div>

      <div class="groups-grid">
        <div v-for="g in groups" :key="g.id" class="group-card">
          <div class="group-title">{{ g.name }}</div>

          <div class="slots-row">
            <div v-for="slotNum in [1, 2]" :key="slotNum" class="slot">
              <div class="preview-box">
                <img :src="imageData[g.id][`slot${slotNum}`].imageUrl" class="preview-img" alt="预览" />
              </div>

              <div class="params">
                <div class="param-row">
                  <span class="param-label">α</span>
                  <input 
                    v-model="imageData[g.id][`slot${slotNum}`].alpha" 
                    type="text" 
                    class="param-input"
                  />
                </div>
                <div class="param-row">
                  <span class="param-label">β</span>
                  <input 
                    v-model="imageData[g.id][`slot${slotNum}`].beta" 
                    type="text" 
                    class="param-input"
                  />
                </div>
                <div class="param-row">
                  <span class="param-label">ρ</span>
                  <input 
                    v-model="imageData[g.id][`slot${slotNum}`].rho" 
                    type="text" 
                    class="param-input"
                  />
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

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  margin: 0;
  letter-spacing: 2px;
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
