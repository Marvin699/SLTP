<template>
  <!-- 全屏投影模式（智能体评分） -->
  <div v-if="isFullScreen" class="fullscreen-dashboard">
    <div class="fs-header">
      <div class="fs-title">
        <span class="fs-title-main">{{ currentSection?.name || '六维能力画像' }}</span>
        <span class="fs-title-sub">基于时效性、安全性、可靠性、经济性、环境适应性、协同性六个维度的AI综合评估</span>
      </div>
      <div class="fs-controls">
        <el-button type="danger" size="small" @click="isFullScreen = false">退出全屏</el-button>
      </div>
    </div>
    <div class="fs-content" v-if="aiHasData">
      <div class="fs-left">
        <div class="fs-card">
          <div class="fs-card-title">小组能力画像</div>
          <div class="group-btns">
            <el-button v-for="(g, i) in aiData.groups" :key="g.group_id" size="small"
              :type="selectedAIGroup === g.group_id ? 'primary' : ''"
              @click="selectAIGroup(g.group_id)"
              :style="selectedAIGroup === g.group_id ? { background: GROUP_COLORS[i % 6], borderColor: GROUP_COLORS[i % 6] } : {}">
              {{ g.group_id }}
            </el-button>
          </div>
          <div ref="fsRadarRef" class="fs-radar"></div>
        </div>
        <div class="fs-card" v-if="selectedAIGroupData">
          <div class="info-row">
            <div><span class="info-label">综合评分</span><br><span class="info-value">{{ selectedAIGroupData.total_avg }}<span class="info-unit">分</span></span></div>
            <div><span class="info-label">排名</span><br><span class="info-rank">{{ selectedAIGroupData.rank || '-' }}<span class="info-rank-total">/ {{ aiData.groups.length }}</span></span></div>
          </div>
        </div>
      </div>
      <div class="fs-right">
        <div class="fs-card">
          <div class="fs-card-title">小组总成绩对比</div>
          <div ref="fsBarRef" class="fs-bar"></div>
        </div>
        <div class="fs-card">
          <div class="fs-card-title">各维度成绩明细</div>
          <el-table :data="aiData.groups" style="width:100%" size="small">
            <el-table-column prop="group_id" label="小组" width="100" fixed />
            <el-table-column v-for="dim in aiData.dimensions" :key="dim" :label="dim" align="center">
              <template #default="{ row }">{{ row.dimension_scores[dim] || '-' }}</template>
            </el-table-column>
            <el-table-column label="综合分" width="100" fixed="right" align="center">
              <template #default="{ row }"><span class="avg-score">{{ row.total_avg }}</span></template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
    <div v-else class="fs-empty">暂无AI评分数据</div>
  </div>

  <!-- 普通模式 -->
  <div class="detail-page" v-else>
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/evaluation')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 教学智评
        </el-button>
        <el-divider direction="vertical" />
        <h1>{{ currentSection?.name || '环节详情' }}</h1>
      </div>
    </div>

    <!-- 三个功能Tab -->
    <div class="func-tabs">
      <div class="func-tab" :class="{ active: viewMode === 'links' }" @click="viewMode = 'links'">
        <el-icon><Link /></el-icon> 评分链接
      </div>
      <div class="func-tab" :class="{ active: viewMode === 'overview' }" @click="switchToOverview">
        <el-icon><DataAnalysis /></el-icon> 成绩总览
      </div>
      <div class="func-tab" :class="{ active: viewMode === 'ai' }" @click="switchToAI">
        <el-icon><Monitor /></el-icon> 智能体评分
      </div>
    </div>

    <!-- ========== 评分链接Tab ========== -->
    <div class="tab-content" v-show="viewMode === 'links'">
      <div class="content-grid">
        <!-- 左侧：链接管理 -->
        <div class="left-panel">
          <div class="panel-header">
            <h3>评分链接</h3>
            <el-button type="primary" size="small" @click="showCreateDialog">
              <el-icon><Plus /></el-icon> 生成链接
            </el-button>
          </div>
          <div class="section-desc" v-if="currentSection">
            <p>{{ currentSection.description }}</p>
            <div class="dim-tags">
              <el-tag v-for="dim in currentSection.dimensions" :key="dim" size="small" type="info" effect="plain">
                {{ dim }} {{ getWeightPercent(dim) }}%
              </el-tag>
            </div>
          </div>
          <div class="session-list">
            <div v-for="s in sessions" :key="s.id" class="session-card"
              :class="{ active: selectedSession?.token === s.token }" @click="selectSession(s)">
              <div class="session-top">
                <span class="session-title">{{ s.title }}</span>
                <el-tag :type="isSessionValid(s) ? 'success' : 'info'" size="small">
                  {{ isSessionValid(s) ? '进行中' : '已结束' }}
                </el-tag>
              </div>
              <div class="session-link" @click.stop>
                <span class="link-text">{{ getScoreUrl(s.token) }}</span>
                <el-button size="small" type="primary" plain @click="copyLink(s.token)">
                  <el-icon><CopyDocument /></el-icon> 复制
                </el-button>
              </div>
              <div class="session-meta">
                <span v-if="s.start_time">开始: {{ formatTime(s.start_time) }}</span>
                <span v-if="s.end_time">结束: {{ formatTime(s.end_time) }}</span>
              </div>
              <el-button size="small" type="warning" plain @click.stop="handleDelete(s)">
                <el-icon><VideoPause /></el-icon> 停用
              </el-button>
            </div>
            <el-empty v-if="!sessions.length" description="暂无评分链接，点击上方生成" :image-size="80" />
          </div>
        </div>

        <!-- 右侧：单链接汇总 -->
        <div class="right-panel">
          <template v-if="summary">
            <div class="panel-header">
              <h3>{{ summary.title }}</h3>
              <div class="panel-meta">
                打分角色: {{ summary.total_scorers }}个
              </div>
            </div>
            <div class="chart-area">
              <div class="chart-section">
                <h4>小组总成绩对比</h4>
                <div ref="barChartRef" class="chart-box"></div>
              </div>
              <div class="chart-section">
                <h4>小组能力画像</h4>
                <div class="group-btns">
                  <el-button v-for="g in summary.groups" :key="g.group_id" size="small"
                    :type="selectedRadarGroup === g.group_id ? 'primary' : ''"
                    @click="selectedRadarGroup = g.group_id; updateRadar()">
                    {{ g.group_id }}
                  </el-button>
                </div>
                <div ref="radarChartRef" class="chart-box"></div>
              </div>
              <div class="table-section">
                <h4>各维度成绩明细</h4>
                <el-table :data="summary.groups" style="width:100%" size="small">
                  <el-table-column prop="group_id" label="小组" width="100" fixed />
                  <el-table-column v-for="dim in summary.dimensions" :key="dim" :label="dim" align="center">
                    <template #default="{ row }">{{ row.dimension_scores[dim] || '-' }}</template>
                  </el-table-column>
                  <el-table-column label="加权分" width="100" fixed="right" align="center">
                    <template #default="{ row }"><span class="avg-score">{{ row.weighted_avg || row.total_avg }}</span></template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </template>
          <div v-else class="empty-right">
            <el-empty description="请选择左侧链接查看汇总" :image-size="120" />
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 成绩总览Tab ========== -->
    <div class="tab-content" v-show="viewMode === 'overview'">
      <div class="overview-scroll">
        <!-- 工具栏：始终显示 -->
        <div class="overview-toolbar">
          <div class="toolbar-left">
            <el-tag v-if="simulating" type="success" effect="dark" size="small" class="toolbar-tag">
              <span class="tag-dot"></span> 展览中
            </el-tag>
            <el-tag v-else-if="hasRealData" type="primary" effect="plain" size="small" class="toolbar-tag">
              真实打分数据
            </el-tag>
            <el-tag v-else-if="hasExhibitionData" type="warning" effect="plain" size="small" class="toolbar-tag">
              展览数据
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="small" class="toolbar-tag">
              等待打分
            </el-tag>
          </div>
          <div class="toolbar-right">
            <el-button v-if="simulating" type="warning" size="small" plain @click="cancelExhibition">
              <el-icon><VideoPause /></el-icon> 取消展览
            </el-button>
            <el-button v-else type="primary" size="small" plain @click="toggleExhibition">
              <el-icon><VideoPlay /></el-icon> 展览
            </el-button>
            <el-button type="danger" size="small" plain @click="handleClearScores">
              <el-icon><Delete /></el-icon> 清空数据
            </el-button>
          </div>
        </div>
        <!-- 实时打分状态栏（展览中） -->
        <div class="live-bar" v-if="simulating">
          <div class="live-dot"></div>
          <span class="live-text">LIVE 展览中</span>
          <span class="live-count">已收到 <strong>{{ submittedCount }}</strong> / {{ totalScorers }} 份评分</span>
          <div class="live-progress">
            <div class="live-progress-fill" :style="{ width: (submittedCount / totalScorers * 100) + '%' }"></div>
          </div>
        </div>
        <!-- 图表区域：始终显示 -->
        <div class="overview-charts">
          <div class="ov-chart-card">
            <div class="ov-chart-title">小组总分排名</div>
            <div ref="ovRankBarRef" class="ov-chart-box"></div>
          </div>
          <div class="ov-chart-card">
            <div class="ov-chart-title">分维度对比</div>
            <div ref="ovDimBarRef" class="ov-chart-box"></div>
          </div>
        </div>
        <!-- 四宫格：各维度小组得分（始终显示） -->
        <div class="dim-grid-title">各维度小组得分</div>
        <div class="dim-grid">
          <div v-for="(dim, i) in (dashboardData?.dimensions || [])" :key="dim" class="dim-grid-card">
            <div class="dim-grid-card-header">
              <span class="dim-grid-card-name">{{ dim }}</span>
              <span class="dim-grid-card-weight">{{ getWeightPercent(dim) }}%</span>
            </div>
            <div :ref="el => { if (el) dimChartRefs[i] = el }" class="dim-grid-chart"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 智能体评分Tab（原成绩总览） ========== -->
    <div class="tab-content" v-show="viewMode === 'ai'">
      <div class="ai-header">
        <button class="back-graph-btn" @click="goBackToGraph">
          <span>📊</span> 返回图谱
        </button>
      </div>
      <div class="overview-grid" v-if="aiHasData">
        <!-- 左侧 -->
        <div class="ov-left">
          <div class="ov-card">
            <div class="ov-card-title">六维能力画像</div>
            <div class="group-btns">
              <el-button v-for="(g, i) in aiData.groups" :key="g.group_id" size="small"
                :type="selectedAIGroup === g.group_id ? 'primary' : ''"
                @click="selectAIGroup(g.group_id)"
                :style="selectedAIGroup === g.group_id ? { background: GROUP_COLORS[i % 6], borderColor: GROUP_COLORS[i % 6] } : {}">
                {{ g.group_id }}
              </el-button>
            </div>
            <div ref="aiRadarRef" class="chart-box-lg"></div>
          </div>
          <div class="ov-card" v-if="selectedAIGroupData">
            <div class="info-row">
              <div><span class="info-label">综合评分</span><br><span class="info-value">{{ selectedAIGroupData.total_avg }}<span class="info-unit">分</span></span></div>
              <div><span class="info-label">排名</span><br><span class="info-rank">{{ selectedAIGroupData.rank || '-' }}<span class="info-rank-total">/ {{ aiData.groups.length }}</span></span></div>
            </div>
          </div>
          <!-- AI对比分析区域 -->
          <div class="ov-card ai-compare-card">
            <div class="ov-card-title">AI对比分析</div>
            <div class="ai-compare-body">
              <div class="ai-compare-label">选择两组进行对比</div>
              <div class="ai-compare-selects">
                <el-select v-model="compareGroupA" placeholder="选择第一组" size="small" style="width: 130px;">
                  <el-option v-for="g in aiData.groups" :key="g.group_id" :label="g.group_id" :value="g.group_id"
                    :disabled="g.group_id === compareGroupB" />
                </el-select>
                <span class="ai-compare-vs">VS</span>
                <el-select v-model="compareGroupB" placeholder="选择第二组" size="small" style="width: 130px;">
                  <el-option v-for="g in aiData.groups" :key="g.group_id" :label="g.group_id" :value="g.group_id"
                    :disabled="g.group_id === compareGroupA" />
                </el-select>
              </div>
              <el-button type="primary" class="ai-compare-btn" :disabled="!compareGroupA || !compareGroupB" @click="goAIAnalysis">
                <el-icon><DataAnalysis /></el-icon> AI分析
              </el-button>
            </div>
          </div>
        </div>
        <!-- 右侧 -->
        <div class="ov-right">
          <div class="ov-card">
            <div class="ov-card-title">小组总成绩对比</div>
            <div ref="aiBarRef" class="chart-box-lg"></div>
          </div>
          <div class="ov-card">
            <div class="ov-card-title">各维度成绩明细</div>
            <el-table :data="aiData.groups" style="width:100%" size="small">
              <el-table-column prop="group_id" label="小组" width="100" fixed />
              <el-table-column v-for="dim in aiData.dimensions" :key="dim" :label="dim" align="center">
                <template #default="{ row }">{{ row.dimension_scores[dim] || '-' }}</template>
              </el-table-column>
              <el-table-column label="综合分" width="100" fixed="right" align="center">
                <template #default="{ row }"><span class="avg-score">{{ row.total_avg }}</span></template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      <div v-else class="empty-overview">
        <el-empty description="暂无AI评分数据" :image-size="120" />
      </div>
    </div>

    <!-- 创建链接弹窗 -->
    <el-dialog v-model="createDialogVisible" title="生成评分链接" width="420px" destroy-on-close>
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="环节">
          <el-tag type="primary" size="large">{{ currentSection?.short_name }}</el-tag>
        </el-form-item>
        <el-form-item label="链接标题">
          <el-input v-model="createForm.title" :placeholder="currentSection?.name || '评分链接标题'" />
        </el-form-item>
        <el-form-item label="有效时间">
          <el-tag type="warning" size="default">生成后立即生效，30分钟后自动失效</el-tag>
        </el-form-item>
        <el-form-item label="评分维度">
          <div style="display:flex;flex-wrap:wrap;gap:4px;">
            <el-tag v-for="dim in currentSection?.dimensions" :key="dim" size="small">{{ dim }} {{ getWeightPercent(dim) }}%</el-tag>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowLeft, Link, DataAnalysis, Monitor, Delete, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { fetchSections, fetchSessions, createSession, deleteSession, fetchSummary, fetchDashboard, clearSectionScores } from '@/api/scoreSession'

const route = useRoute()
const router = useRouter()
const sectionId = computed(() => route.params.sectionId)

// --- 全局状态 ---
const sections = ref([])
const viewMode = ref(route.query.tab || 'links')
const isFullScreen = ref(false)
const GROUP_COLORS = ['#e74c3c', '#3b82f6', '#2ecc71', '#9b59b6', '#f39c16', '#1abc9c']

// 智能体评分：6维能力画像（AI分析维度，与评分维度独立）
const AI_DIMENSIONS = ['时效性', '安全性', '创新性', '经济性', '环境适应性', '协同性']
const AI_DIM_WEIGHTS = { '时效性': 0.20, '安全性': 0.25, '创新性': 0.20, '经济性': 0.15, '环境适应性': 0.10, '协同性': 0.10 }

// AI评分演示数据（每个环节不同）
// 维度顺序：0=时效性 1=安全性 2=创新性 3=经济性 4=环境适应性 5=协同性
// 注：创新性和经济性在六维画像展示时会自动减10分，展示分均为整数
const AI_DEMO_DATA = {
  section1: [
    { group_id: '揽星组', scores: [95, 96, 88, 83, 95, 85] },   // 展示分: [95,96,78,73,95,85] 均分87 ✓第1
    { group_id: '驭风组', scores: [95, 95, 86, 82, 94, 84] },   // 展示分: [95,95,76,72,94,84] 均分86 ✓第2
    { group_id: '长空组', scores: [88, 90, 87, 84, 88, 87] },   // 展示分: [88,90,77,74,88,87] 均分84
    { group_id: '巡天组', scores: [86, 88, 85, 82, 86, 85] },   // 展示分: [86,88,75,72,86,85] 均分82
    { group_id: '逐日组', scores: [80, 82, 73, 75, 80, 80] },   // 展示分: [80,82,63,65,80,80] 均分75
    { group_id: '凌云组', scores: [75, 78, 66, 68, 76, 77] },   // 展示分: [75,78,56,58,76,77] 均分70
  ],
  section2: [
    { group_id: '逐日组', scores: [80, 88, 82, 85, 90, 86] },
    { group_id: '揽星组', scores: [88, 85, 90, 82, 86, 92] },
    { group_id: '驭风组', scores: [85, 92, 86, 80, 88, 90] },
    { group_id: '长空组', scores: [82, 86, 88, 90, 84, 85] },
    { group_id: '凌云组', scores: [90, 84, 85, 86, 82, 88] },
    { group_id: '巡天组', scores: [86, 90, 84, 88, 85, 82] },
  ],
  section3: [
    { group_id: '逐日组', scores: [82, 90, 86, 80, 88, 85] },
    { group_id: '揽星组', scores: [86, 88, 92, 84, 82, 90] },
    { group_id: '驭风组', scores: [90, 85, 88, 82, 86, 88] },
    { group_id: '长空组', scores: [88, 92, 85, 86, 84, 82] },
    { group_id: '凌云组', scores: [84, 86, 84, 90, 92, 86] },
    { group_id: '巡天组', scores: [92, 84, 86, 88, 80, 90] },
  ],
}

const FALLBACK_SECTIONS = [
  { id: 'section1', name: '环节一：运输方案汇报与知识深化', short_name: '方案汇报', time_range: '0-10min', description: '小组汇报运输方案，教师/企业导师提问，AI词云与风险分析', dimensions: ['方案完整性', '表达展示', '操作规范', '团队配合'], weights: { '方案完整性': 0.35, '表达展示': 0.35, '操作规范': 0.15, '团队配合': 0.15 } },
  { id: 'section2', name: '环节二：无预案应急推演', short_name: '应急推演', time_range: '10-20min', description: '突发应急场景，使用路径规划智能体进行无预案推演', dimensions: ['决策速度', '方案可行性', '风险评估', '团队配合'], weights: { '决策速度': 0.35, '方案可行性': 0.35, '风险评估': 0.15, '团队配合': 0.15 } },
  { id: 'section3', name: '环节三：飞行前准备应急演练比拼', short_name: '应急演练', time_range: '21-36min', description: '限时飞行前检查、双电转单电操作、团队协作应急演练', dimensions: ['安全性', '操作规范性', '用时效率', '团队配合'], weights: { '安全性': 0.35, '操作规范性': 0.35, '用时效率': 0.15, '团队配合': 0.15 } },
]

const currentSection = computed(() => {
  const arr = Array.isArray(sections.value) ? sections.value : []
  return arr.find(s => s.id === sectionId.value)
})

function getWeightPercent(dim) {
  const weights = currentSection.value?.weights || {}
  return weights[dim] ? (weights[dim] * 100).toFixed(0) : 0
}

// --- 评分链接Tab ---
const sessions = ref([])
const selectedSession = ref(null)
const summary = ref(null)
const selectedRadarGroup = ref(null)
const createDialogVisible = ref(false)
const creating = ref(false)
const createForm = ref({ title: '' })
const barChartRef = ref(null)
const radarChartRef = ref(null)
let barChart = null
let radarChart = null

// --- 智能体评分Tab（6维AI能力画像） ---
const aiData = ref(null)
const selectedAIGroup = ref(null)
const aiRadarRef = ref(null)
const aiBarRef = ref(null)
let aiRadar = null
let aiBar = null

// --- AI对比分析 ---
const compareGroupA = ref(null)
const compareGroupB = ref(null)

function goAIAnalysis() {
  if (!compareGroupA.value || !compareGroupB.value) return
  router.push({
    path: `/evaluation/section/${sectionId.value}/ai-analysis`,
    query: { groupA: compareGroupA.value, groupB: compareGroupB.value }
  })
}

// --- 成绩总览Tab（新图表） ---
const dashboardData = ref(null)
const selectedDashGroup = ref(null)
const ovRankBarRef = ref(null)
const ovDimBarRef = ref(null)
let ovRankBar = null
let ovDimBar = null
let ovRadar = null
let ovBar = null
// 四宫格：各维度小组得分
const dimChartRefs = ref([])

// --- 模拟实时打分 ---
const simulating = ref(false)
const submittedCount = ref(0)
const totalScorers = ref(8)
let simTimer = null
let dimCharts = []

// --- 轮询实时刷新 ---
let pollTimer = null

// --- 展览状态（持久化到localStorage） ---
const exhibitionEnabled = ref(localStorage.getItem(`exhibition_${sectionId.value}`) === 'true')

function getExhibitionKey() { return `exhibition_${sectionId.value}` }

function toggleExhibition() {
  exhibitionEnabled.value = true
  localStorage.setItem(getExhibitionKey(), 'true')
  // 进入展览模式：加载演示数据并启动模拟
  loadDashboard().then(() => {
    nextTick().then(() => {
      setTimeout(() => {
        if (dashboardData.value) startSimulation()
      }, 150)
    })
  })
}

function cancelExhibition() {
  stopSimulation()
  exhibitionEnabled.value = false
  localStorage.removeItem(getExhibitionKey())
  // 清空图表
  ovRankBar?.dispose(); ovRankBar = null
  ovDimBar?.dispose(); ovDimBar = null
  dimCharts.forEach(c => c?.dispose()); dimCharts = []
  dashboardData.value = null
}

// 是否有真实打分数据
const hasRealData = computed(() => {
  if (!dashboardData.value) return false
  const groups = Array.isArray(dashboardData.value.groups) ? dashboardData.value.groups : []
  // 真实数据的特征：有 score_count > 0（来自后端dashboard接口的真实打分）
  return groups.length > 0 && groups.some(g => g.score_count > 0)
})

// 是否有展览数据（非真实、非模拟中、但有展示数据）
const hasExhibitionData = computed(() => {
  if (!dashboardData.value) return false
  if (hasRealData.value) return false
  if (simulating.value) return false
  const groups = Array.isArray(dashboardData.value.groups) ? dashboardData.value.groups : []
  return groups.length > 0 && groups.some(g => (g.total_avg || 0) > 0)
})

// --- 全屏模式 ---
const fsRadarRef = ref(null)
const fsBarRef = ref(null)
let fsRadar = null
let fsBar = null

const dashHasData = computed(() => {
  if (!dashboardData.value) return false
  const groups = Array.isArray(dashboardData.value.groups) ? dashboardData.value.groups : []
  return groups.length > 0
})

const selectedGroupData = computed(() => {
  if (!dashboardData.value || !selectedDashGroup.value) return null
  const groups = Array.isArray(dashboardData.value.groups) ? dashboardData.value.groups : []
  return groups.find(g => g.group_id === selectedDashGroup.value)
})

// AI评分数据
const aiHasData = computed(() => {
  if (!aiData.value) return false
  return Array.isArray(aiData.value.groups) && aiData.value.groups.length > 0
})
const selectedAIGroupData = computed(() => {
  if (!aiData.value || !selectedAIGroup.value) return null
  return aiData.value.groups.find(g => g.group_id === selectedAIGroup.value)
})

// --- 演示数据 ---
// 展览模式下，揽星组/驭风组/逐日组分数始终为0，仅长空组/凌云组/巡天组有演示数据
const ZERO_GROUPS = ['逐日组', '揽星组', '驭风组']
function getDemoGroups(dimensions) {
  const demoScores = {
    '逐日组': [92, 88, 85, 90],
    '揽星组': [87, 93, 89, 85],
    '驭风组': [90, 86, 92, 88],
    '长空组': [85, 90, 87, 92],
    '凌云组': [88, 85, 90, 87],
    '巡天组': [91, 89, 88, 90],
  }
  const groups = Object.entries(demoScores).map(([name, scores]) => {
    const isZero = ZERO_GROUPS.includes(name)
    const dimScores = {}
    let total = 0
    dimensions.forEach((dim, j) => {
      const val = isZero ? 0 : (scores[j] || 85)
      dimScores[dim] = val
      total += val
    })
    return { group_id: name, dimension_scores: dimScores, total_avg: isZero ? 0 : Math.round(total / dimensions.length * 100) / 100, weighted_avg: isZero ? 0 : Math.round(total / dimensions.length * 100) / 100, score_count: isZero ? 0 : 5, rank: 0 }
  })
  groups.sort((a, b) => b.total_avg - a.total_avg)
  groups.forEach((g, i) => g.rank = i + 1)
  return groups
}

// --- 数据加载 ---
async function loadSections() {
  try {
    const res = await fetchSections()
    sections.value = Array.isArray(res.data) ? res.data : FALLBACK_SECTIONS
  } catch { sections.value = FALLBACK_SECTIONS }
}

async function loadSessions() {
  try {
    const res = await fetchSessions(sectionId.value)
    const all = Array.isArray(res.data) ? res.data : []
    // 管理列表只显示活跃链接，已停用的不显示
    sessions.value = all.filter(s => s.is_active)
  } catch { sessions.value = [] }
}

const DEFAULT_GROUP_NAMES = ['逐日组', '揽星组', '驭风组', '长空组', '凌云组', '巡天组']

function getEmptyGroups(dimensions) {
  return DEFAULT_GROUP_NAMES.map(name => {
    const dimScores = {}
    dimensions.forEach(dim => { dimScores[dim] = 0 })
    return { group_id: name, dimension_scores: dimScores, total_avg: 0, weighted_avg: 0, score_count: 0, rank: 0 }
  })
}

async function loadDashboard() {
  try {
    const res = await fetchDashboard(sectionId.value)
    dashboardData.value = res.data
    const dims = dashboardData.value?.dimensions || []
    let groups = Array.isArray(dashboardData.value?.groups) ? dashboardData.value.groups : []
    // 无真实数据时填充0分小组，让图表始终有内容
    if (!groups.length && dims.length) {
      groups = getEmptyGroups(dims)
      dashboardData.value.groups = groups
    }
    // 展览模式时替换为演示数据
    if (exhibitionEnabled.value && dims.length) {
      groups = getDemoGroups(dims)
      dashboardData.value.groups = groups
    }
    if (groups.length) {
      selectedDashGroup.value = groups[0].group_id
    }
  } catch { dashboardData.value = null }
}

function switchToOverview() {
  viewMode.value = 'overview'
  stopSimulation()
  nextTick().then(() => {
    setTimeout(() => {
      loadDashboard().then(() => {
        nextTick().then(() => {
          // 始终渲染图表（0分 / 演示数据 / 真实数据）
          if (exhibitionEnabled.value && dashboardData.value?.groups?.length) {
            // 展览模式：启动模拟动画
            startSimulation()
          } else {
            // 静态渲染（0分 或 真实数据）
            renderOverviewCharts()
            startPolling()
          }
        })
      })
    }, 100)
  })
}

// 模拟实时打分
const SIM_ROLES = ['老师', '企业导师', '逐日组观察员', '揽星组观察员', '驭风组观察员', '长空组观察员', '凌云组观察员', '巡天组观察员']
let simData = null
let simBaseScores = null

function startSimulation() {
  if (simulating.value) return
  if (!dashboardData.value?.groups?.length) return

  const groups = dashboardData.value.groups
  const dims = dashboardData.value.dimensions || []
  const totalSteps = SIM_ROLES.length

  // 1. 保存目标分数
  simData = groups.map(g => ({
    group_id: g.group_id,
    target_scores: { ...g.dimension_scores },
    current_scores: Object.fromEntries(dims.map(d => [d, 0])),
  }))

  // 2. 预分配每个评委的贡献分（随机波动，总和 = 目标分）
  simBaseScores = {}
  simData.forEach(g => {
    simBaseScores[g.group_id] = {}
    dims.forEach(d => {
      const target = g.target_scores[d] ?? 80
      const perScorer = target / totalSteps
      const shares = []
      let remaining = target
      for (let i = 0; i < totalSteps; i++) {
        const variance = (Math.random() - 0.5) * perScorer * 0.4
        const share = i === totalSteps - 1 ? remaining : Math.round(Math.max(0, perScorer + variance) * 100) / 100
        shares.push(share)
        remaining -= share
      }
      simBaseScores[g.group_id][d] = shares
    })
  })

  // 3. 立即用0分渲染图表（不显示目标分）
  submittedCount.value = 0
  simulating.value = true
  renderSimCharts()

  // 4. 启动定时器，每1.5秒加一个评委的分数
  let step = 0
  simTimer = setInterval(() => {
    if (step >= totalSteps) { stopSimulation(); return }

    const role = SIM_ROLES[step]
    submittedCount.value = step + 1

    // 累加本轮分数
    simData.forEach(g => {
      dims.forEach(d => {
        g.current_scores[d] = Math.round((g.current_scores[d] + simBaseScores[g.group_id][d][step]) * 100) / 100
      })
    })

    // 只更新图表数据，不重建图表
    renderSimCharts()
    step++

    if (step <= 3 || step === totalSteps) {
      ElMessage({ message: `${role} 已提交评分`, type: 'success', duration: 2000 })
    }
  }, 1500)
}

// 构造当前模拟快照
function getSimSnapshot() {
  const dims = dashboardData.value.dimensions || []
  const weights = dashboardData.value.weights || {}
  return simData.map(g => {
    let wSum = 0, wTotal = 0
    dims.forEach(d => { const w = weights[d] || 0.25; wSum += g.current_scores[d] * w; wTotal += w })
    const weightedAvg = wTotal ? Math.round(wSum / wTotal * 100) / 100 : 0
    const totalAvg = dims.length ? Math.round(dims.reduce((s, d) => s + g.current_scores[d], 0) / dims.length * 100) / 100 : 0
    return { group_id: g.group_id, dimension_scores: { ...g.current_scores }, total_avg: totalAvg, weighted_avg: weightedAvg }
  })
}

// 用模拟数据渲染/更新所有成绩总览图表
function renderSimCharts() {
  if (!simData || !dashboardData.value) return
  const groups = getSimSnapshot()
  const dimensions = dashboardData.value.dimensions || []
  const sorted = [...groups].sort((a, b) => (b.weighted_avg || b.total_avg) - (a.weighted_avg || a.total_avg))

  // --- 排名横向柱状图 ---
  if (!ovRankBar && ovRankBarRef.value) {
    ovRankBar = echarts.init(ovRankBarRef.value)
  }
  if (ovRankBar) {
    const maxVal = 100
    ovRankBar.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c}分' },
      grid: { left: 80, right: 60, top: 10, bottom: 10 },
      xAxis: { type: 'value', max: maxVal, axisLabel: { show: false }, splitLine: { show: false }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: {
        type: 'category',
        data: [...sorted].reverse().map(g => g.group_id),
        axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 13, fontWeight: 500 },
        axisLine: { show: false }, axisTick: { show: false },
      },
      series: [{
        type: 'bar',
        data: [...sorted].reverse().map((g, i) => {
          const isTop = i === sorted.length - 1
          return {
            value: g.weighted_avg || g.total_avg,
            itemStyle: {
              color: isTop
                ? new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#00d4ff' }, { offset: 1, color: '#0099ff' }
                  ])
                : new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: 'rgba(64,158,255,0.25)' }, { offset: 1, color: 'rgba(64,158,255,0.12)' }
                  ]),
              borderRadius: [0, 4, 4, 0],
            },
          }
        }),
        barWidth: '55%',
        label: { show: true, position: 'right', color: '#fff', fontSize: 14, fontWeight: 700 },
      }],
    }, true)
  }

  // --- 分维度对比柱状图 ---
  if (!ovDimBar && ovDimBarRef.value) {
    ovDimBar = echarts.init(ovDimBarRef.value)
  }
  if (ovDimBar) {
    const dimColors = ['#00d4ff', '#36d7b7', '#f7b731', '#e056a0']
    ovDimBar.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: dimensions, textStyle: { color: 'rgba(255,255,255,0.7)', fontSize: 11 }, top: 0, itemWidth: 12, itemHeight: 8 },
      grid: { left: 50, right: 20, top: 40, bottom: 40 },
      xAxis: { type: 'category', data: groups.map(g => g.group_id), axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 11 }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
      series: dimensions.map((dim, di) => ({
        name: dim, type: 'bar',
        data: groups.map(g => g.dimension_scores[dim] || 0),
        itemStyle: { color: dimColors[di % 4], borderRadius: [3, 3, 0, 0], opacity: 0.85 },
        barGap: '8%',
      })),
    }, true)
  }

  // --- 四宫格 ---
  const containers = document.querySelectorAll('.dim-grid-chart')
  dimensions.forEach((dim, i) => {
    const el = containers[i]
    if (!el) return
    if (!dimCharts[i]) {
      dimCharts[i] = echarts.init(el)
    }
    const dimSorted = [...groups].sort((a, b) => (b.dimension_scores[dim] || 0) - (a.dimension_scores[dim] || 0))
    const dimScores = dimSorted.map(g => g.dimension_scores[dim] || 0)
    dimCharts[i].setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}分' },
      grid: { left: 12, right: 12, top: 8, bottom: 8, containLabel: true },
      xAxis: {
        type: 'category',
        data: dimSorted.map(g => g.group_id),
        axisLabel: { color: 'rgba(255,255,255,0.55)', fontSize: 10 },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
        axisTick: { show: false },
      },
      yAxis: { type: 'value', show: false, max: 105 },
      series: [{
        type: 'bar',
        data: dimScores.map((v, j) => ({
          value: v,
          itemStyle: {
            color: j === 0
              ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#00d4ff' }, { offset: 1, color: '#00d4ff22' }
                ])
              : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(64,158,255,0.35)' }, { offset: 1, color: 'rgba(64,158,255,0.08)' }
                ]),
            borderRadius: [3, 3, 0, 0],
          },
        })),
        barWidth: '50%',
        label: { show: true, position: 'top', color: 'rgba(255,255,255,0.75)', fontSize: 10, fontWeight: 600 },
      }],
    }, true)
  })
}

function stopSimulation() {
  if (simTimer) { clearInterval(simTimer); simTimer = null }
  simulating.value = false
  // 模拟结束后恢复轮询（如果有真实数据）
  if (viewMode.value === 'overview') {
    nextTick().then(() => startPolling())
  }
}

// 轮询：每3秒刷新成绩总览数据
function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (simulating.value) return // 模拟中不轮询
    if (viewMode.value !== 'overview') return
    if (exhibitionEnabled.value) return // 展览模式不轮询
    await loadDashboard()
    // 有真实数据时刷新图表
    if (hasRealData.value) {
      await nextTick()
      renderOverviewCharts()
    }
  }, 3000)
}
function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

function loadAIData() {
  const demo = AI_DEMO_DATA[sectionId.value] || AI_DEMO_DATA.section1
  const groups = demo.map((item) => {
    const dimScores = {}
    let total = 0
    AI_DIMENSIONS.forEach((dim, j) => {
      let s = item.scores[j]
      if (dim === '创新性' || dim === '经济性') s = Math.max(0, s - 10)
      dimScores[dim] = s
      total += s
    })
    const avg = Math.round(total / AI_DIMENSIONS.length)
    return { group_id: item.group_id, dimension_scores: dimScores, total_avg: avg, rank: 0 }
  })
  groups.sort((a, b) => b.total_avg - a.total_avg)
  groups.forEach((g, i) => g.rank = i + 1)
  aiData.value = { dimensions: AI_DIMENSIONS, groups }
  if (groups.length) selectedAIGroup.value = groups[0].group_id
  if (groups.length >= 1) compareGroupA.value = groups[0].group_id
  if (groups.length >= 2) compareGroupB.value = groups[1].group_id
}

function switchToAI() {
  viewMode.value = 'ai'
  loadAIData()
  nextTick().then(() => {
    setTimeout(() => renderAICharts(), 150)
  })
}

// --- 评分链接操作 ---
function isSessionValid(s) {
  if (!s.is_active) return false
  const now = new Date()
  if (s.end_time && new Date(s.end_time) < now) return false
  return true
}
function getScoreUrl(token) { return `${window.location.origin}/score/${token}` }
function copyLink(token) {
  const url = getScoreUrl(token)
  // 兼容 HTTP 环境（navigator.clipboard 需要 HTTPS/localhost）
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(url).then(() => ElMessage.success('链接已复制'))
  } else {
    const ta = document.createElement('textarea')
    ta.value = url
    ta.style.cssText = 'position:fixed;left:-9999px;top:-9999px'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ElMessage.success('链接已复制')
  }
}
function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
function showCreateDialog() {
  createForm.value = { title: currentSection.value?.name || '' }
  createDialogVisible.value = true
}
function toLocalISO(d) {
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}
async function handleCreate() {
  creating.value = true
  try {
    const now = new Date()
    const expiry = new Date(now.getTime() + 30 * 60 * 1000)
    await createSession({
      section_id: sectionId.value,
      title: createForm.value.title || currentSection.value?.name,
      start_time: toLocalISO(now),
      end_time: toLocalISO(expiry),
    })
    ElMessage.success('链接生成成功，30分钟后自动失效')
    createDialogVisible.value = false
    loadSessions()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '创建失败') } finally { creating.value = false }
}
async function handleDelete(s) {
  try {
    await ElMessageBox.confirm(`确定停用「${s.title}」？链接将失效，已有打分数据保留不变。`, '停用链接', { type: 'warning', confirmButtonText: '确认停用', cancelButtonText: '取消' })
    await deleteSession(s.id)
    ElMessage.success('链接已停用')
    if (selectedSession.value?.token === s.token) { selectedSession.value = null; summary.value = null }
    loadSessions()
  } catch {}
}
async function handleClearScores() {
  try {
    await ElMessageBox.confirm(
      `确定清空「${currentSection.value?.short_name}」的所有打分数据？\n评分链接将保留不变，打分人可重新提交。`,
      '清空打分数据',
      { type: 'warning', confirmButtonText: '确认清空', cancelButtonText: '取消' }
    )
    await clearSectionScores(sectionId.value)
    // 停止模拟
    stopSimulation()
    exhibitionEnabled.value = false
    localStorage.removeItem(getExhibitionKey())
    // 清空图表实例，重新加载dashboard（后端返回空数据 → 填充0分小组）
    ovRankBar?.dispose(); ovRankBar = null
    ovDimBar?.dispose(); ovDimBar = null
    dimCharts.forEach(c => c?.dispose()); dimCharts = []
    await loadDashboard()
    await nextTick()
    setTimeout(() => {
      renderOverviewCharts()
      startPolling()
    }, 100)
    ElMessage.success('打分数据已清空，图表已归零')
    selectedSession.value = null
    summary.value = null
    loadSessions()
  } catch {}
}
async function selectSession(s) {
  selectedSession.value = s
  try {
    const res = await fetchSummary(s.token)
    summary.value = res.data
    if (summary.value.groups?.length) {
      selectedRadarGroup.value = summary.value.groups[0].group_id
      await nextTick(); renderSessionBar(); renderSessionRadar()
    }
  } catch { summary.value = null }
}

// --- 图表渲染 ---
function getRadarOption(dims, group) {
  return {
    backgroundColor: 'transparent',
    radar: { indicator: dims.map(d => ({ name: d, max: 100 })), radius: '65%', axisName: { color: 'rgba(255,255,255,0.7)', fontSize: 12 }, splitArea: { areaStyle: { color: ['transparent'] } }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
    series: [{ type: 'radar', data: [{ value: dims.map(d => group.dimension_scores[d] || 0), name: group.group_id, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { color: 'rgba(64,158,255,0.2)' }, itemStyle: { color: '#409eff' }, label: { show: true, color: '#fff', fontSize: 11 } }] }]
  }
}

// 评分链接Tab图表
function renderSessionBar() {
  if (!barChartRef.value || !summary.value) return
  if (barChart) barChart.dispose()
  barChart = echarts.init(barChartRef.value)
  const groups = Array.isArray(summary.value.groups) ? summary.value.groups : []
  barChart.setOption({
    backgroundColor: 'transparent', tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: groups.map(g => g.group_id), axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 11 }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: 'rgba(255,255,255,0.5)' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
    series: [{ type: 'bar', data: groups.map((g, i) => ({ value: g.weighted_avg || g.total_avg, itemStyle: { color: GROUP_COLORS[i % 6], borderRadius: [4, 4, 0, 0] } })), barWidth: '40%', label: { show: true, position: 'top', color: '#fff', fontSize: 12, formatter: '{c}' } }]
  })
}
function renderSessionRadar() {
  if (!radarChartRef.value || !summary.value) return
  if (radarChart) radarChart.dispose()
  radarChart = echarts.init(radarChartRef.value)
  updateRadar()
}
function updateRadar() {
  if (!radarChart || !summary.value || !selectedRadarGroup.value) return
  const dims = summary.value.dimensions
  const groups = Array.isArray(summary.value.groups) ? summary.value.groups : []
  const group = groups.find(g => g.group_id === selectedRadarGroup.value)
  if (!group) return
  radarChart.setOption(getRadarOption(dims, group))
}

// --- 成绩总览Tab图表（新设计） ---
function selectDashGroup(gid) {
  selectedDashGroup.value = gid
}

function renderOverviewCharts() {
  if (!dashboardData.value) return
  const groups = Array.isArray(dashboardData.value.groups) ? dashboardData.value.groups : []
  if (!groups.length) return
  const dimensions = dashboardData.value.dimensions || []

  // 左图：小组总分排名（横向柱状图，第一名高亮）
  if (ovRankBar) ovRankBar.dispose()
  const rankRef = ovRankBarRef.value
  if (rankRef) {
    ovRankBar = echarts.init(rankRef)
    const sorted = [...groups].sort((a, b) => (b.weighted_avg || b.total_avg) - (a.weighted_avg || a.total_avg))
    const maxVal = Math.max(100, Math.ceil(Math.max(...sorted.map(g => g.weighted_avg || g.total_avg)) / 5) * 5)
    ovRankBar.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c}分' },
      grid: { left: 80, right: 60, top: 10, bottom: 10 },
      xAxis: { type: 'value', max: maxVal, axisLabel: { show: false }, splitLine: { show: false }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: {
        type: 'category',
        data: [...sorted].reverse().map(g => g.group_id),
        axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 13, fontWeight: 500 },
        axisLine: { show: false }, axisTick: { show: false },
      },
      series: [{
        type: 'bar',
        data: [...sorted].reverse().map((g, i) => {
          const isTop = i === sorted.length - 1
          return {
            value: g.weighted_avg || g.total_avg,
            itemStyle: {
              color: isTop
                ? new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#00d4ff' }, { offset: 1, color: '#0099ff' }
                  ])
                : new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: 'rgba(64,158,255,0.25)' }, { offset: 1, color: 'rgba(64,158,255,0.12)' }
                  ]),
              borderRadius: [0, 4, 4, 0],
            },
          }
        }),
        barWidth: '55%',
        label: {
          show: true, position: 'right', fontSize: 14, fontWeight: 700,
          formatter: (p) => {
            const isTop = p.dataIndex === sorted.length - 1
            return `{val|${p.value}}`
          },
          rich: { val: { color: '#fff', fontSize: 14, fontWeight: 700 } },
        },
      }],
    })
  }

  // 右图：分维度对比（分组柱状图）
  if (ovDimBar) ovDimBar.dispose()
  const dimRef = ovDimBarRef.value
  if (dimRef) {
    ovDimBar = echarts.init(dimRef)
    const dimColors = ['#00d4ff', '#36d7b7', '#f7b731', '#e056a0']
    const dimSeries = dimensions.map((dim, di) => ({
      name: dim,
      type: 'bar',
      data: groups.map(g => g.dimension_scores[dim] || 0),
      itemStyle: { color: dimColors[di % 4], borderRadius: [3, 3, 0, 0], opacity: 0.85 },
      barGap: '8%',
    }))
    ovDimBar.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: dimensions, textStyle: { color: 'rgba(255,255,255,0.7)', fontSize: 11 }, top: 0, itemWidth: 12, itemHeight: 8 },
      grid: { left: 50, right: 20, top: 40, bottom: 40 },
      xAxis: { type: 'category', data: groups.map(g => g.group_id), axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 11 }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
      series: dimSeries,
    })
  }

  // 四宫格：各维度小组得分（小雷达图）
  renderDimGrid()
}

function renderDimGrid() {
  if (!dashboardData.value) return
  const groups = Array.isArray(dashboardData.value.groups) ? dashboardData.value.groups : []
  const dimensions = dashboardData.value.dimensions || []
  if (!groups.length || !dimensions.length) return

  nextTick(() => {
    const containers = document.querySelectorAll('.dim-grid-chart')

    dimensions.forEach((dim, i) => {
      const el = containers[i]
      if (!el) return

      // 复用已有图表实例
      if (!dimCharts[i]) {
        dimCharts[i] = echarts.init(el)
      }

      const sorted = [...groups].sort((a, b) => (b.dimension_scores[dim] || 0) - (a.dimension_scores[dim] || 0))
      const dimScores = sorted.map(g => g.dimension_scores[dim] || 0)

      dimCharts[i].setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', formatter: '{b}: {c}分' },
        grid: { left: 12, right: 12, top: 8, bottom: 8, containLabel: true },
        xAxis: {
          type: 'category',
          data: sorted.map(g => g.group_id),
          axisLabel: { color: 'rgba(255,255,255,0.55)', fontSize: 10 },
          axisLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
          axisTick: { show: false },
        },
        yAxis: { type: 'value', show: false, max: 105 },
        series: [{
          type: 'bar',
          data: dimScores.map((v, j) => ({
            value: v,
            itemStyle: {
              color: j === 0
                ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#00d4ff' }, { offset: 1, color: '#00d4ff22' }
                  ])
                : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(64,158,255,0.35)' }, { offset: 1, color: 'rgba(64,158,255,0.08)' }
                  ]),
              borderRadius: [3, 3, 0, 0],
            },
          })),
          barWidth: '50%',
          label: { show: true, position: 'top', color: 'rgba(255,255,255,0.75)', fontSize: 10, fontWeight: 600 },
        }],
      }, true)
    })
  })
}

// 切换tab时停止模拟
watch(viewMode, (val) => {
  if (val !== 'overview') { stopSimulation(); stopPolling() }
})

// --- 智能体评分Tab图表（6维AI能力画像） ---
function selectAIGroup(gid) {
  selectedAIGroup.value = gid
  updateAIRadar()
}

function renderAICharts() {
  if (!aiData.value) return
  const groups = aiData.value.groups || []
  if (!groups.length) return

  // 柱状图
  if (aiBar) aiBar.dispose()
  const bRef = aiBarRef.value
  if (bRef) {
    aiBar = echarts.init(bRef)
    aiBar.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 30, top: 20, bottom: 40 },
      xAxis: { type: 'category', data: groups.map(g => g.group_id), axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 12 }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
      yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: 'rgba(255,255,255,0.5)' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      series: [{ type: 'bar', data: groups.map((g, i) => ({ value: g.total_avg, itemStyle: { color: GROUP_COLORS[i % 6], borderRadius: [6, 6, 0, 0] } })), barWidth: '35%', label: { show: true, position: 'top', color: '#fff', fontSize: 13, fontWeight: 600, formatter: '{c}' } }]
    })
  }

  // 雷达图
  updateAIRadar()
}

function updateAIRadar() {
  if (!aiRadar) {
    const rRef = aiRadarRef.value
    if (!rRef || !aiData.value) return
    aiRadar = echarts.init(rRef)
  }
  if (!aiData.value || !selectedAIGroup.value) return
  const dims = aiData.value.dimensions
  const group = aiData.value.groups.find(g => g.group_id === selectedAIGroup.value)
  if (!group) return
  aiRadar.setOption(getRadarOption(dims, group))
}

// --- 全屏图表（使用AI数据） ---
function renderFsCharts() {
  if (!aiData.value) return
  const groups = aiData.value.groups || []
  if (!groups.length) return

  if (fsBar) fsBar.dispose()
  const bRef = fsBarRef.value
  if (bRef) {
    fsBar = echarts.init(bRef)
    fsBar.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 30, top: 20, bottom: 40 },
      xAxis: { type: 'category', data: groups.map(g => g.group_id), axisLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 12 }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
      yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: 'rgba(255,255,255,0.5)' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
      series: [{ type: 'bar', data: groups.map((g, i) => ({ value: g.total_avg, itemStyle: { color: GROUP_COLORS[i % 6], borderRadius: [6, 6, 0, 0] } })), barWidth: '35%', label: { show: true, position: 'top', color: '#fff', fontSize: 13, fontWeight: 600, formatter: '{c}' } }]
    })
  }

  if (fsRadar) fsRadar.dispose()
  const rRef = fsRadarRef.value
  if (rRef) {
    fsRadar = echarts.init(rRef)
    if (selectedAIGroup.value) {
      const dims = aiData.value.dimensions
      const group = groups.find(g => g.group_id === selectedAIGroup.value)
      if (group) fsRadar.setOption(getRadarOption(dims, group))
    }
  }
}

// 全屏模式切换时渲染图表
watch(isFullScreen, async (val) => {
  if (val) {
    if (!aiData.value) loadAIData()
    await nextTick()
    setTimeout(() => renderFsCharts(), 150)
  }
})

function handleResize() {
  barChart?.resize(); radarChart?.resize()
  ovRadar?.resize(); ovBar?.resize()
  ovRankBar?.resize(); ovDimBar?.resize()
  dimCharts.forEach(c => c?.resize())
  aiRadar?.resize(); aiBar?.resize()
  fsRadar?.resize(); fsBar?.resize()
}

function goBackToGraph() {
  router.push('/agent/teaching-graph/view')
}

onMounted(async () => {
  await loadSections()
  await loadSessions()
  if (viewMode.value === 'overview') {
    await loadDashboard()
    await nextTick()
    setTimeout(() => {
      if (exhibitionEnabled.value && dashboardData.value?.groups?.length) {
        startSimulation()
      } else {
        renderOverviewCharts()
        startPolling()
      }
    }, 100)
  } else if (viewMode.value === 'ai') {
    loadAIData()
    await nextTick()
    setTimeout(() => renderAICharts(), 150)
  }
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  stopSimulation()
  stopPolling()
  barChart?.dispose(); radarChart?.dispose()
  ovRadar?.dispose(); ovBar?.dispose()
  ovRankBar?.dispose(); ovDimBar?.dispose()
  dimCharts.forEach(c => c?.dispose())
  aiRadar?.dispose(); aiBar?.dispose()
  fsRadar?.dispose(); fsBar?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* === 通用 === */
.detail-page { padding: 20px; color: #fff; height: calc(100vh - 100px); display: flex; flex-direction: column; }
.page-header { margin-bottom: 12px; }
.header-left { display: flex; align-items: center; gap: 4px; }
.back-btn { color: #c0c8d4 !important; font-size: 14px; }
.back-btn:hover { color: #409eff !important; }
.page-header h1 { margin: 0; font-size: 20px; }

/* 功能Tab */
.func-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.func-tab {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 20px; border-radius: 8px; font-size: 14px; font-weight: 500;
  background: rgba(13,33,55,0.6); border: 1px solid rgba(255,255,255,0.08);
  cursor: pointer; transition: all 0.2s;
}
.func-tab:hover { border-color: rgba(64,158,255,0.3); }
.func-tab.active { border-color: #409eff; background: rgba(64,158,255,0.12); color: #409eff; }

/* 评分链接布局 */
.content-grid { flex: 1; display: grid; grid-template-columns: 340px 1fr; gap: 16px; overflow: hidden; }
.left-panel, .right-panel {
  background: rgba(13,33,55,0.8); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; display: flex; flex-direction: column; overflow: hidden;
}
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.panel-header h3 { margin: 0; font-size: 15px; }
.section-desc { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.section-desc p { margin: 0 0 8px; font-size: 12px; color: #c0c8d4; line-height: 1.6; }
.dim-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.session-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.session-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s; }
.session-card:hover { border-color: rgba(64,158,255,0.3); }
.session-card.active { border-color: #409eff; background: rgba(64,158,255,0.08); }
.session-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.session-title { font-weight: 600; font-size: 14px; }
.session-link { display: flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.2); border-radius: 4px; padding: 4px 8px; margin-bottom: 6px; }
.link-text { font-size: 11px; color: #c0c8d4; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.session-meta { font-size: 11px; color: #718096; display: flex; gap: 12px; margin-bottom: 6px; }
.chart-area { flex: 1; overflow-y: auto; padding: 16px; }
.chart-section { margin-bottom: 20px; }
.chart-section h4 { margin: 0 0 10px; font-size: 14px; color: #e2e8f0; }
.chart-box { height: 220px; }
.table-section h4 { margin: 0 0 10px; font-size: 14px; color: #e2e8f0; }
.avg-score { color: #409eff; font-weight: 700; font-size: 14px; }
.empty-right { flex: 1; display: flex; align-items: center; justify-content: center; }

/* Tab内容区 */
.tab-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* AI评分Tab头部 */
.ai-header {
  display: flex; justify-content: flex-start; align-items: center;
  padding: 8px 0 16px;
}
.back-graph-btn {
  display: flex; align-items: center; gap: 6px;
  background: rgba(64,158,255,0.15); border: 1px solid rgba(64,158,255,0.3);
  color: #409eff; border-radius: 8px; padding: 8px 16px; cursor: pointer;
  font-size: 14px; transition: all 0.2s;
}
.back-graph-btn:hover { background: rgba(64,158,255,0.25); color: #fff; }

/* 成绩总览工具栏 */
.overview-toolbar {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 10px 16px; margin-bottom: 16px;
  background: rgba(13,33,55,0.6); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
}
.toolbar-left { display: flex; align-items: center; gap: 8px; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }
.toolbar-tag { border-radius: 16px; }
.tag-dot {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: #67c23a; margin-right: 4px;
  animation: tagPulse 1.2s ease-in-out infinite;
}
@keyframes tagPulse {
  0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
}

/* 实时打分状态栏 */
.live-bar {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 20px; margin-bottom: 16px;
  background: rgba(0,212,255,0.06); border: 1px solid rgba(0,212,255,0.15);
  border-radius: 10px;
}
.live-dot {
  width: 10px; height: 10px; border-radius: 50%; background: #00ff88;
  box-shadow: 0 0 8px #00ff88;
  animation: livePulse 1.2s ease-in-out infinite;
}
@keyframes livePulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}
.live-text { font-size: 13px; color: #00ff88; font-weight: 600; letter-spacing: 1px; }
.live-count { font-size: 13px; color: rgba(255,255,255,0.6); margin-left: auto; }
.live-count strong { color: #00d4ff; font-size: 16px; }
.live-progress {
  width: 120px; height: 4px; background: rgba(255,255,255,0.08);
  border-radius: 2px; overflow: hidden;
}
.live-progress-fill {
  height: 100%; background: linear-gradient(90deg, #00d4ff, #00ff88);
  border-radius: 2px; transition: width 0.5s ease;
}

/* 成绩总览Tab */
.overview-scroll { flex: 1; overflow-y: auto; padding-right: 4px; }
.overview-charts {
  display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; margin-bottom: 28px;
}
.ov-chart-card {
  background: linear-gradient(135deg, rgba(0,212,255,0.04) 0%, rgba(13,33,55,0.9) 100%);
  border: 1px solid rgba(0,212,255,0.12);
  border-radius: 12px; padding: 24px; display: flex; flex-direction: column;
  box-shadow: 0 0 20px rgba(0,212,255,0.03);
}
.ov-chart-title {
  font-size: 15px; font-weight: 600; margin-bottom: 16px;
  padding-left: 12px; border-left: 3px solid #00d4ff; color: #e2e8f0;
  letter-spacing: 1px;
}
.ov-chart-box { flex: 1; min-height: 360px; }

/* 四宫格：各维度小组得分 */
.dim-grid-title {
  font-size: 15px; font-weight: 600; margin-bottom: 16px;
  padding-left: 12px; border-left: 3px solid #00d4ff; color: #e2e8f0;
  letter-spacing: 1px;
}
.dim-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
.dim-grid-card {
  background: linear-gradient(135deg, rgba(0,212,255,0.03) 0%, rgba(13,33,55,0.9) 100%);
  border: 1px solid rgba(0,212,255,0.1); border-radius: 10px; padding: 16px;
  transition: border-color 0.3s, box-shadow 0.3s;
}
.dim-grid-card:hover {
  border-color: rgba(0,212,255,0.25);
  box-shadow: 0 0 16px rgba(0,212,255,0.06);
}
.dim-grid-card-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px;
}
.dim-grid-card-name { font-size: 13px; font-weight: 600; color: #e2e8f0; letter-spacing: 0.5px; }
.dim-grid-card-weight { font-size: 11px; color: #00d4ff; font-weight: 600; }
.dim-grid-chart { height: 180px; }

/* 智能体评分布局 */
.overview-grid { flex: 1; display: grid; grid-template-columns: 1fr 1.2fr; gap: 16px; overflow: hidden; }
.ov-left, .ov-right { display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.ov-card { background: rgba(13,33,55,0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 20px; }
.ov-card-title { font-size: 15px; font-weight: 600; margin-bottom: 14px; padding-left: 10px; border-left: 3px solid #409eff; }
.chart-box-lg { height: 300px; }

/* 小组按钮 */
.group-btns { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }

/* 信息卡片 */
.info-row { display: flex; gap: 40px; margin-bottom: 4px; }
.info-label { font-size: 13px; color: #718096; }
.info-value { font-size: 32px; font-weight: 700; color: #409eff; }
.info-unit { font-size: 14px; font-weight: 400; color: #c0c8d4; margin-left: 2px; }
.info-rank { font-size: 32px; font-weight: 700; color: #fff; }
.info-rank-total { font-size: 16px; font-weight: 400; color: #718096; }

/* AI对比分析 */
.ai-compare-card { margin-top: 14px; }
.ai-compare-body { display: flex; flex-direction: column; gap: 12px; align-items: center; }
.ai-compare-label { font-size: 13px; color: #718096; text-align: center; }
.ai-compare-selects { display: flex; align-items: center; gap: 10px; }
.ai-compare-vs { font-size: 13px; font-weight: 700; color: #409eff; }
.ai-compare-btn { width: 100%; }

/* === 全屏投影模式 === */
.fullscreen-dashboard {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999;
  background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
  color: #fff; display: flex; flex-direction: column; padding: 24px 32px;
}
.fs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-shrink: 0; }
.fs-title-main { font-size: 24px; font-weight: 700; }
.fs-title-sub { display: block; font-size: 13px; color: #718096; margin-top: 4px; }
.fs-content { flex: 1; display: grid; grid-template-columns: 1fr 1.3fr; gap: 20px; overflow: hidden; }
.fs-left, .fs-right { display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.fs-card { background: rgba(13,33,55,0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; }
.fs-card-title { font-size: 16px; font-weight: 600; margin-bottom: 14px; padding-left: 10px; border-left: 3px solid #409eff; }
.fs-radar { height: 320px; }
.fs-bar { height: 260px; }
.fs-empty { display: flex; align-items: center; justify-content: center; flex: 1; font-size: 18px; color: #718096; }

/* === 表格 === */
:deep(.el-table) { background: transparent; color: #e2e8f0; }
:deep(.el-table th) { background: rgba(255,255,255,0.06) !important; color: #c0c8d4; }
:deep(.el-table td) { border-bottom-color: rgba(255,255,255,0.06); }
:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) { background: rgba(255,255,255,0.04) !important; }
:deep(.el-dialog) { background: #1a2332; }
:deep(.el-dialog__header) { border-bottom: 1px solid rgba(255,255,255,0.1); }
:deep(.el-dialog__title) { color: #fff; }
:deep(.el-form-item__label) { color: #c0c8d4; }

/* 清空数据按钮（danger plain） */
:deep(.el-button--danger.is-plain) {
  --el-button-bg-color: rgba(245,108,108,0.08);
  --el-button-border-color: rgba(245,108,108,0.25);
  --el-button-text-color: #f56c6c;
  --el-button-hover-bg-color: rgba(245,108,108,0.15);
  --el-button-hover-border-color: rgba(245,108,108,0.4);
  --el-button-hover-text-color: #ff8585;
}
/* 展览取消按钮（warning plain） */
:deep(.el-button--warning.is-plain) {
  --el-button-bg-color: rgba(245,158,11,0.08);
  --el-button-border-color: rgba(245,158,11,0.25);
  --el-button-text-color: #f59c0b;
  --el-button-hover-bg-color: rgba(245,158,11,0.15);
  --el-button-hover-border-color: rgba(245,158,11,0.4);
  --el-button-hover-text-color: #f7b731;
}
/* primary plain按钮 */
:deep(.el-button--primary.is-plain) {
  --el-button-bg-color: rgba(64,158,255,0.08);
  --el-button-border-color: rgba(64,158,255,0.25);
  --el-button-text-color: #409eff;
  --el-button-hover-bg-color: rgba(64,158,255,0.15);
  --el-button-hover-border-color: rgba(64,158,255,0.4);
  --el-button-hover-text-color: #66b1ff;
}
</style>
