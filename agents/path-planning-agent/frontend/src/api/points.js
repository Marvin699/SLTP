import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 获取所有点位
 */
export function fetchAllPoints() {
  return api.get('/points')
}

/**
 * 创建单个点位
 */
export function createPoint(data) {
  return api.post('/points', data)
}

/**
 * 批量创建点位（覆盖旧数据）
 */
export function batchCreatePoints(points) {
  return api.post('/points/batch', { points })
}

/**
 * 更新点位
 */
export function updatePoint(id, data) {
  return api.put(`/points/${id}`, data)
}

/**
 * 删除点位
 */
export function deletePoint(id) {
  return api.delete(`/points/${id}`)
}

/**
 * 获取距离矩阵
 */
export function fetchDistanceMatrix() {
  return api.get('/points/distance-matrix')
}

/**
 * 导出GeoJSON
 */
export function exportGeoJSON() {
  return api.get('/points/geojson/export')
}
