import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/config/axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isAuthenticated = computed(() => !!token.value)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function login(email, password, role) {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/auth/login', {
        email: email.toLowerCase(),
        password,
        role
      })

      const data = response.data
      token.value = data.token
      user.value = data.user
      localStorage.setItem('token', data.token)

      return data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(fullname, email, password, role = 'employee') {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/api/auth/register', {
        fullname,
        email: email.toLowerCase(),
        password,
        role
      })

      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return

    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/auth/me')
      console.log('fetchCurrentUser response:', response.data)
      user.value = response.data.user
      return response.data.user
    } catch (err) {
      console.error('fetchCurrentUser error:', err)
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    // State
    user,
    token,
    isAuthenticated,
    loading,
    error,
    // Actions
    login,
    register,
    fetchCurrentUser,
    logout
  }
})
