<template>
  <div class="s4-live">
    <div class="s4-header">
      <div class="h-left">
        <h1>任务4 · 应急物资低空智慧运输装载与行前准备 · AI智能体大屏</h1>
        <span class="h-sub">渠阳镇特大水灾 · 6组同步装载 · 实时监控</span>
      </div>
      <div class="h-right">
        <div class="timer-box">
          <span class="timer-label">剩余时间</span>
          <span class="timer-value">{{ formatTime(remainingSec) }}</span>
        </div>
        <el-button v-if="!running" type="primary" size="large" @click="startRun">▶ 开始计时</el-button>
        <el-button v-else type="danger" size="large" plain @click="stopRun">■ 结束</el-button>
        <el-button size="large" plain @click="resetAll">⟲ 重置</el-button>
        <el-tag v-if="exhibitionOn" type="warning" effect="dark" size="large">展览模式</el-tag>
        <el-button type="warning" size="small" plain @click="exhibitionOn = !exhibitionOn">
          {{ exhibitionOn ? '关闭展览' : '开启展览' }}
        </el-button>
      </div>
    </div>

    <div class="s4-grid">
      <div v-for="g in groups" :key="g.id"
        class="group-card"
        :class="{ 'has-red': groupHasLevel(g, 'red'), 'has-orange': groupHasLevel(g, 'orange'), 'has-yellow': groupHasLevel(g, 'yellow'), 'focused': focusedGroup === g.id }"
        @click="focusedGroup = g.id">

        <div class="gc-head">
          <div class="gc-badge" :style="{ background: g.color }">{{ g.id }}</div>
          <div class="gc-title">
            <div class="gc-name">{{ g.name }}</div>
            <div class="gc-task">{{ g.task }}</div>
          </div>
          <div class="gc-stage">
            <span class="stage-dot" :class="getStageClass(g)"></span>
            <span>{{ stages[g.stage] }}</span>
          </div>
        </div>

        <div class="gc-body">
          <div class="gc-video">
            <video v-show="g.stream" :ref="el => setVideoRef(g.id, el)" autoplay muted playsinline></video>
            <div v-if="!g.stream" class="video-placeholder">
              <span>📷 等待摄像头</span>
              <el-button size="small" plain @click="startCamera(g)">开启</el-button>
            </div>
            <canvas class="video-overlay" :ref="el => setOverlayRef(g.id, el)"></canvas>
            <div v-if="g.detections.length" class="gc-detections">
              <div v-for="(d, i) in g.detections" :key="i" class="det-tag" :style="d.style">{{ d.label }}</div>
            </div>
          </div>

          <div class="gc-score">
            <div class="score-ring">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="44" stroke="rgba(255,255,255,0.1)" stroke-width="6" fill="none" />
                <circle cx="50" cy="50" r="44" :stroke="g.scoreColor" stroke-width="6" fill="none"
                  stroke-linecap="round" :stroke-dasharray="`${g.score/100 * 276} 276`" transform="rotate(-90 50 50)" />
              </svg>
              <div class="score-val">{{ g.score }}</div>
            </div>
            <div class="score-label">当前得分</div>
          </div>

          <div class="gc-events">
            <div class="ev-title">
              <span>AI 事件流</span>
              <el-tag size="small" :type="groupWarnCount(g) ? 'danger' : 'success'">
                {{ groupWarnCount(g) }} 问题
              </el-tag>
            </div>
            <div class="ev-list" ref="el => setEventLogRef(g.id, el)">
              <div v-for="(ev, i) in g.events" :key="i" class="ev-item" :class="ev.level">
                <span class="ev-time">{{ ev.time }}</span>
                <span class="ev-role">{{ ev.role }}</span>
                <span class="ev-text">{{ ev.text }}</span>
              </div>
              <div v-if="!g.events.length" class="ev-empty">暂无提示</div>
            </div>
          </div>
        </div>

        <div class="gc-quick">
          <el-button size="small" type="warning" plain @click="trigger(g.id, 'yellow')">⚠ 一般</el-button>
          <el-button size="small" type="danger" plain @click="trigger(g.id, 'orange')">⚡ 严重</el-button>
          <el-button size="small" type="danger" @click="trigger(g.id, 'red')">🔴 致命</el-button>
          <el-button size="small" @click="markGood(g.id)">✓ 确认合规</el-button>
          <el-button size="small" plain @click="startCamera(g)">📷 {{ g.stream ? '切' : '开' }}</el-button>
        </div>
      </div>
    </div>

    <div class="s4-control">
      <div class="ctrl-left">
        <h3>预设事件库</h3>
        <div class="preset-list">
          <div v-for="(p, i) in presets" :key="i" class="preset-item">
            <div class="preset-head">
              <el-tag :type="levelTagType(p.level)" size="small" effect="dark">{{ levelLabel(p.level) }}</el-tag>
              <span class="preset-groups">组 {{ p.groups.join(' / ') }}</span>
            </div>
            <div class="preset-text">{{ p.text }}</div>
            <div class="preset-actions">
              <el-button size="small" @click="applyPreset(p)">对选中组触发</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="ctrl-right">
        <h3>手动触发</h3>
        <el-input v-model="manualText" placeholder="事件描述，如：冰排直接接触疫苗会导致冻结失效" maxlength="120" />
        <div class="ctrl-row">
          <span>等级</span>
          <el-radio-group v-model="manualLevel">
            <el-radio-button value="yellow">一般</el-radio-button>
            <el-radio-button value="orange">严重</el-radio-button>
            <el-radio-button value="red">致命</el-radio-button>
          </el-radio-group>
        </div>
        <div class="ctrl-row">
          <span>目标组</span>
          <el-checkbox-group v-model="manualGroups">
            <el-checkbox v-for="g in groups" :key="g.id" :value="g.id">{{ g.id }}</el-checkbox>
          </el-checkbox-group>
        </div>
        <el-button type="primary" @click="fireManual">▶ 立即触发</el-button>

        <h3 style="margin-top: 18px">灾情事件</h3>
        <el-button size="small" type="warning" plain @click="disaster('伤员求助：2 名儿童被铁钉扎伤，急需破伤风疫苗，是否优先安排？')">伤员求助</el-button>
        <el-button size="small" type="warning" plain @click="disaster('风速 8m/s，货物总重量不得超过 10kg，否则飞行不安全')">风速警报</el-button>
        <el-button size="small" type="warning" plain @click="disaster('霍乱疑似病例，需额外增加 20 盒诺氟沙星胶囊')">霍乱疑似病例</el-button>

        <h3 style="margin-top: 18px">📱 学生端 · 扫码进入</h3>
        <div class="stu-qr-grid">
          <div v-for="g in groups" :key="g.id" class="stu-qr-card">
            <div class="stu-qr-header" :style="{ background: g.color }">{{ g.name }}</div>
            <img :src="qrImages[g.id]" :alt="g.name" class="stu-qr-img" />
            <div class="stu-qr-task">{{ g.task }}</div>
            <div class="stu-qr-actions">
              <a :href="stuLink(g)" target="_blank" class="stu-qr-link">打开</a>
              <el-button size="small" text @click="copyStuLink(g)">复制链接</el-button>
            </div>
          </div>
        </div>
        <p class="stu-links-hint">每组学生用手机扫描对应二维码，即可进入自己组的 AI 智能体子系统并开启摄像头</p>
      </div>
    </div>

    <el-dialog v-model="disasterDlg" title="灾情事件推送" width="620px" :close-on-click-modal="false">
      <div class="disaster-banner">
        <div class="disaster-icon">🚨</div>
        <div>
          <div class="disaster-title">突发灾情指令</div>
          <div class="disaster-text">{{ disasterMsg }}</div>
        </div>
      </div>
      <div class="disaster-actions">
        <el-button type="primary" @click="disasterAck('ack')">已告知各组</el-button>
        <el-button type="success" @click="disasterAck('adjust')">建议调整方案</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import QRCode from 'qrcode'

const groups = reactive([
  { id: 1, name: '逐日组', task: '2-8℃ 冷链疫苗', color: '#5b8def', stream: null, detections: [], events: [], score: 88.2, scoreColor: '#42d39c', stage: 1 },
  { id: 2, name: '揽星组', task: '-20℃ 深冷血浆', color: '#c77dff', stream: null, detections: [], events: [], score: 85.5, scoreColor: '#42d39c', stage: 1 },
  { id: 3, name: '驭风组', task: '避光防潮抗生素', color: '#6be6a1', stream: null, detections: [], events: [], score: 93.1, scoreColor: '#42d39c', stage: 2 },
  { id: 4, name: '长空组', task: '易碎防震注射液', color: '#ff9f43', stream: null, detections: [], events: [], score: 76.8, scoreColor: '#ffa94d', stage: 1 },
  { id: 5, name: '凌云组', task: '易燃危险品消毒品', color: '#ff6b81', stream: null, detections: [], events: [], score: 81.4, scoreColor: '#42d39c', stage: 1 },
  { id: 6, name: '巡天组', task: '多品类综合药品', color: '#74b9ff', stream: null, detections: [], events: [], score: 84.0, scoreColor: '#42d39c', stage: 1 },
])

const stages = ['待开始', '物资分拣', '包装装载', '固定贴标', '重心测量', '行前检查', '完成']

const presets = [
  { level: 'yellow', groups: [1], text: '请在冰排与疫苗之间放置 2cm 厚 EPE 缓冲材料，防止疫苗直接接触冰排导致冻结失效', role: 'AI智能体' },
  { level: 'yellow', groups: [2], text: '当前干冰重量 5.2kg，不足 8kg，请补充至 8kg 以上，确保运输过程中温度稳定在 -20℃ 以下', role: 'AI智能体' },
  { level: 'orange', groups: [4], text: '错误！玻璃安瓿瓶应竖直插入防震卡槽，请勿平放，防止运输中碰撞破碎', role: 'AI智能体' },
  { level: 'red',    groups: [5], text: '严重违规！酒精与 84 消毒液混装会产生有毒气体氯气，请立即用防火隔板将它们分隔在两个独立舱室！', role: 'AI智能体' },
  { level: 'yellow', groups: [6], text: '当前重心偏左 2.3cm，请调整右侧物资重量，使重心偏差控制在 ±1cm 以内', role: 'AI智能体' },
  { level: 'yellow', groups: [2], text: '干冰保温箱排气阀请保持打开，防止干冰挥发导致箱内压力过大', role: 'AI智能体' },
  { level: 'yellow', groups: [3], text: '正确！头孢曲松钠遇光会快速分解失效，已确认用铝箔袋完全避光包装 ✓', role: 'AI智能体' },
]

const running = ref(false)
const remainingSec = ref(600)
const exhibitionOn = ref(false)
const focusedGroup = ref(1)
const manualText = ref('')
const manualLevel = ref('yellow')
const manualGroups = ref([1, 2, 3, 4, 5, 6])
const disasterDlg = ref(false)
const disasterMsg = ref('')
const eventLogRefs = reactive({})
const videoRefs = reactive({})
const overlayRefs = reactive({})

let runTimer = null
let scoreTick = null
let detTick = null
let tickStart = 0

function formatTime(s) {
  const m = Math.floor(s / 60).toString().padStart(2, '0')
  const sec = (s % 60).toString().padStart(2, '0')
  return `${m}:${sec}`
}

function getStageClass(g) {
  const classes = ['wait', '', 'packing', 'packing', 'packing', 'packing', 'done']
  return classes[g.stage] || ''
}

function groupHasLevel(g, lv) { return g.events.some(e => e.level === lv) }
function groupWarnCount(g) { return g.events.filter(e => e.level === 'orange' || e.level === 'red').length }
function levelLabel(lv) { return lv === 'yellow' ? '一般' : lv === 'orange' ? '严重' : '致命' }
function levelTagType(lv) { return lv === 'yellow' ? 'warning' : lv === 'orange' ? 'danger' : 'danger' }

function stuLink(g) {
  return `${location.origin}/evaluation/task4/student?group=${encodeURIComponent(g.name)}`
}

const qrImages = reactive({})
async function buildQRs() {
  for (const g of groups) {
    try {
      qrImages[g.id] = await QRCode.toDataURL(stuLink(g), { margin: 1, scale: 3, width: 160 })
    } catch {
      qrImages[g.id] = ''
    }
  }
}

function copyStuLink(g) {
  const u = stuLink(g)
  navigator.clipboard.writeText(u).then(() => {
    ElMessage.success(`${g.name} 链接已复制`)
  }).catch(() => { ElMessage.info(u) })
}

function setVideoRef(id, el) { if (el) videoRefs[id] = el }
function setOverlayRef(id, el) { if (el) overlayRefs[id] = el }
function setEventLogRef(id, el) { if (el) eventLogRefs[id] = el }

function scrollLog(id) {
  requestAnimationFrame(() => {
    const el = eventLogRefs[id]
    if (el) el.scrollTop = el.scrollHeight
  })
}

function emit(groupId, level, text, role = 'AI智能体') {
  const g = groups.find(x => x.id === groupId)
  if (!g) return
  const t = new Date()
  const time = `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}:${String(t.getSeconds()).padStart(2, '0')}`
  g.events.push({ level, text, role, time })
  if (g.events.length > 20) g.events.shift()
  scrollLog(groupId)
  if (role === 'AI智能体' && text) speak(text)
  const color = level === 'yellow' ? '#e6a23c' : level === 'orange' ? '#ff6b81' : '#ff4757'
  ElMessage({ message: `【${g.name}·${levelLabel(level)}】${text}`, type: level === 'yellow' ? 'warning' : 'error', duration: 4000 })
  bumpScore(g, level)
}

function bumpScore(g, level) {
  const delta = level === 'yellow' ? -2 : level === 'orange' ? -5 : -10
  g.score = Math.max(0, Math.min(100, +(g.score + delta).toFixed(1)))
  updateScoreColor(g)
}

function updateScoreColor(g) {
  g.scoreColor = g.score >= 85 ? '#42d39c' : g.score >= 70 ? '#ffa94d' : '#ff4757'
}

function speak(text) {
  try {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text.slice(0, 180))
    u.lang = 'zh-CN'; u.rate = 1.05; u.pitch = 1
    window.speechSynthesis.speak(u)
  } catch {}
}

function trigger(groupId, level) {
  const g = groups.find(x => x.id === groupId)
  const pick = presets.filter(p => p.level === level && p.groups.includes(groupId))
  if (pick.length) {
    const p = pick[Math.floor(Math.random() * pick.length)]
    emit(groupId, level, p.text, p.role)
  } else {
    emit(groupId, level,
      level === 'red' ? '致命错误！立即暂停操作，当前动作存在重大安全隐患' :
      level === 'orange' ? '严重错误，请立即停止当前动作并按照标准流程整改' :
      '操作不规范，建议参考《无人机医疗救援运输操作指南》相关条款修正')
  }
}

function markGood(groupId) {
  const g = groups.find(x => x.id === groupId)
  if (!g) return
  emit(groupId, 'yellow', `${g.name} 已确认当前操作符合规范 ✓`, '教师')
  g.score = Math.min(100, +(g.score + 1.5).toFixed(1))
  updateScoreColor(g)
}

function applyPreset(p) {
  p.groups.forEach(gid => emit(gid, p.level, p.text, p.role))
}

function fireManual() {
  if (!manualText.value.trim()) return
  manualGroups.value.forEach(gid => emit(gid, manualLevel.value, manualText.value.trim(), '教师'))
  manualText.value = ''
}

function disaster(msg) {
  disasterMsg.value = msg
  disasterDlg.value = true
  emit(0, 'orange', `灾情指令：${msg}`, '指挥中心')
}

function disasterAck(action) {
  disasterDlg.value = false
  emit(3, 'yellow', action === 'adjust' ? '建议：驭风组方案调整为优先包装诺氟沙星胶囊，其他药品压缩重量应对风速限制' : '已向各组传达灾情事件，注意各组状态变化', '教师')
}

async function startCamera(g) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 360, facingMode: 'environment' }, audio: false })
    g.stream = stream
    await nextTick()
    const v = videoRefs[g.id]
    if (v) { v.srcObject = stream; v.play() }
    startFakeDetection(g)
  } catch (e) {
    ElMessage.warning('无法开启摄像头，可能权限被拒绝。将使用模拟画面')
    startFakeDetection(g, true)
  }
}

function startFakeDetection(g, noCamera = false) {
  const overlay = overlayRefs[g.id]
  const v = videoRefs[g.id]
  if (!overlay || (!v && !noCamera)) return

  const drawLoop = () => {
    const ov = overlayRefs[g.id]
    if (!ov) return
    let w = 480, h = 360
    if (v && v.videoWidth && v.videoHeight) { w = v.videoWidth; h = v.videoHeight }
    ov.width = w; ov.height = h
    const ctx = ov.getContext('2d')
    ctx.clearRect(0, 0, w, h)

    const nPeople = Math.max(0, Math.round(Math.random() * 2))
    const nBoxes = Math.max(1, Math.round(Math.random() * 3))
    g.detections = []

    for (let i = 0; i < nPeople; i++) {
      const x = 40 + Math.random() * (w - 120)
      const y = 30 + Math.random() * (h - 150)
      const bw = 60 + Math.random() * 30
      const bh = bw * 1.6
      ctx.strokeStyle = '#4fc3f7'; ctx.lineWidth = 2
      ctx.strokeRect(x, y, bw, bh)
      ctx.fillStyle = 'rgba(79, 195, 247, 0.18)'
      ctx.fillRect(x, y, bw, bh)
      ctx.fillStyle = '#4fc3f7'; ctx.font = 'bold 12px sans-serif'
      ctx.fillText('person ' + i, x + 4, y - 4)
      g.detections.push({ label: '人', style: { color: '#4fc3f7' } })
    }
    for (let i = 0; i < nBoxes; i++) {
      const x = 30 + Math.random() * (w - 140)
      const y = 80 + Math.random() * (h - 180)
      const bw = 80 + Math.random() * 40
      const bh = 60 + Math.random() * 40
      ctx.strokeStyle = '#ffb74d'; ctx.lineWidth = 2
      ctx.strokeRect(x, y, bw, bh)
      ctx.fillStyle = 'rgba(255, 183, 77, 0.14)'
      ctx.fillRect(x, y, bw, bh)
      const labels = ['保温箱', '药品盒', '防火箱', '防震盒']
      const lb = labels[Math.floor(Math.random() * labels.length)]
      ctx.fillStyle = '#ffb74d'; ctx.font = 'bold 12px sans-serif'
      ctx.fillText(lb, x + 4, y - 4)
      g.detections.push({ label: lb, style: { color: '#ffb74d' } })
    }

    if (g.stream || noCamera) {
      requestAnimationFrame(drawLoop)
    }
  }
  drawLoop()
}

function tickScoreWave() {
  groups.forEach(g => {
    if (!running.value && !exhibitionOn.value) return
    const sigma = 1.5
    const drift = (g.score - 83) * -0.04
    const noise = (Math.random() - 0.5) * sigma * 2
    g.score = Math.max(0, Math.min(100, +(g.score + noise + drift).toFixed(1)))
    updateScoreColor(g)

    if (running.value || exhibitionOn.value) {
      const elapsed = (Date.now() - tickStart) / 1000
      if (elapsed > 60) {
        g.stage = Math.min(6, Math.max(1, Math.round(1 + elapsed / 8)))
      } else if (elapsed > 10) g.stage = Math.min(6, Math.max(1, Math.round(elapsed / 4)))
    }
  })
}

function startRun() {
  running.value = true
  remainingSec.value = 600
  tickStart = Date.now()
  groups.forEach(g => {
    g.stage = 1; g.events = []
    g.score = 85 + (Math.random() - 0.5) * 8
    updateScoreColor(g)
  })
  emit(0, 'yellow', '计时开始！6组请立即就位，10 分钟内完成标准化包装与装载任务', '指挥中心')
  runTimer = setInterval(() => {
    if (remainingSec.value > 0) remainingSec.value--
    else { stopRun(); ElMessage.success('时间到！所有小组停止操作，请展示货盘') }
  }, 1000)
  scoreTick = setInterval(tickScoreWave, 400)
  detTick = setInterval(() => {
    groups.forEach(g => {
      if (g.stream) startFakeDetection(g)
    })
  }, 2000)

  setTimeout(() => trigger(1, 'yellow'), 8000)
  setTimeout(() => trigger(2, 'yellow'), 16000)
  setTimeout(() => applyPreset(presets[6]), 24000)
  setTimeout(() => trigger(4, 'orange'), 32000)
  setTimeout(() => trigger(5, 'red'), 42000)
  setTimeout(() => applyPreset(presets[3]), 50000)
  setTimeout(() => trigger(6, 'yellow'), 60000)
  setTimeout(() => disaster('风速 8m/s，货物总重量不得超过 10kg，否则飞行不安全'), 70000)
  setTimeout(() => disaster('霍乱疑似病例，需额外增加 20 盒诺氟沙星胶囊，请立即调整'), 140000)
}

function stopRun() {
  running.value = false
  clearInterval(runTimer); runTimer = null
  clearInterval(scoreTick); scoreTick = null
  clearInterval(detTick); detTick = null
}

function resetAll() {
  stopRun()
  remainingSec.value = 600
  groups.forEach(g => {
    g.events = []; g.score = 85; updateScoreColor(g); g.stage = 1
    if (g.stream) { g.stream.getTracks().forEach(t => t.stop()); g.stream = null }
  })
}

onMounted(() => {
  groups.forEach(g => { updateScoreColor(g) })
  buildQRs()
})

onUnmounted(() => {
  stopRun()
  groups.forEach(g => {
    if (g.stream) g.stream.getTracks().forEach(t => t.stop())
  })
  try { window.speechSynthesis.cancel() } catch {}
})
</script>

<style scoped>
.s4-live { display: flex; flex-direction: column; gap: 16px; padding: 16px; height: calc(100vh - 110px); overflow: auto; background: linear-gradient(160deg, #0a1a2e 0%, #16213e 60%, #0f3460 100%); color: #e6ebf5; }
.s4-header { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 20px; backdrop-filter: blur(6px); }
.s4-header h1 { margin: 0; font-size: 18px; font-weight: 700; letter-spacing: 1px; }
.h-sub { margin-left: 12px; font-size: 12px; opacity: 0.75; }
.h-right { display: flex; gap: 10px; align-items: center; }
.timer-box { display: flex; flex-direction: column; align-items: center; padding: 0 16px; border-left: 1px solid rgba(255,255,255,0.15); border-right: 1px solid rgba(255,255,255,0.15); }
.timer-label { font-size: 11px; opacity: 0.6; }
.timer-value { font-family: 'SF Mono', Menlo, monospace; font-size: 26px; font-weight: 700; color: #4fc3f7; }

.s4-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; flex: 1; }
.group-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 10px; transition: all .2s; position: relative; }
.group-card:hover { transform: translateY(-2px); border-color: rgba(79, 195, 247, 0.4); }
.group-card.focused { outline: 2px solid #4fc3f7; }
.group-card.has-yellow { box-shadow: inset 0 0 0 1px rgba(230,162,60,0.5), 0 0 18px rgba(230,162,60,0.15); }
.group-card.has-orange { box-shadow: inset 0 0 0 1px rgba(255,107,129,0.55), 0 0 22px rgba(255,107,129,0.2); }
.group-card.has-red { box-shadow: inset 0 0 0 1px rgba(255,71,87,0.7), 0 0 28px rgba(255,71,87,0.3); }

.gc-head { display: flex; align-items: center; gap: 10px; }
.gc-badge { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px; color: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }
.gc-title { flex: 1; }
.gc-name { font-weight: 700; font-size: 15px; }
.gc-task { font-size: 11px; opacity: 0.7; }
.gc-stage { display: flex; align-items: center; gap: 6px; font-size: 11px; opacity: 0.7; }
.stage-dot { width: 8px; height: 8px; border-radius: 50%; background: #555; }
.stage-dot.packing { background: #ffa94d; box-shadow: 0 0 8px #ffa94d; }
.stage-dot.done { background: #42d39c; box-shadow: 0 0 8px #42d39c; }
.stage-dot.wait { background: #666; }

.gc-body { display: grid; grid-template-columns: 1fr 80px; gap: 10px; }
.gc-video { position: relative; background: #000; border-radius: 8px; aspect-ratio: 4/3; overflow: hidden; min-height: 150px; }
.gc-video video { width: 100%; height: 100%; object-fit: cover; }
.video-placeholder { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; font-size: 13px; opacity: 0.6; }
.video-overlay { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.gc-detections { position: absolute; top: 6px; left: 6px; display: flex; flex-direction: column; gap: 3px; }
.det-tag { font-size: 10px; padding: 2px 6px; background: rgba(0,0,0,0.55); border-radius: 3px; font-family: monospace; }

.gc-score { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.score-ring { position: relative; width: 70px; height: 70px; }
.score-ring svg { width: 100%; height: 100%; transform: scale(1); }
.score-val { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; font-family: monospace; }
.score-label { font-size: 10px; opacity: 0.6; margin-top: 4px; }

.gc-events { background: rgba(0,0,0,0.25); border-radius: 8px; padding: 8px; margin-top: 6px; }
.ev-title { display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 6px; opacity: 0.85; }
.ev-list { max-height: 90px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.ev-item { display: flex; gap: 6px; font-size: 12px; padding: 4px 6px; border-radius: 5px; background: rgba(255,255,255,0.04); }
.ev-item.yellow { background: rgba(230,162,60,0.18); border-left: 2px solid #e6a23c; }
.ev-item.orange { background: rgba(255,107,129,0.2); border-left: 2px solid #ff6b81; }
.ev-item.red { background: rgba(255,71,87,0.25); border-left: 2px solid #ff4757; animation: pulseRed 1.2s infinite; }
@keyframes pulseRed { 0%,100% { opacity: 1 } 50% { opacity: 0.7 } }
.ev-time { font-family: monospace; font-size: 10px; opacity: 0.6; min-width: 60px; }
.ev-role { font-weight: 700; min-width: 70px; }
.ev-text { flex: 1; }
.ev-empty { text-align: center; opacity: 0.5; font-size: 12px; padding: 8px 0; }

.gc-quick { display: flex; gap: 6px; flex-wrap: wrap; }

.s4-control { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; background: rgba(255,255,255,0.04); border-radius: 12px; padding: 14px 18px; border: 1px solid rgba(255,255,255,0.08); }
.s4-control h3 { margin: 0 0 10px; font-size: 14px; }
.preset-list { display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; }
.preset-item { background: rgba(0,0,0,0.25); border-radius: 8px; padding: 8px 10px; }
.preset-head { display: flex; gap: 8px; align-items: center; margin-bottom: 4px; }
.preset-groups { font-size: 11px; opacity: 0.7; }
.preset-text { font-size: 12px; line-height: 1.5; }
.preset-actions { margin-top: 6px; }

.ctrl-row { display: flex; align-items: center; gap: 8px; margin: 8px 0; font-size: 13px; }

.disaster-banner { display: flex; gap: 14px; align-items: center; background: linear-gradient(120deg, #ff475722, #ffa94d22); border-left: 4px solid #ff4757; border-radius: 8px; padding: 14px; margin: 12px 0; }
.disaster-icon { font-size: 38px; }
.disaster-title { font-weight: 700; font-size: 15px; margin-bottom: 6px; }
.disaster-text { font-size: 13px; line-height: 1.6; }
.disaster-actions { display: flex; gap: 10px; justify-content: flex-end; }

.stu-qr-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 8px; }
.stu-qr-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 8px 8px 10px; text-align: center; }
.stu-qr-header { color: #fff; font-weight: 700; font-size: 13px; padding: 5px 8px; border-radius: 6px; margin-bottom: 6px; letter-spacing: 1px; }
.stu-qr-img { width: 140px; height: 140px; background: #fff; border-radius: 6px; padding: 4px; }
.stu-qr-task { font-size: 11px; color: #9fb3c8; margin-top: 4px; }
.stu-qr-actions { margin-top: 4px; display: flex; justify-content: center; gap: 8px; }
.stu-qr-link { color: #f8c537; font-size: 12px; text-decoration: none; }
.stu-qr-link:hover { text-decoration: underline; }
.stu-links-hint { font-size: 12px; color: #9fb3c8; margin-top: 10px; line-height: 1.5; }
</style>
