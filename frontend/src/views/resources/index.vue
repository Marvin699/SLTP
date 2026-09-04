<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/home')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <el-divider direction="vertical" />
        <h1>学习资源</h1>
        <span class="header-sub">虚拟仿真视频 · 按小组播放</span>
      </div>
      <div class="header-right">
        <template v-if="isTeacher">
          <el-button type="primary" @click="uploadVisible = true">
            <el-icon><Upload /></el-icon> 上传仿真视频
          </el-button>
          <el-button @click="refreshList" :loading="loading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </template>
        <el-button v-else @click="refreshList" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- 提示条 -->
    <div class="hint-bar">
      💡 教师上传虚拟仿真视频并标注小组编号（1~6 组）；学生在「应急调度」第四步 · 虚拟仿真模块中
      确定方案后即可点击「开始仿真」观看本组对应的仿真视频。
    </div>

    <div v-loading="loading" class="video-groups">
      <div
        v-for="g in groupedVideos"
        :key="g.key"
        class="group-block"
      >
        <div class="group-head">
          <span class="group-badge">{{ g.key }}</span>
          <span class="group-count">{{ g.videos.length }} 个视频</span>
        </div>
        <div class="video-grid">
          <div v-for="v in g.videos" :key="v.id" class="video-card">
            <div class="vc-cover" @click="play(v)">
              <span class="vc-play">▶</span>
              <span class="vc-ext">{{ v.file_ext?.replace('.', '').toUpperCase() }}</span>
            </div>
            <div class="vc-info">
              <div class="vc-title" :title="v.title">{{ v.title }}</div>
              <div class="vc-meta">
                {{ v.uploader_name || '教师' }} · {{ v.created_at }} · {{ formatSize(v.file_size) }}
              </div>
            </div>
            <el-button
              v-if="isTeacher"
              class="vc-del"
              size="small"
              type="danger"
              link
              @click="handleDelete(v)"
            >删除</el-button>
          </div>
        </div>
      </div>

      <div v-if="!loading && videos.length === 0" class="empty-state">
        <div class="empty-icon">🎬</div>
        <p>暂无仿真视频</p>
        <p class="empty-sub" v-if="isTeacher">点击右上角「上传仿真视频」开始添加</p>
        <p class="empty-sub" v-else>请等待教师上传</p>
      </div>
    </div>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传仿真视频" width="460px">
      <el-form label-width="90px">
        <el-form-item label="视频标题">
          <el-input v-model="uploadForm.title" placeholder="默认使用文件名" maxlength="100" />
        </el-form-item>
        <el-form-item label="小组编号">
          <el-select v-model="uploadForm.group_no" placeholder="选择该视频对应的小组" style="width: 100%">
            <el-option label="第 1 组" value="1" />
            <el-option label="第 2 组" value="2" />
            <el-option label="第 3 组" value="3" />
            <el-option label="第 4 组" value="4" />
            <el-option label="第 5 组" value="5" />
            <el-option label="第 6 组" value="6" />
          </el-select>
        </el-form-item>
        <el-form-item label="视频文件">
          <div class="upload-pick" @click="$refs.fileInput.click()">
            <input
              ref="fileInput"
              type="file"
              accept="video/mp4,video/webm,video/ogg,.mp4,.webm,.mov"
              style="display: none"
              @change="onFileChange"
            />
            <span v-if="!uploadForm.file" class="pick-placeholder">点击选择视频文件（MP4，≤500MB）</span>
            <span v-else class="pick-file">🎬 {{ uploadForm.file.name }}（{{ formatSize(uploadForm.file.size) }}）</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 播放器 -->
    <SimulationVideoPlayer v-model="playerVisible" :video="playingVideo" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Upload, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { fetchSimulationList, uploadSimulationVideo, deleteSimulationVideo } from '@/api/simulations'
import SimulationVideoPlayer from '@/components/SimulationVideoPlayer.vue'

const userStore = useUserStore()
const isTeacher = computed(() => userStore.role === 'teacher')

const videos = ref([])
const loading = ref(false)

const groupedVideos = computed(() => {
  const groups = {}
  for (const v of videos.value) {
    const key = v.group_no ? `第 ${v.group_no} 组` : '通用'
    ;(groups[key] = groups[key] || []).push(v)
  }
  // 按组号数字排序，"通用"排最后
  return Object.entries(groups)
    .map(([key, vids]) => ({ key, videos: vids }))
    .sort((a, b) => {
      const na = a.key.match(/\d+/)?.[0]
      const nb = b.key.match(/\d+/)?.[0]
      if (na && nb) return na - nb
      if (na) return -1
      if (nb) return 1
      return a.key.localeCompare(b.key)
    })
})

const playerVisible = ref(false)
const playingVideo = ref(null)

const uploadVisible = ref(false)
const uploading = ref(false)
const uploadForm = ref({ title: '', group_no: '', file: null })

function formatSize(bytes) {
  if (!bytes) return '—'
  if (bytes > 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return Math.max(1, Math.round(bytes / 1024)) + ' KB'
}

async function refreshList() {
  loading.value = true
  try {
    const res = await fetchSimulationList()
    videos.value = res.data || []
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '获取视频列表失败')
  } finally {
    loading.value = false
  }
}

function play(v) {
  playingVideo.value = v
  playerVisible.value = true
}

function onFileChange(e) {
  uploadForm.value.file = e.target.files[0] || null
}

async function submitUpload() {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择视频文件')
    return
  }
  uploading.value = true
  try {
    await uploadSimulationVideo(uploadForm.value.file, uploadForm.value.group_no, uploadForm.value.title)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    uploadForm.value = { title: '', group_no: '', file: null }
    refreshList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleDelete(v) {
  try {
    await ElMessageBox.confirm(`确定删除视频「${v.title}」？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteSimulationVideo(v.id)
    ElMessage.success('删除成功')
    refreshList()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '删除失败')
  }
}

onMounted(refreshList)
</script>

<style scoped>
.page-container {
  padding: 24px 28px;
  max-width: 1400px;
  margin: 0 auto;
  color: var(--brand-text, #e6edf5);
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-left h1 {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid #22d3ee;
}
.header-sub {
  font-size: 12px;
  color: rgba(200, 212, 226, 0.55);
}
.back-btn { color: rgba(200, 212, 226, 0.7); }

.hint-bar {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid rgba(34, 211, 238, 0.22);
  background: rgba(34, 211, 238, 0.06);
  color: rgba(200, 212, 226, 0.85);
  font-size: 13px;
  line-height: 1.7;
  margin-bottom: 20px;
}

.group-block { margin-bottom: 28px; }
.group-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.group-badge {
  font-size: 14px;
  font-weight: 700;
  color: #22d3ee;
  padding: 3px 14px;
  border-radius: 999px;
  border: 1px solid rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.08);
}
.group-count { font-size: 12px; color: rgba(200, 212, 226, 0.5); }

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.video-card {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  overflow: hidden;
  transition: all 0.2s;
}
.video-card:hover {
  border-color: rgba(34, 211, 238, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}
.vc-cover {
  height: 120px;
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.12), rgba(59, 130, 246, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
}
.vc-play {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, 0.7);
  color: #22d3ee;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  padding-left: 4px;
  transition: all 0.2s;
}
.vc-cover:hover .vc-play {
  background: rgba(34, 211, 238, 0.2);
  box-shadow: 0 0 18px rgba(34, 211, 238, 0.4);
}
.vc-ext {
  position: absolute;
  right: 8px;
  bottom: 8px;
  font-size: 10px;
  color: rgba(200, 212, 226, 0.6);
  letter-spacing: 1px;
}
.vc-info { padding: 10px 12px 6px; }
.vc-title {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.vc-meta {
  font-size: 11px;
  color: rgba(200, 212, 226, 0.5);
  margin-top: 3px;
}
.vc-del { margin: 2px 8px 6px; }

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: rgba(200, 212, 226, 0.7);
}
.empty-icon { font-size: 44px; margin-bottom: 12px; }
.empty-sub { font-size: 12px; color: rgba(200, 212, 226, 0.45); margin-top: 6px; }

.upload-pick {
  width: 100%;
  padding: 14px;
  border-radius: 8px;
  border: 1px dashed rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.04);
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.upload-pick:hover { border-color: #22d3ee; }
.pick-placeholder { color: rgba(200, 212, 226, 0.55); font-size: 13px; }
.pick-file { color: #22d3ee; font-size: 13px; }
</style>
