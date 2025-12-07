<template>
  <div class="flex gap-6 h-[calc(100vh-8rem)]">
    <!-- Sidebar -->
    <div class="w-1/3 bg-white rounded-lg border border-gray-200 shadow-sm flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-200 bg-gray-50">
        <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2">
          <i class="fas fa-briefcase text-indigo-600"></i>
          Jobs
        </h2>
        <button 
          @click="createNewJob"
          class="mt-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
        >
          <i class="fas fa-plus"></i> New Job
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 space-y-2">
        <div v-if="isLoadingHistory" class="text-center py-4 text-gray-500">
          <i class="fas fa-circle-notch animate-spin"></i> Loading...
        </div>
        <div v-else-if="jobHistory.length === 0" class="text-gray-500 text-sm text-center py-4">
          No jobs found.
        </div>
        <div 
          v-for="job in jobHistory" 
          :key="job.job_id"
          @click="loadJob(job)"
          :class="['p-3 rounded-lg cursor-pointer transition-all border group', selectedJobId === job.job_id ? 'bg-indigo-50 border-indigo-200 shadow-sm' : 'bg-white border-transparent hover:bg-gray-50 hover:border-gray-200']"
        >
          <div class="font-medium text-gray-800 group-hover:text-indigo-700 truncate">{{ job.title || 'Untitled Job' }}</div>
          <div class="text-xs text-gray-500 flex justify-between mt-2 items-center">
            <span>{{ formatDate(job.created_at) }}</span>
            <div class="flex gap-2 items-center">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-medium', job.status === 'Open' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600']">
                {{ job.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="w-2/3 bg-white rounded-lg border border-gray-200 shadow-sm flex flex-col overflow-hidden">
      <div class="flex-1 overflow-y-auto p-8">
        <div class="mb-8">
          <h1 class="text-2xl font-bold text-gray-900">{{ isEditing ? 'Edit Job' : 'Create New Job' }}</h1>
          <p class="text-gray-600 mt-1">
            🤖 Just provide the job title and experience level - AI will generate everything else!
          </p>
        </div>

        <JobPromptForm v-model="jobData" />

        <!-- Action Buttons -->
        <div class="mt-8 flex justify-end gap-4">
          <button 
            v-if="isEditing"
            @click="createNewJob"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
          >
            Cancel
          </button>
          <button 
            @click="generateJob"
            :disabled="isGenerating || !canGenerate"
            class="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <i v-if="isGenerating" class="fas fa-circle-notch animate-spin"></i>
            <i v-else class="fas fa-magic"></i>
            {{ isGenerating ? 'AI is working...' : (isEditing ? 'Regenerate with AI' : 'Generate with AI') }}
          </button>
        </div>

        <!-- Generated Output Preview -->
        <div v-if="generatedContent" class="mt-12 border-t border-gray-200 pt-8">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-gray-900">Generated Preview</h2>
            <div class="flex gap-2">
              <button 
                v-if="selectedJobId"
                @click="deleteJob"
                class="px-4 py-2 border border-red-300 text-red-700 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors shadow-sm flex items-center gap-2"
              >
                <i class="fas fa-trash"></i>
                Delete
              </button>

              <button 
                v-if="selectedJobId && currentJobStatus === 'Open'"
                @click="closeJob"
                class="px-4 py-2 border border-orange-300 text-orange-700 rounded-lg text-sm font-medium hover:bg-orange-50 transition-colors shadow-sm flex items-center gap-2"
              >
                <i class="fas fa-ban"></i>
                Close Job
              </button>

              <button 
                v-if="!selectedJobId || (currentJobStatus === 'Draft' || currentJobStatus === 'On Hold')"
                @click="saveDraft"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors shadow-sm flex items-center gap-2"
              >
                <i class="fas fa-save"></i>
                Save Draft
              </button>
              
              <button 
                v-if="selectedJobId && (currentJobStatus === 'Draft' || currentJobStatus === 'On Hold')"
                @click="finalizeJob"
                class="px-4 py-2 bg-yellow-500 text-white rounded-lg text-sm font-medium hover:bg-yellow-600 transition-colors shadow-sm flex items-center gap-2"
              >
                <i class="fas fa-file-signature"></i>
                Finalize
              </button>

              <button 
                v-if="selectedJobId && (currentJobStatus === 'On Hold' || currentJobStatus === 'Draft')"
                @click="handlePostFromPreview"
                class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors shadow-sm flex items-center gap-2"
              >
                <i class="fas fa-check-circle"></i>
                Post Job
              </button>
            </div>
          </div>
          <div 
            class="bg-white p-8 rounded-xl shadow-sm border border-gray-200 prose max-w-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow"
            contenteditable="true"
            @input="handleContentEdit"
            ref="previewContainer"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, computed } from 'vue'
import axios from 'axios'
import JobPromptForm from '../components/JobPromptForm.vue'

const apiClient = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
})

// SIMPLIFIED Default Form Data - AI will infer the rest!
const defaultJobData = {
  // Essential fields (user provides)
  jobTitle: '',
  seniority: 'Mid-Level',
  minExperience: '',
  city: '',
  location: 'Hybrid',
  salaryRange: '',
  quantity: 1,
  
  // Optional advanced fields
  mustHaveSkills: [],
  niceToHaveSkills: [],
  specialRequirements: '',
  tone: 'Startup-friendly',
  employmentType: 'Full-Time',
  
  // Auto-filled company context (hidden from user)
  companyName: 'Acme Inc',
  coreMission: 'To revolutionize the e-commerce experience by delivering seamless, personalized shopping journeys that connect millions of customers with the products they love. We leverage cutting-edge technology and data-driven insights to build the future of online retail.',
  companyBlurb: 'Acme is a leading e-commerce platform transforming how people discover, evaluate, and purchase products online. With a customer-obsessed culture and commitment to innovation, we operate at the intersection of technology, logistics, and retail to deliver exceptional experiences at scale. Our diverse, world-class team is building solutions that shape the future of commerce for millions of users worldwide.',
  field: 'E-Commerce',
  companySize: '120',
  benefits: [
    "Competitive Compensation with Equity & Performance Bonuses",
    "Comprehensive Health & Wellness Benefits",
    "Flexible Work Options & Generous Time Off",
    "Career Growth with Learning & Development Support",
    "Direct Impact on Millions of Customers Worldwide",
    "Cutting-Edge Technology & Innovation-Driven Culture"
  ]
}

const jobData = reactive({ ...defaultJobData })
const jobHistory = ref([])
const isLoadingHistory = ref(false)
const isGenerating = ref(false)
const generatedContent = ref('')
const selectedJobId = ref(null)
const isEditing = ref(false)
const currentJobStatus = ref('Draft')
const previewContainer = ref(null)

// Computed property to check if we can generate
const canGenerate = computed(() => {
  return jobData.jobTitle && jobData.jobTitle.trim().length > 0
})

function handleContentEdit(event) {
  generatedContent.value = event.target.innerHTML
}

// Watch for changes in generatedContent to update the DOM
watch(generatedContent, async (newContent) => {
  await nextTick()
  if (previewContainer.value && previewContainer.value.innerHTML !== newContent) {
     if (document.activeElement !== previewContainer.value) {
        previewContainer.value.innerHTML = newContent
     }
  }
})

async function updateJobContent(status = null) {
  if (!selectedJobId.value) return
  
  try {
    const payload = {
      jd_text: generatedContent.value
    }
    
    if (status) {
      payload.status = status
    }
    
    await apiClient.put(`/api/jobs/${selectedJobId.value}`, payload)
    
    if (status) {
      currentJobStatus.value = status
    }
    
    await fetchJobHistory()
    return true
  } catch (error) {
    console.error('Error updating job:', error)
    alert('Failed to update job.')
    return false
  }
}

async function fetchJobHistory() {
  isLoadingHistory.value = true
  try {
    const response = await apiClient.get('/api/jobs')
    jobHistory.value = response.data.jobs
  } catch (error) {
    console.error('Error fetching job history:', error)
  } finally {
    isLoadingHistory.value = false
  }
}

function createNewJob() {
  selectedJobId.value = null
  isEditing.value = false
  generatedContent.value = ''
  Object.assign(jobData, defaultJobData)
  // Reset arrays specifically to ensure reactivity
  jobData.mustHaveSkills = []
  jobData.niceToHaveSkills = []
  jobData.benefits = [...defaultJobData.benefits]
}

function loadJob(job) {
  selectedJobId.value = job.job_id
  currentJobStatus.value = job.status || 'Draft'
  isEditing.value = true
  
  if (job.input_data) {
    // Load full saved data
    Object.assign(jobData, job.input_data)
    
    // Ensure arrays exist
    jobData.mustHaveSkills = jobData.mustHaveSkills || []
    jobData.niceToHaveSkills = jobData.niceToHaveSkills || []
    jobData.benefits = jobData.benefits || [...defaultJobData.benefits]
  } else {
    // Legacy Job: Map available fields
    console.log('Loading legacy job data...')
    Object.assign(jobData, defaultJobData) // Start with defaults
    
    jobData.jobTitle = job.title || ''
    jobData.location = job.location || 'Hybrid'
    jobData.employmentType = job.employment_type || 'Full-Time'
    jobData.salaryRange = job.salary_range || ''
    jobData.quantity = job.quantity || 1
    
    // Try to map requirements if available
    if (job.requirements && Array.isArray(job.requirements)) {
      jobData.mustHaveSkills = job.requirements
    }
  }
  
  // Load generated content if available
  if (job.jd_text) {
    generatedContent.value = job.jd_text
  }
}

async function generateJob() {
  // Simplified validation - only job title required!
  if (!jobData.jobTitle || !jobData.jobTitle.trim()) {
    alert('Please enter a job title.')
    return
  }

  isGenerating.value = true
  try {
    const payload = { ...jobData }
    
    // Clean up empty arrays to let AI infer
    if (payload.mustHaveSkills.length === 0 || payload.mustHaveSkills.every(s => !s.trim())) {
      delete payload.mustHaveSkills
    }
    if (payload.niceToHaveSkills.length === 0 || payload.niceToHaveSkills.every(s => !s.trim())) {
      delete payload.niceToHaveSkills
    }
    
    if (isEditing.value && selectedJobId.value) {
      payload.job_id = selectedJobId.value
    }
    
    const response = await apiClient.post('/api/policy/generate/job', payload)
    generatedContent.value = response.data.html
    
    // Refresh history to show the new/updated job
    await fetchJobHistory()
    
    // If we just created a new job, select it
    if (!isEditing.value && response.data.job_id) {
      const newJob = jobHistory.value.find(j => j.job_id === response.data.job_id)
      if (newJob) {
        loadJob(newJob)
      }
    }
  } catch (error) {
    console.error('Error generating job:', error)
    const errorMsg = error.response?.data?.error || 'Failed to generate job description.'
    alert(errorMsg)
  } finally {
    isGenerating.value = false
  }
}

async function saveDraft() {
  if (selectedJobId.value) {
    // Job already exists - update content and ensure status is Draft
    const success = await updateJobContent('Draft')
    if (success) {
      alert('Draft saved successfully!')
    }
  } else {
    // New job - generate it as a draft
    await generateJob()
    if (selectedJobId.value) { // Only show alert if generation succeeded
      alert('Draft created successfully!')
    }
  }
}

async function finalizeJob() {
  if (!selectedJobId.value) return
  
  if (!confirm('Are you sure you want to finalize this draft? It will be set to "On Hold".')) return

  const success = await updateJobContent('On Hold')
  if (success) {
    alert('Job finalized and set to On Hold.')
  }
}

async function closeJob() {
  if (!selectedJobId.value) return
  
  if (!confirm('Are you sure you want to close this job? It will be set to "On Hold".')) return

  const success = await updateJobContent('On Hold')
  if (success) {
    alert('Job closed and set to On Hold.')
  }
}

async function deleteJob() {
  if (!selectedJobId.value) return
  
  if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) return

  try {
    await apiClient.delete(`/api/jobs/${selectedJobId.value}`)
    alert('Job deleted successfully.')
    createNewJob() // Reset form
    await fetchJobHistory()
  } catch (error) {
    console.error('Error deleting job:', error)
    alert('Failed to delete job.')
  }
}

async function postJob(job) {
  if (!confirm(`Are you sure you want to post "${job.title}"? This will make it visible to candidates.`)) return
  
  try {
    // If we are posting the currently selected job, update its content first
    if (selectedJobId.value === job.job_id) {
       await updateJobContent('Open')
    } else {
       await apiClient.post(`/api/jobs/${job.job_id}/post`)
    }
    
    job.status = 'Open'
    alert('Job posted successfully!')
    await fetchJobHistory()
  } catch (error) {
    console.error('Error posting job:', error)
    alert('Failed to post job.')
  }
}

function handlePostFromPreview() {
  if (!selectedJobId.value) {
    alert('Please generate the job first to save it.')
    return
  }
  
  const job = jobHistory.value.find(j => j.job_id === selectedJobId.value)
  if (job) {
    postJob(job)
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchJobHistory()
})
</script>