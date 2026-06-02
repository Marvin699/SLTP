<script setup>
import { onMounted, onUnmounted, watch, ref, nextTick, defineProps } from 'vue'
import L from 'leaflet'
import { usePointsStore } from '@/stores/pathPlanning/points'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'

const props = defineProps({
  selectedTripIndex: {
    type: Number,
    default: -1
  },
  selectedDroneId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['tripClick'])

const store = usePointsStore()
const optStore = useOptimizerStore()
const mapContainer = ref(null)
let map = null
let markersGroup = null
let linesGroup = null
let routeGroup = null
let labelGroup = null
let tileLayer = null

// 日夜模式切换
const isNight = ref(true)
function toggleMapMode() {
  isNight.value = !isNight.value
  if (tileLayer) {
    const el = tileLayer.getContainer()
    if (el) {
      el.classList.remove('dark-tiles', 'day-tiles')
      el.classList.add(isNight.value ? 'dark-tiles' : 'day-tiles')
    }
  }
}

// 路线颜色配置 - 多种颜色用于区分不同趟次，避免交叉混淆
const DIRECT_FLIGHT_COLOR = '#ff3d57'  // 必须直飞：红色

// 联飞航次颜色调色板 - 8种高对比度颜色
const ROUTE_COLORS = [
  '#2196f3', // 蓝
  '#4caf50', // 绿
  '#ff9800', // 橙
  '#9c27b0', // 紫
  '#00bcd4', // 青
  '#e91e63', // 粉
  '#795548', // 棕
  '#607d8b', // 灰
]

const DEFAULT_CENTER = [23.25, 106.35]
const DEFAULT_ZOOM = 11

function getRouteColor(tripIndex) {
  // 使用索引取模，循环使用颜色
  return ROUTE_COLORS[tripIndex % ROUTE_COLORS.length]
}

function createIcon(type, label, size) {
  if (type === 'center') {
    return L.divIcon({
      html: `<div style="
        width:${size}px;height:${size}px;border-radius:50%;
        background:rgba(255,107,53,0.15);border:2.5px solid #ff6b35;
        display:flex;align-items:center;justify-content:center;
        font-size:13px;font-weight:900;color:#ff6b35;
        box-shadow:0 0 16px rgba(255,107,53,0.3);
        font-family:'JetBrains Mono',monospace;
      ">C</div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
      popupAnchor: [0, -size / 2 - 6],
      className: '',
    })
  }
  return L.divIcon({
    html: `<div style="
      width:${size}px;height:${size}px;border-radius:50%;
      background:rgba(0,229,255,0.2);border:2px solid #00e5ff;
      display:flex;align-items:center;justify-content:center;
      font-size:9px;font-weight:700;color:#00e5ff;
      box-shadow:0 0 10px rgba(0,229,255,0.25);
      font-family:'JetBrains Mono',monospace;
    ">${label}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2 - 6],
    className: '',
  })
}

function renderMarkers() {
  if (!map || !markersGroup || !linesGroup) return
  markersGroup.clearLayers()
  linesGroup.clearLayers()

  const allPoints = store.points
  if (allPoints.length === 0) return

  const centerPt = store.center
  const demandPts = store.demands

  if (centerPt) {
    const marker = L.marker([centerPt.latitude, centerPt.longitude], {
      icon: createIcon('center', 'C', 36),
    })
      .bindPopup(`<b>配送中心</b><br>${centerPt.name}<br>${centerPt.longitude.toFixed(4)}, ${centerPt.latitude.toFixed(4)}`)
    markersGroup.addLayer(marker)
  }

  demandPts.forEach((pt, i) => {
    const marker = L.marker([pt.latitude, pt.longitude], {
      icon: createIcon('demand', String(i + 1), 22),
    })
      .bindPopup(`<b>需求点${i + 1}</b><br>${pt.name}<br>${pt.longitude.toFixed(4)}, ${pt.latitude.toFixed(4)}`)
    markersGroup.addLayer(marker)

    if (centerPt) {
      const line = L.polyline(
        [[centerPt.latitude, centerPt.longitude], [pt.latitude, pt.longitude]],
        { color: '#00b8d4', weight: 1.5, opacity: 0.55, dashArray: '6 4' }
      )
      linesGroup.addLayer(line)
    }
  })

  const allLatLngs = allPoints.map((p) => [p.latitude, p.longitude])
  if (allLatLngs.length === 1) {
    map.setView(allLatLngs[0], 13)
  } else {
    map.fitBounds(allLatLngs, { padding: [40, 40] })
  }
}

function renderRoutes() {
  if (!map || !routeGroup || !labelGroup) return
  routeGroup.clearLayers()
  labelGroup.clearLayers()

  const geo = optStore.geojson
  if (!geo || !geo.features) return

  // 获取组件的props（selectedDroneId）
  const selectedDroneId = props.selectedDroneId

  for (const feat of geo.features) {
    if (feat.geometry.type === 'LineString') {
      const coords = feat.geometry.coordinates.map(c => [c[1], c[0]])
      const featProps = feat.properties || {}
      const tripIndex = featProps.trip_index || 0
      const uavId = featProps.uav_id || ''
      
      // 确定颜色和样式
      let color
      let weight = 4
      let opacity = 0.85
      let showLabel = true
      
      // 检查是否按无人机筛选
      const isFilteredByDrone = selectedDroneId !== null && selectedDroneId !== undefined
      const isSelectedDrone = uavId === selectedDroneId
      
      if (isFilteredByDrone) {
        if (isSelectedDrone) {
          // 选中的无人机路线高亮显示
          if (featProps.delivery_mode === 'direct') {
            color = DIRECT_FLIGHT_COLOR
          } else {
            color = getRouteColor(tripIndex)
          }
          opacity = 0.95
          weight = 5
        } else {
          // 其他无人机路线变灰
          color = '#666666'
          opacity = 0.15
          weight = 2
          showLabel = false
        }
      } else {
        // 正常显示
        if (featProps.delivery_mode === 'direct') {
          color = DIRECT_FLIGHT_COLOR
        } else {
          color = getRouteColor(tripIndex)
        }
        
        // 如果有选中的航次，降低其他航次的透明度
        if (featProps.selected) {
          opacity = 0.95
          weight = 5
        } else if (featProps.selected === false) {
          opacity = 0.25
        }
      }
      
      // 创建路线
      const lineOptions = {
        color,
        weight,
        opacity,
      }
      
      const line = L.polyline(coords, lineOptions)
      
      // 绑定弹出信息
      const modeText = featProps.delivery_mode === 'direct' ? '必须直飞' : '联飞'
      const loadText = featProps.points_served ? `服务点数: ${featProps.points_served}` : ''
      const tripLabel = `第${tripIndex + 1}趟`
      line.bindPopup(`
        <b>${tripLabel} - ${featProps.uav_name || '无人机'}</b><br>
        距离: ${featProps.distance?.toFixed(1) || '-'} km<br>
        模式: ${modeText}<br>
        载重: ${featProps.load?.toFixed(1) || '-'} kg<br>
        ${loadText}
      `)
      
      // 点击事件
      line.on('click', (e) => {
        L.DomEvent.stopPropagation(e)
        emit('tripClick', tripIndex)
      })
      
      routeGroup.addLayer(line)
    }
  }

  // 如果有路线，调整视图
  const routeLayers = routeGroup.getLayers()
  if (routeLayers.length > 0) {
    const bounds = L.latLngBounds()
    routeLayers.forEach(layer => {
      if (layer.getBounds) {
        bounds.extend(layer.getBounds())
      } else if (layer.getLatLng) {
        bounds.extend(layer.getLatLng())
      }
    })
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] })
    }
  }
}

onMounted(() => {
  nextTick(() => {
    if (!mapContainer.value) return

    map = L.map(mapContainer.value, {
      zoomControl: true,
      attributionControl: false,
    }).setView(DEFAULT_CENTER, DEFAULT_ZOOM)

    tileLayer = L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
      subdomains: ['1', '2', '3', '4'],
      attribution: '&copy; 高德地图',
      className: 'dark-tiles',
    }).addTo(map)

    markersGroup = L.layerGroup().addTo(map)
    linesGroup = L.layerGroup().addTo(map)
    routeGroup = L.layerGroup().addTo(map)
    labelGroup = L.layerGroup().addTo(map)

    // 地图点击事件
    map.on('click', (e) => {
      if (store.clickMode) {
        store.handleMapClick(e.latlng.lat, e.latlng.lng)
      }
    })

    map.invalidateSize()
    setTimeout(() => { if (map) map.invalidateSize() }, 300)

    watch(
      () => store.points,
      () => { nextTick(renderMarkers) },
      { deep: true, immediate: true }
    )

    // 监听优化结果的 GeoJSON
    watch(
      () => optStore.geojson,
      () => { nextTick(renderRoutes) },
      { deep: true }
    )

    // 监听选中的无人机ID变化，重新渲染路线
    watch(
      () => props.selectedDroneId,
      () => { nextTick(renderRoutes) },
      { immediate: false }
    )
  })
})

function onKeydown(e) {
  if (e.key === 'Escape' && store.clickMode) {
    store.setClickMode(null)
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (map) { map.remove(); map = null }
})
</script>

<template>
  <div
    class="map-wrapper"
    :class="{ 'crosshair-cursor': store.clickMode }"
  >
    <div
      ref="mapContainer"
      class="map-root"
    ></div>
    <div
      v-if="store.clickMode"
      class="click-hint"
    >
      点击地图选取{{ store.clickMode === 'center' ? '配送中心' : '需求点' }}位置（按 Esc 取消）
    </div>
    
    <!-- 日夜模式切换 -->
    <button class="map-mode-toggle" @click="toggleMapMode" :title="isNight ? '切换到日间模式' : '切换到夜间模式'">
      {{ isNight ? '☀️' : '🌙' }}
    </button>

    <!-- 图例 - 位置调整到左下，避免遮挡右侧面板 -->
    <div class="map-legend">
      <div class="legend-title">路线图例</div>
      <div class="legend-item">
        <span class="legend-line direct"></span>
        <span class="legend-text">必须直飞</span>
      </div>
      <div class="legend-item">
        <span class="legend-line multi-color"></span>
        <span class="legend-text">联飞航次（多种颜色区分）</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-wrapper {
  flex: 1;
  position: relative;
  width: 100%;
  height: 100%;
}

.map-root {
  width: 100%;
  height: 100%;
}

.map-mode-toggle {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 400;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(0, 229, 255, 0.3);
  background: rgba(13, 17, 23, 0.85);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  padding: 0;
}
.map-mode-toggle:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: rgba(0, 229, 255, 0.6);
}

.crosshair-cursor {
  cursor: crosshair !important;
}

.click-hint {
  position: absolute;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.4);
  color: #00e5ff;
  font-size: 12px;
  padding: 6px 14px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  z-index: 1000;
  pointer-events: none;
  white-space: nowrap;
}

.map-legend {
  position: absolute;
  bottom: 12px;  /* 右下角 */
  right: 12px;
  background: rgba(13, 17, 23, 0.95);
  border: 1px solid rgba(0, 229, 255, 0.25);
  border-radius: 10px;
  padding: 14px;
  z-index: 400;  /* z-index 低于右侧面板(500) */
  backdrop-filter: blur(12px);
  min-width: 140px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.legend-title {
  font-size: 11px;
  font-weight: 700;
  color: #a8b1c2;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-line {
  width: 28px;
  height: 4px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-line.direct {
  background: #ff3d57;
  box-shadow: 0 0 8px rgba(255, 61, 87, 0.6);
}

.legend-line.multi-color {
  background: linear-gradient(90deg, #2196f3, #4caf50, #ff9800, #9c27b0);
}

.legend-text {
  font-size: 11px;
  color: #a8b1c2;
  line-height: 1.4;
}
</style>
