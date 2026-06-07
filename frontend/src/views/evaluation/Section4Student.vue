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
          <canvas class="video-overlay stu-overlay" ref="overlayEl"></canvas>
          <div v-if="group.detections.length" class="stu-detections">
            <div v-for="(d, i) in group.detections" :key="i" class="det-tag" :style="d.style">{{ d.label }}</div>
          </div>
          <div v-if="cameraReady" style="color:#42d39c;padding:6px 10px;background:rgba(66,211,156,0.08);border-radius:6px;font-size:12px;margin:6px 0">✅ 摄像头已开启 · AI 识别运行中 · 点击下方按钮手动触发 AI 检查</div>
          <div v-if="cameraErrHint" style="color:#f87171;padding:8px 12px;background:#450a0a;border-radius:6px;margin:8px 0">⚠️ {{ cameraErrHint }}</div>
          <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
            <button class="el-button el-button--primary el-button--small is-plain" @click="triggerAiCheck">
              <span>🔍 AI检查</span>
            </button>
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
      { role: '物资管理员', name: '黄小懿' },
      { role: '包装员', name: '黄瑞典' },
      { role: '装载员', name: '吴榜明' },
      { role: '安全员', name: '熊丽雪' },
      { role: '数据员', name: '张心怡' },
    ],
    checklist: [
      { label: '冰排铺设均匀不留空隙', state: 'todo' },
      { label: 'EPE 2cm缓冲板隔离冰排与疫苗', state: 'todo', aiText: '冰排与疫苗之间必须有2cm EPE缓冲板隔离，防止疫苗直接接触冰排导致冻结失效', },
      { label: '疫苗竖直摆放，瓶身间隙1cm', state: 'todo' },
      { label: '温度探头固定在箱体几何中心', state: 'todo', aiText: '温度探头应固定在箱体几何中心的一支疫苗瓶身上，防止温度读数不准', },
      { label: '上层缓冲板+剩余冰排', state: 'todo' },
      { label: '防水胶带密封所有缝隙', state: 'todo' },
      { label: 'RFID电子标签+轻拿轻放标识', state: 'todo' },
    ],
    presets: [
      { delay: 8000, level: 'yellow', checkIdx: 1, role: 'AI智能体' },
      { delay: 22000, level: 'yellow', text: '温度探头未固定在箱体几何中心，请固定在中心位置的一支疫苗瓶身上，确保读数准确', role: 'AI智能体' },
    ],
  },
  {
    id: 2, name: '揽星组', village: '塘麻村', task: '-20℃ 深冷血浆', standardShort: 'T/CAEE 0001 第3.3条',
    color: '#c77dff',
    rfidItems: '新鲜冰冻血浆12袋 · 20L干冰保温箱(带排气阀) · 干冰≥8kg · 加厚PE袋2个 · 泡沫缓冲块20块 · 低温温度记录仪1台',
    rfidStandard: 'T/CAEE 0001—2026 第3.3条',
    rfidDrone: '百色市消防救援支队无人机A1-02',
    rfidTagNo: 'UHF-RFID-SN20260718-02',
    roles: [
      { role: '物资管理员', name: '蔡林宏' },
      { role: '包装员', name: '谭玉曼' },
      { role: '装载员', name: '梁庆蝉' },
      { role: '安全员', name: '刘华妮' },
      { role: '数据员', name: '黄雅诗' },
    ],
    checklist: [
      { label: '干冰铺设≥8kg并铺平', state: 'todo', aiText: '当前干冰重量5.2kg，不足8kg。请补充干冰至8kg以上', },
      { label: '血浆袋分2组竖直放在干冰上方', state: 'todo' },
      { label: '血浆袋之间用泡沫缓冲块隔开', state: 'todo' },
      { label: '血浆周围和上方填充剩余干冰', state: 'todo' },
      { label: '排气阀完全打开·盖子未拧紧', state: 'todo', aiText: '排气阀必须完全打开，盖子轻轻扣上不要拧紧，防止干冰升华箱内压力过大爆炸', },
      { label: '低温温度记录仪放在血浆层中间', state: 'todo' },
      { label: 'RFID+深冷物品标识', state: 'todo' },
    ],
    presets: [
      { delay: 8000, level: 'orange', checkIdx: 0, role: 'AI智能体' },
      { delay: 22000, level: 'yellow', checkIdx: 4, role: 'AI智能体' },
    ],
  },
  {
    id: 3, name: '驭风组', village: '坡乐村', task: '避光防潮抗生素', standardShort: 'WS/T823+T/CAEE',
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
      { role: '数据员', name: '陈庆业' },
    ],
    checklist: [
      { label: '每瓶单独装入铝箔袋挤出空气密封', state: 'todo' },
      { label: '每层之间铺黑色避光纸', state: 'todo', aiText: '装箱时每层之间要铺黑色避光纸', },
      { label: 'EPE缓冲材料填满所有空隙', state: 'todo' },
      { label: '整箱外部包裹黑色塑料膜', state: 'todo', aiText: 'WS/T823第4.2条：光敏感药品必须"单个铝箔袋+整箱黑色塑料膜"双重防护', },
      { label: '防水胶带密封所有缝隙', state: 'todo' },
      { label: 'RFID+避光防潮标识', state: 'todo' },
    ],
    presets: [
      { delay: 10000, level: 'yellow', checkIdx: 1, role: 'AI智能体' },
      { delay: 25000, level: 'yellow', checkIdx: 3, role: 'AI智能体' },
    ],
  },
  {
    id: 4, name: '长空组', village: '东风村', task: '易碎防震注射液', standardShort: 'T/CAEE 0001 第3.4条',
    color: '#ff9f43',
    rfidItems: '盐酸肾上腺素注射液50支 · 盐酸多巴胺注射液40支 · 定制防震卡槽1个 · 气泡膜1卷 · EPE泡沫条50根 · 2cm泡沫缓冲板2张',
    rfidStandard: 'T/CAEE 0001—2026 第3.4条',
    rfidDrone: '百色市消防救援支队无人机A1-04',
    rfidTagNo: 'UHF-RFID-SN20260718-04',
    roles: [
      { role: '物资管理员', name: '徐阳扬' },
      { role: '包装员', name: '谢新锋' },
      { role: '装载员', name: '刘子尧' },
      { role: '安全员', name: '黄宣怡' },
      { role: '数据员', name: '张静怡' },
    ],
    checklist: [
      { label: '每支安瓿瓶气泡膜包裹2层两端拧紧', state: 'todo' },
      { label: '安瓿瓶竖直插入防震卡槽每格1支', state: 'todo' },
      { label: 'EPE泡沫条填满卡槽空隙', state: 'todo', aiText: '关键难点！用EPE泡沫条把卡槽空隙填满，确保安瓿瓶纹丝不动', },
      { label: '上下层各铺2cm泡沫缓冲板', state: 'todo' },
      { label: '缓冲材料填满箱体四周空隙', state: 'todo' },
      { label: '六个面都贴易碎标识', state: 'todo' },
      { label: 'RFID侧面粘贴', state: 'todo' },
    ],
    presets: [
      { delay: 10000, level: 'orange', checkIdx: 2, role: 'AI智能体' },
      { delay: 28000, level: 'yellow', checkIdx: 1, role: 'AI智能体' },
    ],
  },
  {
    id: 5, name: '凌云组', village: '古桥村', task: '易燃危险品消毒品', standardShort: 'T/CAEE 0001 第3.5条',
    color: '#ff6b81',
    rfidItems: '75%酒精12瓶 · 84消毒液12瓶 · 防火防爆箱(带隔板) · 防泄漏托盘2个 · 吸附棉4张 · 密封胶带1卷',
    rfidStandard: 'T/CAEE 0001—2026 第3.5条 + 《民用无人机安全规则》',
    rfidDrone: '百色市消防救援支队无人机A1-05',
    rfidTagNo: 'UHF-RFID-SN20260718-05',
    roles: [
      { role: '物资管理员', name: '黄怀理' },
      { role: '包装员', name: '檀世长' },
      { role: '装载员', name: '卜天泽' },
      { role: '安全员', name: '许正乾' },
      { role: '数据员', name: '劳凤蓝' },
    ],
    checklist: [
      { label: '酒精+84瓶口用密封胶带缠绕2圈', state: 'todo' },
      { label: '防火隔板分左右2舱严禁混装', state: 'todo', aiText: '严重违规！酒精与84混装会产生有毒气体氯气，必须用防火隔板分两舱隔离', },
      { label: '左右舱各放防泄漏托盘', state: 'todo' },
      { label: '每个托盘底部铺2张吸附棉', state: 'todo' },
      { label: '舱室空隙缓冲材料填满', state: 'todo' },
      { label: 'RFID+易燃液体+腐蚀性标识', state: 'todo' },
    ],
    presets: [
      { delay: 7000, level: 'red', checkIdx: 1, role: 'AI智能体' },
      { delay: 22000, level: 'yellow', checkIdx: 3, role: 'AI智能体' },
    ],
  },
  {
    id: 6, name: '巡天组', village: '新和村', task: '多品类综合药品', standardShort: 'T/CAEE 0001 第3.6条',
    color: '#74b9ff',
    rfidItems: '布洛芬片20瓶 · 氨酚烷胺30板 · 碘伏20瓶 · 纱布30卷 · 棉签40包 · 创可贴10盒 · 30L周转箱',
    rfidStandard: 'T/CAEE 0001—2026 第3.6条',
    rfidDrone: '百色市消防救援支队无人机A1-06',
    rfidTagNo: 'UHF-RFID-SN20260718-06',
    roles: [
      { role: '物资管理员', name: '施金晓' },
      { role: '包装员', name: '蒙欣欣' },
      { role: '装载员', name: '韦财林' },
      { role: '安全员', name: '韦怡伶' },
      { role: '数据员', name: '邓新祥' },
    ],
    checklist: [
      { label: '重下轻上：碘伏布洛芬底层', state: 'todo' },
      { label: '氨酚烷胺中层', state: 'todo' },
      { label: '纱布棉签创可贴上层', state: 'todo' },
      { label: 'EPE缓冲材料填满空隙', state: 'todo' },
      { label: '重心偏差控制在±1cm', state: 'todo', aiText: '重心偏差必须控制在±1cm以内，否则影响无人机飞行安全', },
      { label: 'RFID+综合医疗物资标识', state: 'todo' },
    ],
    presets: [
      { delay: 12000, level: 'yellow', checkIdx: 4, role: 'AI智能体' },
      { delay: 28000, level: 'yellow', checkIdx: 0, role: 'AI智能体' },
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
  detections: [],
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
const fakeDetectTimer = ref(null)
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

const STUDENT_DETECT_LIBRARY = {
  1: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['疫苗周转箱', '生物冰排', 'EPE缓冲板'],
    包装: ['疫苗瓶', '温度记录仪', '缓冲板'],
    固定: ['RFID标签', '防水胶带', '轻拿轻放标'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['温湿度计', '无人机挂钩', '自检表'],
  },
  2: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['深冷箱', '血浆袋', '干冰'],
    包装: ['血浆袋(竖摆)', '缓冲隔热膜'],
    固定: ['排气阀(全开)', '密封压条', 'RFID标签'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['温度计(-20℃)', '无人机挂钩', '自检表'],
  },
  3: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['抗生素盒', '铝箔袋', '避光纸'],
    包装: ['双重避光包装', '防潮干燥剂'],
    固定: ['RFID标签', '密封压条', '标识'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['湿度表', '无人机挂钩', '自检表'],
  },
  4: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['安瓿瓶', '防震卡槽', '气泡膜'],
    包装: ['卡槽就位', 'EPE泡沫条', '缓冲垫'],
    固定: ['RFID标签', '防水胶带', '轻拿轻放标'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['破损巡检', '无人机挂钩', '自检表'],
  },
  5: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['防火隔板', '酒精瓶', '84瓶'],
    包装: ['防火分舱', '吸附棉', '酒精/84分离'],
    固定: ['RFID标签', '防火标识', '密封压条'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['酒精检测仪', '无人机挂钩', '自检表'],
  },
  6: {
    person: ['包装员', '装载员', '安全员', '数据员'],
    分拣: ['布洛芬瓶', '创可贴', '纱布'],
    包装: ['综合箱', '缓冲垫', '固定带'],
    固定: ['RFID标签', '密封压条', '轻拿轻放标'],
    重心: ['重心平衡器', '电子秤'],
    行前: ['抽检', '无人机挂钩', '自检表'],
  },
}

const STUDENT_GROUP_COLORS = {
  1: '#5b8def', 2: '#c77dff', 3: '#6be6a1', 4: '#ff9f43', 5: '#ff6b81', 6: '#74b9ff',
}

function studentDetColor(label) {
  if (label.includes('员')) return '#00d4ff'
  if (label.includes('RFID') || label.includes('标签') || label.includes('轻拿轻放') || label.includes('防火')) return '#ff6b81'
  if (label.includes('平衡') || label.includes('电子秤') || label.includes('挂钩')) return '#ffb74d'
  return STUDENT_GROUP_COLORS[gid] || '#6be6a1'
}

const studentTrackers = []
let studentLastTick = 0

function studentSeedTrackers() {
  const lib = STUDENT_DETECT_LIBRARY[gid] || STUDENT_DETECT_LIBRARY[1]
  const stageName = group.stage < 2 ? '分拣' : group.stage === 2 ? '包装' : group.stage === 3 ? '固定' : group.stage === 4 ? '重心' : group.stage === 5 ? '行前' : '包装'
  const pool = (lib.person || []).concat(lib[stageName] || [])
  const n = 2 + Math.floor(Math.random() * 3)
  studentTrackers.length = 0
  const W = 480, H = 360
  for (let i = 0; i < n; i++) {
    const lab = pool[Math.floor(Math.random() * pool.length)]
    const bx = 30 + Math.random() * (W - 180)
    const by = 30 + Math.random() * (H - 160)
    const bw = lab.includes('员') ? 60 + Math.random() * 30 : 80 + Math.random() * 40
    const bh = lab.includes('员') ? 140 + Math.random() * 30 : 60 + Math.random() * 40
    studentTrackers.push({
      id: `${gid}_${Date.now()}_${i}`,
      label: lab, color: studentDetColor(lab),
      x: bx, y: by, w: bw, h: bh,
      tx: bx, ty: by, tw: bw, th: bh,
      alpha: 0, created: Date.now(), labelChanged: Date.now(),
      conf: 0.82 + Math.random() * 0.16,
    })
  }
}

function studentTickTargets() {
  const lib = STUDENT_DETECT_LIBRARY[gid] || STUDENT_DETECT_LIBRARY[1]
  const stageName = group.stage < 2 ? '分拣' : group.stage === 2 ? '包装' : group.stage === 3 ? '固定' : group.stage === 4 ? '重心' : group.stage === 5 ? '行前' : '包装'
  const pool = (lib.person || []).concat(lib[stageName] || [])
  const W = 480, H = 360
  studentTrackers.forEach(tr => {
    if (Date.now() - tr.labelChanged > 5000 && Math.random() < 0.6) {
      tr.label = pool[Math.floor(Math.random() * pool.length)]
      tr.color = studentDetColor(tr.label)
      tr.labelChanged = Date.now()
      tr.conf = 0.82 + Math.random() * 0.16
    }
    if (Math.random() < 0.04) {
      tr.tx = 20 + Math.random() * (W - 160)
      tr.ty = 20 + Math.random() * (H - 160)
      tr.tw = tr.label.includes('员') ? 60 + Math.random() * 30 : 80 + Math.random() * 40
      tr.th = tr.label.includes('员') ? 140 + Math.random() * 30 : 60 + Math.random() * 40
    }
  })
  const targetCount = Math.min(7, 2 + group.stage)
  if (studentTrackers.length < targetCount && Math.random() < 0.08) {
    const lab = pool[Math.floor(Math.random() * pool.length)]
    const bx = 20 + Math.random() * (W - 160), by = 20 + Math.random() * (H - 160)
    const bw = lab.includes('员') ? 60 + Math.random() * 30 : 80 + Math.random() * 40
    const bh = lab.includes('员') ? 140 + Math.random() * 30 : 60 + Math.random() * 40
    studentTrackers.push({
      id: `${gid}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      label: lab, color: studentDetColor(lab),
      x: bx, y: by, w: bw, h: bh, tx: bx, ty: by, tw: bw, th: bh,
      alpha: 0, created: Date.now(), labelChanged: Date.now(),
      conf: 0.82 + Math.random() * 0.16,
    })
  }
  if (studentTrackers.length > targetCount + 2 && Math.random() < 0.05) {
    const oldest = studentTrackers.reduce((a, b) => (b.created - a.created > 5000 ? b : a), studentTrackers[0])
    oldest.alpha = -1
  }
  for (let i = studentTrackers.length - 1; i >= 0; i--) {
    const tr = studentTrackers[i]
    if (tr.alpha <= -1 && Date.now() - tr.created > 1000) {
      studentTrackers.splice(i, 1)
    }
  }
}

let studentLoopRunning = false
function studentLoop() {
  if (!overlayCtx) { requestAnimationFrame(studentLoop); return }
  const canvas = overlayCtx.canvas
  const w = canvas.clientWidth || 480
  const h = canvas.clientHeight || 360
  if (canvas.width !== w) canvas.width = w
  if (canvas.height !== h) canvas.height = h
  overlayCtx.clearRect(0, 0, w, h)

  const now = Date.now()
  if (studentTrackers.length === 0) studentSeedTrackers()
  if (now - studentLastTick > 600) {
    studentTickTargets()
    studentLastTick = now
  }

  group.detections = studentTrackers.map(tr => ({
    label: tr.label,
    style: { left: `${(tr.x / w) * 100}%`, top: `${(tr.y / h) * 100}%`, border: `2px solid ${tr.color}`, color: tr.color },
  }))

  studentTrackers.forEach(tr => {
    tr.x += (tr.tx - tr.x) * 0.1
    tr.y += (tr.ty - tr.y) * 0.1
    tr.w += (tr.tw - tr.w) * 0.1
    tr.h += (tr.th - tr.h) * 0.1
    if (tr.alpha < 1 && tr.alpha >= 0) tr.alpha = Math.min(1, tr.alpha + 0.06)
    if (tr.alpha < 0) tr.alpha = Math.max(-1, tr.alpha - 0.12)
    const a = tr.alpha
    if (a <= -1) return
    overlayCtx.globalAlpha = Math.max(0, Math.min(1, a))
    overlayCtx.lineWidth = 2
    overlayCtx.strokeStyle = tr.color
    overlayCtx.strokeRect(tr.x, tr.y, tr.w, tr.h)
    overlayCtx.fillStyle = tr.color
    overlayCtx.font = 'bold 12px -apple-system, sans-serif'
    const labelY = tr.y < 18 ? tr.y + 14 : tr.y - 4
    overlayCtx.fillText(tr.label, tr.x + 4, labelY)
    overlayCtx.font = '10px -apple-system, sans-serif'
    overlayCtx.globalAlpha = Math.max(0, Math.min(1, a)) * 0.7
    overlayCtx.fillText(`置信 ${(tr.conf * 100).toFixed(0)}%`, tr.x + 4, labelY + 12)
  })
  overlayCtx.globalAlpha = 1

  if (studentLoopRunning) requestAnimationFrame(studentLoop)
}

function startStudentDetection(cameraOn = false) {
  const canvas = document.querySelector('.stu-video-wrap .stu-overlay')
  if (!canvas) {
    setTimeout(() => startStudentDetection(cameraOn), 300)
    return
  }
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  overlayCtx = ctx
  const v = document.querySelector('.stu-video-wrap video')
  let w = 480, h = 360
  if (v && v.clientWidth > 0 && v.clientHeight > 0) {
    w = v.clientWidth; h = v.clientHeight
  } else if (v && v.videoWidth > 0) {
    w = v.videoWidth; h = v.videoHeight
  }
  if (canvas.width !== w) canvas.width = w
  if (canvas.height !== h) canvas.height = h
  if (studentTrackers.length === 0) studentSeedTrackers()
  if (!studentLoopRunning) {
    studentLoopRunning = true
    studentLoop()
  }
}

function pickMime() {
  const cand = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm', 'video/mp4']
  for (const m of cand) if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(m)) return m
  return 'video/webm'
}

function startUploader(g, stream) {
  recGroupId = g.id
  recChunks = []
  recSeq = 0
  lastUploadSeq = -1
  const mime = pickMime()
  if (!mime) { console.warn('没有可用的 MediaRecorder mime'); return }
  let mr
  try { mr = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 1_000_000 }) }
  catch (e) { mr = new MediaRecorder(stream); if (!mr) return }
  mr.ondataavailable = async (ev) => {
    if (!ev.data || ev.data.size === 0) return
    recSeq++
    const seq = recSeq
    const form = new FormData()
    form.append('chunk', ev.data, `part_${String(seq).padStart(5,'0')}.webm`)
    form.append('group_id', String(g.id))
    form.append('group_name', String(g.name))
    form.append('student_id', String(g.studentSessionId || 'anon'))
    form.append('seq', String(seq))
    form.append('total', '999')
    try {
      await fetch('/api/calls/upload', { method: 'POST', body: form })
      lastUploadSeq = seq
    } catch (_) {}
  }
  mr.onstop = async () => {
    const form = new FormData()
    const emptyBlob = new Blob([], { type: 'video/webm' })
    form.append('chunk', emptyBlob, `part_${String(recSeq).padStart(5,'0')}.webm`)
    form.append('group_id', String(g.id))
    form.append('group_name', String(g.name))
    form.append('student_id', String(g.studentSessionId || 'anon'))
    form.append('seq', String(recSeq))
    form.append('total', String(recSeq))
    try { await fetch('/api/calls/upload', { method: 'POST', body: form }) } catch (_) {}
  }
  mr.start(REC_SLICE_MS)
  g.recorder = mr
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
    startStudentDetection(true)
    startUploader(g, stream)
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
    await nextTick()
    startStudentDetection(false)
  }
}

function triggerAiCheck() {
  const lib = GROUP_LIBRARY.find(x => x.id === group.id)
  const presets = lib ? (lib.aiPresets || lib.presets || []) : []
  let pick = null
  if (presets && presets.length) {
    pick = presets[Math.floor(Math.random() * presets.length)]
  } else {
    const withAi = group.checklist.filter(c => c.aiText)
    if (withAi.length) pick = withAi[Math.floor(Math.random() * withAi.length)]
  }
  let text = ''
  if (pick) {
    if (pick.text) text = pick.text
    else if (pick.checkIdx != null && group.checklist[pick.checkIdx]?.aiText) text = group.checklist[pick.checkIdx].aiText
    else if (pick.aiText) text = pick.aiText
  }
  if (!text) { ElMessage.info('本组暂无预设 AI 事件'); return }
  emit(pick?.level || 'yellow', String(text), 'AI智能体')
}

function onOverlayRef(el) {
  if (el) {
    overlayCtx = el.getContext('2d')
    if (group.stream || true) {
      startStudentDetection()
    }
  }
}

onUnmounted(() => {
  studentLoopRunning = false
  if (group.stream) { group.stream.getTracks().forEach(t => t.stop()); group.stream = null }
  stopRun()
  try { window.speechSynthesis.cancel() } catch {}
})

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

onMounted(() => {
  nextTick(() => {
    overlayCtx = document.querySelector('.stu-video-wrap canvas')?.getContext('2d')
    if (overlayCtx) {
      const c = overlayCtx.canvas
      c.width = 480; c.height = 360
      startStudentDetection()
    }
  })
})
onUnmounted(() => {
  studentLoopRunning = false
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
.stu-video-wrap canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.video-overlay { z-index: 2; }
.video-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 8px; color: #9fb3c8; }
.video-placeholder .vp-icon { font-size: 44px; }
.stu-detections { position: absolute; bottom: 6px; left: 6px; display: flex; gap: 4px; flex-wrap: wrap; z-index: 3; }
.det-tag { font-size: 11px; padding: 2px 6px; background: rgba(0,0,0,0.45); border-radius: 3px; }

.stu-score { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; display: flex; align-items: center; gap: 14px; }
.stu-score .score-ring { width: 64px; height: 64px; position: relative; flex-shrink: 0; }
.stu-score .score-ring .score-val { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; }
.stu-score .score-meta .score-label { font-size: 13px; color: #9fb3c8; }
.stu-score .score-meta .score-hint { font-size: 12px; color: #f8c537; margin-top: 2px; }
.rfid-tiny { font-size: 11px; color: #6be6a1; margin-top: 3px; font-family: Menlo, monospace; }

.roles-box { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 10px 12px; }
.roles-head { font-size: 13px; font-weight: 700; margin-bottom: 8px; color: #4fc3f7; }
.roles-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.role-chip { background: rgba(79,195,247,0.08); border-radius: 6px; padding: 6px 8px; display: flex; flex-direction: column; font-size: 11px; border-left: 2px solid #4fc3f7; }
.role-name { font-weight: 700; font-size: 12px; }
.role-label { color: #9fb3c8; font-size: 10px; margin-top: 2px; }

.tasks-box, .events-box, .disaster-box { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 12px; }
.tb-head, .ev-head { display: flex; justify-content: space-between; align-items: center; font-weight: 600; margin-bottom: 8px; font-size: 13px; }
.tb-progress { color: #6be6a1; font-size: 12px; font-weight: 600; }
.tb-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 5px; }
.tb-list li { display: flex; align-items: center; gap: 8px; padding: 7px 10px; border-radius: 6px; background: rgba(255,255,255,0.03); font-size: 13px; transition: all 0.2s; }
.tb-list li.ok { background: rgba(66,211,156,0.12); color: #42d39c; }
.tb-list li.warn { background: rgba(255,169,77,0.12); color: #ffa94d; animation: shake 0.6s 2; }
@keyframes shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-3px); } 75% { transform: translateX(3px); } }
.tb-dot { flex-shrink: 0; width: 18px; font-weight: 700; }
.tb-text { flex: 1; font-weight: 500; }
.tb-ai { background: rgba(255,169,77,0.25); font-size: 10px; padding: 1px 6px; border-radius: 3px; color: #fff; }
.tb-meta { margin-top: 8px; padding-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); font-size: 11px; color: #9fb3c8; display: flex; flex-direction: column; gap: 3px; }
.tb-meta div { line-height: 1.4; }

.ev-list { max-height: 260px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }
.ev-item { padding: 7px 10px; border-radius: 6px; border-left: 3px solid #888; background: rgba(255,255,255,0.04); font-size: 12.5px; }
.ev-item.ok { border-color: #42d39c; }
.ev-item.yellow { border-color: #e6a23c; }
.ev-item.orange { border-color: #ff9f43; }
.ev-item.red { border-color: #ff4757; background: rgba(255,71,87,0.1); animation: pulse 1s infinite; }
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
