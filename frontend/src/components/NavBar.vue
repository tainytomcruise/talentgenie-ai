<template>
  <header
    class="flex items-center bg-white border-b border-gray-200 px-8 py-4 shadow-sm"
  >
      <div class="flex-1">
        <span class="text-lg font-medium text-gray-700">{{ isEmployee ? 'Employee Portal' : 'HR Portal' }}</span>
    </div>

    <div class="flex items-center gap-4">
      <div class="text-sm text-gray-600">
        Welcome{{ isEmployee ? ',' : ' back,' }}
        <span class="font-medium" :class="isEmployee ? 'text-green-600' : 'text-indigo-600'">
          {{ authStore.user?.name || (isEmployee ? 'Employee' : 'HR') }}
        </span>
      </div>
      <button
        @click="handleLogout"
        class="flex items-center gap-2 text-sm text-gray-600 hover:text-indigo-600 transition-colors"
      >
        <i class="fas fa-sign-out-alt"></i>
        <span>Logout</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import apiClient from '@/config/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

defineProps({
  isEmployee: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

const handleLogout = async () => {
  try {
    const token = localStorage.getItem('access_token')

    if (token) {
      await apiClient.post('/api/logout')
    }

    // Clear local storage tokens and user info
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_name')
    localStorage.removeItem('token')
    localStorage.removeItem('role')

    // Redirect to login
    router.push('/login')
  } catch (err) {
    console.error('Logout failed:', err)
    // Clear local storage anyway and redirect
    localStorage.clear()
    router.push('/login')
  }
}
</script>
