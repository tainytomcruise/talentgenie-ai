import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/config/axios'

export const useSentimentStore = defineStore('sentiment', () => {
  // State
  const analysis = ref(null)
  const trends = ref([])
  const themes = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function analyzeSentiment(feedback) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/sentiment/analyze', { feedback })
      analysis.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSentimentTrends() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/sentiment/trend')
      trends.value = response.data.trends
      return response.data.trends
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSentimentThemes() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/sentiment/themes')
      themes.value = response.data.themes
      return response.data.themes
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    analysis,
    trends,
    themes,
    loading,
    error,
    // Actions
    analyzeSentiment,
    fetchSentimentTrends,
    fetchSentimentThemes
  }
})
