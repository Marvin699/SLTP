import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  generateReport as apiGenerate,
  getReportHistory as apiHistory,
  getReportDetail as apiDetail,
  updateReport as apiUpdate,
  deleteReport as apiDelete,
  downloadWordUrl,
  downloadPdfUrl,
} from '@/api/pathPlanning/report'
import { useOptimizerStore } from './optimizer'
import { useDiagnosisStore } from './diagnosis'

export const useReportStore = defineStore('report', () => {
  // ─── State ───
  const loading = ref(false)
  const error = ref(null)
  const currentReport = ref(null)
  const history = ref([])
  const historyLoading = ref(false)
  const schemeType = ref('路径规划方案')

  // ─── Getters ───
  const hasReport = computed(() => !!currentReport.value)
  const reportData = computed(() => currentReport.value?.report_data || currentReport.value?.data || null)
  const reportId = computed(() => currentReport.value?.id || null)

  // ─── Actions ───

  /** 生成报告 */
  async function generateReport() {
    loading.value = true
    error.value = null

    try {
      const optStore = useOptimizerStore()
      const diagStore = useDiagnosisStore()

      if (!optStore.result) {
        throw new Error('请先运行路径规划')
      }

      const task = optStore.buildTaskJson()
      task.scheme_type = schemeType.value  // 添加方案类型到task
      const solution = optStore.result
      const diagnosis = diagStore.result || null

      const res = await apiGenerate(task, solution, diagnosis, schemeType.value)
      currentReport.value = res.data

      await loadHistory()
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 加载历史记录 */
  async function loadHistory() {
    historyLoading.value = true
    try {
      const res = await apiHistory(20)
      console.log('API返回:', res)
      console.log('res.data:', res.data)
      history.value = res.data.records || []
      console.log('history设置后:', history.value)
    } catch (e) {
      console.error('加载报告历史失败:', e)
    } finally {
      historyLoading.value = false
    }
  }

  /** 查看报告详情 */
  async function viewReportDetail(reportId) {
    try {
      const res = await apiDetail(reportId)
      currentReport.value = res.data
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    }
  }

  /** 更新报告 */
  async function updateReportData(reportData) {
    if (!currentReport.value?.id) return null

    try {
      const res = await apiUpdate(currentReport.value.id, reportData)
      // 更新本地数据
      currentReport.value.data = reportData
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    }
  }

  /** 删除报告 */
  async function deleteReportItem(reportId) {
    try {
      await apiDelete(reportId)
      // 从本地列表中移除
      history.value = history.value.filter(r => r.id !== reportId)
      // 如果删除的是当前报告，清空当前报告
      if (currentReport.value?.id === reportId) {
        currentReport.value = null
      }
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return false
    }
  }

  /** 设置方案类型 */
  function setSchemeType(type) {
    schemeType.value = type
  }

  /** 重置当前报告 */
  function resetReport() {
    currentReport.value = null
    error.value = null
  }

  /** 获取下载链接 */
  function getWordDownloadUrl() {
    if (!currentReport.value?.id) return null
    return downloadWordUrl(currentReport.value.id)
  }

  function getPdfDownloadUrl() {
    if (!currentReport.value?.id) return null
    return downloadPdfUrl(currentReport.value.id)
  }

  return {
    loading,
    error,
    currentReport,
    history,
    historyLoading,
    schemeType,
    hasReport,
    reportData,
    reportId,
    generateReport,
    loadHistory,
    viewReportDetail,
    updateReportData,
    deleteReportItem,
    setSchemeType,
    resetReport,
    getWordDownloadUrl,
    getPdfDownloadUrl,
  }
})
