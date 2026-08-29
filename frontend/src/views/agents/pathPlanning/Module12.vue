<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useDebateStore } from '@/stores/pathPlanning/debate'
import { useReportStore } from '@/stores/pathPlanning/report'

const debateStore = useDebateStore()
const reportStore = useReportStore()

// ─── 阶段与维度定义（与后端对齐） ───
const STAGE_FLOW = [
  { key: 'hypothesis', name: '假设提出', icon: '💡', desc: '提出你的初始判断与假设' },
  { key: 'verify', name: '验证分析', icon: '🔬', desc: '用数据与标准验证假设' },
  { key: 'rebut', name: '反驳交锋', icon: '⚔️', desc: '回应 AI 的质疑与反驳' },
  { key: 'rebuild', name: '重构优化', icon: '🔧', desc: '重构你的方案结论' },
]
const DIMENSIONS = [
  { key: 'safety', name: '安全性' },
  { key: 'timeliness', name: '时效性' },
  { key: 'economy', name: '经济性' },
  { key: 'feasibility', name: '可行性' },
  { key: 'compliance', name: '合规性' },
  { key: 'load', name: '载重匹配' },
  { key: 'airspace', name: '空域合规' },
  { key: 'cold_chain', name: '冷链时限' },
]

// ─── 新建会话表单 ───
const showCreateForm = ref(false)
const planSummaryDraft = ref('')
const groupNameDraft = ref('')
const creating = ref(false)

/** 从方案库（报告历史）自动带出摘要 */
function fillFromLatestReport() {
  const latest = reportStore.history[0]
  if (!latest) {
    planSummaryDraft.value = ''
    return
  }
  const scores = latest.report_data?.scores || {}
  const stats = latest.report_data?.stats || {}
  const scoreStr = Object.entries(scores).map(([k, v]) => `${k}=${v}`).join(' / ')
  planSummaryDraft.value =
    `方案「${latest.filename || latest.scheme_type || '未命名'}」：` +
    `总距离 ${stats.total_distance ?? '—'} km，` +
    `无人机 ${stats.drone_count ?? '—'} 架，` +
    `趟次 ${stats.total_trips ?? '—'} 趟` +
    (scoreStr ? `，四维评分 ${scoreStr}` : '')
}

async function handleCreateSession() {
  creating.value = true
  await debateStore.createSession(planSummaryDraft.value.trim(), null, groupNameDraft.value.trim())
  creating.value = false
  showCreateForm.value = false
}

// 删除历史会话（含确认提示）
async function handleDeleteSession(s) {
  const name = s.group_name || `#${s.id}`
  if (!confirm(`确认删除会话「${name}」？\n删除后整场辩论记录无法恢复。`)) return
  await debateStore.deleteSession(s.id)
}

// ─── 输入区状态 ───
const inputText = ref('')
const selectedDimensions = ref([])
const confidence = ref(70)
const currentStage = computed(() => debateStore.stage)

function toggleDimension(key) {
  const i = selectedDimensions.value.indexOf(key)
  if (i >= 0) selectedDimensions.value.splice(i, 1)
  else selectedDimensions.value.push(key)
}

const chatFlowEl = ref(null)
async function scrollBottom() {
  await nextTick()
  if (chatFlowEl.value) chatFlowEl.value.scrollTop = chatFlowEl.value.scrollHeight
}

async function handleSubmit() {
  const content = inputText.value.trim()
  if (!content || debateStore.loading || debateStore.isCompleted) return
  inputText.value = ''
  await debateStore.submitStatement(content, {
    stage: currentStage.value,
    judgment_dimensions: selectedDimensions.value,
    judgment_confidence: confidence.value,
  })
  scrollBottom()
}

// ─── 完成闭环 ───
const showComplete = ref(false)
const finalVerdict = ref('')
async function handleComplete() {
  await debateStore.completeSession(finalVerdict.value.trim())
  showComplete.value = false
  finalVerdict.value = ''
}

// ─── 生命周期 ───
onMounted(async () => {
  await Promise.all([
    debateStore.loadSessions(),
    reportStore.loadHistory(),
  ])
  if (debateStore.currentSession) {
    // 已有会话也重新拉取，同步教师介入等新消息
    await debateStore.loadSession(debateStore.currentSession.id)
    scrollBottom()
  } else if (debateStore.sessions.length > 0) {
    // 自动选中最近一个活跃会话
    const active = debateStore.sessions.find(s => s.status === 'active') || debateStore.sessions[0]
    await debateStore.loadSession(active.id)
    scrollBottom()
  }
})

const stageIndex = computed(() => STAGE_FLOW.findIndex(s => s.key === currentStage.value))
</script>

<template>
  <div class="module12 debate-room">
    <!-- ═══ 左栏：会话管理 ═══ -->
    <div class="dr-left">
      <div class="dr-panel-header">
        <h2 class="module-title">🎭 反向质询</h2>
        <p class="dr-sub">AI 是辩论伙伴，不是答案机器</p>
        <button class="btn btn-primary btn-block" @click="showCreateForm = !showCreateForm">
          ＋ 新建辩论会话
        </button>
      </div>

      <!-- 新建表单 -->
      <div v-if="showCreateForm" class="create-form">
        <label class="form-label">小组名（可选）</label>
        <input v-model="groupNameDraft" type="text" class="form-input" placeholder="如：第3组" maxlength="20" />

        <label class="form-label">绑定方案摘要</label>
        <textarea
          v-model="planSummaryDraft"
          class="form-input"
          rows="4"
          placeholder="描述你要质询的方案：机型数量、总距离、四维评分等"
        ></textarea>
        <div class="form-actions">
          <button
            v-if="reportStore.history.length > 0"
            class="btn btn-sm btn-outline"
            @click="fillFromLatestReport"
          >
            📥 从方案库带入
          </button>
          <button class="btn btn-sm btn-primary" :disabled="creating" @click="handleCreateSession">
            {{ creating ? '创建中...' : '开始辩论' }}
          </button>
        </div>
      </div>

      <!-- 会话列表 -->
      <div class="session-list">
        <div class="list-title">历史会话（{{ debateStore.sessions.length }}）</div>
        <div
          v-for="s in debateStore.sessions"
          :key="s.id"
          class="session-card"
          :class="{ active: debateStore.currentSession?.id === s.id }"
          @click="debateStore.loadSession(s.id).then(scrollBottom)"
        >
          <div class="sc-row1">
            <span class="sc-name">#{{ s.id }} {{ s.group_name || '个人辩论' }}</span>
            <span class="sc-status" :class="s.status">{{ s.status === 'completed' ? '已完成' : '进行中' }}</span>
          </div>
          <div class="sc-meta">
            <span>📍 {{ s.stage_name }}</span>
            <span>💬 {{ s.message_count }} 条</span>
            <span>🗣 {{ s.student_statement_count }} 次陈述</span>
          </div>
          <div class="sc-plan">{{ (s.plan_summary || '').slice(0, 60) }}</div>
          <div class="sc-time">{{ s.created_at }}</div>
          <button
            class="sc-delete"
            title="删除该会话"
            @click.stop="handleDeleteSession(s)"
          >🗑</button>
        </div>
        <div v-if="debateStore.sessions.length === 0 && !debateStore.listLoading" class="empty-hint">
          暂无辩论记录<br />点击上方按钮开始第一场质询
        </div>
      </div>
    </div>

    <!-- ═══ 右栏：辩论区 ═══ -->
    <div class="dr-right">
      <!-- 无会话 -->
      <div v-if="!debateStore.currentSession" class="dr-empty">
        <div class="empty-icon">🎭</div>
        <div class="empty-title">反向质询辩论室</div>
        <div class="empty-desc">
          AI 将针对你的方案陈述进行追问挑战<br />
          形成「假设 → 验证 → 反驳 → 重构」深度学习闭环<br />
          左侧点击「新建辩论会话」开始
        </div>
      </div>

      <template v-else>
        <!-- 阶段进度条 -->
        <div class="stage-bar">
          <template v-for="(s, i) in STAGE_FLOW" :key="s.key">
            <div
              class="stage-node"
              :class="{ done: i < stageIndex, current: i === stageIndex, reachable: !debateStore.isCompleted }"
              @click="!debateStore.isCompleted && debateStore.currentSession && (debateStore.currentSession.stage = s.key)"
              :title="s.desc"
            >
              <span class="stage-icon">{{ s.icon }}</span>
              <span class="stage-name">{{ s.name }}</span>
            </div>
            <div v-if="i < STAGE_FLOW.length - 1" class="stage-arrow" :class="{ lit: i < stageIndex }">→</div>
          </template>
          <div class="stage-final" :class="{ reached: debateStore.isCompleted }">🏁 闭环</div>
        </div>

        <!-- 方案摘要条 -->
        <div class="plan-strip" :title="debateStore.currentSession.plan_summary">
          📋 {{ (debateStore.currentSession.plan_summary || '').slice(0, 80) }}
        </div>

        <!-- 对话流 -->
        <div ref="chatFlowEl" class="chat-flow">
          <div
            v-for="m in debateStore.messages"
            :key="m.id"
            class="msg-row"
            :class="m.role"
          >
            <!-- AI 追问 -->
            <template v-if="m.role === 'ai'">
              <div class="avatar ai-avatar">AI</div>
              <div class="bubble ai-bubble">
                <div v-if="m.challenge_name" class="challenge-tag">{{ m.challenge_name }}</div>
                <div class="msg-content">{{ m.content }}</div>
              </div>
            </template>

            <!-- 教师介入 -->
            <template v-else-if="m.role === 'teacher'">
              <div class="bubble teacher-bubble">{{ m.content }}</div>
            </template>

            <!-- 学生陈述 -->
            <template v-else>
              <div class="bubble student-bubble">
                <div class="msg-content">{{ m.content }}</div>
                <div v-if="m.judgment_dimensions?.length || m.judgment_confidence != null" class="judgment-meta">
                  <span
                    v-for="d in m.judgment_dimensions"
                    :key="d"
                    class="jd-chip"
                  >{{ DIMENSIONS.find(x => x.key === d)?.name || d }}</span>
                  <span v-if="m.judgment_confidence != null" class="jd-conf">置信度 {{ m.judgment_confidence }}%</span>
                </div>
                <div class="msg-stage">{{ m.stage_name }}</div>
              </div>
              <div class="avatar student-avatar">我</div>
            </template>
          </div>

          <!-- AI 思考中 -->
          <div v-if="debateStore.loading" class="msg-row ai">
            <div class="avatar ai-avatar">AI</div>
            <div class="bubble ai-bubble thinking">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              辩论伙伴组织追问中...
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="debateStore.error" class="error-bar">⚠️ {{ debateStore.error }}</div>

        <!-- 输入区 -->
        <div class="input-area" v-if="!debateStore.isCompleted">
          <!-- 评判维度 -->
          <div class="dim-row">
            <span class="dim-label">评判维度：</span>
            <button
              v-for="d in DIMENSIONS"
              :key="d.key"
              class="dim-chip"
              :class="{ on: selectedDimensions.includes(d.key) }"
              @click="toggleDimension(d.key)"
            >{{ d.name }}</button>
          </div>

          <!-- 置信度 -->
          <div class="conf-row">
            <span class="dim-label">自评置信度：</span>
            <input v-model.number="confidence" type="range" min="0" max="100" step="10" class="conf-slider" />
            <span class="conf-val">{{ confidence }}%</span>
          </div>

          <div class="text-row">
            <textarea
              v-model="inputText"
              class="statement-input"
              :placeholder="`【${STAGE_FLOW.find(s => s.key === currentStage)?.name || ''}】陈述你的观点、依据或反驳...（Enter 发送 / Shift+Enter 换行）`"
              rows="3"
              @keydown.enter.exact.prevent="handleSubmit"
            ></textarea>
            <button
              class="btn btn-primary send-btn"
              :disabled="debateStore.loading || !inputText.trim()"
              @click="handleSubmit"
            >{{ debateStore.loading ? '追问中...' : '提交陈述' }}</button>
          </div>

          <div class="input-footer">
            <span class="footer-hint">💡 AI 只会追问，不会给答案 —— 用数据和标准回应它</span>
            <button class="btn btn-sm btn-outline" @click="showComplete = true">🏁 完成闭环</button>
          </div>
        </div>

        <!-- 已完成态 -->
        <div v-else class="completed-area">
          <div class="completed-banner">✅ 本轮深度学习闭环已完成</div>
          <div class="verdict-box" v-if="debateStore.currentSession.final_verdict">
            <div class="verdict-title">你的最终结论：</div>
            <div class="verdict-text">{{ debateStore.currentSession.final_verdict }}</div>
          </div>
        </div>
      </template>
    </div>

    <!-- 完成弹窗 -->
    <Teleport to="body">
      <div v-if="showComplete" class="modal-mask" @click.self="showComplete = false">
        <div class="modal-box">
          <h3 class="modal-title">🏁 完成本轮辩论闭环</h3>
          <p class="modal-desc">请总结经过质询后，你对方案的最终结论（将记录为闭环成果）：</p>
          <textarea v-model="finalVerdict" class="form-input" rows="4"
            placeholder="例如：经过验证，我认为方案的时效性假设在急救场景不成立，重构建议为..."></textarea>
          <div class="modal-actions">
            <button class="btn btn-outline" @click="showComplete = false">再辩一轮</button>
            <button class="btn btn-primary" @click="handleComplete">确认完成</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.module12 {
  flex: 1;
  display: flex;
  overflow: hidden;
  height: 100%;
}

/* ═══ 左栏 ═══ */
.dr-left {
  width: 320px;
  flex-shrink: 0;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: var(--navy2);
}

.dr-panel-header {
  padding: 14px 16px 12px;
  border-bottom: 1px solid var(--border);
}

.module-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--teal);
  margin: 0 0 4px;
  font-family: var(--mono);
  letter-spacing: 0.5px;
}

.dr-sub {
  font-size: 11px;
  color: var(--text3);
  margin: 0 0 12px;
}

.create-form {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--navy3);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 11px;
  color: var(--text2);
  font-weight: 600;
}

.form-input {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text);
  font-size: 12px;
  padding: 8px 10px;
  font-family: var(--sans);
  resize: vertical;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--teal);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 4px;
}

.session-list {
  padding: 10px 14px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-title {
  font-size: 11px;
  color: var(--text3);
  font-family: var(--mono);
  margin-bottom: 2px;
}

.session-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--navy3);
  padding: 9px 11px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

/* 删除按钮：默认隐藏，hover 卡片时浮现 */
.sc-delete {
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 22px;
  height: 22px;
  border-radius: 5px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text3);
  font-size: 11px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
  line-height: 1;
}

.session-card:hover .sc-delete {
  opacity: 1;
}

.sc-delete:hover {
  color: #ff5b5b;
  border-color: rgba(255, 91, 91, 0.4);
  background: rgba(255, 91, 91, 0.08);
}

.session-card:hover { border-color: var(--teal); }
.session-card.active {
  border-color: var(--teal);
  background: linear-gradient(180deg, #11305a, #0b2445);
  box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.2);
}

.sc-row1 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.sc-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--teal);
  font-family: var(--mono);
}

.sc-status {
  font-size: 10px;
  padding: 1px 8px;
  border-radius: 10px;
  border: 1px solid currentColor;
}
.sc-status.active { color: var(--green); }
.sc-status.completed { color: var(--text3); }

.sc-meta {
  display: flex;
  gap: 10px;
  font-size: 10.5px;
  color: var(--text3);
}

.sc-plan {
  font-size: 10.5px;
  color: var(--text2);
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sc-time {
  font-size: 10px;
  color: var(--text3);
  margin-top: 3px;
  font-family: var(--mono);
}

.empty-hint {
  text-align: center;
  padding: 30px 10px;
  color: var(--text3);
  font-size: 11px;
  line-height: 2;
}

/* ═══ 右栏 ═══ */
.dr-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.dr-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.empty-icon { font-size: 52px; opacity: 0.35; }
.empty-title { font-size: 18px; font-weight: 700; color: var(--text2); }
.empty-desc {
  font-size: 12px;
  color: var(--text3);
  text-align: center;
  line-height: 2;
}

/* 阶段进度条 */
.stage-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--navy3);
  flex-shrink: 0;
}

.stage-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: default;
  transition: all 0.2s;
}

.stage-node.reachable { cursor: pointer; }
.stage-node.reachable:hover { background: rgba(0, 229, 255, 0.06); }

.stage-node.current {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.1);
}

.stage-node.done .stage-name { color: var(--green); }
.stage-node.done .stage-icon { filter: grayscale(0.2); }

.stage-icon { font-size: 16px; }
.stage-name {
  font-size: 10.5px;
  color: var(--text2);
  font-weight: 600;
}
.stage-node.current .stage-name { color: var(--teal); }

.stage-arrow {
  color: var(--text3);
  font-size: 12px;
}
.stage-arrow.lit { color: var(--green); }

.stage-final {
  margin-left: 6px;
  font-size: 11px;
  color: var(--text3);
  padding: 4px 10px;
  border-radius: 10px;
  border: 1px dashed var(--border2);
}
.stage-final.reached {
  color: var(--green);
  border-color: var(--green);
  border-style: solid;
}

/* 方案摘要条 */
.plan-strip {
  padding: 6px 16px;
  font-size: 11px;
  color: var(--text2);
  background: var(--navy2);
  border-bottom: 1px solid var(--border);
  font-family: var(--mono);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 对话流 */
.chat-flow {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.msg-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.msg-row.student { justify-content: flex-end; }

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--mono);
  flex-shrink: 0;
}

.ai-avatar {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: #fff;
}

.student-avatar {
  background: linear-gradient(135deg, #059669, #047857);
  color: #fff;
}

.bubble {
  max-width: 68%;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.7;
  position: relative;
}

.ai-bubble {
  background: var(--navy3);
  border: 1px solid var(--border2);
  border-top-left-radius: 2px;
  color: var(--text);
}

.student-bubble {
  background: linear-gradient(135deg, #065f46, #064e3b);
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-top-right-radius: 2px;
  color: #d1fae5;
}

.teacher-bubble {
  background: rgba(255, 179, 0, 0.12);
  border: 1px solid rgba(255, 179, 0, 0.4);
  color: #fde68a;
  max-width: 80%;
  margin: 0 auto;
  font-size: 12.5px;
}

.challenge-tag {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  color: var(--purple);
  border: 1px solid rgba(170, 128, 255, 0.5);
  background: rgba(170, 128, 255, 0.1);
  padding: 1px 8px;
  border-radius: 10px;
  margin-bottom: 6px;
  font-family: var(--mono);
}

.msg-content { white-space: pre-wrap; word-break: break-word; }

.judgment-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
  padding-top: 7px;
  border-top: 1px dashed rgba(16, 185, 129, 0.3);
  align-items: center;
}

.jd-chip {
  font-size: 10px;
  padding: 1px 7px;
  border-radius: 9px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #a7f3d0;
}

.jd-conf {
  font-size: 10px;
  color: rgba(209, 250, 229, 0.6);
  font-family: var(--mono);
}

.msg-stage {
  font-size: 9.5px;
  color: rgba(209, 250, 229, 0.45);
  margin-top: 5px;
  font-family: var(--mono);
}

.thinking {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text3);
  font-size: 12px;
}

.dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--purple);
  animation: blink 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 60%, 100% { opacity: 0.25; }
  30% { opacity: 1; }
}

.error-bar {
  padding: 6px 16px;
  font-size: 11px;
  color: #fca5a5;
  background: rgba(220, 38, 38, 0.1);
  border-top: 1px solid rgba(220, 38, 38, 0.3);
  flex-shrink: 0;
}

/* 输入区 */
.input-area {
  border-top: 1px solid var(--border);
  background: var(--navy2);
  padding: 10px 16px 12px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dim-row, .conf-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.dim-label {
  font-size: 11px;
  color: var(--text2);
  font-weight: 600;
  flex-shrink: 0;
}

.dim-chip {
  font-size: 10.5px;
  padding: 2px 9px;
  border-radius: 10px;
  border: 1px solid var(--border2);
  background: transparent;
  color: var(--text2);
  cursor: pointer;
  transition: all 0.15s;
}

.dim-chip:hover { border-color: var(--teal); color: var(--teal); }

.dim-chip.on {
  background: rgba(0, 229, 255, 0.12);
  border-color: var(--teal);
  color: var(--teal);
}

.conf-slider { width: 140px; accent-color: var(--teal); }

.conf-val {
  font-size: 11px;
  color: var(--teal);
  font-family: var(--mono);
  min-width: 38px;
}

.text-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.statement-input {
  flex: 1;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  font-size: 13px;
  padding: 9px 12px;
  font-family: var(--sans);
  resize: none;
  line-height: 1.6;
}

.statement-input:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.1);
}

.send-btn {
  flex-shrink: 0;
  height: 42px;
  min-width: 96px;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-hint {
  font-size: 10.5px;
  color: var(--text3);
}

/* 已完成态 */
.completed-area {
  border-top: 1px solid var(--border);
  padding: 18px 20px;
  background: rgba(0, 230, 118, 0.04);
  flex-shrink: 0;
}

.completed-banner {
  text-align: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--green);
  margin-bottom: 12px;
}

.verdict-box {
  background: var(--navy3);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--green);
  border-radius: 8px;
  padding: 12px 16px;
}

.verdict-title {
  font-size: 11px;
  color: var(--text2);
  font-weight: 700;
  margin-bottom: 6px;
}

.verdict-text {
  font-size: 13px;
  color: var(--text);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 弹窗 */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(6, 13, 26, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.modal-box {
  width: 480px;
  background: var(--navy2);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-title {
  font-size: 15px;
  color: var(--green);
  margin: 0;
}

.modal-desc {
  font-size: 12px;
  color: var(--text2);
  margin: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

/* 通用按钮 */
.btn {
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-family: var(--mono);
  transition: all 0.2s;
  font-size: 12px;
  padding: 0 14px;
  height: 32px;
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #00b4cc, #0088aa);
  color: #fff;
  font-weight: 600;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 0 14px rgba(0, 229, 255, 0.35);
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border2);
  color: var(--text2);
}

.btn-outline:hover {
  border-color: var(--teal);
  color: var(--teal);
}

.btn-block { width: 100%; }

.btn-sm {
  height: 28px;
  font-size: 11px;
}
</style>
