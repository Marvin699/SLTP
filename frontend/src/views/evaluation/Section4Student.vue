<template>
  <div class="s4-stu">
    <div class="stu-header">
      <div class="stu-h-left">
        <span class="stu-badge" :style="{ background: group.color }">{{ group.id }}</span>
        <div>
          <div class="stu-title">{{ group.name }} · AI 智能体子系统</div>
          <div class="stu-sub">📍 {{ group.village }} · {{ group.task }}</div>
        </div>
      </div>
      <div class="stu-h-right">
        <span class="stu-stage">{{ stages[group.stage] }}</span>
        <span class="stu-timer">⏱ {{ formatTime(remainingSec) }}</span>
        <el-tag size="small" type="warning" effect="light">任务工单 · {{ group.standardShort }}</el-tag>
        <el-button v-if="!running" type="primary" size="small" @click="startRun">▶ 开始</el-button>
        <el-button v-else size="small" plain @click="stopRun">■ 暂停</el-button>
        <el-button size="small" plain @click="resetAll">⟲ 重置</el-button>
        <el-button size="small" plain @click="copyLink">🔗 分享链接</el-button>
      </div>
    </div>

    <div class="stu-body">
      <div class="stu-left">
        <div class="stu-video-wrap" :class="{ 'has-alert': hasAlert }" :data-gid="group.id">
          <video v-show="group.stream" ref="videoEl" autoplay muted playsinline></video>
          <div v-if="!group.stream" class="video-placeholder">
            <div class="vp-icon">📷</div>
            <div>摄像头未开启</div>
            <el-button size="small" type="primary" plain @click="startCamera(group)">
              点击开启摄像头
            </el-button>
          </div>
        </div>

        <div class="stu-control-row">
          <div v-if="cameraReady" class="camera-hint camera-hint--ok">✅ 摄像头已开启 · AI 识别运行中</div>
          <div v-if="cameraErrHint" class="camera-hint camera-hint--err">⚠️ {{ cameraErrHint }}</div>
          <div class="ai-check-row">
            <el-button size="small" type="warning" plain @click="() => triggerAiCheck('yellow')">⚠ 一般</el-button>
            <el-button size="small" type="danger" plain @click="() => triggerAiCheck('orange')">⚡ 严重</el-button>
            <el-button size="small" type="danger" @click="() => triggerAiCheck('red')">🔴 致命</el-button>
            <el-button size="small" plain @click="triggerAiCheck()">🔍 AI检查(随机)</el-button>
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
          <div class="score-meta">
            <div class="score-label">本次装载得分</div>
            <div class="score-hint">{{ scoreHint }}</div>
            <div class="rfid-tiny">📦 {{ group.rfidTagNo }}</div>
          </div>
        </div>

        <div class="roles-box">
          <div class="roles-head">👥 本组工位角色</div>
          <div class="roles-grid">
            <div v-for="r in group.roles" :key="r.role" class="role-chip">
              <span class="role-name">{{ r.name }}</span>
              <span class="role-label">{{ r.role }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="stu-right">
        <div class="tasks-box">
          <div class="tb-head">
            <span>📋 任务工单检查清单</span>
            <span class="tb-progress">{{ doneCount }}/{{ group.checklist.length }}</span>
          </div>
          <ul class="tb-list">
            <li v-for="(t, i) in myChecklist" :key="i" :class="t.state">
              <span class="tb-dot">{{ t.state === 'ok' ? '✓' : t.state === 'warn' ? '!' : '·' }}</span>
              <span class="tb-text">{{ t.label }}</span>
              <span v-if="t.state === 'warn'" class="tb-ai">AI 提醒</span>
            </li>
          </ul>
          <div class="tb-meta">
            <div>📦 物资：{{ group.rfidItems }}</div>
            <div>🚁 无人机：{{ group.rfidDrone }}</div>
            <div>📎 执行标准：{{ group.rfidStandard }}</div>
          </div>
        </div>

        <div class="events-box">
          <div class="ev-head">
            <span>🤖 AI 智能体实时提示</span>
            <el-tag size="small" :type="warnCount ? 'danger' : 'success'">{{ warnCount }} 条提醒</el-tag>
          </div>
          <div class="ev-list" ref="evLogRef">
            <div v-for="(ev, i) in group.events" :key="i" class="ev-item" :class="ev.level">
              <span class="ev-time">{{ ev.time }}</span>
              <span class="ev-badge">{{ ev.levelLabel }}</span>
              <span class="ev-role">{{ ev.role }}</span>
              <span class="ev-text">{{ ev.text }}</span>
            </div>
            <div v-if="!group.events.length" class="ev-empty">
              等待 AI 智能体检测你的操作...<br>
              <span class="ev-tip">点「开始」按钮，AI 将按脚本检测工单</span>
            </div>
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

const GROUP_LIBRARY = [
  {
    id: 1, name: '逐日组', village: '怀渠村', task: '2-8℃ 冷链疫苗', standardShort: 'T/CAEE 0001 第3.2条',
    color: '#5b8def',
    rfidItems: '重组乙型肝炎疫苗70支 · 破伤风抗毒素40支 · 30L保温箱 · 生物冰排6块 · EPE缓冲板2张 · 温度记录仪1台',
    rfidStandard: 'T/CAEE 0001—2026 第3.2条',
    rfidDrone: '百色市消防救援支队无人机A1-01',
    rfidTagNo: 'UHF-RFID-SN20260718-01',
    roles: [
      { role: '物资管理员', name: '黄燕玲' },
      { role: '包装员', name: '任子瑜' },
      { role: '装载员', name: '马正兴' },
      { role: '安全员', name: '黄秋云' },
    ],
    checklist: [
      { label: '保温箱预冷至 2~8℃', state: 'todo' },
      { label: '疫苗轻放 · 严禁倒置', state: 'todo', aiText: '疫苗瓶严禁倒置或剧烈晃动，否则药液失效', },
      { label: '四周用冰排填满间隙', state: 'todo', aiText: '冷链箱空隙必须用冰排填满，否则温度超标', },
      { label: '温度记录仪贴箱内壁', state: 'todo' },
      { label: 'RFID+冷链物资标识', state: 'todo' },
    ],
    presets: [
      { delay: 10000, level: 'orange', checkIdx: 1, role: 'AI智能体' },
      { delay: 30000, level: 'yellow', checkIdx: 3, role: 'AI智能体' },
    ],
  },
  {
    id: 2, name: '揽星组', village: '塘麻村', task: '-20℃ 深冷血浆', standardShort: 'WS/T823 第5条',
    color: '#a855f7',
    rfidItems: 'ABO血型血浆20袋 · 深冷转运箱 · 液氮罐 · 防爆冰盒6个 · 静电袋',
    rfidStandard: 'WS/T823-2023 第5条',
    rfidDrone: '百色市消防救援支队无人机A1-02',
    rfidTagNo: 'UHF-RFID-SN20260718-02',
    roles: [
      { role: '物资管理员', name: '欧兰彩' },
      { role: '包装员', name: '杨海琳' },
      { role: '装载员', name: '班丽峰' },
      { role: '安全员', name: '黄日胜' },
    ],
    checklist: [
      { label: '血浆袋逐袋检查有无渗漏', state: 'todo' },
      { label: '血浆袋套静电袋', state: 'todo' },
      { label: '深冷箱预冷至 -20℃', state: 'todo', aiText: '深冷箱必须预冷到 -20℃ 才能开始装血浆', },
      { label: '每层之间铺防爆冰盒', state: 'todo' },
      { label: 'RFID+生物制品标识', state: 'todo' },
    ],
    presets: [
      { delay: 12000, level: 'yellow', checkIdx: 0, role: 'AI智能体' },
      { delay: 32000, level: 'orange', checkIdx: 2, role: 'AI智能体' },
    ],
  },
  {
    id: 3, name: '御风组', village: '坡乐村', task: '避光防潮抗生素', standardShort: 'WS/T823+T/CAEE',
    color: '#6be6a1',
    rfidItems: '头孢曲松钠60瓶 · 阿莫西林钠克拉维酸钾40瓶 · 铝箔袋100个 · 黑色避光纸10张 · 防水胶带1卷 · 30L周转箱',
    rfidStandard: 'WS/T823-2023 第4.2条 + T/CAEE 0001—2026',
    rfidDrone: '百色市消防救援支队无人机A1-03',
    rfidTagNo: 'UHF-RFID-SN20260718-03',
    roles: [
      { role: '物资管理员', name: '王艳' },
      { role: '包装员', name: '莫经玉' },
      { role: '装载员', name: '陆荣旭' },
      { role: '安全员', name: '邹丽丽' },
    ],
    checklist: [
      { label: '抗生素药品用铝箔袋封装', state: 'todo', aiText: '抗生素必须用铝箔袋避光封装', },
      { label: '周转箱内衬黑色避光纸', state: 'todo' },
      { label: '箱内干燥剂不少于 5 袋', state: 'todo', aiText: '防潮干燥剂必须足量', },
      { label: '箱盖缝隙用防水胶带密封', state: 'todo' },
      { label: 'RFID+药品标识', state: 'todo' },
    ],
    presets: [
      { delay: 11000, level: 'yellow', checkIdx: 0, role: 'AI智能体' },
      { delay: 28000, level: 'yellow', checkIdx: 2, role: 'AI智能体' },
    ],
  },
  {
    id: 4, name: '雷霆组', village: '东风村', task: '急救包+氧气袋', standardShort: 'T/CAEE 0001 第2条',
    color: '#ff7a00',
    rfidItems: '急救包6个 · 氧气袋12个 · 压力计 · 止血带 · AED电极片',
    rfidStandard: 'T/CAEE 0001—2026 第2条',
    rfidDrone: '百色市消防救援支队无人机A1-04',
    rfidTagNo: 'UHF-RFID-SN20260718-04',
    roles: [
      { role: '物资管理员', name: '许严天' },
      { role: '包装员', name: '马雪冰' },
      { role: '装载员', name: '黄丽琴' },
      { role: '安全员', name: '吴日品' },
    ],
    checklist: [
      { label: '氧气袋压力预充 15kPa', state: 'todo', aiText: '氧气袋压力不足会在高空供氧失效', },
      { label: '急救包拉链全部朝外', state: 'todo' },
      { label: '止血带放在最上层易取处', state: 'todo' },
      { label: 'AED 电极片需单独密封', state: 'todo', aiText: 'AED电极片受潮失效', },
      { label: 'RFID+急救物资标识', state: 'todo' },
    ],
    presets: [
      { delay: 9000, level: 'red', checkIdx: 0, role: 'AI智能体' },
      { delay: 26000, level: 'yellow', checkIdx: 3, role: 'AI智能体' },
    ],
  },
  {
    id: 5, name: '雄鹰组', village: '古桥村', task: '高海拔抗晕药物', standardShort: 'WS/T823 第6条',
    color: '#f5222d',
    rfidItems: '红景天胶囊 · 葡萄糖口服液 · 氧气瓶 · 防寒毯 · 气压计',
    rfidStandard: 'WS/T823-2023 第6条',
    rfidDrone: '百色市消防救援支队无人机A1-05',
    rfidTagNo: 'UHF-RFID-SN20260718-05',
    roles: [
      { role: '物资管理员', name: '何雄松' },
      { role: '包装员', name: '陆彩兰' },
      { role: '装载员', name: '班艳丹' },
      { role: '安全员', name: '零正杰' },
    ],
    checklist: [
      { label: '药物按有效期排序 · 近效期先出', state: 'todo' },
      { label: '氧气瓶阀门用防尘膜密封', state: 'todo' },
      { label: '防寒毯压缩后排在四周', state: 'todo', aiText: '防寒毯必须压缩以节省空间', },
      { label: '气压计吸附在箱内壁中部', state: 'todo' },
      { label: 'RFID+高原救助标识', state: 'todo' },
    ],
    presets: [
      { delay: 13000, level: 'yellow', checkIdx: 2, role: 'AI智能体' },
      { delay: 33000, level: 'orange', checkIdx: 0, role: 'AI智能体' },
    ],
  },
  {
    id: 6, name: '迅捷组', village: '新和村', task: '危化品应急 · 酸碱中和', standardShort: 'GB 15603',
    color: '#13c2c2',
    rfidItems: '氢氧化钠中和剂 · 碳酸氢钠中和剂 · 防毒面具 · 防化手套 · 中和检测试纸',
    rfidStandard: 'GB 15603—1995 常用化学危险品贮存通则',
    rfidDrone: '百色市消防救援支队无人机A1-06',
    rfidTagNo: 'UHF-RFID-SN20260718-06',
    roles: [
      { role: '物资管理员', name: '苏彩桂' },
      { role: '包装员', name: '黄丽克' },
      { role: '装载员', name: '黄彩英' },
      { role: '安全员', name: '陆正福' },
    ],
    checklist: [
      { label: '酸/碱中和剂分箱隔离', state: 'todo', aiText: '酸碱严禁混装，混合会剧烈反应', },
      { label: '防毒面具检查滤毒罐有效期', state: 'todo' },
      { label: '防化手套内外各戴一层', state: 'todo' },
      { label: '检测试纸单独密封袋封装', state: 'todo' },
      { label: 'RFID+腐蚀性标识', state: 'todo' },
    ],
    presets: [
      { delay: 10000, level: 'red', checkIdx: 0, role: 'AI智能体' },
      { delay: 30000, level: 'orange', checkIdx: 2, role: 'AI智能体' },
    ],
  },
]

function resolveGroupId() {
  const q = route.query.group
  if (q) {
    const n = Number(q)
    if (!isNaN(n) && n >= 1 && n <= 6) return n
    const found = GROUP_LIBRARY.find(x => x.name === q)
    if (found) return found.id
  }
  return 1
}

const gid = resolveGroupId()
const _lib = GROUP_LIBRARY.find(x => x.id === gid) || GROUP_LIBRARY[0]

const group = reactive({
  ...JSON.parse(JSON.stringify(_lib)),
  stream: null,
  events: [],
  score: 85,
  scoreColor: '#42d39c',
  stage: 1,
})

const stages = ['待开始', '物资分拣', '包装装载', '固定贴标', '重心测量', '行前检查', '完成']

const myChecklist = computed(() => group.checklist)
const doneCount = computed(() => myChecklist.value.filter(c => c.state === 'ok').length)

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
const runTimers = ref([])
const cameraErrHint = ref('')
const cameraReady = ref(false)

let recChunks = []
let recGroupId = null
let recSeq = 0
const REC_SLICE_MS = 1000
let lastUploadSeq = -1

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

function autoMarkChecklist(level, checkIdx) {
  if (checkIdx != null && myChecklist.value[checkIdx]) {
    if (level === 'ok') {
      myChecklist.value[checkIdx].state = 'ok'
    } else {
      myChecklist.value[checkIdx].state = 'warn'
    }
  }
}

function emit(level, text, role = 'AI') {
  const scoreDelta = { ok: 1.5, yellow: -2, orange: -5, red: -10 }[level] || 0
  group.score = clampAndRound(group.score + scoreDelta)
  group.scoreColor = group.score >= 80 ? '#42d39c' : group.score >= 70 ? '#ffa94d' : '#ff4757'
  group.events.unshift({
    time: timeNow(), level, role, text, levelLabel: levelLabel(level),
  })
  if (group.events.length > 40) group.events.pop()
  if (level === 'ok') return
  speak(`${group.name}，${text}`)
  nextTick(() => {
    const log = document.querySelector('.ev-list')
    if (log) log.scrollTop = 0
  })
}

function runPresetAt(delay, p) {
  const t = setTimeout(() => {
    autoMarkChecklist(p.level, p.checkIdx)
    const text = p.text || myChecklist.value[p.checkIdx]?.aiText || `操作注意（${myChecklist.value[p.checkIdx]?.label || ''}）`
    emit(p.level, text, p.role || 'AI')
  }, delay)
  runTimers.value.push(t)
}

function tickScoreWave() {
  if (!running.value) return
  const n = gaussianNoise(0.8)
  group.score = clampAndRound(group.score + n, 55, 99)
  group.scoreColor = group.score >= 80 ? '#42d39c' : group.score >= 70 ? '#ffa94d' : '#ff4757'
  scoreWaveTimer.value = setTimeout(tickScoreWave, 600)
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

  group.presets.forEach(p => runPresetAt(p.delay, p))

  runTimers.value.push(setTimeout(() => {
    emit('ok', `小组开始装载，AI 智能体接管 · 目的地 ${group.village}`, '系统')
    speak(`${group.name}，现在开始任务，目的地 ${group.village}`)
  }, 100))

  runTimers.value.push(setTimeout(() => {
    disasterMsg.value = `风速 8m/s · 货物总重量不得超过 10kg，请压缩体积`
    emit('orange', `灾情：风速 8m/s · 货物总重量不得超过 10kg，请压缩体积`, '系统')
    speak(`灾情指令：风速 8 米每秒，货物总重量不得超过 10 公斤，请压缩体积`)
  }, 35000))

  runTimers.value.push(setTimeout(() => {
    emit('ok', `6 项关键检查点全部就绪，RFID 已绑定`, 'AI智能体')
    emit('ok', `温湿度读数 4.2℃ 稳定，密封胶条完整`, 'AI智能体')
  }, 55000))

  runTimers.value.push(setTimeout(() => {
    group.stage = 6
    emit('ok', `本组装载任务完成，请通知安全员核验成果`, 'AI智能体')
    speak(`${group.name}，任务完成，请通知安全员核验`)
  }, 90000))
}

function stopRun() {
  running.value = false
  if (timer.value) { clearInterval(timer.value); timer.value = null }
  if (scoreWaveTimer.value) { clearTimeout(scoreWaveTimer.value); scoreWaveTimer.value = null }
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
  disasterMsg.value = ''
  group.checklist.forEach(c => c.state = 'todo')
}

function copyLink() {
  const url = `${location.origin}${location.pathname}?group=${encodeURIComponent(group.name)}`
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制，可以发到群里或扫码进入')
  }).catch(() => {
    ElMessage.info(url)
  })
}

function pickMime() {
  const cand = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm', 'video/mp4']
  for (const m of cand) if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(m)) return m
  return 'video/webm'
}
function extFromMime(mime) {
  if (mime.includes('mp4')) return '.mp4'
  if (mime.includes('webm')) return '.webm'
  return '.webm'
}

function startUploader(g, stream) {
  recGroupId = g.id
  recChunks = []
  recSeq = 0
  lastUploadSeq = -1
  const mime = pickMime()
  const ext = extFromMime(mime)
  if (!mime) { console.warn('没有可用的 MediaRecorder mime'); return }
  console.log('[uploader] 使用 mimeType:', mime, 'ext:', ext)
  const groupNameEnc = encodeURIComponent(g.name || '')
  const sidEnc = encodeURIComponent(g.studentSessionId || 'anon')
  let mr
  try { mr = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 1_000_000 }) }
  catch (e) { mr = new MediaRecorder(stream); if (!mr) return }
  mr.ondataavailable = async (ev) => {
    if (!ev.data || ev.data.size === 0) return
    recSeq++
    const seq = recSeq
    const url = `/api/calls/upload?group_id=${g.id}&group_name=${groupNameEnc}&student_id=${sidEnc}&seq=${seq}&total=999`
    const form = new FormData()
    form.append('chunk', ev.data, `part_${String(seq).padStart(5,'0')}${ext}`)
    form.append('mime', mime)
    try {
      await fetch(url, { method: 'POST', body: form })
      lastUploadSeq = seq
    } catch (_) {}
  }
  mr.onstop = async () => {
    console.log('[uploader] MediaRecorder stopped, total chunks:', recSeq)
  }
  mr.start(REC_SLICE_MS)
  g.recorder = mr
}

function studentWsUrl() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${location.host}/api/calls/ws`
}

let studentFrameWs = null
let studentFrameTimer = null

function startFrameStream(g, videoEl) {
  try {
    const ws = new WebSocket(studentWsUrl())
    studentFrameWs = ws
    ws.addEventListener('open', () => {
      ws.send(JSON.stringify({ role: 'student', group_id: g.id }))
      console.log('[frame] WS connected for group', g.id)
    })
    ws.addEventListener('close', () => {
      studentFrameWs = null
      if (studentFrameTimer) { clearInterval(studentFrameTimer); studentFrameTimer = null }
      setTimeout(() => startFrameStream(g, videoEl), 2000)
    })
    ws.addEventListener('error', () => {})

    const hiddenCanvas = document.createElement('canvas')
    hiddenCanvas.width = 480
    hiddenCanvas.height = 360
    const hctx = hiddenCanvas.getContext('2d')

    studentFrameTimer = setInterval(() => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return
      if (!videoEl) return
      try {
        if (videoEl.videoWidth > 0 && !isNaN(videoEl.videoWidth)) {
          if (hiddenCanvas.width !== videoEl.videoWidth) hiddenCanvas.width = videoEl.videoWidth
          if (hiddenCanvas.height !== videoEl.videoHeight) hiddenCanvas.height = videoEl.videoHeight
        }
        hctx.drawImage(videoEl, 0, 0, hiddenCanvas.width, hiddenCanvas.height)
        hiddenCanvas.toBlob(async (blob) => {
          if (!blob || blob.size === 0) return
          try {
            const buf = await blob.arrayBuffer()
            const bytes = new Uint8Array(buf)
            let binary = ''
            for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
            const b64 = btoa(binary)
            ws.send(JSON.stringify({ type: 'frame', group_id: g.id, data: b64 }))
          } catch (_) {}
        }, 'image/jpeg', 0.5)
      } catch (_) {}
    }, 150)
  } catch (_) {}
}

function stopFrameStream() {
  if (studentFrameTimer) { clearInterval(studentFrameTimer); studentFrameTimer = null }
  if (studentFrameWs) { try { studentFrameWs.close() } catch (_) {}; studentFrameWs = null }
}

async function startCamera(g) {
  cameraErrHint.value = ''
  cameraReady.value = false
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 480, height: 360, facingMode: { ideal: 'environment' } },
      audio: false,
    })
    g.stream = stream
    group.stream = stream
    const v = document.querySelector('.stu-video-wrap video')
    if (v) {
      v.srcObject = stream
      v.muted = true
      v.playsInline = true
      try { await v.play() } catch (_) {}
      if (!v.videoWidth || v.videoWidth === 0) {
        await new Promise(res => {
          const h = () => { v.removeEventListener('loadedmetadata', h); res() }
          v.addEventListener('loadedmetadata', h)
          setTimeout(h, 2500)
        })
      }
    }
    await nextTick()
    await nextTick()
    cameraReady.value = true
    startUploader(g, stream)
    startFrameStream(g, v)
  } catch (e) {
    const name = e && e.name ? e.name : String(e)
    const m = {
      NotAllowedError: '未授予摄像头权限，请在浏览器地址栏左侧「🔒」授予权限后，重新点击"开启"',
      NotFoundError: '找不到摄像头设备',
      NotReadableError: '摄像头正被其他应用占用，请先关闭其他软件',
      OverconstraintError: '摄像头参数请求过高（已自动降级）',
      AbortError: '请求被中断',
      TypeError: '当前页面协议不支持摄像头（必须 HTTPS 或 localhost）',
    }
    cameraErrHint.value = m[name] || ('摄像头开启失败：' + (e && e.message ? e.message : name))
    ElMessage.error(cameraErrHint.value)
  }
}

function triggerAiCheck(forceLevel = null) {
  const lib = GROUP_LIBRARY.find(x => x.id === group.id)
  const aiList = lib ? (lib.aiKeys || lib.aiPresets || []) : []
  let pick = null
  let pickLevel = forceLevel
  if (forceLevel) {
    const byLevel = aiList.filter(k => k.level === forceLevel)
    if (byLevel.length) pick = byLevel[Math.floor(Math.random() * byLevel.length)]
  }
  if (!pick && aiList.length) {
    pick = aiList[Math.floor(Math.random() * aiList.length)]
    if (pick.level) pickLevel = pick.level
  }
  if (!pick) {
    const withAi = group.checklist.filter(c => c.aiText)
    if (withAi.length) {
      pick = withAi[Math.floor(Math.random() * withAi.length)]
      pickLevel = forceLevel || 'orange'
    }
  }
  let text = ''
  if (pick) {
    if (pick.text) text = pick.text
    else if (pick.aiText) text = pick.aiText
    else if (pick.checkIdx != null && group.checklist[pick.checkIdx]?.aiText) text = group.checklist[pick.checkIdx].aiText
  }
  if (!text) { ElMessage.info('本组暂无预设 AI 事件'); return }
  emit(pickLevel || 'yellow', String(text), 'AI智能体')
  speak(`${group.name}，${text}`)
}

onMounted(() => {})
onUnmounted(() => {
  stopFrameStream()
  stopRun()
  if (group.stream) group.stream.getTracks().forEach(t => t.stop())
  try { window.speechSynthesis.cancel() } catch {}
})
</script>

<style scoped>
.s4-stu { padding: 12px; color: #fff; min-height: 100vh; background: linear-gradient(135deg, #0b1728, #122740); font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; }
.stu-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.05); border-radius: 10px; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.stu-h-left { display: flex; align-items: center; gap: 10px; }
.stu-badge { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
.stu-title { font-size: 16px; font-weight: 700; }
.stu-sub { font-size: 12px; color: #9fb3c8; }
.stu-h-right { display: flex; align-items: center; gap: 8px; font-size: 13px; flex-wrap: wrap; }
.stu-stage { color: #6be6a1; background: rgba(107,230,161,0.1); padding: 4px 10px; border-radius: 4px; }
.stu-timer { font-variant-numeric: tabular-nums; color: #f8c537; font-weight: 600; }

.stu-body { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.stu-left, .stu-right { display: flex; flex-direction: column; gap: 12px; }

.stu-video-wrap { position: relative; aspect-ratio: 4/3; background: #000; border-radius: 12px; overflow: hidden; border: 2px solid transparent; }
.stu-video-wrap.has-alert { border-color: #ff4757; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.5); } 50% { box-shadow: 0 0 0 8px rgba(255,71,87,0); } }
.stu-video-wrap video { width: 100%; height: 100%; object-fit: cover; display: block; }
.video-placeholder { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 8px; color: #9fb3c8; z-index: 1; }
.video-placeholder .vp-icon { font-size: 44px; }

.stu-control-row { display: flex; flex-direction: column; gap: 8px; }
.camera-hint { font-size: 12px; padding: 6px 10px; border-radius: 6px; }
.camera-hint--ok { background: rgba(66,211,156,0.15); color: #42d39c; border: 1px solid rgba(66,211,156,0.3); }
.camera-hint--err { background: rgba(255,71,87,0.15); color: #ff6b81; border: 1px solid rgba(255,71,87,0.3); }
.ai-check-row { display: flex; flex-wrap: wrap; gap: 6px; }

.stu-score { display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }
.score-ring { width: 58px; height: 58px; position: relative; flex-shrink: 0; }
.score-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.score-val { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; }
.score-meta { flex: 1; min-width: 0; }
.score-label { font-size: 11px; color: #9fb3c8; }
.score-hint { font-size: 12px; font-weight: 600; color: #fff; }
.rfid-tiny { font-size: 10px; color: #6b8aab; margin-top: 2px; font-family: Menlo, monospace; }

.roles-box { background: rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }
.roles-head { font-size: 12px; color: #9fb3c8; margin-bottom: 6px; }
.roles-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
.role-chip { display: flex; flex-direction: column; background: rgba(255,255,255,0.06); padding: 6px 8px; border-radius: 6px; }
.role-name { font-size: 13px; font-weight: 700; color: #fff; }
.role-label { font-size: 10px; color: #9fb3c8; }

.tasks-box, .events-box, .disaster-box { background: rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }
.tb-head { display: flex; justify-content: space-between; font-size: 12px; color: #9fb3c8; margin-bottom: 8px; }
.tb-progress { font-variant-numeric: tabular-nums; color: #6be6a1; font-weight: 700; }
.tb-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.tb-list li { display: flex; align-items: center; gap: 6px; font-size: 13px; padding: 5px 8px; border-radius: 4px; background: rgba(255,255,255,0.05); }
.tb-list li.ok { color: #42d39c; }
.tb-list li.warn { color: #ffa94d; background: rgba(255,169,77,0.1); }
.tb-list li .tb-dot { font-weight: 800; }
.tb-list li .tb-ai { margin-left: auto; font-size: 10px; color: #ffa94d; }
.tb-meta { margin-top: 8px; font-size: 11px; color: #9fb3c8; line-height: 1.7; }

.ev-head { display: flex; justify-content: space-between; font-size: 12px; color: #9fb3c8; margin-bottom: 8px; align-items: center; }
.ev-list { display: flex; flex-direction: column; gap: 4px; max-height: 220px; overflow-y: auto; }
.ev-item { display: flex; align-items: center; gap: 6px; padding: 5px 8px; border-radius: 4px; background: rgba(255,255,255,0.05); font-size: 12px; }
.ev-item.ok { border-left: 3px solid #42d39c; }
.ev-item.yellow { border-left: 3px solid #e6a23c; }
.ev-item.orange { border-left: 3px solid #ff9f43; }
.ev-item.red { border-left: 3px solid #ff4757; }
.ev-time { color: #9fb3c8; font-size: 10px; margin-right: 6px; font-family: Menlo, monospace; }
.ev-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 10px; color: #000; background: var(--c, #888); margin-right: 6px; vertical-align: 2px; }
.ev-item.ok .ev-badge { background: #42d39c; }
.ev-item.yellow .ev-badge { background: #e6a23c; }
.ev-item.orange .ev-badge { background: #ff9f43; }
.ev-item.red .ev-badge { background: #ff4757; color: #fff; }
.ev-role { font-size: 10px; color: #9fb3c8; margin-right: 6px; }
.ev-text { color: #fff; }
.ev-empty { color: #9fb3c8; font-size: 12px; text-align: center; padding: 16px 0; line-height: 1.7; }
.ev-tip { color: #6be6a1; }

.disaster-box { background: linear-gradient(135deg, rgba(255,71,87,0.15), rgba(255,107,129,0.05)); border: 1px solid rgba(255,71,87,0.4); }
.disaster-title { font-size: 13px; font-weight: 700; color: #ff6b81; margin-bottom: 4px; }
.disaster-text { font-size: 13px; }

@media (max-width: 900px) {
  .stu-body { grid-template-columns: 1fr; }
  .roles-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
