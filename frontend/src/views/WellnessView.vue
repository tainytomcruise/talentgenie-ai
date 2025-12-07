<template>
  <div class="p-6 max-w-6xl mx-auto">
    <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-8 h-8 bg-pink-100 rounded-lg flex items-center justify-center">
          <i class="fas fa-heart text-pink-600"></i>
        </div>
        <h2 class="text-xl font-semibold">Wellness Resources</h2>
      </div>
      <p class="text-gray-600">
        Access mental health support, wellness programs, and self-care resources
      </p>
    </div>

    <!-- Error Alert -->
    <div v-if="wellnessStore.error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
      <div class="flex items-center gap-2 text-red-600">
        <i class="fas fa-exclamation-circle"></i>
        <span>{{ wellnessStore.error }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="wellnessStore.loading && !wellnessStore.resources.length" class="text-center py-12">
      <i class="fas fa-spinner fa-spin text-4xl text-purple-600 mb-4"></i>
      <p class="text-gray-600">Loading wellness resources...</p>
    </div>

    <!-- Wellness Resources -->
    <div v-else class="grid md:grid-cols-2 gap-6 mb-6">
      <!-- Dynamic Resources from Backend -->
      <div v-for="resource in wellnessStore.resources" :key="resource.id" class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center gap-3 mb-3">
          <div :class="getResourceIconClass(resource)">
            <!-- Render Emoji if detected, otherwise FontAwesome -->
            <span v-if="isEmoji(resource.icon)" class="text-2xl">{{ resource.icon }}</span>
            <i v-else :class="getResourceIcon(resource)"></i>
          </div>
          <h3 class="font-semibold text-lg">{{ resource.title || resource.name }}</h3>
        </div>
        <p class="text-gray-600 mb-4">
          {{ resource.description }}
        </p>
        <a v-if="resource.link || resource.url"
           :href="resource.link || resource.url"
           target="_blank"
           class="text-purple-600 hover:text-purple-700 font-medium inline-flex items-center gap-1">
          Access Resource
          <i class="fas fa-external-link-alt text-xs"></i>
        </a>
      </div>

      <!-- Fallback Static Resources if backend returns empty -->
      <template v-if="!wellnessStore.resources.length && !wellnessStore.loading">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-phone text-purple-600"></i>
            </div>
            <h3 class="font-semibold text-lg">Employee Assistance Program (EAP)</h3>
          </div>
          <p class="text-gray-600 mb-4">
            Free, confidential counseling services for you and your family
          </p>
          <button class="text-purple-600 hover:text-purple-700 font-medium">
            Access EAP Services →
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-spa text-blue-600"></i>
            </div>
            <h3 class="font-semibold text-lg">Meditation & Mindfulness App</h3>
          </div>
          <p class="text-gray-600 mb-4">
            Company-sponsored subscription to Calm or Headspace
          </p>
          <button class="text-blue-600 hover:text-blue-700 font-medium">
            Access Meditation App →
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-heart-pulse text-green-600"></i>
            </div>
            <h3 class="font-semibold text-lg">Mental Health Therapy Coverage</h3>
          </div>
          <p class="text-gray-600 mb-4">
            Insurance covers mental health services
          </p>
          <button class="text-green-600 hover:text-green-700 font-medium">
            View Coverage Details →
          </button>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-person-running text-orange-600"></i>
            </div>
            <h3 class="font-semibold text-lg">Wellness Coaching</h3>
          </div>
          <p class="text-gray-600 mb-4">
            One-on-one coaching for stress management and work-life balance
          </p>
          <button class="text-orange-600 hover:text-orange-700 font-medium">
            Schedule Session →
          </button>
        </div>
      </template>
    </div>

    <!-- Wellness Tip of the day -->
    <div class="bg-blue-50 rounded-lg p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-lightbulb text-blue-600"></i>
          </div>
          <h3 class="font-semibold text-lg">Wellness Tip of the Day</h3>
        </div>
        <select
          v-model="selectedCategory"
          @change="loadTips"
          class="px-4 py-2 border border-blue-200 rounded-lg bg-white text-sm"
        >
          <option value="general">General Wellness</option>
          <option value="mental">Mental Health</option>
          <option value="physical">Physical Health</option>
          <option value="nutrition">Nutrition</option>
          <option value="sleep">Sleep Quality</option>
        </select>
      </div>

      <div v-if="false" class="text-center py-4">
        <!-- Loader removed -->
      </div>

      <ul v-else-if="wellnessStore.tips.length > 0" class="space-y-3 text-gray-700">
        <li v-for="(tip, index) in wellnessStore.tips" :key="index" class="flex items-start gap-2">
          <i class="fas fa-check-circle text-blue-600 mt-1"></i>
          <span>{{ tip }}</span>
        </li>
      </ul>

      <ul v-else class="space-y-3 text-gray-700">
        <li class="flex items-start gap-2">
          <i class="fas fa-check-circle text-blue-600 mt-1"></i>
          Take regular breaks throughout your workday (5-10 minutes every hour)
        </li>
        <li class="flex items-start gap-2">
          <i class="fas fa-check-circle text-blue-600 mt-1"></i>
          Practice the 4-7-8 breathing technique when feeling overwhelmed
        </li>
        <li class="flex items-start gap-2">
          <i class="fas fa-check-circle text-blue-600 mt-1"></i>
          Set clear boundaries between work and personal time
        </li>
        <li class="flex items-start gap-2">
          <i class="fas fa-check-circle text-blue-600 mt-1"></i>
          Connect with colleagues and build supportive relationships
        </li>
        <li class="flex items-start gap-2">
          <i class="fas fa-check-circle text-blue-600 mt-1"></i>
          Don't hesitate to use your EAP services - they're confidential and free
        </li>
      </ul>
    </div>

    <!-- Upcoming Wellness Events Section Removed -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useWellnessStore } from '@/stores/wellness'
import { useAuthStore } from '@/stores/auth'

const wellnessStore = useWellnessStore()
const authStore = useAuthStore()

const selectedCategory = ref('general')
const tipsLoading = ref(false)
const registering = ref(null)

// Helper functions
const isEmoji = (str) => {
  if (!str) return false
  // Check for non-ASCII characters (simple emoji check)
  return /[^\u0000-\u007F]/.test(str)
}

const getResourceIconClass = (resource) => {
  // Use DB color if available
  if (resource.color) {
    return `w-10 h-10 bg-${resource.color}-100 rounded-lg flex items-center justify-center`
  }

  const category = resource.category || resource.type
  const categoryLower = (category || '').toLowerCase()
  const colorMap = {
    'eap': 'w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center',
    'mental': 'w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center',
    'physical': 'w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center',
    'coaching': 'w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center',
    'meditation': 'w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center',
  }

  for (const [key, className] of Object.entries(colorMap)) {
    if (categoryLower.includes(key)) return className
  }

  return 'w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center'
}

const getResourceIcon = (resource) => {
  // Use DB icon if available
  if (resource.icon) {
    // If color is also provided, apply text color
    const colorClass = resource.color ? `text-${resource.color}-600` : 'text-gray-600'
    // If icon string already contains classes, just append color if needed, or assume it's just the icon name
    if (resource.icon.includes(' ')) {
        return `${resource.icon} ${colorClass}`
    }
    return `fas fa-${resource.icon} ${colorClass}`
  }

  const category = resource.category || resource.type
  const categoryLower = (category || '').toLowerCase()
  const iconMap = {
    'eap': 'fas fa-phone text-purple-600',
    'mental': 'fas fa-brain text-blue-600',
    'physical': 'fas fa-dumbbell text-green-600',
    'coaching': 'fas fa-user-tie text-orange-600',
    'meditation': 'fas fa-spa text-indigo-600',
    'therapy': 'fas fa-heart-pulse text-pink-600',
  }

  for (const [key, icon] of Object.entries(iconMap)) {
    if (categoryLower.includes(key)) return icon
  }

  return 'fas fa-heart text-purple-600'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Date TBA'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const loadTips = async () => {
  // tipsLoading.value = true // No loader needed
  try {
    await wellnessStore.fetchWellnessTips(selectedCategory.value)
  } catch (error) {
    console.error('Failed to load wellness tips:', error)
  } finally {
    // tipsLoading.value = false
  }
}


// Load data on mount
onMounted(async () => {
  try {
    // Load wellness resources
    await wellnessStore.fetchWellnessResources()

    // Load default wellness tips
    await loadTips()
  } catch (error) {
    console.error('Failed to load wellness data:', error)
  }
})
</script>
