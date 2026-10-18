<script setup>
import { useAppStore } from '@/stores/pathPlanning/app'

const app = useAppStore()

defineProps({
  isDay: { type: Boolean, default: false },
})
defineEmits(['back', 'toggle-theme'])

const MODULE_LABELS = {
  1: '配送点', 2: '物资需求', 3: '无人机选型', 4: '路径规划',
  9: '航线详情', 5: '方案诊断', 13: '合规核验', 12: '反向质询', 6: '方案优出', 10: '方案审阅', 14: '虚拟仿真',
}

function onSubModule(id) {
  app.setModule(id)
}

function onStep(s) {
  app.gotoStep(s.id)
}

function onSubmitStep() {
  app.submitStep(app.activeStep)
}
</script>

<template>
  <div class="stepnav">
    <!-- 返回首页 -->
    <button class="nav-icon-btn" title="返回首页" @click="$emit('back')">
      <el-icon :size="15"><ArrowLeft /></el-icon>
    </button>

    <!-- ─── 四步向导（紧凑单行）─── -->
    <nav class="steps">
      <template v-for="(s, i) in app.wizardSteps" :key="s.id">
        <!-- 步骤节点 -->
        <div
          class="step"
          :class="{
            current: app.activeAdmin === null && app.activeStep === s.id,
            done: app.stepSubmitted[s.id],
          }"
          :title="s.desc"
          @click="onStep(s)"
        >
          <div class="step-circle">
            <span v-if="app.stepSubmitted[s.id]" class="step-check">✓</span>
            <span v-else class="step-num">{{ i + 1 }}</span>
          </div>
          <span class="step-title">{{ s.title }}</span>
        </div>
        <!-- 连接线 -->
        <div
          v-if="i < app.wizardSteps.length - 1"
          class="step-link"
          :class="{ lit: app.stepSubmitted[s.id] }"
        ></div>
      </template>
    </nav>

    <div class="bar-spacer" />

    <!-- ─── 当前步骤的子模块 ─── -->
    <div class="subtabs" v-if="app.activeAdmin === null">
      <button
        v-for="mid in app.wizardSteps.find(s => s.id === app.activeStep)?.modules || []"
        :key="mid"
        class="subtab"
        :class="{ active: app.activeModule === mid }"
        @click="onSubModule(mid)"
      >{{ MODULE_LABELS[mid] || mid }}</button>
    </div>
    <!-- 管理工具页提示 -->
    <div class="subtabs" v-else>
      <button class="subtab back" @click="app.backToWizard()">← 返回教学流程</button>
      <span class="admin-label">
        {{ app.adminTools.find(t => t.id === app.activeAdmin)?.icon }}
        {{ app.adminTools.find(t => t.id === app.activeAdmin)?.label }}
      </span>
    </div>

    <!-- 提交本步（教学闸口） -->
    <button
      v-if="app.activeAdmin === null"
      class="submit-step-btn"
      :class="{ submitted: app.stepSubmitted[app.activeStep] }"
      @click="onSubmitStep"
    >{{ app.stepSubmitted[app.activeStep] ? '✓ 已提交' : '提交本步' }}</button>

    <!-- ─── 管理工具（图标化）─── -->
    <div class="admintools">
      <button
        v-for="t in app.adminTools"
        :key="t.id"
        class="nav-icon-btn"
        :class="{ active: app.activeAdmin === t.id }"
        :title="t.label"
        @click="app.openAdmin(t.id)"
      >{{ t.icon }}</button>
    </div>

    <!-- 主题切换 -->
    <button
      class="nav-icon-btn theme-btn"
      :title="isDay ? '切换夜间模式' : '切换白天模式'"
      @click="$emit('toggle-theme')"
    >
      <el-icon :size="15"><Sunny v-if="!isDay" /><Moon v-else /></el-icon>
    </button>
  </div>
</template>

<style scoped>
.stepnav {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  background: var(--navy2);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 100;
  position: relative;
}

/* ─── 通用小图标按钮（返回 / 管理工具 / 主题）─── */
.nav-icon-btn {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 7px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text3);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-icon-btn:hover {
  color: var(--text2);
  border-color: var(--border2);
  background: rgba(255, 255, 255, 0.04);
}

.nav-icon-btn.active {
  color: var(--amber);
  border-color: rgba(255, 179, 0, 0.4);
  background: rgba(255, 179, 0, 0.08);
}

.theme-btn:hover {
  color: var(--teal);
  border-color: var(--teal);
}

/* ─── 步骤条 ─── */
.steps {
  display: flex;
  align-items: center;
  gap: 0;
}

.step {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.step:hover { background: rgba(255, 255, 255, 0.04); }

.step.current {
  border-color: rgba(0, 229, 255, 0.3);
  background: rgba(0, 229, 255, 0.07);
}

.step-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--border2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-size: 12px;
  color: var(--text3);
  flex-shrink: 0;
  transition: all 0.3s;
}

.step.current .step-circle {
  border-color: var(--teal);
  color: var(--teal);
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.35);
}

.step.done .step-circle {
  border-color: var(--green);
  background: rgba(0, 230, 118, 0.12);
}

.step-check {
  color: var(--green);
  font-size: 13px;
  font-weight: 700;
}

.step-num { color: var(--text3); }
.step.current .step-num { color: var(--teal); }

.step-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text2);
  white-space: nowrap;
}
.step.current .step-title { color: var(--teal); }
.step.done .step-title { color: var(--text); }

.step-link {
  width: 22px;
  height: 2px;
  background: var(--border2);
  flex-shrink: 0;
  border-radius: 1px;
}

.step-link.lit {
  background: linear-gradient(90deg, var(--green), var(--border2));
}

.bar-spacer { flex: 1; }

/* ─── 子模块 tabs ─── */
.subtabs {
  display: flex;
  gap: 6px;
  align-items: center;
  overflow-x: auto;
  scrollbar-width: none;
  min-width: 0;
}
.subtabs::-webkit-scrollbar { display: none; }

.subtab {
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid var(--border2);
  background: transparent;
  color: var(--text2);
  font-size: 12px;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.subtab:hover { border-color: var(--teal); color: var(--teal); }

.subtab.active {
  background: rgba(0, 229, 255, 0.12);
  border-color: var(--teal);
  color: var(--teal);
  font-weight: 600;
}

.subtab.back { border-style: dashed; }

.admin-label {
  font-size: 12px;
  color: var(--amber);
  font-weight: 600;
  padding: 0 6px;
  white-space: nowrap;
}

/* ─── 提交本步 ─── */
.submit-step-btn {
  flex-shrink: 0;
  padding: 5px 14px;
  border-radius: 7px;
  border: 1px solid var(--teal);
  background: rgba(0, 229, 255, 0.14);
  color: var(--teal);
  font-size: 12px;
  font-weight: 700;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.submit-step-btn:hover {
  background: rgba(0, 229, 255, 0.24);
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);
}
.submit-step-btn.submitted {
  border-color: var(--green);
  background: rgba(0, 230, 118, 0.1);
  color: var(--green);
}

/* ─── 管理工具组 ─── */
.admintools {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

/* ─── 窄屏降级 ─── */
@media (max-width: 1366px) {
  .step-title { display: none; }
  .step { padding: 4px 6px; }
}

@media (max-width: 1280px) {
  .step-link { width: 12px; }
  .submit-step-btn { padding: 5px 10px; }
}
</style>
