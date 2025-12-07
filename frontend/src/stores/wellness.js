import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/config/axios'

export const useWellnessStore = defineStore('wellness', () => {
  // State
  const resources = ref([])
  const tips = ref([])
  const events = ref([])
  const alerts = ref([])
  const milestones = ref([])
  const awards = ref([])
  const birthdays = ref([])
  const surveys = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchWellnessResources() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/wellness/resources')
      resources.value = response.data.resources
      return response.data.resources
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Static tips data
  const wellnessTipsData = {
    general: [
      "Take regular breaks every hour to stretch and rest your eyes.",
      "Stay hydrated! Aim for 8 glasses of water a day.",
      "Practice good posture at your desk to avoid back pain.",
      "Get 7-8 hours of quality sleep tonight.",
      "Take a short walk during your lunch break.",
      "Declutter your workspace for a clearer mind.",
      "Set small, achievable goals for the day."
    ],
    mental: [
      "Practice the 4-7-8 breathing technique when feeling overwhelmed.",
      "Write down three things you are grateful for today.",
      "Take 5 minutes to meditate or sit in silence.",
      "Connect with a colleague or friend for a quick chat.",
      "Limit your screen time after work to recharge.",
      "Be kind to yourself; acknowledge your efforts.",
      "Listen to your favorite calming music."
    ],
    physical: [
      "Do some desk stretches to release tension in your neck and shoulders.",
      "Take the stairs instead of the elevator today.",
      "Stand up and move around for a few minutes every hour.",
      "Try a new physical activity or workout routine this week.",
      "Focus on your ergonomics: adjust your chair and monitor height.",
      "Rest your eyes by looking at something 20 feet away for 20 seconds.",
      "Go for a brisk walk to boost your energy levels."
    ],
    nutrition: [
      "Eat a healthy, balanced breakfast to start your day right.",
      "Swap a sugary snack for a piece of fruit or nuts.",
      "Avoid caffeine late in the afternoon to improve sleep.",
      "Pack a nutritious lunch instead of ordering out.",
      "Include more leafy greens in your meals today.",
      "Drink a glass of water before every meal.",
      "Limit processed foods and choose whole foods when possible."
    ],
    sleep: [
      "Establish a consistent bedtime routine to signal your body it's time to sleep.",
      "Avoid screens (phones, computers, TV) for at least an hour before bed.",
      "Keep your bedroom cool, dark, and quiet.",
      "Avoid heavy meals and caffeine close to bedtime.",
      "Read a book or listen to a podcast to wind down.",
      "Try progressive muscle relaxation to ease into sleep.",
      "Stick to a regular sleep schedule, even on weekends."
    ]
  }

  async function fetchWellnessTips(category = 'general') {
    loading.value = false // No loading needed for local data
    error.value = null

    // Normalize category
    const cat = category.toLowerCase()

    // Check localStorage for cached tip
    const today = new Date().toISOString().split('T')[0]
    const storageKey = 'daily_wellness_tips'
    let cachedData = {}

    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        cachedData = JSON.parse(stored)
        // If date matches and we have a tip for this category, use it
        if (cachedData.date === today && cachedData.tips && cachedData.tips[cat]) {
          tips.value = [cachedData.tips[cat]]
          return tips.value
        }
        // If date doesn't match, reset cache
        if (cachedData.date !== today) {
          cachedData = { date: today, tips: {} }
        }
      } else {
        cachedData = { date: today, tips: {} }
      }
    } catch (e) {
      console.error('Error reading from localStorage', e)
      cachedData = { date: today, tips: {} }
    }

    // Generate new random tip from static data
    const categoryTips = wellnessTipsData[cat] || wellnessTipsData['general']
    const randomTip = categoryTips[Math.floor(Math.random() * categoryTips.length)]

    tips.value = [randomTip]

    // Cache the new tip
    try {
      if (!cachedData.tips) cachedData.tips = {}
      cachedData.tips[cat] = randomTip
      localStorage.setItem(storageKey, JSON.stringify(cachedData))
    } catch (e) {
      console.error('Error saving to localStorage', e)
    }

    return tips.value
  }

  async function fetchWellnessEvents() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/wellness/events')
      events.value = response.data.events
      return response.data.events
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function registerForEvent(employeeId, eventId) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/wellness/events/register', {
        employee_id: employeeId,
        event_id: eventId
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchHRWellnessResources() {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/hr/wellness/resources')
      resources.value = response.data.resources
      return response.data.resources
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createWellnessAlert(alertData) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/hr/wellness/alerts', alertData)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function trackMilestone(milestoneData) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/hr/wellness/milestones', milestoneData)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function giveAward(awardData) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/hr/wellness/awards', awardData)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchBirthdays(month) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/hr/wellness/birthdays', {
        params: { month }
      })
      birthdays.value = response.data.birthdays
      return response.data.birthdays
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createSurvey(surveyData) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/hr/wellness/surveys', surveyData)
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
    resources,
    tips,
    events,
    alerts,
    milestones,
    awards,
    birthdays,
    surveys,
    loading,
    error,
    // Actions
    fetchWellnessResources,
    fetchWellnessTips,
    fetchWellnessEvents,
    registerForEvent,
    fetchHRWellnessResources,
    createWellnessAlert,
    trackMilestone,
    giveAward,
    fetchBirthdays,
    createSurvey
  }
})
