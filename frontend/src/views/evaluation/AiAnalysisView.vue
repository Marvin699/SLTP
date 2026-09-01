<template>
  <div class="ai-analysis-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="header-title">AI助教 · 方案点评</h1>
        <p class="header-sub">AI提取关键词 + 智能风险识别</p>
      </div>
      <div class="header-right">
        <el-radio-group v-model="mode" size="small" class="mode-switch">
          <el-radio-button value="demo">演示数据</el-radio-button>
          <el-radio-button value="real">真实方案</el-radio-button>
        </el-radio-group>
        <el-button class="back-btn" @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 返回首页
        </el-button>
      </div>
    </div>

    <!-- 真实方案模式：方案选择器 -->
    <div class="plan-picker" v-if="mode === 'real'">
      <span class="pp-label">方案对比：</span>
      <el-select v-model="planIdA" placeholder="选择方案 A" size="small" style="width: 220px" clearable>
        <el-option v-for="p in planOptions" :key="p.id" :label="planLabel(p)" :value="p.id" :disabled="p.id === planIdB" />
      </el-select>
      <span class="pp-vs">VS</span>
      <el-select v-model="planIdB" placeholder="选择方案 B（可选）" size="small" style="width: 220px" clearable>
        <el-option v-for="p in planOptions" :key="p.id" :label="planLabel(p)" :value="p.id" :disabled="p.id === planIdA" />
      </el-select>
      <el-button type="primary" size="small" :loading="loadingComment" :disabled="!planIdA && !planIdB" @click="loadComment(true)">
        生成AI点评
      </el-button>
      <el-tag v-if="commentSource === 'rule'" type="warning" size="small">AI模型繁忙，当前为规则点评</el-tag>
      <span v-if="!planOptions.length && !plansLoading" class="pp-empty">暂无课前方案，请学生先在课前生成方案</span>
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
          <!-- 左右双栏词云 -->
          <div class="cloud-columns">
            <!-- 左栏（橙色） -->
            <div class="cloud-col cloud-col-orange">
              <div class="col-header">
                <span class="col-dot dot-orange"></span>
                <span class="col-name">{{ nameB }}</span>
              </div>
              <div class="col-keywords">
                <span v-for="kw in keywordsB" :key="kw.text"
                  class="keyword-pill pill-orange"
                  :class="getKwSizeClass(kw.weight)">
                  {{ kw.text }}
                </span>
              </div>
            </div>
            <!-- 分割线 -->
            <div class="cloud-divider"></div>
            <!-- 右栏（蓝色） -->
            <div class="cloud-col cloud-col-blue">
              <div class="col-header">
                <span class="col-dot dot-blue"></span>
                <span class="col-name">{{ nameA }}</span>
              </div>
              <div class="col-keywords">
                <span v-for="kw in keywordsA" :key="kw.text"
                  class="keyword-pill pill-blue"
                  :class="getKwSizeClass(kw.weight)">
                  {{ kw.text }}
                </span>
              </div>
            </div>
          </div>
          <!-- 底部分析结论 -->
          <div class="cloud-conclusion">
            <div class="conclusion-row">
              <span class="conclusion-label orange">{{ nameB }}：</span>
              <span class="conclusion-text">{{ conclusionB.text }}</span>
              <span class="conclusion-tag tag-orange-light">{{ conclusionB.highlight }}</span>
            </div>
            <div class="conclusion-row">
              <span class="conclusion-label blue">{{ nameA }}：</span>
              <span class="conclusion-text">{{ conclusionA.text }}</span>
              <span class="conclusion-tag tag-blue-light">{{ conclusionA.highlight }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：潜在风险提示 -->
      <div class="panel risk-panel">
        <div class="panel-header">
          <span class="panel-icon">⚠️</span>
          <span class="panel-title">潜在风险提示</span>
          <span class="risk-count-badge">{{ riskAlerts.length }} 条</span>
        </div>
        <div class="panel-body">
          <!-- 方案A -->
          <div class="risk-group-section">
            <div class="risk-group-title grp-blue">{{ nameA }}</div>
            <div v-for="(risk, i) in risksA" :key="'a-' + i" class="risk-item">
              <div class="risk-top">
                <span class="risk-level" :class="'level-' + risk.level">{{ risk.levelLabel }}</span>
              </div>
              <div class="risk-desc">{{ risk.description }}</div>
            </div>
          </div>
          <!-- 方案B -->
          <div class="risk-group-section">
            <div class="risk-group-title grp-orange">{{ nameB }}</div>
            <div v-for="(risk, i) in risksB" :key="'b-' + i" class="risk-item">
              <div class="risk-top">
                <span class="risk-level" :class="'level-' + risk.level">{{ risk.levelLabel }}</span>
              </div>
              <div class="risk-desc">{{ risk.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：综合点评 -->
    <div class="bottom-summary">
      <div class="summary-card card-blue">
        <div class="sc-top">
          <span class="sc-rank">#{{ sumA.rank ?? '-' }}</span>
          <span class="sc-name">{{ nameA }}</span>
        </div>
        <div class="sc-body">
          <div v-for="t in sumA.tags" :key="t" class="sc-tag">{{ t }}</div>
        </div>
        <div class="sc-comment">{{ sumA.comment }}</div>
      </div>
      <div class="summary-card card-orange" v-if="sumB">
        <div class="sc-top">
          <span class="sc-rank">#{{ sumB.rank ?? '-' }}</span>
          <span class="sc-name">{{ nameB }}</span>
        </div>
        <div class="sc-body">
          <div v-for="t in sumB.tags" :key="t" class="sc-tag">{{ t }}</div>
        </div>
        <div class="sc-comment">{{ sumB.comment }}</div>
      </div>
    </div>

    <!-- 底部说明 -->
    <div class="footer-note">
      <div class="footer-main">AI辅助分析，最终决策以教师及企业导师评价为准</div>
      <div class="footer-sub">数据来源：课堂实时评价系统</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { fetchPlanLibrary, fetchAiComment } from '@/api/evaluation'

const route = useRoute()
const router = useRouter()

// ─── 模式：demo=比赛演示数据（保留） | real=真实方案数据（正式使用） ───
const mode = ref('demo')

const groupA = computed(() => route.query.groupA || '揽星组')
const groupB = computed(() => route.query.groupB || '御风组')

function getKwSizeClass(weight) {
  if (weight >= 85) return 'kw-lg'
  if (weight >= 70) return 'kw-md'
  return 'kw-sm'
}

// ═══ 演示模式静态数据（比赛/展览用，保留） ═══
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

function demoKeywords(groupName) {
  return (wordCloudData[groupName] || []).slice().sort((a, b) => b.weight - a.weight)
}

function getTop3(groupName) {
  return (wordCloudData[groupName] || []).slice(0, 3).map(w => w.text).join('、')
}

// ═══ 真实方案模式 ═══
const planOptions = ref([])
const plansLoading = ref(false)
const planIdA = ref(null)
const planIdB = ref(null)
const commentData = ref(null)
const commentSource = ref(null)
const loadingComment = ref(false)

function planLabel(p) {
  const name = p.student_name || `方案#${p.id}`
  const dist = p.total_distance != null ? ` ${p.total_distance.toFixed?.(1) ?? p.total_distance}km` : ''
  const chosen = p.is_chosen ? ' [已择优]' : ''
  return `${name} - ${p.drone_count ?? '?'}机${p.total_trips ?? '?'}趟${dist}${chosen}`
}

async function loadPlanOptions() {
  plansLoading.value = true
  try {
    const res = await fetchPlanLibrary({ limit: 50 })
    planOptions.value = res.data?.plans || []
  } catch {
    planOptions.value = []
  } finally {
    plansLoading.value = false
  }
}

async function loadComment(manual = false) {
  const ids = [planIdA.value, planIdB.value].filter(Boolean)
  if (!ids.length) return
  loadingComment.value = true
  try {
    const res = await fetchAiComment(ids)
    commentData.value = res.data || null
    commentSource.value = res.data?.source || null
  } catch {
    if (manual) ElMessage.error('AI点评生成失败，请稍后重试')
    commentData.value = null
    commentSource.value = null
  } finally {
    loadingComment.value = false
  }
}

// 切换方案自动重新生成
watch([planIdA, planIdB], () => loadComment(false))

// 切到真实模式时加载方案列表
watch(mode, (m) => {
  if (m === 'real' && !planOptions.value.length) loadPlanOptions()
})

onMounted(() => {
  if (mode.value === 'real') loadPlanOptions()
})

// ─── 统一的数据出口（模板统一读取，双模式自适应） ───
const RISK_LABELS = { high: '高风险', medium: '中风险', low: '低风险' }

const realA = computed(() => commentData.value?.groups?.find(g => g.plan_id === planIdA.value) || null)
const realB = computed(() => commentData.value?.groups?.find(g => g.plan_id === planIdB.value) || null)

const nameA = computed(() => mode.value === 'demo' ? groupA.value : (realA.value?.name || '方案A'))
const nameB = computed(() => mode.value === 'demo' ? groupB.value : (realB.value?.name || '方案B'))

const keywordsA = computed(() =>
  mode.value === 'demo' ? demoKeywords(groupA.value) : (realA.value?.keywords || []))
const keywordsB = computed(() =>
  mode.value === 'demo' ? demoKeywords(groupB.value) : (realB.value?.keywords || []))

const conclusionA = computed(() => mode.value === 'demo'
  ? { text: `高频出现"${getTop3(groupA.value)}"`, highlight: '胜在技术深度' }
  : { text: realA.value?.conclusion || '选择方案后自动生成', highlight: realA.value?.highlight || '—' })
const conclusionB = computed(() => mode.value === 'demo'
  ? { text: `高频出现"${getTop3(groupB.value)}"`, highlight: '胜在系统整合' }
  : { text: realB.value?.conclusion || '选择方案后自动生成', highlight: realB.value?.highlight || '—' })

function mapRisks(list) {
  return (list || []).map(r => ({ ...r, levelLabel: RISK_LABELS[r.level] || '风险' }))
}

const risksA = computed(() => mode.value === 'demo'
  ? [{ group: groupA.value, level: 'high', levelLabel: '高风险', description: `揽星组冗余设计导致时效偏低` },
     { group: groupA.value, level: 'low', levelLabel: '低风险', description: `索降和吊装模式物资损坏概率缺少量化依据，仅有定性判断` }]
  : mapRisks(realA.value?.risks))
const risksB = computed(() => mode.value === 'demo'
  ? [{ group: groupB.value, level: 'high', levelLabel: '高风险', description: `极限压缩时间带来安全裕度不足` },
     { group: groupB.value, level: 'medium', levelLabel: '中风险', description: `雅力村索降方案未考虑风速超过安全阈值的应对措施` }]
  : mapRisks(realB.value?.risks))

const riskAlerts = computed(() => [...risksA.value, ...risksB.value])

const sumA = computed(() => mode.value === 'demo'
  ? { rank: 1, tags: ['技术深度', '安全冗余量化', '动态航程约束建模'], comment: '方案数学建模扎实，数据支撑充分；但总耗时偏长，实际应急中需再压缩' }
  : { rank: realA.value?.rank, tags: realA.value?.tags || [], comment: realA.value?.comment || '生成AI点评后展示' })
const sumB = computed(() => mode.value === 'demo'
  ? { rank: 2, tags: ['系统整合', '三层冗余备份', '多机协同设计'], comment: '协同设计有前瞻性，效率优先策略清晰；但数据口径必须统一，这是企业汇报基本要求' }
  : (realB.value ? { rank: realB.value?.rank, tags: realB.value?.tags || [], comment: realB.value?.comment || '' } : null))

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
  padding: clamp(20px, 1.4vw, 40px) clamp(24px, 1.8vw, 56px) clamp(24px, 1.6vw, 48px);
  display: flex;
  flex-direction: column;
  gap: clamp(14px, 1.1vw, 30px);
}

/* ===== 顶部 ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: clamp(4px, 0.4vw, 12px);
}
.header-title {
  font-size: clamp(22px, 2vw, 48px);
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: 0.5px;
}
.header-sub {
  font-size: clamp(13px, 1.1vw, 24px);
  color: #64748b;
  margin: clamp(2px, 0.2vw, 6px) 0 0;
}
.back-btn {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  color: #c0c8d4;
  border-radius: clamp(6px, 0.5vw, 12px);
  font-size: clamp(13px, 1.1vw, 24px);
  padding: clamp(6px, 0.5vw, 14px) clamp(14px, 1.1vw, 28px);
  height: auto !important;
}
.back-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
  border-color: rgba(255,255,255,0.2);
}

/* ===== 顶部右侧：模式切换 ===== */
.header-right {
  display: flex;
  align-items: center;
  gap: clamp(8px, 0.7vw, 18px);
}
.mode-switch :deep(.el-radio-button__inner) {
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.1);
  color: #c0c8d4;
}
.mode-switch :deep(.el-radio-button__original-checked .el-radio-button__inner),
.mode-switch :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: rgba(59,130,246,0.35);
  border-color: rgba(59,130,246,0.5);
  color: #fff;
}

/* ===== 真实方案选择器 ===== */
.plan-picker {
  display: flex;
  align-items: center;
  gap: clamp(8px, 0.7vw, 16px);
  background: rgba(15, 25, 50, 0.8);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: clamp(8px, 0.7vw, 16px);
  padding: clamp(8px, 0.7vw, 16px) clamp(12px, 1vw, 24px);
}
.pp-label { color: #64748b; font-size: clamp(13px, 1.1vw, 22px); }
.pp-vs { color: #f59e0b; font-weight: 700; font-size: clamp(13px, 1.2vw, 24px); }
.pp-empty { color: #64748b; font-size: clamp(12px, 1vw, 20px); }
.plan-picker :deep(.el-select__wrapper),
.plan-picker :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.05);
}

/* ===== 主内容 ===== */
.main-content {
  display: flex;
  gap: clamp(12px, 1.1vw, 30px);
  flex: 1;
}

/* 面板通用 */
.panel {
  background: rgba(15, 25, 50, 0.8);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: clamp(10px, 0.9vw, 22px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex;
  align-items: center;
  gap: clamp(6px, 0.6vw, 16px);
  padding: clamp(12px, 1.1vw, 28px) clamp(16px, 1.6vw, 40px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.panel-icon { font-size: clamp(16px, 1.6vw, 32px); }
.panel-title { font-size: clamp(15px, 1.4vw, 30px); font-weight: 600; color: #e2e8f0; letter-spacing: 0.5px; }

.risk-count-badge {
  margin-left: auto;
  background: rgba(239,68,68,0.18);
  color: #f87171;
  font-size: clamp(12px, 1vw, 22px);
  font-weight: 600;
  padding: clamp(2px, 0.2vw, 6px) clamp(8px, 0.8vw, 20px);
  border-radius: clamp(8px, 0.7vw, 18px);
}
.panel-body {
  flex: 1;
  padding: clamp(14px, 1.4vw, 32px) clamp(16px, 1.6vw, 40px);
  overflow-y: auto;
}

/* ===== 词云面板 ===== */
.wordcloud-panel { flex: 1.3; }

/* 双栏词云 */
.cloud-columns {
  display: flex;
  gap: 0;
  margin-bottom: clamp(12px, 1vw, 26px);
  background: linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.15) 100%);
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: clamp(10px, 0.9vw, 22px);
  overflow: hidden;
  min-height: clamp(200px, 20vw, 420px);
}
.cloud-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: clamp(14px, 1.2vw, 30px) clamp(12px, 1vw, 24px);
}
.cloud-col-orange {
  background: radial-gradient(circle at 30% 50%, rgba(245,158,11,0.08) 0%, transparent 70%);
}
.cloud-col-blue {
  background: radial-gradient(circle at 70% 50%, rgba(59,130,246,0.08) 0%, transparent 70%);
}
.cloud-divider {
  width: 1px;
  background: linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.1) 20%, rgba(255,255,255,0.1) 80%, transparent 100%);
  flex-shrink: 0;
}
.col-header {
  display: flex;
  align-items: center;
  gap: clamp(6px, 0.6vw, 16px);
  margin-bottom: clamp(10px, 0.9vw, 22px);
}
.col-dot {
  width: clamp(6px, 0.6vw, 14px);
  height: clamp(6px, 0.6vw, 14px);
  border-radius: 50%;
}
.dot-orange { background: #f59e0b; box-shadow: 0 0 clamp(6px, 0.6vw, 14px) rgba(245,158,11,0.5); }
.dot-blue { background: #3b82f6; box-shadow: 0 0 clamp(6px, 0.6vw, 14px) rgba(59,130,246,0.5); }
.col-name {
  font-size: clamp(14px, 1.4vw, 28px);
  font-weight: 700;
  letter-spacing: 0.5px;
}
.cloud-col-orange .col-name { color: #fbbf24; }
.cloud-col-blue .col-name { color: #60a5fa; }

.col-keywords {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(6px, 0.6vw, 14px);
  justify-items: center;
}
.keyword-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  border-radius: clamp(5px, 0.5vw, 12px);
  font-weight: 700;
  line-height: 1.4;
  cursor: default;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}
.keyword-pill.kw-lg { font-size: clamp(16px, 1.7vw, 34px); padding: clamp(6px, 0.6vw, 16px) clamp(2px, 0.2vw, 6px); letter-spacing: 1px; }
.keyword-pill.kw-md { font-size: clamp(13px, 1.3vw, 26px); padding: clamp(5px, 0.5vw, 12px) clamp(2px, 0.2vw, 6px); letter-spacing: 0.5px; }
.keyword-pill.kw-sm { font-size: clamp(12px, 1.1vw, 22px); padding: clamp(4px, 0.4vw, 10px) clamp(2px, 0.2vw, 6px); letter-spacing: 0; }
.keyword-pill:hover {
  transform: translateY(-1px);
}
.pill-blue {
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.25);
}
.pill-blue:hover {
  background: rgba(59, 130, 246, 0.22);
  border-color: rgba(59, 130, 246, 0.5);
  color: #93bbfd;
}
.pill-orange {
  background: rgba(245, 158, 11, 0.12);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.25);
}
.pill-orange:hover {
  background: rgba(245, 158, 11, 0.22);
  border-color: rgba(245, 158, 11, 0.5);
  color: #fcd34d;
}

/* 底部结论 */
.cloud-conclusion {
  display: flex;
  flex-direction: column;
  gap: clamp(6px, 0.6vw, 14px);
}
.conclusion-row {
  display: flex;
  align-items: center;
  gap: clamp(4px, 0.4vw, 10px);
  font-size: clamp(13px, 1.2vw, 26px);
  flex-wrap: wrap;
}
.conclusion-label { font-weight: 700; }
.conclusion-label.blue { color: #60a5fa; }
.conclusion-label.orange { color: #fbbf24; }
.conclusion-text { color: #c0c8d4; }
.conclusion-tag {
  padding: clamp(2px, 0.2vw, 6px) clamp(6px, 0.6vw, 16px);
  border-radius: clamp(3px, 0.3vw, 8px);
  font-size: clamp(11px, 1vw, 20px);
  font-weight: 600;
}
.tag-blue-light { background: rgba(59,130,246,0.15); color: #60a5fa; }
.tag-orange-light { background: rgba(245,158,11,0.15); color: #fbbf24; }

/* ===== 风险面板 ===== */
.risk-panel { flex: 0.7; }

.risk-group-section {
  margin-bottom: clamp(12px, 1vw, 26px);
}
.risk-group-section:last-child {
  margin-bottom: 0;
}
.risk-group-title {
  font-size: clamp(14px, 1.4vw, 28px);
  font-weight: 700;
  padding: clamp(6px, 0.7vw, 16px) clamp(12px, 1.2vw, 28px);
  border-radius: clamp(6px, 0.6vw, 14px);
  margin-bottom: clamp(8px, 0.8vw, 18px);
  color: #fff;
  letter-spacing: 0.5px;
}
.risk-group-title.grp-blue { background: linear-gradient(90deg, rgba(59,130,246,0.35) 0%, rgba(59,130,246,0.1) 100%); border-left: clamp(3px, 0.3vw, 8px) solid #3b82f6; }
.risk-group-title.grp-orange { background: linear-gradient(90deg, rgba(245,158,11,0.35) 0%, rgba(245,158,11,0.1) 100%); border-left: clamp(3px, 0.3vw, 8px) solid #f59e0b; }

.risk-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: clamp(6px, 0.6vw, 14px);
  padding: clamp(10px, 1vw, 22px) clamp(12px, 1.2vw, 26px);
  margin-bottom: clamp(6px, 0.6vw, 14px);
}
.risk-item:last-child { margin-bottom: 0; }
.risk-top {
  display: flex;
  align-items: center;
  gap: clamp(6px, 0.6vw, 14px);
  margin-bottom: clamp(6px, 0.6vw, 14px);
}
.risk-level {
  padding: clamp(2px, 0.2vw, 6px) clamp(8px, 0.8vw, 18px);
  border-radius: clamp(3px, 0.3vw, 8px);
  font-size: clamp(12px, 1.1vw, 22px);
  font-weight: 700;
}
.level-high { background: rgba(239,68,68,0.18); color: #f87171; }
.level-medium { background: rgba(245,158,11,0.18); color: #fbbf24; }
.level-low { background: rgba(34,197,94,0.18); color: #4ade80; }

.risk-desc {
  font-size: clamp(13px, 1.2vw, 26px);
  line-height: 1.7;
  color: #c0c8d4;
}

/* ===== 底部总分 ===== */
.bottom-summary {
  display: flex;
  gap: clamp(12px, 1.1vw, 28px);
}
.summary-card {
  flex: 1;
  border-radius: clamp(10px, 0.9vw, 22px);
  padding: clamp(14px, 1.2vw, 30px) clamp(16px, 1.4vw, 34px);
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
  gap: clamp(6px, 0.6vw, 14px);
  margin-bottom: clamp(8px, 0.8vw, 18px);
}
.sc-rank {
  font-size: clamp(13px, 1.2vw, 24px);
  font-weight: 700;
  color: #64748b;
}
.sc-name {
  font-size: clamp(15px, 1.4vw, 30px);
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}
.sc-score {
  font-size: clamp(22px, 2.2vw, 48px);
  font-weight: 800;
  margin-left: auto;
}
.card-blue .sc-score { color: #60a5fa; }
.card-orange .sc-score { color: #fbbf24; }
.sc-score small { font-size: clamp(12px, 1vw, 20px); font-weight: 400; opacity: 0.7; margin-left: 2px; }

.sc-body {
  display: flex;
  flex-wrap: wrap;
  gap: clamp(4px, 0.4vw, 10px);
  margin-bottom: clamp(8px, 0.8vw, 18px);
}
.sc-tag {
  padding: clamp(2px, 0.2vw, 6px) clamp(8px, 0.8vw, 18px);
  border-radius: clamp(4px, 0.4vw, 10px);
  font-size: clamp(11px, 1vw, 20px);
  font-weight: 600;
}
.card-blue .sc-tag { background: rgba(59,130,246,0.15); color: #60a5fa; }
.card-orange .sc-tag { background: rgba(245,158,11,0.15); color: #fbbf24; }

.sc-comment {
  font-size: clamp(13px, 1.2vw, 26px);
  color: #c0c8d4;
  line-height: 1.6;
}

/* ===== 底部说明 ===== */
.footer-note {
  text-align: center;
  padding: clamp(10px, 0.9vw, 22px) 0 clamp(2px, 0.2vw, 6px);
  border-top: 1px solid rgba(255,255,255,0.06);
  margin-top: clamp(6px, 0.6vw, 14px);
}
.footer-main {
  font-size: clamp(12px, 1.1vw, 22px);
  color: rgba(255,255,255,0.5);
  margin-bottom: clamp(2px, 0.2vw, 6px);
}
.footer-sub {
  font-size: clamp(11px, 1vw, 20px);
  color: rgba(255,255,255,0.3);
}

/* ===== 语音播报按钮 ===== */
.speak-btn {
  margin-left: auto;
  background: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.3);
  color: #7dd3fc;
  border-radius: 6px;
  font-size: clamp(11px, 1vw, 20px);
  font-weight: 600;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.speak-btn:hover {
  background: rgba(14, 165, 233, 0.25);
  border-color: #0ea5e9;
  color: #bae6fd;
}
.speak-btn.speaking {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #6ee7b7;
  animation: speakPulse 1.2s ease-in-out infinite;
}
@keyframes speakPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
}

.speak-btn-lg {
  font-size: clamp(12px, 1.1vw, 22px);
  padding: 5px 14px;
  border-radius: 8px;
  margin-left: auto;
}
</style>
