<template>
  <div class="evaluation-page">
    <!-- 仪式感页头 -->
    <div class="page-title-block">
      <div class="title-row">
        <span class="title-bar"></span>
        <h1>教学智评</h1>
        <span class="title-sub">诊断 → 形成 → 总结 · 教师 / 企业导师 / AI / 学生 四元评价</span>
      </div>
      <div class="title-tools">
        <el-select v-model="selectedProjectId" placeholder="选择项目" size="default"
          style="width: 190px" @change="onProjectChange" :loading="projectsLoading">
          <el-option v-for="p in projects" :key="p.project_id" :label="`${p.project_id} · ${p.name}`" :value="p.project_id" />
        </el-select>
        <el-select v-model="selectedTaskId" placeholder="选择任务" size="default"
          style="width: 240px" :disabled="!selectedProjectId || tasksLoading" :loading="tasksLoading"
          @change="onTaskChange">
          <el-option v-for="t in taskList" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <button class="tool-btn" @click="goBackToGraph" title="返回图谱">
          <svg viewBox="0 0 24 24" width="15" height="15"><path fill="currentColor" d="M3.4 20.4 20.9 3.4a1 1 0 0 1 1.7.8v6.4a1 1 0 0 1-.4.8L4.9 20.9z"/><path fill="currentColor" d="m3.4 20.4 15.4-17.9a1 1 0 0 1 .8-.4h6.4z" opacity=".4"/></svg>
          图谱
        </button>
        <button class="tool-btn" @click="$router.push('/')" title="返回首页">
          <svg viewBox="0 0 24 24" width="15" height="15"><path fill="currentColor" d="M12 3 2 12h3v8h6v-6h2v6h6v-8h3z"/></svg>
          首页
        </button>
      </div>
    </div>

    <!-- 数据大屏入口（双卡并排） -->
    <div class="entry-row">
      <div class="entry-card" @click="$router.push('/evaluation/dashboard')">
        <div class="entry-icon">
          <svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M3 13h8V3H3zm0 8h8v-6H3zm10 0h8V11h-8zm0-18v6h8V3z"/></svg>
        </div>
        <div class="entry-text">
          <div class="entry-title">教学效果数据大屏</div>
          <div class="entry-sub">项目达成度 · 五维画像 · 增值评价 · 学员名单联动</div>
        </div>
        <div class="entry-arrow">›</div>
      </div>
      <div class="entry-card" @click="$router.push('/evaluation/task8')">
        <div class="entry-icon">
          <svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M4 4h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-6l2 3h-2l-2-3h-2l-2 3H6l2-3H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1m1 2v10h14V6z"/></svg>
        </div>
        <div class="entry-text">
          <div class="entry-title">任务8 · 方案优化与应急模拟演练</div>
          <div class="entry-sub">实时数据大屏 · 六维能力图谱 · 课堂小结</div>
        </div>
        <div class="entry-arrow">›</div>
      </div>
    </div>

    <!-- 三环节卡片 -->
    <div class="section-cards">
      <div v-for="(sec, idx) in sections" :key="sec.id" class="section-card" :class="{ active: overviewData[sec.id]?.session_count }">
        <span class="card-index">0{{ idx + 1 }}</span>
        <div class="card-top">
          <div class="card-badge" :class="getBadgeClass(sec.id)">{{ sec.short_name }}</div>
          <div class="card-time">{{ sec.time_range }}</div>
          <span class="status-light" :class="overviewData[sec.id]?.session_count ? 'on' : ''"></span>
        </div>
        <h3 class="card-name">{{ sec.name }}</h3>
        <p class="card-desc">{{ sec.description }}</p>

        <!-- 评价主体 -->
        <div class="card-dims">
          <span class="dims-line">评价主体 · 教师 · 企业导师 · AI · 学生</span>
        </div>

        <!-- 统计数据 -->
        <div class="card-stats">
          <div class="stat-item">
            <span class="stat-value mono">{{ overviewData[sec.id]?.session_count || 0 }}</span>
            <span class="stat-label">评分链接</span>
          </div>
          <div class="stat-item">
            <span class="stat-value mono">{{ overviewData[sec.id]?.total_scorers || 0 }}</span>
            <span class="stat-label">打分人</span>
          </div>
          <div class="stat-item">
            <span class="stat-value" :class="overviewData[sec.id]?.session_count ? 'status-active' : 'status-pending'">
              {{ overviewData[sec.id]?.session_count ? '已启用' : '待启用' }}
            </span>
            <span class="stat-label">状态</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <template v-if="sec.isLive">
            <el-button type="primary" @click="$router.push(sec.livePath || '/evaluation/section/task4/live')">
              <el-icon><Monitor /></el-icon> 进入大屏
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" @click="goSection(sec.id, 'links')">
              <el-icon><Link /></el-icon> 管理链接
            </el-button>
            <el-button @click="goSection(sec.id, 'overview')">
              <el-icon><DataAnalysis /></el-icon> 成绩总览
            </el-button>
            <el-button @click="goSection(sec.id, 'ai')">
              <el-icon><Monitor /></el-icon> 智能体评分
            </el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 快速操作提示 -->
    <div class="quick-tips">
      <div class="tip-icon">
        <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M16 2H4a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8zm-5 18a2 2 0 1 1 0-4 2 2 0 0 1 0 4m3-10H6V4h8z"/></svg>
      </div>
      <div class="tip-content">
        课前准备：进入「管理链接」为每个环节生成评分链接，分享给打分人（教师、企业导师、学生观察员），扫码即可打分，数据实时汇总到「成绩总览」。
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

const TASK_SECTION_MAP = {
  4: [
    { id: 'live-task4', name: '任务4 · 应急物资低空智慧运输装载与行前准备', short_name: 'AI智能体大屏', time_range: '10min', description: '6组同步包装装载，AI实时识别操作、语音播报错误、推送灾情指令', dimensions: ['操作规范性', '时效性', '安全性', '团队配合'], isLive: true, livePath: '/evaluation/section/task4/live' },
  ],
  8: [
    { id: 'section1', name: '环节一：运输方案汇报与知识深化', short_name: '方案汇报', time_range: '0-10min', description: '小组汇报运输方案，教师/企业导师提问，AI词云与风险分析', dimensions: ['教师评分', '企业导师评分', 'Ai评分', '学生评分'] },
    { id: 'section2', name: '环节二：应急推演与工单处置', short_name: '应急推演', time_range: '10-20min', description: '突发应急场景推演，各组提交工单三要素，AI生成综合质量分', dimensions: ['教师评分', '企业导师评分', 'Ai评分', '学生评分'] },
    { id: 'section3', name: '环节三：飞行演练与裁判评分', short_name: '飞行演练', time_range: '21-36min', description: '限时飞行前检查、双电转单电操作、裁判六维能力评分', dimensions: ['教师评分', '企业导师评分', 'Ai评分', '学生评分'] },
  ],
}

const backendSections = ref([])

const sections = computed(() => {
  if (!selectedTaskId.value) return []
  const mapped = TASK_SECTION_MAP[selectedTaskId.value]
  if (mapped) return mapped
  return backendSections.value || []
})

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
    backendSections.value = Array.isArray(res.data) ? res.data : []
  } catch {
    backendSections.value = []
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

function goBackToGraph() {
  router.push('/agent/teaching-graph')
}

function onTaskChange(taskId) {
  if (taskId === 7) {
    router.push('/evaluation/task7')
  }
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

/* 仪式感页头 */
.page-title-block {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.title-row { display: flex; align-items: baseline; gap: 14px; min-width: 0; }
.title-bar {
  width: 5px; height: 30px; border-radius: 2px; align-self: center;
  background: linear-gradient(180deg, #00D4FF, #0066FF);
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.55);
  flex-shrink: 0;
}
.title-row h1 {
  margin: 0; font-size: 30px; font-weight: 800; letter-spacing: 2px; white-space: nowrap;
  color: #EAF6FF;
  text-shadow: 0 0 22px rgba(0, 168, 255, 0.45);
}
.title-sub {
  font-size: 13px; color: #8FB3D9; letter-spacing: 1px; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.title-tools { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.tool-btn {
  display: flex; align-items: center; gap: 6px;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.35);
  color: #9BE1FF; border-radius: 6px; padding: 7px 14px; cursor: pointer;
  font-size: 13px; letter-spacing: 1px; transition: all 0.2s;
}
.tool-btn:hover {
  background: rgba(0, 212, 255, 0.18); color: #EAF6FF;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.35);
}
.tool-btn svg { flex-shrink: 0; }

/* 下拉框暗色主题 */
:deep(.el-select .el-input__wrapper) {
  background: rgba(13,33,55,0.8);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: none;
  border-radius: 6px;
}
:deep(.el-select .el-input__wrapper:hover) {
  border-color: rgba(0,212,255,0.4);
}
:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: #00D4FF;
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

/* 数据大屏入口 · 双卡并排 */
.entry-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 26px;
}
.entry-card {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 20px;
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, rgba(10, 32, 62, 0.85), rgba(8, 24, 48, 0.85));
  border: 1px solid rgba(0, 212, 255, 0.28);
  clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
  cursor: pointer;
  transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
}
.entry-card::before {
  content: '';
  position: absolute; top: 0; left: -80%;
  width: 50%; height: 100%;
  background: linear-gradient(105deg, transparent, rgba(0, 212, 255, 0.12), transparent);
  transition: left 0.5s ease;
}
.entry-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 212, 255, 0.6);
  box-shadow: 0 6px 22px rgba(0, 120, 220, 0.3);
}
.entry-card:hover::before { left: 130%; }
.entry-icon {
  width: 46px; height: 46px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: #00D4FF;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.4);
  clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
}
.entry-text { flex: 1; min-width: 0; }
.entry-title { font-size: 15px; font-weight: 700; color: #EAF6FF; letter-spacing: 1px; }
.entry-sub { font-size: 12px; color: #7A9CC6; margin-top: 3px; letter-spacing: 0.5px; }
.entry-arrow {
  font-size: 26px; color: #00D4FF; line-height: 1;
  opacity: 0.6; transition: all 0.25s; flex-shrink: 0;
}
.entry-card:hover .entry-arrow { opacity: 1; transform: translateX(4px); }

/* 环节卡片 · HUD 风 */
.section-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.section-card {
  position: relative;
  background: rgba(8, 24, 48, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.22);
  border-radius: 4px;
  padding: 22px 22px 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s;
}
.section-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
  opacity: 0.5;
}
.section-card::after {
  content: '';
  position: absolute; top: 0; left: -80%;
  width: 50%; height: 100%;
  background: linear-gradient(105deg, transparent, rgba(0, 212, 255, 0.08), transparent);
  transition: left 0.55s ease;
  pointer-events: none;
}
.section-card:hover {
  border-color: rgba(0, 212, 255, 0.55);
  box-shadow: 0 6px 24px rgba(0, 100, 200, 0.3), inset 0 0 30px rgba(0, 212, 255, 0.03);
  transform: translateY(-3px);
}
.section-card:hover::after { left: 130%; }
.card-index {
  position: absolute; right: 14px; top: 6px;
  font-family: Consolas, monospace;
  font-size: 44px; font-weight: 800; line-height: 1;
  color: rgba(0, 212, 255, 0.10);
  letter-spacing: 2px;
  pointer-events: none;
}
.section-card.active .card-index { color: rgba(0, 212, 255, 0.18); }
.card-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  position: relative;
}
.card-badge {
  font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 2px;
  letter-spacing: 2px;
  clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
}
.badge-blue { background: rgba(0,168,255,0.14); color: #4DB8FF; border: 1px solid rgba(0,168,255,0.4); }
.badge-orange { background: rgba(255,182,39,0.12); color: #FFB627; border: 1px solid rgba(255,182,39,0.4); }
.badge-green { background: rgba(74,222,128,0.12); color: #4ADE80; border: 1px solid rgba(74,222,128,0.4); }
.card-time { font-size: 12px; color: #7A9CC6; font-family: Consolas, monospace; }
.status-light {
  width: 8px; height: 8px; border-radius: 50%;
  background: #3A4A63; margin-left: auto; flex-shrink: 0;
}
.status-light.on {
  background: #00E5A8;
  box-shadow: 0 0 8px rgba(0, 229, 168, 0.9);
  animation: breath 2s ease-in-out infinite;
}
@keyframes breath {
  0%, 100% { box-shadow: 0 0 4px rgba(0, 229, 168, 0.5); }
  50% { box-shadow: 0 0 12px rgba(0, 229, 168, 1); }
}
.card-name { margin: 0 0 8px; font-size: 17px; font-weight: 700; color: #EAF6FF; letter-spacing: 1px; position: relative; }
.card-desc { margin: 0 0 14px; font-size: 13px; color: #A8BDD9; line-height: 1.65; flex-shrink: 0; position: relative; }

/* 评价主体 */
.card-dims { margin-bottom: 16px; position: relative; }
.dims-line {
  font-size: 12px; color: #6E8BB5; letter-spacing: 1.5px;
  padding-left: 10px;
  border-left: 2px solid rgba(0, 212, 255, 0.35);
}

/* 统计数据 */
.card-stats {
  display: flex; gap: 12px; margin-bottom: 18px;
  padding: 13px 0;
  border-top: 1px solid rgba(0, 212, 255, 0.12);
  border-bottom: 1px solid rgba(0, 212, 255, 0.12);
  position: relative;
}
.stat-item { flex: 1; text-align: center; }
.stat-value {
  display: block; font-size: 22px; font-weight: 700; color: #EAF6FF;
  text-shadow: 0 0 12px rgba(0, 212, 255, 0.35);
}
.stat-value.mono { font-family: Consolas, monospace; }
.stat-label { display: block; font-size: 12px; color: #6E8BB5; margin-top: 3px; letter-spacing: 1px; }
.status-active { color: #00E5A8 !important; text-shadow: 0 0 12px rgba(0, 229, 168, 0.5) !important; }
.status-pending { color: #5E7BA8 !important; text-shadow: none !important; }

/* 操作按钮 */
.card-actions {
  display: flex; gap: 10px; margin-top: auto;
  position: relative;
}
.card-actions .el-button { flex: 1; }

/* 快速提示 */
.quick-tips {
  display: flex; align-items: center; gap: 12px; padding: 13px 20px;
  background: rgba(8, 24, 48, 0.55);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 4px;
}
.tip-icon { color: #00D4FF; flex-shrink: 0; display: flex; opacity: 0.85; }
.tip-content { font-size: 13px; color: #7A9CC6; line-height: 1.6; letter-spacing: 0.5px; }

:deep(.el-button:not(.el-button--primary):not(.el-button--danger):not(.el-button--success):not(.el-button--warning)) {
  --el-button-bg-color: rgba(0, 212, 255, 0.08);
  --el-button-border-color: rgba(0, 212, 255, 0.35);
  --el-button-text-color: #9BE1FF;
  --el-button-hover-bg-color: rgba(0, 212, 255, 0.18);
  --el-button-hover-border-color: rgba(0, 212, 255, 0.6);
  --el-button-hover-text-color: #EAF6FF;
}
</style>
