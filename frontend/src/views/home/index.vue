<template>
  <div class="home-page">
    <!-- 全屏背景 -->
    <div class="page-bg">
      <img src="@/assets/images/banner.png" alt="" class="bg-img" />
      <div class="bg-overlay"></div>
    </div>

    <div class="home-content">
      <!-- 极简标题 -->
      <header class="home-hero fade-up">
        <h1>{{ welcomeText }}</h1>
        <p>AI 赋能教育 · 智慧决策未来</p>
      </header>

        <!-- 三个智能体卡片 -->
        <div class="agents-section">
          <!-- 智能体1：路径规划 -->
          <div class="agent-card agent-blue" @click="goToAgent('/agent/path-planning')">
            <div class="card-content">
              <div class="card-left">
                <h3 class="agent-title">应急调度</h3>
                <p class="agent-subtitle">智能规划最优运输路线</p>
              </div>
              <div class="card-right">
                <div class="illustration">
                  <svg viewBox="0 0 200 160" class="agent-illustration">
                    <defs>
                      <linearGradient id="pathGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#22d3ee;stop-opacity:0.8"/>
                        <stop offset="50%" style="stop-color:#409eff;stop-opacity:0.6"/>
                        <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:0.8"/>
                      </linearGradient>
                      <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>
                    <ellipse cx="100" cy="140" rx="60" ry="8" fill="rgba(64,158,255,0.15)"/>
                    <path d="M30 120 Q70 100, 100 110 T170 70" stroke="url(#pathGlow)" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#glow)"/>
                    <path d="M30 125 Q70 105, 100 115 T170 75" stroke="#409eff" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.5"/>
                    <circle cx="30" cy="120" r="8" fill="#409eff" filter="url(#glow)">
                      
                    </circle>
                    <circle cx="30" cy="120" r="14" fill="none" stroke="#409eff" stroke-width="1" opacity="0.3"/>
                    <circle cx="100" cy="110" r="6" fill="#22d3ee" filter="url(#glow)"/>
                    <circle cx="170" cy="70" r="8" fill="#f56c6c" filter="url(#glow)">
                      
                    </circle>
                    <circle cx="170" cy="70" r="14" fill="none" stroke="#f56c6c" stroke-width="1" opacity="0.3"/>
                    <g transform="translate(125, 35)">
                      <ellipse cx="22" cy="8" rx="18" ry="6" fill="rgba(64,158,255,0.2)" stroke="#409eff" stroke-width="1.5"/>
                      <rect x="3" y="2" width="38" height="12" rx="4" fill="linear-gradient(135deg, #409eff 0%, #22d3ee 100%)"/>
                      <rect x="0" y="4" width="10" height="3" rx="1.5" fill="#22d3ee" opacity="0.8"/>
                      <rect x="30" y="4" width="10" height="3" rx="1.5" fill="#22d3ee" opacity="0.8"/>
                      <circle cx="22" cy="8" r="4" fill="#fff">
                        
                      </circle>
                      <rect x="15" y="-5" width="3" height="8" rx="1" fill="#409eff"/>
                      <rect x="24" y="-5" width="3" height="8" rx="1" fill="#409eff"/>
                    </g>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- 智能体2：装箱评价 -->
          <div class="agent-card agent-purple" @click="goToAgent('/agent/packing')">
            <div class="card-content">
              <div class="card-left">
                <h3 class="agent-title">装箱评价</h3>
                <p class="agent-subtitle">智能装载评估与优化</p>
              </div>
              <div class="card-right">
                <div class="illustration">
                  <svg viewBox="0 0 200 160" class="agent-illustration">
                    <defs>
                      <linearGradient id="boxGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#0e7490;stop-opacity:0.4"/>
                        <stop offset="100%" style="stop-color:#155e75;stop-opacity:0.2"/>
                      </linearGradient>
                      <linearGradient id="boxGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#22d3ee;stop-opacity:0.4"/>
                        <stop offset="100%" style="stop-color:#155e75;stop-opacity:0.2"/>
                      </linearGradient>
                      <filter id="purpleGlow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>
                    <rect x="55" y="70" width="55" height="55" rx="6" fill="url(#boxGrad1)" stroke="#0e7490" stroke-width="1.5" filter="url(#purpleGlow)"/>
                    <polygon points="55,70 82.5,52 110,70" fill="rgba(14,116,144,0.3)" stroke="#0e7490" stroke-width="1.5"/>
                    <rect x="65" y="60" width="55" height="55" rx="6" fill="url(#boxGrad2)" stroke="#22d3ee" stroke-width="1.5" filter="url(#purpleGlow)">
                      
                      
                    </rect>
                    <polygon points="65,60 92.5,42 120,60" fill="rgba(34,211,238,0.3)" stroke="#22d3ee" stroke-width="1.5"/>
                    <rect x="75" y="50" width="55" height="55" rx="6" fill="rgba(103,232,249,0.4)" stroke="#67e8f9" stroke-width="1.5" filter="url(#purpleGlow)">
                      
                      
                    </rect>
                    <polygon points="75,50 102.5,32 130,50" fill="rgba(103,232,249,0.3)" stroke="#67e8f9" stroke-width="1.5"/>
                    <line x1="102" y1="50" x2="102" y2="100" stroke="#0e7490" stroke-width="0.5" opacity="0.4" stroke-dasharray="3,2"/>
                    <line x1="75" y1="75" x2="130" y2="75" stroke="#0e7490" stroke-width="0.5" opacity="0.4" stroke-dasharray="3,2"/>
                    <rect x="45" y="130" width="110" height="18" rx="4" fill="rgba(14,116,144,0.15)" stroke="#0e7490" stroke-width="1.5"/>
                    <rect x="145" y="35" width="22" height="22" rx="4" fill="rgba(14,116,144,0.3)" stroke="#0e7490" stroke-width="1.5"/>
                    <circle cx="156" cy="46" r="3" fill="#fff" opacity="0.8"/>
                    <rect x="25" y="85" width="20" height="20" rx="4" fill="rgba(14,116,144,0.25)" stroke="#0e7490" stroke-width="1.5"/>
                    <circle cx="35" cy="95" r="3" fill="#fff" opacity="0.8"/>
                    <circle cx="102" cy="140" r="4" fill="#0e7490" opacity="0.6">
                      
                    </circle>
                    <circle cx="85" cy="140" r="3" fill="#0e7490" opacity="0.4">
                      
                    </circle>
                    <circle cx="120" cy="140" r="3" fill="#0e7490" opacity="0.4">
                      
                    </circle>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- 智能体3：课程教学图谱 -->
          <div class="agent-card agent-green" @click="goToAgent('/agent/teaching-graph')">
            <div class="card-content">
              <div class="card-left">
                <h3 class="agent-title">课程图谱</h3>
            <p class="agent-subtitle">知识图谱与能力分析</p>
              </div>
              <div class="card-right">
                <div class="illustration">
                  <svg viewBox="0 0 200 160" class="agent-illustration">
                    <defs>
                      <linearGradient id="graphGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#22d3ee;stop-opacity:0.8"/>
                        <stop offset="100%" style="stop-color:#0ea5e9;stop-opacity:0.6"/>
                      </linearGradient>
                      <filter id="greenGlow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>
                    <circle cx="100" cy="50" r="16" fill="url(#graphGrad)" stroke="#22d3ee" stroke-width="2" filter="url(#greenGlow)">
                      
                    </circle>
                    <circle cx="100" cy="50" r="8" fill="#fff">
                      <animate attributeName="opacity" values="1;0.8;1" dur="1.5s" repeatCount="indefinite"/>
                    </circle>
                    <text x="100" y="54" text-anchor="middle" fill="#22d3ee" font-size="10" font-weight="bold">核心</text>
                    <circle cx="60" cy="90" r="14" fill="rgba(34,211,238,0.35)" stroke="#22d3ee" stroke-width="1.5" filter="url(#greenGlow)">
                      
                    </circle>
                    <circle cx="60" cy="90" r="6" fill="#fff"/>
                    <text x="60" y="108" text-anchor="middle" fill="#22d3ee" font-size="9" font-weight="500">知识</text>
                    <circle cx="100" cy="115" r="14" fill="rgba(34,211,238,0.35)" stroke="#22d3ee" stroke-width="1.5" filter="url(#greenGlow)">
                      
                    </circle>
                    <circle cx="100" cy="115" r="6" fill="#fff"/>
                    <text x="100" y="133" text-anchor="middle" fill="#22d3ee" font-size="9" font-weight="500">能力</text>
                    <circle cx="140" cy="90" r="14" fill="rgba(34,211,238,0.35)" stroke="#22d3ee" stroke-width="1.5" filter="url(#greenGlow)">
                      
                    </circle>
                    <circle cx="140" cy="90" r="6" fill="#fff"/>
                    <text x="140" y="108" text-anchor="middle" fill="#22d3ee" font-size="9" font-weight="500">思政</text>
                    <circle cx="50" cy="140" r="10" fill="rgba(34,211,238,0.25)" stroke="#22d3ee" stroke-width="1"/>
                    <circle cx="100" cy="150" r="10" fill="rgba(34,211,238,0.25)" stroke="#22d3ee" stroke-width="1"/>
                    <circle cx="150" cy="140" r="10" fill="rgba(34,211,238,0.25)" stroke="#22d3ee" stroke-width="1"/>
                    <circle cx="155" cy="55" r="10" fill="rgba(34,211,238,0.25)" stroke="#22d3ee" stroke-width="1"/>
                    <circle cx="45" cy="55" r="10" fill="rgba(34,211,238,0.25)" stroke="#22d3ee" stroke-width="1"/>
                    <line x1="100" y1="66" x2="60" y2="76" stroke="#22d3ee" stroke-width="2" filter="url(#greenGlow)"/>
                    <line x1="100" y1="66" x2="100" y2="101" stroke="#22d3ee" stroke-width="2" filter="url(#greenGlow)"/>
                    <line x1="100" y1="66" x2="140" y2="76" stroke="#22d3ee" stroke-width="2" filter="url(#greenGlow)"/>
                    <line x1="60" y1="104" x2="50" y2="130" stroke="#22d3ee" stroke-width="1.5" opacity="0.5"/>
                    <line x1="100" y1="129" x2="100" y2="140" stroke="#22d3ee" stroke-width="1.5" opacity="0.5"/>
                    <line x1="140" y1="104" x2="150" y2="130" stroke="#22d3ee" stroke-width="1.5" opacity="0.5"/>
                    <line x1="100" y1="66" x2="155" y2="45" stroke="#22d3ee" stroke-width="1.5" opacity="0.5"/>
                    <line x1="100" y1="66" x2="45" y2="45" stroke="#22d3ee" stroke-width="1.5" opacity="0.5"/>
                    <circle cx="35" cy="80" r="4" fill="#22d3ee" opacity="0.6">
                      
                    </circle>
                    <circle cx="165" cy="80" r="4" fill="#22d3ee" opacity="0.6">
                      
                    </circle>
                  </svg>
                </div>
              </div>
            </div>
          </div>
      </div>

      <!-- 数据总览：统一大框（可展开） -->
      <div class="console-wrap fade-up">
        <button class="console-toggle" @click="toggleConsole">
          <span>{{ consoleOpen ? '收起数据总览' : '数据总览' }}</span>
          <svg class="chev" :class="{ open: consoleOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>

        <div v-show="consoleOpen" class="console-panel glass-card">
          <div class="console-grid">
            <!-- 概览列 -->
            <div class="console-col">
              <div class="panel-title">{{ userStore.role === 'teacher' ? '平台概览' : '我的学习' }}</div>
              <div class="mini-stats">
                <div v-for="stat in visibleStats" :key="stat.key" class="mini-stat">
                  <el-icon :size="15" class="mini-stat-icon" :class="stat.key"><component :is="stat.icon" /></el-icon>
                  <div class="mini-stat-info">
                    <span class="mini-stat-value">{{ stat.value }}</span>
                    <span class="mini-stat-label">{{ stat.label }}</span>
                  </div>
                </div>
              </div>
              <div class="panel-title">平台状态</div>
              <div class="status-list">
                <div v-for="status in systemStatus" :key="status.key" class="status-item">
                  <span class="status-dot" :class="status.status"></span>
                  <span class="status-text">{{ status.label }}</span>
                  <span class="status-value" :class="status.status">{{ status.value }}</span>
                </div>
              </div>
            </div>

            <!-- 学习统计 -->
            <div class="console-col mid">
              <div class="chart-header">
                <span>学习数据统计</span>
                <el-radio-group v-model="statsTab" size="small">
                  <el-radio-button label="7天">近7天</el-radio-button>
                  <el-radio-button label="30天">近30天</el-radio-button>
                  <el-radio-button label="学年">学年统计</el-radio-button>
                </el-radio-group>
              </div>
              <div ref="learningChartRef" class="chart-container"></div>
            </div>

            <!-- 雷达 + 资源 -->
            <div class="console-col">
              <div class="chart-header"><span>能力维度分析</span></div>
              <div ref="radarChartRef" class="chart-container radar-box"></div>
              <div class="chart-header"><span>资源使用TOP5</span></div>
              <div class="resource-list">
                <div v-for="(resource, index) in resourceTop5" :key="index" class="resource-item">
                  <span class="resource-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                  <span class="resource-name">{{ resource.name }}</span>
                  <span class="resource-count">{{ resource.count }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="console-row2">
            <div class="console-col">
              <div class="panel-title">通知公告</div>
              <div class="notice-list">
                <div v-for="notice in notices" :key="notice.id" class="notice-item">
                  <div class="notice-dot"></div>
                  <div class="notice-content">
                    <div class="notice-title">{{ notice.title }}</div>
                    <div class="notice-date">{{ notice.date }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="console-col">
              <div class="panel-title">实训任务动态</div>
              <div class="task-list">
                <div v-for="task in trainingTasks" :key="task.id" class="task-item">
                  <div class="task-info">
                    <div class="task-title">{{ task.title }}</div>
                    <div class="task-progress">
                      <el-progress
                        :percentage="task.progress"
                        :stroke-width="6"
                        :show-text="false"
                        :color="task.progress === 100 ? '#67c23a' : '#409eff'"
                      />
                    </div>
                  </div>
                  <el-tag :type="task.status === '进行中' ? 'primary' : 'success'" size="small">
                    {{ task.status }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { Document, List, User, TrendCharts } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

// 数据总览大框（默认收起保持极简）
const consoleOpen = ref(false)
let chartsInited = false
function toggleConsole() {
  consoleOpen.value = !consoleOpen.value
  if (consoleOpen.value && !chartsInited) {
    nextTick(() => {
      initCharts()
      chartsInited = true
    })
  }
}

// 当前用户欢迎语
const welcomeText = computed(() => {
  if (userStore.role === 'teacher') {
    return `${userStore.username}老师，欢迎回到教学平台`
  }
  return `${userStore.username}同学，欢迎开始今天的学习`
})

// 平台统计数据 - 教师看班级数据，学生看个人数据
const platformStats = ref([
  { key: 'courses', icon: 'Document', value: '12', label: '课程总数', change: '+2' },
  { key: 'training', icon: 'List', value: '36', label: '实训任务', change: '+5' },
  { key: 'students', icon: 'User', value: '0', label: '学生总数', change: '+0' },
  { key: 'score', icon: 'TrendCharts', value: '0%', label: '平均成绩', change: '+0%' }
])

// 学生端：个人数据
const studentStats = ref([
  { key: 'courses', icon: 'Document', value: '8', label: '我的课程', change: '进行中' },
  { key: 'training', icon: 'List', value: '5', label: '我的任务', change: '待提交' },
  { key: 'students', icon: 'User', value: '0', label: '已完成实训', change: '本月' },
  { key: 'score', icon: 'TrendCharts', value: '—', label: '我的成绩', change: '待评' }
])

const visibleStats = computed(() => {
  return userStore.role === 'teacher' ? platformStats.value : studentStats.value
})

// 系统状态
const systemStatus = ref([
  { key: 'run', label: '系统运行', value: '正常', status: 'online' },
  { key: 'ai', label: 'AI服务', value: '在线', status: 'online' },
  { key: 'sync', label: '数据同步', value: '正常', status: 'online' }
])

// 加载教师端学生统计
async function loadTeacherStats() {
  if (userStore.role !== 'teacher') return
  try {
    const res = await axios.get('/api/auth/stats', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    if (res.data.success) {
      const s = res.data.stats
      platformStats.value[2].value = String(s.total_students)
      platformStats.value[2].change = `今日+${s.today_new}`
    }
  } catch (err) {
    console.warn('加载教师统计失败:', err)
  }
}

// 通知公告
const notices = ref([
  { id: 1, title: '关于开展低空应急运输实训课程的通知', date: '2026-08-29' },
  { id: 2, title: '平台系统升级维护公告', date: '2026-08-26' },
  { id: 3, title: '新增课程资源上线通知', date: '2026-08-22' },
  { id: 4, title: '关于开展无人机航线规划培训的通知', date: '2026-08-18' }
])

// 实训任务动态
const trainingTasks = ref([
  { id: 1, title: '山地应急物资运输', progress: 75, status: '进行中' },
  { id: 2, title: '城市短途物流配送', progress: 60, status: '进行中' },
  { id: 3, title: '跨区域物资转运', progress: 45, status: '进行中' },
  { id: 4, title: '复杂地形航线规划', progress: 100, status: '已完成' }
])

// 资源使用TOP5
const resourceTop5 = ref([
  { name: '低空运输案例库', count: 1286 },
  { name: '无人机航线规划', count: 962 },
  { name: '应急运输方案库', count: 876 },
  { name: '航线设计工具', count: 745 },
  { name: '风险评估工具', count: 642 }
])

const statsTab = ref('7天')

// 图表引用
const learningChartRef = ref(null)
const radarChartRef = ref(null)

// 跳转到智能体页面
const goToAgent = (path) => {
  router.push(path)
}

// 初始化图表（大框展开后调用；隐藏容器尺寸为0时 echarts 无法渲染）
function initCharts() {
  // 学习数据统计折线图
  const learningChart = echarts.init(learningChartRef.value)
  learningChart.setOption({
    backgroundColor: 'transparent',
    grid: {
      top: 10,
      right: 10,
      bottom: 24,
      left: 36
    },
    xAxis: {
      type: 'category',
      data: ['05-28', '05-29', '05-30', '05-31', '06-01', '06-02', '06-03'],
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [
      {
        data: [120, 200, 150, 80, 70, 110, 130],
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#67c23a' }
          ]),
          width: 2
        },
        itemStyle: { color: '#409eff', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64,158,255,0.25)' },
            { offset: 1, color: 'rgba(64,158,255,0.02)' }
          ])
        },
        animationDuration: 1500,
        animationEasing: 'cubicOut'
      }
    ]
  })

  // 能力维度雷达图
  const radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '航线规划', max: 100 },
        { name: '风险评估', max: 100 },
        { name: '空间优化', max: 100 },
        { name: '决策分析', max: 100 },
        { name: '系统操作', max: 100 }
      ],
      radius: '65%',
      axisName: { color: 'rgba(255,255,255,0.6)', fontSize: 10 },
      splitArea: { areaStyle: { color: ['transparent'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [80, 70, 85, 75, 90],
            name: '学生平均能力',
            lineStyle: {
              color: '#409eff',
              width: 2,
              shadowColor: 'rgba(64,158,255,0.5)',
              shadowBlur: 10
            },
            areaStyle: {
              color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                { offset: 0, color: 'rgba(64,158,255,0.4)' },
                { offset: 1, color: 'rgba(64,158,255,0.05)' }
              ])
            },
            itemStyle: { color: '#409eff', borderColor: '#fff', borderWidth: 1 }
          }
        ],
        animationDuration: 1500
      }
    ]
  })

  // 窗口大小改变时重绘图表
  window.addEventListener('resize', () => {
    learningChart.resize()
    radarChart.resize()
  })
}

onMounted(() => {
  // 加载教师统计（教师端）
  loadTeacherStats()
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.2vw, 20px);
}

.top-section {
  display: grid;
  grid-template-columns: clamp(180px, 15vw, 280px) 1fr clamp(200px, 18vw, 340px);
  gap: clamp(10px, 1.2vw, 20px);
}

/* 左侧面板 */
.left-panel {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  padding: clamp(14px, 1.5vw, 24px);
  border: 1px solid var(--glass-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.panel-title {
  font-size: clamp(13px, 1vw, 16px);
  font-weight: 700;
  margin-bottom: clamp(10px, 1vw, 16px);
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.08em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #22d3ee, rgba(34, 211, 238, 0.2));
  box-shadow: 0 0 8px rgba(34, 211, 238, 0.5);
}

.stats-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: clamp(10px, 1vw, 14px);
  padding: clamp(10px, 1vw, 14px);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(64, 158, 255, 0.12);
  border-color: rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.stat-icon {
  width: clamp(36px, 3vw, 44px);
  height: clamp(36px, 3vw, 44px);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.courses { background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0.1) 100%); color: #409eff; }
.stat-icon.training { background: linear-gradient(135deg, rgba(103, 194, 58, 0.2) 0%, rgba(103, 194, 58, 0.1) 100%); color: #67c23a; }
.stat-icon.students { background: linear-gradient(135deg, rgba(230, 162, 60, 0.2) 0%, rgba(230, 162, 60, 0.1) 100%); color: #e6a23c; }
.stat-icon.score { background: linear-gradient(135deg, rgba(245, 108, 108, 0.2) 0%, rgba(245, 108, 108, 0.1) 100%); color: #f56c6c; }

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: clamp(22px, 1.8vw, 30px);
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.65);
  margin-top: 6px;
}

.stat-change {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.55);
}

.stat-change .up {
  color: #67c23a;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #f56c6c;
}

.status-dot.online {
  background: #67c23a;
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.8);
}

.status-text {
  flex: 1;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
}

.status-value {
  font-size: 13px;
  font-weight: 600;
}

.status-value.online {
  color: #67c23a;
}

/* 中间主区域 */
.center-panel {
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.2vw, 16px);
}

/* ===== 顶部Banner ===== */
.hero-banner {
  position: relative;
  width: 100%;
  height: clamp(260px, 24vw, 420px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.banner-bg {
  position: absolute;
  inset: 0;
}

.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(5, 10, 20, 0.82) 0%, rgba(5, 10, 20, 0.45) 55%, rgba(5, 10, 20, 0.7) 100%);
}

.banner-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 20px;
}

/* 悬浮指标胶囊：接真实统计数据 */
.banner-metrics {
  display: flex;
  gap: 10px;
  margin-top: clamp(10px, 1.2vw, 18px);
  flex-wrap: wrap;
  justify-content: center;
}

.metric-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(5, 10, 20, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-value {
  font-size: 15px;
  font-weight: 700;
  color: #22d3ee;
  font-variant-numeric: tabular-nums;
}

.metric-label {
  font-size: 12px;
  color: rgba(242, 246, 250, 0.65);
  letter-spacing: 0.05em;
}

.ai-chip .metric-label {
  color: rgba(242, 246, 250, 0.8);
}

/* 主视觉行动按钮 */
.banner-actions {
  display: flex;
  gap: 14px;
  margin-top: clamp(12px, 1.4vw, 22px);
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 26px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.06em;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.cta-btn.primary {
  color: #04121c;
  background: linear-gradient(135deg, #22d3ee, #0ea5e9);
  border: none;
}

.cta-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(34, 211, 238, 0.3);
}

.cta-btn.ghost {
  color: rgba(242, 246, 250, 0.85);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.cta-btn.ghost:hover {
  color: #fff;
  border-color: rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.08);
}

.cta-btn .arrow-icon {
  width: 16px;
  height: 16px;
}

.banner-title {
  font-size: clamp(26px, 2.5vw, 44px);
  font-weight: 800;
  color: #fff;
  margin-bottom: clamp(10px, 1vw, 18px);
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
  letter-spacing: 2px;
}

/* ============ 驾驶舱 HUD ============ */
.command-hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.command-hero .hero-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 10px;
  padding-left: 19px;
}

.command-hero .mission-id {
  color: rgba(255, 255, 255, 0.38);
}

/* 顶部指标条 */
.metric-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr) auto;
  gap: 12px;
  margin-bottom: clamp(14px, 1.4vw, 22px);
}

.metric-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 18px;
  border-radius: 6px;
  background: linear-gradient(160deg, rgba(34, 211, 238, 0.07), rgba(34, 211, 238, 0.015) 60%, transparent);
  border: 1px solid rgba(34, 211, 238, 0.12);
  overflow: hidden;
}

.metric-tile::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #22d3ee, rgba(34, 211, 238, 0.1));
}

.metric-tile-value {
  font-size: clamp(22px, 1.8vw, 32px);
  line-height: 1.1;
  color: #fff;
}

.metric-tile-label {
  font-size: 11px;
  letter-spacing: 0.14em;
  color: rgba(242, 246, 250, 0.5);
}

.ai-tile {
  flex-direction: row;
  align-items: center;
  gap: 10px;
  border-color: rgba(74, 222, 128, 0.18);
  background: linear-gradient(160deg, rgba(74, 222, 128, 0.06), transparent);
}

.ai-tile::after {
  background: linear-gradient(180deg, #4ade80, rgba(74, 222, 128, 0.1));
}

.ai-tile .ai-label {
  color: rgba(134, 239, 172, 0.75);
}

/* 主视觉 HUD 层 */
.banner-hud.hud-top {
  position: absolute;
  top: 12px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  z-index: 4;
}

.banner-hud-label {
  display: block;
  margin-bottom: 10px;
  text-align: center;
  opacity: 0.85;
}

.banner-content .hud-label {
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.6);
}

/* 雷达圈：右上角半嵌入 */
.radar-zone {
  position: absolute;
  right: -60px;
  top: -60px;
  width: 220px;
  height: 220px;
  z-index: 1;
  opacity: 0.9;
}

.radar-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(34, 211, 238, 0.22);
  box-shadow: inset 0 0 40px rgba(34, 211, 238, 0.06);
}

.radar-ring::before {
  content: '';
  position: absolute;
  inset: 22%;
  border-radius: 50%;
  border: 1px dashed rgba(34, 211, 238, 0.18);
}

.radar-ring::after {
  content: '';
  position: absolute;
  inset: 44%;
  border-radius: 50%;
  border: 1px solid rgba(34, 211, 238, 0.25);
  background: rgba(34, 211, 238, 0.08);
}

/* 主视觉内指标胶囊复用仪表数字 */
.metric-value.hud-num {
  font-size: 16px;
}

.banner-subtitle {
  font-size: clamp(14px, 1.1vw, 18px);
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 1px;
}

/* ===== 智能体卡片区域 ===== */
.agents-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(10px, 1.2vw, 16px);
  max-width: 960px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

/* 智能体卡片错峰入场 */
.agents-section .agent-card {
  animation: fadeUp 0.5s ease both;
}
.agents-section .agent-card:nth-child(2) { animation-delay: 0.08s; }
.agents-section .agent-card:nth-child(3) { animation-delay: 0.16s; }

.agent-card {
  border-radius: 20px;
  padding: clamp(12px, 1vw, 16px);
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  min-height: clamp(96px, 6.5vw, 118px);
}

.agent-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.agent-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.agent-card:hover::before {
  opacity: 1;
}

/* 透明毛玻璃：透出天空背景，白字加投影保证可读 */
.agent-blue,
.agent-purple,
.agent-green {
  background: rgba(8, 15, 28, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(16px) saturate(1.1);
  -webkit-backdrop-filter: blur(16px) saturate(1.1);
}

.agent-blue::before,
.agent-purple::before,
.agent-green::before {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.05) 0%, rgba(5, 10, 20, 0.9) 100%);
}

.agent-blue:hover,
.agent-purple:hover,
.agent-green:hover {
  border-color: rgba(34, 211, 238, 0.35);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

/* 卡片内容布局 */
.card-content {
  display: flex;
  height: 100%;
  position: relative;
  z-index: 2;
}

.card-left {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-right {
  width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 标题样式 */
.agent-title {
  font-size: clamp(16px, 1.4vw, 22px);
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.agent-subtitle {
  font-size: clamp(13px, 1vw, 15px);
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: clamp(14px, 1.2vw, 20px);
}

/* 功能列表 */
.feature-list {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
  flex: 1;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: clamp(13px, 1vw, 15px);
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: clamp(8px, 0.8vw, 12px);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 功能点统一主色：全站唯一强调色 */
.dot.blue, .dot.purple, .dot.green, .dot.cyan {
  background: #22d3ee;
  box-shadow: 0 0 6px rgba(34, 211, 238, 0.45);
}

/* hover 引导：插画放大泛光 + 标题变青 + 底部滑入光条（静态是常态，动效只在交互时） */
.agent-illustration {
  display: block;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), filter 0.4s ease;
}

.agent-card:hover .agent-illustration {
  transform: scale(1.07) translateY(-3px);
  filter: drop-shadow(0 0 14px rgba(34, 211, 238, 0.4));
}

.agent-title {
  transition: color 0.3s ease;
}

.agent-card:hover .agent-title {
  color: #22d3ee;
}

.agent-card::after {
  content: '';
  position: absolute;
  left: 18%;
  right: 18%;
  bottom: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #22d3ee, transparent);
  opacity: 0;
  transform: scaleX(0.4);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-card:hover::after {
  opacity: 1;
  transform: scaleX(1);
}

.arrow-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s;
}

.enter-btn:hover .arrow-icon {
  transform: translateX(4px);
}

/* 插图 */
.illustration {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.agent-illustration {
  width: clamp(72px, 6vw, 108px);
  height: clamp(72px, 6vw, 108px);
}

/* 右侧面板 */
.right-panel {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  padding: clamp(14px, 1.5vw, 24px);
  border: 1px solid var(--glass-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.panel-section {
  margin-bottom: 20px;
}

.panel-section:last-child {
  margin-bottom: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notice-item {
  display: flex;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.notice-item:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
}

.notice-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  margin-top: 6px;
  flex-shrink: 0;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.6);
}

.notice-content {
  flex: 1;
  min-width: 0;
}

.notice-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.88);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.notice-date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.task-item:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.88);
  margin-bottom: 8px;
}

.task-progress {
  width: 100%;
}

/* 底部统计区 */
.bottom-section {
  display: grid;
  grid-template-columns: clamp(300px, 30vw, 500px) 1fr clamp(200px, 22vw, 350px);
  gap: clamp(10px, 1.2vw, 16px);
}

.chart-card {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  padding: clamp(14px, 1.5vw, 24px);
  border: 1px solid var(--glass-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.chart-header {
  font-size: clamp(13px, 1vw, 16px);
  font-weight: 700;
  margin-bottom: clamp(10px, 1vw, 16px);
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.08em;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header > span:first-child {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-header > span:first-child::before {
  content: '';
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #22d3ee, rgba(34, 211, 238, 0.2));
  box-shadow: 0 0 8px rgba(34, 211, 238, 0.5);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: clamp(8px, 0.8vw, 12px);
  margin-bottom: clamp(10px, 1vw, 14px);
}

.stats-item {
  text-align: center;
  padding: clamp(10px, 1vw, 14px) clamp(8px, 0.8vw, 10px);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stats-value {
  font-size: clamp(20px, 1.6vw, 28px);
  font-weight: 800;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stats-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 6px;
}

.chart-container {
  height: clamp(120px, 10vw, 180px);
}

/* ============ 简约大气版式：全屏背景 + 智能体主角 + 统一数据大框 ============ */
.home-page {
  position: relative;
  min-height: calc(100vh - 60px);
  padding: 0 clamp(16px, 3vw, 48px) 28px;
}

.page-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.page-bg .bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.page-bg .bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(5, 10, 20, 0.55) 0%, rgba(5, 10, 20, 0.25) 42%, rgba(5, 10, 20, 0.78) 100%);
}

.home-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 60px);
  max-width: 1280px;
  margin: 0 auto;
}

/* 极简标题 */
.home-hero {
  text-align: center;
  margin: clamp(40px, 9vh, 96px) 0 clamp(28px, 4vh, 56px);
}

.home-hero h1 {
  font-size: clamp(28px, 3.2vw, 48px);
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #fff;
  text-shadow: 0 4px 24px rgba(0, 0, 0, 0.55);
}

.home-hero p {
  margin-top: 12px;
  font-size: clamp(13px, 1vw, 16px);
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.78);
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

/* 智能体为页面唯一主角，撑开后把数据框推到底部 */
.agents-section {
  margin-top: auto;
}

/* 统一数据大框 */
.console-wrap {
  margin-top: clamp(28px, 5vh, 56px);
}

.console-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
  padding: 10px 30px;
  border-radius: 999px;
  background: rgba(5, 10, 20, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 14px;
  letter-spacing: 0.1em;
  cursor: pointer;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.25s ease;
}

.console-toggle:hover {
  border-color: rgba(34, 211, 238, 0.55);
  background: rgba(5, 10, 20, 0.68);
}

.console-toggle .chev {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.console-toggle .chev.open {
  transform: rotate(180deg);
}

.console-panel {
  margin-top: 14px;
  border-radius: 16px;
  padding: clamp(16px, 1.6vw, 26px);
  background: rgba(8, 15, 28, 0.74);
  animation: consoleIn 0.35s ease;
}

@keyframes consoleIn {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}

.console-grid {
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  gap: clamp(14px, 1.6vw, 26px);
}

.console-row2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(14px, 1.6vw, 26px);
  margin-top: clamp(14px, 1.6vw, 24px);
  padding-top: clamp(14px, 1.6vw, 20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.mini-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 14px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  transition: all 0.25s ease;
}

.mini-stat:hover {
  background: rgba(34, 211, 238, 0.07);
  border-color: rgba(34, 211, 238, 0.25);
  transform: translateY(-1px);
}

.mini-stat-icon.courses { color: #409eff; }
.mini-stat-icon.training { color: #67c23a; }
.mini-stat-icon.students { color: #e6a23c; }
.mini-stat-icon.score { color: #f56c6c; }

.mini-stat-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mini-stat-value {
  font-family: var(--font-display);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-size: 18px;
  color: #fff;
  line-height: 1.1;
  letter-spacing: 0.03em;
}

/* 数据大框内的数字统一仪表读数风格 */
.console-panel .status-value,
.console-panel .resource-count,
.console-panel .notice-date {
  font-family: var(--font-display);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.05em;
}

.console-panel .notice-date {
  color: rgba(255, 255, 255, 0.45);
}

.mini-stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.console-panel .chart-container {
  height: 220px;
}

.console-panel .radar-box {
  height: 180px;
}

@media (max-width: 1024px) {
  .console-grid,
  .console-row2 {
    grid-template-columns: 1fr;
  }
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.resource-item:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
}

.resource-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.resource-rank.rank-1 { background: linear-gradient(135deg, #f56c6c, #e64242); }
.resource-rank.rank-2 { background: linear-gradient(135deg, #e6a23c, #d48806); }
.resource-rank.rank-3 { background: linear-gradient(135deg, #409eff, #2080f0); }
.resource-rank.rank-4,
.resource-rank.rank-5 { background: rgba(255, 255, 255, 0.15); }

.resource-name {
  flex: 1;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
}

.resource-count {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
  font-weight: 600;
}

/* ===== 大屏适配（≥1920px）===== */
@media (min-width: 1920px) {
  .top-section {
    gap: 32px;
  }

  .bottom-section {
    gap: 24px;
  }

  .agent-card {
    min-height: 320px;
    padding: 28px;
  }

  .stat-card {
    padding: 18px;
  }

  .chart-card {
    padding: 28px;
  }

  .stats-grid {
    gap: 16px;
  }

  .agents-section {
    gap: 24px;
  }
}

/* ===== 小屏适配 ===== */
@media (max-width: 1024px) {
  .top-section {
    grid-template-columns: 1fr;
  }

  .agents-section {
    grid-template-columns: 1fr;
  }

  .bottom-section {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .card-right {
    display: none;
  }
}

@media (max-width: 768px) {
  .banner-title {
    font-size: 18px;
    letter-spacing: 1px;
  }

  .banner-subtitle {
    font-size: 11px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>