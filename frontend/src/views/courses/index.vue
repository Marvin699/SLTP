<template>
  <div class="courses-page">
    <!-- 标题区 -->
    <div class="page-hero">
      <div class="title-line">
        <h1 class="main-title">我的课程</h1>
        <span class="sub-title">课件资料 · 随时查阅</span>
      </div>
      <button v-if="isTeacher" class="upload-btn" @click="openUploadDialog">
        <el-icon><Upload /></el-icon>
        <span>上传课件</span>
      </button>
    </div>

    <!-- 课程卡片 -->
    <div v-if="courses.length" class="course-grid">
      <div
        v-for="course in courses"
        :key="course.name"
        class="course-card"
        @click="$router.push(`/courses/${encodeURIComponent(course.name)}`)"
      >
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="url(#cwGrad)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <defs>
              <linearGradient id="cwGrad" x1="0" y1="0" x2="24" y2="24">
                <stop offset="0" stop-color="#22d3ee"/>
                <stop offset="1" stop-color="#3b82f6"/>
              </linearGradient>
            </defs>
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4a2 2 0 0 0-2-2H6.5A2.5 2.5 0 0 0 4 4.5v15z"/>
            <path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>
          </svg>
        </div>
        <div class="card-info">
          <h3 class="course-name">{{ course.name }}</h3>
          <p class="course-meta">{{ course.count }} 个文件 · {{ course.latest }}</p>
        </div>
        <el-icon class="card-arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <p>暂无课程资料</p>
      <p class="empty-hint">{{ isTeacher ? '点击右上角"上传课件"开始建设课程' : '老师还没有上传课件，敬请期待' }}</p>
    </div>

    <div v-if="loading" class="empty-state"><p>加载中...</p></div>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传课件 / 资料" width="440px" class="upload-dialog">
      <el-form label-width="80px">
        <el-form-item label="课程名" required>
          <el-input v-model="uploadForm.courseName" placeholder="如：应急物资低空智慧运输" />
        </el-form-item>
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
import { Upload, ArrowRight, Plus, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { fetchCoursewareList, uploadCourseware } from '@/api/courseware'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isTeacher = computed(() => userStore.role === 'teacher')

const loading = ref(false)
const rawList = ref([])

// 按课程名分组
const courses = computed(() => {
  const map = new Map()
  for (const item of rawList.value) {
    if (!map.has(item.course_name)) map.set(item.course_name, { name: item.course_name, count: 0, latest: item.created_at })
    const c = map.get(item.course_name)
    c.count += 1
    if (item.created_at > c.latest) c.latest = item.created_at
  }
  return [...map.values()].sort((a, b) => b.count - a.count)
})

async function load() {
  loading.value = true
  try {
    const res = await fetchCoursewareList()
    rawList.value = res.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载课件列表失败')
  } finally {
    loading.value = false
  }
}

// 上传相关
const uploadVisible = ref(false)
const uploading = ref(false)
const fileInputRef = ref(null)
const uploadForm = ref({ courseName: '', title: '', fileType: 'courseware', file: null })

function openUploadDialog() {
  uploadForm.value = { courseName: '', title: '', fileType: 'courseware', file: null }
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
  const { courseName, title, fileType, file } = uploadForm.value
  if (!courseName.trim()) return ElMessage.warning('请填写课程名')
  if (!file) return ElMessage.warning('请选择文件')
  uploading.value = true
  try {
    await uploadCourseware(file, courseName, title, fileType)
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
.courses-page {
  padding: 28px clamp(20px, 4vw, 48px);
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 60px);
}

.page-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 28px;
}

.title-line {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.main-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  padding-left: 14px;
  border-left: 4px solid #22d3ee;
  line-height: 1.2;
}

.sub-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 2px;
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
}

.upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 26px rgba(34, 211, 238, 0.55);
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.course-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  border-radius: 16px;
  background: rgba(8, 15, 28, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.course-card:hover {
  border-color: rgba(34, 211, 238, 0.55);
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35), 0 0 18px rgba(34, 211, 238, 0.12);
}

.card-icon {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  border-radius: 12px;
  background: rgba(34, 211, 238, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon svg {
  width: 26px;
  height: 26px;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.course-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.card-arrow {
  color: rgba(255, 255, 255, 0.25);
  transition: all 0.3s ease;
}

.course-card:hover .card-arrow {
  color: #22d3ee;
  transform: translateX(3px);
}

.empty-state {
  text-align: center;
  padding: 120px 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 15px;
}

.empty-hint {
  margin-top: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.3);
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
