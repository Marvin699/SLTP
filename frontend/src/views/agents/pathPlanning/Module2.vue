<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { usePointsStore } from '@/stores/pathPlanning/points'
import { useMaterialsStore } from '@/stores/pathPlanning/materials'
import { useConfigStore } from '@/stores/pathPlanning/config'
import { useCaseStudyStore } from '@/stores/pathPlanning/case_study'
import ConfigPanel from '@/components/pathPlanning/ConfigPanel.vue'
import RightPanel from '@/components/pathPlanning/RightPanel.vue'

const pointsStore = usePointsStore()
const matStore = useMaterialsStore()
const configStore = useConfigStore()
const caseStore = useCaseStudyStore()

const editingPointId = ref(null)
const editingItems = ref(false)
const showConfig = ref(false)
const showCaseDropdown = ref(false)

// supply_type 英文 key → 中文标签映射（与后端 5 大类别一致）
const SUPPLY_TYPE_LABELS = {
  repair: '抢修类',
  life: '生活保障类',
  medical: '医疗救援类',
  cold: '冷链医疗类',
  settle: '安置保障类',
  // 兼容旧数据
  medicine: '医疗救援类',
  food: '生活保障类',
  water: '生活保障类',
  daily: '生活保障类',
  equipment: '抢修类',
}

function supplyTypeLabel(type) {
  return SUPPLY_TYPE_LABELS[type] || type
}

onMounted(async () => {
  await matStore.loadCategories()
  await caseStore.loadCases()
  
  // 先检查当前配送点，再决定是否加载数据库数据
  if (pointsStore.demands.length > 0) {
    await matStore.loadFromDb()
    
    // 检查加载的数据是否与当前配送点匹配
    const currentDemandNames = pointsStore.demands.map(d => d.name)
    const loadedAssignmentNames = Object.values(matStore.assignments).map(a => a.point_name)
    
    // 如果不匹配，清除加载的数据
    const hasMismatch = loadedAssignmentNames.some(name => !currentDemandNames.includes(name))
    if (hasMismatch) {
      matStore.clearAssignments()
    }
  }
  
  if (matStore.assignedCount === 0) {
    await loadFromWorkspace()
  }
})

// 监听需求点变化，自动重新加载物资分配
watch(
  () => pointsStore.demands.length,
  async (newLength, oldLength) => {
    if (newLength > 0 && newLength !== oldLength) {
      await matStore.loadFromDb()
    }
  }
)

async function loadFromWorkspace() {
  try {
    const response = await fetch('/api/path-planning/workspace/load/module2')
    const result = await response.json()
    if (result.success && result.data?.assignments) {
      const newAssignments = { ...matStore.assignments }
      for (const a of result.data.assignments) {
        if (a.point_id && a.materials && a.materials.length > 0) {
          newAssignments[a.point_id] = {
            point_id: a.point_id,
            point_name: a.point_name,
            items: a.materials,
            total_weight: a.total_weight || 0,
            priority: a.priority || 3,
            delivery_mode: a.delivery_mode || 'optional',
            special_requirements: a.special_requirements || '',
            risk_warnings: [],
            supply_types: ['常规'],
            category_ids: [],
          }
        }
      }
      matStore.assignments = newAssignments
    }
  } catch (e) {
    console.warn('[Module2] 从工作空间加载数据失败:', e.message)
  }
}

function openEditPanel(pt) {
  editingPointId.value = pt.id
  editingItems.value = false
}

function closeEditPanel() {
  editingPointId.value = null
  editingItems.value = false
}

const editingPoint = computed(() => {
  if (!editingPointId.value) return null
  return pointsStore.demands.find(p => p.id === editingPointId.value)
})

const editingAssignment = computed(() => {
  if (!editingPointId.value) return null
  return matStore.getAssignment(editingPointId.value)
})

function priorityLabel(p) {
  const map = { 1: '紧急', 2: '高', 3: '中', 4: '低', 5: '普通' }
  return map[p] || '未知'
}

function priorityColor(p) {
  const map = { 1: '#ff3d57', 2: '#ffb300', 3: '#00e5ff', 4: '#7a93bb', 5: '#3d5a80' }
  return map[p] || '#3d5a80'
}

const unassignedCount = computed(() => {
  return pointsStore.demands.length - matStore.assignedCount
})

async function handleSaveModule2() {
  const module2Data = {
    assignments: pointsStore.demands.map(pt => {
      const assignment = matStore.getAssignment(pt.id)
      return {
        point_id: pt.id,
        point_name: pt.name,
        materials: assignment?.items || [],
        total_weight: assignment?.total_weight || 0,
        priority: assignment?.priority || 3,
        delivery_mode: assignment?.delivery_mode || 'optional',
        special_requirements: assignment?.special_requirements || '',
      }
    }),
    saved_at: new Date().toISOString(),
  }
  
  try {
    const response = await fetch('/api/path-planning/workspace/save/module2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(module2Data),
    })
    const result = await response.json()
    if (result.success) {
      alert('模块二数据已保存！')
    } else {
      alert('保存失败: ' + result.message)
    }
  } catch (e) {
    alert('保存失败: ' + e.message)
  }
}

async function handleApplyCase(caseData) {
  if (!caseData.material_data) {
    alert('该案例没有物资配置数据')
    showCaseDropdown.value = false
    return
  }
  
  const currentDemandNames = pointsStore.demands.map(d => d.name)
  const caseDemandNames = Object.keys(caseData.material_data)
  
  const matchedCount = caseDemandNames.filter(name => currentDemandNames.includes(name)).length
  
  if (matchedCount === 0) {
    alert('当前配送点与案例需求点不匹配，请先在模块一加载对应的案例')
    showCaseDropdown.value = false
    return
  }
  
  await matStore.loadAssignmentFromCase(caseData.material_data)
  showCaseDropdown.value = false
  alert(`已应用案例物资，匹配 ${matchedCount} 个需求点`)
}

function toggleCaseDropdown() {
  showCaseDropdown.value = !showCaseDropdown.value
}
</script>

<template>
  <div class="module2">
    <!-- 标题 -->
    <div class="section">
      <div class="section-title">
        物资需求选择
      </div>
      <div class="section-desc">
        点击需求点卡片，在右侧编辑物资明细
      </div>
    </div>

    <!-- 统计 -->
    <div class="section">
      <div class="stat-row">
        <div class="stat-item">
          <span class="stat-num teal">{{ matStore.assignedCount }}</span>
          <span class="stat-label">已分配</span>
        </div>
        <div class="stat-item">
          <span class="stat-num" :class="unassignedCount > 0 ? 'amber' : 'green'">
            {{ unassignedCount }}
          </span>
          <span class="stat-label">未分配</span>
        </div>
        <div class="stat-item">
          <span class="stat-num teal">{{ matStore.totalWeight }}</span>
          <span class="stat-label">总重量(kg)</span>
        </div>
      </div>
    </div>

    <!-- 加载案例 -->
    <div class="section">
      <div class="case-select-wrapper">
        <button
          class="btn btn-primary btn-block"
          :disabled="pointsStore.demands.length === 0"
          @click="toggleCaseDropdown"
        >
          📂 加载案例物资分配
        </button>
        <div
          v-if="showCaseDropdown"
          class="case-dropdown"
        >
          <div
            class="case-dropdown-item case-dropdown-header"
          >
            <span>选择案例加载物资分配</span>
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
        class="btn btn-config btn-block"
        @click="showConfig = true"
      >
        🤖 AI识别配置
      </button>
      <button
        class="btn btn-success btn-block"
        :disabled="matStore.assignedCount === 0"
        @click="handleSaveModule2"
      >
        📋 备份数据
      </button>
    </div>

    <!-- 配置面板 -->
    <ConfigPanel
      v-if="showConfig"
      module-key="module2"
      @close="showConfig = false"
    />

    <!-- 需求点列表 -->
    <div class="section">
      <div class="section-title">
        需求点物资配置
      </div>

      <div
        v-if="pointsStore.demands.length === 0"
        class="empty-hint"
      >
        请先在模块一添加需求点
      </div>

      <div
        v-for="(pt, idx) in pointsStore.demands"
        :key="pt.id"
        class="point-card"
        :class="{ active: editingPointId === pt.id }"
        @click="openEditPanel(pt)"
      >
        <div class="card-header">
          <div class="card-title">
            <span class="point-index">{{ idx + 1 }}</span>
            <span class="point-name">{{ pt.name }}</span>
            <span
              v-if="matStore.getAssignment(pt.id)"
              class="assigned-tag"
            >
              {{ (matStore.getAssignment(pt.id).supply_types || []).map(s => supplyTypeLabel(s)).join(' + ') || '已分配' }}
            </span>
            <span
              v-else
              class="unassigned-tag"
            >
              未分配
            </span>
          </div>
          <div class="card-summary">
            <span
              v-if="matStore.getAssignment(pt.id)"
              class="summary-info"
            >
              <span class="summary-weight">
                {{ matStore.getAssignment(pt.id).total_weight }}kg
              </span>
              <span
                class="summary-priority"
                :style="{ color: priorityColor(matStore.getAssignment(pt.id).priority) }"
              >
                {{ priorityLabel(matStore.getAssignment(pt.id).priority) }}
              </span>
            </span>
            <span class="edit-icon">✎</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧编辑面板 -->
    <RightPanel
      v-if="editingPoint"
      :title="'物资编辑 — ' + editingPoint.name"
      @close="closeEditPanel()"
    >
      <div class="rp-content">
        <!-- 物资类别选择 -->
        <div class="rp-section">
          <div class="rp-section-title">物资类别</div>
          <div class="cat-grid">
            <div
              v-for="cat in matStore.categories"
              :key="cat.id"
              class="cat-item"
              :class="{ selected: matStore.isCategorySelected(editingPointId, cat.id) }"
              @click="matStore.toggleCategory(editingPointId, cat.id)"
            >
              <div class="cat-check">
                <span v-if="matStore.isCategorySelected(editingPointId, cat.id)">✓</span>
              </div>
              <span class="cat-icon">{{ cat.icon }}</span>
              <span class="cat-name">{{ cat.name }}</span>
            </div>
          </div>
        </div>

        <!-- 已选物资详情 -->
        <template v-if="editingAssignment">
          <!-- 编辑开关 -->
          <div class="rp-section">
            <div class="edit-toggle-row">
              <button
                class="btn-edit"
                :class="{ active: editingItems }"
                @click="editingItems = !editingItems"
              >
                {{ editingItems ? '完成编辑' : '编辑物资' }}
              </button>
            </div>
          </div>

          <!-- 物资清单 — 只读模式 -->
          <div v-if="!editingItems" class="rp-section">
            <div class="rp-section-title">物资清单</div>
            <table class="items-table">
              <thead>
                <tr>
                  <th>物资</th>
                  <th>单重(kg)</th>
                  <th>数量</th>
                  <th>小计(kg)</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in editingAssignment.items"
                  :key="item.name"
                >
                  <td>{{ item.name }}</td>
                  <td class="mono">{{ item.unit_weight ?? item.weight ?? '-' }}</td>
                  <td class="mono">×{{ item.qty ?? item.quantity ?? '-' }}</td>
                  <td class="mono">{{ item.subtotal ?? ((item.unit_weight || item.weight || 0) * (item.qty || item.quantity || 0)) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 物资清单 — 编辑模式 -->
          <div v-else class="rp-section">
            <div class="rp-section-title">编辑物资清单</div>
            <table class="items-table editable">
              <thead>
                <tr>
                  <th>物资名称</th>
                  <th>单重</th>
                  <th>数量</th>
                  <th>小计</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, ii) in editingAssignment.items"
                  :key="ii"
                >
                  <td>
                    <input
                      :value="item.name"
                      class="cell-input"
                      @input="matStore.updateItem(editingPointId, ii, 'name', $event.target.value)"
                    />
                  </td>
                  <td>
                    <input
                      :value="item.unit_weight"
                      type="number"
                      min="0"
                      step="0.5"
                      class="cell-input narrow"
                      @input="matStore.updateItem(editingPointId, ii, 'unit_weight', parseFloat($event.target.value) || 0)"
                    />
                  </td>
                  <td>
                    <input
                      :value="item.qty"
                      type="number"
                      min="0"
                      class="cell-input narrow"
                      @input="matStore.updateItem(editingPointId, ii, 'qty', parseInt($event.target.value) || 0)"
                    />
                  </td>
                  <td class="mono">{{ item.subtotal }}</td>
                  <td>
                    <button
                      class="btn-remove"
                      @click="matStore.removeItem(editingPointId, ii)"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <button
              class="btn-add-item"
              @click="matStore.addItem(editingPointId, editingAssignment.supply_types[0] || '')"
            >
              + 添加物资
            </button>
          </div>

          <!-- 汇总信息 -->
          <div class="rp-section">
            <div class="rp-section-title">汇总信息</div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">总重量</span>
                <span class="info-value teal">
                  {{ editingAssignment.total_weight }} kg
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">优先级</span>
                <select
                  class="priority-select"
                  :value="editingAssignment.priority"
                  @change="matStore.updatePriority(editingPointId, parseInt($event.target.value))"
                >
                  <option value="1" :style="{ color: '#ff3d57' }">紧急</option>
                  <option value="2" :style="{ color: '#ffb300' }">高</option>
                  <option value="3" :style="{ color: '#00e5ff' }">中</option>
                  <option value="4" :style="{ color: '#7a93bb' }">低</option>
                  <option value="5" :style="{ color: '#3d5a80' }">普通</option>
                </select>
              </div>
              <div class="info-item">
                <span class="info-label">配送模式</span>
                <select
                  class="delivery-mode-select"
                  :value="editingAssignment.delivery_mode || 'optional'"
                  @change="matStore.updateDeliveryMode(editingPointId, $event.target.value)"
                >
                  <option value="direct">必须直飞</option>
                  <option value="optional">可选联飞</option>
                </select>
              </div>
              <div class="info-item full">
                <span class="info-label">特殊要求</span>
                <span class="info-value">
                  {{ editingAssignment.special_requirements || '无' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 风险提示 -->
          <div
            v-if="Array.isArray(editingAssignment.risk_warnings) && editingAssignment.risk_warnings.length > 0"
            class="rp-section"
          >
            <div class="rp-section-title rp-risk-title">投放风险提示</div>
            <div
              v-for="(risk, ri) in editingAssignment.risk_warnings"
              :key="ri"
              class="risk-item"
            >
              ⚠ {{ risk }}
            </div>
          </div>
        </template>

        <!-- 未分配提示 -->
        <div v-else class="rp-empty">
          该需求点尚未分配物资，请先选择物资类别
        </div>
      </div>
    </RightPanel>
  </div>
</template>

<style scoped>
.module2 {
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
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.section-desc {
  font-size: 10px;
  color: var(--text3);
  margin-bottom: 4px;
}

/* Stats */
.stat-row {
  display: flex;
  gap: 8px;
}

.stat-item {
  flex: 1;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  text-align: center;
}

.stat-num {
  font-family: var(--mono);
  font-size: 18px;
  font-weight: 700;
  display: block;
}

.stat-num.teal { color: var(--teal); }
.stat-num.amber { color: var(--amber); }
.stat-num.green { color: var(--green); }

.stat-label {
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.5px;
}

/* Button */
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

.btn-block { width: 100%; }

.btn-primary {
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  color: #000;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--glow-teal);
}

.btn-config {
  margin-top: 6px;
  background: var(--navy);
  color: var(--text2);
  border: 1px solid var(--border2);
}

.btn-config:hover:not(:disabled) {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-success {
  margin-top: 6px;
  background: var(--navy);
  color: var(--text2);
  border: 1px solid var(--border2);
}

.btn-success:hover:not(:disabled) {
  border-color: var(--green);
  color: var(--green);
}

/* Empty */
.empty-hint {
  padding: 20px;
  text-align: center;
  color: var(--text3);
  font-size: 11px;
}

/* Point Card */
.point-card {
  border: 1px solid var(--border2);
  border-radius: 8px;
  margin-bottom: 6px;
  background: var(--navy);
  cursor: pointer;
  transition: all 0.2s;
}

.point-card:hover {
  border-color: var(--text3);
}

.point-card.active {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.04);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.point-index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: var(--teal);
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: var(--mono);
}

.point-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.assigned-tag {
  font-size: 9px;
  color: var(--teal);
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
  padding: 1px 6px;
  border-radius: 3px;
  white-space: nowrap;
}

.unassigned-tag {
  font-size: 9px;
  color: var(--text3);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  padding: 1px 6px;
  border-radius: 3px;
}

.card-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.summary-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.summary-weight {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--teal);
  font-weight: 600;
}

.summary-priority {
  font-size: 10px;
  font-weight: 600;
}

.edit-icon {
  font-size: 11px;
  color: var(--text3);
  opacity: 0.5;
  transition: all 0.2s;
}

.point-card:hover .edit-icon {
  opacity: 1;
  color: var(--teal);
}

/* ─── Right Panel Content ─── */
.rp-content {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.rp-section {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.rp-section:last-child {
  border-bottom: none;
}

.rp-section-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--teal);
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.rp-risk-title {
  color: var(--amber);
}

.rp-empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text3);
  font-size: 11px;
}

/* Category Grid */
.cat-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border: 1px solid var(--border2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--navy2);
  font-size: 11px;
}

.cat-item:hover {
  border-color: var(--text3);
}

.cat-item.selected {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.08);
}

.cat-check {
  width: 14px;
  height: 14px;
  border: 1px solid var(--border2);
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--teal);
}

.cat-item.selected .cat-check {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.15);
}

.cat-icon { font-size: 13px; }

.cat-name { color: var(--text2); }

.cat-item.selected .cat-name {
  color: var(--teal);
}

/* Edit toggle */
.edit-toggle-row {
  margin-bottom: 0;
}

.btn-edit {
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: 5px;
  color: var(--teal);
  padding: 4px 10px;
  font-size: 10px;
  cursor: pointer;
  font-family: var(--sans);
}

.btn-edit.active {
  background: rgba(0, 229, 255, 0.15);
  border-color: var(--teal);
}

/* Items Table */
.items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.items-table th {
  background: var(--navy2);
  color: var(--text3);
  padding: 4px 8px;
  text-align: left;
  font-weight: 500;
  font-size: 9px;
  border-bottom: 1px solid var(--border);
}

.items-table td {
  padding: 4px 8px;
  border-bottom: 1px solid rgba(22, 37, 64, 0.5);
  color: var(--text2);
}

.mono {
  font-family: var(--mono);
}

/* Editable table */
.items-table.editable td {
  padding: 3px 4px;
}

.cell-input {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text);
  padding: 4px 6px;
  font-size: 10px;
  font-family: var(--sans);
  outline: none;
  transition: border-color 0.2s;
}

.cell-input:focus {
  border-color: var(--teal);
}

.cell-input.narrow {
  width: 50px;
}

.btn-remove {
  background: none;
  border: none;
  color: var(--red);
  cursor: pointer;
  font-size: 11px;
  padding: 2px 4px;
  opacity: 0.6;
}

.btn-remove:hover {
  opacity: 1;
}

.btn-add-item {
  margin-top: 6px;
  background: rgba(0, 229, 255, 0.06);
  border: 1px dashed rgba(0, 229, 255, 0.3);
  border-radius: 5px;
  color: var(--teal);
  padding: 5px 10px;
  font-size: 10px;
  cursor: pointer;
  font-family: var(--sans);
  width: 100%;
}

.btn-add-item:hover {
  background: rgba(0, 229, 255, 0.12);
}

/* Info Grid */
.info-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.info-item {
  flex: 0 0 calc(50% - 4px);
  background: var(--navy);
  border-radius: 6px;
  padding: 8px 10px;
}

.info-item.full {
  flex: 1 1 100%;
}

.info-label {
  display: block;
  font-size: 9px;
  color: var(--text3);
  margin-bottom: 2px;
}

.info-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.info-value.teal {
  color: var(--teal);
  font-family: var(--mono);
}

/* Priority Select */
.priority-select {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text);
  padding: 4px 6px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--sans);
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
}

.priority-select:focus {
  border-color: var(--teal);
}

.priority-select option {
  background: var(--navy);
  color: var(--text);
  font-size: 12px;
  padding: 4px;
}

/* Risk */
.risk-item {
  font-size: 10px;
  color: var(--amber);
  padding: 4px 8px;
  background: rgba(255, 179, 0, 0.06);
  border-radius: 4px;
  margin-bottom: 4px;
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
</style>
