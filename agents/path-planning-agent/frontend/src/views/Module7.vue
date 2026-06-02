<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCaseStudyStore } from '../stores/case_study'
import { usePointsStore } from '../stores/points'
import { useMaterialsStore } from '../stores/materials'

const caseStore = useCaseStudyStore()
const pointsStore = usePointsStore()
const matStore = useMaterialsStore()

// 弹窗控制
const showModal = ref(false)
const modalTitle = ref('')
const editingId = ref(null)

// 展开的物资配置面板索引
const expandedMaterialIndex = ref(null)

// 表单数据
const form = ref({
  name: '',
  description: '',
  center_data: { name: '', longitude: 0, latitude: 0 },
  demand_points: [],
  material_data: {},
  is_default: false,
})

// 物资配置临时数据（用于弹窗中编辑）
const tempMaterialData = ref({})

onMounted(() => {
  caseStore.loadCases()
})

function openAddModal() {
  modalTitle.value = '添加案例'
  editingId.value = null
  form.value = {
    name: '',
    description: '',
    center_data: { name: '', longitude: 106.317264, latitude: 23.310533 },
    demand_points: [],
    material_data: {},
    is_default: false,
  }
  tempMaterialData.value = {}
  expandedMaterialIndex.value = null
  showModal.value = true
}

function openEditModal(caseData) {
  modalTitle.value = '编辑案例'
  editingId.value = caseData.id
  form.value = {
    name: caseData.name,
    description: caseData.description || '',
    center_data: caseData.center_data,
    demand_points: [...caseData.demand_points],
    material_data: caseData.material_data || {},
    is_default: caseData.is_default,
  }
  tempMaterialData.value = JSON.parse(JSON.stringify(form.value.material_data || {}))
  expandedMaterialIndex.value = null
  showModal.value = true
}

async function handleSave() {
  if (!form.value.name || !form.value.center_data.name) {
    alert('请填写案例名称和配送中心')
    return
  }

  form.value.material_data = JSON.parse(JSON.stringify(tempMaterialData.value))

  let result
  if (editingId.value) {
    result = await caseStore.updateCase(editingId.value, form.value)
  } else {
    result = await caseStore.addCase(form.value)
  }

  if (result) {
    showModal.value = false
  }
}

async function handleDelete(id) {
  if (confirm('确定删除此案例？')) {
    await caseStore.removeCase(id)
  }
}

async function handleSetDefault(id) {
  await caseStore.makeDefault(id)
}

async function handleApply(caseData) {
  await caseStore.applyCase(caseData)
  alert('案例已应用到当前数据')
}

async function saveCurrentAsCase() {
  const center = pointsStore.center
  const demands = pointsStore.demands

  if (!center || demands.length === 0) {
    alert('请先配置配送点数据')
    return
  }

  const materialData = {}
  for (const pt of demands) {
    const assignment = matStore.getAssignment(pt.id)
    if (assignment) {
      materialData[pt.name] = {
        weight: assignment.total_weight,
        priority: assignment.priority,
        supply_types: assignment.supply_types,
        items: assignment.items,
      }
    }
  }

  const caseData = {
    name: `案例_${new Date().toLocaleDateString()}`,
    description: '从当前数据保存的案例',
    center_data: {
      name: center.name,
      longitude: center.longitude,
      latitude: center.latitude,
    },
    demand_points: demands.map(d => ({
      name: d.name,
      longitude: d.longitude,
      latitude: d.latitude,
    })),
    material_data: materialData,
    is_default: false,
  }

  await caseStore.addCase(caseData)
  alert('当前数据已保存为案例')
}

function addDemandPoint() {
  form.value.demand_points.push({
    name: '',
    longitude: 0,
    latitude: 0,
  })
}

function removeDemandPoint(index) {
  const pointName = form.value.demand_points[index].name
  delete tempMaterialData.value[pointName]
  if (expandedMaterialIndex.value === index) {
    expandedMaterialIndex.value = null
  }
  form.value.demand_points.splice(index, 1)
}

function toggleMaterialPanel(index) {
  if (expandedMaterialIndex.value === index) {
    expandedMaterialIndex.value = null
  } else {
    expandedMaterialIndex.value = index
  }
}

function getPointMaterialData(pointName) {
  return tempMaterialData.value[pointName] || null
}

function toggleMaterialCategory(pointName, categoryId) {
  if (!tempMaterialData.value[pointName]) {
    tempMaterialData.value[pointName] = {
      weight: 0,
      priority: 3,
      supply_types: [],
      items: [],
    }
  }
  const data = tempMaterialData.value[pointName]
  if (!data.supply_types) data.supply_types = []
  if (!data.items) data.items = []
  
  const idx = data.supply_types.indexOf(categoryId)
  if (idx > -1) {
    data.supply_types.splice(idx, 1)
  } else {
    data.supply_types.push(categoryId)
  }
}

function isCategorySelected(pointName, categoryId) {
  if (!tempMaterialData.value[pointName]) return false
  return tempMaterialData.value[pointName].supply_types?.includes(categoryId) || false
}

function updateMaterialItem(pointName, itemIndex, field, value) {
  if (!tempMaterialData.value[pointName]) return
  if (!tempMaterialData.value[pointName].items) {
    tempMaterialData.value[pointName].items = []
  }
  if (!tempMaterialData.value[pointName].items[itemIndex]) {
    tempMaterialData.value[pointName].items[itemIndex] = { name: '', unit_weight: 0, qty: 0 }
  }
  tempMaterialData.value[pointName].items[itemIndex][field] = value
  recalculateWeight(pointName)
}

function addMaterialItem(pointName) {
  if (!tempMaterialData.value[pointName]) {
    tempMaterialData.value[pointName] = {
      weight: 0,
      priority: 3,
      supply_types: [],
      items: [],
    }
  }
  tempMaterialData.value[pointName].items.push({
    name: '',
    unit_weight: 0,
    qty: 1,
  })
}

function removeMaterialItem(pointName, index) {
  if (!tempMaterialData.value[pointName]) return
  tempMaterialData.value[pointName].items.splice(index, 1)
  recalculateWeight(pointName)
}

function recalculateWeight(pointName) {
  if (!tempMaterialData.value[pointName]) return
  let total = 0
  for (const item of tempMaterialData.value[pointName].items || []) {
    total += (item.unit_weight || 0) * (item.qty || 0)
  }
  tempMaterialData.value[pointName].weight = total
}

function updatePriority(pointName, priority) {
  if (!tempMaterialData.value[pointName]) {
    tempMaterialData.value[pointName] = {
      weight: 0,
      priority: priority,
      supply_types: [],
      items: [],
    }
  }
  tempMaterialData.value[pointName].priority = priority
}

function priorityLabel(p) {
  const map = { 1: '紧急', 2: '高', 3: '中', 4: '低', 5: '普通' }
  return map[p] || '未知'
}

function priorityColor(p) {
  const map = { 1: '#ff3d57', 2: '#ffb300', 3: '#00e5ff', 4: '#7a93bb', 5: '#3d5a80' }
  return map[p] || '#3d5a80'
}

function closeModal() {
  showModal.value = false
  expandedMaterialIndex.value = null
}

// ─── 数据导入导出 ───

// 物资类别中文名 → ID 映射
const CATEGORY_NAME_TO_ID = {
  '抢修类': 'repair',
  '生活保障类': 'life',
  '医疗救援类': 'medical',
  '冷链医疗类': 'cold',
  '安置保障类': 'settle',
}

const CATEGORY_ID_TO_NAME = {
  repair: '抢修类',
  life: '生活保障类',
  medical: '医疗救援类',
  cold: '冷链医疗类',
  settle: '安置保障类',
}

function exportTemplate() {
  const BOM = '\uFEFF'
  const header = '名称,经度,纬度,物资类别,物资名称,单量(kg),数量'
  const example1 = '怀渠村,106.285000,23.345000,抢修类,柴油发电机,30,2'
  const example2 = '怀渠村,106.285000,23.345000,抢修类,电缆(百米),20,2'
  const example3 = '塘麻村,106.425000,23.085000,生活保障类,矿泉水(箱),12,40'
  const csv = BOM + [header, example1, example2, example3].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '案例数据导入模板.csv'
  a.click()
  URL.revokeObjectURL(url)
}

function triggerImport() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.csv,.txt'
  input.onchange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      importFromCsv(ev.target.result)
    }
    reader.readAsText(file, 'utf-8')
  }
  input.click()
}

function importFromCsv(text) {
  const lines = text.trim().split(/\r?\n/)
  if (lines.length < 2) {
    alert('文件为空或缺少数据行')
    return
  }

  // 解析表头
  const header = parseCsvLine(lines[0])
  const colMap = {}
  header.forEach((h, i) => { colMap[h.trim()] = i })

  // 必需列校验
  const requiredCols = ['名称', '经度', '纬度', '物资类别', '物资名称', '单量(kg)', '数量']
  for (const col of requiredCols) {
    if (!(col in colMap)) {
      alert(`缺少必需列: "${col}"，请使用导出模板`)
      return
    }
  }

  // 按名称聚合需求点
  const pointMap = {} // name → { name, lng, lat, items: [{category, name, unit_weight, qty}] }
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    const cols = parseCsvLine(line)
    const name = (cols[colMap['名称']] || '').trim()
    if (!name) continue

    const lng = parseFloat(cols[colMap['经度']]) || 0
    const lat = parseFloat(cols[colMap['纬度']]) || 0
    const catName = (cols[colMap['物资类别']] || '').trim()
    const itemName = (cols[colMap['物资名称']] || '').trim()
    const unitWeight = parseFloat(cols[colMap['单量(kg)']]) || 0
    const qty = parseInt(cols[colMap['数量']]) || 0

    if (!pointMap[name]) {
      pointMap[name] = { name, longitude: lng, latitude: lat, items: [] }
    }
    // 更新坐标（取最后一次出现的值，通常同一名称坐标相同）
    pointMap[name].longitude = lng
    pointMap[name].latitude = lat

    if (itemName) {
      pointMap[name].items.push({
        category_name: catName,
        category_id: CATEGORY_NAME_TO_ID[catName] || '',
        name: itemName,
        unit_weight: unitWeight,
        qty: qty,
      })
    }
  }

  const points = Object.values(pointMap)
  if (points.length === 0) {
    alert('未解析到有效数据')
    return
  }

  // 填充到表单
  form.value.demand_points = points.map(p => ({
    name: p.name,
    longitude: p.longitude,
    latitude: p.latitude,
  }))

  // 构建物资数据
  const newMaterialData = {}
  for (const p of points) {
    if (p.items.length === 0) continue
    // 聚合物资类别
    const supplyTypes = [...new Set(p.items.map(i => i.category_id).filter(Boolean))]
    const items = p.items.map(i => ({
      name: i.name,
      unit_weight: i.unit_weight,
      qty: i.qty,
      subtotal: i.unit_weight * i.qty,
    }))
    const totalWeight = items.reduce((s, i) => s + i.subtotal, 0)
    newMaterialData[p.name] = {
      weight: totalWeight,
      priority: 3,
      supply_types: supplyTypes,
      items,
    }
  }
  tempMaterialData.value = newMaterialData

  alert(`成功导入 ${points.length} 个需求点`)
}

function parseCsvLine(line) {
  const result = []
  let current = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"') {
      inQuotes = !inQuotes
    } else if (ch === ',' && !inQuotes) {
      result.push(current)
      current = ''
    } else {
      current += ch
    }
  }
  result.push(current)
  return result
}
</script>

<template>
  <div class="module7-container">
    <div class="module-header">
      <h2>案例管理</h2>
      <p class="module-desc">管理案例数据，支持查看、编辑、删除和保存案例</p>
    </div>

    <div class="action-bar">
      <button class="btn btn-primary" @click="openAddModal">+ 添加案例</button>
      <button class="btn btn-secondary" @click="saveCurrentAsCase">保存当前为案例</button>
    </div>

    <div class="case-section">
      <div v-if="caseStore.loading" class="loading-text">加载中...</div>
      <div v-else-if="!caseStore.hasCases" class="empty-text">
        暂无案例，点击"添加案例"创建新案例
      </div>
      <div v-else class="case-list">
        <div
          v-for="caseItem in caseStore.cases"
          :key="caseItem.id"
          class="case-card"
          :class="{ active: caseItem.is_default }"
        >
          <div class="case-header">
            <div class="case-name">
              {{ caseItem.name }}
              <span v-if="caseItem.is_default" class="default-badge">默认</span>
            </div>
            <div class="case-actions">
              <button
                v-if="!caseItem.is_default"
                class="btn btn-sm btn-success"
                @click="handleSetDefault(caseItem.id)"
              >
                设为默认
              </button>
              <button
                class="btn btn-sm btn-secondary"
                @click="openEditModal(caseItem)"
              >
                编辑
              </button>
              <button
                class="btn btn-sm btn-info"
                @click="handleApply(caseItem)"
              >
                应用
              </button>
              <button
                class="btn btn-sm btn-danger"
                @click="handleDelete(caseItem.id)"
              >
                删除
              </button>
            </div>
          </div>
          <div class="case-info">
            <div class="info-row">
              <span class="info-label">配送中心:</span>
              <span class="info-value">{{ caseItem.center_data.name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">需求点数量:</span>
              <span class="info-value">{{ caseItem.demand_points.length }} 个</span>
            </div>
            <div class="info-row" v-if="caseItem.description">
              <span class="info-label">描述:</span>
              <span class="info-value">{{ caseItem.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content large-modal" @click.stop>
          <div class="modal-header">
            <h3>{{ modalTitle }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>案例名称 <span class="required">*</span></label>
              <input v-model="form.name" placeholder="如：渠洋镇应急物资配送案例" />
            </div>
            <div class="form-group">
              <label>案例描述</label>
              <textarea v-model="form.description" rows="2" placeholder="案例描述（可选）"></textarea>
            </div>
            
            <div class="form-section">
              <h4>配送中心</h4>
              <div class="form-row">
                <div class="form-group">
                  <label>名称 <span class="required">*</span></label>
                  <input v-model="form.center_data.name" placeholder="如：渠洋村" />
                </div>
                <div class="form-group">
                  <label>经度</label>
                  <input v-model.number="form.center_data.longitude" type="number" step="0.000001" />
                </div>
                <div class="form-group">
                  <label>纬度</label>
                  <input v-model.number="form.center_data.latitude" type="number" step="0.000001" />
                </div>
              </div>
            </div>

            <div class="form-section">
              <div class="section-header">
                <h4>需求点列表</h4>
                <div class="section-header-actions">
                  <button class="btn btn-sm btn-outline" @click="exportTemplate" title="下载CSV模板文件">导出模板</button>
                  <button class="btn btn-sm btn-outline" @click="triggerImport" title="从CSV文件导入需求点和物资">导入数据</button>
                  <button class="btn btn-sm btn-primary" @click="addDemandPoint">+ 添加</button>
                </div>
              </div>
              <div v-if="form.demand_points.length === 0" class="empty-hint">
                点击上方按钮添加需求点
              </div>
              <div v-else class="demand-list">
                <div v-for="(point, index) in form.demand_points" :key="index" class="demand-item">
                  <div class="demand-item-header">
                    <div class="form-row">
                      <div class="form-group">
                        <label>名称</label>
                        <input v-model="point.name" placeholder="村庄名称" />
                      </div>
                      <div class="form-group">
                        <label>经度</label>
                        <input v-model.number="point.longitude" type="number" step="0.000001" />
                      </div>
                      <div class="form-group">
                        <label>纬度</label>
                        <input v-model.number="point.latitude" type="number" step="0.000001" />
                      </div>
                      <div class="form-group action-group">
                        <button 
                          class="btn btn-sm btn-info expand-btn"
                          :class="{ expanded: expandedMaterialIndex === index }"
                          @click="toggleMaterialPanel(index)"
                          :disabled="!point.name"
                        >
                          {{ expandedMaterialIndex === index ? '▼' : '📦' }} 物资配置
                        </button>
                        <button class="btn btn-sm btn-danger" @click="removeDemandPoint(index)">删除</button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 物资配置面板（直接展开在需求点下方） -->
                  <div v-if="expandedMaterialIndex === index && point.name" class="material-panel">
                    <div class="material-panel-header">
                      <span class="panel-title">物资配置 - {{ point.name }}</span>
                      <div class="panel-summary">
                        <span class="summary-item">
                          总重量: <span class="teal">{{ getPointMaterialData(point.name)?.weight || 0 }} kg</span>
                        </span>
                        <span class="summary-item">
                          优先级: 
                          <select
                            class="priority-select-sm"
                            :value="getPointMaterialData(point.name)?.priority || 3"
                            @change="updatePriority(point.name, parseInt($event.target.value))"
                          >
                            <option value="1" style="color: #ff3d57">紧急</option>
                            <option value="2" style="color: #ffb300">高</option>
                            <option value="3" style="color: #00e5ff">中</option>
                            <option value="4" style="color: #7a93bb">低</option>
                            <option value="5" style="color: #3d5a80">普通</option>
                          </select>
                        </span>
                      </div>
                    </div>
                    
                    <!-- 物资类别选择 -->
                    <div class="material-section">
                      <div class="section-label">物资类别</div>
                      <div class="cat-grid-small">
                        <div
                          v-for="cat in matStore.categories"
                          :key="cat.id"
                          class="cat-item"
                          :class="{ selected: isCategorySelected(point.name, cat.id) }"
                          @click="toggleMaterialCategory(point.name, cat.id)"
                        >
                          <span class="cat-icon">{{ cat.icon }}</span>
                          <span class="cat-name">{{ cat.name }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 物资清单 -->
                    <div class="material-section">
                      <div class="section-label">物资清单</div>
                      <table class="items-table-small">
                        <thead>
                          <tr>
                            <th>物资名称</th>
                            <th>单重(kg)</th>
                            <th>数量</th>
                            <th>小计</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(item, idx) in (getPointMaterialData(point.name)?.items || [])"
                            :key="idx"
                          >
                            <td>
                              <input
                                :value="item.name"
                                class="cell-input-sm"
                                @input="updateMaterialItem(point.name, idx, 'name', $event.target.value)"
                                placeholder="物资名称"
                              />
                            </td>
                            <td>
                              <input
                                :value="item.unit_weight"
                                type="number"
                                min="0"
                                step="0.5"
                                class="cell-input-sm narrow"
                                @input="updateMaterialItem(point.name, idx, 'unit_weight', parseFloat($event.target.value) || 0)"
                              />
                            </td>
                            <td>
                              <input
                                :value="item.qty"
                                type="number"
                                min="0"
                                class="cell-input-sm narrow"
                                @input="updateMaterialItem(point.name, idx, 'qty', parseInt($event.target.value) || 0)"
                              />
                            </td>
                            <td class="mono">{{ (item.unit_weight || 0) * (item.qty || 0) }}</td>
                            <td>
                              <button
                                class="btn-remove-sm"
                                @click="removeMaterialItem(point.name, idx)"
                              >✕</button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                      <button
                        class="btn-add-item-sm"
                        @click="addMaterialItem(point.name)"
                      >+ 添加物资</button>
                    </div>
                  </div>
                  
                  <!-- 物资配置预览（未展开时） -->
                  <div v-if="expandedMaterialIndex !== index && tempMaterialData[point.name]" class="material-preview">
                    <span class="preview-label">物资:</span>
                    <span class="preview-weight">{{ tempMaterialData[point.name].weight || 0 }}kg</span>
                    <span class="preview-priority" :style="{ color: priorityColor(tempMaterialData[point.name].priority || 3) }">
                      {{ priorityLabel(tempMaterialData[point.name].priority || 3) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">取消</button>
            <button class="btn btn-primary" @click="handleSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.module7-container {
  padding: 16px;
}

.module-header {
  margin-bottom: 16px;
}

.module-header h2 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.module-desc {
  margin: 0;
  font-size: 12px;
  color: var(--text3);
}

.action-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.case-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.case-card {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
  background: var(--navy2);
}

.case-card.active {
  border-color: var(--teal);
  background: rgba(0, 255, 200, 0.05);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.case-name {
  font-size: 13px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.default-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--orange);
  color: white;
}

.case-actions {
  display: flex;
  gap: 6px;
}

.case-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.info-label {
  color: var(--text3);
  width: 80px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text2);
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.85;
}

.btn-primary {
  background: var(--teal);
  color: var(--navy);
}

.btn-secondary {
  background: var(--border);
  color: var(--text);
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-info {
  background: #1890ff;
  color: white;
}

.btn-danger {
  background: #f5222d;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 560px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large-modal {
  width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 14px;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text3);
  cursor: pointer;
  font-size: 16px;
}

.modal-body {
  padding: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border);
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
  color: var(--text2);
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--navy2);
  color: var(--text);
  font-size: 12px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--teal);
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-row .form-group {
  flex: 1;
}

.form-row .form-group.action-group {
  flex: 0 0 auto;
  display: flex;
  gap: 4px;
}

.form-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header-actions {
  display: flex;
  gap: 6px;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border2);
  color: var(--text2);
}

.btn-outline:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.section-header h4 {
  margin: 0;
  font-size: 13px;
}

.demand-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.demand-item {
  padding: 12px;
  background: var(--navy2);
  border-radius: 6px;
}

.demand-item-header {
  margin-bottom: 8px;
}

.expand-btn {
  background: rgba(0, 229, 255, 0.08);
  border-color: rgba(0, 229, 255, 0.3);
  color: var(--teal);
}

.expand-btn.expanded {
  background: rgba(0, 229, 255, 0.15);
  border-color: var(--teal);
}

.material-panel {
  margin-top: 12px;
  padding: 12px;
  background: var(--navy);
  border-radius: 4px;
  border: 1px solid var(--border2);
}

.material-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--border);
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--teal);
}

.panel-summary {
  display: flex;
  gap: 12px;
  font-size: 11px;
}

.summary-item {
  color: var(--text3);
}

.summary-item .teal {
  color: var(--teal);
  font-family: var(--mono);
}

.priority-select-sm {
  background: var(--navy2);
  border: 1px solid var(--border2);
  border-radius: 3px;
  color: var(--text);
  padding: 2px 6px;
  font-size: 11px;
  outline: none;
}

.material-section {
  margin-bottom: 12px;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text3);
  margin-bottom: 6px;
}

.cat-grid-small {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid var(--border2);
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  background: var(--navy2);
}

.cat-item:hover {
  border-color: var(--text3);
}

.cat-item.selected {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.08);
}

.cat-icon {
  font-size: 12px;
}

.cat-name {
  color: var(--text2);
}

.cat-item.selected .cat-name {
  color: var(--teal);
}

.items-table-small {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.items-table-small th {
  background: var(--navy2);
  color: var(--text3);
  padding: 4px 8px;
  text-align: left;
  font-weight: 500;
  font-size: 10px;
}

.items-table-small td {
  padding: 4px 8px;
  border-bottom: 1px solid rgba(22, 37, 64, 0.5);
}

.cell-input-sm {
  width: 100%;
  background: var(--navy2);
  border: 1px solid var(--border2);
  border-radius: 3px;
  color: var(--text);
  padding: 3px 6px;
  font-size: 11px;
  outline: none;
}

.cell-input-sm:focus {
  border-color: var(--teal);
}

.cell-input-sm.narrow {
  width: 60px;
}

.btn-remove-sm {
  background: none;
  border: none;
  color: var(--red);
  cursor: pointer;
  font-size: 11px;
  opacity: 0.6;
}

.btn-remove-sm:hover {
  opacity: 1;
}

.btn-add-item-sm {
  margin-top: 6px;
  background: rgba(0, 229, 255, 0.06);
  border: 1px dashed rgba(0, 229, 255, 0.3);
  border-radius: 4px;
  color: var(--teal);
  padding: 4px 8px;
  font-size: 11px;
  cursor: pointer;
  width: 100%;
}

.btn-add-item-sm:hover {
  background: rgba(0, 229, 255, 0.12);
}

.material-preview {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border);
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 11px;
}

.preview-label {
  color: var(--text3);
}

.preview-weight {
  font-family: var(--mono);
  color: var(--teal);
  font-weight: 600;
}

.preview-priority {
  font-weight: 600;
}

.empty-hint {
  text-align: center;
  padding: 16px;
  color: var(--text3);
  font-size: 12px;
}

.required {
  color: #f5222d;
}

.loading-text,
.empty-text {
  text-align: center;
  padding: 24px;
  color: var(--text3);
  font-size: 12px;
}

.mono {
  font-family: var(--mono);
}
</style>