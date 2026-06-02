<template>
  <div class="ai-analysis-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="header-title">AI助教 · 方案点评</h1>
        <p class="header-sub">AI提取关键词 + 智能风险识别</p>
      </div>
      <el-button class="back-btn" @click="goBack">
        <el-icon><ArrowLeft /></el-icon> 返回评分页面
      </el-button>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：方案亮点词云 -->
      <div class="panel wordcloud-panel">
        <div class="panel-header">
          <span class="panel-icon">☁️</span>
          <span class="panel-title">方案亮点词云</span>
        </div>
        <div class="panel-body">
          <!-- 小组标签 -->
          <div class="group-tags">
            <span class="group-tag tag-blue">{{ groupA }}</span>
            <span class="group-tag tag-orange">{{ groupB }}</span>
          </div>
          <!-- 关键词标签云 -->
          <div class="keywords-cloud">
            <span v-for="kw in sortedKeywords" :key="kw.text"
              class="keyword-pill"
              :class="kw.group === 'A' ? 'pill-blue' : 'pill-orange'"
              :style="{ fontSize: getKwSize(kw.weight) + 'px' }">
              {{ kw.text }}
            </span>
          </div>
          <!-- 底部分析结论 -->
          <div class="cloud-conclusion">
            <div class="conclusion-row">
              <span class="conclusion-label blue">{{ groupA }}：</span>
              <span class="conclusion-text">高频出现"{{ getTop3(groupA) }}"</span>
              <span class="conclusion-tag tag-blue-light">胜在技术深度</span>
            </div>
            <div class="conclusion-row">
              <span class="conclusion-label orange">{{ groupB }}：</span>
              <span class="conclusion-text">高频出现"{{ getTop3(groupB) }}"</span>
              <span class="conclusion-tag tag-orange-light">胜在系统整合</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：潜在风险提示 -->
      <div class="panel risk-panel">
        <div class="panel-header">
          <span class="panel-icon">⚠️</span>
          <span class="panel-title">潜在风险提示</span>
        </div>
        <div class="panel-body">
          <div v-for="(risk, i) in riskAlerts" :key="i" class="risk-item">
            <div class="risk-top">
              <span class="risk-level" :class="'level-' + risk.level">{{ risk.levelLabel }}</span>
              <span class="risk-group" :class="risk.group === groupA ? 'grp-blue' : 'grp-orange'">{{ risk.group }}</span>
            </div>
            <div class="risk-desc">{{ risk.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：综合点评 -->
    <div class="bottom-summary">
      <div class="summary-card card-blue">
        <div class="sc-top">
          <span class="sc-rank">#1</span>
          <span class="sc-name">{{ groupA }}</span>
          <span class="sc-score">{{ groupAScore }}<small>分</small></span>
        </div>
        <div class="sc-body">
          <div class="sc-tag">技术深度</div>
          <div class="sc-tag">安全冗余量化</div>
          <div class="sc-tag">动态航程约束建模</div>
        </div>
        <div class="sc-comment">方案数学建模扎实，数据支撑充分；但总耗时偏长，实际应急中需再压缩</div>
      </div>
      <div class="summary-card card-orange">
        <div class="sc-top">
          <span class="sc-rank">#2</span>
          <span class="sc-name">{{ groupB }}</span>
          <span class="sc-score">{{ groupBScore }}<small>分</small></span>
        </div>
        <div class="sc-body">
          <div class="sc-tag">系统整合</div>
          <div class="sc-tag">三层冗余备份</div>
          <div class="sc-tag">多机协同设计</div>
        </div>
        <div class="sc-comment">协同设计有前瞻性，效率优先策略清晰；但数据口径必须统一，这是企业汇报基本要求</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const groupA = computed(() => route.query.groupA || '揽星组')
const groupB = computed(() => route.query.groupB || '御风组')
const groupAScore = 92
const groupBScore = 91

// 关键词数据
const wordCloudData = {
  '揽星组': [
    { text: '非线性', weight: 95 },
    { text: '冗余', weight: 88 },
    { text: '验证', weight: 82 },
    { text: '动态航程', weight: 90 },
    { text: '安全冗余', weight: 78 },
    { text: '遗传算法', weight: 75 },
    { text: '载重', weight: 70 },
    { text: '索降', weight: 60 },
    { text: '避障', weight: 65 },
    { text: '量化建模', weight: 85 },
    { text: '连通性', weight: 55 },
    { text: '多机协同', weight: 72 },
    { text: '生命优先', weight: 68 },
    { text: '分级配送', weight: 58 },
    { text: '仿真', weight: 50 },
  ],
  '御风组': [
    { text: '协同', weight: 92 },
    { text: '优先级', weight: 88 },
    { text: '快速恢复', weight: 85 },
    { text: '效率', weight: 80 },
    { text: '闪电波次', weight: 78 },
    { text: '多机协同', weight: 82 },
    { text: '高度层错配', weight: 75 },
    { text: '时间错峰', weight: 70 },
    { text: '一机双投', weight: 65 },
    { text: '备用制冷', weight: 68 },
    { text: '冲突避让', weight: 72 },
    { text: '重载波次', weight: 60 },
    { text: '航线合并', weight: 55 },
    { text: '三层冗余', weight: 88 },
    { text: '智能调度', weight: 62 },
  ],
}

const sortedKeywords = computed(() => {
  const listA = (wordCloudData[groupA.value] || []).map(w => ({ ...w, group: 'A' }))
  const listB = (wordCloudData[groupB.value] || []).map(w => ({ ...w, group: 'B' }))
  return [...listA, ...listB].sort((a, b) => b.weight - a.weight)
})

function getKwSize(weight) {
  return Math.round(12 + (weight / 100) * 14)
}

function getTop3(groupName) {
  return (wordCloudData[groupName] || []).slice(0, 3).map(w => w.text).join('、')
}

// 风险数据
const riskAlerts = computed(() => [
  {
    group: groupA.value,
    level: 'medium',
    levelLabel: '中风险',
    description: `"68.5小时总耗时"与"2.5小时并行作业"逻辑一致性存疑，建议澄清计算口径`,
  },
  {
    group: groupB.value,
    level: 'high',
    levelLabel: '高风险',
    description: `"65小时"总耗时与"150分钟"单批次用时数据口径不一致，需组内校准`,
  },
  {
    group: groupA.value,
    level: 'low',
    levelLabel: '低风险',
    description: `索降和吊装模式物资损坏概率缺少量化依据，仅有定性判断`,
  },
  {
    group: groupB.value,
    level: 'medium',
    levelLabel: '中风险',
    description: `雅力村索降方案未考虑风速超过安全阈值的应对措施`,
  },
])

function goBack() {
  const sectionId = route.params.sectionId
  router.push({ path: `/evaluation/section/${sectionId}`, query: { tab: 'ai' } })
}
</script>

<style scoped>
.ai-analysis-page {
  min-height: 100vh;
  background: #0b1120;
  color: #e2e8f0;
  padding: 28px 32px 32px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* ===== 顶部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}
.header-sub {
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0;
}
.back-btn {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  color: #c0c8d4;
  border-radius: 8px;
}
.back-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
  border-color: rgba(255,255,255,0.2);
}

/* ===== 主内容 ===== */
.main-content {
  display: flex;
  gap: 20px;
  flex: 1;
}

/* 面板通用 */
.panel {
  background: rgba(15, 25, 50, 0.8);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 22px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.panel-icon { font-size: 18px; }
.panel-title { font-size: 15px; font-weight: 600; color: #e2e8f0; }
.panel-body {
  flex: 1;
  padding: 20px 22px;
  overflow-y: auto;
}

/* ===== 词云面板 ===== */
.wordcloud-panel { flex: 1.3; }

.group-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}
.group-tag {
  padding: 4px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}
.tag-blue { background: #3b82f6; }
.tag-orange { background: #f59e0b; }

/* 关键词标签云 */
.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 24px;
  background:
    radial-gradient(circle at 20% 30%, rgba(59,130,246,0.06) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(245,158,11,0.06) 0%, transparent 50%),
    linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.15) 100%);
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 12px;
  min-height: 240px;
  align-content: center;
  justify-content: center;
  margin-bottom: 18px;
  position: relative;
  overflow: hidden;
}
/* 背景网格线 */
.keywords-cloud::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none;
}
.keyword-pill {
  display: inline-block;
  padding: 6px 18px;
  border-radius: 4px;
  font-weight: 600;
  line-height: 1.4;
  cursor: default;
  transition: all 0.2s ease;
  white-space: nowrap;
  position: relative;
  z-index: 1;
}
.keyword-pill:hover {
  transform: translateY(-2px) scale(1.05);
}
.pill-blue {
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.15), inset 0 0 12px rgba(59, 130, 246, 0.05);
}
.pill-blue:hover {
  background: rgba(59, 130, 246, 0.22);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.3), 0 4px 20px rgba(59, 130, 246, 0.2);
  color: #93bbfd;
}
.pill-orange {
  background: rgba(245, 158, 11, 0.12);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.15), inset 0 0 12px rgba(245, 158, 11, 0.05);
}
.pill-orange:hover {
  background: rgba(245, 158, 11, 0.22);
  border-color: rgba(245, 158, 11, 0.5);
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.3), 0 4px 20px rgba(245, 158, 11, 0.2);
  color: #fcd34d;
}

/* 底部结论 */
.cloud-conclusion {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.conclusion-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  flex-wrap: wrap;
}
.conclusion-label { font-weight: 700; }
.conclusion-label.blue { color: #60a5fa; }
.conclusion-label.orange { color: #fbbf24; }
.conclusion-text { color: #c0c8d4; }
.conclusion-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.tag-blue-light { background: rgba(59,130,246,0.15); color: #60a5fa; }
.tag-orange-light { background: rgba(245,158,11,0.15); color: #fbbf24; }

/* ===== 风险面板 ===== */
.risk-panel { flex: 0.7; }

.risk-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 10px;
}
.risk-item:last-child { margin-bottom: 0; }
.risk-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.risk-level {
  padding: 1px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 700;
}
.level-high { background: rgba(239,68,68,0.18); color: #f87171; }
.level-medium { background: rgba(245,158,11,0.18); color: #fbbf24; }
.level-low { background: rgba(34,197,94,0.18); color: #4ade80; }

.risk-group {
  padding: 1px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}
.grp-blue { background: #3b82f6; }
.grp-orange { background: #f59e0b; }

.risk-desc {
  font-size: 13px;
  line-height: 1.6;
  color: #c0c8d4;
}

/* ===== 底部总分 ===== */
.bottom-summary {
  display: flex;
  gap: 20px;
}
.summary-card {
  flex: 1;
  border-radius: 14px;
  padding: 20px 24px;
  border: 1px solid rgba(255,255,255,0.06);
}
.card-blue {
  background: linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(15,25,50,0.8) 100%);
  border-color: rgba(59,130,246,0.2);
}
.card-orange {
  background: linear-gradient(135deg, rgba(245,158,11,0.12) 0%, rgba(15,25,50,0.8) 100%);
  border-color: rgba(245,158,11,0.2);
}
.sc-top {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
}
.sc-rank {
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
}
.sc-name {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}
.sc-score {
  font-size: 28px;
  font-weight: 800;
  margin-left: auto;
}
.card-blue .sc-score { color: #60a5fa; }
.card-orange .sc-score { color: #fbbf24; }
.sc-score small { font-size: 14px; font-weight: 400; opacity: 0.7; margin-left: 2px; }

.sc-body {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}
.sc-tag {
  padding: 3px 10px;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
}
.card-blue .sc-tag { background: rgba(59,130,246,0.15); color: #60a5fa; }
.card-orange .sc-tag { background: rgba(245,158,11,0.15); color: #fbbf24; }

.sc-comment {
  font-size: 13px;
  color: #c0c8d4;
  line-height: 1.6;
}
</style>
