<script setup>
import { usePointsStore } from '../stores/points'

defineEmits(['close'])
const store = usePointsStore()

function exportCSV() {
  const BOM = '\uFEFF'
  const header = ['编号', '名称', '类型', '经度', '纬度']
  const rows = store.points.map((p, i) => [
    p.point_type === 'center' ? 'C' : i,
    p.name,
    p.point_type === 'center' ? '配送中心' : '需求点',
    p.longitude.toFixed(4),
    p.latitude.toFixed(4),
  ])
  const csv = BOM + [header, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `坐标信息表_${Date.now()}.csv`
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
          <h3>坐标信息表</h3>
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
          <table class="coord-table">
            <thead>
              <tr>
                <th>编号</th>
                <th>名称</th>
                <th>类型</th>
                <th>经度</th>
                <th>纬度</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(p, i) in store.points"
                :key="p.id"
                :class="{ 'is-center': p.point_type === 'center' }"
              >
                <td>{{ p.point_type === 'center' ? 'C' : i }}</td>
                <td>{{ p.name }}</td>
                <td>
                  <span
                    class="type-tag"
                    :class="p.point_type"
                  >
                    {{ p.point_type === 'center' ? '配送中心' : '需求点' }}
                  </span>
                </td>
                <td class="mono">{{ p.longitude.toFixed(4) }}</td>
                <td class="mono">{{ p.latitude.toFixed(4) }}</td>
              </tr>
            </tbody>
          </table>
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
  width: 520px;
  max-width: 90vw;
  max-height: 80vh;
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
  overflow-y: auto;
}

.coord-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.coord-table th {
  background: var(--navy);
  color: var(--text3);
  padding: 7px 10px;
  text-align: left;
  font-weight: 500;
  font-size: 10px;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border);
}

.coord-table td {
  padding: 7px 10px;
  border-bottom: 1px solid rgba(22, 37, 64, 0.5);
  color: var(--text2);
}

.coord-table tr.is-center td {
  color: #ff6b35;
}

.mono {
  font-family: var(--mono);
  font-size: 11px;
}

.type-tag {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.type-tag.center {
  background: rgba(255, 107, 53, 0.12);
  color: #ff6b35;
  border: 1px solid rgba(255, 107, 53, 0.3);
}

.type-tag.demand {
  background: rgba(0, 229, 255, 0.08);
  color: var(--teal);
  border: 1px solid rgba(0, 229, 255, 0.2);
}
</style>
