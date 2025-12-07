import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/config/axios'

export const useChatbotStore = defineStore('chatbot', () => {
  // State
  const messages = ref([])
  const chatHistory = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function sendMessage(message, userId = 1) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/askhr/chat', {
        message,
        user_id: userId
      })

      const data = response.data

      // Add user message and bot response to messages array
      messages.value.push({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      })
      messages.value.push({
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString()
      })

      // Handle additional messages (e.g., leave cards)
      if (data.additional_messages && Array.isArray(data.additional_messages)) {
        data.additional_messages.forEach(msg => {
          messages.value.push({
            role: 'assistant', // Map 'ai'/'assistant' to 'assistant'
            content: msg.text,
            type: msg.type,
            data: msg.data,
            timestamp: msg.timestamp
          })
        })
      }

      return data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchChatHistory(userId = 1, limit = 50) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/chat/history', {
        params: { user_id: userId, limit }
      })

      chatHistory.value = response.data.history
      // Populate messages for the view
      messages.value = response.data.history
      console.log("ChatbotStore: History loaded", messages.value.length, "messages")
      return response.data.history
    } catch (err) {
      console.error("ChatbotStore: Fetch history failed", err)
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function clearChatHistory(userId = 1) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/chat/clear', {
        user_id: userId
      })

      messages.value = []
      chatHistory.value = []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearMessages() {
    messages.value = []
  }

  function addMessage(message) {
    messages.value.push(message)
  }

  return {
    // State
    messages,
    chatHistory,
    loading,
    error,
    // Actions
    sendMessage,
    fetchChatHistory,
    clearMessages,
    clearChatHistory,
    addMessage
  }
})
