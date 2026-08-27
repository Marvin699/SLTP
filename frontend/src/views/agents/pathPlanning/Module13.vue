<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/pathPlanning/app'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import {
  getTemplate,
  submitCheck,
  listRecords,
  deleteRecord as apiDeleteRecord,
} from '@/api/pathPlanning/verification'

const app = useAppStore()
const opt = useOptimizerStore()

// ─── 状态 ───
const template = ref([])               // 7 组核验模板
const judgments = ref({})              // { itemId: { student_judgment, remark } }
const submitting = ref(false)
const error = ref(null)
const result = ref(null)               // 提交后的复核结果
const records = ref([])                // 我的核验历史
const showRight = ref(false)

onMounted(async () => {
  // 登录态自检：当前浏览器 origin 无 token 时提前提示，避免提交后才发现
  if (!localStorage.getItem('sltp_token')) {
    error.value = '当前浏览器未检测到登录凭证，请刷新页面并重新登录后再核验'
  }
  try {
    const res = await getTemplate()
    template.value = res.data.groups || []
    const init = {}
    for (const g of template.value) {
      for (const it of g.items) {
        init[it.id] = { student_judgment: 'pass', remark: '' }
      }
    }
    judgments.value = init
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  }
  loadRecords()
})

async function loadRecords() {
  try {
    const res = await listRecords(10)
    records.value = res.data.records || []
  } catch (e) {
    console.error('加载核验历史失败:', e)
  }
}

/** 可提交条件：已生成方案 */
const canSubmit = computed(() => !!opt.result && !submitting.value)

const answeredCount = computed(() =>
  Object.values(judgments.value).filter(j => j.student_judgment !== 'na').length)

/** 从复核结果中找到某指标项的判定明细 */
function findItem(itemId) {
  if (!result.value) return null
  for (const g of result.value.checklist) {
    for (const it of g.items) {
      if (it.id === itemId) return it
    }
  }
  return null
}

/** 差异项列表（学生判 pass 但引擎判 fail） */
const mismatches = computed(() => {
  if (!result.value) return []
  const list = []
  for (const g of result.value.checklist) {
    for (const it of g.items) {
      if (it.mismatch) list.push(it)
    }
  }
  return list
})

/** 提交核验（学生先自判，引擎后复核） */
async function handleSubmit() {
  if (!canSubmit.value) return
  submitting.value = true
  error.value = null
  try {
    const task = opt.buildTaskJson()
    const checklist = Object.entries(judgments.value).map(([id, j]) => ({
      id,
      student_judgment: j.student_judgment,
      remark: j.remark || '',
    }))
    const res = await submitCheck(task, opt.result, checklist)
    result.value = res.data
    showRight.value = true
    loadRecords()
  } catch (e) {
    if (e.response?.status === 401) {
      error.value = '登录已失效，请刷新页面并重新登录后再提交核验'
    } else {
      error.value = e.response?.data?.detail || e.message
    }
  } finally {
    submitting.value = false
  }
}

/** 回填建议参数并跳回路径规划（Module4） */
function applyRegen() {
  if (!result.value) return
  const deltas = result.value.param_suggestions || {}
  if (opt.acoParams && Object.keys(deltas).length > 0) {
    const p = { ...opt.acoParams }
    if (deltas.max_iterations_delta) p.max_iterations = Math.min((p.max_iterations || 100) + deltas.max_iterations_delta, 500)
    if (deltas.beta_delta) p.beta = Math.min(+(((p.beta || 3) + deltas.beta_delta).toFixed(1)), 10)
    if (deltas.elite_ants_delta) p.elite_ants = Math.min((p.elite_ants || 5) + deltas.elite_ants_delta, 20)
    opt.acoParams = p
  }
  opt.regenHints = {
    hints: result.value.regen_hints || [],
    params: deltas,
  }
  app.setModule(4)
}

/** 查看历史记录概要 */
function viewRecord(r) {
  alert(`核验记录 #${r.id}\n得分：${r.score}　判定：${r.verdict}\n差异项：${r.mismatch_count}　一致率：${r.consistency}%\n时间：${r.created_at}`)
}

async function handleDeleteRecord(r) {
  if (!confirm(`确认删除核验记录 #${r.id}？`)) return
  try {
    await apiDeleteRecord(r.id)
    records.value = records.value.filter(x => x.id !== r.id)
    if (result.value?.record_id === r.id) {
      result.value = null
      showRight.value = false
    }
  } catch (e) {
    alert(e.response?.data?.detail || e.message)
  }
}

function closeResult() {
  showRight.value = false
}
</script>

<template>
  <div class="verify-root">
    <!-- ═══ 左栏：当前方案 + 核验历史 ═══ -->
    <div class="vf-left">
      <div class="lf-card">
        <div class="lf-title">🎯 待核验方案</div>
        <template v-if="opt.result">
          <div class="lf-summary">
            <div class="ls-row"><span>总距离</span><b>{{ opt.totalDistance?.toFixed(1) }} km</b></div>
            <div class="ls-row"><span>总趟次</span><b>{{ opt.totalTrips }}</b></div>
            <div class="ls-row"><span>无人机数</span><b>{{ opt.droneCount }}</b></div>
            <div class="ls-row"><span>覆盖点位</span><b>{{ opt.villageCount }}</b></div>
          </div>
          <div v-if="opt.feasibleText" class="lf-feasible" :class="{ bad: !opt.feasible }">
            {{ opt.feasible ? '✓' : '✗' }} {{ opt.feasibleText }}
          </div>
        </template>
        <div v-else class="lf-empty">
          尚未生成规划方案
          <button class="lf-jump" @click="app.setModule(4)">← 去第 3 步路径规划</button>
        </div>
      </div>

      <div class="lf-card">
        <div class="lf-title">📋 我的核验历史</div>
        <div v-if="records.length === 0" class="lf-empty small">暂无核验记录</div>
        <div v-for="r in records" :key="r.id" class="rec-card" @click="viewRecord(r)">
          <div class="rc-top">
            <span class="rc-verdict" :class="r.verdict === '通过' ? 'ok' : r.verdict === '需整改' ? 'bad' : 'mid'">{{ r.verdict }}</span>
            <span class="rc-score">{{ r.score }}分</span>
          </div>
          <div class="rc-meta">
            差异 {{ r.mismatch_count }} 项 · 一致率 {{ r.consistency }}% · {{ r.created_at }}
          </div>
          <button class="rc-del" title="删除该记录" @click.stop="handleDeleteRecord(r)">🗑</button>
        </div>
      </div>
    </div>

    <!-- ═══ 中栏：核验清单 ═══ -->
    <div class="vf-center">
      <div class="vc-header">
        <div class="vc-title">📑 合规性核验清单</div>
        <div class="vc-sub">先完成自判（符合 / 不符合 / 不适用），提交后规则引擎将逐项交叉复核</div>
      </div>

      <div class="vc-scroll">
        <div v-for="g in template" :key="g.group" class="ck-group">
          <div class="cg-title">{{ g.icon }} {{ g.group }}</div>
          <div
            v-for="item in g.items"
            :key="item.id"
            class="ck-item"
            :class="{ mismatch: findItem(item.id)?.mismatch }"
          >
            <div class="ci-main">
              <div class="ci-metric">{{ item.metric }}</div>
              <div class="ci-standard">{{ item.standard }}</div>
              <div
                v-if="findItem(item.id)?.engine_reason"
                class="ci-engine"
                :class="{ fail: findItem(item.id)?.engine_judgment === 'fail', warn: findItem(item.id)?.engine_judgment === 'warn' }"
              >
                引擎复核：
                {{ findItem(item.id)?.engine_judgment === 'fail' ? '❌' : findItem(item.id)?.engine_judgment === 'warn' ? '⚠️' : '✓' }}
                {{ findItem(item.id)?.engine_reason }}
              </div>
            </div>
            <div class="ci-actions">
              <button class="judge-btn pass" :class="{ active: judgments[item.id]?.student_judgment === 'pass' }" title="符合" @click="judgments[item.id].student_judgment = 'pass'">✓</button>
              <button class="judge-btn fail" :class="{ active: judgments[item.id]?.student_judgment === 'fail' }" title="不符合" @click="judgments[item.id].student_judgment = 'fail'">✗</button>
              <button class="judge-btn na" :class="{ active: judgments[item.id]?.student_judgment === 'na' }" title="不适用" @click="judgments[item.id].student_judgment = 'na'">➖</button>
            </div>
            <input v-model="judgments[item.id].remark" class="ci-remark" placeholder="备注（选填）" />
          </div>
        </div>
      </div>

      <div class="vc-footer">
        <span class="answered-hint">已作答 {{ answeredCount }} / {{ Object.keys(judgments).length }} 项</span>
        <span v-if="error" class="err-text">{{ error }}</span>
        <button class="btn-submit" :disabled="!canSubmit" @click="handleSubmit">
          {{ submitting ? '引擎复核中…' : '提交核验 · 引擎交叉复核' }}
        </button>
      </div>
    </div>

    <!-- ═══ 右栏：复核结果 ═══ -->
    <div v-if="showRight && result" class="vf-right">
      <div class="rt-head">
        <div class="rt-score-ring" :class="result.verdict === '通过' ? 'ok' : result.verdict === '需整改' ? 'bad' : 'mid'">
          {{ result.score }}
        </div>
        <div class="rt-head-info">
          <div class="rt-verdict">{{ result.verdict }}</div>
          <div class="rt-meta">一致率 {{ result.consistency }}% · 差异 {{ result.mismatch_count }} 项</div>
        </div>
        <button class="rt-close" @click="closeResult">✕</button>
      </div>

      <div v-if="mismatches.length > 0" class="rt-section danger">
        <div class="rts-title">🚩 判定差异（你判「符合」但引擎发现风险）</div>
        <div v-for="m in mismatches" :key="m.id" class="mis-item">
          <div class="mi-metric">{{ m.metric }}</div>
          <div class="mi-reason">引擎：{{ m.engine_reason }}</div>
        </div>
      </div>

      <div v-if="result.rule_summary.four_dimensional_scores" class="rt-section">
        <div class="rts-title">📊 引擎四维评分参照</div>
        <div class="four-dim">
          <div class="fd-item"><span>安全</span><b>{{ result.rule_summary.four_dimensional_scores.safety ?? '-' }}</b></div>
          <div class="fd-item"><span>时效</span><b>{{ result.rule_summary.four_dimensional_scores.timeliness ?? '-' }}</b></div>
          <div class="fd-item"><span>经济</span><b>{{ result.rule_summary.four_dimensional_scores.economy ?? '-' }}</b></div>
          <div class="fd-item"><span>可行</span><b>{{ result.rule_summary.four_dimensional_scores.feasibility ?? '-' }}</b></div>
        </div>
      </div>

      <div v-if="result.regen_hints.length > 0" class="rt-section regen">
        <div class="rts-title">🔧 重生成建议</div>
        <div v-for="(h, i) in result.regen_hints" :key="i" class="hint-item">{{ h }}</div>
        <button class="btn-regen" @click="applyRegen">⚡ 回填参数并重新规划</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verify-root {
  display: flex;
  gap: 14px;
  height: 100%;
  overflow: hidden;
}

/* ─── 左栏 ─── */
.vf-left {
  width: 230px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}
.lf-card {
  background: var(--bg2, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 10px;
  padding: 12px;
}
.lf-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text1, #1e293b);
}
.lf-summary {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.ls-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text2, #475569);
}
.ls-row b {
  color: var(--text1, #1e293b);
  font-variant-numeric: tabular-nums;
}
.lf-feasible {
  margin-top: 8px;
  font-size: 11px;
  color: #16a34a;
}
.lf-feasible.bad { color: #dc2626; }
.lf-empty {
  text-align: center;
  font-size: 12px;
  color: var(--text3, #94a3b8);
  padding: 16px 0;
  line-height: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.lf-empty.small { padding: 8px 0; display: block; }
.lf-jump {
  background: none;
  border: none;
  color: #2563eb;
  cursor: pointer;
  font-size: 12px;
  text-decoration: underline;
}
.rec-card {
  position: relative;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  padding: 8px 26px 8px 10px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.rec-card:hover {
  border-color: #93c5fd;
  background: rgba(37, 99, 235, 0.03);
}
.rc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.rc-verdict {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 10px;
}
.rc-verdict.ok { color: #16a34a; background: rgba(22, 163, 74, 0.1); }
.rc-verdict.mid { color: #d97706; background: rgba(217, 119, 6, 0.1); }
.rc-verdict.bad { color: #dc2626; background: rgba(220, 38, 38, 0.1); }
.rc-score {
  font-size: 13px;
  font-weight: 700;
  color: var(--text1, #1e293b);
}
.rc-meta {
  font-size: 10px;
  color: var(--text3, #94a3b8);
  margin-top: 4px;
}
.rc-del {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border-radius: 5px;
  border: none;
  background: transparent;
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s;
  line-height: 1;
  font-size: 11px;
  color: var(--text3, #94a3b8);
}
.rec-card:hover .rc-del { opacity: 1; }
.rc-del:hover {
  color: #ff5b5b;
  background: rgba(255, 91, 91, 0.08);
}

/* ─── 中栏 ─── */
.vf-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 10px;
  background: var(--bg1, #fafafa);
  overflow: hidden;
}
.vc-header { padding: 12px 16px 8px; }
.vc-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text1, #1e293b);
}
.vc-sub {
  font-size: 11px;
  color: var(--text3, #94a3b8);
  margin-top: 2px;
}
.vc-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 4px 16px 12px;
}
.ck-group { margin-bottom: 14px; }
.cg-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text2, #475569);
  margin: 6px 0;
  padding-left: 2px;
}
.ck-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px 12px;
  background: var(--bg2, #fff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  padding: 9px 12px;
  margin-bottom: 7px;
  transition: border-color 0.2s;
}
.ck-item.mismatch {
  border-color: rgba(220, 38, 38, 0.55);
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.08);
  background: rgba(220, 38, 38, 0.03);
}
.ci-main { min-width: 0; }
.ci-metric {
  font-size: 12px;
  font-weight: 500;
  color: var(--text1, #1e293b);
}
.ci-standard {
  font-size: 10px;
  color: var(--text3, #94a3b8);
  margin-top: 2px;
}
.ci-engine {
  font-size: 11px;
  margin-top: 4px;
  color: #16a34a;
}
.ci-engine.warn { color: #d97706; }
.ci-engine.fail { color: #dc2626; }
.ci-actions {
  display: flex;
  gap: 5px;
  align-items: center;
}
.judge-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--border, #cbd5e1);
  background: var(--bg2, #fff);
  cursor: pointer;
  font-size: 12px;
  color: var(--text3, #94a3b8);
  transition: all 0.15s;
}
.judge-btn.pass.active { background: #16a34a; border-color: #16a34a; color: #fff; }
.judge-btn.fail.active { background: #dc2626; border-color: #dc2626; color: #fff; }
.judge-btn.na.active { background: #94a3b8; border-color: #94a3b8; color: #fff; }
.ci-remark {
  grid-column: 1 / -1;
  border: none;
  border-top: 1px dashed var(--border, #e2e8f0);
  background: transparent;
  font-size: 11px;
  padding: 5px 0 0;
  color: var(--text2, #475569);
  outline: none;
}
.vc-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-top: 1px solid var(--border, #e2e8f0);
  background: var(--bg2, #fff);
}
.answered-hint {
  font-size: 11px;
  color: var(--text3, #94a3b8);
}
.err-text {
  font-size: 11px;
  color: #dc2626;
  flex: 1;
}
.btn-submit {
  margin-left: auto;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-submit:hover:not(:disabled) { opacity: 0.88; }
.btn-submit:disabled { opacity: 0.45; cursor: not-allowed; }

/* ─── 右栏 ─── */
.vf-right {
  width: 260px;
  flex-shrink: 0;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 10px;
  background: var(--bg2, #fff);
  overflow-y: auto;
  padding: 14px;
}
.rt-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.rt-score-ring {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 800;
  flex-shrink: 0;
}
.rt-score-ring.ok {
  color: #16a34a;
  background: rgba(22, 163, 74, 0.1);
  border: 2px solid rgba(22, 163, 74, 0.4);
}
.rt-score-ring.mid {
  color: #d97706;
  background: rgba(217, 119, 6, 0.1);
  border: 2px solid rgba(217, 119, 6, 0.4);
}
.rt-score-ring.bad {
  color: #dc2626;
  background: rgba(220, 38, 38, 0.1);
  border: 2px solid rgba(220, 38, 38, 0.4);
}
.rt-verdict {
  font-size: 15px;
  font-weight: 700;
  color: var(--text1, #1e293b);
}
.rt-meta {
  font-size: 10px;
  color: var(--text3, #94a3b8);
  margin-top: 2px;
}
.rt-close {
  margin-left: auto;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--text3, #94a3b8);
}
.rt-close:hover {
  color: var(--text1, #1e293b);
  background: var(--bg1, #f1f5f9);
}
.rt-section {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--border, #e2e8f0);
}
.rts-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text2, #475569);
  margin-bottom: 8px;
}
.mis-item {
  background: rgba(220, 38, 38, 0.06);
  border: 1px solid rgba(220, 38, 38, 0.25);
  border-radius: 7px;
  padding: 7px 9px;
  margin-bottom: 6px;
}
.mi-metric {
  font-size: 11px;
  font-weight: 600;
  color: #b91c1c;
}
.mi-reason {
  font-size: 10px;
  color: var(--text2, #475569);
  margin-top: 3px;
  line-height: 1.5;
}
.four-dim {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}
.fd-item {
  text-align: center;
  padding: 7px 0;
  border-radius: 7px;
  background: var(--bg1, #f8fafc);
  border: 1px solid var(--border, #e2e8f0);
}
.fd-item span {
  display: block;
  font-size: 10px;
  color: var(--text3, #94a3b8);
}
.fd-item b {
  font-size: 13px;
  color: var(--text1, #1e293b);
}
.hint-item {
  font-size: 11px;
  line-height: 1.6;
  color: var(--text2, #475569);
  padding: 6px 8px;
  background: rgba(37, 99, 235, 0.05);
  border-left: 3px solid #2563eb;
  border-radius: 0 6px 6px 0;
  margin-bottom: 6px;
}
.btn-regen {
  width: 100%;
  margin-top: 4px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 9px 0;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.btn-regen:hover { opacity: 0.9; }
</style>
