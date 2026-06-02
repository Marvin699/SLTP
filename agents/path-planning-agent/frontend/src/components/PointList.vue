<script setup>
import { usePointsStore } from '../stores/points'

const store = usePointsStore()

const supplyColors = {
  repair: '#ff6b35',
  life: '#00d4ff',
  medical: '#ff4757',
  cold: '#70a1ff',
  settle: '#7bed9f',
}

const supplyIcons = {
  repair: '🔧',
  life: '🍚',
  medical: '🏥',
  cold: '❄️',
  settle: '🏕',
}

function getSupplyColor(type) {
  return supplyColors[type] || '#00e5ff'
}

function getSupplyIcon(type) {
  return supplyIcons[type] || '◇'
}

async function handleDelete(pt) {
  if (!confirm(`确认删除 "${pt.name}" ？`)) return
  try {
    await store.removePoint(pt.id)
  } catch (e) {
    alert('删除失败')
  }
}
</script>

<template>
  <div class="point-list">
    <div
      v-if="store.points.length === 0"
      class="empty-hint"
    >
      暂无点位，请通过上方按钮添加
    </div>

    <div
      v-for="pt in store.points"
      :key="pt.id"
      class="point-card"
      :class="{ 'is-center': pt.point_type === 'center' }"
      @click="store.openEditor(pt)"
    >
      <div
        class="point-badge"
        :style="{
          background: pt.point_type === 'center' ? '#ff6b35' : getSupplyColor(pt.supply_type),
        }"
      >
        {{ pt.point_type === 'center' ? 'C' : store.demands.indexOf(pt) + 1 }}
      </div>

      <div class="point-info">
        <div class="point-name">
          {{ pt.name }}
        </div>
        <div class="point-meta">
          <span
            v-if="pt.point_type === 'center'"
            class="tag tag-amber"
          >配送中心</span>
          <span
            v-else
            class="tag tag-teal"
          >需求点</span>
          <span
            v-if="pt.supply_type"
            class="tag"
            :style="{
              background: getSupplyColor(pt.supply_type) + '18',
              color: getSupplyColor(pt.supply_type),
              borderColor: getSupplyColor(pt.supply_type) + '40',
            }"
          >{{ getSupplyIcon(pt.supply_type) }} {{ pt.supply_type }}</span>
        </div>
      </div>

      <button
        class="del-btn"
        title="删除"
        @click.stop="handleDelete(pt)"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<style scoped>
.point-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 240px;
  overflow-y: auto;
}

.empty-hint {
  padding: 20px;
  text-align: center;
  font-size: 11px;
  color: var(--text3);
  background: var(--navy);
  border: 1px dashed var(--border);
  border-radius: 8px;
}

.point-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--navy);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.point-card:hover {
  border-color: var(--border2);
  background: var(--navy3);
}

.point-card.is-center {
  border-left: 3px solid #ff6b35;
}

.point-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: #000;
  flex-shrink: 0;
  font-family: var(--mono);
}

.point-info {
  flex: 1;
  min-width: 0;
}

.point-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.point-meta {
  display: flex;
  gap: 4px;
  margin-top: 3px;
  flex-wrap: wrap;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.3px;
  border: 1px solid;
}

.tag-teal {
  background: rgba(0, 229, 255, 0.08);
  color: var(--teal);
  border-color: rgba(0, 229, 255, 0.2);
}

.tag-amber {
  background: rgba(255, 179, 0, 0.1);
  color: var(--amber);
  border-color: rgba(255, 179, 0, 0.25);
}

.del-btn {
  background: none;
  border: none;
  color: var(--text3);
  cursor: pointer;
  font-size: 14px;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.15s;
  flex-shrink: 0;
}

.del-btn:hover {
  color: var(--red);
  background: rgba(255, 61, 87, 0.1);
}
</style>
