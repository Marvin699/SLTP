import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getLLMConfigs,
  createLLMConfig,
  updateLLMConfig,
  deleteLLMConfig,
  activateLLMConfig,
  getActiveLLMConfig,
  testLLMConnection,
  initDefaultLLMConfig,
} from '../api/llm'

export const useLLMStore = defineStore('llm', () => {
  // ─── State ───
  const configs = ref([])
  const activeConfig = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const testingId = ref(null)

  // ─── Getters ───
  const hasConfigs = computed(() => configs.value.length > 0)
  const activeConfigName = computed(() => activeConfig.value?.name || '未配置')

  // ─── Actions ───
  /** 加载所有配置 */
  async function loadConfigs() {
    loading.value = true
    error.value = null
    try {
      const res = await getLLMConfigs()
      configs.value = res.data || []
      // 找到激活的配置
      activeConfig.value = configs.value.find(c => c.is_active) || null
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value = false
    }
  }

  /** 添加配置 */
  async function addConfig(config) {
    loading.value = true
    error.value = null
    try {
      const res = await createLLMConfig(config)
      configs.value.unshift(res.data)
      if (res.data.is_active) {
        activeConfig.value = res.data
      }
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 更新配置 */
  async function updateConfig(id, config) {
    loading.value = true
    error.value = null
    try {
      const res = await updateLLMConfig(id, config)
      const index = configs.value.findIndex(c => c.id === id)
      if (index > -1) {
        configs.value[index] = res.data
      }
      if (res.data.is_active) {
        activeConfig.value = res.data
      }
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 删除配置 */
  async function removeConfig(id) {
    loading.value = true
    error.value = null
    try {
      await deleteLLMConfig(id)
      configs.value = configs.value.filter(c => c.id !== id)
      if (activeConfig.value?.id === id) {
        activeConfig.value = configs.value.find(c => c.is_active) || null
      }
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return false
    } finally {
      loading.value = false
    }
  }

  /** 激活配置 */
  async function activateConfig(id) {
    loading.value = true
    error.value = null
    try {
      const res = await activateLLMConfig(id)
      // 更新本地状态
      configs.value.forEach(c => {
        c.is_active = (c.id === id)
      })
      activeConfig.value = configs.value.find(c => c.id === id) || null
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      return null
    } finally {
      loading.value = false
    }
  }

  /** 测试连接 */
  async function testConnection(id) {
    testingId.value = id
    try {
      const res = await testLLMConnection(id)
      return res.data
    } catch (e) {
      return { success: false, message: e.message }
    } finally {
      testingId.value = null
    }
  }

  /** 初始化默认配置 */
  async function initDefault() {
    try {
      const res = await initDefaultLLMConfig()
      await loadConfigs()
      return res.data
    } catch (e) {
      console.error('初始化默认配置失败:', e)
      return null
    }
  }

  return {
    configs,
    activeConfig,
    loading,
    error,
    testingId,
    hasConfigs,
    activeConfigName,
    loadConfigs,
    addConfig,
    updateConfig,
    removeConfig,
    activateConfig,
    testConnection,
    initDefault,
  }
})