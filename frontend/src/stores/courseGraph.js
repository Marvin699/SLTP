import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchProjects, fetchProject } from '@/api/courseGraph'

export const useCourseGraphStore = defineStore('courseGraph', () => {
  const projects = ref([])
  const currentProject = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function loadProjects() {
    loading.value = true
    error.value = null
    try {
      const res = await fetchProjects()
      projects.value = res.data || []
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value = false
    }
  }

  async function loadProject(projectId) {
    loading.value = true
    error.value = null
    try {
      const res = await fetchProject(projectId)
      currentProject.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value = false
    }
  }

  return { projects, currentProject, loading, error, loadProjects, loadProject }
})
