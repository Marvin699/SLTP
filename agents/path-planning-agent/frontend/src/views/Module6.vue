<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportStore } from '../stores/report'
import { useOptimizerStore } from '../stores/optimizer'
import RightPanel from '../components/RightPanel.vue'

const reportStore = useReportStore()
const optStore = useOptimizerStore()

const showRight = ref(false)
const rightType = ref(null)
const showEditor = ref(false)
const editingData = ref(null)
const selectedReports = ref([])  // 选中的报告ID
const compareData = ref(null)    // 对比数据

const canGenerate = computed(() => optStore.result && !reportStore.loading)
const canCompare = computed(() => selectedReports.value.length === 2)

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
  } else if (selectedReports.value.length < 2) {
    selectedReports.value.push(reportId)
  }
}

function isSelected(reportId) {
  return selectedReports.value.includes(reportId)
}

async function handleCompare() {
  if (selectedReports.value.length !== 2) return
  
  // 获取两个报告的详情
  const report1 = await reportStore.viewReportDetail(selectedReports.value[0])
  const report2 = await reportStore.viewReportDetail(selectedReports.value[1])
  
  if (report1 && report2) {
    compareData.value = {
      report1: {
        id: report1.id,
        name: report1.report_data?.project_name || '方案1',
        scheme_type: report1.report_data?.scheme_type || '',
        stats: report1.report_data?.stats || {},
        scores: report1.report_data?.scores || {},
      },
      report2: {
        id: report2.id,
        name: report2.report_data?.project_name || '方案2',
        scheme_type: report2.report_data?.scheme_type || '',
        stats: report2.report_data?.stats || {},
        scores: report2.report_data?.scores || {},
      }
    }
    rightType.value = 'compare'
    showRight.value = true
  }
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

function getDiffClass(val1, val2) {
  if (!val1 || !val2) return ''
  return val1 < val2 ? 'better' : (val1 > val2 ? 'worse' : 'same')
}

function formatDiff(val1, val2) {
  if (val1 === undefined || val2 === undefined) return '-'
  const diff = val1 - val2
  if (diff === 0) return '相同'
  const sign = diff > 0 ? '+' : ''
  return `${sign}${diff.toFixed(2)}`
}

function generateCompareSummary() {
  if (!compareData.value) return ''
  
  const r1 = compareData.value.report1
  const r2 = compareData.value.report2
  
  const distanceDiff = (r1.stats?.total_distance || 0) - (r2.stats?.total_distance || 0)
  const timeDiff = (r1.stats?.total_time || 0) - (r2.stats?.total_time || 0)
  const tripsDiff = (r1.stats?.total_trips || 0) - (r2.stats?.total_trips || 0)
  
  let summary = []
  
  if (distanceDiff < 0) {
    summary.push(`方案1的总飞行距离更短，节省 ${Math.abs(distanceDiff).toFixed(2)} km`)
  } else if (distanceDiff > 0) {
    summary.push(`方案2的总飞行距离更短，节省 ${Math.abs(distanceDiff).toFixed(2)} km`)
  }
  
  if (timeDiff < 0) {
    summary.push(`方案1的总飞行时间更短，节省 ${Math.abs(timeDiff).toFixed(2)} 分钟`)
  } else if (timeDiff > 0) {
    summary.push(`方案2的总飞行时间更短，节省 ${Math.abs(timeDiff).toFixed(2)} 分钟`)
  }
  
  if (tripsDiff < 0) {
    summary.push(`方案1的总趟次更少，减少 ${Math.abs(tripsDiff)} 趟`)
  } else if (tripsDiff > 0) {
    summary.push(`方案2的总趟次更少，减少 ${Math.abs(tripsDiff)} 趟`)
  }
  
  if (summary.length === 0) {
    return '两个方案在核心指标上表现相同'
  }
  
  return summary.join('；') + '。'
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
              <div class="history-name">{{ item.project_name || item.filename }}</div>
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
    
    <!-- 对比面板 -->
    <RightPanel v-if="showRight && rightType === 'compare'" title="方案对比" @close="closeRight">
      <div v-if="compareData" class="compare-container">
        <div class="compare-header">
          <div class="compare-item">
            <h4>{{ compareData.report1.name }}</h4>
            <p class="compare-scheme">{{ compareData.report1.scheme_type }}</p>
          </div>
          <div class="compare-vs">VS</div>
          <div class="compare-item">
            <h4>{{ compareData.report2.name }}</h4>
            <p class="compare-scheme">{{ compareData.report2.scheme_type }}</p>
          </div>
        </div>
        
        <div class="compare-section">
          <h3>核心指标对比</h3>
          <table class="compare-table">
            <thead>
              <tr>
                <th>指标</th>
                <th>方案1</th>
                <th>方案2</th>
                <th>差值</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>总飞行距离</td>
                <td>{{ compareData.report1.stats?.total_distance || 0 }} km</td>
                <td>{{ compareData.report2.stats?.total_distance || 0 }} km</td>
                <td :class="getDiffClass(compareData.report1.stats?.total_distance, compareData.report2.stats?.total_distance)">
                  {{ formatDiff(compareData.report1.stats?.total_distance, compareData.report2.stats?.total_distance) }}
                </td>
              </tr>
              <tr>
                <td>总飞行时间</td>
                <td>{{ compareData.report1.stats?.total_time || 0 }} 分钟</td>
                <td>{{ compareData.report2.stats?.total_time || 0 }} 分钟</td>
                <td :class="getDiffClass(compareData.report1.stats?.total_time, compareData.report2.stats?.total_time)">
                  {{ formatDiff(compareData.report1.stats?.total_time, compareData.report2.stats?.total_time) }}
                </td>
              </tr>
              <tr>
                <td>总趟次</td>
                <td>{{ compareData.report1.stats?.total_trips || 0 }}</td>
                <td>{{ compareData.report2.stats?.total_trips || 0 }}</td>
                <td :class="getDiffClass(compareData.report1.stats?.total_trips, compareData.report2.stats?.total_trips)">
                  {{ formatDiff(compareData.report1.stats?.total_trips, compareData.report2.stats?.total_trips) }}
                </td>
              </tr>
              <tr>
                <td>无人机数量</td>
                <td>{{ compareData.report1.stats?.drone_count || 0 }}</td>
                <td>{{ compareData.report2.stats?.drone_count || 0 }}</td>
                <td :class="getDiffClass(compareData.report1.stats?.drone_count, compareData.report2.stats?.drone_count)">
                  {{ formatDiff(compareData.report1.stats?.drone_count, compareData.report2.stats?.drone_count) }}
                </td>
              </tr>
              <tr>
                <td>配送村庄数</td>
                <td>{{ compareData.report1.stats?.village_count || 0 }}</td>
                <td>{{ compareData.report2.stats?.village_count || 0 }}</td>
                <td :class="getDiffClass(compareData.report1.stats?.village_count, compareData.report2.stats?.village_count)">
                  {{ formatDiff(compareData.report1.stats?.village_count, compareData.report2.stats?.village_count) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="compare-summary">
          <h3>对比结论</h3>
          <div class="summary-text">
            {{ generateCompareSummary() }}
          </div>
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
  gap: 16px;
  padding: 16px;
}

.module-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  gap: 8px;
}

.config-label {
  font-weight: bold;
  font-size: 14px;
}

.config-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
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
  padding: 8px;
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
  gap: 8px;
}

.history-item {
  padding: 12px;
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
  gap: 8px;
  font-size: 12px;
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
  padding: 40px;
}

/* 报告预览样式 */
.report-preview {
  padding: 20px;
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
  font-size: 12px;
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
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
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
  gap: 12px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.score-name {
  font-weight: bold;
}

.score-value {
  font-weight: bold;
  padding: 4px 12px;
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
  font-size: 12px;
}

.report-table th,
.report-table td {
  border: 1px solid #e0e0e0;
  padding: 8px;
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
  padding: 16px;
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
  padding: 16px;
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
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.editor-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.loading-text,
.empty-text {
  text-align: center;
  color: #999;
  padding: 24px;
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
  gap: 8px;
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
  font-size: 12px;
  padding: 6px 12px;
}

/* 对比样式 */
.compare-container {
  padding: 16px;
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
  font-size: 12px;
  margin: 0;
}

.compare-vs {
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
  padding: 0 16px;
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
  font-size: 12px;
}

.compare-table th,
.compare-table td {
  border: 1px solid #e0e0e0;
  padding: 10px;
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
  gap: 16px;
}

.score-compare-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.compare-summary {
  margin-top: 24px;
  padding: 16px;
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
  font-size: 13px;
}
</style>
