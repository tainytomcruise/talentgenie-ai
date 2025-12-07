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
      <div class="text-center mb-4">
        <h2 class="text-lg font-semibold text-gray-800">
          {{ mode === 'login' ? 'Sign in to Your Account' : 'Create a New Account' }}
        </h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ mode === 'login' ? 'Choose your role to continue' : 'Register as an employee, HR, or Candidate' }}
        </p>
      </div>

      <!-- Role toggle / Register tabs -->
      <!-- Role toggle / Register tabs -->
      <div class="flex flex-col gap-3 mb-6">
        <button
          v-if="mode === 'login'"
          @click="role = 'hr'"
          :class="role === 'hr' ? activeRoleClass : inactiveRoleClass"
          class="w-full flex items-center justify-center gap-3 py-3 rounded-xl text-sm font-medium border transition-all duration-200"
        >
          <i class="fas fa-briefcase"></i> HR Portal
        </button>
        <button
          v-if="mode === 'login'"
          @click="role = 'employee'"
          :class="role === 'employee' ? activeRoleClass : inactiveRoleClass"
          class="w-full flex items-center justify-center gap-3 py-3 rounded-xl text-sm font-medium border transition-all duration-200"
        >
          <i class="fas fa-user"></i> Employee
        </button>
        <button
          v-if="mode === 'login'"
          @click="role = 'candidate'"
          :class="role === 'candidate' ? activeRoleClass : inactiveRoleClass"
          class="w-full flex items-center justify-center gap-3 py-3 rounded-xl text-sm font-medium border transition-all duration-200"
        >
          <i class="fas fa-user-graduate"></i> Candidate
        </button>

        <!-- Registration top tabs -->
        <button
          v-if="mode === 'register'"
          @click="role = 'employee'"
          :class="role === 'employee' ? activeRoleClass : inactiveRoleClass"
          class="w-full flex items-center justify-center gap-3 py-3 rounded-xl text-sm font-medium border transition-all duration-200"
        >
          <i class="fas fa-user-plus"></i> Register as Employee
        </button>
        <button
          v-if="mode === 'register'"
          @click="role = 'hr'"
          :class="role === 'hr' ? activeRoleClass : inactiveRoleClass"
          class="w-full flex items-center justify-center gap-3 py-3 rounded-xl text-sm font-medium border transition-all duration-200"
        >
          <i class="fas fa-user-tie"></i> Register as HR
        </button>
        <button
          v-if="mode === 'register'"
          @click="role = 'candidate'"
          :class="role === 'candidate' ? activeRoleClass : inactiveRoleClass"
          class="w-full flex items-center justify-center gap-3 py-3 rounded-xl text-sm font-medium border transition-all duration-200"
        >
          <i class="fas fa-user-graduate"></i> Register as Candidate
        </button>
      </div>

      <!-- Login Form -->
      <div v-if="mode === 'login'">
        <form @submit.prevent="login">
          <div class="mb-4">
            <label class="block text-sm text-gray-700 mb-1">Email</label>
            <input
              type="email"
              v-model="email"
              placeholder="email@company.com"
              class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
          </div>

          <div class="mb-6">
            <label class="block text-sm text-gray-700 mb-1">Password</label>
            <input
              type="password"
              v-model="password"
              placeholder="••••••••"
              class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition"
            />
          </div>

          <button
            type="submit"
            class="w-full bg-gray-900 text-white py-2.5 rounded-lg font-medium hover:bg-gray-800 transition-all duration-300"
          >
            Sign in as {{ role === 'hr' ? 'HR' : (role === 'candidate' ? 'Candidate' : 'Employee') }}
          </button>
        </form>
      </div>

      <!-- Registration Form -->
      <div v-else>
        <form @submit.prevent="register">
          <div class="mb-4">
            <label class="block text-sm text-gray-700 mb-1">Full Name</label>
            <input v-model="name" type="text" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 transition" />
          </div>

          <div class="mb-4">
            <label class="block text-sm text-gray-700 mb-1">Email</label>
            <input v-model="email" type="email" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 transition" />
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm text-gray-700 mb-1">Password</label>
              <input v-model="password" type="password" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 transition" />
            </div>
            <div>
              <label class="block text-sm text-gray-700 mb-1">Confirm Password</label>
              <input v-model="confirmPassword" type="password" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 transition" />
            </div>
          </div>

          <button
            type="submit"
            class="w-full bg-green-600 text-white py-2.5 rounded-lg font-medium hover:bg-green-500 transition-all duration-300"
          >
            Register as {{ role === 'hr' ? 'HR' : (role === 'candidate' ? 'Candidate' : 'Employee') }}
          </button>

          <p class="text-center text-xs text-gray-500 mt-3">
            By registering you agree to the demo terms.
          </p>
        </form>
      </div>

      <!-- Mode toggle -->
      <div class="mt-5 text-center">
        <button @click="toggleMode" class="text-sm text-indigo-600 hover:underline">
          {{ mode === 'login' ? 'New user? Create an account' : 'Already have an account? Sign in' }}
        </button>
      </div>
    </div>

    <!-- Footer -->
    <footer
      class="absolute bottom-6 text-center text-sm text-white opacity-80 w-full"
    >
      Powered by <b>AI</b> • Secure • Compliant
    </footer>
  </div>
</template>

<script>
import apiClient from '@/config/axios'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'LoginRegistrationView',
  data() {
    return {
      // shared
      email: '',
      password: '',
      role: 'hr',
      mode: 'login', // 'login' | 'register'
      activeRoleClass: 'bg-purple-600 text-white border-purple-600 shadow-md',
      inactiveRoleClass: 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100 hover:border-gray-300',
      // registration fields
      name: '',
      confirmPassword: '',
    };
  },
  methods: {
    toggleMode() {
      // clear fields when switching
      if (this.mode === 'login') {
        this.mode = 'register';
      } else {
        this.mode = 'login';
      }
      this.clearTransientFields();
    },
    clearTransientFields() {
      this.email = '';
      this.password = '';
      this.confirmPassword = '';
      this.name = '';
    },
    async login() {
      if (!this.email || !this.password) {
        alert('Please provide email and password');
        return;
      }

      try {
        const response = await apiClient.post('/api/auth/login', {
          email: this.email,
          password: this.password,
          role: this.role
        });

        const data = response.data;

        // store token and redirect based on role returned from backend
        localStorage.setItem('token', data.token);
        localStorage.setItem('role', data.user?.role || this.role);

        // Update authStore state immediately so dashboard has data
        const authStore = useAuthStore()
        authStore.token = data.token
        authStore.user = data.user

        // Use case-insensitive role comparison for redirect
        const userRole = (data.user?.role || this.role).toLowerCase();

        if (userRole === 'hr' || userRole === 'hr manager') {
          this.$router.push('/admin');
        } else if (userRole === 'candidate') {
          this.$router.push('/candidate');
        } else {
          this.$router.push('/employee');
        }
      } catch (err) {
        console.error(err);
        if (err.response && err.response.status === 403) {
           alert('Contact HR to activate your account');
        } else {
           alert(err.response?.data?.message || err.response?.data?.msg || 'Login failed');
        }
      }
    },

    async register() {
      // Basic client-side validation with specific messages
      const name = this.name && this.name.trim();
      if (!name) {
        alert('Please enter your full name.');
        return;
      }
      if (!this.email) {
        alert('Please enter your email address.');
        return;
      }
      if (!this.password) {
        alert('Please enter a password.');
        return;
      }
      if (this.password !== this.confirmPassword) {
        alert('Passwords do not match. Please confirm your password.');
        return;
      }

      const payload = {
        fullname: name,
        email: this.email,
        password: this.password,
        role: this.role,
      };

      try {
        await apiClient.post('/api/auth/register', payload);

        // After successful register, switch to login mode and pre-fill email
        if (this.role === 'employee') {
            alert('Registration successful. Please wait for HR approval before logging in.');
        } else {
            alert('Registration successful — please sign in');
        }
        this.mode = 'login';
        this.password = '';
        this.confirmPassword = '';
      } catch (err) {
        console.error(err);
        alert(err.response?.data?.message || err.response?.data?.msg || 'Registration failed');
      }
    },
  },
};
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
