<template>
  <div class="p-6">
    <div class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Employees</h1>
        <p class="text-sm text-gray-500 mt-1">Manage and view all employee records</p>
      </div>
      
      <!-- Actions -->
      <div class="flex gap-3">
        <button v-if="isHR" @click="openAddModal" class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2">
          <i class="fas fa-plus"></i> Add Employee
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1 relative">
          <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by name, email, or job title..." 
            class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
          />
        </div>
        <div class="w-full md:w-64">
          <select 
            v-model="selectedDept" 
            class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent bg-white"
          >
            <option value="">All Departments</option>
            <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Employee Grid -->
    <div v-if="loading" class="flex justify-center py-12">
      <i class="fas fa-spinner fa-spin text-4xl text-purple-500"></i>
    </div>

    <div v-else-if="filteredEmployees.length === 0" class="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
      <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-users text-2xl text-gray-400"></i>
      </div>
      <h3 class="text-lg font-medium text-gray-900">No employees found</h3>
      <p class="text-gray-500 mt-1">Try adjusting your search or filters</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="emp in filteredEmployees" 
        :key="emp.emp_id" 
        class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {{ getInitials(emp.name) }}
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ emp.name }}</h3>
                <p class="text-xs text-gray-500">{{ emp.job_title }}</p>
              </div>
            </div>
            <span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full font-medium">
              {{ emp.department }}
            </span>
          </div>

          <div class="space-y-3 text-sm text-gray-600 mb-6">
            <div class="flex items-center gap-2">
              <i class="fas fa-envelope w-5 text-gray-400"></i>
              <span class="truncate">{{ emp.email }}</span>
            </div>
            <div class="flex items-center gap-2">
              <i class="fas fa-calendar-alt w-5 text-gray-400"></i>
              <span>Hired: {{ formatDate(emp.hire_date) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <i class="fas fa-door-open w-5 text-gray-400"></i>
              <span>Leaves Taken: {{ emp.leaves_taken || 0 }}</span>
            </div>
            <div v-if="emp.performance_score !== null" class="flex items-center gap-2">
              <i class="fas fa-star w-5 text-yellow-400"></i>
              <span class="font-medium text-gray-900">Performance Score: {{ emp.performance_score }}</span>
            </div>
          </div>

          <!-- Skills -->
          <div class="mb-6">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Skills</p>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="(skill, index) in (emp.skills || []).slice(0, 3)" 
                :key="index"
                class="px-2 py-1 bg-purple-50 text-purple-600 text-xs rounded-md border border-purple-100"
              >
                {{ skill }}
              </span>
              <span v-if="(emp.skills || []).length > 3" class="px-2 py-1 bg-gray-50 text-gray-500 text-xs rounded-md border border-gray-100">
                +{{ emp.skills.length - 3 }}
              </span>
              <span v-if="!(emp.skills || []).length" class="text-xs text-gray-400 italic">No skills listed</span>
            </div>
          </div>

          <div class="flex gap-2">
            <button 
              @click="openRateModal(emp)"
              class="flex-1 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
            >
              Rate
            </button>
            <button 
              v-if="isHR"
              @click="openAssignModal(emp)"
              class="flex-1 py-2 bg-white text-purple-600 border border-purple-600 rounded-lg hover:bg-purple-50 transition-colors text-sm font-medium"
            >
              Assign
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Rating Modal -->
    <div v-if="showRateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Rate Performance: {{ selectedEmployee?.name }}</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Score (-2 to 2)</label>
            <input 
              v-model.number="ratingForm.score" 
              type="number" 
              min="-2" 
              max="2"
              step="0.1"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Comment</label>
            <textarea 
              v-model="ratingForm.comment" 
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="e.g. Great leadership in meeting..."
            ></textarea>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button 
            @click="closeRateModal"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="confirmRating"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
    <!-- Add Employee Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Add New Employee</h3>
        
        <form @submit.prevent="submitAddEmployee" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <input v-model="addEmployeeForm.name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="addEmployeeForm.email" type="email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input v-model="addEmployeeForm.password" type="password" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
            <input v-model="addEmployeeForm.job_title" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
            <select v-model="addEmployeeForm.department" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 bg-white">
              <option value="" disabled>Select Department</option>
              <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
              <option value="Engineering">Engineering</option>
              <option value="HR">HR</option>
              <option value="Sales">Sales</option>
              <option value="Marketing">Marketing</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hire Date</label>
            <input v-model="addEmployeeForm.hire_date" type="date" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" />
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="closeAddModal" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">Add Employee</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assign Modal -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Assign Manager & Training</h3>
        <p class="text-sm text-gray-500 mb-4">For {{ selectedEmployee?.name }}</p>
        
        <div class="space-y-4">
          <!-- Manager Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Assign Manager</label>
            <div class="relative">
              <input 
                v-model="managerSearchQuery" 
                type="text" 
                placeholder="Search manager..." 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 mb-2"
              />
              <select 
                v-model="assignForm.manager_id" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 bg-white"
                size="5"
              >
                <option value="">-- No Manager --</option>
                <option v-for="mgr in filteredManagers" :key="mgr.emp_id" :value="mgr.emp_id">
                  {{ mgr.name }} ({{ mgr.job_title }})
                </option>
              </select>
            </div>
          </div>
          
          <!-- Training Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Assign Training</label>
            <select 
              v-model="assignForm.training_id" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 bg-white"
            >
              <option value="">-- Select Training --</option>
              <option v-for="training in trainings" :key="training.training_id" :value="training.training_id">
                {{ training.title }}
              </option>
            </select>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button 
            @click="closeAssignModal"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="submitAssignment"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/config/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isHR = computed(() => {
  const role = authStore.user?.role?.toLowerCase()
  return role === 'hr' || role === 'hr manager'
})

const isManager = computed(() => {
  if (!authStore.user?.job_title) return false
  const title = authStore.user.job_title.toLowerCase()
  return title.includes('manager') || 
         title.includes('head') || 
         title.includes('chief') || 
         title.includes('lead')
})

const employees = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedDept = ref('')
const showRateModal = ref(false)
const showAddModal = ref(false)
const selectedEmployee = ref(null)
const ratingForm = ref({
  score: 1,
  comment: ''
})

const addEmployeeForm = ref({
  name: '',
  email: '',
  password: '',
  job_title: '',
  department: '',
  hire_date: ''
})

// Computed properties for filtering
const departments = computed(() => {
  const depts = new Set(employees.value.map(e => e.department).filter(Boolean))
  return Array.from(depts).sort()
})

const filteredEmployees = computed(() => {
  return employees.value.filter(emp => {
    // Filter by manager if user is a manager (and not HR)
    if (isManager.value && !isHR.value) {
      if (emp.manager_id !== authStore.user?.emp_id) {
        return false
      }
    }

    const matchesSearch = (
      emp.name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      emp.email?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      emp.job_title?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    const matchesDept = !selectedDept.value || emp.department === selectedDept.value
    
    return matchesSearch && matchesDept
  })
})

// Methods
function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

async function fetchEmployees() {
  loading.value = true
  try {
    const response = await apiClient.get('/api/employees')
    employees.value = response.data.employees
  } catch (error) {
    console.error('Failed to fetch employees:', error)
  } finally {
    loading.value = false
  }
}

async function openRateModal(emp) {
  try {
    const response = await apiClient.get(`/api/performance/can-rate/${emp.emp_id}`)
    if (!response.data.can_rate) {
      alert(response.data.message)
      return
    }
    
    selectedEmployee.value = emp
    ratingForm.value = { score: 1, comment: '' }
    showRateModal.value = true
  } catch (error) {
    console.error('Failed to check rating eligibility:', error)
    alert('Failed to check rating eligibility')
  }
}

function closeRateModal() {
  showRateModal.value = false
  selectedEmployee.value = null
}

async function confirmRating() {
  if (!ratingForm.value.score) {
    alert('Please enter a score')
    return
  }
  
  if (!confirm('Are you sure you want to submit this rating?')) {
    return
  }
  
  try {
    await apiClient.post('/api/performance/log', {
      emp_id: selectedEmployee.value.emp_id,
      score: ratingForm.value.score,
      type: 'HR_Manual',
      comment: ratingForm.value.comment || 'HR Manual Entry'
    })
    
    alert('Performance rated successfully!')
    closeRateModal()
    fetchEmployees() // Refresh list to update scores
  } catch (error) {
    console.error('Failed to submit rating:', error)
    const msg = error.response?.data?.error || 'Failed to submit rating'
    alert(msg)
  }
}

function openAddModal() {
  addEmployeeForm.value = {
    name: '',
    email: '',
    password: '',
    job_title: '',
    department: '',
    hire_date: new Date().toISOString().split('T')[0]
  }
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
}

async function submitAddEmployee() {
  try {
    await apiClient.post('/api/employees/add', addEmployeeForm.value)
    alert('Employee added successfully!')
    closeAddModal()
    fetchEmployees() // Refresh list
  } catch (error) {
    console.error('Failed to add employee:', error)
    alert(error.response?.data?.error || 'Failed to add employee')
  }
}

// Assign Feature
const showAssignModal = ref(false)
const trainings = ref([])
const potentialManagers = ref([])
const managerSearchQuery = ref('')
const assignForm = ref({
  manager_id: '',
  training_id: ''
})

const filteredManagers = computed(() => {
  if (!managerSearchQuery.value) return potentialManagers.value
  const query = managerSearchQuery.value.toLowerCase()
  return potentialManagers.value.filter(m => 
    m.name.toLowerCase().includes(query) || 
    m.email.toLowerCase().includes(query)
  )
})

async function fetchTrainings() {
  try {
    const response = await apiClient.get('/api/trainings')
    trainings.value = response.data.trainings
  } catch (error) {
    console.error('Failed to fetch trainings:', error)
  }
}

function openAssignModal(emp) {
  selectedEmployee.value = emp
  // Potential managers are all employees except the selected one
  potentialManagers.value = employees.value.filter(e => e.emp_id !== emp.emp_id)
  
  assignForm.value = {
    manager_id: emp.manager_id || '',
    training_id: ''
  }
  managerSearchQuery.value = ''
  showAssignModal.value = true
}

function closeAssignModal() {
  showAssignModal.value = false
  selectedEmployee.value = null
}

async function submitAssignment() {
  try {
    await apiClient.post('/api/employees/assign', {
      emp_id: selectedEmployee.value.emp_id,
      manager_id: assignForm.value.manager_id,
      training_id: assignForm.value.training_id
    })
    
    alert('Assignment updated successfully!')
    closeAssignModal()
    fetchEmployees() // Refresh list to show updated manager
  } catch (error) {
    console.error('Failed to update assignment:', error)
    alert(error.response?.data?.error || 'Failed to update assignment')
  }
}

onMounted(() => {
  fetchEmployees()
  fetchTrainings()
})
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";
</style>
