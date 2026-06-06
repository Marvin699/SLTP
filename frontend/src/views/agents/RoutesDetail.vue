<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import { usePointsStore } from '@/stores/pathPlanning/points'
import { useMaterialsStore } from '@/stores/pathPlanning/materials'
import { useUavsStore } from '@/stores/pathPlanning/uavs'
import { useOptimizerStore } from '@/stores/pathPlanning/optimizer'

const props = defineProps({
  embedded: { type: Boolean, default: false },
  embeddedFull: { type: Boolean, default: false }
})
const router = useRouter()
const pointsStore = usePointsStore()
const matStore = useMaterialsStore()
const uavStore = useUavsStore()
const optStore = useOptimizerStore()

const stage = ref(1)
const isPanelOpen = ref(true)
const isNight = ref(true)
let map = null
let baseTileLayer = null
let routeLayer = null
let markerLayer = null
let floodLayer = null
let noFlyLayer = null

function toggleMapMode() {
  isNight.value = !isNight.value
  if (baseTileLayer) {
    const el = baseTileLayer.getContainer()
    if (el) {
      el.classList.remove('dark-tiles', 'day-tiles')
      el.classList.add(isNight.value ? 'dark-tiles' : 'day-tiles')
    }
  }
}

const stages = [
  { id: 1, title: '初始航线', subtitle: '蚁群算法自动输出' },
  { id: 2, title: '约束设置', subtitle: '设定应急配送规则' },
  { id: 3, title: '备选路径', subtitle: '智能体生成2条方案' },
  { id: 4, title: '人工优化', subtitle: '拖拽航点精细化调整' }
]

const constraint = ref({
  slope: 5,
  obstacleDist: 50,
  medicineTime: 10,
  battery: 30
})

const altRoutes = ref({
  A: { name: '方案A · 改降篮球场', color: '#f59e0b', extraDist: 2.8, risk: '低', timeAdd: 3, battery: 68 },
  B: { name: '方案B · 空中抛投', color: '#22c55e', extraDist: 0, risk: '中', timeAdd: 0, battery: 72 }
})

const fallbackCenter = { name: '渠洋村', longitude: 106.317264, latitude: 23.310533 }
const fallbackDemands = [
  { name: '怀渠村', longitude: 106.285000, latitude: 23.345000 },
  { name: '塘麻村', longitude: 106.425000, latitude: 23.085000 },
  { name: '坡乐村', longitude: 106.380000, latitude: 23.075000 },
  { name: '东风村', longitude: 106.320150, latitude: 23.309040 },
  { name: '古桥村', longitude: 106.350000, latitude: 23.200000 },
  { name: '新和村', longitude: 106.335000, latitude: 23.295000 },
  { name: '怀书村', longitude: 106.278670, latitude: 23.339030 },
  { name: '雅力村', longitude: 106.380000, latitude: 23.250000 },
]

const depotReal = computed(() => {
  if (pointsStore.center) return {
    name: pointsStore.center.name || '起飞点',
    lng: Number(pointsStore.center.longitude),
    lat: Number(pointsStore.center.latitude),
    type: 'start'
  }
  return { name: fallbackCenter.name, lng: fallbackCenter.longitude, lat: fallbackCenter.latitude, type: 'start' }
})

const demandsReal = computed(() => {
  const src = pointsStore.demands.length > 0 ? pointsStore.demands : fallbackDemands
  return src.map((p, i) => ({
    name: p.name || `需求点${i + 1}`,
    lng: Number(p.longitude),
    lat: Number(p.latitude),
    type: 'delivery',
    priority: matStore.assignments[p.id]?.priority || 3,
    materials: matStore.assignments[p.id]?.items || []
  }))
})

const totalPayload = computed(() => uavStore.totalPayload || 0)
const totalDistance = computed(() => optStore.totalDistance || 0)
const totalTime = computed(() => optStore.totalTime || 0)
const feasible = computed(() => optStore.feasible)

const routeTableReal = computed(() => optStore.routeTable || [])
const tripsReal = computed(() => optStore.routes || [])

const initialRoute = computed(() => {
  const pts = [depotReal.value, ...demandsReal.value]
  return pts.concat({ ...depotReal.value, name: '返航点', type: 'end' })
})

function offsetCoord(lng, lat, dLng, dLat) {
  return [lat + dLat, lng + dLng]
}

const routeA = computed(() => {
  const d = depotReal.value
  const dems = demandsReal.value.slice()
  if (dems.length >= 2) {
    dems[0] = { ...dems[0], lng: dems[0].lng - 0.005, name: dems[0].name + '(改降)' }
  }
  return [
    [d.lat, d.lng],
    ...dems.map(p => [p.lat, p.lng]),
    [d.lat + 0.005, d.lng - 0.012]
  ]
})

const routeB = computed(() => {
  const d = depotReal.value
  const dems = demandsReal.value.slice()
  if (dems.length >= 2) {
    dems[0] = { ...dems[0], lng: dems[0].lng + 0.008, name: dems[0].name + '(抛投)' }
  }
  return [
    [d.lat, d.lng],
    ...dems.map(p => [p.lat, p.lng]),
    [d.lat + 0.005, d.lng - 0.012]
  ]
})

const floodArea = computed(() => {
  const d = depotReal.value
  return [
    offsetCoord(d.lng, d.lat, 0.005, -0.003),
    offsetCoord(d.lng, d.lat, 0.015, -0.001),
    offsetCoord(d.lng, d.lat, 0.025, 0.003),
    offsetCoord(d.lng, d.lat, 0.020, 0.008),
    offsetCoord(d.lng, d.lat, 0.008, 0.006),
    offsetCoord(d.lng, d.lat, 0.003, 0.001),
  ]
})

const noFlyArea = computed(() => {
  const d = depotReal.value
  return [
    offsetCoord(d.lng, d.lat, -0.002, 0.008),
    offsetCoord(d.lng, d.lat, 0.006, 0.012),
    offsetCoord(d.lng, d.lat, 0.010, 0.018),
    offsetCoord(d.lng, d.lat, 0.002, 0.015),
  ]
})

const trees = computed(() => {
  const d = depotReal.value
  return [
    { lat: d.lat + 0.002, lng: d.lng + 0.008, name: '树木群' },
    { lat: d.lat + 0.008, lng: d.lng + 0.015, name: '电线杆' },
  ]
})

const optimizedRoute = computed(() => {
  const pts = [depotReal.value, ...demandsReal.value]
  if (pts.length >= 2) {
    pts[1] = { ...pts[1], lng: pts[1].lng + 0.006, name: pts[1].name + '(改降篮球场)' }
  }
  return pts.concat({ ...depotReal.value, lng: depotReal.value.lng + 0.005, name: '返航点', type: 'end' })
})

const draggingIdx = ref(-1)
const dragPoints = ref([])

function refreshDragPoints() {
  dragPoints.value = JSON.parse(JSON.stringify(optimizedRoute.value))
}

watch([() => depotReal.value, () => demandsReal.value], () => {
  if (stage.value === 4) refreshDragPoints()
}, { deep: true })

function initMap() {
  const el = document.getElementById('routes-detail-map')
  if (!el) return
  if (map) map.remove()

  const center = depotReal.value
  map = L.map(el, {
    center: [center.lat, center.lng],
    zoom: 13,
    zoomControl: true,
    attributionControl: false,
    scrollWheelZoom: true,
    dragging: true
  })

  baseTileLayer = L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    subdomains: ['1', '2', '3', '4'],
    className: 'dark-tiles',
  })
  baseTileLayer.addTo(map)

  floodLayer = L.layerGroup().addTo(map)
  noFlyLayer = L.layerGroup().addTo(map)
  routeLayer = L.layerGroup().addTo(map)
  markerLayer = L.layerGroup().addTo(map)

  updateMap()
  setTimeout(() => { if (map) map.invalidateSize({ animate: false }) }, 50)
  setTimeout(() => { if (map) map.invalidateSize({ animate: false }) }, 300)
}

function clearLayers() {
  floodLayer.clearLayers()
  noFlyLayer.clearLayers()
  routeLayer.clearLayers()
  markerLayer.clearLayers()
}

function drawFlood() {
  L.polygon(floodArea.value, {
    color: '#0ea5e9',
    weight: 0,
    fillColor: '#0ea5e9',
    fillOpacity: 0.25
  }).addTo(floodLayer)

  L.marker(floodArea.value[0], {
    icon: L.divIcon({
      className: 'zone-label',
      html: '<div style="background:rgba(14,165,233,0.85);color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">💧 洪水淹没区</div>',
      iconSize: [80, 22],
      iconAnchor: [40, 11]
    })
  }).addTo(floodLayer)
}

function drawNoFly() {
  L.polygon(noFlyArea.value, {
    color: '#ef4444',
    weight: 2,
    fillColor: '#ef4444',
    fillOpacity: 0.28,
    dashArray: '6,4'
  }).addTo(noFlyLayer)

  const c = noFlyArea.value[0]
  L.marker(c, {
    icon: L.divIcon({
      className: 'zone-label',
      html: '<div style="background:rgba(239,68,68,0.9);color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">🚫 禁飞区</div>',
      iconSize: [70, 22],
      iconAnchor: [35, 11]
    })
  }).addTo(noFlyLayer)
}

function drawTrees() {
  trees.value.forEach(t => {
    L.marker([t.lat, t.lng], {
      icon: L.divIcon({
        className: 'tree-marker',
        html: '<div style="font-size:22px;line-height:1;">🌳</div>',
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      })
    }).addTo(markerLayer)
  })
}

function drawRoute(points, color = '#facc15', dash = false, weight = 4) {
  const latlngs = points.map(p => Array.isArray(p) ? p : [p.lat, p.lng])
  if (latlngs.length < 2) return
  L.polyline(latlngs, {
    color,
    weight,
    opacity: 0.9,
    dashArray: dash ? '10,8' : null,
    lineCap: 'round'
  }).addTo(routeLayer)
}

function drawMarker(pt, idx, total, isDraggable = false, isGreen = false) {
  const colors = {
    start: '#22c55e',
    delivery: isGreen ? '#16a34a' : '#f59e0b',
    end: '#3b82f6'
  }
  const c = colors[pt.type] || '#f59e0b'
  const label = pt.type === 'start' ? '🛫' : pt.type === 'end' ? '🛬' : (idx + ' / ' + total)

  const el = document.createElement('div')
  el.innerHTML = `
    <div style="
      width:28px;height:28px;border-radius:50%;
      background:${c};border:3px solid #fff;
      box-shadow:0 2px 10px rgba(0,0,0,0.3);
      display:flex;align-items:center;justify-content:center;
      color:#fff;font-size:12px;font-weight:700;
      cursor:${isDraggable ? 'grab' : 'default'};
      transition:transform 0.15s;
    " title="${pt.name}">${label}</div>
    <div style="
      margin-top:4px;background:rgba(0,0,0,0.75);color:#fff;
      padding:2px 8px;border-radius:3px;font-size:11px;
      white-space:nowrap;text-align:center;
    ">${pt.name}</div>
  `

  const icon = L.divIcon({
    className: 'waypoint-marker',
    html: el,
    iconSize: [40, 52],
    iconAnchor: [20, 14]
  })

  const m = L.marker([pt.lat, pt.lng], { icon, draggable: isDraggable })
  m.bindTooltip(pt.name, { permanent: false, offset: [0, -20] })

  if (isDraggable) {
    m.on('dragstart', () => { draggingIdx.value = idx })
    m.on('drag', (e) => {
      const p = e.target.getLatLng()
      dragPoints.value[idx].lat = p.lat
      dragPoints.value[idx].lng = p.lng
      redrawOptimizedRoute()
    })
    m.on('dragend', () => { draggingIdx.value = -1; redrawOptimizedRoute() })
  }
  return m
}

function redrawOptimizedRoute() {
  routeLayer.clearLayers()
  markerLayer.clearLayers()
  drawFlood()
  drawNoFly()
  drawTrees()

  const pts = dragPoints.value
  if (pts.length >= 2) drawRoute(pts, '#22c55e', false, 5)
  pts.forEach((pt, i) => {
    drawMarker(pt, i, pts.length, true, true).addTo(markerLayer)
  })
}

function updateMap() {
  if (!map) return
  clearLayers()
  drawFlood()
  drawNoFly()
  drawTrees()

  const initPts = initialRoute.value

  if (stage.value === 1) {
    drawRoute(initPts, '#facc15', false, 4)
    initPts.forEach((pt, i) => { drawMarker(pt, i, initPts.length, false, false).addTo(markerLayer) })
  } else if (stage.value === 2) {
    drawRoute(initPts, '#facc15', true, 3)
    initPts.forEach((pt, i) => { drawMarker(pt, i, initPts.length, false, false).addTo(markerLayer) })
  } else if (stage.value === 3) {
    drawRoute(routeA.value, altRoutes.value.A.color, false, 4)
    drawRoute(routeB.value, altRoutes.value.B.color, '10,8', 3)
    const d = depotReal.value
    L.marker(routeA.value[1], {
      icon: L.divIcon({
        className: 'route-label',
        html: '<div style="background:#f59e0b;color:#fff;padding:3px 10px;border-radius:4px;font-size:12px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,0.3);">🅰 改降篮球场</div>',
        iconSize: [110, 26], iconAnchor: [55, 13]
      })
    }).addTo(markerLayer)
    L.marker(routeB.value[1], {
      icon: L.divIcon({
        className: 'route-label',
        html: '<div style="background:#22c55e;color:#fff;padding:3px 10px;border-radius:4px;font-size:12px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,0.3);">🅱 空中抛投</div>',
        iconSize: [100, 26], iconAnchor: [50, 13]
      })
    }).addTo(markerLayer)
    initPts.forEach((pt, i) => {
      const isDelivery = pt.type === 'delivery'
      const ic = L.divIcon({
        className: 'waypoint-marker',
        html: `<div style="width:24px;height:24px;border-radius:50%;background:${isDelivery ? '#f59e0b' : (pt.type === 'start' ? '#22c55e' : '#3b82f6')};border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:700;">${isDelivery ? '📍' : (pt.type === 'start' ? '🛫' : '🛬')}</div>`,
        iconSize: [30, 30], iconAnchor: [15, 15]
      })
      L.marker([pt.lat, pt.lng], { icon: ic }).addTo(markerLayer)
    })
  } else if (stage.value === 4) {
    drawRoute(initPts, '#facc15', true, 2)
    const opt = dragPoints.value
    if (opt.length >= 2) drawRoute(opt, '#22c55e', false, 5)
    opt.forEach((pt, i) => { drawMarker(pt, i, opt.length, true, true).addTo(markerLayer) })
    L.marker([opt.length >= 2 ? opt[1].lat : depotReal.value.lat, opt.length >= 2 ? opt[1].lng - 0.002 : depotReal.value.lng + 0.003], {
      icon: L.divIcon({
        className: 'optimize-tag',
        html: '<div style="background:#16a34a;color:#fff;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,0.25);">✓ 已调整配送顺序</div>',
        iconSize: [100, 22], iconAnchor: [50, 11]
      })
    }).addTo(markerLayer)
  }

  const center = depotReal.value
  map.setView([center.lat, center.lng], 13)
}

watch(stage, (v) => {
  nextTick(() => {
    if (v === 4) {
      refreshDragPoints()
    }
    updateMap()
    setTimeout(() => { if (map) map.invalidateSize({ animate: false }) }, 30)
    setTimeout(() => { if (map) map.invalidateSize({ animate: false }) }, 250)
  })
})

watch([() => depotReal.value, () => demandsReal.value], () => {
  nextTick(() => {
    updateMap()
  })
}, { deep: true })

watch(isPanelOpen, () => {
  nextTick(() => {
    setTimeout(() => { if (map) map.invalidateSize({ animate: false }) }, 30)
    setTimeout(() => { if (map) map.invalidateSize({ animate: false }) }, 250)
  })
})

onMounted(() => {
  refreshDragPoints()
  nextTick(() => {
    setTimeout(initMap, 150)
  })
})

onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
})

function selectStage(sid) {
  isPanelOpen.value = true
  stage.value = sid
}
function goHome() { router.push('/home') }
function gotoAgent() { router.push('/agent/path-planning') }
</script>

<template>
  <div class="routes-detail-page"
       :class="{
         'embedded': props.embedded,
         'embedded-full': props.embeddedFull
       }">
    <header v-if="!props.embedded && !props.embeddedFull" class="top-bar">
      <div class="tb-left">
        <el-button @click="goHome" text class="back-home">← 返回首页</el-button>
        <el-button @click="gotoAgent" text class="back-agent">← 路径规划</el-button>
        <div class="tb-title">
          <span class="tb-icon">🛰️</span>
          <div>
            <h1>航线详情</h1>
            <span class="tb-sub">应急物流无人机配送 · 全流程演示</span>
          </div>
        </div>
      </div>
      <div class="tb-right">
        <el-tag type="info" effect="dark">v1.0</el-tag>
      </div>
    </header>

    <div class="app-body">
      <aside class="left-nav">
        <div class="ln-title">
          <span class="ln-icon">🛰️</span>
          <div>
            <div class="ln-name">航线详情</div>
            <div class="ln-sub">全流程演示</div>
          </div>
        </div>

        <div class="ln-list">
          <div v-for="s in stages" :key="s.id"
               class="ln-item"
               :class="{ active: stage === s.id, done: stage > s.id }"
               @click="selectStage(s.id)">
            <div class="ln-num">
              <span v-if="stage > s.id">✓</span>
              <span v-else>{{ s.id }}</span>
            </div>
            <div class="ln-text">
              <div class="ln-title-line">{{ s.title }}</div>
              <div class="ln-sub-line">{{ s.subtitle }}</div>
            </div>
            <div class="ln-arrow">›</div>
          </div>
        </div>

        <div class="ln-footer">
          <div class="ln-foot-tip">起飞点: {{ depotReal.name }}<br/>需求点: {{ demandsReal.length }} 个</div>
        </div>
      </aside>

      <div class="right-content">
        <div class="main-row">
          <!-- 底层：绝对定位铺满的地图背景 -->
          <div class="map-bg-wrap">
            <div id="routes-detail-map" class="map-area"></div>
          </div>

          <!-- 顶部居中：当前步骤标题+图例 -->
          <div class="map-toolbar">
            <div class="mt-title">
              <span class="mt-icon">🗺️</span>
              <span v-if="stage === 1">蚁群算法 · 初始航线</span>
              <span v-else-if="stage === 2">约束设置</span>
              <span v-else-if="stage === 3">智能体备选路径</span>
              <span v-else>人工优化航线 · 拖拽调整</span>
            </div>
            <div class="mt-badges">
              <span class="badge badge-blue">洪水淹没区</span>
              <span class="badge badge-red">禁飞区</span>
              <span class="badge badge-yellow" v-if="stage <= 2 || stage === 4">初始航线</span>
              <span class="badge badge-green" v-if="stage >= 3">应急路径</span>
            </div>
          </div>

          <!-- 地图右上角日夜模式切换（与其他模块完全一致）-->
          <button class="map-mode-toggle" @click="toggleMapMode" :title="isNight ? '切换到日间模式' : '切换到夜间模式'">
            {{ isNight ? '☀️' : '🌙' }}
          </button>

          <div class="panel-col" v-if="isPanelOpen">
            <div class="panel-close-bar">
              <div class="pc-title">📋 航线详情步骤面板</div>
              <div class="pc-close" @click="isPanelOpen = false" title="关闭面板">✕</div>
            </div>
            <!-- Stage 1 -->
            <div v-if="stage === 1" class="stage-panel">
              <div class="panel-title">
                <span class="p-icon">📋</span>蚁群算法初始航线
              </div>
              <div class="route-preview">
                <div class="route-line-yellow"></div>
                <div class="route-label">蚁群算法初始航线（{{ depotReal.name }} 出发）</div>
              </div>
              <div class="info-grid">
                <div class="info-card">
                  <div class="info-label">起飞点</div>
                  <div class="info-value small">{{ depotReal.name }}</div>
                </div>
                <div class="info-card">
                  <div class="info-label">需求点数</div>
                  <div class="info-value">{{ demandsReal.length }} <small>个</small></div>
                </div>
                <div class="info-card">
                  <div class="info-label">无人机载重</div>
                  <div class="info-value">{{ totalPayload.toFixed(1) }} <small>kg</small></div>
                </div>
                <div class="info-card">
                  <div class="info-label">需求总量</div>
                  <div class="info-value">{{ matStore.totalWeight.toFixed(1) || 0 }} <small>kg</small></div>
                </div>
              </div>
              <div class="info-grid">
                <div class="info-card">
                  <div class="info-label">上次航程</div>
                  <div class="info-value">{{ totalDistance.toFixed(1) || '—' }} <small>km</small></div>
                </div>
                <div class="info-card">
                  <div class="info-label">上次耗时</div>
                  <div class="info-value">{{ totalTime.toFixed(0) || '—' }} <small>min</small></div>
                </div>
              </div>
              <div class="note-box">
                <div class="note-icon">💡</div>
                <div class="note-text">仅基于{{ demandsReal.length }}个需求点的最短距离优化，未叠加应急约束（坡度/障碍物/时效/禁飞区）</div>
              </div>
              <div class="panel-actions">
                <el-button type="primary" size="large" @click="stage = 2">下一步 → 设定约束</el-button>
              </div>
            </div>

            <!-- Stage 2 -->
            <div v-if="stage === 2" class="stage-panel">
              <div class="panel-title">
                <span class="p-icon">⚙️</span>应急配送约束设置
              </div>
              <div class="constraint-list">
                <div class="constraint-item">
                  <div class="constraint-head">
                    <span class="ci-icon">🛡️</span>
                    <span class="ci-title">安全约束</span>
                  </div>
                  <div class="ci-fields">
                    <label>降落坡度 ≤ <input type="number" v-model.number="constraint.slope" min="0" max="30"> <span>°</span></label>
                    <label>与障碍物距离 ≥ <input type="number" v-model.number="constraint.obstacleDist" min="10" max="200"> <span>m</span></label>
                  </div>
                </div>
                <div class="constraint-item">
                  <div class="constraint-head">
                    <span class="ci-icon">⏱️</span>
                    <span class="ci-title">时效约束</span>
                  </div>
                  <div class="ci-fields">
                    <label>药品送达时效 ≤ <input type="number" v-model.number="constraint.medicineTime" min="1" max="60"> <span>min</span></label>
                  </div>
                </div>
                <div class="constraint-item">
                  <div class="constraint-head">
                    <span class="ci-icon">🔋</span>
                    <span class="ci-title">续航约束</span>
                  </div>
                  <div class="ci-fields">
                    <label>最低剩余电量 ≥ <input type="number" v-model.number="constraint.battery" min="0" max="80"> <span>%</span></label>
                  </div>
                </div>
              </div>
              <div class="zone-info">
                <div class="zone-row"><span class="dot dot-blue"></span>洪水淹没区（浅蓝色）：不可降落，绕行</div>
                <div class="zone-row"><span class="dot dot-red"></span>山洪禁飞区（红色）：绝对不可穿越</div>
              </div>
              <div class="panel-actions">
                <el-button size="large" @click="stage = 1">← 上一步</el-button>
                <el-button type="primary" size="large" @click="stage = 3">🤖 生成应急路径</el-button>
              </div>
            </div>

            <!-- Stage 3 -->
            <div v-if="stage === 3" class="stage-panel">
              <div class="panel-title">
                <span class="p-icon">🤖</span>智能体已生成 2 条应急备选路径
              </div>
              <div class="compare-row">
                <div class="compare-card ca">
                  <div class="ca-head">
                    <span class="ca-badge" style="background:#f59e0b;">🅰</span>
                    <div>
                      <div class="ca-name">{{ altRoutes.A.name }}</div>
                      <div class="ca-sub">改降篮球场临时起降点</div>
                    </div>
                  </div>
                  <div class="ca-body">
                    <div class="ca-line"><span>额外航程</span><span class="plus">+{{ altRoutes.A.extraDist }} km</span></div>
                    <div class="ca-line"><span>预计时间</span><span>{{ (totalTime || 28) + altRoutes.A.timeAdd }} min</span></div>
                    <div class="ca-line"><span>风险指数</span><span class="risk-low">{{ altRoutes.A.risk }}</span></div>
                    <div class="ca-line"><span>电量消耗</span><span class="val">{{ altRoutes.A.battery }}%</span></div>
                  </div>
                </div>
                <div class="compare-card cb">
                  <div class="ca-head">
                    <span class="ca-badge" style="background:#22c55e;">🅱</span>
                    <div>
                      <div class="ca-name">{{ altRoutes.B.name }}</div>
                      <div class="ca-sub">不降落 · 空中精确抛投</div>
                    </div>
                  </div>
                  <div class="ca-body">
                    <div class="ca-line"><span>额外航程</span><span class="plus">+{{ altRoutes.B.extraDist }} km</span></div>
                    <div class="ca-line"><span>预计时间</span><span>{{ (totalTime || 28) + altRoutes.B.timeAdd }} min</span></div>
                    <div class="ca-line"><span>风险指数</span><span class="risk-mid">{{ altRoutes.B.risk }}</span></div>
                    <div class="ca-line"><span>电量消耗</span><span class="val">{{ altRoutes.B.battery }}%</span></div>
                  </div>
                </div>
              </div>
              <div class="opt-table-wrap" v-if="routeTableReal.length > 0">
                <div class="opt-table-title">📊 优化器当前路线（{{ routeTableReal.length }} 趟）</div>
                <div class="opt-table">
                  <div class="opt-table-head">
                    <span>趟</span><span>无人机</span><span>途经</span><span>距离</span><span>时间</span>
                  </div>
                  <div v-for="r in routeTableReal.slice(0, 6)" :key="r.route_id" class="opt-table-row">
                    <span class="rid">#{{ r.route_id }}</span>
                    <span class="rname">{{ r.drone_name }}</span>
                    <span class="rvia" :title="r.village_name">{{ r.village_name || '-' }}</span>
                    <span class="rdist">{{ r.distance }}km</span>
                    <span class="rtime">{{ r.time }}min</span>
                  </div>
                </div>
              </div>
              <div class="note-box">
                <div class="note-icon">💡</div>
                <div class="note-text">方案A安全优先；方案B时效更快。建议结合现场天气、空投设备和无人机载重 {{ totalPayload }}kg 综合决策。</div>
              </div>
              <div class="panel-actions">
                <el-button size="large" @click="stage = 2">← 上一步</el-button>
                <el-button type="primary" size="large" @click="stage = 4">✋ 人工优化</el-button>
              </div>
            </div>

            <!-- Stage 4 -->
            <div v-if="stage === 4" class="stage-panel">
              <div class="panel-title">
                <span class="p-icon">✋</span>人工拖拽优化
              </div>
              <div class="drag-tip">
                <div class="dt-icon">🖱️</div>
                <div class="dt-text">在地图上<b>拖拽航点</b>，绕开树木、淹没区、禁飞区。航线从黄色（初始）→ 绿色（优化）</div>
              </div>
              <div class="opt-lines">
                <div class="opt-line"><span class="dot dot-green"></span>已调整配送顺序</div>
                <div class="opt-line"><span class="dot dot-green"></span>已改降篮球场</div>
                <div class="opt-line"><span class="dot dot-green"></span>已绕行淹没区</div>
              </div>
              <div class="info-grid">
                <div class="info-card">
                  <div class="info-label">优化前航程</div>
                  <div class="info-value">{{ (totalDistance || 21.4).toFixed(1) }} <small>km</small></div>
                </div>
                <div class="info-card">
                  <div class="info-label">优化后航程</div>
                  <div class="info-value">
                    {{ Math.max((totalDistance || 21.4) - 1.3, 0).toFixed(1) }} <small>km</small>
                    <div class="delta down">-1.3km</div>
                  </div>
                </div>
                <div class="info-card">
                  <div class="info-label">风险等级</div>
                  <div class="info-value risk-low">低</div>
                </div>
                <div class="info-card">
                  <div class="info-label">可行性</div>
                  <div class="info-value" :class="feasible ? 'risk-low' : 'risk-high'">{{ feasible ? '可行' : '待验证' }}</div>
                </div>
              </div>
              <div class="note-box success">
                <div class="note-icon">✅</div>
                <div class="note-text">优化完成，航线已符合应急配送安全规则</div>
              </div>
              <div class="panel-actions">
                <el-button size="large" @click="stage = 3">← 上一步</el-button>
                <el-button type="primary" size="large" @click="stage = 1" plain>🔄 重新开始</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
html, body { margin: 0; padding: 0; }
#routes-detail-map { width: 100%; height: 100%; }
.leaflet-control-zoom a { background: rgba(255,255,255,0.1) !important; color: #fff !important; border: 1px solid rgba(255,255,255,0.2) !important; }
.leaflet-control-zoom a:hover { background: rgba(14,165,233,0.4) !important; }

.waypoint-marker, .zone-label, .route-label, .tree-marker, .optimize-tag { pointer-events: none; }
.waypoint-marker > div:first-child { pointer-events: auto; }
</style>

<style scoped>
.routes-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0b1120 0%, #0f1a32 100%);
  color: #e2e8f0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.routes-detail-page.embedded {
  min-height: 0;
  height: 100%;
  background: transparent;
  padding: 0;
  overflow: hidden;
}

.routes-detail-page.embedded-full {
  min-height: 0;
  height: 100%;
  width: 100%;
  background: transparent;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.routes-detail-page.embedded-full .app-body { padding-top: 0; }

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  background: rgba(15,26,50,0.9);
  border-bottom: 1px solid rgba(14,165,233,0.2);
  backdrop-filter: blur(10px);
  flex-shrink: 0;
}
.tb-left { display: flex; align-items: center; gap: 16px; }
.back-home, .back-agent {
  color: #94a3b8 !important;
  font-size: 12px !important;
  padding: 4px 10px !important;
  background: rgba(255,255,255,0.06) !important;
  border-radius: 6px !important;
}
.back-home:hover, .back-agent:hover { color: #fff !important; background: rgba(14,165,233,0.3) !important; }
.back-agent { border-left: 1px solid rgba(255,255,255,0.1); padding-left: 16px !important; }

.tb-title { display: flex; align-items: center; gap: 12px; margin-left: 8px; }
.tb-icon { font-size: 28px; }
.tb-title h1 { margin: 0; font-size: 20px; font-weight: 700; color: #fff; letter-spacing: 2px; }
.tb-sub { font-size: 12px; color: #64748b; }

.app-body {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 0;
  padding: 0;
}

.left-nav {
  width: 248px;
  flex-shrink: 0;
  margin-left: 0;
  background: rgba(11, 17, 32, 0.82);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(14, 165, 233, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 2;
}

.ln-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 14px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(180deg, rgba(14,165,233,0.14), rgba(11,17,32,0));
}
.ln-icon { font-size: 24px; }
.ln-name { font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 1px; }
.ln-sub { font-size: 11px; color: #64748b; }

.ln-list {
  padding: 10px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  overflow-y: auto;
}

.ln-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 10px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid transparent;
  background: transparent;
  transition: all 0.2s;
}
.ln-item:hover {
  background: rgba(14, 165, 233, 0.1);
  border-color: rgba(14, 165, 233, 0.18);
}
.ln-item.active {
  background: linear-gradient(180deg, rgba(14,165,233,0.25), rgba(14,165,233,0.1));
  border-color: rgba(14, 165, 233, 0.5);
  box-shadow: inset 0 0 0 1px rgba(14,165,233,0.2), 0 4px 18px rgba(14,165,233,0.15);
}
.ln-item.done { opacity: 0.85; }
.ln-item.done:hover { opacity: 1; }

.ln-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: #1e293b; color: #94a3b8;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
  transition: all 0.2s;
}
.ln-item.active .ln-num { background: #0ea5e9; color: #fff; }
.ln-item.done .ln-num { background: #22c55e; color: #fff; }

.ln-text { flex: 1; min-width: 0; }
.ln-title-line {
  font-size: 13.5px; font-weight: 700; color: #e2e8f0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ln-sub-line {
  font-size: 10.5px; color: #64748b;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin-top: 2px;
}
.ln-item.active .ln-title-line { color: #7dd3fc; }
.ln-item.done .ln-title-line { color: #86efac; }

.ln-arrow {
  font-size: 18px;
  color: #334155;
  transition: transform 0.2s, color 0.2s;
  flex-shrink: 0;
}
.ln-item:hover .ln-arrow { color: #7dd3fc; transform: translateX(2px); }
.ln-item.active .ln-arrow { color: #38bdf8; transform: translateX(3px); }

.ln-footer {
  padding: 12px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(2, 6, 23, 0.6);
}
.ln-foot-tip {
  font-size: 11px; line-height: 1.55;
  color: #64748b;
}

.right-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
  padding: 12px 12px 12px 0;
}

.main-row {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 0;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: hidden;
  position: relative;
}

/* 底层：绝对定位铺满的地图背景 */
.map-bg-wrap {
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
}
.map-bg-wrap .map-area {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0;
  min-height: 0;
}

/* 浮层 toolbar：顶部水平居中 */
.map-toolbar {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(15,26,50,0.88);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(14,165,233,0.28);
  border-radius: 10px;
  box-shadow: 0 6px 24px rgba(2, 18, 38, 0.55);
  max-width: 80%;
}

/* 地图右上角日夜模式切换（与 MapView.vue 完全一致）*/
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
.mt-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; color: #e2e8f0; }
.mt-icon { font-size: 16px; }
.mt-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-left: 14px; }
.badge { padding: 2px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.badge-blue { background: rgba(14,165,233,0.2); color: #38bdf8; }
.badge-red { background: rgba(239,68,68,0.2); color: #f87171; }
.badge-yellow { background: rgba(250,204,21,0.2); color: #facc15; }
.badge-green { background: rgba(34,197,94,0.2); color: #4ade80; }

/* 右侧抽屉面板：与其他模块 ConfigPanel.vue 一致，不遮挡顶部 header/TopBar */
.panel-col {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 460px;
  background: #0b1628;
  border-left: 1px solid #162540;
  display: flex;
  flex-direction: column;
  z-index: 500;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}
.stage-panel {
  background: rgba(15,26,50,0.92);
  border: 1px solid rgba(14,165,233,0.2);
  border-top: none;
  border-radius: 0 0 10px 10px;
  padding: 18px;
  flex: 1;
  overflow-y: auto;
}
.panel-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 700; color: #fff;
  margin-bottom: 14px; padding-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.p-icon { font-size: 18px; }

.route-preview { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.route-line-yellow { width: 60px; height: 4px; background: #facc15; border-radius: 2px; }
.route-line { width: 60px; height: 4px; background: currentColor; border-radius: 2px; }
.route-label { font-size: 12.5px; color: #cbd5e1; font-weight: 600; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.info-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 10px 12px;
}
.info-label { font-size: 11px; color: #64748b; margin-bottom: 4px; }
.info-value { font-size: 20px; font-weight: 800; color: #fff; letter-spacing: 1px; }
.info-value.small { font-size: 15px; font-weight: 700; }
.info-value small { font-size: 11px; font-weight: 400; color: #94a3b8; margin-left: 2px; }
.risk-high { color: #f87171 !important; }
.risk-mid { color: #fbbf24 !important; }
.risk-low { color: #4ade80 !important; }
.delta { font-size: 10.5px; margin-top: 2px; }
.delta.down { color: #4ade80; }
.delta.up { color: #f87171; }

.note-box {
  display: flex; gap: 10px;
  background: rgba(14,165,233,0.08);
  border: 1px solid rgba(14,165,233,0.2);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 14px;
}
.note-box.success { background: rgba(34,197,94,0.1); border-color: rgba(34,197,94,0.25); }
.note-icon { font-size: 16px; flex-shrink: 0; }
.note-text { font-size: 12px; color: #cbd5e1; line-height: 1.6; }

.panel-actions { display: flex; gap: 10px; margin-top: 10px; }
.panel-actions .el-button { flex: 1; }

.constraint-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.constraint-item {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 10px 12px;
}
.constraint-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.ci-icon { font-size: 16px; }
.ci-title { font-size: 12.5px; font-weight: 700; color: #e2e8f0; }
.ci-fields { display: flex; flex-direction: column; gap: 6px; }
.ci-fields label {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #94a3b8;
}
.ci-fields input[type="number"] {
  width: 64px; padding: 3px 6px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(14,165,233,0.3);
  border-radius: 4px; color: #fff;
  font-size: 12.5px; font-weight: 700; text-align: center;
}
.ci-fields input[type="number"]:focus { outline: none; border-color: #0ea5e9; }
.ci-fields span:last-child { color: #64748b; font-size: 11px; }

.zone-info {
  display: flex; flex-direction: column; gap: 4px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 6px;
  margin-bottom: 12px;
}
.zone-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #94a3b8; }
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-blue { background: #0ea5e9; box-shadow: 0 0 8px rgba(14,165,233,0.5); }
.dot-red { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.5); }
.dot-green { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); }

.compare-row { display: flex; gap: 10px; margin-bottom: 12px; }
.compare-card {
  flex: 1;
  background: rgba(255,255,255,0.04);
  border: 2px solid transparent;
  border-radius: 10px;
  padding: 10px;
  cursor: default;
  transition: all 0.2s;
}
.compare-card.ca { border-color: rgba(245,158,11,0.25); }
.compare-card.cb { border-color: rgba(34,197,94,0.25); }
.ca-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.ca-badge {
  width: 24px; height: 24px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 12px; font-weight: 700; flex-shrink: 0;
}
.ca-name { font-size: 12.5px; font-weight: 700; color: #fff; }
.ca-sub { font-size: 10px; color: #64748b; }
.ca-body { display: flex; flex-direction: column; gap: 3px; }
.ca-line { display: flex; justify-content: space-between; font-size: 11.5px; color: #94a3b8; }
.ca-line .plus { color: #fbbf24; font-weight: 600; }
.ca-line .val { color: #cbd5e1; font-weight: 600; }

.opt-table-wrap {
  margin-bottom: 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(14,165,233,0.18);
  border-radius: 8px;
  overflow: hidden;
}
.opt-table-title {
  padding: 8px 12px;
  font-size: 12px; font-weight: 700; color: #7dd3fc;
  background: rgba(14,165,233,0.1);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.opt-table { display: flex; flex-direction: column; }
.opt-table-head, .opt-table-row {
  display: grid;
  grid-template-columns: 32px 1fr 1fr 52px 52px;
  gap: 4px;
  padding: 6px 12px;
  font-size: 11px;
  align-items: center;
}
.opt-table-head { color: #64748b; font-weight: 600; background: rgba(255,255,255,0.02); border-bottom: 1px solid rgba(255,255,255,0.04); }
.opt-table-row { color: #cbd5e1; border-bottom: 1px solid rgba(255,255,255,0.04); }
.opt-table-row:last-child { border-bottom: none; }
.rid { color: #64748b; font-weight: 700; }
.rname { color: #e2e8f0; font-weight: 600; }
.rvia { color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rdist { color: #fbbf24; }
.rtime { color: #7dd3fc; }

.drag-tip {
  display: flex; gap: 10px;
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 10px;
}
.dt-icon { font-size: 18px; flex-shrink: 0; }
.dt-text { font-size: 12px; color: #cbd5e1; line-height: 1.7; }
.dt-text b { color: #60a5fa; }

.opt-lines { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.opt-line {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #4ade80;
  padding: 6px 10px;
  background: rgba(34,197,94,0.08);
  border-radius: 4px;
}

/* 面板顶部标题栏（与 RightPanel.vue 的 rp-header 风格一致）*/
.panel-close-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #112040;
  border-bottom: 1px solid #162540;
  flex-shrink: 0;
}
.pc-title {
  font-size: 12px;
  font-weight: 700;
  color: #cdd9f0;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.5px;
}
.pc-close {
  background: none;
  border: 1px solid #1e3560;
  border-radius: 4px;
  color: #3d5a80;
  cursor: pointer;
  padding: 2px 8px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  transition: all 0.2s;
}
.pc-close:hover {
  border-color: #ff3d57;
  color: #ff3d57;
}

/* 抽屉内滚动区域 */
.panel-col .stage-panel {
  flex: 1;
  overflow-y: auto;
  background: #0b1628;
  border: none;
  border-radius: 0;
  padding: 12px 16px;
}


</style>
