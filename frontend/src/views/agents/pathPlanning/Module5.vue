<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDiagnosisStore } from '@/stores/pathPlanning/diagnosis'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import RightPanel from '@/components/pathPlanning/RightPanel.vue'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

const diagStore = useDiagnosisStore()
const optStore = useOptimizerStore()

const showRight = ref(false)
const rightType = ref(null)
const assessing = ref(false)

const exhibitMode = ref(localStorage.getItem('pathPlanningExhibit') === '1')

function toggleExhibit() {
  exhibitMode.value = !exhibitMode.value
  localStorage.setItem('pathPlanningExhibit', exhibitMode.value ? '1' : '0')
}

const canRun = computed(() => exhibitMode.value || (optStore.result && !diagStore.loading))

const dimensions = [
  { key: 'safety', name: '安全性', weight: 35, icon: '🛡️', desc: '载重、航程、飞行安全' },
  { key: 'timeliness', name: '时效性', weight: 35, icon: '⏱️', desc: '配送时间、无人机利用率、优先级满足' },
  { key: 'economy', name: '经济性', weight: 15, icon: '💰', desc: '路径优化、负载均衡、资源利用' },
  { key: 'feasibility', name: '可行性', weight: 15, icon: '✅', desc: '需求覆盖、硬约束满足、可执行性' },
]

onMounted(() => {
  diagStore.loadHistory()
})

// 展览模式下，路径规划 & 规则诊断 & AI诊断 全部塞一份预设的假数据
async function handleRuleDiagnosis() {
  if (exhibitMode.value) {
    assessing.value = true
    await new Promise(r => setTimeout(r, 2000))
    diagStore.result = {
      feasible: true,
      score: 100,
      issues: [],
      warnings: [],
      suggestions: ['✅ 各项指标均优秀，满分通过'],
      four_dimensional_scores: { safety: 100, timeliness: 100, economy: 100, feasibility: 100 },
      rule_report: {
        summary: '展览模式：方案各项指标均优秀，满分通过 ✅',
        details: {
          safety_verdict: '✅ 通过 — 所有无人机载重/航程/飞行高度均在安全阈值内',
          timeliness_verdict: '✅ 通过 — 9 个需求点中 8 个在时效窗口内',
          economy_verdict: '✅ 良好 — 路径总里程 124km，负载均衡度 0.88',
          feasibility_verdict: '✅ 通过 — 所有硬约束满足（最大起飞重量、最小间隔、禁飞区避让）',
        },
      },
      ai_report: '',
      task_summary: { total_tasks: 9, priority_p1: 3, priority_p2: 4, priority_p3: 2 },
      diagnosis_mode: 'rule',
    }
    diagStore.activeTab = 'rule'
    diagStore.diagnosisMode = 'rule'
    assessing.value = false
    rightType.value = 'result'
    showRight.value = true
    return
  }
  assessing.value = true
  const res = await diagStore.runRuleDiagnosis()
  assessing.value = false
  if (res) {
    rightType.value = 'result'
    showRight.value = true
    diagStore.setActiveTab('rule')
  }
}

async function handleAiDiagnosis() {
  if (exhibitMode.value) {
    assessing.value = true
    await new Promise(r => setTimeout(r, 5000))
    diagStore.result = {
      feasible: true,
      score: 94,
      issues: [],
      warnings: [
        { code: 'W-PAYLOAD', msg: '无人机 PT-5 最大载重 5kg，任务 #T07 装载 4.8kg，接近上限', level: 'warning' },
        { code: 'W-WIND', msg: '区域 #R04 起飞时风速 6 级，建议增加 1 架备用', level: 'warning' },
      ],
      suggestions: [
        '将 #T07 任务由 PT-5 更换为 FY-15（载重 15kg），冗余更充足',
        '在配送中心增加 1 架备用 PT-5 应对突发情况',
        '建议在 #R02 与 #R05 之间增设 1 个地面中继站，提升通信覆盖率',
      ],
      four_dimensional_scores: { safety: 97, timeliness: 92, economy: 91, feasibility: 94 },
      rule_report: {
        summary: 'AI 综合诊断：方案整体优秀，建议优化 2 处细节',
        details: {
          safety_verdict: '🛡️ 安全：载重冗余 15%+，航程裕量满足往返',
          timeliness_verdict: '⏱️ 时效：黄金救援时间 3 小时内可覆盖全部需求点',
          economy_verdict: '💰 经济：单位载荷成本 0.42 元/kg·km，优于行业均值',
          feasibility_verdict: '✅ 可行：已避让禁飞区 7 处，起降坪 9 座全部满足',
        },
      },
      ai_report: `# 🤖 AI 智能诊断报告

## 诊断概览
- 诊断引擎：低空应急配送 LLM v2.3 + 规则引擎双校验
- 方案版本：V1.2（2026-06-11 09:42 生成）
- 综合评分：**94 / 100**（优秀）
- 可行性：✅ **通过**

## 可行性评估
方案整体可行，所有硬约束（最大起飞重量 / 最小间隔 / 禁飞区 / 起降坪长度）全部通过校验。软约束中识别到 **2 条警告**、**0 条致命问题**。

## 严重问题（🔴 致命）
**未发现致命问题** — 方案可直接执行。

## 风险与警告（🟡 建议关注）
- 无人机 PT-5 最大载重 5kg，任务 #T07 装载 4.8kg，接近上限，建议更换为 FY-15
- 区域 #R04 起飞时风速 6 级（风力预警），建议增加 1 架备用无人机
- 需求点 #D09 周边通信信号较弱（LTE 覆盖率 78%），建议预先布设中继

## 优化建议（💡 AI 推荐）
1. **载重优化**：将 #T07 任务从 PT-5 切换到 FY-15，可获得 3 倍载重冗余
2. **风速冗余**：配送中心常驻 1 架备用 PT-5，遇大风天气可替换出任务机型
3. **通信增强**：在 #R02—#R05 之间增设 1 台便携中继站，预计覆盖率从 78% 提升到 98%
4. **路径微调**：将原 #T03 的直飞路径改为途经 #R06 补给，减少 8min 返航时间

## 四维评分详情
| 维度 | 得分 | 权重 | 加权分 | 说明 |
|------|------|------|--------|------|
| 🛡️ 安全性 | 97 | 35% | 33.95 | 载重/航程/抗风均在阈值内 |
| ⏱️ 时效性 | 92 | 35% | 32.20 | 1 个需求点接近时效上限 |
| 💰 经济性 | 91 | 15% | 13.65 | 单位载荷成本低于行业均值 12% |
| ✅ 可行性 | 94 | 15% | 14.10 | 硬约束全部通过 |

## 执行路线建议
- 第一批（0~30min）：重载无人机（CW-25 / Y30）优先起飞，覆盖 3 个 P1 级需求点
- 第二批（30~60min）：中载通用无人机（FY-15）起飞，覆盖 4 个 P2 级需求点
- 第三批（60~90min）：轻载高速无人机（PT-5）起飞，负责急救药品急件
- 地面指挥：建立 3 人指挥小组 + 双通道通信（4G/5G + 数传 900MHz）

> 本报告由 **低空应急智能体 · AI 诊断引擎** 生成，已通过规则引擎双校验 ✅`,
      task_summary: { total_tasks: 9, priority_p1: 3, priority_p2: 4, priority_p3: 2 },
      diagnosis_mode: 'ai',
    }
    diagStore.activeTab = 'ai'
    diagStore.diagnosisMode = 'ai'
    assessing.value = false
    rightType.value = 'result'
    showRight.value = true
    return
  }
  assessing.value = true
  const res = await diagStore.runAiDiagnosis()
  assessing.value = false
  if (res) {
    rightType.value = 'result'
    showRight.value = true
    diagStore.setActiveTab('ai')
  }
}

function handleReset() {
  diagStore.resetResult()
  showRight.value = false
  rightType.value = null
}

function closeRight() {
  showRight.value = false
  rightType.value = null
}

function getScoreColor(score) {
  if (score === undefined || score === null) return 'bad'
  if (score >= 80) return 'good'
  if (score >= 60) return 'warning'
  return 'bad'
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

// 雷达图计算函数
const CENTER_X = 140
const CENTER_Y = 140
const MAX_RADIUS = 96

function getAngle(index, total) {
  return (Math.PI * 2 * index) / total - Math.PI / 2
}

function getAxisPoint(index, value) {
  const angle = getAngle(index, dimensions.length)
  const radius = (value / 100) * MAX_RADIUS
  return {
    x: CENTER_X + radius * Math.cos(angle),
    y: CENTER_Y + radius * Math.sin(angle)
  }
}

function getPolygonPoints(level) {
  const points = dimensions.map((_, index) => {
    const point = getAxisPoint(index, level)
    return `${point.x},${point.y}`
  })
  return points.join(' ')
}

function getDataPoints() {
  const points = dimensions.map((dim, index) => {
    const value = diagStore.fourDimensionalScores[dim.key] || 0
    const point = getAxisPoint(index, value)
    return `${point.x},${point.y}`
  })
  return points.join(' ')
}

function getLabelPoint(index) {
  const angle = getAngle(index, dimensions.length)
  const radius = MAX_RADIUS + 8
  return {
    x: CENTER_X + radius * Math.cos(angle),
    y: CENTER_Y + radius * Math.sin(angle) + 4
  }
}

function getLabelAnchor(index) {
  const angle = getAngle(index, dimensions.length)
  const cos = Math.cos(angle)
  if (cos > 0.1) return 'start'
  if (cos < -0.1) return 'end'
  return 'middle'
}

async function viewHistory(recordId) {
  const data = await diagStore.viewHistoryDetail(recordId)
  if (data) {
    rightType.value = 'result'
    showRight.value = true
  }
}

async function deleteHistory(recordId) {
  if (!confirm('确定要删除这条诊断记录吗？')) return
  await diagStore.deleteRecord(recordId)
}

// AI报告解析：将Markdown转换为结构化数据
const aiReportSections = computed(() => {
  if (!diagStore.aiReport) return []
  
  const markdown = diagStore.aiReport
  const sections = []
  
  // 按二级标题分割
  const heading2Regex = /^## (.+)$/gm
  const parts = markdown.split(heading2Regex)
  
  for (let i = 1; i < parts.length; i += 2) {
    const title = parts[i]?.trim() || ''
    const content = parts[i + 1]?.trim() || ''
    
    if (!title) continue
    
    // 分类判断
    let type = 'default'
    let icon = '📋'
    let items = []
    
    if (title.includes('可行性')) {
      type = 'feasibility'
      icon = content.includes('✅') ? '✅' : '❌'
    } else if (title.includes('问题') && title.includes('严重')) {
      type = 'issues'
      icon = '🔴'
      items = extractListItems(content)
    } else if (title.includes('风险') || title.includes('警告')) {
      type = 'warnings'
      icon = '🟡'
      items = extractListItems(content)
    } else if (title.includes('建议') || title.includes('优化')) {
      type = 'suggestions'
      icon = '💡'
      items = extractListItems(content)
    } else if (title.includes('评估') || title.includes('评分')) {
      type = 'summary'
      icon = '📊'
    }
    
    // 提取评分
    let score = null
    const scoreMatch = content.match(/(\d+(?:\.\d+)?)\s*(?:分|\/100)/)
    if (scoreMatch) {
      score = parseFloat(scoreMatch[1])
    }
    
    sections.push({
      type,
      title,
      icon,
      content,
      items,
      score,
      raw: content,
    })
  }
  
  return sections
})

function extractListItems(content) {
  const items = []
  const lines = content.split('\n')
  
  for (const line of lines) {
    const trimmed = line.trim()
    // 匹配各种列表格式：- item, * item, 1. item, ✅ item, ❌ item, ⚠️ item
    const match = trimmed.match(/^[-*]\s+(.+)$/) || 
                  trimmed.match(/^\d+\.\s+(.+)$/) ||
                  trimmed.match(/^[✅❌⚠️💡🔴🟡]\s+(.+)$/)
    
    if (match) {
      let text = match[1].trim()
      // 移除可能的加粗标记
      text = text.replace(/\*\*(.+?)\*\*/g, '$1')
      items.push(text)
    }
  }
  
  return items
}

// AI报告的可行性和评分
const aiFeasibility = computed(() => {
  const section = aiReportSections.value.find(s => s.type === 'feasibility')
  if (!section) return null
  return section.content.includes('✅') || section.content.includes('可行')
})

const aiScore = computed(() => {
  const section = aiReportSections.value.find(s => s.type === 'summary')
  return section?.score || null
})

const aiIssues = computed(() => {
  const section = aiReportSections.value.find(s => s.type === 'issues')
  return section?.items || []
})

const aiWarnings = computed(() => {
  const section = aiReportSections.value.find(s => s.type === 'warnings')
  return section?.items || []
})

const aiSuggestions = computed(() => {
  const section = aiReportSections.value.find(s => s.type === 'suggestions')
  return section?.items || []
})
</script>

<template>
  <div class="module5">
    <div class="mod-title">
      <span class="mod-icon">🔍</span>
      <span>方案诊断</span>
    </div>

    <div class="task-overview">
      <div class="stat-item">
        <span class="stat-value">{{ optStore.result?.summary?.village_count || 0 }}</span>
        <span class="stat-label">需求点</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ optStore.result?.summary?.drone_count || 0 }}</span>
        <span class="stat-label">无人机</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ optStore.result?.summary?.total_trips || 0 }}</span>
        <span class="stat-label">配送趟次</span>
      </div>
    </div>

    <div class="action-row">
      <button class="btn-primary rule-btn" :disabled="!canRun || assessing" @click="handleRuleDiagnosis">
        {{ assessing ? '诊断中...' : '📋 规则诊断' }}
      </button>
      <button class="btn-primary ai-btn" :disabled="!canRun || assessing" @click="handleAiDiagnosis">
        {{ assessing ? '诊断中...' : '🤖 AI诊断' }}
      </button>
      <button class="btn-secondary" :disabled="!diagStore.hasResult" @click="handleReset">
        重置
      </button>
      <button class="exhibit-toggle" :class="{ active: exhibitMode }" @click="toggleExhibit" :title="exhibitMode ? '展览模式已开启 · 点击关闭' : '点击开启展览模式'">
        展
      </button>
    </div>

    <div v-if="diagStore.error" class="error-msg">{{ diagStore.error }}</div>

    <div v-if="diagStore.loading" class="loading-bar"><div class="loading-bar-inner" /></div>

    <div v-if="!optStore.result" class="hint-box">
      <span class="hint-icon">💡</span>
      <span>请先在「路径规划」模块运行规划，然后再进行方案诊断</span>
    </div>

    <div v-if="diagStore.hasResult" class="section">
      <div class="section-header">
        <span>诊断结果</span>
        <span class="badge">{{ diagStore.score.toFixed(0) }}分</span>
      </div>
      <div class="section-body">
        <div class="result-header">
          <div class="feasibility-badge" :class="diagStore.feasible ? 'feasible' : 'infeasible'">
            {{ diagStore.feasible ? '✅ 方案可行' : '❌ 方案不可行' }}
          </div>
        </div>

        <!-- 四维评分卡片 -->
        <div class="four-d-grid">
          <div v-for="dim in dimensions" :key="dim.key" class="four-d-card">
            <div class="four-d-header">
              <span class="four-d-icon">{{ dim.icon }}</span>
              <span class="four-d-name">{{ dim.name }}</span>
              <span class="four-d-weight">{{ dim.weight }}%</span>
            </div>
            <div class="four-d-score" :class="getScoreColor(diagStore.fourDimensionalScores[dim.key])">
              {{ diagStore.fourDimensionalScores[dim.key] || 0 }}
              <span class="four-d-score-unit">分</span>
            </div>
            <div class="four-d-desc">{{ dim.desc }}</div>
          </div>
        </div>

        <!-- 四维评分雷达图 -->
        <div class="radar-chart">
          <svg viewBox="0 0 280 280" class="radar-svg">
            <!-- 雷达图背景 -->
            <polygon 
              v-for="level in [100, 75, 50, 25]" 
              :key="level"
              :points="getPolygonPoints(level)"
              class="radar-level"
              :style="{ opacity: 1 - level / 150 }"
            />
            <!-- 坐标轴 -->
            <line 
              v-for="(dim, index) in dimensions" 
              :key="'axis-' + dim.key"
              :x1="CENTER_X" :y1="CENTER_Y"
              :x2="getAxisPoint(index, 100).x"
              :y2="getAxisPoint(index, 100).y"
              class="radar-axis"
            />
            <!-- 数据区域 -->
            <polygon 
              :points="getDataPoints()"
              class="radar-data"
              :class="getScoreColor(diagStore.score)"
            />
            <!-- 数据点 -->
            <circle 
              v-for="(dim, index) in dimensions" 
              :key="'point-' + dim.key"
              :cx="getAxisPoint(index, diagStore.fourDimensionalScores[dim.key]).x"
              :cy="getAxisPoint(index, diagStore.fourDimensionalScores[dim.key]).y"
              r="4"
              class="radar-point"
            />
            <!-- 维度标签 -->
            <text 
              v-for="(dim, index) in dimensions" 
              :key="'label-' + dim.key"
              :x="getLabelPoint(index).x"
              :y="getLabelPoint(index).y"
              class="radar-label"
              :text-anchor="getLabelAnchor(index)"
            >
              {{ dim.name }}: {{ diagStore.fourDimensionalScores[dim.key] }}分
            </text>
          </svg>
        </div>

        <div class="summary-grid">
          <div class="sum-card">
            <span class="sum-val" :class="getScoreColor(diagStore.score)">{{ diagStore.score.toFixed(0) }}</span>
            <span class="sum-unit">分</span>
            <span class="sum-label">综合评分</span>
          </div>
          <div class="sum-card">
            <span class="sum-val" :class="diagStore.hasIssues ? 'bad' : 'good'">{{ diagStore.issues.length }}</span>
            <span class="sum-unit">个</span>
            <span class="sum-label">严重问题</span>
          </div>
          <div class="sum-card">
            <span class="sum-val" :class="diagStore.hasWarnings ? 'warning' : 'good'">{{ diagStore.warnings.length }}</span>
            <span class="sum-unit">个</span>
            <span class="sum-label">潜在风险</span>
          </div>
          <div class="sum-card">
            <span class="sum-val">{{ diagStore.suggestions.length }}</span>
            <span class="sum-unit">条</span>
            <span class="sum-label">优化建议</span>
          </div>
        </div>

        <button class="btn-detail" @click="rightType = 'result'; showRight = true">
          查看详细诊断报告 →
        </button>
      </div>
    </div>

    <div v-if="diagStore.history.length > 0" class="section">
      <div class="section-header">
        <span>诊断历史</span>
      </div>
      <div class="section-body">
        <div class="history-list">
          <div v-for="record in diagStore.history" :key="record.id" class="history-item">
            <div class="history-main">
              <div class="history-score" :class="getScoreColor(record.score)">
                {{ record.score.toFixed(0) }}
              </div>
              <div class="history-info">
                <div class="history-mode" :class="record.diagnosis_mode">
                  {{ record.diagnosis_mode === 'ai' ? '🤖 AI诊断' : record.diagnosis_mode === 'both' ? '🔍 综合诊断' : '📋 规则诊断' }}
                </div>
                <div class="history-meta">
                  <span>问题: {{ record.issues_count }} | 警告: {{ record.warnings_count }}</span>
                </div>
                <div class="history-time">{{ formatTime(record.created_at) }}</div>
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

    <RightPanel
      v-if="showRight && rightType === 'result'"
      :title="diagStore.diagnosisMode === 'ai' ? 'AI 诊断报告' : '规则诊断报告'"
      :width="600"
      @close="closeRight"
    >
      <div class="rp-content">
        <div v-if="diagStore.diagnosisMode === 'both'" class="rp-tabs">
          <button
            class="rp-tab"
            :class="{ active: diagStore.activeTab === 'rule' }"
            @click="diagStore.setActiveTab('rule')"
          >
            规则评估
          </button>
          <button
            class="rp-tab"
            :class="{ active: diagStore.activeTab === 'ai' }"
            @click="diagStore.setActiveTab('ai')"
          >
            AI评估
          </button>
        </div>

        <div v-if="diagStore.activeTab === 'rule'" class="rule-report">
          <!-- 可行性结论 -->
          <div class="report-section" :class="diagStore.feasible ? 'pass' : 'fail'">
            <div class="report-section-header">
              <span class="report-section-icon">{{ diagStore.feasible ? '✅' : '❌' }}</span>
              <span>方案可行性结论</span>
            </div>
            <div class="report-section-body">
              <p v-if="diagStore.feasible && diagStore.issues.length === 0">方案通过所有安全性检查，无致命问题，可以执行。</p>
              <p v-else-if="diagStore.feasible">方案基本可行，但存在需要关注的问题（见下方详细诊断）。</p>
              <p v-else>方案存在 {{ diagStore.issues.length }} 个致命安全问题，必须修正后才能执行。</p>
            </div>
          </div>

          <!-- 四维诊断详情 -->
          <div class="dim-detail" v-for="dim in [
            { key: 'safety', name: '安全性检查', icon: '🛡️', weight: '35%', desc: '超载检测、航程安全、机型匹配' },
            { key: 'timeliness', name: '时效性检查', icon: '⏱️', weight: '35%', desc: '优先级执行、配送顺序、资源利用' },
            { key: 'economy', name: '经济性检查', icon: '💰', weight: '15%', desc: '航线效率、负载均衡、能耗控制' },
            { key: 'feasibility', name: '可行性检查', icon: '✅', weight: '15%', desc: '需求覆盖、点位遗漏、重复配送' }
          ]" :key="dim.key">
            <div class="dim-header">
              <span class="dim-icon">{{ dim.icon }}</span>
              <span class="dim-name">{{ dim.name }}</span>
              <span class="dim-weight">{{ dim.weight }}</span>
              <span class="dim-score" :class="getScoreColor(diagStore.fourDimensionalScores[dim.key])">
                {{ diagStore.fourDimensionalScores[dim.key] || 0 }}分
              </span>
            </div>
            <div class="dim-desc">{{ dim.desc }}</div>
            <!-- 该维度发现的问题 -->
            <div class="dim-findings" v-if="diagStore.ruleReport?.details?.[dim.key]">
              <div v-for="(item, i) in (diagStore.ruleReport.details[dim.key].issue_items || [])" :key="'i'+i" class="finding-item bad">
                <span>{{ item }}</span>
              </div>
              <div v-for="(item, i) in (diagStore.ruleReport.details[dim.key].warning_items || [])" :key="'w'+i" class="finding-item warn">
                <span>{{ item }}</span>
              </div>
              <div v-for="(str, i) in (diagStore.ruleReport.details[dim.key].strengths || [])" :key="'s'+i" class="finding-item good">
                <span class="finding-icon">✅</span>
                <span>{{ str }}</span>
              </div>
              <div v-if="(diagStore.ruleReport.details[dim.key].issue_items || []).length === 0 && (diagStore.ruleReport.details[dim.key].warning_items || []).length === 0 && (diagStore.ruleReport.details[dim.key].strengths || []).length === 0" class="no-finding">
                未发现问题
              </div>
            </div>
          </div>

          <!-- 致命问题 -->
          <div class="report-section issues">
            <div class="report-section-header">
              <span class="report-section-icon">🔴</span>
              <span>致命问题（{{ diagStore.issues.length }}个）</span>
            </div>
            <div class="report-section-body">
              <ul v-if="diagStore.issues.length > 0" class="issue-list">
                <li v-for="(issue, i) in diagStore.issues" :key="i" class="issue-item">
                  <span>{{ issue }}</span>
                </li>
              </ul>
              <p v-else class="no-finding">未发现致命安全问题</p>
            </div>
          </div>

          <!-- 潜在风险 -->
          <div class="report-section warnings">
            <div class="report-section-header">
              <span class="report-section-icon">🟡</span>
              <span>潜在风险（{{ diagStore.warnings.length }}个）</span>
            </div>
            <div class="report-section-body">
              <ul v-if="diagStore.warnings.length > 0" class="warning-list">
                <li v-for="(warning, i) in diagStore.warnings" :key="i" class="warning-item">
                  <span>{{ warning }}</span>
                </li>
              </ul>
              <p v-else class="no-finding">未发现潜在风险</p>
            </div>
          </div>

          <!-- 优化建议 -->
          <div class="report-section suggestions">
            <div class="report-section-header">
              <span class="report-section-icon">💡</span>
              <span>优化建议（{{ diagStore.suggestions.length }}条）</span>
            </div>
            <div class="report-section-body">
              <ul v-if="diagStore.suggestions.length > 0" class="suggestion-list">
                <li v-for="(suggestion, i) in diagStore.suggestions" :key="i" class="suggestion-item">
                  <span>{{ suggestion }}</span>
                </li>
              </ul>
              <p v-else class="no-finding">暂无优化建议</p>
            </div>
          </div>

          <!-- 综合评估 -->
          <div class="report-section summary">
            <div class="report-section-header">
              <span class="report-section-icon">📊</span>
              <span>综合评估</span>
            </div>
            <div class="report-section-body">
              <div class="summary-grid">
                <div class="summary-item">
                  <span class="summary-label">综合评分</span>
                  <span class="summary-value" :class="getScoreColor(diagStore.score)">
                    {{ diagStore.score.toFixed(0) }}/100
                  </span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">需求点</span>
                  <span class="summary-value">{{ diagStore.taskSummary.demand_points_count }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">无人机</span>
                  <span class="summary-value">{{ diagStore.taskSummary.uavs_count }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">总趟次</span>
                  <span class="summary-value">{{ diagStore.taskSummary.total_trips }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="diagStore.activeTab === 'ai'" class="ai-report">
          <div v-if="diagStore.aiReport" class="ai-structured">
            <!-- 概览卡片 -->
            <div class="ai-overview">
              <div class="feasibility-badge" :class="aiFeasibility ? 'feasible' : 'infeasible'">
                {{ aiFeasibility ? '✅ AI评估：方案可行' : '❌ AI评估：方案存在严重问题' }}
              </div>
              <div v-if="aiScore !== null" class="ai-score-badge" :class="getScoreColor(aiScore)">
                {{ aiScore.toFixed(0) }}分
              </div>
            </div>

            <!-- 严重问题卡片 -->
            <div v-if="aiIssues.length > 0" class="report-section issues">
              <div class="report-section-header">
                <span class="report-section-icon">🔴</span>
                <span>严重问题（{{ aiIssues.length }}个）</span>
              </div>
              <div class="report-section-body">
                <ul class="issue-list">
                  <li v-for="(item, i) in aiIssues" :key="i" class="issue-item">
                    <span class="issue-bullet">•</span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 潜在风险卡片 -->
            <div v-if="aiWarnings.length > 0" class="report-section warnings">
              <div class="report-section-header">
                <span class="report-section-icon">🟡</span>
                <span>潜在风险（{{ aiWarnings.length }}个）</span>
              </div>
              <div class="report-section-body">
                <ul class="warning-list">
                  <li v-for="(item, i) in aiWarnings" :key="i" class="warning-item">
                    <span class="warning-bullet">•</span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 优化建议卡片 -->
            <div v-if="aiSuggestions.length > 0" class="report-section suggestions">
              <div class="report-section-header">
                <span class="report-section-icon">💡</span>
                <span>优化建议（{{ aiSuggestions.length }}条）</span>
              </div>
              <div class="report-section-body">
                <ul class="suggestion-list">
                  <li v-for="(item, i) in aiSuggestions" :key="i" class="suggestion-item">
                    <span class="suggestion-bullet">•</span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 其他内容卡片（未分类的内容） -->
            <div v-for="section in aiReportSections.filter(s => s.type === 'default' && s.items.length === 0)" 
                 :key="section.title" 
                 class="report-section default">
              <div class="report-section-header">
                <span class="report-section-icon">{{ section.icon }}</span>
                <span>{{ section.title }}</span>
              </div>
              <div class="report-section-body">
                <p>{{ section.content }}</p>
              </div>
            </div>

            <!-- 原始报告入口（可选显示） -->
            <details class="raw-report">
              <summary>查看AI原始报告</summary>
              <div class="raw-content" v-html="marked(diagStore.aiReport)" />
            </details>
          </div>
          <div v-else class="ai-empty">
            <span class="empty-icon">🤖</span>
            <p>AI评估需要配置大模型API</p>
            <p class="empty-hint">请在后端配置 LLM_API_KEY 后使用此功能</p>
          </div>
        </div>
      </div>
    </RightPanel>
  </div>
</template>

<style scoped>
.module5 {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mod-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  font-family: var(--mono);
}

.mod-icon { font-size: 18px; }

.task-overview { display: flex; gap: 10px; }

.stat-item {
  flex: 1;
  background: var(--navy3);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 800;
  color: var(--teal);
  font-family: var(--mono);
}

.stat-label {
  font-size: 11px;
  color: var(--text3);
  font-family: var(--mono);
}

.action-row { display: flex; gap: 10px; }

.btn-primary {
  flex: 1;
  height: 36px;
  background: var(--teal);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
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
  font-size: 13px;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover:not(:disabled) { border-color: var(--text3); color: var(--text); }
.btn-secondary:disabled { opacity: 0.3; cursor: not-allowed; }

.btn-primary.rule-btn {
  background: #00c8de;
}
.btn-primary.rule-btn:hover:not(:disabled) { background: #00b4cc; }

.btn-primary.ai-btn {
  background: #6c5ce7;
}
.btn-primary.ai-btn:hover:not(:disabled) { background: #5b4cdb; }

.error-msg {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  color: #ff4757;
  font-size: 13px;
  font-family: var(--mono);
  padding: 10px 14px;
  border-radius: 4px;
}

.exhibit-toggle {
  background: transparent;
  border: 1px dashed rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.2);
  font-size: 10px;
  font-family: var(--mono);
  padding: 0 6px;
  height: 35px;
  width: 28px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
  transition: color 0.2s, border-color 0.2s;
}
.exhibit-toggle:hover {
  color: rgba(255,255,255,0.4);
  border-color: rgba(255,255,255,0.3);
}
.exhibit-toggle.active {
  color: #22c55e;
  border-color: rgba(34,197,94,0.4);
  background: rgba(34,197,94,0.08);
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

.hint-box {
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 6px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text2);
  font-family: var(--mono);
}
.hint-icon { font-size: 16px; }

.section {
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: var(--navy3);
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
  font-family: var(--mono);
}
.badge {
  font-size: 11px;
  color: var(--teal);
  background: rgba(0, 229, 255, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
}
.section-body { padding: 14px; }

.result-header { margin-bottom: 12px; }
.feasibility-badge {
  display: inline-block;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  font-family: var(--mono);
}
.feasibility-badge.feasible {
  background: rgba(46, 213, 115, 0.1);
  color: #2ed573;
  border: 1px solid rgba(46, 213, 115, 0.3);
}
.feasibility-badge.infeasible {
  background: rgba(255, 71, 87, 0.1);
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.3);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}
.sum-card {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.sum-val {
  font-size: 18px;
  font-weight: 800;
  color: var(--teal);
  font-family: var(--mono);
}
.sum-val.good { color: #2ed573; }
.sum-val.warning { color: #ffb300; }
.sum-val.bad { color: #ff4757; }
.sum-unit { font-size: 11px; color: var(--text3); font-family: var(--mono); }
.sum-label { font-size: 10px; color: var(--text3); font-family: var(--mono); }

/* 四维评分卡片 */
.four-d-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.four-d-card {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.four-d-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.four-d-icon { font-size: 16px; }
.four-d-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  font-family: var(--mono);
}
.four-d-weight {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
  margin-left: auto;
}

/* 雷达图 */
.radar-chart {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  padding: 14px;
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
}
.radar-svg {
  width: 260px;
  height: 260px;
}
.radar-level {
  fill: rgba(0, 229, 255, 0.08);
  stroke: rgba(0, 229, 255, 0.2);
  stroke-width: 1;
}
.radar-axis {
  stroke: rgba(0, 229, 255, 0.3);
  stroke-width: 1;
}
.radar-data {
  fill: rgba(0, 229, 255, 0.3);
  stroke: var(--teal);
  stroke-width: 2;
}
.radar-data.good {
  fill: rgba(46, 213, 115, 0.3);
  stroke: #2ed573;
}
.radar-data.warning {
  fill: rgba(255, 179, 0, 0.3);
  stroke: #ffb300;
}
.radar-data.bad {
  fill: rgba(255, 71, 87, 0.3);
  stroke: #ff4757;
}
.radar-point {
  fill: var(--teal);
}
.radar-label {
  font-size: 11px;
  fill: var(--text2);
  font-family: var(--mono);
}

.four-d-score {
  font-size: 20px;
  font-weight: 800;
  color: var(--teal);
  font-family: var(--mono);
}
.four-d-score.good { color: #2ed573; }
.four-d-score.warning { color: #ffb300; }
.four-d-score.bad { color: #ff4757; }
.four-d-score-unit {
  font-size: 11px;
  color: var(--text3);
  font-family: var(--mono);
  margin-left: 2px;
}
.four-d-desc {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--mono);
}

.btn-detail {
  width: 100%;
  padding: 10px;
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  color: var(--teal);
  font-size: 13px;
  font-family: var(--mono);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-detail:hover { background: rgba(0, 229, 255, 0.15); border-color: rgba(0, 229, 255, 0.4); }

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 4px;
}
.history-score {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  font-family: var(--mono);
  background: rgba(0, 229, 255, 0.1);
  color: var(--teal);
}
.history-score.good { background: rgba(46, 213, 115, 0.1); color: #2ed573; }
.history-score.warning { background: rgba(255, 179, 0, 0.1); color: #ffb300; }
.history-score.bad { background: rgba(255, 71, 87, 0.1); color: #ff4757; }
.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.history-meta {
  font-size: 13px;
  color: var(--text2);
  font-family: var(--mono);
}
.history-time {
  font-size: 10px;
  color: var(--text3);
}

.history-main {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-actions {
  display: flex;
  gap: 6px;
}

.btn-history-view,
.btn-history-del {
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 11px;
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

.rp-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.rp-tabs {
  display: flex;
  gap: 6px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}
.rp-tab {
  flex: 1;
  padding: 10px 6px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text3);
  font-size: 13px;
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

.rule-report {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 四维诊断详情 */
.dim-detail {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 14px;
}
.dim-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dim-icon { font-size: 14px; }
.dim-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
  font-family: var(--mono);
  flex: 1;
}
.dim-weight {
  font-size: 11px;
  color: var(--text3);
  background: var(--navy3);
  padding: 3px 7px;
  border-radius: 3px;
}
.dim-score {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--mono);
}
.dim-desc {
  font-size: 11px;
  color: var(--text3);
  margin: 4px 0 6px 20px;
}
.dim-findings {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-left: 20px;
}
.finding-item {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 13px;
  line-height: 1.4;
}
.finding-item.good { color: var(--green); }
.finding-item.bad { color: var(--red, #ff4757); }
.finding-item.warn { color: var(--orange, #ffa502); }
.finding-icon { font-size: 13px; flex-shrink: 0; margin-top: 1px; }

.report-section.pass { border-color: rgba(0, 200, 83, 0.3); }
.report-section.fail { border-color: rgba(255, 71, 87, 0.3); }

.no-finding {
  font-size: 13px;
  color: var(--text3);
  margin: 0;
  font-style: italic;
}

.report-section {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.report-section.issues { border-color: rgba(255, 71, 87, 0.3); }
.report-section.warnings { border-color: rgba(255, 179, 0, 0.3); }
.report-section.suggestions { border-color: rgba(0, 229, 255, 0.3); }

.report-section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: var(--navy3);
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
  font-family: var(--mono);
}
.report-section-icon { font-size: 14px; }

.report-section-body {
  padding: 12px 14px;
  font-size: 13px;
  color: var(--text2);
  font-family: var(--mono);
  line-height: 1.5;
}

.issue-list, .warning-list, .suggestion-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.issue-item, .warning-item, .suggestion-item {
  display: flex;
  gap: 10px;
}

.issue-bullet { color: #ff4757; }
.warning-bullet { color: #ffb300; }
.suggestion-bullet { color: #00e5ff; }

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: var(--navy3);
  border-radius: 4px;
}
.summary-label {
  font-size: 13px;
  color: var(--text3);
  font-family: var(--mono);
}
.summary-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--teal);
  font-family: var(--mono);
}

.ai-report {
  min-height: 300px;
}
.ai-content {
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text2);
}
.ai-content h1 { font-size: 16px; color: var(--teal); margin: 0 0 12px 0; }
.ai-content h2 { font-size: 14px; color: var(--text); margin: 12px 0 8px 0; }
.ai-content h3 { font-size: 13px; color: var(--text2); margin: 8px 0 6px 0; }
.ai-content ul, .ai-content ol { padding-left: 20px; margin: 6px 0; }
.ai-content li { margin: 4px 0; }
.ai-content p { margin: 6px 0; }
.ai-content strong { color: var(--teal); }

.ai-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 42px 22px;
  text-align: center;
}
.empty-icon { font-size: 40px; margin-bottom: 12px; }
.ai-empty p {
  font-size: 13px;
  color: var(--text2);
  font-family: var(--mono);
  margin: 4px 0;
}
.empty-hint {
  font-size: 11px !important;
  color: var(--text3) !important;
}

.ai-structured {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ai-overview {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: var(--navy3);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.ai-score-badge {
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 800;
  font-family: var(--mono);
  background: rgba(0, 229, 255, 0.1);
  color: var(--teal);
}
.ai-score-badge.good {
  background: rgba(46, 213, 115, 0.1);
  color: #2ed573;
}
.ai-score-badge.warning {
  background: rgba(255, 179, 0, 0.1);
  color: #ffb300;
}
.ai-score-badge.bad {
  background: rgba(255, 71, 87, 0.1);
  color: #ff4757;
}

.report-section.default {
  background: var(--navy1);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}

.raw-report {
  margin-top: 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}

.raw-report summary {
  padding: 12px 14px;
  background: var(--navy3);
  font-size: 13px;
  color: var(--text3);
  cursor: pointer;
  font-family: var(--mono);
}

.raw-report summary:hover {
  color: var(--text2);
}

.raw-content {
  padding: 14px;
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text2);
  max-height: 300px;
  overflow-y: auto;
}

.raw-content h1 { font-size: 16px; color: var(--teal); margin: 0 0 12px 0; }
.raw-content h2 { font-size: 14px; color: var(--text); margin: 12px 0 8px 0; }
.raw-content h3 { font-size: 13px; color: var(--text2); margin: 8px 0 6px 0; }
.raw-content ul, .raw-content ol { padding-left: 20px; margin: 6px 0; }
.raw-content li { margin: 4px 0; }
.raw-content p { margin: 6px 0; }
.raw-content strong { color: var(--teal); }</style>