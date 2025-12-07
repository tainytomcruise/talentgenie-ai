import { defineStore } from 'pinia'
import { ref } from 'vue'

// Use relative API path - Vite proxy will forward /api to backend
const API_BASE_URL = ''

export const usePolicyStore = defineStore('policy', () => {
  // State
  const jobPosting = ref(null)
  const policyDocument = ref(null)
  const locations = ref([])
  const tones = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function generateJobPosting(jobPostingRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/policy/generate/job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jobPostingRequest)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Job posting generation failed')
      }

      jobPosting.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function generatePolicyDocument(location, requirements) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/policy/generate/document`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, requirements })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Policy document generation failed')
      }

      policyDocument.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchLocations() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/policy/locations`)

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch locations')
      }

      locations.value = data.locations
      return data.locations
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTones() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/policy/tones`)

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch tones')
      }

      tones.value = data.tones
      return data.tones
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    jobPosting,
    policyDocument,
    locations,
    tones,
    loading,
    error,
    // Actions
    generateJobPosting,
    generatePolicyDocument,
    fetchLocations,
    fetchTones
  }
})
