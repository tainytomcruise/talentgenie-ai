<template>
  <div class="p-6 bg-gray-50 min-h-full">
    <div class="max-w-3xl mx-auto">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-800">Details</h1>
        <p class="text-gray-600">Manage your information</p>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Date of Birth</h2>
        
        <div v-if="isLoading" class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>

        <div v-else>
          <div v-if="existingDob" class="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <p class="text-gray-700">
              Your Date of Birth is set to: 
              <span class="font-bold text-indigo-600">{{ formatDate(existingDob) }}</span>
            </p>
            <p class="text-sm text-gray-500 mt-2">
              <i class="fas fa-lock mr-1"></i> This field cannot be modified. Please contact HR for any corrections.
            </p>
          </div>

          <div v-else>
            <p class="text-sm text-gray-600 mb-4">Please enter your Date of Birth. <strong>Note: This can only be set once.</strong></p>
            
            <div class="flex gap-4 mb-6">
              <div class="w-24">
                <label class="block text-xs font-medium text-gray-500 mb-1">Day</label>
                <input 
                  v-model="day" 
                  type="text" 
                  placeholder="DD" 
                  maxlength="2"
                  class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-center"
                  @input="validateNumber($event, 'day', 31)"
                >
              </div>
              <div class="w-24">
                <label class="block text-xs font-medium text-gray-500 mb-1">Month</label>
                <input 
                  v-model="month" 
                  type="text" 
                  placeholder="MM" 
                  maxlength="2"
                  class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-center"
                  @input="validateNumber($event, 'month', 12)"
                >
              </div>
              <div class="w-32">
                <label class="block text-xs font-medium text-gray-500 mb-1">Year</label>
                <input 
                  v-model="year" 
                  type="text" 
                  placeholder="YYYY" 
                  maxlength="4"
                  class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-center"
                  @input="validateNumber($event, 'year', new Date().getFullYear())"
                >
              </div>
            </div>

            <div v-if="error" class="text-red-500 text-sm mb-4">
              {{ error }}
            </div>

            <button 
              @click="saveDob" 
              :disabled="!isValidDate"
              class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Save Date of Birth
            </button>
          </div>
        </div>
      </div>

      <!-- Skills Section -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Skills & Expertise</h2>
        
        <div class="mb-6">
          <div class="flex gap-2 mb-4">
            <input 
              v-model="newSkill" 
              @keyup.enter="addSkill"
              type="text" 
              placeholder="Add a new skill (e.g. Python, Leadership)" 
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <button 
              @click="addSkill"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
            >
              <i class="fas fa-plus"></i> Add
            </button>
          </div>

          <div class="flex flex-wrap gap-2">
            <div 
              v-for="(skill, index) in skills" 
              :key="index"
              class="group relative px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-100 flex items-center gap-2 transition-all hover:bg-indigo-100"
            >
              <span v-if="editingIndex !== index" @click="startEditing(index)" class="cursor-pointer">{{ skill }}</span>
              <input 
                v-else
                v-model="editingSkill"
                @blur="saveEdit(index)"
                @keyup.enter="saveEdit(index)"
                ref="editInput"
                class="w-24 px-1 py-0 bg-white border border-indigo-300 rounded text-sm focus:outline-none focus:border-indigo-500"
              />
              
              <button 
                @click="removeSkill(index)"
                class="text-indigo-400 hover:text-red-500 transition-colors"
                title="Remove skill"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div v-if="skills.length === 0" class="text-gray-400 italic text-sm py-2">
              No skills added yet. Add your key skills above!
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog Removed -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/config/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isLoading = ref(true)
const existingDob = ref(null)
const day = ref('')
const month = ref('')
const year = ref('')
const error = ref('')

const isValidDate = computed(() => {
  if (!day.value || !month.value || !year.value) return false
  const d = parseInt(day.value)
  const m = parseInt(month.value)
  const y = parseInt(year.value)
  
  if (isNaN(d) || isNaN(m) || isNaN(y)) return false
  if (y < 1900 || y > new Date().getFullYear()) return false
  if (m < 1 || m > 12) return false
  
  const date = new Date(y, m - 1, d)
  return date.getDate() === d && date.getMonth() === m - 1 && date.getFullYear() === y
})

const validateNumber = (event, field, max) => {
  let value = event.target.value.replace(/\D/g, '')
  if (value && parseInt(value) > max && field !== 'year') {
    value = max.toString()
  }
  
  if (field === 'day') day.value = value
  if (field === 'month') month.value = value
  if (field === 'year') year.value = value
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const skills = ref([])
const newSkill = ref('')
const editingIndex = ref(-1)
const editingSkill = ref('')
const editInput = ref(null)

const fetchProfile = async () => {
  isLoading.value = true
  try {
    const response = await apiClient.get('/api/employee/personal-details')
    if (response.data.dob) {
      existingDob.value = response.data.dob
    }
    if (response.data.skills) {
      skills.value = response.data.skills
    }
  } catch (err) {
    console.error('Error fetching profile:', err)
  } finally {
    isLoading.value = false
  }
}

const saveDob = async () => {
  error.value = ''
  if (!isValidDate.value) {
    error.value = 'Please enter a valid date.'
    return
  }

  if (!window.confirm(`Are you sure you want to set your Date of Birth to ${day.value}/${month.value}/${year.value}?\n\nThis cannot be modified later.`)) {
    return
  }

  isLoading.value = true
  
  try {
    // Format YYYY-MM-DD
    const dob = `${year.value}-${month.value.padStart(2, '0')}-${day.value.padStart(2, '0')}`
    
    await apiClient.put('/api/employee/personal-details', { dob })
    
    existingDob.value = dob
  } catch (err) {
    console.error('Error saving DOB:', err)
    error.value = err.response?.data?.message || 'Failed to save Date of Birth.'
  } finally {
    isLoading.value = false
  }
}

// Skills Management
const updateSkills = async (newSkillsList) => {
  try {
    await apiClient.put('/api/employee/personal-details', { skills: newSkillsList })
    skills.value = newSkillsList
  } catch (err) {
    console.error('Error updating skills:', err)
    alert('Failed to update skills')
  }
}

const addSkill = async () => {
  const skill = newSkill.value.trim()
  if (!skill) return
  
  if (skills.value.includes(skill)) {
    alert('This skill is already added!')
    return
  }
  
  const updatedSkills = [...skills.value, skill]
  await updateSkills(updatedSkills)
  newSkill.value = ''
}

const removeSkill = async (index) => {
  if (!confirm('Remove this skill?')) return
  
  const updatedSkills = skills.value.filter((_, i) => i !== index)
  await updateSkills(updatedSkills)
}

const startEditing = (index) => {
  editingIndex.value = index
  editingSkill.value = skills.value[index]
  // Focus input next tick
  setTimeout(() => {
    if (editInput.value && editInput.value[0]) {
      editInput.value[0].focus()
    }
  }, 0)
}

const saveEdit = async (index) => {
  if (editingIndex.value === -1) return
  
  const skill = editingSkill.value.trim()
  if (!skill) {
    // If empty, cancel edit
    editingIndex.value = -1
    return
  }
  
  // Check duplicate if changed
  if (skill !== skills.value[index] && skills.value.includes(skill)) {
    alert('This skill already exists!')
    return
  }
  
  const updatedSkills = [...skills.value]
  updatedSkills[index] = skill
  
  await updateSkills(updatedSkills)
  editingIndex.value = -1
}

onMounted(() => {
  fetchProfile()
})
</script>
