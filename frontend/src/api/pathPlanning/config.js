import { createApi } from '@/utils/request'

const api = createApi({ baseURL: '/api/path-planning/config' })

export const listConfigs = () => api.get('/list')

export const loadConfig = (filename) => api.get(`/load/${encodeURIComponent(filename)}`)

export const saveConfig = (filename, content) => api.post('/save', { filename, content })

export const deleteConfig = (filename) => api.delete(`/delete/${encodeURIComponent(filename)}`)
