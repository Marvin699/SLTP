<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportStore } from '@/stores/pathPlanning/report'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import { useAppStore } from '@/stores/pathPlanning/app'
import RightPanel from '@/components/pathPlanning/RightPanel.vue'

const reportStore = useReportStore()
const optStore = useOptimizerStore()
const appStore = useAppStore()

const showRight = ref(false)
const rightType = ref(null)
const showEditor = ref(false)
const editingData = ref(null)
const MAX_COMPARE = 4                    // 最多支持 4 方案对比
const selectedReports = ref([])          // 选中的报告ID
const compareData = ref(null)            // 对比数据 { items: [...] }

const canGenerate = computed(() => optStore.result && !reportStore.loading)
const canCompare = computed(() => selectedReports.value.length >= 2 && selectedReports.value.length <= MAX_COMPARE)

onMounted(() => {
  console.log('Module6 mounted, loading history...')
  reportStore.loadHistory().then(() => {
    console.log('History loaded:', reportStore.history)
  })
})

async function handleGenerate() {
  const data = await reportStore.generateReport()
  console.log('生成报告返回:', data)
  if (data) {
    rightType.value = 'result'
    showRight.value = true
  }
}

function handleReset() {
  reportStore.resetReport()
  showRight.value = false
  rightType.value = null
}

function closeRight() {
  showRight.value = false
  rightType.value = null
}

async function handleViewHistory(reportId) {
  console.log('点击历史报告:', reportId)
  const data = await reportStore.viewReportDetail(reportId)
  console.log('获取到的数据:', data)
  if (data) {
    rightType.value = 'result'
    showRight.value = true
    console.log('设置显示预览:', rightType.value, showRight.value)
  }
}

function toggleSelect(reportId) {
  const index = selectedReports.value.indexOf(reportId)
  if (index > -1) {
    selectedReports.value.splice(index, 1)
  } else if (selectedReports.value.length < MAX_COMPARE) {
    selectedReports.value.push(reportId)
  }
}

function isSelected(reportId) {
  return selectedReports.value.includes(reportId)
}

async function handleCompare() {
  if (selectedReports.value.length < 2) return

  // 拉取 N 个报告详情，对比结构改为数组（支持 2~4 个方案）
  const details = await Promise.all(selectedReports.value.map(id => reportStore.viewReportDetail(id)))
  const items = details.filter(Boolean).map((r, i) => ({
    id: r.id,
    name: r.report_data?.project_name || `方案${i + 1}`,
    scheme_type: r.report_data?.scheme_type || '',
    stats: r.report_data?.stats || {},
    scores: r.report_data?.scores || {},
    aco_params: r.aco_params || null,     // 派生重生成用
    is_chosen: r.is_chosen || false,
    choice_reason: r.choice_reason || '',
  }))
  if (items.length < 2) return
  compareData.value = { items }
  rightType.value = 'compare'
  showRight.value = true
}

/** 择优决策：选定最终方案并记录理由 */
async function handleChoose(item) {
  const reason = prompt(
    `选定「${item.name}」为最终方案。\n请简述决策理由（将随报告存档）：`,
    item.scores && Object.keys(item.scores).length ? '综合四维评分最优' : ''
  )
  if (reason === null) return
  const res = await reportStore.chooseReportItem(item.id, reason)
  if (res) {
    // 同步更新对比面板与本地徽标
    compareData.value.items.forEach(it => {
      it.is_chosen = it.id === item.id
      it.choice_reason = it.id === item.id ? res.choice_reason : ''
    })
  }
}

/** 从此方案派生重生成：回填当时的 ACO 参数到路径规划面板 */
function handleDerive(item) {
  if (!item.aco_params) {
    alert('该报告生成于旧版本，未记录 ACO 参数；\n请以当前规划面板的参数为基础手动调整。')
    appStore.setModule(4)
    return
  }
  optStore.acoParams = JSON.parse(JSON.stringify(item.aco_params))
  optStore.regenHints = {
    hints: [`已从报告「${item.name}」回填当时的 ACO 参数（蚂蚁数/迭代次数等），可在此基础微调后重新规划`],
    params: null,
  }
  appStore.setModule(4)
}

async function handleDelete(reportId) {
  if (confirm('确定删除此报告？')) {
    await reportStore.deleteReportItem(reportId)
  }
}

function handleEdit() {
  if (reportStore.reportData) {
    editingData.value = JSON.parse(JSON.stringify(reportStore.reportData))
    showEditor.value = true
  }
}

async function handleSaveEdit() {
  const res = await reportStore.updateReportData(editingData.value)
  if (res) {
    showEditor.value = false
  }
}

function handleDownloadWord() {
  const url = reportStore.getWordDownloadUrl()
  if (url) {
    window.open(url, '_blank')
  }
}

function handleDownloadPdf() {
  const url = reportStore.getPdfDownloadUrl()
  if (url) {
    window.open(url, '_blank')
  }
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

function scoreName(key) {
  const names = {
    safety: '安全性',
    timeliness: '时效性',
    economy: '经济性',
    feasibility: '可行性'
  }
  return names[key] || key
}

function scoreClass(score) {
  if (score >= 80) return 'good'
  if (score >= 60) return 'warning'
  return 'bad'
}

// ─── 对比表格定义（指标行配置） ───
const statRows = [
  { label: '总飞行距离 (km)', get: r => r.stats?.total_distance || 0, better: 'min' },
  { label: '总飞行时间 (分钟)', get: r => r.stats?.total_time || 0, better: 'min' },
  { label: '总趟次', get: r => r.stats?.total_trips || 0, better: 'min' },
  { label: '无人机数量', get: r => r.stats?.drone_count || 0, better: 'min' },
  { label: '配送村庄数', get: r => r.stats?.village_count || 0, better: 'max' },
]
const scoreRows = [
  { label: '安全评分', get: r => r.scores?.safety, better: 'max' },
  { label: '时效评分', get: r => r.scores?.timeliness, better: 'max' },
  { label: '经济评分', get: r => r.scores?.economy, better: 'max' },
  { label: '可行评分', get: r => r.scores?.feasibility, better: 'max' },
]

/** 该单元格是否为该行最优 */
function isBest(row, value) {
  const vals = compareData.value.items.map(row.get).filter(v => v !== undefined && v !== null && v !== '')
  if (vals.length < 2 || value === undefined || value === null || value === '') return false
  const best = row.better === 'min' ? Math.min(...vals) : Math.max(...vals)
  return Number(value) === Number(best)
}

function formatDiff(val1, val2) {
  if (val1 === undefined || val2 === undefined) return '-'
  const diff = val1 - val2
  if (diff === 0) return '相同'
  const sign = diff > 0 ? '+' : ''
  return `${sign}${diff.toFixed(2)}`
}

/** 差值方向类（含最优方向语义） */
function diffClass(row, val1, val2) {
  if (val1 === undefined || val2 === undefined || val1 === val2) return 'same'
  const firstBetter = row.better === 'min' ? val1 < val2 : val1 > val2
  return firstBetter ? 'better' : 'worse'
}

function generateCompareSummary() {
  if (!compareData.value?.items?.length) return ''
  const items = compareData.value.items

  if (items.length === 2) {
    // 双方案：逐项比较给文字结论
    const [r1, r2] = items
    const distanceDiff = (r1.stats?.total_distance || 0) - (r2.stats?.total_distance || 0)
    const timeDiff = (r1.stats?.total_time || 0) - (r2.stats?.total_time || 0)
    const tripsDiff = (r1.stats?.total_trips || 0) - (r2.stats?.total_trips || 0)
    const summary = []
    if (distanceDiff < 0) summary.push(`${r1.name}的总飞行距离更短，节省 ${Math.abs(distanceDiff).toFixed(2)} km`)
    else if (distanceDiff > 0) summary.push(`${r2.name}的总飞行距离更短，节省 ${Math.abs(distanceDiff).toFixed(2)} km`)
    if (timeDiff < 0) summary.push(`${r1.name}的总飞行时间更短，节省 ${Math.abs(timeDiff).toFixed(2)} 分钟`)
    else if (timeDiff > 0) summary.push(`${r2.name}的总飞行时间更短，节省 ${Math.abs(timeDiff).toFixed(2)} 分钟`)
    if (tripsDiff < 0) summary.push(`${r1.name}的总趟次更少，减少 ${Math.abs(tripsDiff)} 趟`)
    else if (tripsDiff > 0) summary.push(`${r2.name}的总趟次更少，减少 ${Math.abs(tripsDiff)} 趟`)
    return summary.length === 0 ? '两个方案在核心指标上表现相同' : summary.join('；') + '。'
  }

  // 多方案（3~4 个）：按指标指出最优者
  const summary = []
  for (const row of [...statRows.slice(0, 3), ...scoreRows]) {
    const vals = items.map(it => ({ name: it.name, v: row.get(it) })).filter(x => x.v !== undefined && x.v !== null && x.v !== '')
    if (vals.length < 2) continue
    const best = row.better === 'min'
      ? Math.min(...vals.map(x => x.v))
      : Math.max(...vals.map(x => x.v))
    const winners = vals.filter(x => Number(x.v) === Number(best)).map(x => x.name)
    if (winners.length === 1) {
      const unit = scoreRows.includes(row) ? `（${best}分）` : ''
      summary.push(`「${row.label}」最优：${winners[0]}${unit}`)
    }
  }
  return summary.length === 0 ? '各方案在主要指标上表现接近' : summary.join('；') + '。'
}
</script>

<template>
  <div class="module6-container">
    <!-- 左侧操作区 -->
    <div class="module-left">
      <div class="module-header">
        <h2 class="module-title">📊 方案优出</h2>
        <p class="module-desc">生成并导出方案报告</p>
      </div>
      
      <!-- 方案类型设置 -->
      <div class="config-section">
        <label class="config-label">方案类型</label>
        <input 
          v-model="reportStore.schemeType" 
          class="config-input"
          placeholder="输入方案类型"
        />
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button 
          class="btn btn-primary"
          :disabled="!canGenerate"
          @click="handleGenerate"
        >
          <span v-if="reportStore.loading">生成中...</span>
          <span v-else>生成报告</span>
        </button>
        
        <button 
          v-if="reportStore.hasReport"
          class="btn btn-secondary"
          @click="handleEdit"
        >
          编辑报告
        </button>
        
        <button 
          v-if="reportStore.hasReport"
          class="btn btn-success"
          @click="handleDownloadWord"
        >
          下载Word
        </button>
        
        <button 
          v-if="reportStore.hasReport"
          class="btn btn-info"
          @click="handleDownloadPdf"
        >
          下载PDF
        </button>
        
        <button 
          v-if="reportStore.hasReport"
          class="btn btn-warning"
          @click="handleReset"
        >
          重置
        </button>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="reportStore.error" class="error-msg">
        {{ reportStore.error }}
      </div>
      
      <!-- 历史记录 -->
      <div class="history-section">
        <div class="history-header">
          <h3 class="history-title">历史报告 ({{ reportStore.history.length }})</h3>
          <button 
            v-if="canCompare"
            class="btn btn-compare"
            @click="handleCompare"
          >
            对比选中方案
          </button>
        </div>
        <div v-if="reportStore.historyLoading" class="loading-text">加载中...</div>
        <div v-else-if="reportStore.history.length === 0" class="empty-text">暂无历史报告</div>
        <div v-else class="history-list">
          <div 
            v-for="item in reportStore.history" 
            :key="item.id"
            class="history-item"
            :class="{ active: reportStore.reportId === item.id, selected: isSelected(item.id) }"
          >
            <div class="history-select">
              <input 
                type="checkbox" 
                :checked="isSelected(item.id)"
                @click.stop="toggleSelect(item.id)"
              />
            </div>
            <div class="history-content" @click="handleViewHistory(item.id)">
              <div class="history-name">
                {{ item.project_name || item.filename }}
                <span v-if="item.is_chosen" class="chosen-badge inline" :title="item.choice_reason">🏆 最终方案</span>
              </div>
              <div class="history-meta">
                <span class="history-type">{{ item.scheme_type }}</span>
                <span class="history-time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
            <button 
              class="history-delete"
              @click.stop="handleDelete(item.id)"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧预览区 -->
    <RightPanel v-if="showRight" title="报告预览" @close="closeRight">
      <div v-if="rightType === 'result' && reportStore.reportData" class="preview-container">
          <!-- 报告内容 -->
          <div class="report-preview">
            <!-- 封面 -->
            <div class="report-header">
              <h1 class="report-title">{{ reportStore.reportData.project_name }}</h1>
              <h2 class="report-subtitle">{{ reportStore.reportData.scheme_type }}</h2>
              <p class="report-note">（{{ reportStore.reportData.subtitle }}）</p>
              <p class="report-time">生成时间：{{ reportStore.reportData.generated_at }}</p>
            </div>
            
            <!-- 项目概况 -->
            <div class="report-section">
              <h3>一、项目概况</h3>
              <div class="overview-text">
                本次无人机应急物资配送任务以{{ reportStore.reportData.depot?.name || '未知' }}为配送中心，
                共需配送{{ reportStore.reportData.stats?.village_count }}个村庄，总物资重量约{{ reportStore.reportData.stats?.total_weight }}kg。
                调配{{ reportStore.reportData.stats?.drone_count }}架无人机执行配送任务，
                预计总飞行距离{{ reportStore.reportData.stats?.total_distance }}km，总飞行时间{{ reportStore.reportData.stats?.total_time }}分钟，
                共需执行{{ reportStore.reportData.stats?.total_trips }}趟次。
              </div>
              
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-label">总飞行距离</span>
                  <span class="stat-value">{{ reportStore.reportData.stats?.total_distance }} km</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总飞行时间</span>
                  <span class="stat-value">{{ reportStore.reportData.stats?.total_time }} 分钟</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总趟次</span>
                  <span class="stat-value">{{ reportStore.reportData.stats?.total_trips }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">无人机数量</span>
                  <span class="stat-value">{{ reportStore.reportData.stats?.drone_count }}</span>
                </div>
              </div>
            </div>
            
            <!-- 方案评估 -->
            <div class="report-section" v-if="reportStore.reportData.scores && Object.keys(reportStore.reportData.scores).length > 0">
              <h3>方案评估</h3>
              <div class="scores-grid">
                <div class="score-item" v-for="(score, key) in reportStore.reportData.scores" :key="key">
                  <span class="score-name">{{ scoreName(key) }}</span>
                  <span class="score-value" :class="scoreClass(score)">{{ score }}分</span>
                </div>
              </div>
            </div>
            
            <!-- 航线规划 -->
            <div class="report-section">
              <h3>二、航线规划与调度</h3>
              
              <h4>路径汇总</h4>
              <table class="report-table" v-if="reportStore.reportData.route_table?.length">
                <thead>
                  <tr>
                    <th>路径编号</th>
                    <th>无人机</th>
                    <th>路径</th>
                    <th>距离(km)</th>
                    <th>时间(min)</th>
                    <th>配送重量(kg)</th>
                    <th>目标村庄</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="route in reportStore.reportData.route_table" :key="route.route_id">
                    <td>{{ route.route_id }}</td>
                    <td>{{ route.drone_name }}</td>
                    <td>{{ route.route_path }}</td>
                    <td>{{ route.distance }}</td>
                    <td>{{ route.time }}</td>
                    <td>{{ route.weight }}</td>
                    <td>{{ route.village_name }}</td>
                  </tr>
                </tbody>
              </table>
              
              <h4>村庄配送详情</h4>
              <table class="report-table" v-if="reportStore.reportData.village_table?.length">
                <thead>
                  <tr>
                    <th>村庄编号</th>
                    <th>村庄名称</th>
                    <th>需求重量(kg)</th>
                    <th>配送无人机</th>
                    <th>趟次</th>
                    <th>特殊要求</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="village in reportStore.reportData.village_table" :key="village.village_id">
                    <td>{{ village.village_id }}</td>
                    <td>{{ village.village_name }}</td>
                    <td>{{ village.demand_weight }}</td>
                    <td>{{ village.drone_name }}</td>
                    <td>{{ village.trip_count }}</td>
                    <td>{{ village.special_req }}</td>
                  </tr>
                </tbody>
              </table>
              
              <h4>无人机配送详情</h4>
              <table class="report-table" v-if="reportStore.reportData.drone_table?.length">
                <thead>
                  <tr>
                    <th>无人机编号</th>
                    <th>机型</th>
                    <th>总飞行距离(km)</th>
                    <th>总飞行时间(min)</th>
                    <th>总趟次</th>
                    <th>服务村庄</th>
                    <th>备注</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="drone in reportStore.reportData.drone_table" :key="drone.drone_id">
                    <td>{{ drone.drone_id }}</td>
                    <td>{{ drone.drone_type }}</td>
                    <td>{{ drone.total_distance }}</td>
                    <td>{{ drone.total_time }}</td>
                    <td>{{ drone.total_trips }}</td>
                    <td>{{ drone.villages }}</td>
                    <td>{{ drone.note }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else class="empty-preview">
          暂无报告数据
        </div>
    </RightPanel>
    
    <!-- 对比面板（2~4 方案） -->
    <RightPanel v-if="showRight && rightType === 'compare'" title="方案对比与择优" @close="closeRight">
      <div v-if="compareData" class="compare-container">
        <div class="compare-header">
          <div
            v-for="item in compareData.items"
            :key="item.id"
            class="compare-item"
            :class="{ chosen: item.is_chosen }"
          >
            <h4>{{ item.name }}</h4>
            <p class="compare-scheme">{{ item.scheme_type }}</p>
            <div v-if="item.is_chosen" class="chosen-badge">🏆 最终方案</div>
            <div class="compare-actions">
              <button
                class="cmp-btn choose"
                :disabled="item.is_chosen"
                :title="item.is_chosen ? `已选定：${item.choice_reason}` : '选定此方案为最终方案'"
                @click="handleChoose(item)"
              >
                {{ item.is_chosen ? '已选定' : '✓ 选定此方案' }}
              </button>
              <button
                class="cmp-btn derive"
                title="回填该方案生成时的 ACO 参数并跳到路径规划"
                @click="handleDerive(item)"
              >↻ 派生重生成</button>
            </div>
          </div>
        </div>

        <div class="compare-section">
          <h3>核心指标对比（绿色为该行最优）</h3>
          <table class="compare-table">
            <thead>
              <tr>
                <th>指标</th>
                <th v-for="it in compareData.items" :key="it.id">{{ it.name.slice(0, 8) }}</th>
                <th v-if="compareData.items.length === 2">差值</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in statRows" :key="row.label">
                <td>{{ row.label }}</td>
                <td
                  v-for="it in compareData.items"
                  :key="it.id"
                  :class="{ better: isBest(row, row.get(it)) }"
                >{{ row.get(it) }}</td>
                <td
                  v-if="compareData.items.length === 2"
                  :class="diffClass(row, row.get(compareData.items[0]), row.get(compareData.items[1]))"
                >
                  {{ formatDiff(row.get(compareData.items[0]), row.get(compareData.items[1])) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="compare-section" v-if="compareData.items.some(it => it.scores && Object.keys(it.scores).length)">
          <h3>四维评分对比</h3>
          <table class="compare-table">
            <thead>
              <tr>
                <th>维度</th>
                <th v-for="it in compareData.items" :key="it.id">{{ it.name.slice(0, 8) }}</th>
                <th v-if="compareData.items.length === 2">差值</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in scoreRows" :key="row.label">
                <td>{{ row.label }}</td>
                <td
                  v-for="it in compareData.items"
                  :key="it.id"
                  :class="{ better: isBest(row, row.get(it)) }"
                >{{ row.get(it) ?? '-' }}</td>
                <td
                  v-if="compareData.items.length === 2 && row.get(compareData.items[0]) != null && row.get(compareData.items[1]) != null"
                  :class="diffClass(row, row.get(compareData.items[0]), row.get(compareData.items[1]))"
                >
                  {{ formatDiff(row.get(compareData.items[0]), row.get(compareData.items[1])) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="compare-summary">
          <h3>对比结论</h3>
          <div class="summary-text">{{ generateCompareSummary() }}</div>
        </div>
      </div>
    </RightPanel>
    
    <!-- 编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showEditor" class="editor-modal">
        <div class="editor-overlay" @click="showEditor = false"></div>
        <div class="editor-content">
          <div class="editor-header">
            <h3>编辑报告</h3>
            <button class="editor-close" @click="showEditor = false">✕</button>
          </div>
          <div class="editor-body">
            <div class="editor-field">
              <label>项目名称</label>
              <input v-model="editingData.project_name" />
            </div>
            <div class="editor-field">
              <label>方案类型</label>
              <input v-model="editingData.scheme_type" />
            </div>
            <div class="editor-field">
              <label>副标题</label>
              <input v-model="editingData.subtitle" />
            </div>
          </div>
          <div class="editor-footer">
            <button class="btn btn-primary" @click="handleSaveEdit">保存</button>
            <button class="btn btn-secondary" @click="showEditor = false">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.module6-container {
  display: flex;
  height: 100%;
  gap: 18px;
  padding: 18px;
}

.module-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
}

.module-header {
  text-align: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.module-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 8px 0;
}

.module-desc {
  color: #666;
  margin: 0;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-label {
  font-weight: bold;
  font-size: 14px;
}

.config-input {
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.btn {
  padding: 10px 18px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s;
}

.btn:hover:not(:disabled) {
  opacity: 0.8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-secondary {
  background: #52c41a;
  color: white;
}

.btn-success {
  background: #237804;
  color: white;
}

.btn-info {
  background: #13c2c2;
  color: white;
}

.btn-warning {
  background: #faad14;
  color: white;
}

.error-msg {
  color: #f5222d;
  padding: 10px;
  background: #fff1f0;
  border: 1px solid #ffa39e;
  border-radius: 4px;
}

.history-section {
  flex: 1;
  overflow-y: auto;
}

.history-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 12px 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  padding: 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.history-item:hover {
  background: #f5f5f5;
  border-color: #1890ff;
}

.history-item.active {
  background: #e6f7ff;
  border-color: #1890ff;
}

.history-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  gap: 10px;
  font-size: 13px;
  color: #666;
}

.history-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .history-delete {
  opacity: 1;
}

.preview-container {
  height: 100%;
  overflow-y: auto;
}

.empty-preview {
  text-align: center;
  color: #999;
  padding: 42px;
}

/* 报告预览样式 */
.report-preview {
  padding: 22px;
  background: white;
}

.report-header {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid #1890ff;
}

.report-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
}

.report-subtitle {
  font-size: 20px;
  margin: 0 0 8px 0;
}

.report-note {
  color: #666;
  margin: 0 0 8px 0;
}

.report-time {
  color: #999;
  font-size: 13px;
  margin: 0;
}

.report-section {
  margin-bottom: 24px;
}

.report-section h3 {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.report-section h4 {
  font-size: 14px;
  font-weight: bold;
  margin: 16px 0 8px 0;
}

.overview-text {
  line-height: 1.8;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 14px;
  background: #f5f5f5;
  border-radius: 4px;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: bold;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background: #f5f5f5;
  border-radius: 4px;
}

.score-name {
  font-weight: bold;
}

.score-value {
  font-weight: bold;
  padding: 6px 14px;
  border-radius: 12px;
}

.score-value.good {
  background: #f6ffed;
  color: #52c41a;
}

.score-value.warning {
  background: #fffbe6;
  color: #faad14;
}

.score-value.bad {
  background: #fff1f0;
  color: #f5222d;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
  font-size: 13px;
}

.report-table th,
.report-table td {
  border: 1px solid #e0e0e0;
  padding: 10px;
  text-align: center;
}

.report-table th {
  background: #4472C4;
  color: white;
  font-weight: bold;
}

.report-table tr:nth-child(even) {
  background: #f5f5f5;
}

/* 编辑器弹窗 */
.editor-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.editor-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.editor-content {
  position: relative;
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px;
  border-bottom: 1px solid #e0e0e0;
}

.editor-header h3 {
  margin: 0;
}

.editor-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.editor-body {
  padding: 18px;
}

.editor-field {
  margin-bottom: 16px;
}

.editor-field label {
  display: block;
  margin-bottom: 4px;
  font-weight: bold;
}

.editor-field input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.editor-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 18px;
  border-top: 1px solid #e0e0e0;
}

.loading-text,
.empty-text {
  text-align: center;
  color: #999;
  padding: 26px;
}

/* 历史记录勾选 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-select {
  flex-shrink: 0;
}

.history-select input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.history-content {
  flex: 1;
  cursor: pointer;
}

.history-item.selected {
  background: #e6f7ff;
  border-color: #1890ff;
}

.btn-compare {
  background: #722ed1;
  color: white;
  font-size: 13px;
  padding: 8px 14px;
}

/* 对比样式 */
.compare-container {
  padding: 18px;
}

.compare-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
}

.compare-item {
  flex: 1;
  text-align: center;
}

.compare-item h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
}

.compare-scheme {
  color: #666;
  font-size: 13px;
  margin: 0;
}

.compare-vs {
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
  padding: 0 16px;
}

/* 择优决策相关 */
.compare-item.chosen {
  outline: 2px solid #faad14;
  border-radius: 6px;
  background: rgba(250, 173, 20, 0.06);
}

.chosen-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: bold;
  color: #d48806;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 10px;
  padding: 2px 10px;
}

.chosen-badge.inline {
  margin-left: 6px;
  padding: 0 8px;
  font-size: 11px;
}

.compare-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 10px;
  flex-wrap: wrap;
}

.cmp-btn {
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.cmp-btn:hover:not(:disabled) { opacity: 0.85; }
.cmp-btn:disabled { opacity: 0.55; cursor: default; }

.cmp-btn.choose {
  background: #faad14;
  color: white;
  font-weight: bold;
}

.cmp-btn.derive {
  background: #722ed1;
  color: white;
}

.compare-section {
  margin-bottom: 24px;
}

.compare-section h3 {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.compare-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.compare-table th,
.compare-table td {
  border: 1px solid #e0e0e0;
  padding: 12px;
  text-align: center;
}

.compare-table th {
  background: #f5f5f5;
  font-weight: bold;
}

.compare-table td.better {
  color: #52c41a;
  font-weight: bold;
}

.compare-table td.worse {
  color: #f5222d;
  font-weight: bold;
}

.compare-table td.same {
  color: #999;
}

.scores-compare {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.score-compare-item {
  display: flex;
  align-items: center;
  gap: 14px;
}

.compare-summary {
  margin-top: 24px;
  padding: 18px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
}

.compare-summary h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.summary-text {
  line-height: 1.6;
  font-size: 14px;
}
</style>
