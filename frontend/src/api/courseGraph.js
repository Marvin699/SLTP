import axios from 'axios'

const api = axios.create({
  baseURL: '/api/course-graph',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 获取所有项目列表（简要信息）
export function fetchProjects() {
  return api.get('/projects')
}

// 获取单个项目完整数据
export function fetchProject(projectId) {
  return api.get(`/projects/${projectId}`)
}

// 创建新项目
export function createProject(data) {
  return api.post('/projects', data)
}

// 更新项目
export function updateProject(projectId, data) {
  return api.put(`/projects/${projectId}`, data)
}

// 删除项目
export function deleteProject(projectId) {
  return api.delete(`/projects/${projectId}`)
}

// 导入JSON数据
export function importProjectData(projectId, data) {
  return api.post(`/projects/${projectId}/import`, data)
}

// 上传JSON文件
export function uploadProjectFile(projectId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/projects/${projectId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// 获取某项目所有节点的教学达成状态
export function fetchTeachingStatus(projectId) {
  return api.get(`/teaching-status/${projectId}`)
}

// 更新某节点的教学达成状态
export function updateTeachingStatus(data) {
  return api.put('/teaching-status', data)
}
