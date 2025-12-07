<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center gap-3 mb-2">
      <i :class="icon" class="text-lg" :style="{ color: iconColor }"></i>
      <h3 class="text-lg font-semibold text-gray-800">{{ title }}</h3>
    </div>
    <p class="text-sm text-gray-500 mb-4">{{ description }}</p>
    
    <div v-if="details" class="text-sm text-gray-600 mb-4">
      {{ details }}
    </div>

    <div v-if="availability" class="grid grid-cols-2 gap-4 text-sm mb-4">
      <div>
        <div class="text-gray-500">Contact</div>
        <div>{{ availability.contact }}</div>
      </div>
      <div>
        <div class="text-gray-500">Available</div>
        <div>{{ availability.time }}</div>
      </div>
    </div>

    <button 
      v-if="actionLabel"
      class="w-full bg-black text-white rounded-lg py-2 text-sm font-medium hover:bg-gray-800 transition"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  iconColor: {
    type: String,
    default: '#FF69B4' // pink color for wellness
  },
  details: {
    type: String,
    default: ''
  },
  availability: {
    type: Object,
    default: null
  },
  actionLabel: {
    type: String,
    default: ''
  }
})
</script>