<script setup>
import { usePointsStore } from '@/stores/pathPlanning/points'

defineEmits(['close'])
const store = usePointsStore()

function exportCSV() {
  const BOM = '\uFEFF'
  const header = ['', '回程距离', ...store.distLabels]
  const rows = store.distMatrix.map((row, i) => [
    store.distLabels[i],
    store.distReturn[i].toFixed(2),
    ...row.map((val, j) => (i === j ? '0' : val.toFixed(2))),
  ])
  const csv = BOM + [header, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `距离矩阵_${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <Teleport to="body">
    <div
      class="overlay"
      @click.self="$emit('close')"
    >
      <div class="modal">
        <div class="modal-header">
          <h3>距离矩阵（km）</h3>
          <div class="header-actions">
            <button
              class="export-btn"
              @click="exportCSV"
            >
              导出 Excel
            </button>
            <button
              class="close-btn"
              @click="$emit('close')"
            >
              ✕
            </button>
          </div>
        </div>
        <div class="modal-body">
          <div
            v-if="store.distMatrix.length === 0"
            class="empty"
          >
            暂无数据
          </div>
          <div
            v-else
            class="matrix-scroll"
          >
            <table class="matrix-table">
              <thead>
                <tr>
                  <th class="corner"></th>
                  <th class="return-header">
                    回程距离
                  </th>
                  <th
                    v-for="label in store.distLabels"
                    :key="label"
                    class="col-h"
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
                  <td class="row-h">
                    {{ store.distLabels[i] }}
                  </td>
                  <td class="return-cell">
                    {{ store.distReturn[i].toFixed(2) }}
                  </td>
                  <td
                    v-for="(val, j) in row"
                    :key="j"
                    class="dist-cell"
                    :class="{ diag: i === j }"
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
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 13, 26, 0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: var(--navy2);
  border: 1px solid var(--border2);
  border-radius: 14px;
  width: 90vw;
  max-width: 1100px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.close-btn {
  background: none;
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--text3);
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  border-color: var(--red);
  color: var(--red);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn {
  background: rgba(0, 229, 255, 0.1);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: 5px;
  color: var(--teal);
  padding: 4px 10px;
  font-size: 11px;
  cursor: pointer;
  font-family: var(--sans);
}

.export-btn:hover {
  background: rgba(0, 229, 255, 0.2);
}

.modal-body {
  padding: 14px 18px;
  overflow: auto;
  flex: 1;
}

.empty {
  padding: 40px;
  text-align: center;
  color: var(--text3);
  font-size: 12px;
}

.matrix-scroll {
  overflow: auto;
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

.corner {
  background: var(--navy);
}

.return-header {
  background: var(--navy3);
  color: var(--amber);
  font-weight: 600;
  font-size: 9px;
}

.col-h {
  background: var(--navy3);
  color: var(--teal);
  font-weight: 600;
  font-size: 9px;
}

.row-h {
  background: var(--navy3);
  color: var(--teal);
  font-weight: 600;
  text-align: left !important;
  font-size: 9px;
}

.return-cell {
  background: rgba(255, 179, 0, 0.06);
  color: var(--amber);
  font-weight: 600;
}

.dist-cell {
  color: var(--text2);
}

.dist-cell.diag {
  color: var(--text3);
  background: rgba(6, 13, 26, 0.4);
}
</style>
