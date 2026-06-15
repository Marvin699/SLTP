<script setup>
import { ref, reactive } from 'vue'

const groups = reactive([
  { id: 1, name: '逐日组' },
  { id: 2, name: '揽星组' },
  { id: 3, name: '御风组' },
  { id: 4, name: '长空组' },
  { id: 5, name: '凌云组' },
  { id: 6, name: '巡天组' },
])

const imageData = reactive({})
groups.forEach(g => {
  imageData[g.id] = {
    slot1: { imageUrl: null, alpha: '', beta: '', rho: '' },
    slot2: { imageUrl: null, alpha: '', beta: '', rho: '' },
  }
})

const expandedGroup = ref(null)

function toggleExpand(id) {
  expandedGroup.value = expandedGroup.value === id ? null : id
}

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

function getSlotData(groupId, slot) {
  return imageData[groupId]?.[slot] || { imageUrl: null, alpha: '', beta: '', rho: '' }
}
</script>

<template>
  <div class="module9">
    <div class="m9-header">
      <h2>🖼 图片管理面板</h2>
      <p class="m9-desc">管理六组图片与参数配置（α、β、ρ）</p>
    </div>

    <div class="m9-groups">
      <div
        v-for="g in groups"
        :key="g.id"
        class="group-section"
        :class="{ expanded: expandedGroup === g.id }"
      >
        <div class="group-header" @click="toggleExpand(g.id)">
          <span class="group-title">{{ g.name }}</span>
          <span class="group-toggle">{{ expandedGroup === g.id ? '▼' : '▶' }}</span>
        </div>

        <div v-show="expandedGroup === g.id" class="group-content">
          <div class="slots-container">
            <div v-for="slotNum in [1, 2]" :key="slotNum" class="slot-box">
              <div class="slot-label">图片 {{ slotNum }}</div>

              <div class="upload-area">
                <label v-if="!getSlotData(g.id, `slot${slotNum}`).imageUrl" class="upload-label">
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleFileUpload(g.id, `slot${slotNum}`, $event)"
                    style="display: none"
                  />
                  <span class="upload-text">点击上传图片</span>
                </label>

                <div v-else class="preview-area">
                  <img
                    :src="getSlotData(g.id, `slot${slotNum}`).imageUrl"
                    class="preview-img"
                    alt="预览"
                  />
                  <button class="clear-btn" @click="clearImage(g.id, `slot${slotNum}`)">✕</button>
                </div>
              </div>

              <div class="params">
                <div class="param-row">
                  <label class="param-label">α</label>
                  <input
                    v-model="imageData[g.id][`slot${slotNum}`].alpha"
                    type="text"
                    class="param-input"
                    placeholder="α"
                  />
                </div>
                <div class="param-row">
                  <label class="param-label">β</label>
                  <input
                    v-model="imageData[g.id][`slot${slotNum}`].beta"
                    type="text"
                    class="param-input"
                    placeholder="β"
                  />
                </div>
                <div class="param-row">
                  <label class="param-label">ρ</label>
                  <input
                    v-model="imageData[g.id][`slot${slotNum}`].rho"
                    type="text"
                    class="param-input"
                    placeholder="ρ"
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
.module9 {
  padding: 16px;
  color: var(--text, #e6ebf5);
}

.m9-header {
  margin-bottom: 16px;
}

.m9-header h2 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: var(--teal, #00e5ff);
}

.m9-desc {
  margin: 0;
  font-size: 12px;
  color: var(--text3, #6b7a8f);
}

.m9-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-section {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  overflow: hidden;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.2);
  transition: background 0.2s;
}

.group-header:hover {
  background: rgba(0, 229, 255, 0.08);
}

.group-title {
  font-size: 14px;
  font-weight: 600;
}

.group-toggle {
  font-size: 12px;
  color: var(--text3, #6b7a8f);
}

.group-content {
  padding: 16px;
}

.slots-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.slot-box {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  padding: 12px;
}

.slot-label {
  font-size: 12px;
  color: var(--text3, #6b7a8f);
  margin-bottom: 8px;
}

.upload-area {
  width: 100%;
  height: 120px;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  overflow: hidden;
  position: relative;
}

.upload-label {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.upload-text {
  font-size: 12px;
  color: var(--text3, #6b7a8f);
}

.preview-area {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 4px;
}

.clear-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(255, 77, 79, 0.9);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  background: rgba(255, 77, 79, 1);
}

.params {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-label {
  width: 24px;
  font-size: 13px;
  font-weight: 600;
  color: var(--teal, #00e5ff);
}

.param-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 6px 8px;
  color: var(--text, #e6ebf5);
  font-size: 12px;
  outline: none;
}

.param-input:focus {
  border-color: var(--teal, #00e5ff);
}

.param-input::placeholder {
  color: var(--text3, #6b7a8f);
}
</style>
