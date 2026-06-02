<script setup>
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'
import { useUavsStore } from '../stores/uavs'
import { usePointsStore } from '../stores/points'
import { useMaterialsStore } from '../stores/materials'
import { useConfigStore } from '../stores/config'
import ConfigPanel from '../components/ConfigPanel.vue'
import RightPanel from '../components/RightPanel.vue'

const uavStore = useUavsStore()
const ptsStore = usePointsStore()
const matStore = useMaterialsStore()
const configStore = useConfigStore()

const showConfig = ref(false)
const assessing = ref(false)
const assessingAI = ref(false)
const expandedBrand = ref({})
// 右侧面板: null | 'edit' | 'assess' | 'ai'
const rightPanelType = ref(null)
// 编辑状态
const editingModel = ref(null)
const editForm = ref({})
const savingModel = ref(false)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

function renderMarkdown(text) {
  return marked(text || '')
}

onMounted(async () => {
  await uavStore.loadModels()
  uavStore.loadAIResults()
  // 加载物资分配数据，确保需求总重正确显示
  await matStore.loadFromDb()
  if (uavStore.brands.length > 0) {
    expandedBrand.value[uavStore.brands[0].name] = true
  }
})

function toggleBrand(brandName) {
  expandedBrand.value[brandName] = !expandedBrand.value[brandName]
}

async function handleAssess() {
  assessing.value = true
  await uavStore.runAssessment()
  assessing.value = false
  if (uavStore.assessment) {
    rightPanelType.value = 'assess'
  }
}

async function handleAIAssess() {
  assessingAI.value = true
  await uavStore.runAIAssessment()
  assessingAI.value = false
  if (uavStore.aiResult) {
    rightPanelType.value = 'ai'
  }
}

function viewAIHistory(item) {
  uavStore.aiResult = {
    raw_text: item.raw_text,
    elapsed_seconds: item.elapsed_seconds,
    saved_id: item.id,
  }
  rightPanelType.value = 'ai'
}

function openHistory() {
  rightPanelType.value = 'history'
}

function closeRightPanel() {
  rightPanelType.value = null
  editingModel.value = null
  editForm.value = {}
}

function statusColor(status) {
  if (status === '满足' || status === '适配') return 'green'
  if (status === '紧张' || status === '部分适配') return 'amber'
  return 'red'
}

function statusIcon(status) {
  if (status === '满足' || status === '适配') return '✓'
  if (status === '紧张' || status === '部分适配') return '!'
  return '✕'
}

async function handleSaveModule3() {
  const module3Data = {
    // 所有无人机型号配置
    all_models: uavStore.models.map(m => ({
      model_id: m.id,
      brand: m.brand,
      model: m.model,
      max_payload: m.max_payload,
      range_km: m.range_km,
      max_speed: m.max_speed,
      cabin_volume: m.cabin_volume,
      wind_resist: m.wind_resist,
      ip_rating: m.ip_rating,
      range_points: m.range_points || [],
      suitable_for: m.suitable_for || [],
      description: m.description,
    })),
    // 用户选择的无人机
    selected_uavs: uavStore.selectedDetails.map(d => ({
      model_id: d.model_id,
      model: d.model,
      quantity: d.quantity,
      max_payload: d.model.max_payload,
      range_km: d.model.range_km,
    })),
    saved_at: new Date().toISOString(),
  }
  
  try {
    const response = await fetch('/api/workspace/save/module3', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(module3Data),
    })
    const result = await response.json()
    if (result.success) {
      alert('模块三数据已保存！')
    } else {
      alert('保存失败: ' + result.message)
    }
  } catch (e) {
    alert('保存失败: ' + e.message)
  }
}

// 无人机参数编辑 — 打开右侧面板
function startEdit(model) {
  editingModel.value = model
  editForm.value = {
    max_payload: model.max_payload,
    range_km: model.range_km,
    max_speed: model.max_speed,
    cabin_volume: model.cabin_volume || 0,
    wind_resist: model.wind_resist || 0,
    ip_rating: model.ip_rating || '',
    description: model.description || '',
  }
  rightPanelType.value = 'edit'
}

async function saveEdit() {
  if (!editingModel.value) return
  savingModel.value = true
  try {
    await uavStore.updateModelParam(editingModel.value.id, {
      max_payload: parseFloat(editForm.value.max_payload) || 0,
      range_km: parseFloat(editForm.value.range_km) || 0,
      max_speed: parseFloat(editForm.value.max_speed) || 0,
      cabin_volume: parseFloat(editForm.value.cabin_volume) || 0,
      wind_resist: parseInt(editForm.value.wind_resist) || 0,
      ip_rating: editForm.value.ip_rating || '',
      description: editForm.value.description || '',
    })
    closeRightPanel()
  } catch (e) {
    // error is already in store
  } finally {
    savingModel.value = false
  }
}

const demandWeight = computed(() => matStore.totalWeight)
const maxDistance = computed(() => {
  if (ptsStore.distReturn.length === 0) return 0
  return Math.max(...ptsStore.distReturn).toFixed(1)
})
</script>

<template>
  <div class="module3">
    <!-- 标题 -->
    <div class="section">
      <div class="section-title">无人机选择</div>
      <div class="section-desc">选择无人机型号和数量，系统自动评估适配性</div>
    </div>

    <!-- 任务概览 -->
    <div class="section">
      <div class="stat-row">
        <div class="stat-item">
          <span class="stat-num teal">{{ demandWeight }}</span>
          <span class="stat-label">需求总重(kg)</span>
        </div>
        <div class="stat-item">
          <span class="stat-num teal">{{ maxDistance || '-' }}</span>
          <span class="stat-label">最远距离(km)</span>
        </div>
        <div class="stat-item">
          <span class="stat-num teal">{{ uavStore.totalCount }}</span>
          <span class="stat-label">已选(架)</span>
        </div>
        <div class="stat-item">
          <span class="stat-num" :class="uavStore.totalPayload >= demandWeight ? 'green' : 'amber'">
            {{ uavStore.totalPayload }}
          </span>
          <span class="stat-label">总载重(kg)</span>
        </div>
      </div>
    </div>

    <!-- 无人机型号选择 -->
    <div class="section">
      <div class="section-subtitle">内置无人机型号库</div>

      <div v-for="brand in uavStore.brands" :key="brand.name" class="brand-group">
        <div class="brand-header" @click="toggleBrand(brand.name)">
          <span class="brand-icon">{{ expandedBrand[brand.name] ? '▼' : '▶' }}</span>
          <span class="brand-name">{{ brand.name }}</span>
          <span class="brand-count">{{ brand.models.length }} 款</span>
        </div>

        <div v-show="expandedBrand[brand.name]" class="brand-models">
          <div
            v-for="model in brand.models"
            :key="model.id"
            class="model-card"
            :class="{ selected: uavStore.getQuantity(model.id) > 0 }"
          >
            <div class="model-header">
              <div class="model-name">
                {{ model.model }}
                <button
                  class="btn-edit-param"
                  title="编辑参数"
                  @click.stop="startEdit(model)"
                >✎</button>
              </div>
              <div class="model-qty">
                <button class="qty-btn" @click="uavStore.decrement(model.id)">-</button>
                <span class="qty-num">{{ uavStore.getQuantity(model.id) }}</span>
                <button class="qty-btn" @click="uavStore.increment(model.id)">+</button>
              </div>
            </div>

            <div class="model-desc">{{ model.description }}</div>

            <div class="model-specs">
              <div class="spec">
                <span class="spec-label">载重</span>
                <span class="spec-value">{{ model.max_payload }}kg</span>
              </div>
              <div class="spec">
                <span class="spec-label">航程</span>
                <span class="spec-value">{{ model.range_km }}km</span>
              </div>
              <div class="spec">
                <span class="spec-label">速度</span>
                <span class="spec-value">{{ model.max_speed }}km/h</span>
              </div>
              <div class="spec">
                <span class="spec-label">货舱</span>
                <span class="spec-value">{{ model.cabin_volume }}L</span>
              </div>
              <div class="spec">
                <span class="spec-label">抗风</span>
                <span class="spec-value">{{ model.wind_resist }}级</span>
              </div>
              <div class="spec">
                <span class="spec-label">防护</span>
                <span class="spec-value">{{ model.ip_rating }}</span>
              </div>
            </div>

            <div class="model-tags">
              <span
                v-for="tag in model.suitable_for"
                :key="tag"
                class="tag"
              >{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 已选无人机汇总 -->
    <div v-if="uavStore.selectedDetails.length > 0" class="section">
      <div class="section-subtitle">已选无人机</div>
      <div class="selected-list">
        <div v-for="d in uavStore.selectedDetails" :key="d.model_id" class="selected-item">
          <span class="sel-brand">{{ d.model.brand }}</span>
          <span class="sel-model">{{ d.model.model }}</span>
          <span class="sel-qty">× {{ d.quantity }}</span>
          <span class="sel-payload">{{ d.model.max_payload * d.quantity }}kg</span>
        </div>
      </div>
    </div>

    <!-- 评估按钮 -->
    <div class="section">
      <div class="llm-status" :class="uavStore.llmConfigured ? 'on' : 'off'">
        <span class="llm-dot" />
        <span>{{ uavStore.llmConfigured ? '大模型已接入' : '大模型未配置' }}</span>
      </div>
      <button
        class="btn btn-primary btn-block"
        :disabled="uavStore.selections.length === 0 || assessing"
        @click="handleAssess"
      >
        {{ assessing ? '评估中...' : '配置评估（规则引擎）' }}
      </button>
      <button
        v-if="uavStore.llmConfigured"
        class="btn btn-ai btn-block"
        :disabled="assessingAI"
        @click="handleAIAssess"
      >
        {{ assessingAI ? 'AI 选型中...' : 'AI 智能选型' }}
      </button>
      <button
        class="btn btn-success btn-block"
        :disabled="uavStore.selections.length === 0"
        @click="handleSaveModule3"
      >
        📋 备份数据
      </button>
      <button
        v-if="uavStore.selections.length > 0"
        class="btn btn-ghost btn-block btn-sm"
        @click="uavStore.clearSelections()"
      >
        清空选择
      </button>
    </div>

    <!-- AI 历史记录按钮 -->
    <div class="section">
      <button class="btn btn-ghost btn-block" @click="openHistory">
        历史选型记录{{ uavStore.aiResults.length > 0 ? ' (' + uavStore.aiResults.length + '条)' : '' }}
      </button>
    </div>

    <!-- 错误信息 -->
    <div v-if="uavStore.error" class="section">
      <div class="error-msg">{{ uavStore.error }}</div>
    </div>

    <!-- 配置保存 -->
    <div class="section">
      <button class="btn btn-ghost btn-block" @click="showConfig = !showConfig">
        {{ showConfig ? '关闭配置面板' : '🤖 AI识别配置' }}
      </button>
    </div>

    <ConfigPanel v-if="showConfig" module-key="module3" @close="showConfig = false" />

    <!-- ─── 右侧：参数编辑面板 ─── -->
    <RightPanel
      v-if="rightPanelType === 'edit' && editingModel"
      :title="'参数编辑 — ' + editingModel.model"
      @close="closeRightPanel"
    >
      <div class="rp-content">
        <!-- 型号信息 -->
        <div class="rp-section">
          <div class="rp-model-info">
            <span class="rp-brand-tag">{{ editingModel.brand }}</span>
            <span class="rp-model-name">{{ editingModel.model }}</span>
          </div>
          <div class="rp-model-id">ID: {{ editingModel.model_id }}</div>
        </div>

        <!-- 核心参数 -->
        <div class="rp-section">
          <div class="rp-section-title">核心参数</div>
          <div class="rp-form-grid">
            <div class="rp-field">
              <label>最大载重 (kg)</label>
              <input v-model="editForm.max_payload" type="number" min="0" step="1" />
            </div>
            <div class="rp-field">
              <label>航程 (km)</label>
              <input v-model="editForm.range_km" type="number" min="0" step="1" />
            </div>
            <div class="rp-field">
              <label>最大速度 (km/h)</label>
              <input v-model="editForm.max_speed" type="number" min="0" step="1" />
            </div>
          </div>
        </div>

        <!-- 其他参数 -->
        <div class="rp-section">
          <div class="rp-section-title">其他参数</div>
          <div class="rp-form-grid">
            <div class="rp-field">
              <label>货舱容积 (L)</label>
              <input v-model="editForm.cabin_volume" type="number" min="0" step="1" />
            </div>
            <div class="rp-field">
              <label>抗风等级 (级)</label>
              <input v-model="editForm.wind_resist" type="number" min="0" max="12" step="1" />
            </div>
            <div class="rp-field">
              <label>防护等级</label>
              <input v-model="editForm.ip_rating" type="text" placeholder="如 IP55" />
            </div>
          </div>
        </div>

        <!-- 描述 -->
        <div class="rp-section">
          <div class="rp-section-title">描述</div>
          <textarea v-model="editForm.description" class="rp-textarea" rows="3" />
        </div>

        <!-- 原始参数（只读） -->
        <div v-if="editingModel.raw_params" class="rp-section">
          <div class="rp-section-title">原始参数参考</div>
          <div class="rp-raw">{{ editingModel.raw_params }}</div>
        </div>

        <!-- 操作按钮 -->
        <div class="rp-section rp-actions">
          <button class="btn btn-primary btn-block" :disabled="savingModel" @click="saveEdit">
            {{ savingModel ? '保存中...' : '保存到数据库' }}
          </button>
          <button class="btn btn-ghost btn-block btn-sm" @click="closeRightPanel">
            取消
          </button>
        </div>
      </div>
    </RightPanel>

    <!-- ─── 右侧：评估结果面板 ─── -->
    <RightPanel
      v-if="rightPanelType === 'assess' && uavStore.assessment"
      title="配置评估结果"
      @close="closeRightPanel"
    >
      <div class="rp-content">
        <!-- 总体评估 -->
        <div
          class="assess-summary"
          :class="uavStore.assessment.summary.feasible ? 'feasible' : 'infeasible'"
        >
          <div class="summary-status">
            {{ uavStore.assessment.summary.feasible ? '✓ 方案可行' : '方案可能存在的问题' }}
          </div>
          <div class="summary-detail">
            需求总重 {{ uavStore.assessment.summary.total_demand_weight }}kg /
            总载重能力 {{ uavStore.assessment.summary.total_payload_capacity }}kg /
            载重利用率 {{ uavStore.assessment.summary.load_ratio }}%
          </div>
        </div>

        <!-- 各机型评估 -->
        <div v-for="uav in uavStore.assessment.uavs" :key="uav.model_id" class="assess-card">
          <div class="assess-header">
            <span class="assess-model">{{ uav.brand }} {{ uav.model_name }}</span>
            <span class="assess-qty">× {{ uav.quantity }}</span>
          </div>
          <div class="assess-checks">
            <div class="check-row">
              <span class="check-label">载重判断</span>
              <span class="check-status" :class="statusColor(uav.load_status)">
                {{ statusIcon(uav.load_status) }} {{ uav.load_status }}
              </span>
            </div>
            <div class="check-detail">{{ uav.load_detail }}</div>
            <div class="check-row">
              <span class="check-label">航程判断</span>
              <span class="check-status" :class="statusColor(uav.range_status)">
                {{ statusIcon(uav.range_status) }} {{ uav.range_status }}
              </span>
            </div>
            <div class="check-detail">{{ uav.range_detail }}</div>
            <div class="check-row">
              <span class="check-label">适配性</span>
              <span class="check-status" :class="statusColor(uav.fit_status)">
                {{ statusIcon(uav.fit_status) }} {{ uav.fit_status }}
              </span>
            </div>
            <div v-if="uav.fit_issues && uav.fit_issues.length > 0" class="check-detail">
              <div v-for="issue in uav.fit_issues" :key="issue" class="fit-issue">{{ issue }}</div>
            </div>
          </div>
        </div>

        <!-- 建议 -->
        <div v-if="uavStore.assessment.suggestions.length > 0" class="suggestions">
          <div class="rp-section-title">风险预警与优化建议</div>
          <div
            v-for="(sug, i) in uavStore.assessment.suggestions"
            :key="i"
            class="suggestion-item"
            :class="sug.type"
          >
            <span class="sug-icon">
              {{ sug.type === 'warning' ? '⚠' : sug.type === 'success' ? '✓' : 'ℹ' }}
            </span>
            <span class="sug-text">{{ sug.content }}</span>
          </div>
        </div>
      </div>
    </RightPanel>

    <!-- ─── 右侧：AI选型结果面板 ─── -->
    <RightPanel
      v-if="rightPanelType === 'ai' && uavStore.aiResult"
      title="AI 智能选型方案"
      @close="closeRightPanel"
    >
      <template #header-actions>
        <span class="ai-badge">{{ uavStore.aiResult.elapsed_seconds }}s</span>
      </template>
      <div class="rp-content">
        <div class="ai-output markdown-body" v-html="renderMarkdown(uavStore.aiResult.raw_text)" />
      </div>
    </RightPanel>

    <!-- ─── 右侧：历史记录面板 ─── -->
    <RightPanel
      v-if="rightPanelType === 'history'"
      title="历史选型记录"
      @close="closeRightPanel"
    >
      <div class="rp-content">
        <div v-if="uavStore.aiResults.length === 0" class="rp-empty">
          暂无历史记录，点击「AI 智能选型」生成第一条方案
        </div>
        <div
          v-for="(item, idx) in uavStore.aiResults"
          :key="item.id"
          class="history-card"
        >
          <div class="history-card-header" @click="viewAIHistory(item)">
            <div class="history-card-title">
              <span class="history-index">{{ uavStore.aiResults.length - idx }}</span>
              <span class="history-date">{{ item.created_at }}</span>
            </div>
            <div class="history-card-meta">
              <span class="history-duration">{{ item.elapsed_seconds }}s</span>
              <span class="history-arrow">→</span>
            </div>
          </div>
          <button
            class="history-del"
            title="删除此记录"
            @click="uavStore.removeAIResult(item.id)"
          >删除</button>
        </div>
      </div>
    </RightPanel>
  </div>
</template>

<style scoped>
.module3 {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.section {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.section-subtitle {
  font-size: 12px;
  font-weight: 700;
  color: var(--teal);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.section-desc {
  font-size: 11px;
  color: var(--text3);
}

/* Stat row */
.stat-row {
  display: flex;
  gap: 8px;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 4px;
  background: var(--navy);
  border-radius: 6px;
  border: 1px solid var(--border);
}

.stat-num {
  font-size: 16px;
  font-weight: 800;
  font-family: var(--mono);
}

.stat-num.teal { color: var(--teal); }
.stat-num.green { color: var(--green); }
.stat-num.amber { color: var(--amber); }
.stat-num.red { color: var(--red); }

.stat-label {
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.5px;
}

/* Brand groups */
.brand-group {
  margin-bottom: 6px;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.brand-header:hover {
  border-color: var(--teal);
}

.brand-icon {
  font-size: 10px;
  color: var(--text3);
  width: 14px;
  text-align: center;
}

.brand-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  flex: 1;
}

.brand-count {
  font-size: 10px;
  color: var(--text3);
  background: var(--navy3);
  padding: 2px 8px;
  border-radius: 10px;
}

.brand-models {
  padding: 6px 0 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Model cards */
.model-card {
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
  transition: all 0.2s;
}

.model-card:hover {
  border-color: var(--border2);
}

.model-card.selected {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.04);
}

.model-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.model-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 6px;
}

.model-qty {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qty-btn {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid var(--border2);
  background: var(--navy3);
  color: var(--text2);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.qty-btn:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.qty-num {
  font-size: 16px;
  font-weight: 800;
  font-family: var(--mono);
  color: var(--teal);
  min-width: 20px;
  text-align: center;
}

.model-desc {
  font-size: 10px;
  color: var(--text3);
  margin-bottom: 8px;
  line-height: 1.4;
}

.model-specs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.spec {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4px;
  background: var(--navy2);
  border-radius: 4px;
}

.spec-label {
  font-size: 9px;
  color: var(--text3);
}

.spec-value {
  font-size: 11px;
  font-weight: 700;
  color: var(--text2);
  font-family: var(--mono);
}

.model-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 3px;
  background: rgba(0, 229, 255, 0.08);
  color: var(--teal);
  border: 1px solid rgba(0, 229, 255, 0.15);
}

/* Selected list */
.selected-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--navy);
  border: 1px solid var(--teal);
  border-radius: 6px;
  font-size: 12px;
}

.sel-brand {
  font-size: 10px;
  color: var(--text3);
  background: var(--navy3);
  padding: 1px 6px;
  border-radius: 3px;
}

.sel-model {
  flex: 1;
  font-weight: 700;
  color: var(--text);
}

.sel-qty {
  font-family: var(--mono);
  font-weight: 700;
  color: var(--teal);
}

.sel-payload {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text2);
}

/* LLM status */
.llm-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: var(--text3);
  margin-bottom: 6px;
}

.llm-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.llm-status.on .llm-dot {
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
}

.llm-status.off .llm-dot {
  background: var(--text3);
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  color: #000;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--glow-teal);
}

.btn-ai {
  margin-top: 6px;
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: #fff;
}

.btn-ai:hover:not(:disabled) {
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
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

.btn-ghost {
  background: var(--navy);
  color: var(--text3);
  border: 1px solid var(--border2);
}

.btn-ghost:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-sm {
  margin-top: 6px;
  padding: 5px 12px;
  font-size: 10px;
}

/* Error */
.error-msg {
  padding: 8px 10px;
  background: rgba(255, 61, 87, 0.08);
  border: 1px solid rgba(255, 61, 87, 0.2);
  border-radius: 6px;
  color: var(--red);
  font-size: 11px;
}

/* ─── Edit button on model card ─── */
.btn-edit-param {
  background: none;
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text3);
  font-size: 11px;
  cursor: pointer;
  padding: 1px 5px;
  transition: all 0.2s;
  line-height: 1;
}

.btn-edit-param:hover {
  border-color: var(--teal);
  color: var(--teal);
}

/* ─── Right Panel: Edit Form ─── */
.rp-content {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.rp-section {
  padding: 12px 0;
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

.rp-model-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.rp-brand-tag {
  font-size: 10px;
  color: var(--text3);
  background: var(--navy3);
  padding: 2px 8px;
  border-radius: 4px;
}

.rp-model-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.rp-model-id {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
}

.rp-form-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rp-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.rp-field label {
  font-size: 11px;
  color: var(--text2);
  white-space: nowrap;
  min-width: 100px;
}

.rp-field input {
  flex: 1;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text);
  padding: 6px 10px;
  font-size: 12px;
  font-family: var(--mono);
  outline: none;
  transition: border-color 0.2s;
  text-align: right;
}

.rp-field input:focus {
  border-color: var(--teal);
}

.rp-textarea {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text);
  padding: 8px 10px;
  font-size: 11px;
  font-family: var(--sans);
  outline: none;
  resize: vertical;
  transition: border-color 0.2s;
}

.rp-textarea:focus {
  border-color: var(--teal);
}

.rp-raw {
  font-size: 10px;
  color: var(--text3);
  line-height: 1.6;
  background: var(--navy);
  padding: 8px 10px;
  border-radius: 6px;
  white-space: pre-wrap;
}

.rp-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* ─── Right Panel: Assessment ─── */
.assess-summary {
  padding: 12px;
  border-radius: 8px;
}

.assess-summary.feasible {
  background: rgba(0, 230, 118, 0.08);
  border: 1px solid rgba(0, 230, 118, 0.2);
}

.assess-summary.infeasible {
  background: rgba(255, 61, 87, 0.08);
  border: 1px solid rgba(255, 61, 87, 0.2);
}

.summary-status {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}

.feasible .summary-status { color: var(--green); }
.infeasible .summary-status { color: var(--red); }

.summary-detail {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
}

.assess-card {
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
}

.assess-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.assess-model {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.assess-qty {
  font-family: var(--mono);
  font-weight: 700;
  color: var(--teal);
}

.check-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;
}

.check-label {
  font-size: 11px;
  color: var(--text2);
}

.check-status {
  font-size: 11px;
  font-weight: 700;
  font-family: var(--mono);
}

.check-status.green { color: var(--green); }
.check-status.amber { color: var(--amber); }
.check-status.red { color: var(--red); }

.check-detail {
  font-size: 10px;
  color: var(--text3);
  padding: 2px 0 8px 0;
  line-height: 1.4;
  border-bottom: 1px solid var(--border);
}

.check-detail:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.fit-issue {
  padding: 2px 0;
  color: var(--amber);
}

/* Suggestions */
.suggestions {
  margin-top: 4px;
}

.suggestion-item {
  display: flex;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 4px;
  font-size: 11px;
  line-height: 1.4;
}

.suggestion-item.warning {
  background: rgba(255, 179, 0, 0.08);
  border: 1px solid rgba(255, 179, 0, 0.2);
  color: var(--amber);
}

.suggestion-item.success {
  background: rgba(0, 230, 118, 0.08);
  border: 1px solid rgba(0, 230, 118, 0.2);
  color: var(--green);
}

.suggestion-item.info {
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
  color: var(--teal);
}

.sug-icon {
  flex-shrink: 0;
}

.sug-text {
  flex: 1;
}

/* AI output */
.ai-badge {
  font-size: 9px;
  font-weight: 400;
  color: var(--text3);
  background: var(--navy3);
  padding: 1px 6px;
  border-radius: 3px;
}

.ai-output {
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
}

/* AI history */
.ai-history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ai-history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-history-item:hover {
  border-color: var(--teal);
}

.ai-history-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-history-time {
  font-size: 11px;
  color: var(--text2);
  font-family: var(--mono);
}

.ai-history-duration {
  font-size: 10px;
  color: var(--text3);
  background: var(--navy3);
  padding: 1px 6px;
  border-radius: 3px;
}

.ai-history-del {
  background: none;
  border: none;
  color: var(--text3);
  font-size: 11px;
  cursor: pointer;
  padding: 2px 4px;
  opacity: 0.5;
  transition: all 0.2s;
}

.ai-history-del:hover {
  opacity: 1;
  color: var(--red);
}

/* Markdown body */
.markdown-body {
  font-size: 13px;
  color: var(--text);
  line-height: 1.7;
  font-family: var(--sans);
}

.markdown-body :deep(h1) {
  font-size: 18px;
  font-weight: 700;
  color: var(--teal);
  margin: 16px 0 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.markdown-body :deep(h2) {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  margin: 14px 0 6px;
}

.markdown-body :deep(h3) {
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
  margin: 12px 0 4px;
}

.markdown-body :deep(h4) {
  font-size: 12px;
  font-weight: 600;
  color: var(--text2);
  margin: 10px 0 4px;
}

.markdown-body :deep(p) {
  margin: 6px 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

.markdown-body :deep(li) {
  margin: 2px 0;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 11px;
}

.markdown-body :deep(th) {
  background: var(--navy2);
  color: var(--text3);
  padding: 6px 8px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  font-size: 10px;
}

.markdown-body :deep(td) {
  padding: 5px 8px;
  border-bottom: 1px solid rgba(22, 37, 64, 0.5);
  color: var(--text2);
}

.markdown-body :deep(tr:hover td) {
  background: rgba(0, 229, 255, 0.03);
}

.markdown-body :deep(code) {
  background: var(--navy2);
  color: var(--teal);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 11px;
  font-family: var(--mono);
}

.markdown-body :deep(pre) {
  background: var(--navy2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 11px;
  line-height: 1.5;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid var(--teal);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text3);
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 12px 0;
}

.markdown-body :deep(strong) {
  color: var(--text);
  font-weight: 700;
}

.markdown-body :deep(em) {
  color: var(--text2);
}

/* History panel */
.rp-empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--text3);
  font-size: 12px;
}

.history-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 6px;
  transition: all 0.2s;
}

.history-card:hover {
  border-color: var(--border2);
}

.history-card-header {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.history-card-header:hover .history-date {
  color: var(--teal);
}

.history-card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-index {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: var(--teal);
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
}

.history-date {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  font-family: var(--mono);
  transition: color 0.2s;
}

.history-card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.history-duration {
  font-size: 10px;
  color: var(--text3);
  background: var(--navy3);
  padding: 1px 6px;
  border-radius: 3px;
}

.history-arrow {
  font-size: 12px;
  color: var(--text3);
}

.history-del {
  background: none;
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--text3);
  font-size: 10px;
  padding: 2px 8px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.history-del:hover {
  border-color: var(--red);
  color: var(--red);
}
</style>
