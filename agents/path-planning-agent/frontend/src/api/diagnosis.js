import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export async function runDiagnosis(task, solution) {
  const response = await axios.post(`${API_BASE}/diagnosis/run`, { task, solution })
  return response
}

export async function runRuleDiagnosis(task, solution) {
  const response = await axios.post(`${API_BASE}/diagnosis/rule`, { task, solution })
  return response
}

export async function runAiDiagnosis(task, solution) {
  const response = await axios.post(`${API_BASE}/diagnosis/ai`, { task, solution })
  return response
}

export async function getDiagnosisHistory(limit = 10) {
  const response = await axios.get(`${API_BASE}/diagnosis/history`, { params: { limit } })
  return response
}

export async function getDiagnosisDetail(recordId) {
  const response = await axios.get(`${API_BASE}/diagnosis/${recordId}`)
  return response
}

export async function deleteDiagnosis(recordId) {
  const response = await axios.delete(`${API_BASE}/diagnosis/${recordId}`)
  return response
}