<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 bg-slate-50 min-h-screen">
    
    <!-- Header -->
    <div class="relative overflow-hidden rounded-3xl bg-slate-900 text-white shadow-2xl">
      <div class="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-indigo-500 rounded-full blur-3xl opacity-20"></div>
      <div class="absolute bottom-0 left-0 -mb-10 -ml-10 w-64 h-64 bg-purple-500 rounded-full blur-3xl opacity-20"></div>
      
      <div class="relative z-10 p-8 sm:p-12 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <div class="flex items-center gap-3 mb-3">
            <h1 class="text-3xl font-extrabold tracking-tight">Recruitment Dashboard</h1>
          </div>
          <p class="text-slate-400 max-w-xl text-lg">
            Manage open positions, review ranked candidates, and prepare for interviews.
          </p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Left Sidebar: Job List -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden">
          <div class="p-6 border-b border-slate-100 bg-slate-50/50">
            <h2 class="text-lg font-bold text-slate-800">Open Positions</h2>
          </div>
          <div class="p-4 space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
            
            <div v-if="isLoadingJobs" class="text-center py-8 text-slate-400">
              <i class="fas fa-circle-notch fa-spin text-2xl mb-2"></i>
              <p>Loading jobs...</p>
            </div>
            <div v-else-if="jobs.length === 0" class="text-center py-8 text-slate-400">
              <p>No open jobs found.</p>
            </div>
            <div 
              v-for="job in jobs" 
              :key="job.id"
              @click="selectJob(job)"
              :class="['p-4 rounded-xl cursor-pointer transition-all border', selectedJob?.id === job.id ? 'bg-indigo-50 border-indigo-200 shadow-md' : 'bg-white border-slate-100 hover:border-indigo-100 hover:shadow-sm']"
            >
              <h3 class="font-bold text-slate-800">{{ job.title }}</h3>
              <div class="flex items-center gap-2 mt-2 text-xs text-slate-500">
                <span class="bg-slate-100 px-2 py-1 rounded">{{ job.location }}</span>
                <span class="bg-slate-100 px-2 py-1 rounded">{{ job.type }}</span>
              </div>
            </div>


          </div>
        </div>
      </div>

      <!-- Main Content: Job Details & Candidates -->
      <div class="lg:col-span-8 space-y-6">
        

        <!-- JOB DETAILS (Existing) -->
        <div v-if="selectedJob" class="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden min-h-[600px] flex flex-col">
          
          <!-- Tabs -->
          <div class="flex border-b border-slate-100">
            <button 
              @click="activeTab = 'candidates'"
              :class="['flex-1 py-4 text-sm font-bold uppercase tracking-wider transition-colors', activeTab === 'candidates' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/30' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50']"
            >
              Candidates
            </button>
            <button 
              @click="activeTab = 'jd'"
              :class="['flex-1 py-4 text-sm font-bold uppercase tracking-wider transition-colors', activeTab === 'jd' ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/30' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50']"
            >
              Job Description
            </button>
          </div>

          <!-- Tab Content -->
          <div class="p-6 flex-1 overflow-y-auto custom-scrollbar">
            
            <!-- Candidates Tab -->
            <div v-if="activeTab === 'candidates'" class="space-y-6">
              <div v-if="isLoadingApplicants" class="text-center py-12 text-slate-400">
                <i class="fas fa-circle-notch fa-spin text-3xl mb-3"></i>
                <p>Ranking candidates...</p>
              </div>
              
              <div v-else-if="applicants.length === 0" class="text-center py-12 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl">
                <i class="fas fa-users text-4xl mb-3 opacity-30"></i>
                <p>No candidates have applied yet.</p>
              </div>

              <div v-else class="space-y-4">
                <div 
                  v-for="(applicant, index) in applicants" 
                  :key="applicant.applicant_id"
                  class="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md transition-all group"
                >
                  <div class="flex justify-between items-start">
                    <div class="flex gap-4">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-md">
                        {{ applicant.name ? applicant.name.charAt(0) : '?' }}
                      </div>
                      <div>
                        <h4 class="font-bold text-slate-800 text-lg group-hover:text-indigo-600 transition-colors">
                          {{ applicant.name }}
                        </h4>
                        <div class="text-sm text-slate-500 space-y-0.5 mt-1">
                          <p><i class="fas fa-envelope w-4 text-center mr-1"></i> {{ applicant.email }}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div class="text-right flex items-center gap-4">
                      <div class="flex flex-col items-end">
                        <span class="text-2xl font-black"
                              :class="applicant.score >= 80 ? 'text-emerald-500' : applicant.score >= 60 ? 'text-amber-500' : 'text-red-500'">
                          {{ Math.round(applicant.score || 0) }}%
                        </span>
                        <span class="text-[10px] uppercase font-bold text-slate-400">Match Score</span>
                      </div>

                      <div class="flex flex-col items-end pl-4 border-l border-slate-100" v-if="applicant.q_and_a_scores && applicant.q_and_a_scores.length > 0">
                        <span class="text-xl font-bold text-indigo-600">
                           {{ (applicant.q_and_a_scores.reduce((a, b) => a + b, 0) / applicant.q_and_a_scores.length).toFixed(1) }}/10
                        </span>
                        <span class="text-[10px] uppercase font-bold text-slate-400">Interview Score</span>
                      </div>
                    </div>
                  </div>

                  <div class="mt-4 pt-4 border-t border-slate-100">
                    <p class="text-sm text-slate-600 mb-4 line-clamp-2">{{ applicant.summary }}</p>
                    
                    <div class="flex justify-between items-center">
                      <a 
                        v-if="applicant.resume_url"
                        :href="applicant.resume_url" 
                        target="_blank"
                        class="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                      >
                        <i class="fas fa-file-alt"></i> View Resume
                      </a>
                      
                      <button 
                        @click="generateQuestions(applicant)"
                        class="px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-2"
                      >
                        <i class="fas fa-comments"></i> Interview Q&A
                      </button>

                      <!-- Hire / Reject Actions (Only if Interviewed) -->
                      <div v-if="applicant.q_and_a_scores && applicant.q_and_a_scores.length > 0 && applicant.status !== 'Hired' && applicant.status !== 'Rejected'" class="flex gap-2">
                        <button 
                          @click="updateStatus(applicant, 'Hired')"
                          class="px-4 py-2 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                        >
                          <i class="fas fa-check"></i> Hire
                        </button>
                        <button 
                          @click="updateStatus(applicant, 'Rejected')"
                          class="px-4 py-2 bg-red-600 text-white text-xs font-bold rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                        >
                          <i class="fas fa-times"></i> Reject
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Job Description Tab -->
            <div v-else-if="activeTab === 'jd'" class="prose max-w-none text-slate-600">
              <div v-html="selectedJob.full_description"></div>
            </div>

          </div>
        </div>

        <div v-else class="bg-white rounded-2xl shadow-xl border border-slate-100 h-[600px] flex flex-col items-center justify-center text-slate-400">
          <i class="fas fa-briefcase text-5xl mb-4 opacity-30"></i>
          <p class="text-lg font-medium">Select a job to view details</p>
        </div>
      </div>

    </div>

    <!-- Interview Questions Modal -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showInterviewQuestions" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="showInterviewQuestions = false"></div>

        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden">
          
          <div class="px-8 py-6 bg-slate-900 text-white flex justify-between items-start">
            <div>
              <h3 class="text-2xl font-bold flex items-center gap-3">
                <i class="fas fa-comments text-indigo-400"></i> Interview Guide
              </h3>
              <div class="flex items-center gap-4 mt-1">
                <p class="text-slate-400 text-sm" v-if="selectedCandidate">
                  Tailored for <span class="text-white font-semibold">{{ selectedCandidate.name }}</span>
                </p>
                <div v-if="selectedCandidate && selectedCandidate.q_and_a_scores && selectedCandidate.q_and_a_scores.length > 0" 
                     class="px-3 py-1 bg-indigo-600/30 border border-indigo-500/30 rounded-full text-xs font-bold text-indigo-300">
                  Avg Score: {{ (selectedCandidate.q_and_a_scores.reduce((a, b) => a + b, 0) / selectedCandidate.q_and_a_scores.length).toFixed(1) }}/10
                </div>
              </div>
            </div>
            <button @click="showInterviewQuestions = false" class="text-white/50 hover:text-white transition-colors">
              <i class="fas fa-times text-xl"></i>
            </button>
          </div>

          <div class="p-8 overflow-y-auto custom-scrollbar">
            <div v-if="loadingQuestions" class="py-12 flex flex-col items-center justify-center text-slate-500">
               <div class="w-16 h-16 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
               <p class="font-medium">Generating questions tailored to resume & job...</p>
            </div>

            <div v-else-if="interviewQuestions.length > 0" class="space-y-8">
              
              <div v-for="category in ['Project Questions', 'Resume Technical Questions', 'Job Description Technical Questions', 'Experience Based Questions', 'Certification Questions', 'General']" :key="category">
                <div v-if="interviewQuestions.some(q => q.category === category)">
                  <h4 class="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-200 pb-2">
                    <i class="fas fa-layer-group text-indigo-500"></i> {{ category }}
                  </h4>
                  <div class="space-y-4">
                    <div v-for="(question, index) in interviewQuestions.filter(q => q.category === category)" :key="index" 
                         class="flex gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-indigo-200 transition-colors">
                      <span class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-sm">
                        {{ interviewQuestions.indexOf(question) + 1 }}
                      </span>
                      <div class="flex-1">
                        <p class="text-slate-800 font-bold text-lg mb-2">{{ question.question }}</p>
                        
                        <div class="bg-indigo-50/50 rounded-lg p-3 mb-3 border border-indigo-100">
                          <p class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Suggested Answer / Key Points</p>
                          <p class="text-slate-700 text-sm leading-relaxed">{{ question.suggested_answer }}</p>
                        </div>

                        <div class="flex flex-wrap gap-2">
                          <span v-for="(keyword, kIdx) in question.keywords" :key="kIdx" 
                                class="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded-md border border-slate-200">
                            {{ keyword }}
                          </span>
                        </div>
                      </div>

                      <!-- Score Input -->
                      <div class="flex flex-col items-center justify-center pl-4 border-l border-slate-100">
                        <label class="text-xs font-bold text-slate-400 uppercase mb-1">Score</label>
                        <div class="relative flex items-center">
                          <input 
                            v-model.number="question.score" 
                            type="number" 
                            min="0" 
                            max="10" 
                            step="0.1"
                            class="w-16 text-center font-bold text-lg border border-slate-200 rounded-lg py-1 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                            :class="{'border-red-300 bg-red-50': question.score < 0 || question.score > 10}"
                          />
                          <span class="ml-2 text-xs text-slate-400 font-bold">/ 10</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
            
            <div v-else class="text-center py-8 text-slate-400">
              <p>No questions generated.</p>
            </div>
          </div>

          <div class="p-6 border-t border-slate-100 bg-slate-50 flex justify-between items-center">
            <div class="text-sm text-slate-500">
              <span v-if="interviewQuestions.length > 0">
                Average Score: <span class="font-bold text-indigo-600">{{ calculateAverageScore() }}/10</span>
              </span>
            </div>
            <div class="flex gap-3">
              
              <button 
                v-if="interviewQuestions.length > 0"
                @click="submitScores"
                class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-md transition-all flex items-center gap-2"
              >
                <i class="fas fa-save"></i> Submit Scores
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/config/axios'

// State
const jobs = ref([])
const selectedJob = ref(null)
const applicants = ref([])
const activeTab = ref('candidates')
const isLoadingJobs = ref(false)
const isLoadingApplicants = ref(false)

// Interview Questions State
const showInterviewQuestions = ref(false)
const interviewQuestions = ref([])
const selectedCandidate = ref(null)
const loadingQuestions = ref(false)


// Fetch Jobs
const fetchJobs = async () => {
  isLoadingJobs.value = true
  try {
    const response = await apiClient.get('/api/jobs')
    // Filter for Open jobs
    jobs.value = response.data.jobs
      .filter(job => job.status === 'Open')
      .map(job => ({
        id: job.job_id,
        title: job.title,
        location: job.location,
        type: job.employment_type,
        full_description: job.jd_text
      }))
  } catch (error) {
    console.error('Error fetching jobs:', error)
  } finally {
    isLoadingJobs.value = false
  }
}

// Select Job & Fetch Applicants
const selectJob = async (job) => {
  selectedJob.value = job
  activeTab.value = 'candidates'
  isLoadingApplicants.value = true
  applicants.value = []
  
  try {
    const response = await apiClient.get(`/api/jobs/${job.id}/applicants`)
    applicants.value = response.data.applicants
  } catch (error) {
    console.error('Error fetching applicants:', error)
  } finally {
    isLoadingApplicants.value = false
  }
}


// Generate Interview Questions
const generateQuestions = async (applicant) => {
  selectedCandidate.value = applicant
  showInterviewQuestions.value = true
  loadingQuestions.value = true
  interviewQuestions.value = []

  try {
    const response = await apiClient.post('/api/recruitment/questions', {
      applicant_id: applicant.applicant_id,
      candidate_name: applicant.name,
      skills: [], // Backend will extract from resume
      job_description: selectedJob.value.full_description
    })

    const questionsData = response.data.questions || response.data
    const allQuestions = []
    
    // Map backend keys to readable categories
    const categoryMap = {
        'project_questions': 'Project Questions',
        'resume_technical_questions': 'Resume Technical Questions',
        'jd_technical_questions': 'Job Description Technical Questions',
        'experience_questions': 'Experience Based Questions',
        'certificate_questions': 'Certification Questions'
    }

    // Flatten questions and assign category
    Object.keys(categoryMap).forEach(key => {
        if (questionsData[key] && Array.isArray(questionsData[key])) {
            questionsData[key].forEach(q => {
                allQuestions.push({
                    ...q,
                    category: categoryMap[key]
                })
            })
        }
    })
    
    interviewQuestions.value = allQuestions.length > 0 ? allQuestions : [{ question: 'No questions could be generated.', suggested_answer: '', keywords: [], category: 'General' }]

    // Populate saved scores if they exist
    if (applicant.q_and_a_scores && applicant.q_and_a_scores.length > 0) {
        interviewQuestions.value.forEach((q, index) => {
            if (index < applicant.q_and_a_scores.length) {
                q.score = applicant.q_and_a_scores[index]
            }
        })
    }
    
  } catch (error) {
    console.error('Error generating questions:', error)
    interviewQuestions.value = [{ question: 'Error generating questions. Please try again.', suggested_answer: '', keywords: [], category: 'General' }]
  } finally {
    loadingQuestions.value = false
  }
}



const calculateAverageScore = () => {
  const scores = interviewQuestions.value.map(q => q.score).filter(s => s !== undefined && s !== '' && s !== null)
  if (scores.length === 0) return 0
  const sum = scores.reduce((a, b) => a + b, 0)
  return (sum / scores.length).toFixed(1)
}

const submitScores = async () => {
  const scores = interviewQuestions.value.map(q => q.score)
  
  // Validation
  if (scores.some(s => s === undefined || s === '' || s === null)) {
    alert('Please enter a score for all questions.')
    return
  }
  
  if (scores.some(s => s < 0 || s > 10)) {
    alert('All scores must be between 0 and 10.')
    return
  }
  
  try {
    await apiClient.post(`/api/applicants/${selectedCandidate.value.applicant_id}/scores`, {
      scores: scores
    })
    
    alert('Scores submitted successfully!')
    showInterviewQuestions.value = false
    // Refresh applicants to show new score
    if (selectedJob.value) {
        fetchApplicants(selectedJob.value.job_id)
    }
  } catch (error) {
    alert('Failed to submit scores.')
  }
}

const updateStatus = async (applicant, status) => {
  if (!confirm(`Are you sure you want to mark this candidate as ${status}?`)) return

  try {
    await apiClient.post(`/api/applicants/${applicant.applicant_id}/status`, {
      status: status
    })
    
    // Update local state
    applicant.status = status
    
    // Optional: Refresh list
    // if (selectedJob.value) fetchApplicants(selectedJob.value.job_id)
    
  } catch (error) {
    console.error(`Error marking candidate as ${status}:`, error)
    alert(`Failed to update status to ${status}`)
  }
}


onMounted(() => {
  fetchJobs()
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
