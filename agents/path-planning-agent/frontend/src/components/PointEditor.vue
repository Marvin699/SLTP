<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePointsStore } from '../stores/points'

const store = usePointsStore()

const isPreview = computed(() => store.editingPoint?._preview === true)
const isNew = computed(() => !store.editingPoint?.id && !isPreview.value)

const form = ref({
  name: '',
  point_type: 'demand',
  longitude: 0,
  latitude: 0,
  demand_weight: 0,
  demand_priority: 3,
  supply_type: '',
  note: '',
})

const supplyOptions = [
  { value: 'repair', label: '抢修类', icon: '🔧' },
  { value: 'life', label: '生活保障类', icon: '🍚' },
  { value: 'medical', label: '医疗救援类', icon: '🏥' },
  { value: 'cold', label: '冷链医疗类', icon: '❄️' },
  { value: 'settle', label: '安置保障类', icon: '🏕' },
]

onMounted(() => {
  if (store.editingPoint && !isPreview.value) {
    form.value = {
      name: store.editingPoint.name || '',
      point_type: store.editingPoint.point_type || 'demand',
      longitude: store.editingPoint.longitude || 0,
      latitude: store.editingPoint.latitude || 0,
      demand_weight: store.editingPoint.demand_weight || 0,
      demand_priority: store.editingPoint.demand_priority || 3,
      supply_type: store.editingPoint.supply_type || '',
      note: store.editingPoint.note || '',
    }
  }

  document.addEventListener('keydown', onEsc)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onEsc)
})

function onEsc(e) {
  if (e.key === 'Escape') {
    store.closeEditor()
  }
}

async function handleSave() {
  if (!form.value.name.trim()) {
    alert('请输入点位名称')
    return
  }

  const data = {
    ...form.value,
    supply_type: form.value.supply_type || null,
    note: form.value.note || null,
  }

  try {
    if (isNew.value) {
      await store.addPoint(data)
    } else {
      await store.updatePoint(store.editingPoint.id, data)
    }
    store.closeEditor()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

const geojsonPreview = computed(() => {
  return JSON.stringify(store.geojson, null, 2)
})

function copyGeoJSON() {
  navigator.clipboard.writeText(geojsonPreview.value)
    .then(() => alert('已复制到剪贴板'))
    .catch(() => alert('复制失败'))
}
</script>

<template>
  <Teleport to="body">
    <div
      class="editor-overlay"
      @click.self="store.closeEditor()"
    >
      <div class="editor-modal">
        <!-- 头部 -->
        <div class="editor-header">
          <h3 class="editor-title">
            {{ isPreview ? 'GeoJSON 数据预览' : (isNew ? '添加点位' : '编辑点位') }}
          </h3>
          <button
            class="close-btn"
            @click="store.closeEditor()"
          >
            ✕
          </button>
        </div>

        <!-- GeoJSON 预览模式 -->
        <div
          v-if="isPreview"
          class="editor-body"
        >
          <div class="preview-info">
            共 {{ store.points.length }} 个点位 · {{ store.centers.length }} 个配送中心 · {{ store.demands.length }} 个需求点
          </div>
          <pre class="geojson-code">{{ geojsonPreview }}</pre>
          <div class="preview-actions">
            <button
              class="save-btn"
              @click="copyGeoJSON"
            >
              复制 JSON
            </button>
            <button
              class="cancel-btn"
              @click="store.closeEditor()"
            >
              关闭
            </button>
          </div>
        </div>

        <!-- 编辑表单模式 -->
        <div
          v-else
          class="editor-body"
        >
          <!-- 点位类型 -->
          <div class="field">
            <label>点位类型</label>
            <div class="type-toggle">
              <button
                class="type-btn"
                :class="{ active: form.point_type === 'center' }"
                @click="form.point_type = 'center'"
              >
                ◈ 配送中心
              </button>
              <button
                class="type-btn"
                :class="{ active: form.point_type === 'demand' }"
                @click="form.point_type = 'demand'"
              >
                ◇ 需求点
              </button>
            </div>
          </div>

          <!-- 名称 -->
          <div class="field">
            <label>名称</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="输入点位名称"
            />
          </div>

          <!-- 坐标 -->
          <div class="coord-row">
            <div class="field">
              <label>纬度 (Latitude)</label>
              <input
                v-model.number="form.latitude"
                type="number"
                step="0.000001"
                min="-90"
                max="90"
              />
            </div>
            <div class="field">
              <label>经度 (Longitude)</label>
              <input
                v-model.number="form.longitude"
                type="number"
                step="0.000001"
                min="-180"
                max="180"
              />
            </div>
          </div>

          <!-- 需求点专属字段 -->
          <template v-if="form.point_type === 'demand'">
            <!-- 物资类型 -->
            <div class="field">
              <label>物资类型</label>
              <select v-model="form.supply_type">
                <option value="">
                  -- 请选择 --
                </option>
                <option
                  v-for="opt in supplyOptions"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.icon }} {{ opt.label }}
                </option>
              </select>
            </div>

            <!-- 需求重量 & 优先级 -->
            <div class="coord-row">
              <div class="field">
                <label>需求重量 (kg)</label>
                <input
                  v-model.number="form.demand_weight"
                  type="number"
                  min="0"
                  step="1"
                />
              </div>
              <div class="field">
                <label>优先级 (1-5)</label>
                <select v-model.number="form.demand_priority">
                  <option :value="1">
                    1 - 最高
                  </option>
                  <option :value="2">
                    2 - 高
                  </option>
                  <option :value="3">
                    3 - 中
                  </option>
                  <option :value="4">
                    4 - 低
                  </option>
                  <option :value="5">
                    5 - 最低
                  </option>
                </select>
              </div>
            </div>
          </template>

          <!-- 备注 -->
          <div class="field">
            <label>备注</label>
            <textarea
              v-model="form.note"
              rows="2"
              placeholder="可选备注信息"
            />
          </div>

          <!-- 操作按钮 -->
          <div class="editor-actions">
            <button
              class="save-btn"
              @click="handleSave"
            >
              {{ isNew ? '创建点位' : '保存修改' }}
            </button>
            <button
              class="cancel-btn"
              @click="store.closeEditor()"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.editor-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 13, 26, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.editor-modal {
  background: var(--navy2);
  border: 1px solid var(--border2);
  border-radius: 16px;
  width: 440px;
  max-width: 90vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 1px rgba(0, 229, 255, 0.2);
}

.editor-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.editor-title {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.close-btn {
  background: none;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text3);
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  border-color: var(--red);
  color: var(--red);
}

.editor-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

/* Form fields */
.field {
  margin-bottom: 14px;
}

.field label {
  display: block;
  font-size: 10px;
  color: var(--text2);
  margin-bottom: 5px;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  padding: 9px 12px;
  font-size: 13px;
  font-family: var(--sans);
  outline: none;
  transition: border-color 0.2s;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: var(--teal);
  box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.1);
}

.field select option {
  background: var(--navy2);
}

.field textarea {
  resize: vertical;
  min-height: 60px;
}

.coord-row {
  display: flex;
  gap: 10px;
}

.coord-row .field {
  flex: 1;
}

/* Type toggle */
.type-toggle {
  display: flex;
  gap: 8px;
}

.type-btn {
  flex: 1;
  padding: 10px;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text2);
  font-size: 12px;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  border-color: var(--border2);
}

.type-btn.active:first-child {
  border-color: #ff6b35;
  background: rgba(255, 107, 53, 0.08);
  color: #ff6b35;
}

.type-btn.active:last-child {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.06);
  color: var(--teal);
}

/* Actions */
.editor-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.save-btn {
  flex: 1;
  padding: 10px 16px;
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  border: none;
  border-radius: 8px;
  color: #000;
  font-size: 13px;
  font-weight: 700;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover {
  box-shadow: var(--glow-teal);
  transform: translateY(-1px);
}

.cancel-btn {
  padding: 10px 16px;
  background: none;
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text2);
  font-size: 13px;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  border-color: var(--text3);
  color: var(--text);
}

/* Preview */
.preview-info {
  font-size: 11px;
  color: var(--text2);
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--navy);
  border-radius: 6px;
  border: 1px solid var(--border);
}

.geojson-code {
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--teal);
  overflow: auto;
  max-height: 400px;
  white-space: pre;
  line-height: 1.6;
}

.preview-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
</style>
