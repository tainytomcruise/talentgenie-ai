import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/config/axios'

export const useEmployeeStore = defineStore('employee', () => {
  // State
  const dashboard = ref(null)
  const skillRecommendations = ref([])
  const referenceLetter = ref(null)
  const employmentProof = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchDashboardSummary(employeeId) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/api/employee/dashboard/summary/${employeeId}`)
      dashboard.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSkillRecommendations(employeeId, careerGoal = null) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/employee/ai_skill_recommendations', {
        employee_id: employeeId,
        career_goal: careerGoal
      })
      skillRecommendations.value = response.data.recommendations
      return response.data.recommendations
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function generateReferenceLetter(employeeId, achievements = null) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/employee/document_request/reference', {
        employee_id: employeeId,
        achievements
      })
      referenceLetter.value = response.data.letter
      return response.data.letter
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function generateEmploymentProof(employeeId) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/employee/document_request/employment_proof', {
        employee_id: employeeId
      })
      employmentProof.value = response.data.document
      return response.data.document
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    dashboard,
    skillRecommendations,
    referenceLetter,
    employmentProof,
    loading,
    error,
    // Actions
    fetchDashboardSummary,
    fetchSkillRecommendations,
    generateReferenceLetter,
    generateEmploymentProof
  }
})
