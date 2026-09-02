import axios from 'axios'

const api = axios.create({
  baseURL: '/api/courseware',
  timeout: 60000,
})

function authHeaders() {
  const token = localStorage.getItem('sltp_token') || ''
  return { Authorization: `Bearer ${token}` }
}

/**
 * 课件列表（可按课程名筛选）
 */
export function fetchCoursewareList(courseName) {
  return api.get('/list', {
    params: courseName ? { course_name: courseName } : {},
    headers: authHeaders(),
  })
}

/**
 * 课程名列表
 */
export function fetchCourseNames() {
  return api.get('/courses', { headers: authHeaders() })
}

/**
 * 上传课件/资料（仅教师）
 */
export function uploadCourseware(file, courseName, title, fileType = 'courseware') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('course_name', courseName)
  formData.append('title', title || '')
  formData.append('file_type', fileType)
  return api.post('/upload', formData, {
    headers: { ...authHeaders(), 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  })
}

/**
 * 下载课件（浏览器直接跳转，携带 token 的场景需用 fetch 转 blob）
 */
export function downloadCourseware(item) {
  return axios.get(`/api/courseware/${item.id}/download`, {
    responseType: 'blob',
    headers: authHeaders(),
    timeout: 300000,
  }).then(res => {
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = item.filename || item.title
    a.click()
    URL.revokeObjectURL(url)
  })
}

/**
 * 删除课件（仅教师）
 */
export function deleteCourseware(id) {
  return api.delete(`/${id}`, { headers: authHeaders() })
}

/**
 * 文件预览地址（StaticFiles 静态挂载）
 */
export function previewUrl(item) {
  return `/uploads/${item.file_path}`
}
