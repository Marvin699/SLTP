<script setup>
import { ref, computed } from 'vue'
import { usePointsStore } from '../stores/points'

const store = usePointsStore()

const inputText = ref('')
const inputError = ref('')

async function handleParse() {
  inputError.value = ''
  const parsed = store.parseInputText(inputText.value)
  if (parsed.length === 0) {
    inputError.value = '未解析到有效坐标，请检查格式（每行: 村名 经度 纬度）'
    return
  }
  try {
    await store.submitBatch(parsed)
  } catch (e) {
    inputError.value = '提交失败: ' + (e.message || '未知错误')
  }
}

async function handleLoadDefault() {
  inputError.value = ''
  inputText.value = ''
  try {
    await store.loadDefaultCase()
  } catch (e) {
    inputError.value = '加载失败: ' + (e.message || '未知错误')
  }
}

async function handleGenMatrix() {
  try {
    await store.loadDistanceMatrix()
  } catch (e) {
    alert('生成距离矩阵失败: ' + (store.error || e.message))
  }
}

async function handleExport() {
  try {
    await store.saveGeoJSON()
  } catch (e) {
    alert('导出失败')
  }
}

function handleDeleteDemand(idx) {
  const pt = store.demands[idx]
  if (pt && pt.id) {
    store.removePoint(pt.id)
  }
}
</script>

<template>
  <div class="panel-root">
    <!-- 头部 -->
    <div class="panel-header">
      <div class="panel-logo">
        <span class="logo-icon">◈</span>
        <span class="logo-text">低空应急智能体</span>
      </div>
      <span class="panel-badge">M1</span>
    </div>

    <!-- 标签栏 -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ active: store.currentTab === 'input' }"
        @click="store.setTab('input')"
      >
        输入坐标
      </button>
      <button
        class="tab-btn"
        :class="{ active: store.currentTab === 'matrix' }"
        @click="store.setTab('matrix')"
      >
        距离矩阵
      </button>
    </div>

    <!-- 页面1：输入坐标 -->
    <div
      v-show="store.currentTab === 'input'"
      class="panel-body"
    >
      <!-- 批量输入 -->
      <div class="section-title">
        批量获取村庄坐标
      </div>
      <textarea
        v-model="inputText"
        class="input-area"
        placeholder="请输入应急需求点 (每行格式: 村名 经度 纬度)
例如:
渠洋村 106.33 23.35
塘麻村 106.45 23.08"
        rows="6"
      ></textarea>

      <div
        v-if="inputError"
        class="error-msg"
      >
        {{ inputError }}
      </div>

      <div class="btn-row">
        <button
          class="btn btn-primary"
          @click="handleParse"
        >
          解析并标注
        </button>
        <button
          class="btn btn-secondary"
          @click="handleLoadDefault"
        >
          加载默认案例
        </button>
      </div>

      <!-- 配送中心坐标 -->
      <div class="info-card">
        <div class="info-label">
          配送中心 (C)
        </div>
        <div
          v-if="store.center"
          class="info-value"
        >
          经度: {{ store.center.longitude.toFixed(4) }}，纬度: {{ store.center.latitude.toFixed(4) }}
        </div>
        <div
          v-else
          class="info-value empty"
        >
          未设置
        </div>
      </div>

      <!-- 需求点列表 -->
      <div class="section-title">
        需求点列表
      </div>
      <div class="demand-list">
        <div
          v-if="store.demands.length === 0"
          class="empty-hint"
        >
          暂无需求点，请输入坐标或加载默认案例
        </div>
        <div
          v-for="(d, i) in store.demands"
          :key="d.id || i"
          class="demand-item"
        >
          <span class="demand-idx">{{ i + 1 }}</span>
          <span class="demand-name">{{ d.name }}</span>
          <button
            class="demand-del"
            @click="handleDeleteDemand(i)"
          >
            ×
          </button>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="btn-row">
        <button
          class="btn btn-primary"
          :disabled="store.points.length < 2"
          @click="handleGenMatrix"
        >
          生成距离矩阵
        </button>
        <button
          class="btn btn-secondary"
          :disabled="store.points.length === 0"
          @click="handleExport"
        >
          导出 GeoJSON
        </button>
      </div>
    </div>

    <!-- 页面2：距离矩阵 -->
    <div
      v-show="store.currentTab === 'matrix'"
      class="panel-body"
    >
      <div class="section-title">
        需求点列表
      </div>

      <div
        v-if="store.distMatrix.length === 0"
        class="empty-hint"
      >
        请先在"输入坐标"页面生成距离矩阵
      </div>

      <div
        v-else
        class="matrix-wrap"
      >
        <div class="matrix-scroll">
          <table class="matrix-table">
            <thead>
              <tr>
                <th
                  class="corner-cell"
                  colspan="2"
                ></th>
                <th
                  v-for="label in store.distLabels"
                  :key="label"
                  class="col-header"
                >
                  {{ label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, i) in store.distMatrix"
                :key="i"
              >
                <td class="row-header">
                  {{ store.distLabels[i] }}
                </td>
                <td class="return-cell">
                  {{ store.distReturn[i].toFixed(2) }}
                </td>
                <td
                  v-for="(val, j) in row"
                  :key="j"
                  :class="{ diag: i === j }"
                  class="dist-cell"
                >
                  {{ i === j ? '0' : val.toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-root {
  position: absolute;
  top: 16px;
  left: 16px;
  bottom: 16px;
  width: 420px;
  background: rgba(11, 22, 40, 0.92);
  backdrop-filter: blur(24px);
  border: 1px solid var(--border2);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5), 0 0 1px rgba(0, 229, 255, 0.2);
}

/* Header */
.panel-header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.panel-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 18px;
  color: var(--teal);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.logo-text {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--teal);
  letter-spacing: 1px;
}

.panel-badge {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--teal);
  border: 1px solid rgba(0, 229, 255, 0.3);
  padding: 2px 8px;
  border-radius: 3px;
  letter-spacing: 1px;
}

/* Tabs */
.tab-bar {
  display: flex;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text3);
  font-family: var(--sans);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text2);
}

.tab-btn.active {
  color: var(--teal);
  border-bottom-color: var(--teal);
  background: rgba(0, 229, 255, 0.04);
}

/* Body */
.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
}

/* Section title */
.section-title {
  font-family: var(--sans);
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

/* Textarea */
.input-area {
  width: 100%;
  background: var(--navy);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  padding: 10px 12px;
  font-size: 12px;
  font-family: var(--mono);
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.input-area:focus {
  border-color: var(--teal);
}

.input-area::placeholder {
  color: var(--text3);
  font-family: var(--sans);
}

/* Error */
.error-msg {
  padding: 8px 10px;
  background: rgba(255, 61, 87, 0.08);
  border: 1px solid rgba(255, 61, 87, 0.25);
  border-radius: 6px;
  font-size: 11px;
  color: var(--red);
  margin-bottom: 8px;
}

/* Buttons */
.btn-row {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.btn {
  flex: 1;
  padding: 9px 12px;
  border-radius: 7px;
  font-size: 12px;
  font-family: var(--sans);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--teal), var(--teal2));
  color: #000;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: var(--glow-teal);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--navy);
  color: var(--text2);
  border: 1px solid var(--border2);
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--text3);
  color: var(--text);
}

/* Info card */
.info-card {
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 14px;
}

.info-label {
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.info-value {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--teal);
}

.info-value.empty {
  color: var(--text3);
}

/* Demand list */
.demand-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
}

.empty-hint {
  padding: 20px;
  text-align: center;
  font-size: 11px;
  color: var(--text3);
}

.demand-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-bottom: 1px solid rgba(22, 37, 64, 0.5);
  font-size: 12px;
  color: var(--text2);
}

.demand-item:last-child {
  border-bottom: none;
}

.demand-idx {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--teal);
  color: #000;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: var(--mono);
}

.demand-name {
  flex: 1;
}

.demand-del {
  background: none;
  border: none;
  color: var(--text3);
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.demand-del:hover {
  color: var(--red);
}

/* Matrix */
.matrix-wrap {
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid var(--border);
}

.matrix-scroll {
  overflow: auto;
  max-height: calc(100vh - 180px);
}

.matrix-table {
  border-collapse: collapse;
  font-size: 10px;
  font-family: var(--mono);
  white-space: nowrap;
}

.matrix-table th,
.matrix-table td {
  padding: 5px 8px;
  border: 1px solid var(--border);
  text-align: center;
}

.corner-cell {
  background: var(--navy);
  position: sticky;
  top: 0;
  z-index: 2;
}

.col-header {
  background: var(--navy3);
  color: var(--teal);
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 2;
  font-size: 9px;
}

.row-header {
  background: var(--navy3);
  color: var(--teal);
  font-weight: 600;
  text-align: left !important;
  position: sticky;
  left: 0;
  z-index: 1;
  font-size: 9px;
}

.return-cell {
  background: var(--navy);
  color: var(--amber);
  font-weight: 600;
  position: sticky;
  left: 80px;
  z-index: 1;
}

.dist-cell {
  color: var(--text2);
}

.dist-cell.diag {
  color: var(--text3);
  background: rgba(6, 13, 26, 0.5);
}
</style>
