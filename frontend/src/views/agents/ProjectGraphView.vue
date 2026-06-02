<template>
  <div class="project-page">
    <!-- 顶部导航 -->
    <header class="view-header">
      <div class="header-left">
        <el-button @click="goBack" class="back-btn" text>
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-divider"></div>
        <div class="header-title">
          <el-icon :size="18"><DataBoard /></el-icon>
          项目详情
        </div>
      </div>
      <div class="header-right">
        <el-tag type="info" effect="dark" size="small">{{ projects.length }} 个项目</el-tag>
      </div>
    </header>

    <!-- 项目详情列表 -->
    <main class="detail-main">
      <div v-loading="loading" class="detail-list">
        <div
          v-for="proj in projects"
          :key="proj.project_id"
          class="detail-card"
        >
          <div class="card-head">
            <div class="card-head-left">
              <span class="card-id" :style="{ color: getProjectColor(proj.project_id) }">{{ proj.project_id }}</span>
              <h3 class="card-name">{{ proj.name }}</h3>
            </div>
            <el-button
              type="primary"
              size="small"
              plain
              @click.stop="goToGraph(proj.project_id)"
            >
              查看图谱
              <el-icon class="el-icon--right"><Share /></el-icon>
            </el-button>
          </div>

          <div class="card-stats">
            <div class="stat-item">
              <span class="stat-value">{{ proj.hours }}</span>
              <span class="stat-label">学时</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ proj.task_count }}</span>
              <span class="stat-label">任务数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ getSubProjectCount(proj) }}</span>
              <span class="stat-label">子项目</span>
            </div>
          </div>

          <!-- 描述 -->
          <div v-if="proj.description" class="card-section">
            <div class="section-label">项目描述</div>
            <div class="section-text">{{ proj.description }}</div>
          </div>

          <!-- 关联认证 -->
          <div v-if="proj.certifications && proj.certifications.length" class="card-section">
            <div class="section-label">关联认证与大赛</div>
            <div class="cert-list">
              <el-tag
                v-for="(cert, ci) in proj.certifications"
                :key="ci"
                size="small"
                effect="dark"
                type="warning"
                class="cert-tag"
              >{{ cert }}</el-tag>
            </div>
          </div>

          <!-- 子项目结构 -->
          <div v-if="getSubProjects(proj).length" class="card-section">
            <div class="section-label">
              子项目结构
              <span class="section-count">{{ getSubProjects(proj).length }} 个子项目</span>
            </div>
            <div class="sub-projects">
              <div
                v-for="(sp, si) in getSubProjects(proj)"
                :key="si"
                class="sub-project-item"
              >
                <div class="sp-header" @click="toggleSubProject(proj.project_id, si)">
                  <el-icon class="sp-arrow" :class="{ expanded: isExpanded(proj.project_id, si) }"><ArrowRight /></el-icon>
                  <span class="sp-name">{{ sp.name || `子项目 ${si + 1}` }}</span>
                  <span class="sp-hours" v-if="sp.hours">{{ sp.hours }}学时</span>
                  <span class="sp-tasks" v-if="sp.tasks">{{ sp.tasks.length }}个任务</span>
                </div>
                <div v-if="isExpanded(proj.project_id, si)" class="sp-detail">
                  <div v-if="sp.description" class="sp-desc">{{ sp.description }}</div>
                  <div v-if="sp.tasks && sp.tasks.length" class="task-list">
                    <div
                      v-for="(task, ti) in sp.tasks"
                      :key="ti"
                      class="task-item"
                    >
                      <div class="task-header">
                        <span class="task-name">{{ task.name || `任务 ${ti + 1}` }}</span>
                        <el-tag v-if="task.type" size="small" effect="plain" class="task-type-tag">{{ task.type }}</el-tag>
                      </div>
                      <div v-if="task.points && task.points.length" class="task-points">
                        <span
                          v-for="(pt, pti) in task.points"
                          :key="pti"
                          class="point-chip"
                        >{{ pt.name || pt }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading && projects.length === 0" description="暂无项目数据" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight, DataBoard, Share } from '@element-plus/icons-vue'
import { fetchProjects } from '@/api/courseGraph'

const router = useRouter()
const projects = ref([])
const loading = ref(false)
const expandedKeys = reactive({})

const projectColors = {
  P1: '#3498db',
  P2: '#9b59b6',
  P3: '#00e5ff',
  P4: '#ff9800',
  P5: '#67c23a'
}

function getProjectColor(id) {
  return projectColors[id] || '#409eff'
}

function getSubProjects(proj) {
  if (!proj.sub_projects) return []
  if (Array.isArray(proj.sub_projects)) return proj.sub_projects
  return []
}

function getSubProjectCount(proj) {
  return getSubProjects(proj).length
}

function toggleSubProject(projectId, index) {
  const key = `${projectId}-${index}`
  expandedKeys[key] = !expandedKeys[key]
}

function isExpanded(projectId, index) {
  return !!expandedKeys[`${projectId}-${index}`]
}

async function loadProjects() {
  loading.value = true
  try {
    const res = await fetchProjects()
    projects.value = res.data || []
  } catch (e) {
    console.error('加载项目失败', e)
  } finally {
    loading.value = false
  }
}

function goToGraph(projectId) {
  router.push({ path: '/agent/teaching-graph/view', query: { project: projectId } })
}

const goBack = () => router.push('/agent/teaching-graph')

onMounted(() => loadProjects())
</script>

<style scoped>
.project-page {
  min-height: 100vh;
  background: #0a1628;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
}

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 52px;
  background: linear-gradient(90deg, #0d2137 0%, #1a3a5c 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.3);
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.back-btn { color: #c0c8d4 !important; font-size: 13px; }
.back-btn:hover { color: #409eff !important; }
.header-divider { width: 1px; height: 18px; background: rgba(255,255,255,0.15); }
.header-title { font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.header-title .el-icon { color: #409eff; }

.detail-main {
  flex: 1;
  padding: 32px 24px;
  display: flex;
  justify-content: center;
  overflow-y: auto;
}

.detail-list {
  max-width: 900px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  background: linear-gradient(135deg, rgba(13, 33, 55, 0.9) 0%, rgba(26, 58, 92, 0.7) 100%);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 14px;
  padding: 24px;
  transition: border-color 0.3s;
}
.detail-card:hover {
  border-color: rgba(64, 158, 255, 0.4);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.card-id {
  font-size: 14px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(255,255,255,0.08);
}
.card-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #fff;
}

.card-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-value {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.stat-label { font-size: 12px; color: #c0c8d4; margin-top: 4px; }

.card-section { margin-bottom: 16px; }
.card-section:last-child { margin-bottom: 0; }
.section-label {
  font-size: 13px;
  font-weight: 600;
  color: #c0c8d4;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-count {
  font-weight: 400;
  font-size: 12px;
  color: #718096;
}
.section-text {
  font-size: 13px;
  color: #cbd5e0;
  line-height: 1.7;
}

.cert-list { display: flex; flex-wrap: wrap; gap: 6px; }
.cert-tag { border-radius: 10px; }

.sub-projects { display: flex; flex-direction: column; gap: 8px; }

.sub-project-item {
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  overflow: hidden;
}

.sp-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.sp-header:hover { background: rgba(64, 158, 255, 0.06); }

.sp-arrow {
  font-size: 12px;
  color: #718096;
  transition: transform 0.2s;
}
.sp-arrow.expanded { transform: rotate(90deg); color: #409eff; }

.sp-name { font-size: 14px; font-weight: 600; color: #e2e8f0; flex: 1; }
.sp-hours, .sp-tasks {
  font-size: 12px;
  color: #718096;
  padding: 2px 8px;
  border-radius: 8px;
  background: rgba(255,255,255,0.06);
}

.sp-detail {
  padding: 0 14px 12px;
  border-top: 1px solid rgba(255,255,255,0.04);
}
.sp-desc {
  font-size: 12px;
  color: #c0c8d4;
  line-height: 1.6;
  margin: 8px 0;
}

.task-list { display: flex; flex-direction: column; gap: 6px; }
.task-item {
  padding: 8px 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 6px;
  border-left: 2px solid rgba(64, 158, 255, 0.4);
}
.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.task-name { font-size: 13px; font-weight: 500; color: #e2e8f0; }
.task-type-tag { border-radius: 8px; }

.task-points {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.point-chip {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 8px;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}
</style>
