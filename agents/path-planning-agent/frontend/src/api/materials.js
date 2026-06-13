import axios from 'axios'

const api = axios.create({ baseURL: '/api/materials' })

export const fetchCategories = () => api.get('/categories')

export const computeMaterials = (payload) => api.post('/compute', payload)

export const fetchDefaultCase = () => api.get('/default-case')

export const fetchDefaultCaseVillage = (name) => api.get(`/default-case/${encodeURIComponent(name)}`)

/** 保存单个需求点的物资分配 */
export const saveAssignment = (payload) => api.post('/save', payload)

/** 批量保存物资分配 */
export const saveAssignmentsBatch = (payload) => api.post('/save-batch', payload)

/** 加载所有已保存的物资分配 */
export const loadSavedAssignments = () => api.get('/saved')

/** 删除指定需求点的物资分配 */
export const deleteSavedAssignment = (pointId) => api.delete(`/saved/${pointId}`)

/** 删除所有物资分配 */
export const deleteAllSavedAssignments = () => api.delete('/saved')
