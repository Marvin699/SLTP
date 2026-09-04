import axios from 'axios'

const api = axios.create({
  baseURL: '/api/simulations',
  timeout: 60000,
})

function authHeaders() {
  const token = localStorage.getItem('sltp_token') || ''
  return { Authorization: `Bearer ${token}` }
}

/**
 * 仿真视频列表
 */
export function fetchSimulationList() {
  return api.get('/list', { headers: authHeaders() })
}

/**
 * 上传仿真视频（仅教师）
 * @param {File} file 视频文件
 * @param {string} groupNo 小组编号（如 1~6）
 * @param {string} title 标题（默认取文件名）
 */
export function uploadSimulationVideo(file, groupNo, title = '') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('group_no', groupNo || '')
  formData.append('title', title)
  return api.post('/upload', formData, {
    headers: { ...authHeaders(), 'Content-Type': 'multipart/form-data' },
    timeout: 600000,
  })
}

/**
 * 删除仿真视频（仅教师）
 */
export function deleteSimulationVideo(id) {
  return api.delete(`/${id}`, { headers: authHeaders() })
}
