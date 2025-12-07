<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Header -->
    <header class="bg-white shadow-sm z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg p-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <span class="text-xl font-bold text-gray-800">TalentGenie <span class="text-purple-600 text-sm font-medium">Candidate Portal</span></span>
        </div>
        <button @click="logout" class="text-gray-500 hover:text-red-600 transition-colors">
          <i class="fas fa-sign-out-alt mr-1"></i> Sign Out
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 py-8 max-w-5xl">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <!-- Left Column: Job Selection -->
        <div class="md:col-span-1 space-y-6">
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Open Positions</h2>
            <p class="text-sm text-gray-500 mb-4">Select a role to view details and apply.</p>
            
            <div class="space-y-3">
              <div 
                v-for="job in jobs" 
                :key="job.id"
                @click="selectedJob = job"
                :class="['p-4 rounded-lg cursor-pointer transition-all border', selectedJob?.id === job.id ? 'bg-purple-50 border-purple-200 shadow-sm' : 'bg-gray-50 border-transparent hover:bg-gray-100']"
              >
                <h3 class="font-medium text-gray-900">{{ job.title }}</h3>
                <p class="text-xs text-gray-500 mt-1">{{ job.location }} • {{ job.type }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Job Details & Application -->
        <div class="md:col-span-2">
          <div v-if="selectedJob" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <!-- Job Header -->
            <div class="p-6 border-b border-gray-100 bg-gray-50/50">
              <h1 class="text-2xl font-bold text-gray-900">{{ selectedJob.title }}</h1>
              <div class="flex gap-4 mt-2 text-sm text-gray-600">
                <span class="flex items-center gap-1"><i class="fas fa-map-marker-alt text-gray-400"></i> {{ selectedJob.location }}</span>
                <span class="flex items-center gap-1"><i class="fas fa-clock text-gray-400"></i> {{ selectedJob.type }}</span>
                <span class="flex items-center gap-1"><i class="fas fa-dollar-sign text-gray-400"></i> {{ selectedJob.salary }}</span>
              </div>
            </div>

            <!-- Job Description -->
            <div class="p-6 space-y-6">
              <div>
                <h3 class="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2">About the Role</h3>
                <div class="text-gray-600 leading-relaxed prose" v-html="selectedJob.full_description"></div>
              </div>

              <hr class="border-gray-100" />

              <!-- Application Form -->
              <div class="bg-purple-50 rounded-xl p-6 border border-purple-100">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Apply for this position</h3>
                
                <div v-if="selectedJob.has_applied">
                  <div class="text-center py-8">
                    <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <i class="fas fa-info-circle text-2xl text-blue-600"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-2">Application Status</h3>
                    
                    <div class="mt-4">
                      <span 
                        class="px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wide"
                        :class="{
                          'bg-blue-100 text-blue-700': selectedJob.application_status === 'Applied',
                          'bg-purple-100 text-purple-700': selectedJob.application_status === 'Screening',
                          'bg-orange-100 text-orange-700': selectedJob.application_status === 'Interview',
                          'bg-green-100 text-green-700': selectedJob.application_status === 'Hired',
                          'bg-red-100 text-red-700': selectedJob.application_status === 'Rejected'
                        }"
                      >
                        {{ selectedJob.application_status || 'Applied' }}
                      </span>
                    </div>
                    
                    <p class="text-gray-600 mt-4">
                      {{ getStatusMessage(selectedJob.application_status) }}
                    </p>
                  </div>
                </div>
                
                <div v-else-if="!submitted">

                  <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Upload Resume / CV</label>
                    <div 
                      class="border-2 border-dashed border-purple-200 rounded-lg p-6 text-center hover:bg-white transition-colors cursor-pointer"
                      @click="$refs.fileInput.click()"
                    >
                      <input 
                        type="file" 
                        ref="fileInput" 
                        class="hidden" 
                        accept=".pdf,.doc,.docx"
                        @change="handleFileUpload"
                      />
                      <i class="fas fa-cloud-upload-alt text-3xl text-purple-400 mb-2"></i>
                      <p class="text-sm text-gray-600 font-medium">{{ fileName || 'Click to upload or drag and drop' }}</p>
                      <p class="text-xs text-gray-400 mt-1">PDF, DOC, DOCX up to 5MB</p>
                    </div>
                  </div>

                  <button 
                    @click="submitApplication"
                    :disabled="!file || isSubmitting"
                    class="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg flex items-center justify-center gap-2"
                  >
                    <i v-if="isSubmitting" class="fas fa-circle-notch animate-spin"></i>
                    {{ isSubmitting ? 'Submitting...' : 'Submit Application' }}
                  </button>
                </div>

                <!-- Success Message -->
                <div v-else class="text-center py-8">
                  <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-check text-2xl text-green-600"></i>
                  </div>
                  <h3 class="text-xl font-bold text-gray-900 mb-2">Application Received</h3>
                  <p class="text-gray-600">Resume submitted. You will receive a call from the company. Thank you for applying.</p>
                  <button @click="resetForm" class="mt-6 text-purple-600 font-medium hover:text-purple-700">
                    Apply for another role
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="h-full flex flex-col items-center justify-center text-center p-12 bg-white rounded-xl border border-dashed border-gray-300 text-gray-400">
            <i class="fas fa-briefcase text-4xl mb-4 opacity-50"></i>
            <p class="text-lg font-medium">Select a position to view details</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const jobs = ref([])
const isLoading = ref(false)
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

async function fetchJobs() {
  isLoading.value = true
  try {
    const response = await apiClient.get('/api/jobs')
    // Filter for Open jobs and map to display format
    jobs.value = response.data.jobs
      .filter(job => job.status === 'Open')
      .map(job => ({
        id: job.job_id,
        title: job.title,
        location: job.location,
        type: job.employment_type,
        salary: job.salary_range,
        description: job.jd_text.replace(/<[^>]*>/g, '').substring(0, 200) + '...', // Simple strip tags for preview
        full_description: job.jd_text, // Keep full HTML for details
        has_applied: job.has_applied || false,
        application_status: job.application_status
      }))
  } catch (error) {
    console.error('Error fetching jobs:', error)
  } finally {
    isLoading.value = false
  }
}

import { onMounted } from 'vue'

onMounted(() => {
  fetchJobs()
})

const selectedJob = ref(null)
const file = ref(null)
const fileName = ref('')
const submitted = ref(false)

const isSubmitting = ref(false)

function handleFileUpload(event) {
  const uploadedFile = event.target.files[0]
  if (uploadedFile) {
    file.value = uploadedFile
    fileName.value = uploadedFile.name
  }
}

async function submitApplication() {
  if (!file.value) return
  
  isSubmitting.value = true
  
  try {
    const formData = new FormData()
    formData.append('files[]', file.value)
    formData.append('job_id', selectedJob.value.id)
    
    await apiClient.post('/api/recruitment/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    submitted.value = true
  } catch (error) {
    console.error('Error submitting application:', error)
    if (error.response && error.response.status === 409) {
      // Treat duplicate submission as success for user experience
      submitted.value = true
    } else {
      alert('Failed to submit application. Please try again.')
    }
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  submitted.value = false
  file.value = null
  fileName.value = ''
  // Keep selected job
}

function logout() {
  authStore.logout()
  router.push('/login')
}

function getStatusMessage(status) {
  switch(status) {
    case 'Applied': return "You have applied for this position. Please wait for a call from the company / HR.";
    case 'Screening': return "Your application is currently being reviewed by our team.";
    case 'Interview': return "You have been selected for an interview! Check your email for details.";
    case 'Hired': return "Congratulations! You have been selected for this role.";
    case 'Rejected': return "Thank you for your interest. Unfortunately, we have decided to move forward with other candidates.";
    default: return "You have applied for this position.";
  }
}
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";
</style>
