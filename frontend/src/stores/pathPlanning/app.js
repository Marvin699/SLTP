import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const activeModule = ref(1)

  const modules = [
    { id: 1, label: '配送点设置', icon: '📍' },
    { id: 2, label: '物资需求', icon: '📦' },
    { id: 3, label: '无人机选型', icon: '🚁' },
    { id: 4, label: '路径规划', icon: '🗺' },
    { id: 9, label: '航线详情', icon: '🛰️' },
    { id: 5, label: '方案诊断', icon: '🔍' },
    { id: 6, label: '方案优出', icon: '📊' },
    { id: 10, label: '方案审阅', icon: '👨‍🏫' },
    { id: 7, label: '案例管理', icon: '📚' },
    { id: 8, label: '系统设置', icon: '⚙' },
  ]

  function setModule(id) {
    activeModule.value = id
  }

  return { activeModule, modules, setModule }
})
