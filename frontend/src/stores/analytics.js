import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

// Use relative API path - Vite proxy will forward /api to backend
const API_BASE_URL = ''

export const useAnalyticsStore = defineStore('analytics', () => {
  // State
  const summary = ref(null)
  const absenteeismTrends = ref(null)
  const retentionRisk = ref(null)
  const trainingCompletion = ref(null)
  const departments = ref([])
  const overview = ref(null)
  const recruitment = ref(null)
  const training = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Helper to get auth header
  function getAuthHeader() {
    const authStore = useAuthStore()
    return {
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    }
  }

  // Actions
  async function fetchSummary() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/summary`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch summary')
      }

      summary.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAbsenteeismTrends() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/absenteeism-trends`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch absenteeism trends')
      }

      absenteeismTrends.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRetentionRisk() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/retention-risk`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch retention risk')
      }

      retentionRisk.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTrainingCompletion() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/training-completion`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch training completion')
      }

      trainingCompletion.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchDepartments() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/departments`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch departments')
      }

      departments.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchOverview() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/overview`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch overview')
      }

      overview.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRecruitmentAnalytics() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/recruitment`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch recruitment analytics')
      }

      recruitment.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTrainingAnalytics() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/analytics/training`, {
        headers: getAuthHeader()
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch training analytics')
      }

      training.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    summary,
    absenteeismTrends,
    retentionRisk,
    trainingCompletion,
    departments,
    overview,
    recruitment,
    training,
    loading,
    error,
    // Actions
    fetchSummary,
    fetchAbsenteeismTrends,
    fetchRetentionRisk,
    fetchTrainingCompletion,
    fetchDepartments,
    fetchOverview,
    fetchRecruitmentAnalytics,
    fetchTrainingAnalytics
  }
})
