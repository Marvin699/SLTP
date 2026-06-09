<template>
  <div class="rate-page">
    <div class="rate-head">
      <div class="rate-logo">🛡️</div>
      <div class="rate-title">任务8 · 飞行演练电子评量表</div>
      <div class="rate-sub">{{ groupName }} · {{ roleLabel }}</div>
    </div>

    <div class="rate-section">
      <div class="rate-hint">请选择要打分的小组，按 <b>安全 · 规划 · 团队 · 改进</b> 四个维度评分（每项 0-10）</div>

      <div class="rate-group-tabs">
        <button
          class="rate-group-tab"
          :class="{ active: activeGid === gid }"
          v-for="gid in ALLOW_GIDS"
          :key="gid"
          @click="switchGroup(gid)"
        >
          {{ GROUP_MAP[gid] }}
          <span class="rg-count" v-if="latest[gid].count">· {{ latest[gid].count }}人 · {{ latest[gid].total }}</span>
        </button>
      </div>

      <div class="rate-list">
        <div v-for="(d, i) in dims" :key="i" class="rate-row">
          <div class="rate-label">
            <span class="rate-dim">{{ d.label }}</span>
            <span class="rate-weight">· {{ d.weight }}</span>
          </div>
          <div class="rate-controls">
            <button class="rate-btn" @click="setDim(i, d.val - 1)" :disabled="d.val<=0">−</button>
            <input class="rate-input" type="number" min="0" max="10" v-model.number="d.val" @input="clampDim(i)">
            <button class="rate-btn" @click="setDim(i, d.val + 1)" :disabled="d.val>=10">+</button>
            <div class="rate-slider">
              <input type="range" min="0" max="10" :value="d.val" @input="onSlider(i, $event)">
            </div>
          </div>
        </div>
      </div>

      <div class="rate-total-row">
        <div class="rate-total-label">合计（×2.5 → 百分制）</div>
        <div class="rate-total-value">{{ total }} / 40 分 ⇒ <b>{{ total*2.5 }}</b></div>
      </div>

      <div class="rate-name-row">
        <input class="rate-name-input" v-model="studentName" placeholder="你的名字（选填）" />
        <select class="rate-role" v-model="role">
          <option value="student">学生自评</option>
          <option value="peer">同学互评</option>
          <option value="teacher">教师/裁判</option>
        </select>
      </div>

      <button class="rate-submit" :disabled="submitting" @click="submit">
        <span v-if="!submitting && !submitted">✅ 提交评分</span>
        <span v-else-if="submitting">⏳ 提交中...</span>
        <span v-else>✅ 已提交（可继续给下一组打分）</span>
      </button>

      <div v-if="submitMsg" class="rate-msg" :class="{ ok: submitOk, err: !submitOk }">{{ submitMsg }}</div>
    </div>

    <div class="rate-link-foot">
      <router-link to="/evaluation">← 返回教学智评</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const API_BASE = (location.protocol || 'http') + '//' + (location.hostname || 'localhost') + ':8000'

const GROUP_MAP = {
  1: '揽星组', 2: '御风组', 3: '巡天组', 4: '逐日组', 5: '凌云组', 6: '长空组',
}
const ALLOW_GIDS = [1, 3, 6]
const ROLE_MAP = {
  student: '学生自评', peer: '同学互评', teacher: '教师/裁判',
}
const DIMS_TEMPLATE = [
  { label: '安全',    weight: '35%', val: 0 },
  { label: '规划',    weight: '35%', val: 0 },
  { label: '团队',    weight: '15%', val: 0 },
  { label: '改进',    weight: '15%', val: 0 },
]

function parseGroupIds() {
  const raw = route.query.group_id
  if (!raw) return ALLOW_GIDS[0]
  if (typeof raw === 'string' && raw.includes(',')) {
    const first = parseInt(raw.split(',')[0])
    return ALLOW_GIDS.includes(first) ? first : ALLOW_GIDS[0]
  }
  const n = parseInt(raw)
  return ALLOW_GIDS.includes(n) ? n : ALLOW_GIDS[0]
}

const activeGid = ref(parseGroupIds())
const groupName = computed(() => GROUP_MAP[activeGid.value] || '揽星组')
const dims = ref(DIMS_TEMPLATE.map(d => ({ ...d })))
const studentName = ref('')
const role = ref('student')
const submitting = ref(false)
const submitted = ref(false)
const submitMsg = ref('')
const submitOk = ref(true)
const roleLabel = computed(() => ROLE_MAP[role.value] || '学生自评')
const total = computed(() => dims.value.reduce((s, d) => s + d.val, 0))

const latest = reactive({
  1:{count:0,total:0}, 3:{count:0,total:0}, 6:{count:0,total:0},
})

function switchGroup(gid) {
  activeGid.value = gid
  dims.value = DIMS_TEMPLATE.map(d => ({ ...d }))
  submitted.value = false
  submitMsg.value = ''
}
function clampDim(i) {
  if (dims.value[i].val < 0) dims.value[i].val = 0
  if (dims.value[i].val > 10) dims.value[i].val = 10
  if (Number.isNaN(dims.value[i].val)) dims.value[i].val = 0
}
function setDim(i, v) { dims.value[i].val = Math.max(0, Math.min(10, v)) }
function onSlider(i, e) { dims.value[i].val = parseInt(e.target.value) }

async function refreshLatest() {
  try {
    const r = await fetch(`${API_BASE}/api/ratings/latest_all`)
    const j = await r.json()
    for (const gid of ALLOW_GIDS) {
      if (j[gid]) {
        latest[gid].count = j[gid].count || 0
        latest[gid].total = j[gid].total || 0
      }
    }
  } catch(e) {}
}

async function submit() {
  if (submitting.value) return
  submitting.value = true
  submitMsg.value = ''
  try {
    const r = await fetch(`${API_BASE}/api/ratings/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        group_id: activeGid.value,
        dims: dims.value.map(d => ({ label: d.label, val: d.val })),
        total: Math.round(total.value * 2.5),
        name: studentName.value,
        role: role.value,
      }),
    })
    const j = await r.json()
    if (j.ok) {
      submitOk.value = true
      submitMsg.value = `已提交！${GROUP_MAP[activeGid.value]} 已有 ${j.count} 人评分，当前均分 ${j.total} 分`
      submitted.value = true
      refreshLatest()
    } else {
      submitOk.value = false
      submitMsg.value = '提交失败：' + (j.detail || '未知错误')
    }
  } catch (e) {
    submitOk.value = false
    submitMsg.value = '网络错误，请稍后重试（确认后端 8000 端口已启动）'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  refreshLatest()
  setInterval(refreshLatest, 5000)
})
</script>

<style scoped>
.rate-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a1a3a 0%, #071226 100%);
  color: #e4ecf6;
  padding: 20px 16px 60px;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
}
.rate-head { text-align: center; padding: 6px 0 18px; }
.rate-logo { font-size: 40px; }
.rate-title { font-size: 18px; font-weight: 700; margin-top: 6px; letter-spacing: 1px; }
.rate-sub { margin-top: 4px; color: #8ab4d0; font-size: 13px; }

.rate-section {
  background: rgba(0,168,255,0.06);
  border: 1px solid rgba(0,168,255,0.18);
  border-radius: 14px;
  padding: 16px;
  backdrop-filter: blur(8px);
}
.rate-hint { font-size: 14px; color: #c8d4e0; margin-bottom: 14px; line-height: 1.5; }

.rate-group-tabs { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.rate-group-tab {
  flex: 1; min-width: 88px;
  padding: 10px 10px;
  font-size: 14px;
  font-weight: 600;
  color: #b8d4e8;
  border-radius: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(0,168,255,0.2);
  transition: all 0.25s;
}
.rate-group-tab.active {
  background: linear-gradient(135deg, rgba(0,220,130,0.22), rgba(0,168,255,0.22));
  border-color: rgba(0,220,130,0.6);
  color: #00dc82;
  box-shadow: 0 0 14px rgba(0,220,130,0.25);
}
.rg-count { font-size: 11px; color: #5a7a9a; font-weight: 400; margin-left: 4px; }

.rate-list { display: flex; flex-direction: column; gap: 12px; }
.rate-row {
  display: flex; flex-direction: column; gap: 8px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  border: 1px solid rgba(0,168,255,0.1);
}
.rate-label { display: flex; align-items: baseline; gap: 6px; }
.rate-dim { font-size: 16px; font-weight: 600; color: #e4ecf6; }
.rate-weight { font-size: 12px; color: #5a7a9a; }
.rate-controls { display: flex; align-items: center; gap: 10px; }
.rate-btn {
  width: 36px; height: 36px; border-radius: 8px;
  border: 1px solid rgba(0,168,255,0.3);
  background: rgba(0,168,255,0.08);
  color: #00dc82; font-size: 18px; font-weight: 700;
}
.rate-btn:disabled { opacity: 0.35; }
.rate-input {
  width: 64px; height: 36px; text-align: center;
  font-size: 18px; font-weight: 700; color: #00dc82;
  background: rgba(0,220,130,0.06);
  border: 1px solid rgba(0,220,130,0.25);
  border-radius: 8px;
}
.rate-slider { flex: 1; }
.rate-slider input[type=range] { width: 100%; accent-color: #00dc82; }

.rate-total-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 14px; padding: 12px 14px;
  background: linear-gradient(135deg, rgba(0,220,130,0.1), rgba(0,168,255,0.1));
  border: 1px solid rgba(0,220,130,0.3);
  border-radius: 10px;
}
.rate-total-label { font-size: 14px; color: #c8d4e0; }
.rate-total-value { font-size: 22px; font-weight: 800; color: #00dc82; letter-spacing: 1px; }

.rate-name-row { display: flex; gap: 10px; margin-top: 14px; }
.rate-name-input {
  flex: 1; height: 42px; padding: 0 12px;
  font-size: 14px; color: #e4ecf6;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(0,168,255,0.25);
  border-radius: 8px;
}
.rate-role {
  height: 42px; padding: 0 10px;
  font-size: 13px; color: #e4ecf6;
  background: rgba(0,168,255,0.08);
  border: 1px solid rgba(0,168,255,0.25);
  border-radius: 8px;
}

.rate-submit {
  width: 100%; height: 50px; margin-top: 16px;
  font-size: 16px; font-weight: 700; letter-spacing: 2px;
  color: #fff;
  background: linear-gradient(135deg, #00dc82, #00a8ff);
  border: none; border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0,220,130,0.25);
}
.rate-submit:disabled { opacity: 0.6; }

.rate-msg { margin-top: 10px; padding: 10px 14px; font-size: 13px; border-radius: 8px; }
.rate-msg.ok { background: rgba(0,220,130,0.1); color: #00dc82; border: 1px solid rgba(0,220,130,0.25); }
.rate-msg.err { background: rgba(255,107,107,0.1); color: #ff6b50; border: 1px solid rgba(255,107,107,0.25); }

.rate-link-foot { margin-top: 20px; text-align: center; }
.rate-link-foot a { color: #00a8ff; font-size: 13px; }
</style>
