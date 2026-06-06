import { defineStore } from 'pinia'

function buildGeojson(depot, trips) {
  const features = trips.map((t, i) => ({
    type: 'Feature',
    geometry: { type: 'LineString', coordinates: t.coords },
    properties: {
      trip_index: i,
      uav_id: t.uavId,
      uav_name: t.uavName,
      delivery_mode: 'relay',
      distance: t.distance,
      points_served: t.waypoints.length - 1
    }
  }))
  return { type: 'FeatureCollection', features }
}

const D = [106.408, 23.816]

const presetSolutions = [
  {
    id: 'mock_s_001',
    groupId: '第1组',
    studentName: '陈建国',
    submittedAt: '2026-05-18 14:22',
    notes: '使用2台载重10kg无人机，优先覆盖高优先级点',
    depot: { name: '渠洋村应急起降点', lng: 106.408, lat: 23.816, type: 'start' },
    demands: [
      { name: '怀渠村', lng: 106.402, lat: 23.825, type: 'delivery', priority: 1 },
      { name: '塘麻村', lng: 106.432, lat: 23.812, type: 'delivery', priority: 2 },
      { name: '坡乐村', lng: 106.426, lat: 23.808, type: 'delivery', priority: 2 },
      { name: '东风村', lng: 106.415, lat: 23.822, type: 'delivery', priority: 3 },
      { name: '古桥村', lng: 106.428, lat: 23.830, type: 'delivery', priority: 1 },
      { name: '新和村', lng: 106.418, lat: 23.819, type: 'delivery', priority: 3 },
      { name: '怀书村', lng: 106.404, lat: 23.828, type: 'delivery', priority: 2 },
      { name: '雅力村', lng: 106.426, lat: 23.826, type: 'delivery', priority: 1 }
    ],
    materials: { totalMass: 920, items: ['饮用水','医用包','食品','通信设备'] },
    uav: { model: 'DJI M300 RTK', count: 2, perPayload: 10, totalPayload: 20 },
    optimizer: {
      feasible: true,
      totalDistance: 38.4,
      totalTime: 78,
      routes: [
        { id: 'r1', drone: 'M300-01', waypoints: ['depot','古桥村','怀渠村','怀书村','depot'], distance: 19.8, time: 40 },
        { id: 'r2', drone: 'M300-02', waypoints: ['depot','雅力村','塘麻村','坡乐村','东风村','新和村','depot'], distance: 18.6, time: 38 }
      ],
      routeTable: [
        { trip: 1, drone: 'M300-01', via: '古桥村→怀渠村→怀书村', dist: 19.8, time: 40 },
        { trip: 2, drone: 'M300-02', via: '雅力村→塘麻村→坡乐村→东风村→新和村', dist: 18.6, time: 38 }
      ],
      geojson: buildGeojson(D, [
        { uavId: 'M300-01', uavName: 'DJI M300 RTK', distance: 19.8, coords: [D, [106.428,23.830], [106.402,23.825], [106.404,23.828], D], waypoints: ['depot','古桥村','怀渠村','怀书村','depot'] },
        { uavId: 'M300-02', uavName: 'DJI M300 RTK', distance: 18.6, coords: [D, [106.426,23.826], [106.432,23.812], [106.426,23.808], [106.415,23.822], [106.418,23.819], D], waypoints: ['depot','雅力村','塘麻村','坡乐村','东风村','新和村','depot'] }
      ])
    },
    verdict: '优秀',
    verdictColor: '#22c55e'
  },
  {
    id: 'mock_s_002',
    groupId: '第3组',
    studentName: '李欣怡',
    submittedAt: '2026-05-18 15:47',
    notes: '无人机只有1台，载重15kg，必须分多趟次运输',
    depot: { name: '渠洋村应急起降点', lng: 106.408, lat: 23.816, type: 'start' },
    demands: [
      { name: '怀渠村', lng: 106.402, lat: 23.825, type: 'delivery', priority: 1 },
      { name: '塘麻村', lng: 106.432, lat: 23.812, type: 'delivery', priority: 2 },
      { name: '坡乐村', lng: 106.426, lat: 23.808, type: 'delivery', priority: 2 },
      { name: '东风村', lng: 106.415, lat: 23.822, type: 'delivery', priority: 3 },
      { name: '古桥村', lng: 106.428, lat: 23.830, type: 'delivery', priority: 1 },
      { name: '新和村', lng: 106.418, lat: 23.819, type: 'delivery', priority: 3 }
    ],
    materials: { totalMass: 680, items: ['饮用水','医用包','食品'] },
    uav: { model: '纵横 CW-25', count: 1, perPayload: 15, totalPayload: 15 },
    optimizer: {
      feasible: true,
      totalDistance: 62.1,
      totalTime: 132,
      routes: [
        { id: 'r1', drone: 'CW-25-01', waypoints: ['depot','古桥村','怀渠村','怀书村','depot'], distance: 21.4, time: 44 },
        { id: 'r2', drone: 'CW-25-01', waypoints: ['depot','塘麻村','坡乐村','depot'], distance: 20.3, time: 42 },
        { id: 'r3', drone: 'CW-25-01', waypoints: ['depot','雅力村','东风村','新和村','depot'], distance: 20.4, time: 46 }
      ],
      routeTable: [
        { trip: 1, drone: 'CW-25-01', via: '古桥村→怀渠村→怀书村', dist: 21.4, time: 44 },
        { trip: 2, drone: 'CW-25-01', via: '塘麻村→坡乐村', dist: 20.3, time: 42 },
        { trip: 3, drone: 'CW-25-01', via: '雅力村→东风村→新和村', dist: 20.4, time: 46 }
      ],
      geojson: buildGeojson(D, [
        { uavId: 'CW-25-01', uavName: '纵横 CW-25', distance: 21.4, coords: [D, [106.428,23.830], [106.402,23.825], [106.404,23.828], D], waypoints: ['depot','古桥村','怀渠村','怀书村','depot'] },
        { uavId: 'CW-25-01', uavName: '纵横 CW-25', distance: 20.3, coords: [D, [106.432,23.812], [106.426,23.808], D], waypoints: ['depot','塘麻村','坡乐村','depot'] },
        { uavId: 'CW-25-01', uavName: '纵横 CW-25', distance: 20.4, coords: [D, [106.426,23.826], [106.415,23.822], [106.418,23.819], D], waypoints: ['depot','雅力村','东风村','新和村','depot'] }
      ])
    },
    verdict: '良好',
    verdictColor: '#0ea5e9'
  },
  {
    id: 'mock_s_003',
    groupId: '第5组',
    studentName: '王浩宇',
    submittedAt: '2026-05-18 16:12',
    notes: '无人机载重10kg，需求总量1486kg——运力严重不足，方案不可行，需要3架以上。',
    depot: { name: '渠洋村应急起降点', lng: 106.408, lat: 23.816, type: 'start' },
    demands: [
      { name: '怀渠村', lng: 106.402, lat: 23.825, type: 'delivery', priority: 1 },
      { name: '塘麻村', lng: 106.432, lat: 23.812, type: 'delivery', priority: 2 },
      { name: '坡乐村', lng: 106.426, lat: 23.808, type: 'delivery', priority: 2 },
      { name: '东风村', lng: 106.415, lat: 23.822, type: 'delivery', priority: 3 },
      { name: '古桥村', lng: 106.428, lat: 23.830, type: 'delivery', priority: 1 },
      { name: '新和村', lng: 106.418, lat: 23.819, type: 'delivery', priority: 3 },
      { name: '怀书村', lng: 106.404, lat: 23.828, type: 'delivery', priority: 2 },
      { name: '雅力村', lng: 106.426, lat: 23.826, type: 'delivery', priority: 1 }
    ],
    materials: { totalMass: 1486, items: ['饮用水','医用包','食品','通信设备'] },
    uav: { model: 'SKY-10', count: 1, perPayload: 10, totalPayload: 10 },
    optimizer: {
      feasible: false,
      totalDistance: 128.6,
      totalTime: 268,
      routes: [
        { id: 'r1', drone: 'SKY-10-01', waypoints: ['depot','古桥村','怀渠村','depot'], distance: 16.8, time: 34 },
        { id: 'r2', drone: 'SKY-10-01', waypoints: ['depot','雅力村','怀书村','depot'], distance: 17.2, time: 36 },
        { id: 'r3', drone: 'SKY-10-01', waypoints: ['depot','塘麻村','坡乐村','depot'], distance: 20.3, time: 42 },
        { id: 'r4', drone: 'SKY-10-01', waypoints: ['depot','东风村','新和村','depot'], distance: 18.4, time: 38 },
        { id: 'r5', drone: 'SKY-10-01', waypoints: ['depot','古桥村','雅力村','depot'], distance: 15.9, time: 32 }
      ],
      routeTable: [
        { trip: 1, drone: 'SKY-10-01', via: '古桥村→怀渠村', dist: 16.8, time: 34 },
        { trip: 2, drone: 'SKY-10-01', via: '雅力村→怀书村', dist: 17.2, time: 36 },
        { trip: 3, drone: 'SKY-10-01', via: '塘麻村→坡乐村', dist: 20.3, time: 42 },
        { trip: 4, drone: 'SKY-10-01', via: '东风村→新和村', dist: 18.4, time: 38 },
        { trip: 5, drone: 'SKY-10-01', via: '古桥村→雅力村', dist: 15.9, time: 32 }
      ],
      geojson: buildGeojson(D, [
        { uavId: 'SKY-10-01', uavName: 'SKY-10', distance: 16.8, coords: [D, [106.428,23.830], [106.402,23.825], D], waypoints: ['depot','古桥村','怀渠村','depot'] },
        { uavId: 'SKY-10-01', uavName: 'SKY-10', distance: 17.2, coords: [D, [106.426,23.826], [106.404,23.828], D], waypoints: ['depot','雅力村','怀书村','depot'] },
        { uavId: 'SKY-10-01', uavName: 'SKY-10', distance: 20.3, coords: [D, [106.432,23.812], [106.426,23.808], D], waypoints: ['depot','塘麻村','坡乐村','depot'] },
        { uavId: 'SKY-10-01', uavName: 'SKY-10', distance: 18.4, coords: [D, [106.415,23.822], [106.418,23.819], D], waypoints: ['depot','东风村','新和村','depot'] },
        { uavId: 'SKY-10-01', uavName: 'SKY-10', distance: 15.9, coords: [D, [106.428,23.830], [106.426,23.826], D], waypoints: ['depot','古桥村','雅力村','depot'] }
      ])
    },
    verdict: '需优化',
    verdictColor: '#f59e0b'
  }
]

export const useTeacherSolutionsStore = defineStore('teacherSolutions', {
  state: () => ({
    solutions: [...presetSolutions],
    selectedId: presetSolutions[0]?.id || null
  }),
  getters: {
    list: (s) => s.solutions,
    selected: (s) => s.solutions.find(x => x.id === s.selectedId) || null
  },
  actions: {
    select(id) { this.selectedId = id },
    remove(id) {
      this.solutions = this.solutions.filter(x => x.id !== id)
      if (this.selectedId === id) {
        this.selectedId = this.solutions[0]?.id || null
      }
    },
    add(solution) {
      const id = 's_' + Date.now()
      const item = { ...solution, id, submittedAt: new Date().toLocaleString('zh-CN') }
      this.solutions.unshift(item)
      this.selectedId = id
      return id
    }
  }
})
