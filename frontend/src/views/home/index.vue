<template>
  <div class="home-page">
    <!-- 顶部内容区 -->
    <div class="top-section">
      <!-- 左侧平台概览 -->
      <aside class="left-panel">
        <div class="panel-title">平台概览</div>
        <div class="stats-cards">
          <div v-for="stat in platformStats" :key="stat.key" class="stat-card">
            <div class="stat-icon" :class="stat.key">
              <el-icon :size="18"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-change">较上月 <span class="up">{{ stat.change }}</span></div>
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
      </aside>

      <!-- 中间主区域 -->
      <main class="center-panel">
        <!-- Banner区域 -->
        <div class="hero-banner">
          <div class="banner-bg">
            <img src="@/assets/images/banner.png" alt="banner" class="banner-img" />
            <div class="banner-overlay"></div>
          </div>
          <div class="banner-content">
            <h1 class="banner-title">AI赋能教育 · 智慧决策未来</h1>
            <p class="banner-subtitle">融合人工智能与低空运输技术，构建沉浸式教学新体验</p>
          </div>
        </div>

        <!-- 三个智能体卡片 -->
        <div class="agents-section">
          <!-- 智能体1：路径规划 -->
          <div class="agent-card agent-blue" @click="goToAgent('/agent/path-planning')">
            <div class="card-content">
              <div class="card-left">
                <h3 class="agent-title">路径规划智能体</h3>
                <p class="agent-subtitle">智能规划最优运输路线</p>
                <ul class="feature-list">
                  <li><span class="dot blue"></span>多目标路径优化</li>
                  <li><span class="dot blue"></span>地形避障分析</li>
                  <li><span class="dot blue"></span>航线风险评估</li>
                </ul>
                <button class="enter-btn">
                  <span>进入模块</span>
                  <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
              <div class="card-right">
                <div class="illustration">
                  <svg viewBox="0 0 200 160" class="agent-illustration">
                    <rect x="20" y="80" width="160" height="70" rx="8" fill="rgba(64,158,255,0.15)" stroke="rgba(64,158,255,0.3)" stroke-width="1"/>
                    <path d="M40 115 L80 95 L120 105 L160 85" stroke="#409eff" stroke-width="2" fill="none" stroke-linecap="round"/>
                    <path d="M40 115 L80 95 L120 105 L160 85" stroke="#409eff" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.3"/>
                    <circle cx="40" cy="115" r="6" fill="#409eff"/>
                    <circle cx="40" cy="115" r="10" fill="none" stroke="#409eff" stroke-width="1" opacity="0.5"/>
                    <circle cx="80" cy="95" r="5" fill="#67c23a"/>
                    <circle cx="120" cy="105" r="5" fill="#67c23a"/>
                    <circle cx="160" cy="85" r="6" fill="#f56c6c"/>
                    <circle cx="160" cy="85" r="10" fill="none" stroke="#f56c6c" stroke-width="1" opacity="0.5"/>
                    <g transform="translate(130, 45)">
                      <ellipse cx="20" cy="5" rx="15" ry="4" fill="#1a3a5c"/>
                      <rect x="5" y="0" width="30" height="10" rx="3" fill="#409eff"/>
                      <rect x="0" y="2" width="8" height="2" rx="1" fill="#67c23a"/>
                      <rect x="32" y="2" width="8" height="2" rx="1" fill="#67c23a"/>
                      <circle cx="20" cy="5" r="3" fill="#fff"/>
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
                <h3 class="agent-title">装箱评价智能体</h3>
                <p class="agent-subtitle">智能装载评估与优化</p>
                <ul class="feature-list">
                  <li><span class="dot purple"></span>装载空间优化</li>
                  <li><span class="dot purple"></span>重量平衡分析</li>
                  <li><span class="dot purple"></span>安全风险评估</li>
                </ul>
                <button class="enter-btn">
                  <span>进入模块</span>
                  <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
              <div class="card-right">
                <div class="illustration">
                  <svg viewBox="0 0 200 160" class="agent-illustration">
                    <rect x="60" y="60" width="50" height="50" rx="4" fill="rgba(156,39,176,0.2)" stroke="#9c27b0" stroke-width="1.5"/>
                    <rect x="70" y="50" width="50" height="50" rx="4" fill="rgba(156,39,176,0.3)" stroke="#9c27b0" stroke-width="1.5"/>
                    <rect x="80" y="40" width="50" height="50" rx="4" fill="rgba(156,39,176,0.4)" stroke="#9c27b0" stroke-width="1.5"/>
                    <line x1="105" y1="50" x2="105" y2="90" stroke="#9c27b0" stroke-width="0.5" opacity="0.5"/>
                    <line x1="80" y1="70" x2="130" y2="70" stroke="#9c27b0" stroke-width="0.5" opacity="0.5"/>
                    <rect x="50" y="110" width="100" height="15" rx="3" fill="rgba(156,39,176,0.15)" stroke="#9c27b0" stroke-width="1"/>
                    <rect x="140" y="30" width="20" height="20" rx="3" fill="rgba(156,39,176,0.3)" stroke="#9c27b0" stroke-width="1"/>
                    <rect x="30" y="80" width="18" height="18" rx="3" fill="rgba(156,39,176,0.25)" stroke="#9c27b0" stroke-width="1"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- 智能体3：课程教学图谱 -->
          <div class="agent-card agent-green" @click="goToAgent('/agent/teaching-graph')">
            <div class="card-content">
              <div class="card-left">
                <h3 class="agent-title">课程图谱智能体</h3>
            <p class="agent-subtitle">知识图谱与能力分析</p>
                <ul class="feature-list">
                  <li><span class="dot green"></span>知识图谱可视化</li>
                  <li><span class="dot green"></span>能力模型分析</li>
                  <li><span class="dot green"></span>思政元素映射</li>
                </ul>
                <button class="enter-btn">
                  <span>进入模块</span>
                  <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
              <div class="card-right">
                <div class="illustration">
                  <svg viewBox="0 0 200 160" class="agent-illustration">
                    <circle cx="100" cy="50" r="12" fill="rgba(103,194,58,0.3)" stroke="#67c23a" stroke-width="2"/>
                    <text x="100" y="55" text-anchor="middle" fill="#67c23a" font-size="10" font-weight="bold">核心</text>
                    <circle cx="60" cy="90" r="10" fill="rgba(103,194,58,0.2)" stroke="#67c23a" stroke-width="1.5"/>
                    <text x="60" y="94" text-anchor="middle" fill="#67c23a" font-size="8">节点1</text>
                    <circle cx="100" cy="110" r="10" fill="rgba(103,194,58,0.2)" stroke="#67c23a" stroke-width="1.5"/>
                    <text x="100" y="114" text-anchor="middle" fill="#67c23a" font-size="8">节点2</text>
                    <circle cx="140" cy="90" r="10" fill="rgba(103,194,58,0.2)" stroke="#67c23a" stroke-width="1.5"/>
                    <text x="140" y="94" text-anchor="middle" fill="#67c23a" font-size="8">节点3</text>
                    <circle cx="50" cy="130" r="8" fill="rgba(103,194,58,0.15)" stroke="#67c23a" stroke-width="1"/>
                    <circle cx="90" cy="140" r="8" fill="rgba(103,194,58,0.15)" stroke="#67c23a" stroke-width="1"/>
                    <circle cx="130" cy="130" r="8" fill="rgba(103,194,58,0.15)" stroke="#67c23a" stroke-width="1"/>
                    <circle cx="150" cy="60" r="8" fill="rgba(103,194,58,0.15)" stroke="#67c23a" stroke-width="1"/>
                    <line x1="100" y1="62" x2="60" y2="80" stroke="#67c23a" stroke-width="1" opacity="0.5"/>
                    <line x1="100" y1="62" x2="100" y2="100" stroke="#67c23a" stroke-width="1" opacity="0.5"/>
                    <line x1="100" y1="62" x2="140" y2="80" stroke="#67c23a" stroke-width="1" opacity="0.5"/>
                    <line x1="60" y1="100" x2="50" y2="122" stroke="#67c23a" stroke-width="0.8" opacity="0.4"/>
                    <line x1="100" y1="120" x2="90" y2="132" stroke="#67c23a" stroke-width="0.8" opacity="0.4"/>
                    <line x1="140" y1="100" x2="130" y2="122" stroke="#67c23a" stroke-width="0.8" opacity="0.4"/>
                    <line x1="100" y1="62" x2="150" y2="52" stroke="#67c23a" stroke-width="0.8" opacity="0.4"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 右侧面板 -->
      <aside class="right-panel">
        <div class="panel-section">
          <div class="panel-header">
            <span class="panel-title">通知公告</span>
            <el-button type="primary" link size="small">更多</el-button>
          </div>
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

        <div class="panel-section">
          <div class="panel-header">
            <span class="panel-title">实训任务动态</span>
            <el-button type="primary" link size="small">更多</el-button>
          </div>
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
      </aside>
    </div>

    <!-- 底部统计区 -->
    <div class="bottom-section">
      <div class="chart-card learning-stats">
        <div class="chart-header">
          <span>学习数据统计</span>
          <el-radio-group v-model="statsTab" size="small">
            <el-radio-button label="7天">近7天</el-radio-button>
            <el-radio-button label="30天">近30天</el-radio-button>
            <el-radio-button label="学年">学年统计</el-radio-button>
          </el-radio-group>
        </div>
        <div class="stats-grid">
          <div class="stats-item">
            <div class="stats-value">286.5</div>
            <div class="stats-label">课时(小时)</div>
          </div>
          <div class="stats-item">
            <div class="stats-value">1289</div>
            <div class="stats-label">完成任务</div>
          </div>
          <div class="stats-item">
            <div class="stats-value">96</div>
            <div class="stats-label">平均分</div>
          </div>
          <div class="stats-item">
            <div class="stats-value">87.4</div>
            <div class="stats-label">课堂评分</div>
          </div>
        </div>
        <div ref="learningChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card ability-analysis">
        <div class="chart-header">能力维度分析</div>
        <div ref="radarChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card resource-top">
        <div class="chart-header">资源使用TOP5</div>
        <div class="resource-list">
          <div v-for="(resource, index) in resourceTop5" :key="index" class="resource-item">
            <span class="resource-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            <span class="resource-name">{{ resource.name }}</span>
            <span class="resource-count">{{ resource.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 小翼悬浮数字人 -->
    <div v-if="showAiBall" class="ai-float-ball" @click="goToAiAssistant">
      <div class="ai-ball-avatar">
        <div class="ball-head">
          <div class="ball-face">
            <div class="ball-eyes">
              <div class="ball-eye"><div class="ball-pupil"></div></div>
              <div class="ball-eye"><div class="ball-pupil"></div></div>
            </div>
            <div class="ball-mouth"></div>
          </div>
          <div class="ball-antenna"><div class="ball-antenna-dot"></div></div>
        </div>
        <div class="ball-body">
          <div class="ball-core"></div>
        </div>
        <div class="ball-glow"></div>
      </div>
      <span class="ball-label">小翼</span>
      <div class="ball-hide-btn" @click.stop="showAiBall = false" title="隐藏">
        <el-icon :size="12"><Close /></el-icon>
      </div>
    </div>

    <!-- 悬浮球隐藏后的恢复按钮 -->
    <div v-else class="ai-restore-btn" @click="showAiBall = true" title="显示小翼">
      <el-icon :size="16"><ChatDotRound /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { Document, List, User, TrendCharts, Close, ChatDotRound } from '@element-plus/icons-vue'

const router = useRouter()

// 小翼悬浮球状态
const showAiBall = ref(true)
const goToAiAssistant = () => {
  router.push('/ai-assistant')
}

// 平台统计数据
const platformStats = ref([
  { key: 'courses', icon: 'Document', value: '12', label: '课程总数', change: '+2' },
  { key: 'training', icon: 'List', value: '36', label: '实训任务', change: '+5' },
  { key: 'students', icon: 'User', value: '1286', label: '学生总数', change: '+66' },
  { key: 'score', icon: 'TrendCharts', value: '78.6%', label: '平均成绩', change: '+6.3%' }
])

// 系统状态
const systemStatus = ref([
  { key: 'run', label: '系统运行', value: '正常', status: 'online' },
  { key: 'ai', label: 'AI服务', value: '在线', status: 'online' },
  { key: 'sync', label: '数据同步', value: '正常', status: 'online' }
])

// 通知公告
const notices = ref([
  { id: 1, title: '关于开展低空应急运输实训课程的通知', date: '2024-05-25' },
  { id: 2, title: '平台系统升级维护公告', date: '2024-05-20' },
  { id: 3, title: '新增课程资源上线通知', date: '2024-05-18' },
  { id: 4, title: '关于开展无人机航线规划培训的通知', date: '2024-05-15' }
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

// 初始化图表
onMounted(() => {
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
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 22, 40, 0.98) 100%);
  border-radius: 10px;
  padding: clamp(14px, 1.5vw, 24px);
  border: 1px solid rgba(64, 158, 255, 0.25);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.panel-title {
  font-size: clamp(13px, 1vw, 16px);
  font-weight: 700;
  margin-bottom: clamp(10px, 1vw, 16px);
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.5px;
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
  font-size: clamp(18px, 1.5vw, 24px);
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
  margin-top: 4px;
}

.stat-change {
  font-size: 12px;
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
  height: clamp(200px, 18vw, 360px);
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
  background: linear-gradient(135deg, rgba(10, 22, 40, 0.7) 0%, rgba(10, 22, 40, 0.4) 50%, rgba(10, 22, 40, 0.6) 100%);
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

.banner-title {
  font-size: clamp(20px, 2vw, 36px);
  font-weight: 800;
  color: #fff;
  margin-bottom: clamp(8px, 0.8vw, 14px);
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.banner-subtitle {
  font-size: clamp(12px, 0.9vw, 15px);
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 1px;
}

/* ===== 智能体卡片区域 ===== */
.agents-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(10px, 1.2vw, 16px);
}

.agent-card {
  border-radius: 12px;
  padding: clamp(14px, 1.2vw, 20px);
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  min-height: clamp(200px, 15vw, 280px);
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

/* 蓝色主题 - 路径规划 */
.agent-blue {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.15) 0%, rgba(10, 22, 40, 0.95) 100%);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.agent-blue::before {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.25) 0%, rgba(10, 22, 40, 0.95) 100%);
}

.agent-blue:hover {
  border-color: rgba(64, 158, 255, 0.6);
  box-shadow: 0 12px 32px rgba(64, 158, 255, 0.2);
}

/* 紫色主题 - 装箱评价 */
.agent-purple {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.15) 0%, rgba(10, 22, 40, 0.95) 100%);
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.agent-purple::before {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.25) 0%, rgba(10, 22, 40, 0.95) 100%);
}

.agent-purple:hover {
  border-color: rgba(156, 39, 176, 0.6);
  box-shadow: 0 12px 32px rgba(156, 39, 176, 0.2);
}

/* 绿色主题 - 课程图谱 */
.agent-green {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(10, 22, 40, 0.95) 100%);
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.agent-green::before {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.25) 0%, rgba(10, 22, 40, 0.95) 100%);
}

.agent-green:hover {
  border-color: rgba(103, 194, 58, 0.6);
  box-shadow: 0 12px 32px rgba(103, 194, 58, 0.2);
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
  width: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 标题样式 */
.agent-title {
  font-size: clamp(14px, 1.2vw, 18px);
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}

.agent-subtitle {
  font-size: clamp(11px, 0.8vw, 12px);
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: clamp(10px, 1vw, 16px);
}

/* 功能列表 */
.feature-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px 0;
  flex: 1;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: clamp(11px, 0.8vw, 13px);
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: clamp(6px, 0.6vw, 10px);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot.blue {
  background: #409eff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.6);
}

.dot.purple {
  background: #9c27b0;
  box-shadow: 0 0 8px rgba(156, 39, 176, 0.6);
}

.dot.green {
  background: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.6);
}

/* 进入按钮 */
.enter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: clamp(8px, 0.8vw, 10px) clamp(16px, 1.5vw, 24px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  color: #fff;
  font-size: clamp(12px, 0.9vw, 14px);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  width: fit-content;
}

.enter-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.1));
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateX(4px);
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
  width: clamp(80px, 8vw, 130px);
  height: clamp(80px, 8vw, 130px);
}

/* 右侧面板 */
.right-panel {
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 22, 40, 0.98) 100%);
  border-radius: 10px;
  padding: clamp(14px, 1.5vw, 24px);
  border: 1px solid rgba(64, 158, 255, 0.25);
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
  background: linear-gradient(180deg, rgba(13, 33, 55, 0.95) 0%, rgba(10, 22, 40, 0.98) 100%);
  border-radius: 10px;
  padding: clamp(14px, 1.5vw, 24px);
  border: 1px solid rgba(64, 158, 255, 0.25);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.chart-header {
  font-size: clamp(13px, 1vw, 16px);
  font-weight: 700;
  margin-bottom: clamp(10px, 1vw, 16px);
  color: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  font-size: clamp(16px, 1.3vw, 22px);
  font-weight: 800;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stats-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.chart-container {
  height: clamp(120px, 10vw, 180px);
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

/* ===== 小翼悬浮数字人 ===== */
.ai-float-ball {
  position: fixed;
  bottom: 28px;
  right: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  z-index: 100;
  animation: ballFloat 3s ease-in-out infinite;
}

@keyframes ballFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.ai-float-ball:hover {
  animation-play-state: paused;
}

.ai-ball-avatar {
  position: relative;
  width: 72px;
  height: 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.3s;
}

.ai-float-ball:hover .ai-ball-avatar {
  transform: scale(1.1);
}

/* 光晕 */
.ball-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 229, 255, 0.25) 0%, transparent 70%);
  animation: ballGlowPulse 2.5s ease-in-out infinite;
  pointer-events: none;
}

@keyframes ballGlowPulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
}

/* 小头 */
.ball-head {
  position: relative;
  width: 52px;
  height: 52px;
  z-index: 2;
}

.ball-face {
  width: 52px;
  height: 48px;
  background: linear-gradient(135deg, #0d2137, #0a1a2e);
  border-radius: 22px 22px 20px 20px;
  border: 2px solid rgba(0, 229, 255, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.25), inset 0 0 10px rgba(0, 229, 255, 0.1);
}

/* 小眼睛 */
.ball-eyes {
  display: flex;
  gap: 12px;
}

.ball-eye {
  width: 10px;
  height: 10px;
  background: #0a1628;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 229, 255, 0.5);
}

.ball-pupil {
  width: 5px;
  height: 5px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.9);
  animation: ballBlink 3.5s ease-in-out infinite;
}

@keyframes ballBlink {
  0%, 44%, 56%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}

/* 小嘴巴 */
.ball-mouth {
  width: 10px;
  height: 4px;
  background: rgba(0, 229, 255, 0.5);
  border-radius: 0 0 5px 5px;
}

/* 小天线 */
.ball-antenna {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 10px;
  background: linear-gradient(to top, rgba(0, 229, 255, 0.5), rgba(0, 229, 255, 0.2));
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ball-antenna-dot {
  position: absolute;
  top: -4px;
  width: 5px;
  height: 5px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 229, 255, 0.9);
  animation: antennaPulse 2s ease-in-out infinite;
}

@keyframes antennaPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 小身体 */
.ball-body {
  width: 40px;
  height: 30px;
  background: linear-gradient(135deg, #0d2137, #0a1a2e);
  border-radius: 8px 8px 16px 16px;
  border: 2px solid rgba(0, 229, 255, 0.4);
  margin-top: -4px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
}

.ball-core {
  width: 10px;
  height: 10px;
  background: #00e5ff;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.9);
  animation: corePulse 2s ease-in-out infinite;
}

@keyframes corePulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(0.8); opacity: 0.6; }
}

/* 标签 */
.ball-label {
  font-size: 12px;
  color: #00e5ff;
  background: rgba(0, 20, 30, 0.95);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid rgba(0, 229, 255, 0.4);
  box-shadow: 0 2px 8px rgba(0, 229, 255, 0.15);
  font-weight: 600;
}

/* 隐藏按钮 */
.ball-hide-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  background: rgba(245, 108, 108, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 10;
}

.ai-float-ball:hover .ball-hide-btn {
  opacity: 1;
}

.ball-hide-btn:hover {
  background: rgba(245, 108, 108, 1);
}

/* 恢复按钮 */
.ai-restore-btn {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.25), rgba(0, 180, 204, 0.25));
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  color: #00e5ff;
  transition: all 0.3s;
  box-shadow: 0 2px 12px rgba(0, 229, 255, 0.2);
}

.ai-restore-btn:hover {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.45), rgba(0, 180, 204, 0.45));
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(0, 229, 255, 0.35);
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

  .ai-float-ball {
    bottom: 16px;
    right: 16px;
  }

  .ai-ball-avatar {
    transform: scale(0.8);
  }

  .ai-restore-btn {
    bottom: 16px;
    right: 16px;
    width: 38px;
    height: 38px;
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