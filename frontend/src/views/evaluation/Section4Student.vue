<template>
  <div class="s4-stu">
    <div class="stu-header">
      <div class="stu-h-left">
        <span class="stu-badge" :style="{ background: group.color }">{{ group.id }}</span>
        <div>
          <div class="stu-title">{{ group.name }} · AI智能体子系统</div>
          <div class="stu-sub">{{ group.task }}</div>
        </div>
      </div>
      <div class="stu-h-right">
        <span class="stu-stage">{{ stages[group.stage] }}</span>
        <span class="stu-timer">⏱ {{ formatTime(remainingSec) }}</span>
        <el-button v-if="!running" type="primary" size="small" @click="startRun">▶ 开始</el-button>
        <el-button v-else size="small" plain @click="stopRun">■ 暂停</el-button>
        <el-button size="small" plain @click="resetAll">⟲ 重置</el-button>
        <el-button size="small" plain @click="copyLink">🔗 分享链接</el-button>
      </div>
    </div>

    <div class="stu-body">
      <div class="stu-left">
        <div class="stu-video-wrap" :class="{ 'has-alert': hasAlert }">
          <video v-show="group.stream" ref="videoEl" autoplay muted playsinline></video>
          <div v-if="!group.stream" class="video-placeholder">
            <div class="vp-icon">📷</div>
            <div>摄像头未开启</div>
            <el-button size="small" type="primary" plain @click="startCamera(group)">
              点击开启摄像头
            </el-button>
          </div>
          <canvas class="video-overlay" ref="overlayEl"></canvas>
          <div v-if="group.detections.length" class="stu-detections">
            <div v-for="(d, i) in group.detections" :key="i" class="det-tag" :style="d.style">{{ d.label }}</div>
          </div>
        </div>

        <div class="stu-score">
          <div class="score-ring">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="44" stroke="rgba(255,255,255,0.1)" stroke-width="6" fill="none" />
              <circle cx="50" cy="50" r="44" :stroke="group.scoreColor" stroke-width="6" fill="none"
                stroke-linecap="round" :stroke-dasharray="`${group.score/100 * 276} 276`" transform="rotate(-90 50 50)" />
            </svg>
            <div class="score-val">{{ group.score }}</div>
          </div>
          <div class="score-label">我的得分</div>
          <div class="score-hint">{{ scoreHint }}</div>
        </div>
      </div>

      <div class="stu-right">
        <div class="tasks-box">
          <div class="tb-head">
            <span>📋 我的装载任务清单</span>
          </div>
          <ul class="tb-list">
            <li v-for="t in myTasks" :key="t.title" :class="{ done: t.done, ok: !t.done && !t.wrong, wrong: t.wrong }">
              <span class="tb-dot">{{ t.done ? '✓' : t.wrong ? '✗' : '·' }}</span>
              <span class="tb-text">{{ t.title }}</span>
              <span class="tb-sub">{{ t.hint }}</span>
            </li>
          </ul>
        </div>

        <div class="events-box">
          <div class="ev-head">
            <span>🤖 AI 实时提示</span>
            <el-tag size="small" :type="warnCount ? 'danger' : 'success'">{{ warnCount }} 条提醒</el-tag>
          </div>
          <div class="ev-list" ref="evLogRef">
            <div v-for="(ev, i) in group.events" :key="i" class="ev-item" :class="ev.level">
              <span class="ev-time">{{ ev.time }}</span>
              <span class="ev-badge">{{ ev.levelLabel }}</span>
              <span class="ev-role">{{ ev.role }}</span>
              <span class="ev-text">{{ ev.text }}</span>
            </div>
            <div v-if="!group.events.length" class="ev-empty">等待 AI 检测你的操作...</div>
          </div>
        </div>

        <div v-if="disasterMsg" class="disaster-box">
          <div class="disaster-title">🚨 灾情指令</div>
          <div class="disaster-text">{{ disasterMsg }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()

const ALL_GROUPS = [
  { id: 1, name: '逐日组', task: '2-8℃ 冷链疫苗', color: '#5b8def' },
  { id: 2, name: '揽星组', task: '-20℃ 深冷血浆', color: '#c77dff' },
  { id: 3, name: '驭风组', task: '避光防潮抗生素', color: '#6be6a1' },
  { id: 4, name: '长空组', task: '易碎防震注射液', color: '#ff9f43' },
  { id: 5, name: '凌云组', task: '易燃危险品消毒品', color: '#ff6b81' },
  { id: 6, name: '巡天组', task: '多品类综合药品', color: '#74b9ff' },
]

const groupId = computed(() => {
  const g = route.query.group
  if (g) {
    const n = Number(g)
    if (!isNaN(n) && n >= 1 && n <= 6) return n
    const found = ALL_GROUPS.find(x => x.name === g)
    if (found) return found.id
  }
  return 1
})

const _g = ALL_GROUPS.find(x => x.id === groupId.value) || ALL_GROUPS[0]

const group = reactive({
  ..._g,
  stream: null,
  detections: [],
  events: [],
  score: 85,
  scoreColor: '#42d39c',
  stage: 1,
})

const stages = ['待开始', '物资分拣', '包装装载', '固定贴标', '重心测量', '行前检查', '完成']

const myTasks = computed(() => {
  const map = {
    1: [
      { title: '疫苗冰排与药品隔离', hint: 'EPE 缓冲层 2cm', done: true, wrong: false },
      { title: '保温箱温度 2~8℃', hint: '已贴温湿度传感器', done: true, wrong: false },
      { title: '安瓿瓶竖直插入防震卡槽', hint: '正在检查...', done: false, wrong: group.events.some(e => e.text.includes('安瓿')), },
      { title: '防水胶带密封箱盖', hint: '还差 1 步', done: false, wrong: false },
      { title: '重心配平（≤1kg/m²）', hint: '进行中', done: false, wrong: false },
    ],
    2: [
      { title: '干冰重量占比 ≤ 10%', hint: '当前 ~8%', done: true, wrong: false },
      { title: '深冷箱排气阀保持打开', hint: '⚠ AI 提醒过', done: false, wrong: group.events.some(e => e.text.includes('排气阀')), },
      { title: '血浆袋竖直放置', hint: '正在检查...', done: false, wrong: false },
      { title: '防水膜 + 防火隔板', hint: '进行中', done: false, wrong: false },
      { title: '重心配平', hint: '进行中', done: false, wrong: false },
    ],
    3: [
      { title: '避光包装（铝箔袋）', hint: '✅ 已确认', done: true, wrong: false },
      { title: '防潮干燥剂 2 袋', hint: '✅ 已确认', done: true, wrong: false },
      { title: '抗生素有效期检查', hint: '进行中', done: false, wrong: false },
      { title: '重量压缩（风速限制）', hint: '灾情指令', done: false, wrong: false },
      { title: '重心配平', hint: '进行中', done: false, wrong: false },
    ],
    4: [
      { title: '注射液防震泡棉', hint: '✅ 已确认', done: true, wrong: false },
      { title: '易碎品上层摆放', hint: '⚠ AI 提醒过', done: false, wrong: group.events.some(e => e.text.includes('上层')), },
      { title: '防火隔板（酒精类）', hint: '进行中', done: false, wrong: false },
      { title: '标签：易碎 + 向上', hint: '还差 1 步', done: false, wrong: false },
      { title: '重心配平', hint: '进行中', done: false, wrong: false },
    ],
    5: [
      { title: '酒精与 84 分箱隔离', hint: '🔴 错误', done: false, wrong: group.events.some(e => e.text.includes('84') || e.text.includes('酒精')), },
      { title: '防火隔板（危险品）', hint: '✅ 已确认', done: true, wrong: false },
      { title: '静电防静电袋', hint: '进行中', done: false, wrong: false },
      { title: '危险品警示标签', hint: '还差 1 步', done: false, wrong: false },
      { title: '重心配平', hint: '进行中', done: false, wrong: false },
    ],
    6: [
      { title: '多品类分层分类', hint: '✅ 已确认', done: true, wrong: false },
      { title: '重物下层·易碎上层', hint: '⚠ 重心偏', done: false, wrong: group.events.some(e => e.text.includes('重心')), },
      { title: '药品密封膜检查', hint: '进行中', done: false, wrong: false },
      { title: '防火 + 防水膜', hint: '进行中', done: false, wrong: false },
      { title: '重心配平（±2cm）', hint: 'AI 提醒调整', done: false, wrong: false },
    ],
  }
  return map[groupId.value] || map[1]
})

const warnCount = computed(() => group.events.filter(e => e.level !== 'ok').length)
const hasAlert = computed(() => group.events.some(e => e.level === 'red') || group.events.some(e => e.level === 'orange'))
const scoreHint = computed(() => {
  if (group.score >= 90) return '优秀 · 继续保持'
  if (group.score >= 80) return '良好 · 注意 AI 提示'
  if (group.score >= 70) return '中等 · 有明显错误'
  return '需整改 · 请立即修正'
})

const remainingSec = ref(600)
const running = ref(false)
const disasterMsg = ref('')
const timer = ref(null)
const scoreWaveTimer = ref(null)
const fakeDetectTimer = ref(null)
const runTimers = ref([])

const presets = [
  { group: 1, level: 'yellow', text: '冰排与疫苗之间未放置 2cm 缓冲层，建议使用 EPE 隔离' },
  { group: 2, level: 'yellow', text: '深冷箱排气阀请保持打开状态，避免气体压力过高箱盖崩开' },
  { group: 2, level: 'orange', text: '干冰重量 14% 超出 ≤10% 标准，超出部分请分摊至其他保温箱' },
  { group: 4, level: 'orange', text: '安瓿瓶未竖直插入防震卡槽，运输震动可能断裂' },
  { group: 5, level: 'red', text: '酒精与 84 混装会产生有毒气体氯气，必须立即分箱隔离' },
  { group: 6, level: 'yellow', text: '重心偏左 2.3cm，请将重物重新均匀分布' },
  { group: 3, level: 'ok', text: '避光包装（铝箔袋）规范，传感器位置正确', role: 'AI' },
]

function levelLabel(lvl) {
  return ({ ok: '合规', yellow: '一般', orange: '严重', red: '致命' })[lvl] || '提醒'
}
function levelColor(lvl) {
  return ({ ok: '#42d39c', yellow: '#e6a23c', orange: '#ff9f43', red: '#ff4757' })[lvl] || '#888'
}
function formatTime(sec) {
  const m = Math.floor(sec / 60), s = sec % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
function timeNow() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}
function speak(text) {
  if (!('speechSynthesis' in window)) return
  try {
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'zh-CN'; u.rate = 1.05
    window.speechSynthesis.speak(u)
  } catch {}
}
function clampAndRound(x, lo = 40, hi = 99) {
  return Math.max(lo, Math.min(hi, Math.round(x)))
}
function gaussianNoise(sigma) {
  let u = 0, v = 0
  while (u === 0) u = Math.random()
  while (v === 0) v = Math.random()
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v) * sigma
}

function emit(level, text, role = 'AI') {
  const scoreDelta = { ok: 1.5, yellow: -2, orange: -5, red: -10 }[level] || 0
  group.score = clampAndRound(group.score + scoreDelta)
  group.scoreColor = group.score >= 80 ? '#42d39c' : group.score >= 70 ? '#ffa94d' : '#ff4757'
  group.events.unshift({
    time: timeNow(), level, role, text, levelLabel: levelLabel(level),
  })
  if (group.events.length > 30) group.events.pop()
  if (level === 'ok') return
  speak(`${group.name}，${text}`)
  nextTick(() => {
    const log = document.querySelector('.ev-list')
    if (log) log.scrollTop = 0
  })
}
function applyPreset(p) {
  if (p.group !== groupId.value) return
  emit(p.level, p.text, p.role || 'AI')
}

function tickScoreWave() {
  if (!running.value) return
  const target = 85
  const n = gaussianNoise(0.6)
  group.score = clampAndRound(group.score + n, 50, 99)
  group.scoreColor = group.score >= 80 ? '#42d39c' : group.score >= 70 ? '#ffa94d' : '#ff4757'
  scoreWaveTimer.value = setTimeout(tickScoreWave, 400)
}

const DET_LABELS = ['person', 'person', '保温箱', '药品盒', '防火箱', '防震盒', '温湿度传感器']
function fakeDetect() {
  const arr = []
  const n = 2 + Math.floor(Math.random() * 2)
  for (let i = 0; i < n; i++) {
    const lab = DET_LABELS[Math.floor(Math.random() * DET_LABELS.length)]
    const x = Math.floor(Math.random() * 60) + 10
    const y = Math.floor(Math.random() * 50) + 10
    const w = Math.floor(Math.random() * 20) + 15
    const h = Math.floor(Math.random() * 20) + 15
    const color = lab === 'person' ? '#42d39c' : lab === '防火箱' ? '#ff6b81' : '#6be6a1'
    arr.push({ label: `${lab}`, style: { left: `${x}%`, top: `${y}%`, border: `2px solid ${color}`, color } })
  }
  group.detections = arr
}

let overlayCtx = null
let lastBoxes = []
function drawOverlay() {
  if (!overlayCtx || !group.stream) { fakeDetect(); return }
  const canvas = overlayCtx.canvas
  const w = canvas.clientWidth, h = canvas.clientHeight
  if (canvas.width !== w) canvas.width = w
  if (canvas.height !== h) canvas.height = h
  overlayCtx.clearRect(0, 0, w, h)

  const newBoxes = []
  const n = 3 + Math.floor(Math.random() * 3)
  const labels = ['person', 'person', '保温箱', '药品盒', '防火箱', '防震盒']
  for (let i = 0; i < n; i++) {
    const lab = labels[Math.floor(Math.random() * labels.length)]
    let bx = Math.random() * (w - 140) + 20
    let by = Math.random() * (h - 120) + 20
    let bw = 100 + Math.random() * 80
    let bh = 80 + Math.random() * 60
    if (lastBoxes[i]) {
      bx += (lastBoxes[i].x - bx) * 0.3
      by += (lastBoxes[i].y - by) * 0.3
      bw += (lastBoxes[i].w - bw) * 0.3
      bh += (lastBoxes[i].h - bh) * 0.3
    }
    newBoxes.push({ x: bx, y: by, w: bw, h: bh })
    const color = lab === 'person' ? '#00d4ff' : lab === '防火箱' ? '#ff6b81' : lab === '保温箱' ? '#ffa94d' : '#6be6a1'
    overlayCtx.lineWidth = 2; overlayCtx.strokeStyle = color
    overlayCtx.strokeRect(bx, by, bw, bh)
    overlayCtx.fillStyle = color; overlayCtx.font = 'bold 12px sans-serif'
    overlayCtx.fillText(lab, bx + 4, by - 4)
  }
  lastBoxes = newBoxes
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 480, height: 360, facingMode: 'environment' }, audio: false,
    })
    group.stream = stream
    const v = document.querySelector('.stu-video-wrap video')
    if (v) { v.srcObject = stream; v.play() }
    drawOverlay()
  } catch (e) {
    ElMessage.warning('无法开启摄像头，将使用模拟画面')
    group.stream = null
    fakeDetect()
  }
}

function startRun() {
  if (running.value) return
  running.value = true
  timer.value = setInterval(() => {
    if (remainingSec.value > 0) {
      remainingSec.value--
      if (remainingSec.value % 60 === 0 && remainingSec.value < 600) {
        group.stage = Math.min(6, 7 - Math.floor(remainingSec.value / 60))
      }
    } else {
      running.value = false
      if (timer.value) { clearInterval(timer.value); timer.value = null }
    }
  }, 1000)
  tickScoreWave()
  fakeDetect()
  drawOverlay()
  fakeDetectTimer.value = setInterval(fakeDetect, 2500)
  const redraw = () => { if (running.value) { drawOverlay(); setTimeout(redraw, 1500) } }
  redraw()
  scheduleScript()
  emit('ok', `${group.name} 开始装载任务 · ${group.task}`, '教师')
  speak(`${group.name}，现在开始装载任务`)
}

function stopRun() {
  running.value = false
  if (timer.value) { clearInterval(timer.value); timer.value = null }
  if (scoreWaveTimer.value) { clearTimeout(scoreWaveTimer.value); scoreWaveTimer.value = null }
  if (fakeDetectTimer.value) { clearInterval(fakeDetectTimer.value); fakeDetectTimer.value = null }
  runTimers.value.forEach(t => clearTimeout(t))
  runTimers.value = []
}

function resetAll() {
  stopRun()
  remainingSec.value = 600
  group.score = 85
  group.scoreColor = '#42d39c'
  group.stage = 1
  group.events = []
  group.detections = []
  disasterMsg.value = ''
}

function scheduleScript() {
  const g = groupId.value
  const schedule = [
    [8000, 1, 'yellow'],
    [16000, 2, 'yellow'],
    [32000, 4, 'orange'],
    [42000, 5, 'red'],
    [50000, 3, 'ok'],
    [60000, 6, 'yellow'],
    [70000, 0, 'disaster', '风速 8m/s，货物总重量不得超过 10kg，请压缩体积'],
    [90000, 6, 'yellow'],
    [140000, 0, 'disaster', '霍乱疑似病例，请立刻向驭风组输送药品'],
    [180000, 4, 'orange'],
  ]
  schedule.forEach(([delay, targetG, level, text]) => {
    const t = setTimeout(() => {
      if (level === 'disaster') {
        disasterMsg.value = text
        emit('orange', `灾情：${text}`, '系统')
        speak(`灾情指令：${text}`)
      } else if (targetG === g) {
        const p = presets.find(p2 => p2.group === targetG && p2.level === level)
        if (p) applyPreset(p)
        else emit(level, '操作注意', 'AI')
      }
    }, delay)
    runTimers.value.push(t)
  })
}

function copyLink() {
  const url = `${location.origin}${location.pathname}?group=${encodeURIComponent(group.name)}`
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制，可以发到群里')
  }).catch(() => {
    ElMessage.info(url)
  })
}

onMounted(() => {
  nextTick(() => {
    overlayCtx = document.querySelector('.stu-video-wrap canvas')?.getContext('2d')
    if (overlayCtx) {
      const c = overlayCtx.canvas
      c.width = 480; c.height = 360
    }
  })
})
onUnmounted(() => {
  stopRun()
  if (group.stream) group.stream.getTracks().forEach(t => t.stop())
})
</script>

<style scoped>
.s4-stu { padding: 12px; color: #fff; min-height: 100vh; background: linear-gradient(135deg, #0b1728, #122740); }
.stu-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.05); border-radius: 10px; margin-bottom: 12px; }
.stu-h-left { display: flex; align-items: center; gap: 10px; }
.stu-badge { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
.stu-title { font-size: 16px; font-weight: 700; }
.stu-sub { font-size: 12px; color: #9fb3c8; }
.stu-h-right { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.stu-stage { color: #6be6a1; background: rgba(107,230,161,0.1); padding: 4px 10px; border-radius: 4px; }
.stu-timer { font-variant-numeric: tabular-nums; color: #f8c537; }

.stu-body { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.stu-left, .stu-right { display: flex; flex-direction: column; gap: 12px; }

.stu-video-wrap { position: relative; aspect-ratio: 4/3; background: #000; border-radius: 12px; overflow: hidden; border: 2px solid transparent; }
.stu-video-wrap.has-alert { border-color: #ff4757; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.5); } 50% { box-shadow: 0 0 0 8px rgba(255,71,87,0); } }
.stu-video-wrap video { width: 100%; height: 100%; object-fit: cover; display: block; }
.stu-video-wrap canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.video-overlay { z-index: 2; }
.video-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 8px; color: #9fb3c8; }
.video-placeholder .vp-icon { font-size: 44px; }
.stu-detections { position: absolute; bottom: 6px; left: 6px; display: flex; gap: 4px; flex-wrap: wrap; z-index: 3; }
.det-tag { font-size: 11px; padding: 2px 6px; background: rgba(0,0,0,0.45); border-radius: 3px; }

.stu-score { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; display: flex; align-items: center; gap: 12px; }
.stu-score .score-ring { width: 64px; height: 64px; position: relative; flex-shrink: 0; }
.stu-score .score-ring .score-val { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; }
.stu-score .score-label { font-size: 13px; color: #9fb3c8; }
.stu-score .score-hint { font-size: 12px; color: #f8c537; margin-top: 2px; }

.tasks-box, .events-box, .disaster-box { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; }
.tb-head, .ev-head { display: flex; justify-content: space-between; align-items: center; font-weight: 600; margin-bottom: 8px; font-size: 13px; }
.tb-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.tb-list li { display: flex; align-items: flex-start; gap: 8px; padding: 6px 8px; border-radius: 6px; background: rgba(255,255,255,0.03); font-size: 13px; }
.tb-list li.done { background: rgba(66,211,156,0.1); color: #42d39c; }
.tb-list li.wrong { background: rgba(255,71,87,0.1); color: #ff4757; }
.tb-dot { flex-shrink: 0; width: 16px; }
.tb-text { flex: 1; font-weight: 600; }
.tb-sub { color: #9fb3c8; font-size: 12px; margin-left: 6px; }

.ev-list { max-height: 240px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
.ev-item { padding: 6px 8px; border-radius: 6px; border-left: 3px solid #888; background: rgba(255,255,255,0.04); font-size: 13px; }
.ev-item.ok { border-color: #42d39c; }
.ev-item.yellow { border-color: #e6a23c; }
.ev-item.orange { border-color: #ff9f43; }
.ev-item.red { border-color: #ff4757; background: rgba(255,71,87,0.1); animation: pulse 1s infinite; }
.ev-time { color: #9fb3c8; font-size: 11px; margin-right: 6px; }
.ev-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 10px; color: #000; background: var(--c, #888); margin-right: 6px; vertical-align: 2px; }
.ev-item.ok .ev-badge { background: #42d39c; }
.ev-item.yellow .ev-badge { background: #e6a23c; }
.ev-item.orange .ev-badge { background: #ff9f43; }
.ev-item.red .ev-badge { background: #ff4757; color: #fff; }
.ev-role { font-size: 11px; color: #9fb3c8; margin-right: 6px; }
.ev-text { color: #fff; }
.ev-empty { color: #9fb3c8; font-size: 12px; text-align: center; padding: 20px 0; }

.disaster-box { background: linear-gradient(135deg, rgba(255,71,87,0.15), rgba(255,107,129,0.05)); border: 1px solid rgba(255,71,87,0.4); }
.disaster-title { font-size: 13px; font-weight: 700; color: #ff6b81; margin-bottom: 4px; }
.disaster-text { font-size: 13px; }

@media (max-width: 800px) {
  .stu-body { grid-template-columns: 1fr; }
}
</style>
