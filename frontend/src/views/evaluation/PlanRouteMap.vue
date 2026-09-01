<template>
  <div ref="mapEl" class="plan-route-map"></div>
</template>

<script setup>
/**
 * 轻量航线图：渲染课前方案的 GeoJSON 航线（课中环节一投影展示用）
 * 与路径规划智能体的 MapView 独立，仅做只读展示
 */
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  geojson: { type: Object, default: null },
})

const mapEl = ref(null)
let map = null
let routeGroup = null

const TRIP_COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#a855f7', '#ef4444', '#06b6d4']

function getColor(tripIndex) {
  return TRIP_COLORS[tripIndex % TRIP_COLORS.length]
}

function render() {
  if (!map || !routeGroup) return
  routeGroup.clearLayers()

  const geo = props.geojson
  if (!geo || !geo.features) return

  const bounds = L.latLngBounds()
  for (const feat of geo.features) {
    if (feat.geometry?.type !== 'LineString') continue
    const p = feat.properties || {}
    const coords = feat.geometry.coordinates.map(c => [c[1], c[0]])
    const line = L.polyline(coords, {
      color: p.delivery_mode === 'direct' ? '#f43f5e' : getColor(p.trip_index || 0),
      weight: 4,
      opacity: 0.85,
    })
    line.bindPopup(
      `<b>第${(p.trip_index || 0) + 1}趟 - ${p.uav_name || '无人机'}</b><br>` +
      `距离: ${p.distance?.toFixed?.(1) ?? '-'} km<br>` +
      `载重: ${p.load?.toFixed?.(1) ?? '-'} kg`
    )
    routeGroup.addLayer(line)
    bounds.extend(line.getBounds())
  }

  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [40, 40] })
  }
}

onMounted(() => {
  nextTick(() => {
    if (!mapEl.value) return
    map = L.map(mapEl.value, {
      zoomControl: true,
      attributionControl: false,
    }).setView([23.31, 106.32], 11)

    L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
      subdomains: ['1', '2', '3', '4'],
      attribution: '&copy; 高德地图',
      className: 'dark-tiles',
    }).addTo(map)

    routeGroup = L.layerGroup().addTo(map)
    render()
  })
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(() => props.geojson, () => render(), { deep: false })
</script>

<style scoped>
.plan-route-map {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: 10px;
  overflow: hidden;
  background: #0b1120;
}
</style>

<style>
/* 高德瓦片暗色滤镜（与平台其他地图一致） */
.dark-tiles {
  filter: invert(1) hue-rotate(180deg) brightness(0.9) contrast(0.9);
}
</style>
