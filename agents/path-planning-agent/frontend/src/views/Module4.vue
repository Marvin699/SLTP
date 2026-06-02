<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { usePointsStore } from '../stores/points'
import { useMaterialsStore } from '../stores/materials'
import { useUavsStore } from '../stores/uavs'
import { useOptimizerStore } from '../stores/optimizer'
import RightPanel from '../components/RightPanel.vue'

const ptsStore = usePointsStore()
const matStore = useMaterialsStore()
const uavStore = useUavsStore()
const optStore = useOptimizerStore()

const showRight = ref(false)
const rightType = ref(null)
const showAdvanced = ref(false)
const localParams = ref({})
const activeTab = ref('route') // 'route' | 'village' | 'drone' | 'feasibility'
const selectedTripIndex = ref(-1) // 当前选中的航次索引

function toggleDroneRoute(droneId) {
  if (optStore.selectedDroneId === droneId) {
    optStore.setSelectedDroneId(null)
  } else {
    optStore.setSelectedDroneId(droneId)
  }
}

const taskStats = computed(() => {
  const demandCount = ptsStore.demands.length
  const totalWeight = ptsStore.demands.reduce((sum, pt) => {
    const a = matStore.getAssignment(pt.id)
    return sum + (a?.total_weight || 0)
  }, 0)
  const uavCount = uavStore.totalCount
  return { demandCount, totalWeight, uavCount }
})

const canRun = computed(() =>
  taskStats.value.demandCount > 0 &&
  taskStats.value.uavCount > 0 &&
  !optStore.loading
)

onMounted(async () => {
  if (ptsStore.demands.length > 0 && uavStore.selections.length > 0) {
    await optStore.fetchDefaultParams()
    optStore.error = null
  }
  if (optStore.acoParams) {
    localParams.value = { ...optStore.acoParams }
  }
  // 自动加载历史记录
  await optStore.loadHistory()
})

watch(() => optStore.acoParams, (p) => {
  if (p) localParams.value = { ...p }
}, { immediate: true })

async function handleRun() {
  const res = await optStore.runOptimization(localParams.value)
  if (res) {
    rightType.value = 'result'
    showRight.value = true
    activeTab.value = 'route'
  }
}

function handleReset() {
  optStore.resetResult()
  showRight.value = false
  rightType.value = null
}

function closeRight() {
  showRight.value = false
  rightType.value = null
}

function formatTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function viewHistory(recordId) {
  const data = await optStore.viewHistoryDetail(recordId)
  if (data) {
    rightType.value = 'result'
    showRight.value = true
    activeTab.value = 'route'
  }
}

async function deleteHistory(recordId) {
  if (!confirm('确定要删除这条记录吗？')) return
  await optStore.deleteRecord(recordId)
}
</script>

<template>
  <div class="module4">
    <div class="mod-title">
      <span class="mod-icon">🗺</span>
      <span>路径规划</span>
    </div>

    <!-- 任务概览 -->
    <div class="task-overview">
      <div class="stat-item">
        <span class="stat-value">{{ taskStats.demandCount }}</span>
        <span class="stat-label">需求点</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ taskStats.totalWeight.toFixed(0) }}</span>
        <span class="stat-label">总重量(kg)</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ taskStats.uavCount }}</span>
        <span class="stat-label">无人机</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-row">
      <button class="btn-primary" :disabled="!canRun" @click="handleRun">
        {{ optStore.loading ? '规划中...' : '开始规划' }}
      </button>
      <button class="btn-secondary" :disabled="!optStore.result" @click="handleReset">
        重置
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="optStore.error" class="error-msg">{{ optStore.error }}</div>

    <!-- 加载状态 -->
    <div v-if="optStore.loading" class="loading-bar"><div class="loading-bar-inner" /></div>

    <!-- 高级设置 -->
    <div class="section">
      <div class="section-header" @click="showAdvanced = !showAdvanced">
        <span>高级优化参数</span>
        <span class="chevron" :class="{ open: showAdvanced }">▸</span>
      </div>
      <div v-if="showAdvanced" class="section-body">
        <div class="param-grid">
          <label class="param-item">
            <span class="param-name">蚂蚁数量</span>
            <input v-model.number="localParams.num_ants" type="number" min="5" max="200" class="param-input" />
          </label>
          <label class="param-item">
            <span class="param-name">迭代次数</span>
            <input v-model.number="localParams.max_iterations" type="number" min="10" max="500" class="param-input" />
          </label>
          <label class="param-item">
            <span class="param-name">信息素权重 α</span>
            <input v-model.number="localParams.alpha" type="number" min="0.1" max="5" step="0.1" class="param-input" />
          </label>
          <label class="param-item">
            <span class="param-name">启发式权重 β</span>
            <input v-model.number="localParams.beta" type="number" min="0.1" max="10" step="0.1" class="param-input" />
          </label>
          <label class="param-item">
            <span class="param-name">挥发率 ρ</span>
            <input v-model.number="localParams.evaporation_rate" type="number" min="0.1" max="0.9" step="0.05" class="param-input" />
          </label>
          <label class="param-item">
            <span class="param-name">精英蚂蚁数</span>
            <input v-model.number="localParams.elite_ants" type="number" min="1" max="10" class="param-input" />
          </label>
        </div>
      </div>
    </div>

    <!-- 总体统计（规划完成后） -->
    <div v-if="optStore.result" class="section">
      <div class="section-header">
        <span>总体统计</span>
        <span class="badge">{{ optStore.elapsed }}s</span>
      </div>
      <div class="section-body">
        <div class="summary-grid">
          <div class="sum-card">
            <span class="sum-val">{{ optStore.totalDistance.toFixed(1) }}</span>
            <span class="sum-unit">km</span>
            <span class="sum-label">总飞行距离</span>
          </div>
          <div class="sum-card">
            <span class="sum-val">{{ optStore.totalTime.toFixed(0) }}</span>
            <span class="sum-unit">min</span>
            <span class="sum-label">总飞行时间</span>
          </div>
          <div class="sum-card">
            <span class="sum-val">{{ optStore.totalTrips }}</span>
            <span class="sum-unit">趟</span>
            <span class="sum-label">总趟次</span>
          </div>
          <div class="sum-card">
            <span class="sum-val">{{ optStore.droneCount }}</span>
            <span class="sum-unit">架</span>
            <span class="sum-label">使用无人机</span>
          </div>
          <div class="sum-card">
            <span class="sum-val">{{ optStore.villageCount }}</span>
            <span class="sum-unit">个</span>
            <span class="sum-label">服务村庄</span>
          </div>
          <div class="sum-card">
            <span class="sum-val" :class="optStore.feasible ? 'good' : 'bad'">
              {{ optStore.feasible ? '✓' : '✗' }}
            </span>
            <span class="sum-unit"></span>
            <span class="sum-label">方案可行性</span>
          </div>
        </div>

        <!-- 可行性详情 -->
        <div v-if="optStore.feasibility" class="feasibility-box" :class="optStore.feasible ? 'feasible' : 'infeasible'">
          <div class="feasibility-header">
            <span class="feasibility-icon">{{ optStore.feasible ? '✓' : '!' }}</span>
            <span class="feasibility-text">{{ optStore.feasibleText }}</span>
          </div>
          <!-- 问题列表 -->
          <div v-if="optStore.feasibilityIssues.length > 0" class="feasibility-issues">
            <div v-for="(issue, i) in optStore.feasibilityIssues" :key="'i'+i" class="issue-item">
              <span class="issue-icon">!</span>
              <span>{{ issue }}</span>
            </div>
          </div>
          <!-- 警告列表 -->
          <div v-if="optStore.feasibilityWarnings.length > 0" class="feasibility-warnings">
            <div v-for="(w, i) in optStore.feasibilityWarnings" :key="'w'+i" class="warning-item">
              <span class="warning-icon">~</span>
              <span>{{ w }}</span>
            </div>
          </div>
        </div>

        <button class="btn-detail" @click="rightType = 'result'; showRight = true">
          查看详细结果 →
        </button>
      </div>
    </div>

    <!-- 运行信息 -->
    <div v-if="optStore.result" class="run-info">
      <span>耗时 {{ optStore.elapsed }}s</span>
    </div>

    <!-- 历史记录 -->
    <div class="section">
      <div class="section-header">
        <span>规划历史</span>
        <span class="badge">{{ optStore.history.length }}条</span>
      </div>
      <div class="section-body">
        <div v-if="optStore.historyLoading" class="loading-bar"><div class="loading-bar-inner" /></div>
        <div v-else-if="optStore.history.length === 0" class="empty-hint">
          暂无规划记录
        </div>
        <div v-else class="history-list">
          <div
            v-for="record in optStore.history"
            :key="record.id"
            class="history-item"
          >
            <div class="history-main">
              <div class="history-meta">
                <span class="history-time">{{ formatTime(record.created_at) }}</span>
                <span class="history-stats">
                  {{ record.village_count }}村 / {{ record.drone_count }}机 / {{ record.total_trips }}趟
                </span>
              </div>
              <div class="history-numbers">
                <span class="history-dist">{{ record.total_distance?.toFixed(1) }}km</span>
                <span class="history-energy">{{ record.total_energy?.toFixed(0) }}kWh</span>
              </div>
            </div>
            <div class="history-actions">
              <button class="btn-history-view" @click="viewHistory(record.id)">查看</button>
              <button class="btn-history-del" @click="deleteHistory(record.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 右侧面板：3个表格 -->
  <RightPanel
    v-if="showRight && rightType === 'result' && optStore.result"
    title="运输方案详情"
    :width="600"
    @close="closeRight"
  >
    <div class="rp-content">
      <!-- Excel 导出按钮 -->
      <button class="btn-excel" @click="optStore.downloadExcel()">
        📊 导出 Excel 运输汇总
      </button>

      <!-- 表格切换 Tab -->
      <div class="rp-tabs">
        <button
          class="rp-tab"
          :class="{ active: activeTab === 'route' }"
          @click="activeTab = 'route'"
        >
          路径汇总
        </button>
        <button
          class="rp-tab"
          :class="{ active: activeTab === 'village' }"
          @click="activeTab = 'village'"
        >
          村庄配送详情
        </button>
        <button
          class="rp-tab"
          :class="{ active: activeTab === 'drone' }"
          @click="activeTab = 'drone'"
        >
          无人机配送详情
        </button>
        <button
          class="rp-tab"
          :class="{ active: activeTab === 'feasibility' }"
          @click="activeTab = 'feasibility'"
        >
          可行性校验
        </button>
      </div>

      <!-- 表格1: 路径汇总 -->
      <div v-if="activeTab === 'route'" class="rp-table-wrap">
        <table class="rp-table">
          <thead>
            <tr>
              <th>路径编号</th>
              <th>无人机</th>
              <th>路径</th>
              <th>途经村庄</th>
              <th>距离(km)</th>
              <th>时间(min)</th>
              <th>配送重量(kg)</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in optStore.routeTable" :key="r.route_id">
              <td>{{ r.route_id }}</td>
              <td>{{ r.drone_name }}</td>
              <td class="mono">{{ r.route_path }}</td>
              <td>{{ r.village_name }}</td>
              <td>{{ (r.distance ?? 0).toFixed(2) }}</td>
              <td>{{ (r.time ?? 0).toFixed(2) }}</td>
              <td>{{ (r.weight ?? 0).toLocaleString() }}</td>
              <td>
                <span :class="['status-badge', r.feasible ? 'success' : 'error']">
                  {{ r.feasible ? '可行' : '不可行' }}
                </span>
              </td>
            </tr>
            <!-- 总计行 -->
            <tr class="total-row">
              <td>总计</td>
              <td>-</td>
              <td>-</td>
              <td>-</td>
              <td>{{ optStore.totalDistance.toFixed(2) }}</td>
              <td>{{ optStore.totalTime.toFixed(2) }}</td>
              <td>{{ optStore.result?.solution?.total_delivered?.toLocaleString() || '-' }}</td>
              <td>-</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 表格2: 村庄配送详情 -->
      <div v-if="activeTab === 'village'" class="rp-table-wrap">
        <table class="rp-table">
          <thead>
            <tr>
              <th>编号</th>
              <th>村庄</th>
              <th>需求重量(kg)</th>
              <th>配送无人机</th>
              <th>配送重量(kg)</th>
              <th>趟次</th>
              <th>单程距离(km)</th>
              <th>特殊要求</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(v, i) in optStore.villageTable" :key="i">
              <td>{{ v.village_id }}</td>
              <td>{{ v.village_name }}</td>
              <td>{{ (v.demand_weight ?? 0).toLocaleString() }}</td>
              <td>{{ v.drone_name }}</td>
              <td>{{ (v.drone_weight ?? 0).toLocaleString() }}</td>
              <td>{{ v.trip_count }}</td>
              <td>{{ (v.one_way_distance ?? 0).toFixed(2) }}</td>
              <td class="note-cell">{{ v.special_req }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 表格3: 无人机配送详情 -->
      <div v-if="activeTab === 'drone'" class="rp-table-wrap">
        <table class="rp-table">
          <thead>
            <tr>
              <th>编号</th>
              <th>机型</th>
              <th>速度(m/s)</th>
              <th>最大载重(kg)</th>
              <th>总距离(km)</th>
              <th>总时间(min)</th>
              <th>总趟次</th>
              <th>服务村庄</th>
              <th>操作</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in optStore.droneTable" :key="i" :class="{ 'total-row': d.drone_id === '总计' }">
              <td>{{ d.drone_id }}</td>
              <td>{{ d.drone_type }}</td>
              <td>{{ d.speed_ms }}</td>
              <td>{{ d.max_payload }}</td>
              <td>{{ (d.total_distance ?? 0).toFixed(2) }}</td>
              <td>{{ (d.total_time ?? 0).toFixed(2) }}</td>
              <td>{{ d.total_trips }}</td>
              <td class="note-cell">{{ d.villages }}</td>
              <td>
                <button
                  v-if="d.drone_id !== '总计'"
                  class="btn-view-route"
                  :class="{ active: optStore.selectedDroneId === d.drone_id }"
                  @click="toggleDroneRoute(d.drone_id)"
                >
                  {{ optStore.selectedDroneId === d.drone_id ? '隐藏' : '查看路线' }}
                </button>
                <span v-else>-</span>
              </td>
              <td class="note-cell">{{ d.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 表格4: 可行性校验 -->
      <div v-if="activeTab === 'feasibility'" class="rp-feasibility">
        <!-- 总体状态 -->
        <div class="feas-card" :class="optStore.feasible ? 'feas-ok' : 'feas-fail'">
          <span class="feas-icon">{{ optStore.feasible ? '✓' : '✗' }}</span>
          <span class="feas-text">{{ optStore.feasibleText }}</span>
        </div>

        <!-- 趟次统计 -->
        <div v-if="optStore.tripChecks.total > 0" class="feas-stats">
          <div class="feas-stat-item">
            <span class="feas-stat-val">{{ optStore.tripChecks.total }}</span>
            <span class="feas-stat-label">总趟次</span>
          </div>
          <div class="feas-stat-item">
            <span class="feas-stat-val good">{{ optStore.tripChecks.feasible }}</span>
            <span class="feas-stat-label">可行</span>
          </div>
          <div class="feas-stat-item">
            <span class="feas-stat-val" :class="optStore.tripChecks.infeasible > 0 ? 'bad' : ''">{{ optStore.tripChecks.infeasible }}</span>
            <span class="feas-stat-label">不可行</span>
          </div>
          <div class="feas-stat-item">
            <span class="feas-stat-val" :class="optStore.tripChecks.overload > 0 ? 'bad' : ''">{{ optStore.tripChecks.overload }}</span>
            <span class="feas-stat-label">超载</span>
          </div>
          <div class="feas-stat-item">
            <span class="feas-stat-val" :class="optStore.tripChecks.over_range > 0 ? 'bad' : ''">{{ optStore.tripChecks.over_range }}</span>
            <span class="feas-stat-label">超航程</span>
          </div>
        </div>

        <!-- 需求覆盖表 -->
        <div v-if="Object.keys(optStore.demandCoverage).length > 0" class="rp-table-wrap">
          <table class="rp-table">
            <thead>
              <tr>
                <th>村庄</th>
                <th>需求(kg)</th>
                <th>配送(kg)</th>
                <th>缺口(kg)</th>
                <th>覆盖率</th>
                <th>趟次</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(info, name) in optStore.demandCoverage" :key="name">
                <td>{{ name }}</td>
                <td>{{ info.demand.toFixed(1) }}</td>
                <td>{{ info.delivered.toFixed(1) }}</td>
                <td :class="info.shortfall > 0.01 ? 'bad' : ''">{{ info.shortfall.toFixed(1) }}</td>
                <td>{{ info.coverage_pct }}%</td>
                <td>{{ info.trip_count }}</td>
                <td>
                  <span :class="info.shortfall > 0.01 ? 'bad' : 'good'">
                    {{ info.shortfall > 0.01 ? '未完成' : '已完成' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 问题列表 -->
        <div v-if="optStore.feasibilityIssues.length > 0" class="feas-issue-list">
          <div class="feas-issue-title">问题 ({{ optStore.feasibilityIssues.length }})</div>
          <div v-for="(issue, i) in optStore.feasibilityIssues" :key="'fi'+i" class="feas-issue-item">
            <span class="feas-issue-icon">!</span>
            <span>{{ issue }}</span>
          </div>
        </div>

        <!-- 警告列表 -->
        <div v-if="optStore.feasibilityWarnings.length > 0" class="feas-warn-list">
          <div class="feas-warn-title">警告 ({{ optStore.feasibilityWarnings.length }})</div>
          <div v-for="(w, i) in optStore.feasibilityWarnings" :key="'fw'+i" class="feas-warn-item">
            <span class="feas-warn-icon">~</span>
            <span>{{ w }}</span>
          </div>
        </div>
      </div>
    </div>
  </RightPanel>
</template>

<style scoped>
.module4 {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mod-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  font-family: var(--mono);
}

.mod-icon { font-size: 18px; }

/* 任务概览 */
.task-overview { display: flex; gap: 8px; }

.stat-item {
  flex: 1;
  background: var(--navy3);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-value {
  font-size: 18px;
  font-weight: 800;
  color: var(--teal);
  font-family: var(--mono);
}

.stat-label {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
}

/* 操作按钮 */
.action-row { display: flex; gap: 8px; }

.btn-primary {
  flex: 1;
  height: 36px;
  background: var(--teal);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #00c8de; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-secondary {
  height: 36px;
  padding: 0 16px;
  background: transparent;
  color: var(--text2);
  border: 1px solid var(--border2);
  border-radius: 6px;
  font-size: 12px;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover:not(:disabled) { border-color: var(--text3); color: var(--text); }
.btn-secondary:disabled { opacity: 0.3; cursor: not-allowed; }

.error-msg {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  color: #ff4757;
  font-size: 11px;
  font-family: var(--mono);
  padding: 8px 12px;
  border-radius: 4px;
}

.loading-bar {
  height: 3px;
  background: var(--navy3);
  border-radius: 2px;
  overflow: hidden;
}
.loading-bar-inner {
  height: 100%;
  width: 40%;
  background: var(--teal);
  border-radius: 2px;
  animation: loadSlide 1.2s ease-in-out infinite;
}
@keyframes loadSlide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}

/* Section */
.section {
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--navy3);
  font-size: 12px;
  font-weight: 700;
  color: var(--text2);
  font-family: var(--mono);
  cursor: pointer;
  user-select: none;
}
.chevron { transition: transform 0.2s; font-size: 10px; color: var(--text3); }
.chevron.open { transform: rotate(90deg); }
.badge {
  font-size: 10px;
  color: var(--teal);
  background: rgba(0, 229, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}
.section-body { padding: 10px 12px; }

/* 参数网格 */
.param-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.param-item { display: flex; flex-direction: column; gap: 4px; }
.param-name { font-size: 10px; color: var(--text3); font-family: var(--mono); }
.param-input {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text);
  font-size: 12px;
  font-family: var(--mono);
  padding: 5px 8px;
  width: 100%;
  box-sizing: border-box;
}
.param-input:focus { outline: none; border-color: var(--teal); }

/* 总体统计 */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-bottom: 10px;
}
.sum-card {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.sum-val {
  font-size: 18px;
  font-weight: 800;
  color: var(--teal);
  font-family: var(--mono);
}
.sum-val.good { color: #2ed573; }
.sum-val.bad { color: #ff4757; }
.sum-unit { font-size: 10px; color: var(--text3); font-family: var(--mono); }
.sum-label { font-size: 9px; color: var(--text3); font-family: var(--mono); }

.btn-detail {
  width: 100%;
  margin-top: 8px;
  padding: 8px;
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  color: var(--teal);
  font-size: 12px;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-detail:hover { background: rgba(0, 229, 255, 0.15); border-color: rgba(0, 229, 255, 0.4); }

.run-info {
  display: flex;
  gap: 16px;
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
  padding: 4px 0;
}

/* ─── Right Panel ─── */
.rp-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-excel {
  width: 100%;
  padding: 10px;
  background: rgba(46, 213, 115, 0.1);
  border: 1px solid rgba(46, 213, 115, 0.3);
  border-radius: 6px;
  color: #2ed573;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-excel:hover { background: rgba(46, 213, 115, 0.2); }

/* Tabs */
.rp-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}
.rp-tab {
  flex: 1;
  padding: 8px 4px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text3);
  font-size: 11px;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.rp-tab:hover { color: var(--text2); border-color: var(--text3); }
.rp-tab.active {
  color: var(--teal);
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.08);
}

/* Table */
.rp-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 6px;
}
.rp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  font-family: var(--mono);
  white-space: nowrap;
}
.rp-table th {
  background: var(--navy3);
  color: var(--teal);
  font-weight: 700;
  padding: 8px 10px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 1;
}
.rp-table td {
  padding: 6px 10px;
  text-align: center;
  border-bottom: 1px solid rgba(22, 37, 64, 0.5);
  color: var(--text2);
}
.rp-table tr:hover td { background: rgba(0, 229, 255, 0.04); }
.rp-table .total-row td {
  background: var(--navy3);
  color: var(--teal);
  font-weight: 700;
}
.rp-table .mono { font-family: var(--mono); }
.rp-table .note-cell {
  text-align: left;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ─── 可行性校验 ─── */
.feasibility-box {
  margin-top: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-family: var(--mono);
}
.feasibility-box.feasible {
  background: rgba(46, 213, 115, 0.08);
  border: 1px solid rgba(46, 213, 115, 0.25);
}
.feasibility-box.infeasible {
  background: rgba(255, 71, 87, 0.08);
  border: 1px solid rgba(255, 71, 87, 0.25);
}
.feasibility-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.feasibility-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}
.feasible .feasibility-icon {
  background: rgba(46, 213, 115, 0.2);
  color: #2ed573;
}
.infeasible .feasibility-icon {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
}
.feasibility-text {
  font-weight: 700;
  color: var(--text2);
}
.feasibility-issues, .feasibility-warnings {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.issue-item, .warning-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 10px;
  color: var(--text3);
  line-height: 1.4;
}
.issue-icon {
  color: #ff4757;
  font-weight: 700;
  flex-shrink: 0;
}
.warning-icon {
  color: #ffb300;
  font-weight: 700;
  flex-shrink: 0;
}

/* ─── 右侧面板可行性 ─── */
.rp-feasibility {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.feas-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 6px;
  font-family: var(--mono);
}
.feas-card.feas-ok {
  background: rgba(46, 213, 115, 0.1);
  border: 1px solid rgba(46, 213, 115, 0.3);
}
.feas-card.feas-fail {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
}
.feas-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
}
.feas-ok .feas-icon {
  background: rgba(46, 213, 115, 0.2);
  color: #2ed573;
}
.feas-fail .feas-icon {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
}
.feas-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
}
.feas-stats {
  display: flex;
  gap: 6px;
}
.feas-stat-item {
  flex: 1;
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.feas-stat-val {
  font-size: 16px;
  font-weight: 800;
  color: var(--teal);
  font-family: var(--mono);
}
.feas-stat-val.good { color: #2ed573; }
.feas-stat-val.bad { color: #ff4757; }
.feas-stat-label {
  font-size: 9px;
  color: var(--text3);
  font-family: var(--mono);
}
.feas-issue-list, .feas-warn-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.feas-issue-title, .feas-warn-title {
  font-size: 11px;
  font-weight: 700;
  font-family: var(--mono);
  color: var(--text2);
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}
.feas-issue-item, .feas-warn-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 11px;
  color: var(--text3);
  font-family: var(--mono);
  line-height: 1.4;
}
.feas-issue-icon {
  color: #ff4757;
  font-weight: 700;
  flex-shrink: 0;
}
.feas-warn-icon {
  color: #ffb300;
  font-weight: 700;
  flex-shrink: 0;
}
.bad { color: #ff4757; }
.good { color: #2ed573; }

/* 查看路线按钮 */
.btn-view-route {
  padding: 4px 10px;
  background: rgba(0, 229, 255, 0.1);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: 4px;
  color: var(--teal);
  font-size: 10px;
  font-weight: 700;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-view-route:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: rgba(0, 229, 255, 0.5);
}
.btn-view-route.active {
  background: rgba(0, 229, 255, 0.25);
  border-color: var(--teal);
  color: #fff;
}

/* ─── 历史记录 ─── */
.empty-hint {
  text-align: center;
  padding: 20px;
  color: var(--text3);
  font-size: 11px;
  font-family: var(--mono);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--border2);
  background: var(--navy2);
}

.history-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-time {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
}

.history-stats {
  font-size: 10px;
  color: var(--text2);
  font-family: var(--mono);
}

.history-numbers {
  display: flex;
  gap: 8px;
}

.history-dist {
  font-size: 11px;
  color: var(--teal);
  font-family: var(--mono);
  font-weight: 600;
}

.history-energy {
  font-size: 11px;
  color: var(--amber);
  font-family: var(--mono);
  font-weight: 600;
}

.history-actions {
  display: flex;
  gap: 4px;
}

.status-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-family: var(--mono);
}

.status-badge.success {
  background: rgba(46, 213, 115, 0.15);
  color: #2ed573;
  border: 1px solid rgba(46, 213, 115, 0.3);
}

.status-badge.error {
  background: rgba(255, 71, 87, 0.15);
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.3);
}

.btn-history-view,
.btn-history-del {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-history-view {
  background: rgba(0, 229, 255, 0.08);
  color: var(--teal);
  border: 1px solid rgba(0, 229, 255, 0.2);
}

.btn-history-view:hover {
  background: rgba(0, 229, 255, 0.15);
}

.btn-history-del {
  background: rgba(255, 71, 87, 0.08);
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.2);
}

.btn-history-del:hover {
  background: rgba(255, 71, 87, 0.15);
}
</style>
