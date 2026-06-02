<template>
  <div class="evaluation-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <div class="header-left">
        <h1>{{ selectedTaskName }}</h1>
      </div>
      <div class="header-right">
        <!-- 项目选择 -->
        <el-select v-model="selectedProjectId" placeholder="选择项目" size="default"
          style="width: 200px" @change="onProjectChange" :loading="projectsLoading">
          <el-option v-for="p in projects" :key="p.project_id" :label="`${p.project_id} · ${p.name}`" :value="p.project_id" />
        </el-select>
        <!-- 任务选择 -->
        <el-select v-model="selectedTaskId" placeholder="选择任务" size="default"
          style="width: 260px" :disabled="!selectedProjectId || tasksLoading" :loading="tasksLoading">
          <el-option v-for="t in taskList" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <button class="back-home-btn" @click="$router.push('/')">
          <span>🏠</span> 返回首页
        </button>
      </div>
    </div>

    <!-- 三环节卡片 -->
    <div class="section-cards">
      <div v-for="sec in sections" :key="sec.id" class="section-card">
        <div class="card-top">
          <div class="card-badge" :class="getBadgeClass(sec.id)">{{ sec.short_name }}</div>
          <div class="card-time">{{ sec.time_range }}</div>
        </div>
        <h3 class="card-name">{{ sec.name }}</h3>
        <p class="card-desc">{{ sec.description }}</p>

        <!-- 维度标签 -->
        <div class="card-dims">
          <span v-for="dim in sec.dimensions" :key="dim" class="dim-tag">{{ dim }}</span>
        </div>

        <!-- 统计数据 -->
        <div class="card-stats">
          <div class="stat-item">
            <span class="stat-value">{{ overviewData[sec.id]?.session_count || 0 }}</span>
            <span class="stat-label">评分链接</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ overviewData[sec.id]?.total_scorers || 0 }}</span>
            <span class="stat-label">打分人</span>
          </div>
          <div class="stat-item">
            <span class="stat-value" :class="getStatusClass(sec.id)">
              {{ overviewData[sec.id]?.session_count ? '已启用' : '待启用' }}
            </span>
            <span class="stat-label">状态</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <el-button type="primary" @click="goSection(sec.id, 'links')">
            <el-icon><Link /></el-icon> 管理链接
          </el-button>
          <el-button @click="goSection(sec.id, 'overview')">
            <el-icon><DataAnalysis /></el-icon> 成绩总览
          </el-button>
          <el-button @click="goSection(sec.id, 'ai')">
            <el-icon><Monitor /></el-icon> 智能体评分
          </el-button>
        </div>
      </div>
    </div>

    <!-- 快速操作提示 -->
    <div class="quick-tips">
      <div class="tip-icon">📋</div>
      <div class="tip-content">
        <h4>课前准备</h4>
        <p>进入「管理链接」为每个环节生成评分链接，将链接分享给打分人（教师、企业导师、学生观察员），扫码即可进入打分页面。打分数据实时汇总到「成绩总览」。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Link, DataAnalysis, Monitor } from '@element-plus/icons-vue'
import { fetchSections, fetchOverview } from '@/api/scoreSession'
import { fetchProjects, fetchProject } from '@/api/courseGraph'

const router = useRouter()
const route = useRoute()
const sections = ref([])
const overviewData = ref({})

// --- 项目/任务选择 ---
const projects = ref([])
const projectsLoading = ref(false)
const selectedProjectId = ref('')
const taskList = ref([])
const tasksLoading = ref(false)
const selectedTaskId = ref(null)

const selectedTaskName = computed(() => {
  if (!selectedTaskId.value || !taskList.value.length) {
    return '教学智评'
  }
  const task = taskList.value.find(t => t.id === selectedTaskId.value)
  if (task) return task.name
  return '教学智评'
})

const FALLBACK_SECTIONS = [
  { id: 'section1', name: '环节一：运输方案汇报与知识深化', short_name: '方案汇报', time_range: '0-10min', description: '小组汇报运输方案，教师/企业导师提问，AI词云与风险分析', dimensions: ['方案完整性', '表达展示', '操作规范', '团队配合'] },
  { id: 'section2', name: '环节二：无预案应急推演', short_name: '应急推演', time_range: '10-20min', description: '突发应急场景，使用路径规划智能体进行无预案推演', dimensions: ['决策速度', '方案可行性', '风险评估', '团队配合'] },
  { id: 'section3', name: '环节三：飞行前准备应急演练比拼', short_name: '应急演练', time_range: '21-36min', description: '限时飞行前检查、双电转单电操作、团队协作应急演练', dimensions: ['安全性', '操作规范性', '用时效率', '团队配合'] },
]

// --- 数据加载 ---
async function loadProjects() {
  projectsLoading.value = true
  try {
    const res = await fetchProjects()
    projects.value = Array.isArray(res.data) ? res.data : []
    // 默认选中P5
    if (!selectedProjectId.value && projects.value.length) {
      const p5 = projects.value.find(p => p.project_id === 'P5')
      selectedProjectId.value = p5 ? p5.project_id : projects.value[0].project_id
      await onProjectChange(selectedProjectId.value)
    }
  } catch {
    projects.value = []
  } finally {
    projectsLoading.value = false
  }
}

async function onProjectChange(projectId) {
  if (!projectId) { taskList.value = []; selectedTaskId.value = null; return }
  tasksLoading.value = true
  taskList.value = []
  selectedTaskId.value = null
  try {
    const res = await fetchProject(projectId)
    const project = res.data
    // 从 sub_projects 中提取所有任务
    const subProjects = Array.isArray(project.sub_projects) ? project.sub_projects : []
    const allTasks = []
    for (const sub of subProjects) {
      const tasks = Array.isArray(sub.tasks) ? sub.tasks : []
      for (const task of tasks) {
        allTasks.push({ id: task.id, name: task.name, sub_project_name: sub.name })
      }
    }
    taskList.value = allTasks
    // 默认选中任务8
    const task8 = allTasks.find(t => t.id === 8)
    selectedTaskId.value = task8 ? task8.id : (allTasks.length ? allTasks[0].id : null)
  } catch {
    taskList.value = []
  } finally {
    tasksLoading.value = false
  }
}

async function loadSections() {
  try {
    const res = await fetchSections()
    sections.value = Array.isArray(res.data) ? res.data : FALLBACK_SECTIONS
  } catch {
    sections.value = FALLBACK_SECTIONS
  }
}

async function loadOverview() {
  try {
    const res = await fetchOverview()
    overviewData.value = res.data || {}
  } catch {
    overviewData.value = {}
  }
}

function getBadgeClass(secId) {
  const map = { section1: 'badge-blue', section2: 'badge-orange', section3: 'badge-green' }
  return map[secId] || 'badge-blue'
}

function getStatusClass(secId) {
  const ov = overviewData.value[secId]
  if (ov?.session_count) return 'status-active'
  return 'status-pending'
}

function goSection(secId, tab) {
  router.push({ path: `/evaluation/section/${secId}`, query: { tab } })
}

onMounted(async () => {
  await Promise.all([loadProjects(), loadSections(), loadOverview()])
  // 如果有 section 和 tab query params，直接跳转到对应环节的对应tab
  const targetSection = route.query.section
  const targetTab = route.query.tab
  if (targetSection) {
    goSection(targetSection, targetTab || 'ai')
  }
})
</script>

<style scoped>
.evaluation-page {
  padding: 24px;
  color: #fff;
  min-height: calc(100vh - 100px);
}

/* 顶部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  gap: 16px;
}
.page-header h1 { margin: 0; font-size: 22px; font-weight: 700; white-space: nowrap; }
.header-right {
  display: flex; align-items: center; gap: 12px; flex-shrink: 0;
}
.back-home-btn {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
  color: #c0c8d4; border-radius: 8px; padding: 8px 16px; cursor: pointer;
  font-size: 14px; transition: all 0.2s;
}
.back-home-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* 下拉框暗色主题 */
:deep(.el-select .el-input__wrapper) {
  background: rgba(13,33,55,0.8);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: none;
  border-radius: 8px;
}
:deep(.el-select .el-input__wrapper:hover) {
  border-color: rgba(64,158,255,0.4);
}
:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: #409eff;
}
:deep(.el-select .el-input__inner) {
  color: #e2e8f0;
}
:deep(.el-select .el-input__inner::placeholder) {
  color: rgba(255,255,255,0.35);
}
:deep(.el-select .el-input__suffix) {
  color: rgba(255,255,255,0.4);
}

/* 环节卡片 */
.section-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.section-card {
  background: rgba(13, 33, 55, 0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}
.section-card:hover {
  border-color: rgba(64,158,255,0.3);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  transform: translateY(-2px);
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.card-badge {
  font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 20px;
}
.badge-blue { background: rgba(64,158,255,0.15); color: #409eff; border: 1px solid rgba(64,158,255,0.3); }
.badge-orange { background: rgba(245,158,11,0.15); color: #f59c0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-green { background: rgba(103,194,58,0.15); color: #67c23a; border: 1px solid rgba(103,194,58,0.3); }
.card-time { font-size: 12px; color: #718096; }
.card-name { margin: 0 0 8px; font-size: 17px; font-weight: 600; }
.card-desc { margin: 0 0 14px; font-size: 13px; color: #c0c8d4; line-height: 1.6; flex-shrink: 0; }

/* 维度标签 */
.card-dims {
  display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px;
}
.dim-tag {
  font-size: 11px; padding: 3px 8px; border-radius: 4px;
  background: rgba(255,255,255,0.04); color: #718096; border: 1px solid rgba(255,255,255,0.06);
}

/* 统计数据 */
.card-stats {
  display: flex; gap: 16px; margin-bottom: 18px;
  padding: 14px 0; border-top: 1px solid rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.06);
}
.stat-item { flex: 1; text-align: center; }
.stat-value { display: block; font-size: 22px; font-weight: 700; color: #fff; }
.stat-label { display: block; font-size: 12px; color: #718096; margin-top: 2px; }
.status-active { color: #67c23a; }
.status-pending { color: #718096; }

/* 操作按钮 */
.card-actions {
  display: flex; gap: 10px; margin-top: auto;
}
.card-actions .el-button { flex: 1; }

/* 快速提示 */
.quick-tips {
  display: flex; gap: 14px; padding: 18px 22px;
  background: rgba(13,33,55,0.6); border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
}
.tip-icon { font-size: 28px; flex-shrink: 0; }
.tip-content h4 { margin: 0 0 6px; font-size: 14px; color: #e2e8f0; }
.tip-content p { margin: 0; font-size: 13px; color: #718096; line-height: 1.6; }

:deep(.el-button:not(.el-button--primary):not(.el-button--danger):not(.el-button--success):not(.el-button--warning)) {
  --el-button-bg-color: rgba(64,158,255,0.15);
  --el-button-border-color: rgba(64,158,255,0.3);
  --el-button-text-color: #a0c4ff;
  --el-button-hover-bg-color: rgba(64,158,255,0.25);
  --el-button-hover-border-color: rgba(64,158,255,0.5);
  --el-button-hover-text-color: #66b1ff;
}
</style>
