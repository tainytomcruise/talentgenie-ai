import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/config/axios'

export const useLearningStore = defineStore('learning', () => {
  // State
  const learningPath = ref(null) // Current/Active path being viewed
  const savedPaths = ref([]) // List of all saved paths
  const progress = ref([]) // Training progress
  const roles = ref([])
  const goals = ref([])
  const loading = ref(false)
  const loadingPaths = ref(false)
  const generating = ref(false)
  const error = ref(null)

  // Actions
  async function generateLearningPath(currentRole, careerGoal, employeeId = null) {
    generating.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/learning/generate-path', {
        current_role: currentRole,
        career_goal: careerGoal,
        employee_id: employeeId
      })

      // Add to saved paths if it has an ID
      if (response.data.id) {
        const newPath = {
          id: response.data.id,
          learning_path: response.data.learning_path,
          progress: 1,
          created_at: new Date().toISOString()
        }
        savedPaths.value.unshift(newPath)
      }

      learningPath.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      generating.value = false
    }
  }

  async function fetchSavedLearningPath(employeeId) {
    loadingPaths.value = true
    error.value = null
    try {
      console.log('Store: Fetching saved paths for', employeeId)
      const response = await apiClient.get(`/api/learning/paths/${employeeId}`)
      console.log('Store: Saved paths response:', response.data)

      if (response.data.learning_paths) {
        savedPaths.value = response.data.learning_paths
        // Set the most recent one as active if none selected
        if (savedPaths.value.length > 0 && !learningPath.value) {
          learningPath.value = savedPaths.value[0].learning_path
          // Attach ID and progress to it for updates
          learningPath.value.id = savedPaths.value[0].id
          learningPath.value.progress = savedPaths.value[0].progress
        }
      }
      return response.data
    } catch (err) {
      console.error('Failed to fetch saved paths:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateLearningPathModule(pathId, moduleIndex, completed) {
    try {
      console.log('Store: Updating module for path', pathId, moduleIndex, completed)
      const response = await apiClient.patch('/api/learning/path/module', {
        path_id: pathId,
        module_index: moduleIndex,
        completed: completed
      })

      // Update in savedPaths list
      const path = savedPaths.value.find(p => p.id === pathId)
      if (path) {
        const modules = path.learning_path.modules
        if (modules && modules[moduleIndex]) {
          modules[moduleIndex].completed = completed
          // Update progress from response if available, otherwise increment
          if (response.data && response.data.progress) {
            path.progress = response.data.progress
          } else {
            // Fallback: increment progress (assuming sequential)
            path.progress = Math.floor(path.progress) + 1
          }
        }
      }

      // Also update current learningPath if it matches
      if (learningPath.value && learningPath.value.id === pathId) {
        learningPath.value.progress = (savedPaths.value.find(p => p.id === pathId)?.progress) || learningPath.value.progress

        // Also update the specific module in the active path if needed
        let activeModules = learningPath.value.learning_path?.modules || learningPath.value.modules
        if (activeModules && activeModules[moduleIndex]) {
          activeModules[moduleIndex].completed = completed
        }
      }

      return response.data
    } catch (err) {
      console.error('Failed to update module:', err)
      throw err
    }
  }

  async function fetchLearningProgress(employeeId) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/api/learning/progress/${employeeId}`)
      progress.value = response.data.progress
      return response.data.progress
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function completeModule(moduleId) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.patch('/api/learning/module/complete', {
        module_id: moduleId
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTrainingStatus(trainingId, status) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.patch('/api/learning/training/status', {
        training_id: trainingId,
        status: status
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRolesAndGoals() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/learning/roles-goals')

      roles.value = response.data.roles
      goals.value = response.data.goals
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    learningPath,
    savedPaths,
    progress,
    roles,
    goals,
    loading,
    loadingPaths,
    generating,
    error,
    // Actions
    generateLearningPath,
    fetchLearningProgress,
    completeModule,
    updateTrainingStatus,
    fetchRolesAndGoals,
    fetchSavedLearningPath,
    updateLearningPathModule
  }
})
