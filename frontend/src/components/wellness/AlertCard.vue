<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-start mb-4">
      <div class="flex items-start gap-3">
        <div class="mt-1">
          <i :class="icon" class="text-indigo-600"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="font-semibold text-gray-800">{{ name }}</h3>
            <span class="text-sm text-gray-500">{{ department }}</span>
          </div>
          <p class="text-sm text-gray-600 mt-1">{{ description }}</p>
        </div>
      </div>
      <span 
        v-if="riskLevel"
        class="px-2 py-1 text-sm rounded-full"
        :class="riskLevelClass"
      >
        {{ riskLevel }}
      </span>
    </div>

    <div v-if="aiRecommendation" class="bg-yellow-50 border border-yellow-100 rounded-lg p-3 mb-4">
      <div class="flex items-start gap-2">
        <i class="fas fa-robot text-yellow-600 mt-1"></i>
        <div>
          <div class="text-xs font-medium text-yellow-800">AI Recommendation</div>
          <div class="text-sm text-yellow-800">{{ aiRecommendation }}</div>
        </div>
      </div>
    </div>

    <div class="flex gap-3">
      <button
        v-for="action in actions"
        :key="action"
        class="flex-1 text-sm text-gray-700 py-2 px-3 rounded-lg hover:bg-gray-100 transition"
      >
        {{ action }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  department: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'fas fa-user'
  },
  riskLevel: {
    type: String,
    default: ''
  },
  aiRecommendation: {
    type: String,
    default: ''
  },
  actions: {
    type: Array,
    default: () => []
  }
})

const riskLevelClass = computed(() => {
  switch (props.riskLevel) {
    case 'Low Risk':
      return 'bg-emerald-100 text-emerald-700'
    case 'Medium Risk':
      return 'bg-orange-100 text-orange-700'
    case 'High Risk':
      return 'bg-red-100 text-red-700'
    default:
      return ''
  }
})
</script>