<template>
  <div class="course-detail-page">
    <!-- 标题区 -->
    <div class="page-hero">
      <div class="title-line">
        <el-icon class="back-btn" :size="22" @click="$router.push('/courses')"><ArrowLeft /></el-icon>
        <h1 class="main-title">{{ courseName }}</h1>
        <span class="sub-title">{{ filteredList.length }} 个文件</span>
      </div>
      <button v-if="isTeacher" class="upload-btn" @click="openUploadDialog">
        <el-icon><Upload /></el-icon>
        <span>上传</span>
      </button>
    </div>

    <!-- 类型筛选 -->
    <div class="filter-bar">
      <button
        v-for="tab in filterTabs"
        :key="tab.key"
        class="filter-tab"
        :class="{ active: filterType === tab.key }"
        @click="filterType = tab.key"
      >{{ tab.label }}</button>
    </div>

    <!-- 文件列表 -->
    <div class="file-panel">
      <div v-for="item in filteredList" :key="item.id" class="file-row">
        <div class="file-icon" :data-type="iconType(item.file_ext)">
          <span>{{ extLabel(item.file_ext) }}</span>
        </div>
        <div class="file-info">
          <p class="file-title">{{ item.title }}</p>
          <p class="file-meta">
            {{ item.filename }} · {{ formatSize(item.file_size) }} · {{ item.uploader_name || '未知' }} · {{ item.created_at }} · 下载 {{ item.download_count }} 次
          </p>
        </div>
        <div class="file-actions">
          <el-tooltip content="该格式不支持在线预览，请下载查看" placement="top" :disabled="canPreview(item)">
            <span>
              <el-button text size="small" class="action-btn" :disabled="!canPreview(item)" @click="preview(item)">预览</el-button>
            </span>
          </el-tooltip>
          <el-button text size="small" class="action-btn" @click="download(item)">下载</el-button>
          <el-button v-if="isTeacher" text size="small" class="action-btn danger" @click="removeItem(item)">删除</el-button>
        </div>
      </div>
      <div v-if="!filteredList.length" class="empty-state">
        <p>{{ filterType === 'all' ? '该课程还没有文件' : '该类型下暂无文件' }}</p>
      </div>
    </div>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" :title="'上传到：' + courseName" width="440px" class="upload-dialog">
      <el-form label-width="80px">
        <el-form-item label="课件标题">
          <el-input v-model="uploadForm.title" placeholder="默认使用文件名" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="uploadForm.fileType">
            <el-radio value="courseware">课件</el-radio>
            <el-radio value="material">资料</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="文件" required>
          <div v-if="uploadForm.file" class="file-selected">
            <span class="fs-name">{{ uploadForm.file.name }}</span>
            <el-icon class="fs-remove" title="移除文件" @click="clearFile"><CircleCloseFilled /></el-icon>
          </div>
          <div v-else class="file-picker" @click="fileInputRef && fileInputRef.click()">
            <el-icon><Plus /></el-icon>
            <span>点击选择文件</span>
            <span class="picker-hint">PPT / Word / PDF / 视频 / 图片等，≤200MB</span>
          </div>
          <input ref="fileInputRef" type="file" class="file-input-hidden" @change="onFileChange" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Upload, ArrowLeft, Plus, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchCoursewareList, uploadCourseware, downloadCourseware, deleteCourseware, previewUrl } from '@/api/courseware'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const isTeacher = computed(() => userStore.role === 'teacher')
const courseName = computed(() => decodeURIComponent(route.params.courseName || ''))

const loading = ref(false)
const rawList = ref([])
const filterType = ref('all')

const filterTabs = [
  { key: 'all', label: '全部' },
  { key: 'courseware', label: '课件' },
  { key: 'material', label: '资料' },
]

const filteredList = computed(() => {
  if (filterType.value === 'all') return rawList.value
  return rawList.value.filter(i => i.file_type === filterType.value)
})

async function load() {
  loading.value = true
  try {
    const res = await fetchCoursewareList(courseName.value)
    rawList.value = res.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// 文件类型展示
function iconType(ext) {
  if (['.pdf'].includes(ext)) return 'pdf'
  if (['.ppt', '.pptx'].includes(ext)) return 'ppt'
  if (['.doc', '.docx', '.txt'].includes(ext)) return 'doc'
  if (['.xls', '.xlsx'].includes(ext)) return 'xls'
  if (['.mp4', '.mp3'].includes(ext)) return 'video'
  if (['.png', '.jpg', '.jpeg', '.gif'].includes(ext)) return 'image'
  return 'other'
}

function extLabel(ext) {
  return (ext || '?').replace('.', '').toUpperCase() || '?'
}

function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function canPreview(item) {
  return ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mp3'].includes(item.file_ext)
}

function preview(item) {
  window.open(previewUrl(item), '_blank')
}

async function download(item) {
  try {
    await downloadCourseware(item)
    ElMessage.success('开始下载')
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

async function removeItem(item) {
  try {
    await ElMessageBox.confirm(`确定删除「${item.title}」吗？此操作不可恢复。`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteCourseware(item.id)
    ElMessage.success('删除成功')
    await load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

// 上传相关
const uploadVisible = ref(false)
const uploading = ref(false)
const fileInputRef = ref(null)
const uploadForm = ref({ title: '', fileType: 'courseware', file: null })

function openUploadDialog() {
  uploadForm.value = { title: '', fileType: 'courseware', file: null }
  uploadVisible.value = true
}

function onFileChange(e) {
  uploadForm.value.file = e.target.files[0] || null
}

function clearFile() {
  uploadForm.value.file = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

async function submitUpload() {
  const { title, fileType, file } = uploadForm.value
  if (!file) return ElMessage.warning('请选择文件')
  uploading.value = true
  try {
    await uploadCourseware(file, courseName.value, title, fileType)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

onMounted(load)
</script>

<style scoped>
.course-detail-page {
  padding: 28px clamp(20px, 4vw, 48px);
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 60px);
}

.page-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
}

.title-line {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.back-btn {
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: color 0.25s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  color: #22d3ee;
}

.main-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  padding-left: 14px;
  border-left: 4px solid #22d3ee;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  flex-shrink: 0;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 26px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #22d3ee, #3b82f6);
  color: #04121c;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.35);
  flex-shrink: 0;
}

.upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 26px rgba(34, 211, 238, 0.55);
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.filter-tab {
  padding: 7px 20px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.filter-tab:hover {
  color: #fff;
}

.filter-tab.active {
  border-color: rgba(34, 211, 238, 0.6);
  background: rgba(34, 211, 238, 0.12);
  color: #22d3ee;
}

.file-panel {
  border-radius: 16px;
  background: rgba(8, 15, 28, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  overflow: hidden;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 22px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: background 0.25s ease;
}

.file-row:last-child {
  border-bottom: none;
}

.file-row:hover {
  background: rgba(34, 211, 238, 0.05);
}

.file-icon {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.file-icon[data-type='pdf'] { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.file-icon[data-type='ppt'] { background: rgba(249, 115, 22, 0.15); color: #fb923c; }
.file-icon[data-type='doc'] { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.file-icon[data-type='xls'] { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.file-icon[data-type='video'] { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.file-icon[data-type='image'] { background: rgba(34, 211, 238, 0.15); color: #22d3ee; }
.file-icon[data-type='other'] { background: rgba(255, 255, 255, 0.08); color: rgba(255, 255, 255, 0.5); }

.file-info {
  flex: 1;
  min-width: 0;
}

.file-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.38);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.action-btn {
  color: rgba(255, 255, 255, 0.65);
}

.action-btn:hover {
  color: #22d3ee;
  background: rgba(34, 211, 238, 0.1);
}

.action-btn.danger:hover {
  color: #f87171;
  background: rgba(239, 68, 68, 0.1);
}

.action-btn.is-disabled,
.action-btn:disabled {
  color: rgba(255, 255, 255, 0.22) !important;
  background: transparent !important;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
}

.file-picker {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  padding: 24px 16px;
  border-radius: 10px;
  border: 1px dashed rgba(34, 211, 238, 0.45);
  background: rgba(34, 211, 238, 0.05);
  color: #22d3ee;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.file-picker:hover {
  border-color: rgba(34, 211, 238, 0.8);
  background: rgba(34, 211, 238, 0.1);
}

.picker-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
}

.file-input-hidden {
  display: none;
}

.file-selected {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.08);
}

.fs-name {
  flex: 1;
  font-size: 13px;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fs-remove {
  color: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  transition: color 0.25s ease;
  flex-shrink: 0;
}

.fs-remove:hover {
  color: #f87171;
}
</style>
