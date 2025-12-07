import { defineStore } from 'pinia'
import { ref } from 'vue'

// Use relative API path - Vite proxy will forward /api to backend
const API_BASE_URL = ''

export const useRecruitmentStore = defineStore('recruitment', () => {
  // State
  const resumes = ref([])
  const matchResults = ref([])
  const interviewQuestions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function uploadResumes(files) {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files[]', file)
      })

      const response = await fetch(`${API_BASE_URL}/api/recruitment/upload`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Upload failed')
      }

      resumes.value = data.results
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function parseResume(file) {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/api/recruitment/parse`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Parse failed')
      }

      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function matchCandidates(jobDescription, jobId = null) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/recruitment/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_description: jobDescription, job_id: jobId })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Matching failed')
      }

      matchResults.value = data.rankings
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function generateInterviewQuestions(candidateName, skills, jobDescription) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_BASE_URL}/api/recruitment/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_name: candidateName,
          skills,
          job_description: jobDescription
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Question generation failed')
      }

      interviewQuestions.value = data.questions
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
    resumes,
    matchResults,
    interviewQuestions,
    loading,
    error,
    // Actions
    uploadResumes,
    parseResume,
    matchCandidates,
    generateInterviewQuestions
  }
})
