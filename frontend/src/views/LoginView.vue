<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-pink-500 text-gray-900 px-4"
  >
    <!-- Card -->
    <div
      class="bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl w-full max-w-md p-8 relative z-10"
    >
      <!-- Logo -->
      <div class="flex flex-col items-center mb-6">
        <div
          class="bg-gradient-to-br from-purple-500 to-blue-500 rounded-full p-4 shadow-md"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-10 w-10 text-white"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              d="M13 2L3 14h7v8l11-12h-8z"
            />
          </svg>
        </div>
        <h1 class="text-2xl font-semibold text-gray-800 mt-4">TalentGenie</h1>
        <p class="text-sm text-gray-500 -mt-1">
          AI-Powered HR Management Platform
        </p>
      </div>

      <!-- Form header -->
      <div class="text-center mb-6">
        <h2 class="text-lg font-semibold text-gray-800">
          {{ isRegistering ? 'Create Your Account' : 'Sign in to Your Account' }}
        </h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ isRegistering ? 'Fill in your details to get started' : 'Choose your role to continue' }}
        </p>
      </div>

      <!-- Role toggle -->
      <div class="flex bg-gray-100 rounded-full mb-5 p-1">
        <button
          @click="role = 'hr'"
          :class="role === 'hr' ? activeRoleClass : inactiveRoleClass"
          class="flex-1 flex items-center justify-center gap-2 rounded-full py-2 text-sm font-medium"
        >
          <i class="fas fa-briefcase"></i> HR Portal
        </button>
        <button
          @click="role = 'employee'"
          :class="role === 'employee' ? activeRoleClass : inactiveRoleClass"
          class="flex-1 flex items-center justify-center gap-2 rounded-full py-2 text-sm font-medium"
        >
          <i class="fas fa-user"></i> Employee
        </button>
      </div>

      <!-- Error message -->
      <div v-if="authStore.error" class="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm">
        <i class="fas fa-exclamation-circle mr-2"></i>{{ authStore.error }}
      </div>

      <!-- Success message -->
      <div v-if="successMessage" class="mb-4 p-3 bg-green-100 border border-green-300 text-green-700 rounded-lg text-sm">
        <i class="fas fa-check-circle mr-2"></i>{{ successMessage }}
      </div>

      <!-- Full Name (only for registration) -->
      <div v-if="isRegistering" class="mb-4">
        <label class="block text-sm text-gray-700 mb-1">Full Name</label>
        <input
          type="text"
          v-model="fullname"
          placeholder="John Doe"
          class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
          required
        />
      </div>

      <!-- Email -->
      <div class="mb-4">
        <label class="block text-sm text-gray-700 mb-1">Email</label>
        <input
          type="email"
          v-model="email"
          placeholder="email@company.com"
          class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
          required
        />
      </div>

      <!-- Password -->
      <div class="mb-6">
        <label class="block text-sm text-gray-700 mb-1">Password</label>
        <input
          type="password"
          v-model="password"
          placeholder="••••••••"
          class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
          required
        />
      </div>

      <!-- Login/Register button -->
      <button
        @click="handleSubmit"
        :disabled="authStore.loading"
        class="w-full bg-gray-900 text-white py-2.5 rounded-lg font-medium hover:bg-gray-800 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="authStore.loading">
          <i class="fas fa-spinner fa-spin mr-2"></i>
          {{ isRegistering ? 'Creating Account...' : 'Signing in...' }}
        </span>
        <span v-else>
          {{ isRegistering ? 'Create Account' : `Sign in as ${role === 'hr' ? 'HR' : 'Employee'}` }}
        </span>
      </button>

      <!-- Toggle between login and register -->
      <div class="text-center mt-4">
        <button
          @click="toggleMode"
          class="text-sm text-purple-600 hover:text-purple-700 font-medium"
        >
          {{ isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Register" }}
        </button>
      </div>

      <p class="text-center text-xs text-gray-500 mt-4">
        {{ isRegistering ? 'By registering, you agree to our Terms of Service' : 'Secure authentication powered by JWT' }}
      </p>
    </div>

    <!-- Footer -->
    <footer
      class="absolute bottom-6 text-center text-sm text-white opacity-80 w-full"
    >
      Powered by <b>AI</b> • Secure • Compliant
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const email = ref('')
const password = ref('')
const fullname = ref('')
const role = ref('hr')
const isRegistering = ref(false)
const successMessage = ref('')

// CSS classes
const activeRoleClass = 'bg-white shadow-md text-gray-900 transition-all duration-300'
const inactiveRoleClass = 'text-gray-500 hover:text-gray-700 transition-all duration-300'

// Toggle between login and register
function toggleMode() {
  isRegistering.value = !isRegistering.value
  successMessage.value = ''
  authStore.error = null
}

// Handle form submission
async function handleSubmit() {
  // Clear previous messages
  successMessage.value = ''
  authStore.error = null

  // Validation
  if (!email.value || !password.value) {
    authStore.error = 'Please fill in all required fields'
    return
  }

  if (isRegistering.value && !fullname.value) {
    authStore.error = 'Please enter your full name'
    return
  }

  try {
    if (isRegistering.value) {
      // Register new user
      await authStore.register(fullname.value, email.value, password.value, role.value)
      successMessage.value = 'Account created successfully! Please sign in.'

      // Switch to login mode after successful registration
      setTimeout(() => {
        isRegistering.value = false
        password.value = '' // Clear password for security
      }, 1500)
    } else {
      // Login existing user
      await authStore.login(email.value, password.value, role.value)

      // Navigate based on role
      if (role.value === 'hr') {
        router.push('/admin')
      } else {
        router.push('/employee')
      }
    }
  } catch (error) {
    // Error is already set in the store
    console.error('Authentication error:', error)
  }
}
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";

/* Add a subtle animated gradient overlay */
body {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
  background-size: 200% 200%;
  animation: gradientMove 8s ease infinite;
}

@keyframes gradientMove {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
