<template>
  <Teleport to="body">
    <!-- ─── 仿真平台加载引导层 ─── -->
    <Transition name="sim-fade">
      <div v-if="modelValue && booting" class="sim-boot">
        <div class="boot-logo">◤</div>
        <div class="boot-name">低空应急运输虚拟仿真系统</div>
        <div class="boot-stage">{{ bootStage }}</div>
        <div class="boot-bar"><div class="boot-bar-fill" :style="{ width: bootProgress + '%' }"></div></div>
        <div class="boot-sub">{{ video?.group_no ? '小组频道 · ' + video.group_no : '教师演示模式' }} · SESSION {{ sessionNo }}</div>
      </div>
    </Transition>

    <!-- ─── 仿真工作站主界面 ─── -->
    <Transition name="sim-fade">
      <div v-if="modelValue" class="sim-station">
        <!-- 顶部系统栏 -->
        <header class="st-top">
          <div class="st-brand">
            <span class="st-logo">◤</span>
            <div class="st-brand-text">
              <b>低空应急运输虚拟仿真系统</b>
              <i>SIM-PLATFORM V2.1 · SESSION {{ sessionNo }}</i>
            </div>
          </div>
          <div class="st-status"><span class="st-dot"></span>{{ statusText }}</div>
          <div class="st-right">
            <span v-if="video?.group_no" class="st-group">{{ video.group_no }}</span>
            <span class="st-clock">{{ clockText }}</span>
            <button class="st-exit" title="退出仿真 (ESC)" @click="close">⏏ 退出仿真</button>
          </div>
        </header>

        <div class="st-main">
          <!-- 左侧遥测面板 -->
          <aside class="st-col">
            <div class="st-col-title">无人机遥测 TELEMETRY</div>
            <div v-for="(t, i) in telemetry" :key="i" class="tel-item">
              <div class="tel-row">
                <span class="tel-name">{{ t.name }}</span>
                <span class="tel-val">{{ t.value }}<i>{{ t.unit }}</i></span>
              </div>
              <div class="tel-bar"><div :style="{ width: t.pct + '%' }"></div></div>
            </div>
            <div class="st-col-foot">遥测链路 · 实时同步中</div>
          </aside>

          <!-- 中央仿真视口 -->
          <div class="st-viewport" ref="viewportEl">
            <video
              v-if="modelValue && video"
              ref="videoEl"
              class="vp-video"
              :src="video.blobUrl || video.url"
              playsinline
              @timeupdate="onTime"
              @ended="onEnded"
              @play="paused = false"
              @pause="paused = true"
              @loadedmetadata="onMeta"
              @click="togglePlay"
            ></video>
            <div class="vp-grid"></div>
            <div class="vp-corner tl"></div><div class="vp-corner tr"></div>
            <div class="vp-corner bl"></div><div class="vp-corner br"></div>
            <div class="vp-scan"></div>

            <div v-if="paused && !ended" class="vp-paused" @click="togglePlay">
              <span class="vp-play-icon">▶</span> 继续仿真
            </div>
            <div v-if="ended" class="vp-end">
              <div class="vp-end-title">✓ 仿真演练完成</div>
              <div class="vp-end-sub">本组运输方案仿真回放已结束</div>
              <div class="vp-end-actions">
                <button @click="replay">↻ 重新仿真</button>
                <button class="primary" @click="close">退出仿真</button>
              </div>
            </div>
          </div>

          <!-- 右侧任务面板 -->
          <aside class="st-col">
            <div class="st-col-title">任务参数 MISSION</div>
            <template v-if="hasPlan">
              <div class="mis-item"><span>运输总距离</span><b>{{ optStore.totalDistance?.toFixed(2) || '—' }} <i>km</i></b></div>
              <div class="mis-item"><span>预计总用时</span><b>{{ optStore.totalTime || '—' }} <i>min</i></b></div>
              <div class="mis-item"><span>出动无人机</span><b>{{ uavCount }} <i>架</i></b></div>
              <div class="mis-item"><span>配送目标点</span><b>{{ demandCount }} <i>个</i></b></div>
            </template>
            <div v-else class="mis-empty">当前方案数据未同步<br />（演示回放模式）</div>
            <div class="st-col-title" style="margin-top:14px">执行阶段 PHASE</div>
            <div class="phase-list">
              <div v-for="(p, i) in phases" :key="i" class="phase-item" :class="{ on: phaseIdx >= i }">
                <span class="ph-dot"></span>{{ p }}
              </div>
            </div>
            <div class="st-col-foot">方案来源 · 应急规划智能体</div>
          </aside>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import { useUavsStore } from '@/stores/pathPlanning/uavs'
import { usePointsStore } from '@/stores/pathPlanning/points'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  video: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'ended'])

const optStore = useOptimizerStore()
const uavStore = useUavsStore()
const pointsStore = usePointsStore()

const videoEl = ref(null)
const viewportEl = ref(null)

/* ─── 会话标识与方案数据 ─── */
const sessionNo = 'SIM-' + Date.now().toString(36).toUpperCase().slice(-6)
const hasPlan = computed(() => !!optStore.result)
const uavCount = computed(() => uavStore.selections?.length || 0)
const demandCount = computed(() => pointsStore.demands?.length || 0)

/* ─── 加载引导序列 ─── */
const booting = ref(false)
const bootProgress = ref(0)
const bootStage = ref('')
const bootStages = ['正在连接仿真引擎…', '加载三维场景资源…', '同步本组运输方案数据…', '建立无人机遥测链路…']
let bootTimer = null

function startBoot() {
  booting.value = true
  bootProgress.value = 0
  let i = 0
  bootStage.value = bootStages[0]
  bootTimer = setInterval(() => {
    bootProgress.value = Math.min(100, bootProgress.value + 4 + Math.random() * 6)
    const stage = Math.min(bootStages.length - 1, Math.floor(bootProgress.value / (100 / bootStages.length)))
    bootStage.value = bootStages[stage]
    if (bootProgress.value >= 100) {
      clearInterval(bootTimer)
      setTimeout(() => { booting.value = false; enterStation() }, 400)
    }
  }, 110)
}

/* ─── 进入工作站：起表、起遥测、自动播放 ─── */
const clockText = ref('--:--:--')
const statusText = ref('仿真引擎运行中')
const paused = ref(true)
const ended = ref(false)
const cur = ref(0)
const dur = ref(0)
const pct = computed(() => (dur.value ? (cur.value / dur.value) * 100 : 0))
const telemetry = ref([
  { name: '飞行高度 ALT', value: '118.0', unit: 'm', pct: 59 },
  { name: '飞行速度 SPD', value: '12.4', unit: 'm/s', pct: 52 },
  { name: '机体姿态 ATT', value: '-2.3', unit: '°', pct: 48 },
  { name: '链路信号 LINK', value: '96', unit: '%', pct: 96 },
  { name: '剩余电量 BAT', value: '100', unit: '%', pct: 100 },
])
const phases = ['航线装载', '起飞爬升', '巡航运输', '精准投送', '返航降落']
const phaseIdx = ref(0)
let tickTimer = null
let telTimer = null
let clockTimer = null

function enterStation() {
  ended.value = false
  phaseIdx.value = 0
  // 自动播放仿真视口
  if (videoEl.value) videoEl.value.play().catch(() => {})
  // 仿真阶段随播放进度推进
  tickTimer = setInterval(() => {
    if (dur.value) phaseIdx.value = Math.min(phases.length - 1, Math.floor((cur.value / dur.value) * phases.length))
  }, 500)
  // 遥测数据随机游走，电量随播放进度消耗
  telTimer = setInterval(() => {
    const t = telemetry.value
    const alt = 100 + Math.random() * 40
    const spd = 10 + Math.random() * 5
    const att = (Math.random() - 0.5) * 8
    const link = 88 + Math.random() * 11
    const bat = Math.max(5, 100 - pct.value * 0.35)
    t[0].value = alt.toFixed(1); t[0].pct = ((alt - 90) / 60) * 100
    t[1].value = spd.toFixed(1); t[1].pct = ((spd - 8) / 9) * 100
    t[2].value = att.toFixed(1); t[2].pct = 50 + att * 6
    t[3].value = link.toFixed(0); t[3].pct = link
    t[4].value = bat.toFixed(0); t[4].pct = bat
  }, 600)
  // 平台时钟
  const tick = () => { clockText.value = new Date().toLocaleTimeString('zh-CN', { hour12: false }) }
  tick()
  clockTimer = setInterval(tick, 1000)
}

/* ─── 播放控制 ─── */
function togglePlay() {
  if (!videoEl.value) return
  videoEl.value.paused ? videoEl.value.play().catch(() => {}) : videoEl.value.pause()
}
function replay() {
  ended.value = false
  if (videoEl.value) { videoEl.value.currentTime = 0; videoEl.value.play().catch(() => {}) }
}
function onTime() { if (videoEl.value) cur.value = videoEl.value.currentTime }
function onMeta() { if (videoEl.value) dur.value = videoEl.value.duration || 0 }
function onEnded() {
  ended.value = true
  statusText.value = '演练结束 · 数据已归档'
  emit('ended')
}

function close() { emit('update:modelValue', false) }
function onEsc(e) { if (e.key === 'Escape' && props.modelValue && !booting.value) close() }

/* 打开 → 走加载引导；关闭 → 全部清理 */
watch(() => props.modelValue, (open) => {
  if (open) {
    startBoot()
  } else {
    clearInterval(bootTimer)
    videoEl.value?.pause()
  }
})

onMounted(() => document.addEventListener('keydown', onEsc))
onUnmounted(() => {
  document.removeEventListener('keydown', onEsc)
  clearInterval(bootTimer); clearInterval(tickTimer); clearInterval(telTimer); clearInterval(clockTimer)
})
// 组件卸载/关闭时清掉运行中的定时器
watch([paused, ended], () => {
  if (!paused.value && !ended.value) statusText.value = '仿真引擎运行中'
})
watch(() => props.modelValue, (open) => {
  if (open) {
    statusText.value = '仿真引擎运行中'
  } else {
    clearInterval(tickTimer); clearInterval(telTimer); clearInterval(clockTimer)
  }
})
</script>

<style scoped>
/* ═══ 加载引导层 ═══ */
.sim-boot {
  position: fixed;
  inset: 0;
  z-index: 4200;
  background: #030a18;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
}
.boot-logo {
  font-size: 44px;
  color: #22d3ee;
  text-shadow: 0 0 30px rgba(34, 211, 238, 0.8);
  animation: bootPulse 1.2s ease-in-out infinite;
}
@keyframes bootPulse { 0%, 100% { opacity: 0.55; transform: scale(0.97); } 50% { opacity: 1; transform: scale(1.03); } }
.boot-name { color: #e6f3ff; font-size: 20px; font-weight: 700; letter-spacing: 6px; }
.boot-stage { color: #22d3ee; font-size: 13px; letter-spacing: 2px; margin-top: 18px; min-height: 18px; }
.boot-bar {
  width: 320px; height: 4px; border-radius: 2px;
  background: rgba(34, 211, 238, 0.12); overflow: hidden;
}
.boot-bar-fill {
  height: 100%; border-radius: 2px;
  background: linear-gradient(90deg, #0ea5b7, #22d3ee);
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.7);
  transition: width 0.12s linear;
}
.boot-sub { color: rgba(160, 190, 220, 0.45); font-size: 11px; letter-spacing: 1.5px; font-family: Consolas, monospace; }

/* ═══ 工作站整体 ═══ */
.sim-station {
  position: fixed;
  inset: 0;
  z-index: 4000;
  background: #040b1a;
  display: flex;
  flex-direction: column;
}
/* 顶部系统栏 */
.st-top {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 10px 20px;
  border-bottom: 1px solid rgba(34, 211, 238, 0.22);
  background: linear-gradient(180deg, rgba(12, 32, 58, 0.9), rgba(6, 18, 36, 0.9));
  flex-shrink: 0;
}
.st-brand { display: flex; align-items: center; gap: 10px; }
.st-logo { color: #22d3ee; font-size: 22px; text-shadow: 0 0 14px rgba(34, 211, 238, 0.8); }
.st-brand-text { display: flex; flex-direction: column; gap: 1px; }
.st-brand-text b { color: #e6f3ff; font-size: 14px; letter-spacing: 2px; }
.st-brand-text i { color: rgba(140, 180, 215, 0.55); font-size: 10px; font-style: normal; font-family: Consolas, monospace; letter-spacing: 1px; }
.st-status {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  color: #4ade80; font-size: 12px; letter-spacing: 1.5px;
}
.st-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #4ade80; box-shadow: 0 0 8px rgba(74, 222, 128, 0.9);
  animation: blink 1.6s ease-in-out infinite;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
.st-right { display: flex; align-items: center; gap: 12px; }
.st-group {
  color: #22d3ee; font-size: 12px;
  border: 1px solid rgba(34, 211, 238, 0.45); border-radius: 999px;
  padding: 2px 12px; letter-spacing: 1px;
  background: rgba(34, 211, 238, 0.08);
}
.st-clock { color: #9fc3e8; font-size: 13px; font-family: Consolas, monospace; letter-spacing: 1px; }
.st-exit {
  padding: 7px 16px;
  border: 1px solid rgba(255, 120, 120, 0.4);
  border-radius: 8px;
  background: rgba(255, 90, 90, 0.08);
  color: #ff9b9b; font-size: 12px; letter-spacing: 1px;
  cursor: pointer; transition: all 0.2s;
}
.st-exit:hover { background: rgba(255, 90, 90, 0.18); border-color: rgba(255, 120, 120, 0.7); color: #ffc9c9; }

/* ═══ 主体三栏 ═══ */
.st-main { flex: 1; min-height: 0; display: flex; gap: 12px; padding: 12px 16px; }
.st-col {
  width: 228px; flex-shrink: 0;
  display: flex; flex-direction: column;
  border: 1px solid rgba(34, 211, 238, 0.16);
  border-radius: 10px;
  background: rgba(10, 26, 48, 0.55);
  padding: 12px 14px;
  overflow-y: auto;
}
.st-col-title { color: rgba(140, 190, 230, 0.75); font-size: 11px; letter-spacing: 2px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(34, 211, 238, 0.14); }
.st-col-foot { margin-top: auto; padding-top: 10px; color: rgba(120, 160, 200, 0.4); font-size: 10px; letter-spacing: 1px; }

/* 遥测条目 */
.tel-item { margin-bottom: 14px; }
.tel-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 5px; }
.tel-name { color: rgba(170, 200, 228, 0.7); font-size: 11px; letter-spacing: 0.5px; }
.tel-val { color: #22d3ee; font-family: Consolas, monospace; font-size: 16px; font-weight: 700; }
.tel-val i { font-style: normal; font-size: 10px; color: rgba(140, 190, 230, 0.6); margin-left: 3px; }
.tel-bar { height: 3px; border-radius: 2px; background: rgba(34, 211, 238, 0.12); overflow: hidden; }
.tel-bar div { height: 100%; background: linear-gradient(90deg, #0ea5b7, #22d3ee); box-shadow: 0 0 6px rgba(34, 211, 238, 0.6); transition: width 0.5s ease; }

/* 任务参数 */
.mis-item { display: flex; justify-content: space-between; align-items: baseline; padding: 8px 0; border-bottom: 1px dashed rgba(34, 211, 238, 0.1); }
.mis-item span { color: rgba(170, 200, 228, 0.7); font-size: 12px; }
.mis-item b { color: #e6f3ff; font-family: Consolas, monospace; font-size: 14px; }
.mis-item b i { font-style: normal; font-size: 10px; color: rgba(140, 190, 230, 0.6); margin-left: 2px; }
.mis-item b { font-weight: 700; }
.mis-empty { color: rgba(150, 180, 210, 0.45); font-size: 12px; line-height: 1.8; padding: 10px 0; text-align: center; }
.phase-list { display: flex; flex-direction: column; gap: 8px; }
.phase-item { display: flex; align-items: center; gap: 8px; color: rgba(150, 180, 210, 0.45); font-size: 12px; letter-spacing: 1px; transition: color 0.3s; }
.phase-item.on { color: #4ade80; }
.ph-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(150, 180, 210, 0.3); flex-shrink: 0; }
.phase-item.on .ph-dot { background: #4ade80; box-shadow: 0 0 8px rgba(74, 222, 128, 0.8); }

/* ═══ 中央视口 ═══ */
.st-viewport {
  flex: 1; min-width: 0;
  position: relative;
  border: 1px solid rgba(34, 211, 238, 0.28);
  border-radius: 10px;
  background: #000;
  overflow: hidden;
  box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.5), 0 0 24px rgba(34, 211, 238, 0.08);
}
.vp-video { width: 100%; height: 100%; object-fit: contain; outline: none; }
/* HUD 网格叠加 */
.vp-grid {
  position: absolute; inset: 0; pointer-events: none; opacity: 0.1;
  background-image: linear-gradient(rgba(34, 211, 238, 0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 211, 238, 0.5) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse at center, transparent 55%, black 100%);
  -webkit-mask-image: radial-gradient(ellipse at center, transparent 55%, black 100%);
}
/* 四角框线 */
.vp-corner { position: absolute; width: 34px; height: 34px; pointer-events: none; border-color: rgba(34, 211, 238, 0.75); border-style: solid; border-width: 0; }
.vp-corner.tl { top: 10px; left: 10px; border-top-width: 2px; border-left-width: 2px; }
.vp-corner.tr { top: 10px; right: 10px; border-top-width: 2px; border-right-width: 2px; }
.vp-corner.bl { bottom: 10px; left: 10px; border-bottom-width: 2px; border-left-width: 2px; }
.vp-corner.br { bottom: 10px; right: 10px; border-bottom-width: 2px; border-right-width: 2px; }
/* 扫描光效 */
.vp-scan {
  position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(180deg, transparent 0%, rgba(34, 211, 238, 0.05) 48%, rgba(34, 211, 238, 0.12) 50%, rgba(34, 211, 238, 0.05) 52%, transparent 100%);
  background-size: 100% 240px;
  animation: scanMove 7s linear infinite;
  opacity: 0.55;
}
@keyframes scanMove { 0% { background-position: 0 -240px; } 100% { background-position: 0 calc(100% + 240px); } }

/* 暂停浮层 */
.vp-paused {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  background: rgba(2, 8, 18, 0.55);
  color: #e6f3ff; font-size: 16px; letter-spacing: 3px;
  cursor: pointer;
}
.vp-play-icon {
  width: 52px; height: 52px; border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, 0.8);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; color: #22d3ee; padding-left: 4px;
  background: rgba(34, 211, 238, 0.12);
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.4);
}
/* 结束浮层 */
.vp-end {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  background: rgba(2, 8, 18, 0.72);
}
.vp-end-title { color: #4ade80; font-size: 22px; font-weight: 700; letter-spacing: 4px; }
.vp-end-sub { color: rgba(170, 200, 228, 0.6); font-size: 13px; letter-spacing: 1px; }
.vp-end-actions { display: flex; gap: 14px; margin-top: 16px; }
.vp-end-actions button {
  padding: 10px 26px;
  border: 1px solid rgba(34, 211, 238, 0.45); border-radius: 8px;
  background: rgba(34, 211, 238, 0.08);
  color: #9fd8ee; font-size: 13px; letter-spacing: 2px; cursor: pointer; transition: all 0.2s;
}
.vp-end-actions button:hover { background: rgba(34, 211, 238, 0.18); color: #e6f3ff; }
.vp-end-actions button.primary { background: rgba(34, 211, 238, 0.22); color: #e6f3ff; border-color: rgba(34, 211, 238, 0.7); }

/* 过渡动画 */
.sim-fade-enter-active, .sim-fade-leave-active { transition: opacity 0.3s ease; }
.sim-fade-enter-from, .sim-fade-leave-to { opacity: 0; }

/* 窄屏隐藏侧栏，保视口 */
@media (max-width: 1100px) {
  .st-col { display: none; }
  .st-status { display: none; }
}
</style>
