<script setup>
import { ref, computed, onUnmounted, onMounted, watch } from 'vue'
import { usePointsStore } from '../stores/points'
import { useConfigStore } from '../stores/config'
import { useCaseStudyStore } from '../stores/case_study'
import CoordTable from './CoordTable.vue'
import DistMatrix from './DistMatrix.vue'
import ConfigPanel from '../components/ConfigPanel.vue'

const store = usePointsStore()
const configStore = useConfigStore()
const caseStore = useCaseStudyStore()

const showCaseDropdown = ref(false)

const inputText = ref('')
const inputError = ref('')
const showCoordTable = ref(false)
const showDistMatrix = ref(false)
const showConfig = ref(false)

// 编辑状态
const editingId = ref(null)
const editForm = ref({ name: '', longitude: '', latitude: '' })

function startEdit(point) {
  editingId.value = point.id
  editForm.value = {
    name: point.name,
    longitude: point.longitude,
    latitude: point.latitude,
  }
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(id) {
  const f = editForm.value
  if (!f.name || !f.longitude || !f.latitude) return
  try {
    await store.updatePoint(id, {
      name: f.name,
      longitude: parseFloat(f.longitude),
      latitude: parseFloat(f.latitude),
    })
    editingId.value = null
  } catch (e) {
    alert('更新失败')
  }
}

async function handleDeletePoint(id) {
  if (!confirm('确认删除该点位？')) return
  try {
    await store.removePoint(id)
  } catch (e) {
    alert('删除失败')
  }
}

// 配送中心表单 - 动态从store获取
const centerForm = ref({
  name: '',
  longitude: '',
  latitude: '',
})

// 监听store中的配送中心变化，同步到表单
watch(
  () => store.center,
  (newCenter) => {
    if (newCenter) {
      centerForm.value.name = newCenter.name
      centerForm.value.longitude = newCenter.longitude
      centerForm.value.latitude = newCenter.latitude
    }
  },
  { immediate: true }
)

// 添加需求点表单
const demandForm = ref({ name: '', longitude: '', latitude: '' })

// 地址搜索
const searchQuery = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const searchError = ref('')

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  searchLoading.value = true
  searchError.value = ''
  searchResults.value = []
  try {
    const res = await fetch(`/api/points/geocode/search?keyword=${encodeURIComponent(searchQuery.value)}`)
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      searchError.value = err.detail || '搜索失败'
      return
    }
    const data = await res.json()
    if (data.length > 0) {
      searchResults.value = data
    } else {
      searchError.value = '未找到结果'
    }
  } catch (e) {
    searchError.value = '搜索失败'
  } finally {
    searchLoading.value = false
  }
}

function selectSearchResult(r, type) {
  if (type === 'center') {
    centerForm.value.name = r.name
    centerForm.value.longitude = r.lng
    centerForm.value.latitude = r.lat
  } else {
    demandForm.value.name = r.name
    demandForm.value.longitude = r.lng
    demandForm.value.latitude = r.lat
  }
  searchResults.value = []
  searchQuery.value = ''
}

function handleAddCenter() {
  const c = centerForm.value
  if (!c.name || !c.longitude || !c.latitude) return
  store.setCenter({ name: c.name, longitude: parseFloat(c.longitude), latitude: parseFloat(c.latitude) })
}

function handleAddDemand() {
  const d = demandForm.value
  if (!d.name || !d.longitude || !d.latitude) return
  store.addDemand({ name: d.name, longitude: parseFloat(d.longitude), latitude: parseFloat(d.latitude) })
  demandForm.value = { name: '', longitude: '', latitude: '' }
}

async function handleParse() {
  inputError.value = ''
  const parsed = store.parseInputText(inputText.value)
  if (parsed.length === 0) {
    inputError.value = '未解析到有效坐标（每行: 村名 经度 纬度）'
    return
  }
  try {
    await store.submitBatch(parsed)
  } catch (e) {
    inputError.value = '提交失败'
  }
}

async function handleLoadDefault() {
  inputError.value = ''
  inputText.value = ''
  try {
    await store.loadDefaultCase()
  } catch (e) {
    inputError.value = '加载失败'
  }
}

async function handleGenMatrix() {
  try {
    await store.loadDistanceMatrix()
    showDistMatrix.value = true
  } catch (e) {
    alert('生成失败: ' + (store.error || e.message))
  }
}

function handleShowCoordTable() {
  if (store.points.length === 0) {
    alert('请先添加点位')
    return
  }
  showCoordTable.value = true
}

async function handleSaveModule1() {
  const module1Data = {
    center: store.center ? {
      id: store.center.id,
      name: store.center.name,
      longitude: store.center.longitude,
      latitude: store.center.latitude,
    } : null,
    demands: store.demands.map(d => ({
      id: d.id,
      name: d.name,
      longitude: d.longitude,
      latitude: d.latitude,
    })),
    distance_matrix: store.distMatrix.length > 0 ? store.distMatrix : null,
    saved_at: new Date().toISOString(),
  }
  
  try {
    const response = await fetch('/api/workspace/save/module1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(module1Data),
    })
    const result = await response.json()
    if (result.success) {
      alert('模块一数据已保存！')
    } else {
      alert('保存失败: ' + result.message)
    }
  } catch (e) {
    alert('保存失败: ' + e.message)
  }
}

async function handleExport() {
  try {
    await store.saveGeoJSON()
  } catch (e) {
    alert('导出失败')
  }
}

onMounted(async () => {
  await caseStore.loadCases()
})

async function handleApplyCase(caseData) {
  await caseStore.applyCase(caseData)
  showCaseDropdown.value = false
  alert('案例已应用！')
}

function toggleCaseDropdown() {
  showCaseDropdown.value = !showCaseDropdown.value
}

function closeCaseDropdown() {
  showCaseDropdown.value = false
}
</script>

<template>
  <div class="module1">
    <!-- 地址搜索 -->
    <div class="section">
      <div class="section-title">
        地址搜索
      </div>
      <div class="form-row search-row">
        <input
          v-model="searchQuery"
          class="input-sm"
          placeholder="输入地名搜索经纬度"
          @keyup.enter="handleSearch"
        />
        <button
          class="btn btn-search"
          :disabled="searchLoading"
          @click="handleSearch"
        >
          {{ searchLoading ? '...' : '搜索' }}
        </button>
      </div>
      <div
        v-if="searchError"
        class="error-msg"
      >
        {{ searchError }}
      </div>
      <div
        v-if="searchResults.length > 0"
        class="search-results"
      >
        <div
          v-for="(r, i) in searchResults"
          :key="i"
          class="search-item"
        >
          <div class="search-item-name">
            {{ r.name }}
          </div>
          <div class="search-item-coord">
            {{ r.lng.toFixed(4) }}, {{ r.lat.toFixed(4) }}
          </div>
          <div class="search-item-actions">
            <button
              class="btn-sm center"
              @click="selectSearchResult(r, 'center')"
            >
              设为中心
            </button>
            <button
              class="btn-sm demand"
              @click="selectSearchResult(r, 'demand')"
            >
              设为需求点
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 设置配送中心 -->
    <div class="section">
      <div class="section-title">
        设置配送中心
      </div>
      <div class="form-row">
        <input
          v-model="centerForm.name"
          class="input-sm"
          placeholder="名称"
        />
      </div>
      <div class="form-row cols-2">
        <input
          v-model.number="centerForm.longitude"
          class="input-sm"
          type="number"
          step="0.0001"
          placeholder="经度"
        />
        <input
          v-model.number="centerForm.latitude"
          class="input-sm"
          type="number"
          step="0.0001"
          placeholder="纬度"
        />
      </div>
      <div class="btn-row">
        <button
          class="btn btn-block"
          @click="handleAddCenter"
        >
          确认配送中心
        </button>
        <button
          class="btn btn-map-pick"
          :class="{ active: store.clickMode === 'center' }"
          @click="store.setClickMode(store.clickMode === 'center' ? null : 'center')"
        >
          {{ store.clickMode === 'center' ? '取消选点' : '地图选点' }}
        </button>
      </div>
    </div>

    <!-- 设置需求点 -->
    <div class="section">
      <div class="section-title">
        设置需求点
      </div>
      <div class="form-row">
        <input
          v-model="demandForm.name"
          class="input-sm"
          placeholder="村名"
        />
      </div>
      <div class="form-row cols-2">
        <input
          v-model="demandForm.longitude"
          class="input-sm"
          type="number"
          step="0.0001"
          placeholder="经度"
        />
        <input
          v-model="demandForm.latitude"
          class="input-sm"
          type="number"
          step="0.0001"
          placeholder="纬度"
        />
      </div>
      <div class="btn-row">
        <button
          class="btn btn-block"
          @click="handleAddDemand"
        >
          + 添加需求点
        </button>
        <button
          class="btn btn-map-pick"
          :class="{ active: store.clickMode === 'demand' }"
          @click="store.setClickMode(store.clickMode === 'demand' ? null : 'demand')"
        >
          {{ store.clickMode === 'demand' ? '取消选点' : '地图选点' }}
        </button>
      </div>
    </div>

    <!-- 批量输入 -->
    <div class="section">
      <div class="section-title">
        批量获取村庄坐标
      </div>
      <textarea
        v-model="inputText"
        class="input-area"
        placeholder="每行格式: 村名 经度 纬度"
        rows="4"
      ></textarea>
      <div
        v-if="inputError"
        class="error-msg"
      >
        {{ inputError }}
      </div>
      <div class="btn-row">
        <button
          class="btn btn-primary"
          @click="handleParse"
        >
          解析并标注
        </button>
        <button
          class="btn btn-secondary"
          @click="handleLoadDefault"
        >
          加载默认案例
        </button>
      </div>
    </div>

    <!-- 当前点位统计 -->
    <div class="section">
      <div class="stat-row">
        <div class="stat-item">
          <span class="stat-num center-num">{{ store.center ? 1 : 0 }}</span>
          <span class="stat-label">配送中心</span>
        </div>
        <div class="stat-item">
          <span class="stat-num demand-num">{{ store.demands.length }}</span>
          <span class="stat-label">需求点</span>
        </div>
      </div>
    </div>

    <!-- 点位编辑 -->
    <div
      v-if="store.points.length > 0"
      class="section"
    >
      <div class="section-title">
        点位编辑
      </div>

      <!-- 配送中心 -->
      <div
        v-if="store.center"
        class="point-edit-item"
      >
        <template v-if="editingId === store.center.id">
          <div class="edit-form">
            <input
              v-model="editForm.name"
              class="input-sm"
              placeholder="名称"
            />
            <div class="form-row cols-2">
              <input
                v-model="editForm.longitude"
                class="input-sm"
                type="number"
                step="0.0001"
                placeholder="经度"
              />
              <input
                v-model="editForm.latitude"
                class="input-sm"
                type="number"
                step="0.0001"
                placeholder="纬度"
              />
            </div>
            <div class="edit-actions">
              <button
                class="btn btn-save-sm"
                @click="saveEdit(store.center.id)"
              >
                保存
              </button>
              <button
                class="btn btn-cancel-sm"
                @click="cancelEdit"
              >
                取消
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="point-edit-row">
            <span class="point-tag center">C</span>
            <span class="point-edit-name">{{ store.center.name }}</span>
            <span class="point-edit-coord">
              {{ store.center.longitude.toFixed(4) }}, {{ store.center.latitude.toFixed(4) }}
            </span>
            <button
              class="btn-icon"
              @click="startEdit(store.center)"
            >
              ✎
            </button>
          </div>
        </template>
      </div>

      <!-- 需求点列表 -->
      <div class="demand-list">
        <div
          v-for="(d, i) in store.demands"
          :key="d.id"
          class="point-edit-item"
        >
          <template v-if="editingId === d.id">
            <div class="edit-form">
              <input
                v-model="editForm.name"
                class="input-sm"
                placeholder="名称"
              />
              <div class="form-row cols-2">
                <input
                  v-model="editForm.longitude"
                  class="input-sm"
                  type="number"
                  step="0.0001"
                  placeholder="经度"
                />
                <input
                  v-model="editForm.latitude"
                  class="input-sm"
                  type="number"
                  step="0.0001"
                  placeholder="纬度"
                />
              </div>
              <div class="edit-actions">
                <button
                  class="btn btn-save-sm"
                  @click="saveEdit(d.id)"
                >
                  保存
                </button>
                <button
                  class="btn btn-cancel-sm"
                  @click="cancelEdit"
                >
                  取消
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="point-edit-row">
              <span class="point-tag demand">{{ i + 1 }}</span>
              <span class="point-edit-name">{{ d.name }}</span>
              <span class="point-edit-coord">
                {{ d.longitude.toFixed(4) }}, {{ d.latitude.toFixed(4) }}
              </span>
              <button
                class="btn-icon"
                @click="startEdit(d)"
              >
                ✎
              </button>
              <button
                class="btn-icon danger"
                @click="handleDeletePoint(d.id)"
              >
                ✕
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 功能按钮 -->
    <div class="section">
      <div class="section-title">
        数据操作
      </div>
      <div class="btn-col">
        <button
          class="btn btn-action"
          @click="handleShowCoordTable"
        >
          📋 坐标信息表
        </button>
        <button
          class="btn btn-action"
          :disabled="store.points.length < 2"
          @click="handleGenMatrix"
        >
          📊 生成距离矩阵
        </button>
        <button
          class="btn btn-action"
          :disabled="store.points.length === 0"
          @click="handleExport"
        >
          ⬇ 导出 GeoJSON
        </button>
        <button
          class="btn btn-action config-btn"
          @click="showConfig = true"
        >
          🤖 AI识别配置
        </button>
        <div class="case-select-wrapper">
          <button
            class="btn btn-action primary"
            @click="toggleCaseDropdown"
          >
            📂 选择案例
          </button>
          <div
            v-if="showCaseDropdown"
            class="case-dropdown"
          >
            <div
              class="case-dropdown-item case-dropdown-header"
            >
              <span>选择案例加载配送点</span>
            </div>
            <div
              v-for="caseItem in caseStore.cases"
              :key="caseItem.id"
              class="case-dropdown-item"
              @click="handleApplyCase(caseItem)"
            >
              <span class="case-name">{{ caseItem.name }}</span>
              <span v-if="caseItem.is_default" class="case-default">默认</span>
            </div>
            <div
              v-if="caseStore.cases.length === 0"
              class="case-dropdown-empty"
            >
              暂无案例，请在案例管理模块添加
            </div>
          </div>
        </div>
        <button
          class="btn btn-success"
          :disabled="!store.center || store.demands.length === 0"
          @click="handleSaveModule1"
        >
          📋 备份数据
        </button>
      </div>
    </div>

    <!-- 配置面板 -->
    <ConfigPanel
      v-if="showConfig"
      module-key="module1"
      @close="showConfig = false"
    />

    <!-- 悬浮窗口：坐标信息表 -->
    <CoordTable
      v-if="showCoordTable"
      @close="showCoordTable = false"
    />

    <!-- 悬浮窗口：距离矩阵 -->
    <DistMatrix
      v-if="showDistMatrix"
      @close="showDistMatrix = false"
    />
  </div>
</template>

<style scoped>
.module1 {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

/* Form */
.form-row {
  margin-bottom: 6px;
}

.form-row.cols-2 {
  display: flex;
  gap: 6px;
}

.input-sm {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text);
  padding: 7px 10px;
  font-size: 12px;
  font-family: var(--sans);
  outline: none;
  transition: border-color 0.2s;
}

.input-sm:focus {
  border-color: var(--teal);
}

.input-area {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text);
  padding: 8px 10px;
  font-size: 11px;
  font-family: var(--mono);
  line-height: 1.5;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.input-area:focus {
  border-color: var(--teal);
}

.input-area::placeholder {
  color: var(--text3);
  font-family: var(--sans);
}

.error-msg {
  padding: 6px 8px;
  background: rgba(255, 61, 87, 0.08);
  border: 1px solid rgba(255, 61, 87, 0.2);
  border-radius: 4px;
  font-size: 10px;
  color: var(--red);
  margin-bottom: 6px;
}

/* Buttons */
.btn {
  padding: 7px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-family: var(--sans);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
  background: var(--navy3);
  color: var(--text2);
  border: 1px solid var(--border2);
  margin-top: 4px;
}

.btn-block:hover:not(:disabled) {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-row {
  display: flex;
  gap: 6px;
}

.btn-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.btn-primary {
  flex: 1;
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  color: #000;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--glow-teal);
}

.btn-secondary {
  flex: 1;
  background: var(--navy);
  color: var(--text2);
  border: 1px solid var(--border2);
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--text3);
  color: var(--text);
}

.btn-action {
  width: 100%;
  background: var(--navy);
  color: var(--text2);
  border: 1px solid var(--border2);
  text-align: left;
  padding: 9px 12px;
}

.btn-action:hover:not(:disabled) {
  border-color: var(--teal);
  color: var(--teal);
  background: rgba(0, 229, 255, 0.04);
}

/* Stats */
.stat-row {
  display: flex;
  gap: 10px;
}

.stat-item {
  flex: 1;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.stat-num {
  font-family: var(--mono);
  font-size: 22px;
  font-weight: 700;
  display: block;
}

.stat-num.center-num {
  color: #ff6b35;
}

.stat-num.demand-num {
  color: var(--teal);
}

.stat-label {
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.5px;
}

/* Search */
.search-row {
  display: flex;
  gap: 6px;
}

.btn-search {
  flex-shrink: 0;
  background: var(--navy3);
  color: var(--text2);
  border: 1px solid var(--border2);
  padding: 7px 10px;
  font-size: 11px;
}

.btn-search:hover:not(:disabled) {
  border-color: var(--teal);
  color: var(--teal);
}

.search-results {
  margin-top: 6px;
  max-height: 160px;
  overflow-y: auto;
  border: 1px solid var(--border2);
  border-radius: 6px;
  background: var(--navy);
}

.search-item {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
}

.search-item:last-child {
  border-bottom: none;
}

.search-item-name {
  font-size: 11px;
  color: var(--text);
  margin-bottom: 2px;
}

.search-item-coord {
  font-size: 10px;
  font-family: var(--mono);
  color: var(--text3);
  margin-bottom: 4px;
}

.search-item-actions {
  display: flex;
  gap: 4px;
}

.btn-sm {
  padding: 3px 8px;
  font-size: 10px;
  border-radius: 4px;
  border: 1px solid var(--border2);
  background: var(--navy2);
  color: var(--text3);
  cursor: pointer;
  font-family: var(--sans);
}

.btn-sm.center {
  border-color: rgba(255, 107, 53, 0.3);
  color: #ff6b35;
}

.btn-sm.center:hover {
  background: rgba(255, 107, 53, 0.1);
}

.btn-sm.demand {
  border-color: rgba(0, 229, 255, 0.3);
  color: var(--teal);
}

.btn-sm.demand:hover {
  background: rgba(0, 229, 255, 0.1);
}

/* Map pick button */
.btn-map-pick {
  flex-shrink: 0;
  background: var(--navy);
  color: var(--text3);
  border: 1px solid var(--border2);
  font-size: 10px;
  padding: 7px 10px;
}

.btn-map-pick:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-map-pick.active {
  background: rgba(0, 229, 255, 0.1);
  border-color: var(--teal);
  color: var(--teal);
}

/* Point edit */
.demand-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 6px;
}

.point-edit-item {
  border-bottom: 1px solid var(--border);
}

.point-edit-item:last-child {
  border-bottom: none;
}

.point-edit-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
}

.point-tag {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
  font-family: var(--mono);
}

.point-tag.center {
  background: rgba(255, 107, 53, 0.15);
  border: 1px solid rgba(255, 107, 53, 0.3);
  color: #ff6b35;
}

.point-tag.demand {
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: var(--teal);
}

.point-edit-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--text);
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.point-edit-coord {
  font-size: 9px;
  font-family: var(--mono);
  color: var(--text3);
  flex-shrink: 0;
}

.btn-icon {
  background: none;
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text3);
  cursor: pointer;
  padding: 2px 6px;
  font-size: 11px;
  flex-shrink: 0;
}

.btn-icon:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-icon.danger:hover {
  border-color: var(--red);
  color: var(--red);
}

/* Edit form */
.edit-form {
  padding: 8px;
  background: var(--navy);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.edit-actions {
  display: flex;
  gap: 6px;
}

.btn-save-sm {
  flex: 1;
  padding: 5px 10px;
  font-size: 10px;
  border-radius: 5px;
  border: none;
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  color: #000;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--sans);
}

.btn-cancel-sm {
  flex: 1;
  padding: 5px 10px;
  font-size: 10px;
  border-radius: 5px;
  border: 1px solid var(--border2);
  background: var(--navy2);
  color: var(--text3);
  cursor: pointer;
  font-family: var(--sans);
}

/* Case dropdown */
.case-select-wrapper {
  position: relative;
  margin-bottom: 6px;
}

.case-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.case-dropdown-header {
  background: var(--navy2);
  cursor: default;
  font-weight: 600;
  color: var(--teal);
}

.case-dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
  transition: background 0.2s;
}

.case-dropdown-item:last-child {
  border-bottom: none;
}

.case-dropdown-item:hover {
  background: rgba(0, 229, 255, 0.08);
}

.case-dropdown-item .case-name {
  font-size: 11px;
  color: var(--text2);
}

.case-dropdown-item:hover .case-name {
  color: var(--teal);
}

.case-default {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
  background: rgba(255, 107, 53, 0.15);
  color: #ff6b35;
}

.case-dropdown-empty {
  padding: 12px;
  text-align: center;
  font-size: 11px;
  color: var(--text3);
}

/* Success button */
.btn-success {
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: var(--teal);
}

.btn-success:hover:not(:disabled) {
  background: rgba(0, 229, 255, 0.15);
  border-color: var(--teal);
}
</style>
