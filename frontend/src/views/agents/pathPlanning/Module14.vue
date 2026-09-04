<template>
  <div class="module14">
    <!-- ─── 方案摘要卡 ─── -->
    <div class="sim-panel plan-panel">
      <div class="panel-head">
        <span class="panel-title">📋 当前方案</span>
        <span class="panel-sub">来自路径规划与方案优出</span>
      </div>

      <template v-if="hasPlan">
        <div class="plan-stats">
          <div class="stat">
            <span class="stat-val">{{ optStore.totalDistance?.toFixed(2) || '—' }}</span>
            <span class="stat-label">总距离 (km)</span>
          </div>
          <div class="stat">
            <span class="stat-val">{{ optStore.totalTime || '—' }}</span>
            <span class="stat-label">总用时 (min)</span>
          </div>
          <div class="stat">
            <span class="stat-val">{{ uavCount }}</span>
            <span class="stat-label">无人机 (架)</span>
          </div>
          <div class="stat">
            <span class="stat-val">{{ demandCount }}</span>
            <span class="stat-label">配送点 (个)</span>
          </div>
        </div>
        <div class="plan-meta" v-if="reportStore.hasReport">
          已生成方案报告：{{ reportStore.reportData?.title || reportStore.currentReport?.title || '未命名方案' }}
        </div>
      </template>
      <div v-else class="plan-empty">
        还没有可仿真的方案 —— 请先在「路径规划」中完成规划，或进入「方案优出」确定方案。
      </div>
    </div>

    <!-- ─── 仿真视频区 ─── -->
    <div class="sim-panel video-panel">
      <div class="panel-head">
        <span class="panel-title">🎬 虚拟仿真</span>
        <span class="panel-sub">{{ myGroupLabel }}</span>
      </div>

      <!-- 本组视频 -->
      <div v-if="myVideos.length > 0" class="my-video-area">
        <div
          v-for="v in myVideos"
          :key="v.id"
          class="sim-video-card"
          @click="startSimulation(v)"
        >
          <div class="svc-play">▶</div>
          <div class="svc-info">
            <div class="svc-title">{{ v.title }}</div>
            <div class="svc-meta">{{ v.uploader_name || '教师' }} · {{ v.created_at }}</div>
          </div>
        </div>
        <button
          class="start-sim-btn"
          :disabled="!hasPlan"
          :title="hasPlan ? '全屏播放本组仿真视频' : '请先完成路径规划确定方案'"
          @click="startSimulation(myVideos[0])"
        >▶ 开始仿真</button>
        <p class="preload-status" v-if="myVideos[0]">
          <template v-if="myVideos[0].blobUrl">✓ 视频已缓存到本机，播放不占服务器带宽</template>
          <template v-else-if="myVideos[0].preloading">⬇ 正在预加载本组视频… {{ preloadProgress }}%</template>
        </p>
      </div>

      <!-- 没有本组视频：教师显示全部可选 / 学生提示 -->
      <div v-else class="no-video">
        <template v-if="videos.length > 0">
          <p class="nv-hint">{{ isTeacher ? '当前账号没有小组编号，可选择任意视频演示：' : '未找到你所在小组的视频，可从下方选择（或联系教师确认小组编号）：' }}</p>
          <div class="all-videos">
            <div
              v-for="v in videos"
              :key="v.id"
              class="sim-video-card"
              @click="startSimulation(v)"
            >
              <div class="svc-play">▶</div>
              <div class="svc-info">
                <div class="svc-title">{{ v.title }}</div>
                <div class="svc-meta">{{ v.group_no ? `第 ${v.group_no} 组` : '通用' }} · {{ v.created_at }}</div>
              </div>
            </div>
          </div>
          <button class="start-sim-btn" :disabled="!hasPlan" @click="startSimulation(videos[0])">▶ 开始仿真</button>
        </template>
        <template v-else>
          <div class="nv-empty">
            <div class="nv-icon">🎬</div>
            <p>教师还没有上传仿真视频</p>
            <p class="nv-sub" v-if="isTeacher">请到「学习资源」页面上传（右上角菜单 → 学习资源）</p>
            <p class="nv-sub" v-else>请等待教师在「学习资源」页面上传本组视频</p>
          </div>
        </template>
      </div>
    </div>

    <!-- 全屏播放器 -->
    <SimulationVideoPlayer v-model="playerVisible" :video="playingVideo" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import { useReportStore } from '@/stores/pathPlanning/report'
import { useUavsStore } from '@/stores/pathPlanning/uavs'
import { usePointsStore } from '@/stores/pathPlanning/points'
import { useUserStore } from '@/stores/user'
import { fetchSimulationList } from '@/api/simulations'
import SimulationVideoPlayer from '@/components/SimulationVideoPlayer.vue'

const optStore = useOptimizerStore()
const reportStore = useReportStore()
const uavStore = useUavsStore()
const pointsStore = usePointsStore()
const userStore = useUserStore()

const isTeacher = computed(() => userStore.role === 'teacher')
const myGroup = computed(() => String(userStore.user?.group_no || '').trim())

/** 小组编号归一化：提取数字（"第3组"/"3组"/"3" 都视为 3） */
function normGroup(s) {
  const m = String(s || '').match(/\d+/)
  return m ? m[0] : String(s || '').trim()
}

const hasPlan = computed(() => !!optStore.result)
const uavCount = computed(() => uavStore.selections?.length || 0)
const demandCount = computed(() => pointsStore.demands?.length || 0)

const videos = ref([])
const playerVisible = ref(false)
const playingVideo = ref(null)

const myVideos = computed(() => {
  if (!myGroup.value) return []
  return videos.value.filter(v => normGroup(v.group_no) === normGroup(myGroup.value))
})

const myGroupLabel = computed(() =>
  myGroup.value ? `第 ${myGroup.value} 组专属仿真视频` : '教师演示模式 · 可选择任意视频'
)

function startSimulation(v) {
  if (!hasPlan.value) {
    ElMessage.warning('请先完成路径规划，确定方案后再开始仿真')
    return
  }
  if (!v) return
  playingVideo.value = v
  playerVisible.value = true
}

/* ─── 预加载：进页面即把本组视频后台下载为 Blob，点播放时零网络请求 ─── */
const preloadProgress = ref(0)

async function preloadVideo(v) {
  if (!v || v.blobUrl || v.preloading) return
  v.preloading = true
  preloadProgress.value = 0
  try {
    const res = await fetch(v.url)
    if (!res.ok) throw new Error(res.status)
    const total = Number(res.headers.get('content-length')) || v.file_size || 0
    const reader = res.body.getReader()
    const chunks = []
    let received = 0
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      chunks.push(value)
      received += value.length
      if (total) preloadProgress.value = Math.min(99, Math.round((received / total) * 100))
    }
    const blob = new Blob(chunks, { type: 'video/mp4' })
    v.blobUrl = URL.createObjectURL(blob)
    preloadProgress.value = 100
  } catch (err) {
    console.warn('[Module14] 预加载失败，将回退为在线流式播放', err)
  } finally {
    v.preloading = false
  }
}

onMounted(async () => {
  try {
    const res = await fetchSimulationList()
    videos.value = res.data || []
    // 只预加载本组的第一个视频：6 组各自缓存各自的，带宽错峰
    preloadVideo(myVideos.value[0])
  } catch (err) {
    console.warn('[Module14] 仿真视频列表加载失败', err)
  }
})
</script>

<style scoped>
.module14 {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
  overflow-y: auto;
  min-height: 0;
}

.sim-panel {
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--navy2);
  padding: 16px 20px;
}
.panel-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}
.panel-title { font-size: 14px; font-weight: 700; color: var(--text); }
.panel-sub { font-size: 11px; color: var(--text3); }

/* 方案统计 */
.plan-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: rgba(0, 229, 255, 0.04);
}
.stat-val {
  font-family: var(--mono);
  font-size: 22px;
  font-weight: 700;
  color: var(--teal);
}
.stat-label { font-size: 11px; color: var(--text3); }
.plan-meta {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text2);
}
.plan-empty {
  padding: 18px 4px;
  font-size: 13px;
  color: var(--text3);
  line-height: 1.7;
}

/* 视频卡片 */
.my-video-area, .all-videos {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.sim-video-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
  transition: all 0.2s;
  min-width: 260px;
}
.sim-video-card:hover {
  border-color: var(--teal);
  background: rgba(0, 229, 255, 0.06);
  transform: translateY(-1px);
}
.svc-play {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid var(--teal);
  color: var(--teal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  padding-left: 3px;
  flex-shrink: 0;
}
.sim-video-card:hover .svc-play {
  background: rgba(0, 229, 255, 0.15);
  box-shadow: 0 0 14px rgba(0, 229, 255, 0.35);
}
.svc-title { font-size: 13px; font-weight: 600; color: var(--text); }
.svc-meta { font-size: 11px; color: var(--text3); margin-top: 2px; }

/* 开始仿真按钮 */
.start-sim-btn {
  align-self: flex-start;
  padding: 10px 34px;
  border-radius: 9px;
  border: 1px solid var(--teal);
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.18), rgba(0, 229, 255, 0.08));
  color: var(--teal);
  font-size: 15px;
  font-weight: 700;
  font-family: var(--sans);
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s;
}
.start-sim-btn:hover:not(:disabled) {
  background: rgba(0, 229, 255, 0.26);
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.35);
}
.start-sim-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.preload-status {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--text3);
}
.preload-status { color: var(--teal); opacity: 0.85; }

/* 无视频空态 */
.no-video { padding: 4px 0; }
.nv-hint { font-size: 13px; color: var(--text2); margin-bottom: 10px; }
.nv-empty { text-align: center; padding: 36px 0 20px; color: var(--text3); }
.nv-icon { font-size: 40px; margin-bottom: 10px; }
.nv-sub { font-size: 12px; color: var(--text3); opacity: 0.8; margin-top: 6px; }
</style>
