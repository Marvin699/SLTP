<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/pathPlanning/app'
import { usePointsStore } from '@/stores/pathPlanning/points'
import { useMaterialsStore } from '@/stores/pathPlanning/materials'
import { useUavsStore } from '@/stores/pathPlanning/uavs'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'
import TopBar from '@/components/pathPlanning/TopBar.vue'
import MapView from '@/components/pathPlanning/MapView.vue'
import Module1 from '@/views/agents/pathPlanning/Module1.vue'
import Module2 from '@/views/agents/pathPlanning/Module2.vue'
import Module3 from '@/views/agents/pathPlanning/Module3.vue'
import Module4 from '@/views/agents/pathPlanning/Module4.vue'
import Module5 from '@/views/agents/pathPlanning/Module5.vue'
import Module6 from '@/views/agents/pathPlanning/Module6.vue'
import Module7 from '@/views/agents/pathPlanning/Module7.vue'
import Module8 from '@/views/agents/pathPlanning/Module8.vue'
import RoutesDetail from '@/views/agents/RoutesDetail.vue'
import { useTeacherSolutionsStore } from '@/stores/pathPlanning/teacherSolutions'

const router = useRouter()
const app = useAppStore()
const store = usePointsStore()
const matStore = useMaterialsStore()
const uavStore = useUavsStore()
const optStore = useOptimizerStore()
const tSolStore = useTeacherSolutionsStore()

const isLoading = computed(() => store.loading || matStore.loading || uavStore.loading)
const isDayMode = ref(false)
const toggleTheme = () => { isDayMode.value = !isDayMode.value }

const goBack = () => {
  router.push('/home')
}

function deleteSolution(s) {
  ElMessageBox.confirm(`确定删除「${s.groupId} ${s.studentName}」的提交方案吗？`, '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    tSolStore.remove(s.id)
    ElMessage.success('方案已删除')
  }).catch(() => {})
}

onMounted(() => {
  store.loadPoints()
})
</script>

<template>
  <div class="path-planning-agent-page" :class="{ 'day-mode': isDayMode }">
    <!-- Top header with back button -->
    <header class="agent-top-header">
      <div class="header-left">
        <el-button @click="goBack" type="primary" plain size="small">
          <el-icon><ArrowLeft /></el-icon>
          返回首页
        </el-button>
        <h1 class="page-title">无人机应急调度智能体</h1>
        <el-tag type="info" size="small">v1.2</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="toggleTheme" circle size="small" class="theme-toggle-btn">
          <el-icon :size="16">
            <Sunny v-if="!isDayMode" />
            <Moon v-else />
          </el-icon>
        </el-button>
      </div>
    </header>

    <!-- TopBar for module switching -->
    <TopBar />

    <!-- Main area -->
    <div class="main-area routes-mode" v-if="app.activeModule === 9">
      <RoutesDetail embedded-full />
    </div>

    <!-- 教师端方案审阅（模块 10）-->
    <div class="main-area" v-else-if="app.activeModule === 10">
      <div class="side-panel">
        <div class="panel-body">
          <div class="tc-header">
            <div class="tc-title">👨‍🏫 教师端 · 学生方案审阅</div>
            <div class="tc-sub">共 {{ tSolStore.list.length }} 份方案 · 点击查看可视化</div>
          </div>

          <div class="tc-list">
            <div
              v-for="s in tSolStore.list"
              :key="s.id"
              class="tc-card"
              :class="{ active: s.id === tSolStore.selectedId }"
            >
              <div class="tc-row-1" @click="tSolStore.select(s.id)">
                <span class="tc-group">{{ s.groupId }}</span>
                <span class="tc-verdict" :style="{ color: s.verdictColor || '#64748b', borderColor: s.verdictColor || '#64748b' }">{{ s.verdict || '待评' }}</span>
              </div>
              <div class="tc-name" @click="tSolStore.select(s.id)">👤 {{ s.studentName }}</div>
              <div class="tc-meta" @click="tSolStore.select(s.id)">
                <span>📅 {{ s.submittedAt }}</span>
                <span>✈️ {{ s.uav?.model || '未填' }}</span>
              </div>
              <div class="tc-meta" @click="tSolStore.select(s.id)">
                <span>🛰️ {{ s.optimizer?.totalDistance?.toFixed(1) || 0 }} km</span>
                <span>⏱️ {{ s.optimizer?.totalTime || 0 }} min</span>
                <span>📍 {{ s.demands?.length || 0 }} 点</span>
              </div>
              <div class="tc-note" @click="tSolStore.select(s.id)">{{ s.notes }}</div>
              <button class="tc-del-btn" @click.stop="deleteSolution(s)">🗑 删除</button>
            </div>

            <div v-if="tSolStore.list.length === 0" class="tc-empty">
              暂无学生提交的方案
            </div>
          </div>
        </div>
      </div>

      <div class="tc-map-side">
        <RoutesDetail embedded-full :solution="tSolStore.selected" readOnly />
      </div>
    </div>

    <div class="main-area" v-else>
      <!-- Left side panel -->
      <div class="side-panel">
        <div class="panel-body">
          <!-- Module 1: Delivery Points -->
          <Module1 v-if="app.activeModule === 1" />

          <!-- Module 2: Material Requirements -->
          <Module2 v-else-if="app.activeModule === 2" />

          <!-- Module 3: UAV Selection -->
          <Module3 v-else-if="app.activeModule === 3" />

          <!-- Module 4: Path Planning -->
          <Module4 v-else-if="app.activeModule === 4" />

          <!-- Module 5: Plan Diagnosis -->
          <Module5 v-else-if="app.activeModule === 5" />

          <!-- Module 6: Plan Output -->
          <Module6 v-else-if="app.activeModule === 6" />

          <!-- Module 7: Case Management -->
          <Module7 v-else-if="app.activeModule === 7" />

          <!-- Module 8: System Settings -->
          <Module8 v-else-if="app.activeModule === 8" />

          <!-- Placeholder for other modules -->
          <div
            v-else
            class="placeholder"
          >
            <div class="placeholder-icon">
              {{ app.modules.find(m => m.id === app.activeModule)?.icon }}
            </div>
            <div class="placeholder-text">
              {{ app.modules.find(m => m.id === app.activeModule)?.label }}
            </div>
            <div class="placeholder-sub">
              模块开发中...
            </div>
          </div>
        </div>
      </div>

      <!-- Right side map -->
      <MapView :selected-drone-id="optStore.selectedDroneId" />
    </div>

    <!-- Global loading overlay -->
    <Teleport to="body">
      <div
        v-if="isLoading"
        class="loading-veil"
      >
        <div class="spinner" />
        <div class="loading-msg">数据处理中...</div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.path-planning-agent-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #060d1a;
  color: #cdd9f0;
  font-family: 'Noto Sans SC', sans-serif;
}

/* CSS Variables for path planning agent theme */
.path-planning-agent-page {
  --navy: #060d1a;
  --navy2: #0b1628;
  --navy3: #112040;
  --navy4: #1a2e50;
  --teal: #00e5ff;
  --teal2: #00b4cc;
  --amber: #ffb300;
  --red: #ff3d57;
  --green: #00e676;
  --purple: #aa80ff;
  --text: #cdd9f0;
  --text2: #7a93bb;
  --text3: #3d5a80;
  --border: #162540;
  --border2: #1e3560;
  --glow-teal: 0 0 20px rgba(0, 229, 255, 0.25);
  --glow-amber: 0 0 20px rgba(255, 179, 0, 0.25);
  --mono: 'JetBrains Mono', monospace;
  --sans: 'Noto Sans SC', sans-serif;
}

/* 白天模式 - 柔光色系 */
.path-planning-agent-page.day-mode {
  --navy: #f5f0e8;
  --navy2: #ebe4d8;
  --navy3: #e0d8cc;
  --navy4: #d5ccc0;
  --teal: #1a7a7a;
  --teal2: #155e5e;
  --amber: #b8860b;
  --red: #c0392b;
  --green: #27ae60;
  --purple: #7d3c98;
  --text: #3a3530;
  --text2: #6b6560;
  --text3: #9a9590;
  --border: #d0c8bc;
  --border2: #c0b8ac;
  --glow-teal: 0 0 15px rgba(26, 122, 122, 0.15);
  --glow-amber: 0 0 15px rgba(184, 134, 11, 0.15);
}

.day-mode {
  color: var(--text);
}

.agent-top-header {
  min-height: 52px;
  height: 52px;
  background: var(--navy2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
  z-index: 200;
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-toggle-btn {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text2) !important;
  transition: all 0.3s;
}

.theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: var(--teal) !important;
  border-color: var(--teal) !important;
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--teal);
  margin: 0;
  letter-spacing: 0.5px;
}

.main-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Left side panel */
.side-panel {
  width: 420px;
  flex-shrink: 0;
  background: var(--navy2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 18px;
}

/* Placeholder module */
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 8px;
}

.placeholder-icon {
  font-size: 40px;
  opacity: 0.3;
}

.placeholder-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--text2);
}

.placeholder-sub {
  font-size: 11px;
  color: var(--text3);
}

/* Loading overlay */
.loading-veil {
  position: fixed;
  inset: 0;
  background: rgba(6, 13, 26, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  flex-direction: column;
  gap: 16px;
}

.spinner {
  width: 44px;
  height: 44px;
  border: 2px solid var(--border);
  border-top-color: var(--teal);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-msg {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--teal);
  letter-spacing: 2px;
}

.tc-map-side { flex: 1; position: relative; overflow: hidden; background: #060d1a; }
.tc-header { padding: 16px 16px 10px; border-bottom: 1px solid var(--border); background: var(--navy3); }
.tc-title { font-size: 14px; font-weight: 700; color: #cdd9f0; font-family: var(--mono); letter-spacing: 0.4px; }
.tc-sub { font-size: 11px; color: var(--text3); margin-top: 4px; letter-spacing: 0.3px; }
.tc-list { padding: 10px 16px 20px; display: flex; flex-direction: column; gap: 10px; }
.tc-card { border: 1px solid var(--border); border-radius: 8px; background: var(--navy3); padding: 10px 12px; cursor: pointer; transition: all 0.2s; }
.tc-card:hover { border-color: var(--teal); background: #15325f; }
.tc-card.active { border-color: var(--teal); background: linear-gradient(180deg, #11305a, #0b2445); box-shadow: 0 0 0 1px rgba(0,229,255,0.2), 0 2px 10px rgba(0,0,0,0.35); }
.tc-row-1 { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.tc-group { font-size: 12px; font-weight: 700; color: var(--teal); font-family: var(--mono); }
.tc-verdict { font-size: 10px; font-weight: 700; border: 1px solid currentColor; padding: 1px 8px; border-radius: 10px; letter-spacing: 0.5px; }
.tc-name { font-size: 12px; color: var(--text); margin-bottom: 4px; }
.tc-meta { display: flex; gap: 10px; font-size: 10.5px; color: var(--text3); margin-top: 2px; }
.tc-note { font-size: 10.5px; color: #64748b; margin-top: 6px; line-height: 1.5; border-left: 2px solid var(--border2); padding-left: 8px; }
.tc-del-btn {
  margin-top: 8px; width: 100%; padding: 5px 0; font-size: 11px; font-family: var(--mono);
  color: #fca5a5; background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.4);
  border-radius: 6px; cursor: pointer; transition: all 0.2s;
}
.tc-del-btn:hover { background: rgba(220,38,38,0.25); color: #fecaca; border-color: #ef4444; }
.tc-empty { text-align: center; padding: 40px 10px; color: var(--text3); font-size: 12px; font-family: var(--mono); }
</style>
