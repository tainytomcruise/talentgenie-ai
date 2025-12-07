<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 bg-slate-50 min-h-screen">
    
    <!-- Header -->
    <div class="relative overflow-hidden rounded-3xl bg-slate-900 text-white shadow-2xl">
      <div class="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-indigo-500 rounded-full blur-3xl opacity-20"></div>
      <div class="absolute bottom-0 left-0 -mb-10 -ml-10 w-64 h-64 bg-purple-500 rounded-full blur-3xl opacity-20"></div>
      
      <div class="relative z-10 p-8 sm:p-12 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <div class="flex items-center gap-3 mb-3">
            <h1 class="text-3xl font-extrabold tracking-tight">Pending Approvals</h1>
          </div>
          <p class="text-slate-400 max-w-xl text-lg">
            Review and activate pending employee accounts.
          </p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-4 border-b border-slate-200">
      <button 
        @click="activeTab = 'employees'"
        :class="['px-6 py-3 font-bold text-sm transition-colors border-b-2', activeTab === 'employees' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-700']"
      >
        Employee Approvals
        <span v-if="pendingEmployees.length > 0" class="ml-2 bg-red-100 text-red-600 px-2 py-0.5 rounded-full text-xs">{{ pendingEmployees.length }}</span>
      </button>
      <button 
        @click="activeTab = 'leaves'"
        :class="['px-6 py-3 font-bold text-sm transition-colors border-b-2', activeTab === 'leaves' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-700']"
      >
        Leave Requests
        <span v-if="pendingLeaves.length > 0" class="ml-2 bg-red-100 text-red-600 px-2 py-0.5 rounded-full text-xs">{{ pendingLeaves.length }}</span>
      </button>
    </div>

    <!-- Employee Approvals View -->
    <div v-if="activeTab === 'employees'" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Left Sidebar: Pending List -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
          <div class="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
            <h2 class="text-lg font-bold text-slate-800">Pending Requests</h2>
          </div>
          <div class="p-4 space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
            
            <div v-if="isLoadingPending" class="text-center py-8 text-slate-400">
              <i class="fas fa-circle-notch fa-spin text-2xl mb-2"></i>
              <p>Loading requests...</p>
            </div>
            <div v-else-if="pendingEmployees.length === 0" class="text-center py-8 text-slate-400">
              <p>No pending approvals.</p>
            </div>
            <div 
              v-for="emp in pendingEmployees" 
              :key="emp.user_id"
              @click="selectPendingEmployee(emp)"
              :class="['p-4 rounded-xl cursor-pointer transition-all border', selectedPending?.user_id === emp.user_id ? 'bg-amber-50 border-amber-200 shadow-md' : 'bg-white border-slate-100 hover:border-amber-100 hover:shadow-sm']"
            >
              <div class="flex justify-between items-start">
                <h3 class="font-bold text-slate-800">{{ emp.name }}</h3>
                <span class="bg-amber-100 text-amber-700 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">Pending</span>
              </div>
              <p class="text-xs text-slate-500 mt-1">{{ emp.email }}</p>
              <p class="text-[10px] text-slate-400 mt-2">Registered: {{ new Date(emp.created_at).toLocaleDateString() }}</p>
            </div>

          </div>
        </div>
      </div>

      <!-- Main Content: Approval Form -->
      <div class="lg:col-span-8 space-y-6">
        
        <div v-if="selectedPending" class="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden min-h-[600px] flex flex-col">
          <div class="p-8 border-b border-slate-100 bg-amber-50/30">
            <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
              <span class="w-10 h-10 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center text-lg"><i class="fas fa-user-check"></i></span>
              Approve Employee
            </h2>
            <p class="text-slate-500 mt-2 ml-14">Review and activate account for <span class="font-bold text-slate-800">{{ selectedPending.name }}</span></p>
          </div>
          
          <div class="p-8 space-y-6 max-w-2xl">
            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Full Name</label>
                <input type="text" :value="selectedPending.name" disabled class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 cursor-not-allowed">
              </div>
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Email Address</label>
                <input type="text" :value="selectedPending.email" disabled class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 cursor-not-allowed">
              </div>
            </div>

            <div class="border-t border-slate-100 my-6"></div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-2">Job Title <span class="text-red-500">*</span></label>
              <input v-model="approvalForm.job_title" type="text" placeholder="e.g. Senior Software Engineer" class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition">
            </div>

            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Department</label>
                <select v-model="approvalForm.dept_id" class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition bg-white">
                  <option value="" disabled>Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Annual Salary</label>
                <div class="relative">
                  <span class="absolute left-4 top-3.5 text-slate-400">$</span>
                  <input v-model="approvalForm.salary" type="number" placeholder="0.00" class="w-full pl-8 pr-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition">
                </div>
              </div>
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-2">Skills <span class="text-xs font-normal text-slate-400">(comma separated)</span></label>
              <input v-model="approvalForm.skills" type="text" placeholder="e.g. Python, Vue.js, SQL" class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition">
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-2">Assign Manager</label>
              <select v-model="approvalForm.manager_id" class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition bg-white">
                <option value="" disabled>Select Manager</option>
                <option v-for="mgr in managers" :key="mgr.emp_id" :value="mgr.emp_id">{{ mgr.name }} ({{ mgr.job_title }})</option>
              </select>
            </div>

            <div class="pt-6 flex gap-4">
              <button @click="approveEmployee" :disabled="isApproving" class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center gap-2">
                <i v-if="isApproving" class="fas fa-circle-notch fa-spin"></i>
                <span v-else><i class="fas fa-check-circle"></i> Approve & Activate</span>
              </button>
            </div>
          </div>
        </div>

        <div v-else class="bg-white rounded-2xl shadow-xl border border-slate-100 h-[600px] flex flex-col items-center justify-center text-slate-400">
          <i class="fas fa-user-clock text-5xl mb-4 opacity-30"></i>
          <p class="text-lg font-medium">Select a pending request to review</p>
        </div>
      </div>

    </div>

    <!-- Leave Requests View -->
    <div v-if="activeTab === 'leaves'" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Left Sidebar: Leave List -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
          <div class="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
            <h2 class="text-lg font-bold text-slate-800">Pending Leaves</h2>
          </div>
          <div class="p-4 space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
            
            <div v-if="isLoadingLeaves" class="text-center py-8 text-slate-400">
              <i class="fas fa-circle-notch fa-spin text-2xl mb-2"></i>
              <p>Loading leaves...</p>
            </div>
            <div v-else-if="pendingLeaves.length === 0" class="text-center py-8 text-slate-400">
              <p>No pending leave requests.</p>
            </div>
            <div 
              v-for="leave in pendingLeaves" 
              :key="leave.leave_id"
              @click="selectLeaveRequest(leave)"
              :class="['p-4 rounded-xl cursor-pointer transition-all border', selectedLeave?.leave_id === leave.leave_id ? 'bg-indigo-50 border-indigo-200 shadow-md' : 'bg-white border-slate-100 hover:border-indigo-100 hover:shadow-sm']"
            >
              <div class="flex justify-between items-start">
                <h3 class="font-bold text-slate-800">{{ leave.employee_name }}</h3>
                <span class="bg-indigo-100 text-indigo-700 text-[10px] px-2 py-0.5 rounded-full font-bold uppercase">{{ leave.leave_type }}</span>
              </div>
              <p class="text-xs text-slate-500 mt-1">{{ leave.start_date }} to {{ leave.end_date }}</p>
              <p class="text-[10px] text-slate-400 mt-2">Requested: {{ new Date(leave.created_at).toLocaleDateString() }}</p>
            </div>

          </div>
        </div>
      </div>

      <!-- Main Content: Leave Details -->
      <div class="lg:col-span-8 space-y-6">
        
        <div v-if="selectedLeave" class="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden min-h-[600px] flex flex-col">
          <div class="p-8 border-b border-slate-100 bg-indigo-50/30">
            <h2 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
              <span class="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-lg"><i class="fas fa-calendar-check"></i></span>
              Review Leave Request
            </h2>
            <p class="text-slate-500 mt-2 ml-14">Request from <span class="font-bold text-slate-800">{{ selectedLeave.employee_name }}</span></p>
          </div>
          
          <div class="p-8 space-y-6 max-w-2xl">
            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Leave Type</label>
                <div class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-medium">
                  {{ selectedLeave.leave_type }}
                </div>
              </div>
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Duration</label>
                <div class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700">
                  {{ selectedLeave.start_date }} <span class="text-slate-400 mx-2">to</span> {{ selectedLeave.end_date }}
                </div>
              </div>
            </div>

            <div>
              <label class="block text-sm font-bold text-slate-700 mb-2">Reason</label>
              <div class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 min-h-[100px]">
                {{ selectedLeave.reason }}
              </div>
            </div>

            <div class="pt-6 flex gap-4">
              <button @click="processLeave('Reject')" :disabled="isProcessingLeave" class="flex-1 bg-white border border-red-200 text-red-600 hover:bg-red-50 font-bold py-4 rounded-xl transition-all flex items-center justify-center gap-2">
                <i class="fas fa-times-circle"></i> Reject
              </button>
              <button @click="processLeave('Approve')" :disabled="isProcessingLeave" class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center gap-2">
                <i v-if="isProcessingLeave" class="fas fa-circle-notch fa-spin"></i>
                <span v-else><i class="fas fa-check-circle"></i> Approve Request</span>
              </button>
            </div>
          </div>
        </div>

        <div v-else class="bg-white rounded-2xl shadow-xl border border-slate-100 h-[600px] flex flex-col items-center justify-center text-slate-400">
          <i class="fas fa-calendar-day text-5xl mb-4 opacity-30"></i>
          <p class="text-lg font-medium">Select a leave request to review</p>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import apiClient from '@/config/axios'

// State
const activeTab = ref('employees') // 'employees' or 'leaves'
const pendingEmployees = ref([])
const pendingLeaves = ref([])
const isLoadingPending = ref(false)
const isLoadingLeaves = ref(false)
const selectedPending = ref(null)
const selectedLeave = ref(null)
const isApproving = ref(false)
const isProcessingLeave = ref(false)

const departments = ref([
    { id: 1, name: 'Engineering' },
    { id: 2, name: 'Human Resources' },
    { id: 3, name: 'Sales' },
    { id: 4, name: 'Marketing' }
]) 

const managers = ref([])
const approvalForm = ref({
    job_title: '',
    dept_id: '',
    salary: '',
    skills: '',
    manager_id: ''
})

// Fetch Pending Employees
const fetchPendingEmployees = async () => {
  isLoadingPending.value = true
  try {
    const response = await apiClient.get('/api/employees/pending')
    pendingEmployees.value = response.data.pending_employees
  } catch (error) {
    console.error('Error fetching pending employees:', error)
  } finally {
    isLoadingPending.value = false
  }
}

// Fetch Pending Leaves
const fetchPendingLeaves = async () => {
  isLoadingLeaves.value = true
  try {
    const response = await apiClient.get('/api/hr/leave/requests')
    pendingLeaves.value = response.data.leave_requests
  } catch (error) {
    console.error('Error fetching pending leaves:', error)
  } finally {
    isLoadingLeaves.value = false
  }
}

// Fetch Managers (Employees)
const fetchManagers = async () => {
  try {
    const response = await apiClient.get('/api/employees')
    managers.value = response.data.employees
  } catch (error) {
    console.error('Error fetching managers:', error)
  }
}

// Select Pending Employee
const selectPendingEmployee = (emp) => {
    selectedPending.value = emp
    approvalForm.value = {
        job_title: '',
        dept_id: '',
        salary: '',
        skills: '',
        manager_id: ''
    }
}

// Select Leave Request
const selectLeaveRequest = (leave) => {
    selectedLeave.value = leave
}

// Approve Employee
const approveEmployee = async () => {
    if (!approvalForm.value.job_title) {
        alert('Please fill in Job Title')
        return
    }
    
    isApproving.value = true
    try {
        const skillsArray = approvalForm.value.skills ? approvalForm.value.skills.split(',').map(s => s.trim()).filter(s => s) : []
        
        await apiClient.post('/api/employees/approve', {
            user_id: selectedPending.value.user_id,
            ...approvalForm.value,
            skills: skillsArray
        })
        alert('Employee approved successfully!')
        await fetchPendingEmployees()
        selectedPending.value = null
    } catch (error) {
        console.error('Error approving employee:', error)
        alert('Failed to approve employee')
    } finally {
        isApproving.value = false
    }
}

// Process Leave Request
const processLeave = async (action) => {
    if (!selectedLeave.value) return
    
    isProcessingLeave.value = true
    try {
        await apiClient.post('/api/hr/leave/action', {
            leave_id: selectedLeave.value.leave_id,
            action: action
        })
        alert(`Leave request ${action}ed successfully!`)
        await fetchPendingLeaves()
        selectedLeave.value = null
    } catch (error) {
        console.error(`Error ${action}ing leave:`, error)
        alert(`Failed to ${action} leave request`)
    } finally {
        isProcessingLeave.value = false
    }
}

onMounted(() => {
  fetchPendingEmployees()
  fetchPendingLeaves()
  fetchManagers()
})
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
</style>
