<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getDashboard,
  getStudentVerifications,
  getStudentDebateSessions,
  getDebateReplay,
  sendTeacherNote,
} from '@/api/pathPlanning/teacher'

// ─── 总览 ───
const loading = ref(false)
const students = ref([])
const summary = ref({})
const selected = ref(null)            // 当前选中学生
const keyword = ref('')               // 搜索过滤

async function loadDashboard() {
  loading.value = true
  try {
    const res = await getDashboard()
    students.value = res.data.students || []
    summary.value = res.data.summary || {}
    // 默认选中第一个学生，右侧即刻有内容
    if (students.value.length && !selected.value) selectStudent(students.value[0])
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

const filteredStudents = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return students.value
  return students.value.filter(s =>
    [s.username, s.student_no, s.class_name, s.group_no]
      .some(v => (v || '').toLowerCase().includes(kw))
  )
})

function selectStudent(s) {
  selected.value = s
  replay.value = null
  if (activeTab.value === 'debate') loadDebateSessions()
  else loadVerifications()
}

// ─── Tab 切换时按需加载 ───
const activeTab = ref('verify')
watch(activeTab, (t) => {
  if (!selected.value) return
  if (t === 'verify') loadVerifications()
  else if (t === 'debate') { loadDebateSessions(); replay.value = null }
})

// ─── 核验记录 ───
const verLoading = ref(false)
const verifications = ref([])

async function loadVerifications() {
  if (!selected.value) return
  verLoading.value = true
  try {
    const res = await getStudentVerifications(selected.value.user_id)
    verifications.value = res.data.records || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    verLoading.value = false
  }
}

/** 从核验清单里抽取差异项展示 */
function mismatchesOf(checklist) {
  const list = []
  for (const g of checklist || []) {
    for (const it of g.items) {
      if (it.mismatch) list.push({ group: g.group, metric: it.metric, reason: it.engine_reason })
    }
  }
  return list
}

function verdictType(v) {
  return v === '通过' ? 'success' : v === '需整改' ? 'danger' : 'warning'
}

// ─── 辩论回放 ───
const debLoading = ref(false)
const sessionsList = ref([])          // 当前学生的会话列表
const replay = ref(null)              // 当前回放的消息流
const replayLoading = ref(false)
const noteText = ref('')
const sendingNote = ref(false)

const STAGE_NAMES = { hypothesis: '假设提出', verify: '验证分析', rebut: '反驳交锋', rebuild: '重构优化', completed: '闭环完成' }

async function loadDebateSessions() {
  if (!selected.value) return
  debLoading.value = true
  try {
    const res = await getStudentDebateSessions(selected.value.user_id)
    sessionsList.value = res.data.sessions || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    debLoading.value = false
  }
}

async function openReplay(session) {
  replayLoading.value = true
  try {
    const res = await getDebateReplay(session.id)
    replay.value = res.data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    replayLoading.value = false
  }
}

/** 教师介入留言 */
async function submitNote() {
  if (!replay.value || !noteText.value.trim()) return
  const text = noteText.value.trim()
  sendingNote.value = true
  try {
    await sendTeacherNote(replay.value.session.id, text)
    ElMessage.success('留言已发送，学生端可见')
    noteText.value = ''
    // 把留言追加到当前回放末尾
    replay.value.messages.push({
      id: Date.now(), role: 'teacher',
      content: `👨‍🏫 教师介入：${text}`,
      stage: replay.value.session.stage,
      created_at: new Date().toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
    })
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    sendingNote.value = false
  }
}

const summaryCards = computed(() => [
  { label: '学生总数', value: summary.value.student_total ?? '-', icon: '👥' },
  { label: '已提交核验', value: `${summary.value.with_verification ?? '-'} 人`, icon: '✅' },
  { label: '已参与辩论', value: `${summary.value.with_debate ?? '-'} 人`, icon: '🎭' },
  { label: '班级平均核验分', value: summary.value.class_avg_score ?? '-', icon: '📊' },
])

onMounted(loadDashboard)
</script>

<template>
  <div class="page-container" v-loading="loading">
    <!-- 页头（对齐学生管理页） -->
    <div class="page-header">
      <div class="header-left">
        <h1>🛰️ 教学监控</h1>
        <span class="page-desc">跟踪全班学生的课前方案产出、合规核验质量与反向质询参与情况</span>
      </div>
      <div class="header-right">
        <el-button :loading="loading" @click="loadDashboard">🔄 刷新数据</el-button>
      </div>
    </div>

    <!-- 统计卡片（对齐 StudentManage stat-card 风格） -->
    <div class="stats-row">
      <div v-for="c in summaryCards" :key="c.label" class="stat-card">
        <span class="stat-icon">{{ c.icon }}</span>
        <div>
          <div class="stat-label">{{ c.label }}</div>
          <div class="stat-value">{{ c.value }}</div>
        </div>
      </div>
    </div>

    <!-- 主体两栏 -->
    <div class="monitor-body">
      <!-- 左：学生列表 -->
      <div class="panel">
        <div class="panel-head">
          <b>👥 学生列表</b>
          <el-input
            v-model="keyword"
            placeholder="搜索姓名 / 学号 / 小组"
            size="small"
            clearable
            style="width: 200px"
          />
        </div>
        <el-table
          :data="filteredStudents"
          size="small"
          highlight-current-row
          height="500px"
          class="dark-table"
          :header-cell-style="{ background: 'rgba(64, 158, 255, 0.1)', color: '#c0c8d4' }"
          @row-click="(row) => selectStudent(row)"
        >
          <el-table-column type="index" width="44" />
          <el-table-column prop="username" label="学生" min-width="80">
            <template #default="{ row }">
              <b>{{ row.username }}</b>
              <div class="cell-sub">{{ row.student_no || '-' }} · {{ row.class_name || '未分班' }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="group_no" label="小组" width="64" align="center" />
          <el-table-column label="产出" width="88" align="center">
            <template #header>方案/报告</template>
            <template #default="{ row }">
              <span>{{ row.plan_count }} / {{ row.report_count }}</span>
              <div class="cell-sub">方案 · 报告</div>
            </template>
          </el-table-column>
          <el-table-column label="核验" align="center" width="92">
            <template #default="{ row }">
              <template v-if="row.verification_count">
                <span :class="{ lowscore: (row.avg_verification_score ?? 0) < 60 }">{{ row.avg_verification_score }}分</span>
                <div class="cell-sub">{{ row.verification_count }}次 · 一致{{ row.avg_consistency }}%</div>
              </template>
              <span v-else class="dim">未开始</span>
            </template>
          </el-table-column>
          <el-table-column label="辩论" align="center" width="100">
            <template #default="{ row }">
              <template v-if="row.debate_session_count">
                <span>{{ row.debate_session_count }}场</span>
                <div class="cell-sub">{{ row.last_debate_at || '' }}</div>
              </template>
              <span v-else class="dim">未参与</span>
            </template>
          </el-table-column>
        </el-table>
        <p class="table-tip">点击行查看该生的学习轨迹详情</p>
      </div>

      <!-- 右：学习轨迹 -->
      <div class="panel detail-panel" :class="{ empty: !selected }">
        <div class="panel-head">
          <b>{{ selected ? `🔎 ${selected.username} 的学习轨迹` : '👆 请先在左侧选择一名学生' }}</b>
        </div>

        <template v-if="selected">
          <el-tabs v-model="activeTab" class="monitor-tabs">
            <!-- ════ 核验记录 ════ -->
            <el-tab-pane label="✅ 合规核验" name="verify">
              <div v-loading="verLoading" class="tab-body">
                <el-empty v-if="!verifications.length" description="该学生还没有核验记录" :image-size="70" />
                <div v-else class="ver-list">
                  <div v-for="v in verifications" :key="v.id" class="ver-item">
                    <div class="ver-title">
                      <el-tag :type="verdictType(v.verdict)" size="small">{{ v.verdict }}</el-tag>
                      <b class="ver-score">{{ v.score }} 分</b>
                      <span class="dim">一致率 {{ v.consistency }}% · 差异 {{ v.mismatch_count }} 项 · {{ v.created_at }}</span>
                    </div>
                    <template v-if="mismatchesOf(v.checklist).length">
                      <div class="mis-block-title">🚩 认知差异点（学生判「符合」但引擎发现风险）：</div>
                      <div v-for="(m, i) in mismatchesOf(v.checklist)" :key="i" class="mis-row">
                        <b>[{{ m.group }}] {{ m.metric }}</b>
                        <div class="mis-reason">引擎：{{ m.reason }}</div>
                      </div>
                    </template>
                    <div v-else class="mis-ok">✓ 本次核验无认知差异项</div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- ════ 辩论回放 ════ -->
            <el-tab-pane label="🎭 反向质询" name="debate">
              <div v-loading="debLoading || replayLoading" class="tab-body">
                <el-empty v-if="!sessionsList.length" description="该学生还没有辩论会话" :image-size="70" />
                <div v-else class="debate-layout">
                  <div class="session-mini-list">
                    <div
                      v-for="s in sessionsList"
                      :key="s.id"
                      class="mini-session"
                      :class="{ active: replay?.session?.id === s.id }"
                      @click="openReplay(s)"
                    >
                      <div class="ms-top">
                        <b>#{{ s.id }} {{ s.group_name || s.username }}</b>
                        <el-tag size="small" :type="s.status === 'completed' ? 'success' : 'info'">
                          {{ STAGE_NAMES[s.stage] || s.stage }}
                        </el-tag>
                      </div>
                      <div class="cell-sub">{{ s.message_count }} 条消息 · {{ s.created_at }}</div>
                    </div>
                  </div>

                  <div v-if="replay" class="replay-area">
                    <div class="msg-flow">
                      <div
                        v-for="m in replay.messages"
                        :key="m.id"
                        class="msg-line"
                        :class="'role-' + m.role"
                      >
                        <span class="msg-role">{{ m.role === 'student' ? '🙋 学生' : m.role === 'ai' ? '🤖 AI' : '👨‍🏫 教师' }}</span>
                        <div class="msg-bubble">{{ m.content }}</div>
                        <span class="msg-time">{{ m.created_at }}</span>
                      </div>
                    </div>
                    <div v-if="replay.session.status !== 'completed'" class="note-input">
                      <el-input
                        v-model="noteText"
                        type="textarea" :rows="2"
                        placeholder="以教师身份介入这场辩论，给学生一句提示或引导…"
                      />
                      <el-button type="primary" :loading="sendingNote" @click="submitNote">发送留言</el-button>
                    </div>
                    <div v-else class="mis-ok" style="margin-top: 10px;">✓ 该场辩论已闭环完成</div>
                  </div>
                  <div v-else class="pick-session dim">← 选择一场会话查看完整时间线</div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </template>

        <el-empty v-else description="选择学生后可查看其核验清单与辩论时间线" :image-size="90" style="padding-top: 120px;" />
      </div>
    </div>
  </div>
</template>

<script>
export default { name: 'TeachingMonitor' }
</script>

<style scoped>
/* 与 StudentManage 等页面保持一致的暗色设计语言 */
.page-container {
  padding: 20px;
  color: #fff;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-left {
  display: flex;
  align-items: baseline;
  gap: 16px;
}
.page-container h1 {
  margin: 0;
  font-size: 22px;
}
.page-desc {
  color: #8a97a8;
  font-size: 13px;
}

/* 统计卡 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 16px 20px;
}
.stat-icon { font-size: 28px; }
.stat-label { font-size: 12px; color: #8a97a8; }
.stat-value { font-size: 22px; font-weight: 700; line-height: 1.3; }

/* 面板容器 */
.monitor-body {
  display: grid;
  grid-template-columns: 54% 46%;
  gap: 16px;
  align-items: start;
}
.panel {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 14px 16px;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.panel.empty { min-height: 420px; }

.table-tip { font-size: 11px; color: #5d6b7e; margin: 8px 0 0; }

.cell-sub { font-size: 11px; color: #64748b; }
.dim { color: #5d6b7e; font-size: 11px; }
.lowscore { color: #f56c6c; font-weight: 600; }

/* 核验记录 */
.tab-body { min-height: 200px; }
.ver-list { max-height: 480px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
.ver-item {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  padding: 10px 14px;
}
.ver-title { display: flex; align-items: center; gap: 10px; }
.ver-score { font-size: 15px; }
.mis-block-title { font-size: 13px; font-weight: 600; color: #e6a23c; margin: 8px 0; }
.mis-row {
  border-left: 3px solid #f56c6c;
  background: rgba(245, 108, 108, 0.06);
  padding: 6px 10px;
  border-radius: 0 6px 6px 0;
  margin-bottom: 6px;
  font-size: 13px;
}
.mis-reason { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.mis-ok { color: #67c23a; font-size: 12px; margin-top: 6px; }

/* 辩论回放 */
.debate-layout { display: flex; gap: 12px; }
.session-mini-list { width: 198px; flex-shrink: 0; max-height: 470px; overflow-y: auto; }
.mini-session {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 10px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s;
  background: rgba(255, 255, 255, 0.02);
}
.mini-session:hover { border-color: #409eff; }
.mini-session.active { background: rgba(64, 158, 255, 0.15); border-color: #409eff; }
.ms-top { display: flex; justify-content: space-between; align-items: center; gap: 6px; }

.replay-area { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.msg-flow {
  max-height: 380px;
  overflow-y: auto;
  padding-right: 6px;
}
.msg-line { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 10px; }
.msg-role { font-size: 11px; flex-shrink: 0; padding-top: 6px; width: 52px; text-align: right; color: #8a97a8; }
.msg-bubble {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  flex: 1;
}
.role-student .msg-bubble { background: rgba(103, 194, 58, 0.12); }
.role-ai .msg-bubble { background: rgba(230, 162, 60, 0.1); }
.role-teacher .msg-bubble { background: rgba(245, 108, 108, 0.12); border: 1px dashed #f56c6c; }
.msg-time { font-size: 10px; color: #5d6b7e; flex-shrink: 0; padding-top: 8px; }

.note-input { display: flex; gap: 10px; margin-top: 12px; align-items: flex-end; }
.pick-session { text-align: center; padding: 80px 0; }

/* Element 组件深色补丁 */
.dark-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(64, 158, 255, 0.1);
  --el-table-border-color: rgba(255, 255, 255, 0.08);
  --el-table-row-hover-bg-color: rgba(64, 158, 255, 0.1);
  cursor: pointer;
}

.monitor-tabs :deep(.el-tabs__item) {
  color: #8a97a8;
}
.monitor-tabs :deep(.el-tabs__item.is-active),
.monitor-tabs :deep(.el-tabs__item:hover) {
  color: #409eff;
}
.monitor-tabs :deep(.el-tabs__nav-wrap::after) {
  background: rgba(255, 255, 255, 0.08);
}
</style>
