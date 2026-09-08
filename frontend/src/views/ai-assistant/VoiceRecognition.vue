<template>
  <div class="voice-page">
    <!-- 星空背景 -->
    <div class="starfield" aria-hidden="true">
      <div class="stars stars-1"></div>
      <div class="stars stars-2"></div>
    </div>

    <!-- 页头 -->
    <header class="page-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" width="15" height="15"><path fill="currentColor" d="M15.4 7.4 14 6l-6 6 6 6 1.4-1.4L10.8 12z"/></svg>
        返回助教
      </button>
      <div class="title-row">
        <span class="title-bar"></span>
        <h1>语音识别 · 汇报考核</h1>
        <span class="title-sub">无人机操作口令 · 实时识别比对评分</span>
      </div>
      <div class="header-actions">
        <button class="clear-btn" @click="clearAllScores" title="清空所有小组的识别成绩">
          <svg viewBox="0 0 24 24" width="13" height="13"><path fill="currentColor" d="M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6zM19 4h-3.5l-1-1h-5l-1 1H5v2h14z"/></svg>
          清空成绩
        </button>
        <div class="header-status">
          <span class="engine-dot"></span>
          识别引擎在线
        </div>
      </div>
    </header>

    <!-- 小组选择 -->
    <div class="group-row">
      <div
        v-for="g in groupList"
        :key="g.id"
        class="group-card"
        :class="{ active: selectedGroupId === g.id, disabled: phase === 'recognizing' }"
        @click="selectGroup(g.id)"
      >
        <div class="group-flag" :class="g.id">{{ g.name.slice(0, 1) }}</div>
        <div class="group-info">
          <div class="group-name">{{ g.name }}</div>
          <div class="group-meta">
            <span class="lang-badge" :class="g.id">{{ g.langLabel }}</span>
            <span class="member-count">6 人</span>
          </div>
        </div>
        <div class="group-score" v-if="finishedGroups[g.id]">
          <div class="score-main">
            <span class="score-num" :class="scoreLevelClass(finishedGroups[g.id].score)">{{ finishedGroups[g.id].score }}</span>
            <span class="score-unit">分</span>
          </div>
          <span class="score-time">{{ finishedGroups[g.id].time }}完成</span>
        </div>
      </div>
    </div>

    <!-- 主对照区 -->
    <div class="main-panels">
      <!-- 左：标准口令 -->
      <section class="panel std-panel">
        <div class="panel-head">
          <span class="panel-title">
            <svg viewBox="0 0 24 24" width="15" height="15"><path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zm2 16H8v-2h8zm0-4H8v-2h8zm-3-5V3.5L18.5 9z"/></svg>
            标准口令卡
          </span>
          <span class="panel-tag">共 {{ standardLines.length }} 句</span>
        </div>
        <div class="std-list" ref="stdListRef">
          <div
            v-for="(line, i) in standardLines"
            :key="i"
            class="std-item"
            :class="{ current: i === currentIndex, passed: i < currentIndex }"
            :ref="el => setStdItemRef(el, i)"
          >
            <span class="line-no">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="line-text">{{ line }}</span>
            <span class="line-check" v-if="i < currentIndex">
              {{ getLineMark(i) }}
            </span>
          </div>
        </div>
      </section>

      <!-- 右：识别结果 -->
      <section class="panel result-panel">
        <div class="panel-head">
          <span class="panel-title">
            <svg viewBox="0 0 24 24" width="15" height="15"><path fill="currentColor" d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3m5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V22h2v-3.08A7 7 0 0 0 19 12z"/></svg>
            实时识别结果
            <span v-if="selectedGroup" class="panel-lang">{{ selectedGroup.name }} · {{ selectedGroup.langLabel }}</span>
          </span>
          <span class="panel-tag live">
            <span v-if="phase === 'recognizing'" class="rec-dot"></span>
            {{ phaseText }}
          </span>
        </div>

        <!-- 未选择组 -->
        <div v-if="!selectedGroup" class="result-empty">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" width="42" height="42"><path fill="currentColor" d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3m5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V22h2v-3.08A7 7 0 0 0 19 12z"/></svg>
          </div>
          <p>请先选择小组，开始语音识别考核</p>
        </div>

        <!-- 识别结果列表 -->
        <div v-else class="result-list" ref="resultListRef">
          <div
            v-for="(r, i) in results"
            :key="i"
            class="result-item"
            :class="r.done ? r.status : 'typing'"
          >
            <span class="result-no">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="result-text">{{ r.displayText }}<span v-if="!r.done" class="type-caret"></span></span>
            <span class="result-mark">{{ r.done ? statusMark(r.status) : '···' }}</span>
          </div>
          <div v-if="phase === 'recognizing'" class="recognizing-hint">
            <span class="wave-mini"><i></i><i></i><i></i></span>
            {{ listeningHint }}
          </div>
        </div>

        <!-- 得分面板 -->
        <transition name="score-pop">
          <div v-if="phase === 'done' && selectedGroup" class="score-panel">
            <div class="score-ring">
              <svg viewBox="0 0 120 120" width="120" height="120">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/>
                <circle
                  cx="60" cy="60" r="52" fill="none"
                  :stroke="scoreColor"
                  stroke-width="8" stroke-linecap="round"
                  :stroke-dasharray="2 * Math.PI * 52"
                  :stroke-dashoffset="2 * Math.PI * 52 * (1 - displayScore / 100)"
                  transform="rotate(-90 60 60)"
                  style="transition: stroke-dashoffset 1.2s ease-out; filter: drop-shadow(0 0 8px currentColor);"
                />
              </svg>
              <div class="score-center">
                <span class="score-value">{{ displayScore }}</span>
                <span class="score-label">得分</span>
              </div>
            </div>
            <div class="score-detail">
              <div class="detail-row">
                <span class="detail-label">口令正确率</span>
                <span class="detail-value">{{ selectedGroup.accuracy }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">错误 / 部分正确</span>
                <span class="detail-value">{{ wrongCount }} / {{ partialCount }} 句</span>
              </div>
              <div class="detail-comment">{{ scoreComment }}</div>
            </div>
          </div>
        </transition>
      </section>
    </div>

    <!-- 底部控制条 -->
    <footer class="control-bar">
      <canvas v-if="phase === 'recognizing'" ref="waveCanvas" class="wave-canvas" width="220" height="40"></canvas>
      <div v-else class="control-hint">{{ controlHint }}</div>
      <div class="control-actions">
        <el-button
          v-if="phase !== 'recognizing' && phase !== 'done'"
          type="primary"
          size="large"
          round
          :disabled="!selectedGroup"
          @click="startRecognition"
        >
          <el-icon style="margin-right: 6px"><Microphone /></el-icon>
          开始语音识别
        </el-button>
        <el-button
          v-else-if="phase === 'recognizing'"
          type="info"
          size="large"
          round
          disabled
        >
          识别进行中...
        </el-button>
        <el-button
          v-else
          type="warning"
          size="large"
          round
          @click="resetRecognition"
        >
          <el-icon style="margin-right: 6px"><RefreshRight /></el-icon>
          重新识别
        </el-button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Microphone, RefreshRight } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()

function goBack() {
  router.push('/ai-assistant')
}

// ===== 标准口令（20句） =====
const standardLines = [
  '检查机臂，卡扣锁死，无松动，正常。',
  '检查桨叶，无损伤，AB桨安装正确，转动正常。',
  '检查机身脚架，结构完好，无变形，正常。',
  '检查降落伞指示灯，应急装置正常。',
  '检查电池，无鼓包，电量充足，正常。',
  '吊绳无磨损断丝，正常。',
  '负载捆绑牢固，检查完毕。',
  '遥控器开机完成，航电系统正常。',
  '天线展开到位，通信信号正常。',
  '电量充足，图传画面流畅，正常。',
  '遵循开机顺序，飞行器开始自检。',
  'IMU、指南针、雷达无告警，正常。',
  'GPS信号稳定，无磁场干扰，正常。',
  '关闭飞行器与遥控器，整机断电放电。',
  '取下电池，放置安全区域。',
  '按压卡扣，拔除分电接头。',
  '分电接头卡入收纳卡槽，固定牢固，分电线路放至挡板后，无遮挡。',
  '安装电池，卡扣锁紧，无松动。',
  '整机开机，无供电告警。',
  '重新开机，双电转单电操作完成。'
]

// ===== 三组演示数据 =====
// 巡天组：全对 100 分
const xuntianLines = standardLines.map(text => ({ text, status: 'correct' }))

// 长空组（柬埔寨学生）：高棉语识别结果，第10句部分正确，98 分
const changkongRaw = [
  'ពិនិត្យដៃយន្តហោះ សោបិទជិត គ្មានរលុង ធម្មតា។',
  'ពិនិត្យស្លាបវិល គ្មានខូចខាត ការដំឡើងស្លាប A/B ត្រឹមត្រូវ បង្វិលធម្មតា។',
  'ពិនិត្យជើងទ្រតួយន្តហោះ រចនាសម្ព័ន្ធល្អឥតខ្ចោះ គ្មានខូចទ្រង់ទ្រាយ ធម្មតា។',
  'ពិនិត្យភ្លើងសញ្ញាឆ័ត្រយោង ឧបករណ៍សង្គ្រោះបន្ទាន់ធម្មតា។',
  'ពិនិត្យថ្ម គ្មានប៉ោង ថាមពលគ្រប់គ្រាន់ ធម្មតា។',
  'ខ្សែព្យួរគ្មានការរលុប ឬដាច់សរសៃ ធម្មតា។',
  'ការចងទំនិញរឹងមាំ ការត្រួតពិនិត្យបានបញ្ចប់។',
  'ការបើកឧបករណ៍បញ្ជាពីចម្ងាយបានបញ្ចប់ ប្រព័ន្ធអេឡិចត្រូនិកអាកាសចរណ៍ធម្មតា។',
  'អង់តែនលាតដល់ទីតាំង សញ្ញាទំនាក់ទំនងធម្មតា។',
  'ថាមពលគ្រប់គ្រាន់ រូបភាពបញ្ជូនហូររលូន ធម្មតា។',
  'អនុវត្តតាមលំដាប់នៃការបើកម៉ាស៊ីន យន្តហោះចាប់ផ្តើមត្រួតពិនិត្យដោយខ្លួនឯង។',
  'IMU ត្រីវិស័យ រ៉ាដា គ្មានការជូនដំណឹង ធម្មតា។',
  'សញ្ញា GPS មានស្ថេរភាព គ្មានការរំខានដែនម៉ាញេទិច ធម្មតា។',
  'បិទយន្តហោះ និងឧបករណ៍បញ្ជាពីចម្ងាយ ផ្តាច់ចរន្តអគ្គិសនីទាំងស្រុង។',
  'ដកថ្មចេញ ដាក់ក្នុងតំបន់សុវត្ថិភាព។',
  'ចុចសោ ដកឧបករណ៍ភ្ជាប់ចរន្តអគ្គិសនីចេញ។',
  'ឧបករណ៍ភ្ជាប់ចរន្តអគ្គិសនីចាប់ចូលរន្ធទុកដាក់ ជាប់រឹងមាំ ខ្សែចរន្តអគ្គិសនីដាក់ក្រោយបន្ទះការពារ គ្មានការបិទបាំង។',
  'ដំឡើងថ្ម ចាក់សោឱ្យជិត គ្មានរលុង។',
  'បើកម៉ាស៊ីនទាំងមូល គ្មានការជូនដំណឹងអំពីការផ្គត់ផ្គង់ថាមពល។',
  'បើកម៉ាស៊ីនម្តងទៀត ការប្តូរពីថ្មពីរទៅថ្មមួយបានបញ្ចប់។'
]
const changkongLines = changkongRaw.map((text, i) => ({
  text,
  status: i === 9 ? 'partial' : 'correct'
}))

// 御风组：正确率 89%，得分 89
// TODO(御风组): 错字数据待补充，当前第 5、17 句为占位错误，拿到错字数据后替换
const yufengPlaceholderWrong = new Set([4, 16])
const yufengLines = standardLines.map((text, i) => ({
  text,
  status: yufengPlaceholderWrong.has(i) ? 'wrong' : 'correct'
}))

const groupList = [
  { id: 'xuntian', name: '巡天组', langLabel: '普通话', score: 100, accuracy: '100%', lines: xuntianLines },
  { id: 'changkong', name: '长空组', langLabel: '高棉语', score: 98, accuracy: '98%', lines: changkongLines },
  { id: 'yufeng', name: '御风组', langLabel: '普通话', score: 89, accuracy: '89%', lines: yufengLines }
]

// ===== 状态 =====
const selectedGroupId = ref(null)
const phase = ref('idle') // idle | recognizing | done
const currentIndex = ref(-1)
const results = ref([])
const finishedGroups = ref({})
const stdListRef = ref(null)
const resultListRef = ref(null)
const waveCanvas = ref(null)
const stdItemRefs = []
let animFrame = null
let waveHeights = []
let aborted = false

// 得分持久化：不同时间识别的小组，分数都保留显示
const SCORE_KEY = 'sltp_voice_scores'
function loadFinished() {
  try {
    const raw = localStorage.getItem(SCORE_KEY)
    if (raw) finishedGroups.value = JSON.parse(raw)
  } catch (e) { /* 忽略损坏数据 */ }
}
function saveFinished() {
  try {
    localStorage.setItem(SCORE_KEY, JSON.stringify(finishedGroups.value))
  } catch (e) { /* 忽略写入失败 */ }
}
loadFinished()

function setStdItemRef(el, i) {
  if (el) stdItemRefs[i] = el
}

const selectedGroup = computed(() => groupList.find(g => g.id === selectedGroupId.value) || null)

const phaseText = computed(() => {
  if (phase.value === 'recognizing') return `识别中 ${currentIndex.value + 1}/${standardLines.length}`
  if (phase.value === 'done') return '识别完成'
  return '待开始'
})

const listeningHint = computed(() => {
  if (phase.value !== 'recognizing') return ''
  return currentIndex.value < 0 ? '正在聆听小组汇报...' : `正在聆听 · 第 ${currentIndex.value + 1} 句`
})

const controlHint = computed(() => {
  if (!selectedGroup.value) return '选择小组后点击「开始语音识别」'
  if (phase.value === 'done') return `${selectedGroup.value.name} 汇报识别完成`
  return `已选择 ${selectedGroup.value.name} · 准备就绪`
})

const wrongCount = computed(() => results.value.filter(r => r.status === 'wrong').length)
const partialCount = computed(() => results.value.filter(r => r.status === 'partial').length)

const displayScore = computed(() => (phase.value === 'done' && selectedGroup.value ? selectedGroup.value.score : 0))

const scoreColor = computed(() => {
  const s = displayScore.value
  if (s >= 95) return '#67c23a'
  if (s >= 85) return '#e6a23c'
  return '#f56c6c'
})

const scoreComment = computed(() => {
  const s = displayScore.value
  if (s >= 95) return '口令汇报完整流畅，操作术语规范，继续保持。'
  if (s >= 85) return '整体汇报良好，个别口令发音或术语需课后纠正。'
  return '口令完成度不足，建议对照标准口令卡加强训练。'
})

function statusMark(status) {
  if (status === 'correct') return '✓'
  if (status === 'partial') return '⚠'
  return '✗'
}

function getLineMark(i) {
  const r = results.value[i]
  if (!r) return ''
  return statusMark(r.status)
}

function scoreLevelClass(score) {
  if (score >= 95) return 'lv-good'
  if (score >= 85) return 'lv-mid'
  return 'lv-bad'
}

// ===== 交互 =====
function selectGroup(id) {
  if (phase.value === 'recognizing') return
  if (selectedGroupId.value !== id) {
    selectedGroupId.value = id
    resetState()
  }
}

function resetState() {
  phase.value = 'idle'
  currentIndex.value = -1
  results.value = []
  stdItemRefs.length = 0
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 模拟真实节奏：按句长计算朗读时长，高棉语音节字符多，封顶处理
function listenDuration(text) {
  return Math.min(3000, Math.max(1100, text.length * 85)) + Math.random() * 350
}
function typeInterval() {
  return 14 + Math.random() * 20
}

async function startRecognition() {
  if (!selectedGroup.value || phase.value === 'recognizing') return
  resetState()
  phase.value = 'recognizing'
  await nextTick()
  drawWave()
  await sleep(1000) // 引擎启动缓冲
  if (aborted) return

  const lines = selectedGroup.value.lines
  for (let i = 0; i < lines.length; i++) {
    if (aborted) return
    // 1. 聆听阶段：左栏高亮该句，按真实朗读速度推进
    currentIndex.value = i
    scrollStdTo(i)
    await sleep(listenDuration(lines[i].text))
    if (aborted) return

    // 2. 识别转写阶段：逐字打出，此时为灰色待判定
    // 必须用 reactive 包装，普通对象修改属性不会触发视图更新
    const item = reactive({ text: lines[i].text, status: lines[i].status, displayText: '', done: false })
    results.value.push(item)
    scrollResultToBottom()
    for (let j = 1; j <= item.text.length; j++) {
      if (aborted) return
      item.displayText = item.text.slice(0, j)
      if (j % 4 === 0) scrollResultToBottom()
      await sleep(typeInterval())
    }
    // 3. 判定时刻：整句瞬间变色（绿/黄/红）
    item.done = true
    scrollResultToBottom()
    await sleep(320)
  }

  currentIndex.value = -1
  phase.value = 'done'
  const now = new Date()
  finishedGroups.value[selectedGroupId.value] = {
    score: selectedGroup.value.score,
    accuracy: selectedGroup.value.accuracy,
    time: `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  }
  saveFinished()
  cancelAnimationFrame(animFrame)
}

function resetRecognition() {
  resetState()
}

// 清空所有小组识别成绩（方便第二次使用）
function clearAllScores() {
  ElMessageBox.confirm('确定清空所有小组的识别成绩吗？清空后需要重新识别。', '清空识别数据', {
    confirmButtonText: '确定清空',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      finishedGroups.value = {}
      localStorage.removeItem(SCORE_KEY)
      ElMessage.success('识别数据已清空')
    })
    .catch(() => {})
}

function scrollStdTo(i) {
  nextTick(() => {
    const el = stdItemRefs[i]
    const container = stdListRef.value
    if (!el || !container) return
    const target = el.offsetTop - container.clientHeight / 2 + el.clientHeight / 2
    container.scrollTo({ top: Math.max(0, target), behavior: 'smooth' })
  })
}

function scrollResultToBottom() {
  nextTick(() => {
    if (resultListRef.value) {
      resultListRef.value.scrollTop = resultListRef.value.scrollHeight
    }
  })
}

// 模拟波形（复用平台演示逻辑）
function drawWave() {
  const canvas = waveCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const barCount = 40
  const barWidth = canvas.width / barCount
  if (waveHeights.length !== barCount) {
    waveHeights = Array.from({ length: barCount }, (_, i) => {
      const center = barCount / 2
      const dist = Math.abs(i - center) / center
      return 0.2 + (1 - dist) * 0.3
    })
  }
  let tick = 0
  const draw = () => {
    animFrame = requestAnimationFrame(draw)
    tick += 0.06
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    for (let i = 0; i < barCount; i++) {
      const center = barCount / 2
      const dist = Math.abs(i - center) / center
      const envelope = 1 - dist * 0.6
      const wave = Math.sin(tick + i * 0.4) * 0.3 + 0.5
      const wave2 = Math.sin(tick * 1.7 + i * 0.25) * 0.15
      const target = envelope * (wave + wave2)
      waveHeights[i] += (target - waveHeights[i]) * 0.3
      const h = Math.max(3, waveHeights[i] * canvas.height * 0.85)
      const gradient = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - h)
      gradient.addColorStop(0, 'rgba(0, 229, 255, 0.2)')
      gradient.addColorStop(1, 'rgba(0, 229, 255, 0.85)')
      ctx.fillStyle = gradient
      ctx.fillRect(i * barWidth + 1, canvas.height - h, barWidth - 2, h)
    }
  }
  draw()
}

onUnmounted(() => {
  aborted = true
  cancelAnimationFrame(animFrame)
})
</script>

<style scoped>
.voice-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #0a1628;
  color: #e2e8f0;
}

/* ===== 星空背景 ===== */
.starfield {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.stars {
  position: absolute;
  inset: -50%;
  background-image:
    radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.8) 50%, transparent 50%),
    radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.5) 50%, transparent 50%),
    radial-gradient(1.5px 1.5px at 60% 20%, rgba(0,229,255,0.7) 50%, transparent 50%),
    radial-gradient(1px 1px at 80% 50%, rgba(255,255,255,0.6) 50%, transparent 50%),
    radial-gradient(1.5px 1.5px at 10% 80%, rgba(0,229,255,0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 90% 85%, rgba(255,255,255,0.4) 50%, transparent 50%),
    radial-gradient(1px 1px at 50% 45%, rgba(255,255,255,0.5) 50%, transparent 50%),
    radial-gradient(1.5px 1.5px at 30% 10%, rgba(255,255,255,0.6) 50%, transparent 50%);
  background-size: 560px 560px;
  animation: starDrift 90s linear infinite;
  opacity: 0.7;
}
.stars-2 {
  background-size: 320px 320px;
  animation-duration: 60s;
  animation-direction: reverse;
  opacity: 0.4;
}
@keyframes starDrift {
  from { transform: translate3d(0, 0, 0); }
  to { transform: translate3d(-280px, 140px, 0); }
}

/* ===== 页头 ===== */
.page-header {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  padding: 14px 24px;
  flex-shrink: 0;
  gap: 16px;
}
.back-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  background: rgba(0, 229, 255, 0.06);
  border: 1px solid rgba(0, 229, 255, 0.25);
  border-radius: 8px;
  color: rgba(226, 232, 240, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.back-btn:hover {
  background: rgba(0, 229, 255, 0.12);
  border-color: rgba(0, 229, 255, 0.45);
  color: #00e5ff;
}
.title-row {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.title-bar {
  width: 4px;
  height: 22px;
  align-self: center;
  border-radius: 2px;
  background: linear-gradient(180deg, #00e5ff, #0080ff);
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.6);
}
.page-header h1 {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #fff;
}
.title-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 1px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.clear-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background: rgba(245, 108, 108, 0.06);
  border: 1px solid rgba(245, 108, 108, 0.25);
  border-radius: 20px;
  color: rgba(245, 140, 140, 0.85);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.clear-btn:hover {
  background: rgba(245, 108, 108, 0.12);
  border-color: rgba(245, 108, 108, 0.5);
  color: #f56c6c;
}
.header-status {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  color: rgba(103, 194, 58, 0.85);
  padding: 6px 12px;
  border: 1px solid rgba(103, 194, 58, 0.25);
  border-radius: 20px;
  background: rgba(103, 194, 58, 0.06);
}
.engine-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.9);
  animation: dotBreath 2s ease-in-out infinite;
}
@keyframes dotBreath {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ===== 小组选择 ===== */
.group-row {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 16px;
  padding: 4px 24px 14px;
  flex-shrink: 0;
}
.group-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: rgba(13, 33, 55, 0.55);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s;
}
.group-card:hover {
  border-color: rgba(0, 229, 255, 0.4);
  transform: translateY(-2px);
}
.group-card.active {
  border-color: rgba(0, 229, 255, 0.7);
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), rgba(0, 128, 255, 0.05));
  box-shadow: 0 0 18px rgba(0, 229, 255, 0.15), inset 0 0 20px rgba(0, 229, 255, 0.04);
}
.group-card.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
.group-flag {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.group-flag.xuntian { background: linear-gradient(135deg, #00e5ff, #0080ff); box-shadow: 0 0 14px rgba(0, 229, 255, 0.35); }
.group-flag.changkong { background: linear-gradient(135deg, #a78bfa, #6366f1); box-shadow: 0 0 14px rgba(167, 139, 250, 0.35); }
.group-flag.yufeng { background: linear-gradient(135deg, #fbbf24, #f59e0b); box-shadow: 0 0 14px rgba(251, 191, 36, 0.3); }
.group-info { flex: 1; min-width: 0; }
.group-name {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 5px;
}
.group-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.lang-badge {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 10px;
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: rgba(0, 229, 255, 0.85);
}
.lang-badge.changkong {
  border-color: rgba(167, 139, 250, 0.4);
  color: rgba(196, 181, 253, 0.95);
}
.member-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}
.group-score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}
.score-main {
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.score-num {
  font-size: 24px;
  font-weight: 800;
  text-shadow: 0 0 12px currentColor;
}
.score-num.lv-good { color: #67c23a; }
.score-num.lv-mid { color: #e6a23c; }
.score-num.lv-bad { color: #f56c6c; }
.score-unit {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}
.score-time {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.35);
}

/* ===== 主对照区 ===== */
.main-panels {
  position: relative;
  z-index: 2;
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 16px;
  padding: 0 24px;
}
.panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: rgba(10, 25, 45, 0.55);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 14px;
  overflow: hidden;
}
.result-panel {
  background: rgba(8, 20, 38, 0.65);
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-bottom: 1px solid rgba(0, 229, 255, 0.12);
  flex-shrink: 0;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.9);
}
.panel-title svg { color: #00e5ff; }
.panel-lang {
  font-size: 12px;
  font-weight: 400;
  color: rgba(0, 229, 255, 0.7);
  margin-left: 4px;
}
.panel-tag {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  display: flex;
  align-items: center;
  gap: 6px;
}
.panel-tag.live { color: rgba(245, 108, 108, 0.85); }
.rec-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f56c6c;
  animation: dotBreath 1s ease-in-out infinite;
}

/* 左栏标准口令 */
.std-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  scroll-behavior: smooth;
}
.std-list::-webkit-scrollbar,
.result-list::-webkit-scrollbar { width: 5px; }
.std-list::-webkit-scrollbar-thumb,
.result-list::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 255, 0.2);
  border-radius: 3px;
}
.std-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.3s;
  opacity: 0.55;
}
.std-item .line-no {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  width: 22px;
}
.std-item .line-text {
  flex: 1;
  font-size: 13px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.75);
}
.std-item.passed {
  opacity: 0.9;
}
.std-item.passed .line-text { color: rgba(255, 255, 255, 0.85); }
.std-item.current {
  opacity: 1;
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.14), rgba(0, 128, 255, 0.04));
  border-color: rgba(0, 229, 255, 0.5);
  box-shadow: 0 0 16px rgba(0, 229, 255, 0.12);
  transform: scale(1.02);
}
.std-item.current .line-text {
  color: #fff;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}
.std-item.current .line-no { color: #00e5ff; }
.line-check {
  font-size: 13px;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
}

/* 右栏识别结果 */
.result-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;
}
.empty-icon { opacity: 0.4; }
.result-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.result-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid transparent;
  animation: slideIn 0.35s ease-out;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.result-item .result-no {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  width: 22px;
  line-height: 1.7;
}
.result-item .result-text {
  flex: 1;
  font-size: 13.5px;
  line-height: 1.6;
}
.result-item.typing {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(0, 229, 255, 0.18);
}
.result-item.typing .result-text { color: rgba(255, 255, 255, 0.7); }
.result-item.typing .result-mark {
  color: rgba(0, 229, 255, 0.5);
  font-size: 11px;
  letter-spacing: 1px;
}
.result-item.correct {
  background: rgba(103, 194, 58, 0.06);
  border-color: rgba(103, 194, 58, 0.25);
}
.result-item.correct .result-text { color: rgba(147, 220, 110, 0.95); }
.result-item.partial {
  background: rgba(230, 162, 60, 0.07);
  border-color: rgba(230, 162, 60, 0.3);
}
.result-item.partial .result-text { color: rgba(240, 190, 110, 0.95); }
.result-item.wrong {
  background: rgba(245, 108, 108, 0.07);
  border-color: rgba(245, 108, 108, 0.3);
}
.result-item.wrong .result-text { color: rgba(250, 140, 140, 0.95); }
.result-mark {
  font-size: 13px;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
}
.result-item.correct .result-mark { color: #67c23a; }
.result-item.partial .result-mark { color: #e6a23c; }
.result-item.wrong .result-mark { color: #f56c6c; }
/* 打字光标 */
.type-caret {
  display: inline-block;
  width: 2px;
  height: 13px;
  margin-left: 2px;
  vertical-align: -2px;
  background: #00e5ff;
  animation: caretBlink 0.7s steps(1) infinite;
}
@keyframes caretBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.recognizing-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  color: rgba(0, 229, 255, 0.6);
}
.wave-mini {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 14px;
}
.wave-mini i {
  width: 3px;
  background: rgba(0, 229, 255, 0.7);
  border-radius: 2px;
  animation: waveJump 0.9s ease-in-out infinite;
}
.wave-mini i:nth-child(1) { height: 6px; }
.wave-mini i:nth-child(2) { height: 12px; animation-delay: 0.15s; }
.wave-mini i:nth-child(3) { height: 8px; animation-delay: 0.3s; }
@keyframes waveJump {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1.2); }
}

/* 得分面板 */
.score-panel {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 14px 20px;
  border-top: 1px solid rgba(0, 229, 255, 0.15);
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.05), transparent);
}
.score-ring { position: relative; width: 120px; height: 120px; flex-shrink: 0; }
.score-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.score-value {
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
  color: #fff;
}
.score-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 4px;
}
.score-detail { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 7px; }
.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.detail-label { color: rgba(255, 255, 255, 0.5); }
.detail-value { color: rgba(226, 232, 240, 0.95); font-weight: 600; }
.detail-comment {
  margin-top: 2px;
  padding: 8px 12px;
  font-size: 12.5px;
  line-height: 1.6;
  color: rgba(0, 229, 255, 0.85);
  background: rgba(0, 229, 255, 0.05);
  border: 1px dashed rgba(0, 229, 255, 0.25);
  border-radius: 8px;
}
.score-pop-enter-active { transition: all 0.45s cubic-bezier(0.34, 1.4, 0.64, 1); }
.score-pop-enter-from { opacity: 0; transform: translateY(24px); }

/* ===== 底部控制条 ===== */
.control-bar {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 12px 24px 16px;
  flex-shrink: 0;
}
.wave-canvas {
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(0, 229, 255, 0.15);
}
.control-hint {
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.4);
}
.control-actions :deep(.el-button--large) {
  padding: 12px 30px;
  font-size: 15px;
}

/* 响应式 */
@media (max-width: 900px) {
  .main-panels { flex-direction: column; overflow-y: auto; }
  .panel { min-height: 300px; }
  .group-row { flex-direction: column; }
}
</style>
