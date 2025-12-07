<template>
  <div class="p-6 max-w-6xl mx-auto">
    <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
          <i class="fas fa-graduation-cap text-indigo-600"></i>
        </div>
        <h2 class="text-xl font-semibold">My Training & Learning Paths</h2>
      </div>
      
      
      <div v-if="learningStore.loading && !learningStore.progress.length" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>

      <div v-else>
          <!-- Assigned Training List -->
          <div v-if="learningStore.progress && learningStore.progress.length > 0" class="mb-8">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Assigned Training</h3>
            <div class="space-y-4">
              <div v-for="training in learningStore.progress" :key="training.id" 
                   class="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors">
                 <div class="flex justify-between items-start">
                  <div>
                    <h4 class="font-semibold text-gray-900">{{ training.training_title }}</h4>
                    <p class="text-sm text-gray-600">{{ training.category }}</p>
                    <div class="flex items-center gap-4 mt-2 text-sm text-gray-500">
                        <span><i class="far fa-clock mr-1"></i> {{ training.duration_hours }} hours</span>
                        <span><i class="far fa-user mr-1"></i> {{ training.instructor }}</span>
                        <span 
                          class="ml-2 px-2.5 py-0.5 text-xs rounded-full font-medium whitespace-nowrap"
                          :class="{
                            'bg-green-100 text-green-700': training.status === 'Completed',
                            'bg-blue-100 text-blue-700': training.status === 'In Progress',
                            'bg-yellow-100 text-yellow-700': training.status === 'Enrolled'
                          }"
                        >
                          {{ training.status }}
                        </span>
                    </div>
                  </div>
                  <div class="flex flex-col items-end gap-2">
                      
                      <div class="flex gap-2">
                          <button 
                            v-if="training.status === 'Enrolled'"
                            @click="updateStatus(training, 'In Progress')"
                            class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                          >
                            Start
                          </button>
                          <button 
                            v-if="training.status === 'In Progress'"
                            @click="updateStatus(training, 'Completed')"
                            class="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                          >
                            Complete
                          </button>
                      </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="learningStore.savedPaths.length === 0" class="text-center py-8 text-gray-500">
            <p>No training modules assigned yet.</p>
          </div>

          <!-- Saved Learning Paths List -->
          <div v-if="learningStore.savedPaths.length > 0" class="mt-8 pt-6 border-t border-gray-100">
            <h3 class="text-lg font-medium text-gray-700 mb-3">Personalized Learning Paths</h3>
            <div class="grid md:grid-cols-2 gap-4">
              <div 
                v-for="path in learningStore.savedPaths" 
                :key="path.id"
                class="border border-gray-200 rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-colors"
                :class="{ 'ring-2 ring-blue-500 border-transparent': learningPath && learningPath.id === path.id }"
                @click="selectPath(path)"
              >
                <div class="flex justify-between items-start mb-2">
                  <h3 class="font-semibold text-gray-900">{{ path.learning_path?.learning_path?.title || path.learning_path?.title || 'Learning Path' }}</h3>
                  <span class="text-xs text-gray-500">{{ new Date(path.created_at).toLocaleDateString() }}</span>
                </div>
                
                <div class="flex items-center gap-4 text-sm text-gray-600 mb-3">
                   <span>{{ path.learning_path?.learning_path?.total_duration_weeks || path.learning_path?.total_duration_weeks || 0 }} weeks</span>
                   <span>{{ path.learning_path?.learning_path?.modules?.length || path.learning_path?.modules?.length || 0 }} modules</span>
                </div>
                
              </div>
            </div>
          </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
          <i class="fas fa-magic text-purple-600"></i>
        </div>
        <h2 class="text-xl font-semibold">Adaptive Learning Path Generator</h2>
      </div>
      <p class="text-gray-600 mb-4">
        Generate personalized micro-learning modules, quizzes, and skill simulations based on role and career goals
      </p>

      <!-- Error Alert -->
      <div v-if="learningStore.error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center gap-2 text-red-600">
          <i class="fas fa-exclamation-circle"></i>
          <span>{{ learningStore.error }}</span>
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-6 mb-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Current Role</label>
          <div class="w-full rounded-md border border-gray-300 p-2.5 bg-gray-100 text-gray-600">
            {{ currentRole || 'Loading...' }}
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Career Goal</label>
          <select v-model="careerGoal" class="w-full rounded-md border border-gray-300 p-2.5" :disabled="learningStore.generating">
            <option value="">Select your career goal</option>
            <option v-if="learningStore.goals.length === 0" value="Tech Lead">Tech Lead</option>
            <option v-if="learningStore.goals.length === 0" value="Software Architect">Software Architect</option>
            <option v-if="learningStore.goals.length === 0" value="Engineering Manager">Engineering Manager</option>
            <option v-if="learningStore.goals.length === 0" value="Full Stack Developer">Full Stack Developer</option>
            <option v-for="goal in learningStore.goals" :key="goal" :value="goal">{{ goal }}</option>
          </select>
        </div>
      </div>

      <button
        @click="generatePath"
        :disabled="learningStore.generating || !currentRole || !careerGoal"
        class="w-full bg-black text-white rounded-lg py-3 font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <i v-if="learningStore.generating" class="fas fa-spinner fa-spin"></i>
        <span>{{ learningStore.generating ? 'Generating Your Path...' : 'Generate Personalized Learning Path' }}</span>
      </button>
    </div>

    <!-- Learning Path Display -->
    <div v-if="learningPath" id="path-details" class="space-y-6">
      <!-- Header Card -->
      <div class="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <h3 class="text-2xl font-bold mb-2">{{ learningPath.title }}</h3>
        <div class="flex items-center gap-4 text-sm">
          <span class="flex items-center gap-2">
            <i class="far fa-calendar"></i>
            <span>{{ learningPath.total_duration_weeks }} weeks total</span>
          </span>
          <span class="flex items-center gap-2">
            <i class="far fa-clipboard"></i>
            <span>{{ modules.length }} modules</span>
          </span>
        </div>
      </div>

      <!-- Progress Overview -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h4 class="font-medium mb-3">Your Progress</h4>
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div class="bg-green-600 h-3 rounded-full transition-all duration-500" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <p class="text-sm text-gray-600 mt-2">
          <span v-if="currentModuleNumber > totalModules">All modules completed (100%)</span>
          <span v-else>Module {{ currentModuleNumber }} of {{ totalModules }} ({{ progressPercentage }}%)</span>
        </p>
      </div>

      <!-- Learning Modules -->
      <div class="space-y-4">
        <div v-for="(module, index) in modules" :key="index" class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <!-- Module Header -->
          <div
            class="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
            @click="toggleModule(index)"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex items-start gap-4 flex-1">
                <!-- Module Number Badge -->
                <div class="w-10 h-10 bg-purple-600 text-white rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-lg">
                  {{ index + 1 }}
                </div>

                <div class="flex-1">
                  <h5 class="font-semibold text-lg mb-2">{{ module.module_name }}</h5>
                  <p class="text-gray-600 text-sm mb-3">{{ module.description }}</p>

                  <div class="flex items-center gap-3 text-sm flex-wrap">
                    <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full flex items-center gap-1">
                      <i class="far fa-clock"></i>
                      {{ module.duration_weeks }} weeks
                    </span>
                    <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full flex items-center gap-1">
                      <i class="fas fa-book"></i>
                      {{ module.key_topics?.length || 0 }} topics
                    </span>
                    <span v-if="module.completed" class="px-3 py-1 bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                      <i class="fas fa-check-circle"></i>
                      Completed
                    </span>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <button
                  v-if="!module.completed"
                  @click.stop="markComplete(module, index)"
                  :disabled="(index + 1) !== currentModuleNumber"
                  class="px-4 py-2 rounded-lg transition-colors text-sm font-medium flex items-center gap-1"
                  :class="(index + 1) === currentModuleNumber ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'"
                >
                  <i v-if="(index + 1) === currentModuleNumber" class="fas fa-check mr-1"></i>
                  <i v-else class="fas fa-lock mr-1"></i>
                  {{ (index + 1) === currentModuleNumber ? 'Complete' : 'Locked' }}
                </button>
                <button class="p-2 text-gray-400 hover:text-gray-600">
                  <i :class="expandedModules.includes(index) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Expanded Module Details -->
          <div v-if="expandedModules.includes(index)" class="border-t border-gray-200 bg-gray-50 p-6 space-y-6">
            <!-- Key Topics -->
            <div v-if="module.key_topics && module.key_topics.length > 0">
              <h6 class="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <i class="fas fa-list-ul text-purple-600"></i>
                Key Topics
              </h6>
              <ul class="space-y-2">
                <li v-for="(topic, tIndex) in module.key_topics" :key="tIndex" class="flex items-start gap-2 text-sm text-gray-700">
                  <i class="fas fa-check text-green-600 mt-1"></i>
                  <span>{{ topic }}</span>
                </li>
              </ul>
            </div>

            <!-- Prerequisites -->
            <div v-if="module.prerequisites && module.prerequisites.length > 0">
              <h6 class="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <i class="fas fa-exclamation-circle text-orange-600"></i>
                Prerequisites
              </h6>
              <ul class="space-y-2">
                <li v-for="(prereq, pIndex) in module.prerequisites" :key="pIndex" class="flex items-start gap-2 text-sm text-gray-700">
                  <i class="fas fa-angle-right text-orange-600 mt-1"></i>
                  <span>{{ prereq }}</span>
                </li>
              </ul>
            </div>

            <!-- Resources -->
            <div v-if="module.resources && module.resources.length > 0">
              <h6 class="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <i class="fas fa-book-open text-blue-600"></i>
                Recommended Resources
              </h6>
              <div class="space-y-2">
                <div v-for="(resource, rIndex) in module.resources" :key="rIndex" class="flex items-start gap-2 text-sm">
                  <i class="fas fa-bookmark text-blue-600 mt-1"></i>
                  <span class="text-gray-700">{{ resource }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!learningStore.loading" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-graduation-cap text-purple-600 text-2xl"></i>
      </div>
      <h3 class="text-xl font-semibold mb-2">Ready to Start Your Learning Journey?</h3>
      <p class="text-gray-600 mb-4">Select your current role and career goal above, then generate your personalized learning path.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useLearningStore } from '@/stores/learning'
import { useAuthStore } from '@/stores/auth'

const learningStore = useLearningStore()
const authStore = useAuthStore()

const currentRole = computed(() => {
  return authStore.user?.job_title || authStore.user?.role || 'Employee'
})
const careerGoal = ref('')
const expandedModules = ref([])

// Computed properties
const learningPath = computed(() => {
  if (!learningStore.learningPath) return null
  
  let path = learningStore.learningPath
  
  // Recursively unwrap learning_path until we find modules
  // This handles both API response structure and nested saved path structure
  while (path && !path.modules && path.learning_path) {
    path = path.learning_path
  }
  
  // Ensure ID is preserved if it exists on the parent (the store wrapper)
  if (learningStore.learningPath.id && path && !path.id) {
      // Create a new object to avoid mutating the deep state if it's frozen/shared
      path = { ...path, id: learningStore.learningPath.id }
  }
  
  return path
})

const modules = computed(() => {
  if (!learningPath.value) return []
  return learningPath.value.modules || []
})

const totalModules = computed(() => modules.value.length)

const currentModuleNumber = computed(() => {
  if (!learningStore.learningPath) return 1
  // If progress is missing, default to 1
  return Math.floor(learningStore.learningPath.progress) || 1
})

const progressPercentage = computed(() => {
  if (totalModules.value === 0) return 0
  // Progress 1 means 0% done (started module 1)
  // Progress 2 means 1 module done
  return Math.round(((currentModuleNumber.value - 1) / totalModules.value) * 100)
})

// Actions
const toggleModule = (index) => {
  const idx = expandedModules.value.indexOf(index)
  if (idx > -1) {
    expandedModules.value.splice(idx, 1)
  } else {
    expandedModules.value.push(index)
  }
}

const selectPath = (path) => {
    // Set the selected path as the current one to view details
    // We need to construct it such that the computed 'learningPath' works
    learningStore.learningPath = {
        id: path.id,
        learning_path: path.learning_path,
        progress: path.progress
    }
    expandedModules.value = []
    
    // Scroll to details
    setTimeout(() => {
        const el = document.getElementById('path-details')
        if (el) el.scrollIntoView({ behavior: 'smooth' })
    }, 100)
}

const generatePath = async () => {
  if (!currentRole.value || !careerGoal.value) {
    learningStore.error = 'Please select both current role and career goal'
    return
  }

  // Reset expanded modules
  expandedModules.value = []

  try {
    const employeeId = authStore.user?.emp_id || authStore.user?.id || null
    console.log('Generating path for employeeId:', employeeId)
    await learningStore.generateLearningPath(currentRole.value, careerGoal.value, employeeId)
  } catch (error) {
    console.error('Failed to generate learning path:', error)
    // Error is already set in the store
  }
}

const markComplete = async (module, index) => {
  try {
    // Mark as completed locally first for immediate UI feedback
    module.completed = true

    // If we have a path ID, save to backend
    // The computed 'learningPath' should have the ID attached now
    if (learningPath.value?.id) {
      const response = await learningStore.updateLearningPathModule(learningPath.value.id, index, true)
      // Update local progress from response or increment
      if (response && response.progress) {
          learningStore.learningPath.progress = response.progress
      }
    } else {
        console.warn('No path ID found, cannot save progress')
    }
  } catch (error) {
    console.error('Failed to mark module as complete:', error)
    // Revert on error
    module.completed = false
  }
}

const updateStatus = async (training, newStatus) => {
  try {
    // Optimistic update
    const oldStatus = training.status
    training.status = newStatus
    
    await learningStore.updateTrainingStatus(training.id, newStatus)
    
    // If completed, set completion date locally
    if (newStatus === 'Completed') {
      training.completion_date = new Date().toISOString()
    }
  } catch (error) {
    console.error('Failed to update status:', error)
    // Revert on error (would need to store old status to do this properly, 
    // but for now we just log it. A real app would revert.)
    alert('Failed to update status. Please try again.')
  }
}

const initData = async (user) => {
  if (!user?.emp_id) {
    console.log('initData: User or emp_id missing')
    return
  }
  
  try {
    console.log('initData: Fetching data for emp_id:', user.emp_id)
    await Promise.all([
      learningStore.fetchRolesAndGoals(),
      learningStore.fetchLearningProgress(user.emp_id),
      learningStore.fetchSavedLearningPath(user.emp_id)
    ])
  } catch (error) {
    console.error('initData: Failed to load data:', error)
  }
}

onMounted(async () => {
  console.log('MyLearningView mounted. User:', authStore.user)
  
  if (!authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch (e) {
      console.error('Failed to fetch user:', e)
    }
  }
  
  if (authStore.user?.emp_id) {
    initData(authStore.user)
  } else if (authStore.user) {
      // Fallback: if emp_id is missing but user exists, maybe try to fetch using user_id if the store supports it
      // or just log error. For now, we'll log.
      console.warn('User loaded but emp_id missing:', authStore.user)
  }
})

// Watch for user changes (e.g. initial load or refresh)
watch(() => authStore.user, (newUser) => {
  console.log('User changed:', newUser)
  if (newUser?.emp_id) {
    initData(newUser)
  }
}, { deep: true })
</script>
