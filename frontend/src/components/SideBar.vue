<template>
  <aside class="h-screen w-64 bg-white border-r border-gray-200 flex flex-col">
    <div class="p-6 flex items-center space-x-3">
      <div class="bg-gradient-to-br from-purple-500 to-blue-500 rounded-full p-3 shadow-md">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" viewBox="0 0 24 24" fill="currentColor">
          <path d="M13 2L3 14h7v8l11-12h-8z" />
        </svg>
      </div>
      <div>
        <h1 class="text-lg font-semibold text-gray-800">TalentGenie</h1>
        <p class="text-xs text-gray-500">{{ isEmployee ? 'Employee Portal' : 'HR Portal' }}</p>
      </div>
    </div>

    <nav class="flex-1 px-4 space-y-2">
      <template v-for="item in getNavItems" :key="item.label">
        <!-- Regular Link -->
        <router-link
          v-if="!item.isModal"
          :to="item.route"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            :class="[
              'flex items-center space-x-3 w-full px-3 py-2 rounded-lg transition-all duration-200',
              isActive
                ? isEmployee
                  ? 'bg-gradient-to-r from-green-600 to-teal-500 text-white shadow'
                  : 'bg-gradient-to-r from-indigo-600 to-purple-500 text-white shadow'
                : 'text-gray-700 hover:bg-gray-100'
            ]"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </button>
        </router-link>

        <!-- Modal Trigger Button -->
        <button
          v-else
          @click="item.action"
          class="flex items-center space-x-3 w-full px-3 py-2 rounded-lg transition-all duration-200 text-gray-700 hover:bg-gray-100"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </button>
      </template>
    </nav>

    <!-- Leave Request Modal -->
    <div v-if="showLeaveModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
            <i class="fas fa-calendar-plus text-indigo-600"></i> Request Leave
          </h2>
          <button @click="showLeaveModal = false" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">Leave Type</label>
            <select v-model="leaveForm.leave_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              <option value="Vacation">Vacation</option>
              <option value="Sick Leave">Sick Leave</option>
              <option value="Personal Leave">Personal Leave</option>
              <option value="Bereavement">Bereavement</option>
              <option value="Parental Leave">Parental Leave</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">Start Date</label>
              <input v-model="leaveForm.start_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1">End Date</label>
              <input v-model="leaveForm.end_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1">Reason</label>
            <textarea v-model="leaveForm.reason" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Reason..."></textarea>
          </div>

          <div class="pt-4 flex gap-3">
            <button 
              @click="showLeaveModal = false"
              class="flex-1 py-2.5 border border-gray-300 text-gray-700 font-bold rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="submitLeaveRequest" 
              :disabled="isSubmittingLeave"
              class="flex-1 py-2.5 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex justify-center items-center gap-2 transition-colors"
            >
              <i v-if="isSubmittingLeave" class="fas fa-circle-notch fa-spin"></i>
              <span>{{ isSubmittingLeave ? 'Submitting...' : 'Submit Request' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import apiClient from '@/config/axios'
import { useAuthStore } from '@/stores/auth'

const { isEmployee } = defineProps({
  isEmployee: {
    type: Boolean,
    default: false
  }
})

const authStore = useAuthStore()

// Check if user is a manager
const isManager = computed(() => {
  if (!authStore.user?.job_title) return false
  const title = authStore.user.job_title.toLowerCase()
  return title.includes('manager') || 
         title.includes('head') || 
         title.includes('chief') || 
         title.includes('lead')
})

// Modal State
const showLeaveModal = ref(false)
const isSubmittingLeave = ref(false)
const leaveForm = ref({
  leave_type: 'Vacation',
  start_date: '',
  end_date: '',
  reason: ''
})

const openLeaveModal = () => {
  showLeaveModal.value = true
}

const submitLeaveRequest = async () => {
  if (!leaveForm.value.start_date || !leaveForm.value.end_date || !leaveForm.value.reason) {
    alert('Please fill in all fields')
    return
  }
  
  isSubmittingLeave.value = true
  try {
    await apiClient.post('/api/leave/request', leaveForm.value)
    
    // Success
    showLeaveModal.value = false
    alert('Leave Request Submitted Successfully!')
    
    // Reset form
    leaveForm.value = { leave_type: 'Vacation', start_date: '', end_date: '', reason: '' }
    
  } catch (error) {
    console.error('Error submitting leave:', error)
    alert(error.response?.data?.error || 'Failed to submit leave request')
  } finally {
    isSubmittingLeave.value = false
  }
}

const hrNavItems = [
  { label: 'Recruitment', icon: 'fas fa-user-plus', route: '/admin/recruitment' },
  { label: 'Jobs', icon: 'fas fa-briefcase', route: '/admin/jobs' },
  { label: 'Policies', icon: 'fas fa-file-contract', route: '/admin/policy' },
  { label: 'Analytics', icon: 'fas fa-chart-bar', route: '/admin/analytics' },
  { label: 'Employees', icon: 'fas fa-users', route: '/admin/employees' },
  { label: 'Notifications', icon: 'fas fa-bell', route: '/admin/notifications' }
]

const employeeNavItems = computed(() => {
  const items = [
    { label: 'Dashboard', icon: 'fas fa-home', route: '/employee/dashboard' },
    { label: 'Wellness', icon: 'fas fa-heart', route: '/employee/wellness' },
    { label: 'My Learning', icon: 'fas fa-graduation-cap', route: '/employee/learning' },
    { label: 'Request Leave', icon: 'fas fa-calendar-plus', isModal: true, action: openLeaveModal },
    { label: 'Details', icon: 'fas fa-user-circle', route: '/employee/personal-details' },
  ]
  
  if (isManager.value) {
    items.splice(1, 0, { label: 'Team', icon: 'fas fa-users', route: '/employee/team' })
  }
  
  return items
})

const getNavItems = computed(() => (isEmployee ? employeeNavItems.value : hrNavItems))
</script>
