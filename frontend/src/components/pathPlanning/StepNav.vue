<script setup>
import { useAppStore } from '@/stores/pathPlanning/app'

const app = useAppStore()

const MODULE_LABELS = {
  1: '配送点', 2: '物资需求', 3: '无人机选型', 4: '路径规划',
  9: '航线详情', 5: '方案诊断', 13: '合规核验', 12: '反向质询', 6: '方案优出', 10: '方案审阅',
}

function onSubModule(id) {
  app.setModule(id)
}
</script>

<template>
  <div class="stepnav">
    <!-- ─── 四步向导 ─── -->
    <nav class="steps">
      <template v-for="(s, i) in app.wizardSteps" :key="s.id">
        <!-- 步骤节点 -->
        <div
          class="step"
          :class="{
            current: app.activeAdmin === null && app.activeStep === s.id,
            done: app.stepStatus[s.id],
          }"
          @click="app.gotoStep(s.id)"
        >
          <div class="step-circle">
            <span v-if="app.stepStatus[s.id]" class="step-check">✓</span>
            <span v-else class="step-num">{{ i + 1 }}</span>
          </div>
          <div class="step-text">
            <div class="step-title">{{ s.title }}</div>
            <div class="step-desc">{{ s.desc }}</div>
          </div>
        </div>
        <!-- 连接线 -->
        <div
          v-if="i < app.wizardSteps.length - 1"
          class="step-link"
          :class="{ lit: app.stepStatus[s.id] }"
        ></div>
      </template>
    </nav>

    <!-- ─── 当前步骤的子模块 + 管理工具 ─── -->
    <div class="subrow">
      <!-- 子模块 tab -->
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

      <!-- 管理工具按钮组 -->
      <div class="admintools">
        <button
          v-for="t in app.adminTools"
          :key="t.id"
          class="admintool-btn"
          :class="{ active: app.activeAdmin === t.id }"
          :title="t.label"
          @click="app.openAdmin(t.id)"
        >{{ t.icon }}<span class="at-label">{{ t.label }}</span></button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stepnav {
  background: var(--navy2);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 100;
  position: relative;
}

/* ─── 步骤条 ─── */
.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px 4px;
  gap: 0;
}

.step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 10px;
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
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid var(--border2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  font-size: 13px;
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
  font-size: 14px;
  font-weight: 700;
}

.step-num { color: var(--text3); }
.step.current .step-num { color: var(--teal); }

.step-text { text-align: left; }

.step-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text2);
  white-space: nowrap;
}
.step.current .step-title { color: var(--teal); }
.step.done .step-title { color: var(--text); }

.step-desc {
  font-size: 10px;
  color: var(--text3);
  white-space: nowrap;
  margin-top: 1px;
}

.step-link {
  width: 36px;
  height: 2px;
  background: var(--border2);
  flex-shrink: 0;
  border-radius: 1px;
}

.step-link.lit {
  background: linear-gradient(90deg, var(--green), var(--border2));
}

/* ─── 子模块行 ─── */
.subrow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 20px 10px;
  gap: 16px;
}

.subtabs {
  display: flex;
  gap: 6px;
  align-items: center;
}

.subtab {
  padding: 5px 14px;
  border-radius: 6px;
  border: 1px solid var(--border2);
  background: transparent;
  color: var(--text2);
  font-size: 12px;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
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
}

/* ─── 管理工具 ─── */
.admintools {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.admintool-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text3);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.admintool-btn:hover {
  color: var(--text2);
  border-color: var(--border2);
  background: rgba(255, 255, 255, 0.04);
}

.admintool-btn.active {
  color: var(--amber);
  border-color: rgba(255, 179, 0, 0.4);
  background: rgba(255, 179, 0, 0.08);
}

.at-label { font-size: 11px; }

/* 窄屏时隐藏工具文字只留图标 */
@media (max-width: 1280px) {
  .at-label { display: none; }
  .step-desc { display: none; }
}
</style>
