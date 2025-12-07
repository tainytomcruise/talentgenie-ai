<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-start gap-3">
      <div class="mt-1">
        <i class="fas fa-poll text-blue-500"></i>
      </div>
      <div class="flex-1">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-gray-800">{{ title }}</h3>
            <div class="text-sm text-gray-500">{{ description }}</div>
          </div>
          <div class="flex gap-2">
            <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm">
              {{ deadline }}
            </span>
            <button class="px-3 py-1 bg-black text-white text-sm rounded-lg hover:bg-gray-800 transition">
              Take Survey
            </button>
          </div>
        </div>
      </div>
    </div>
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
  deadline: {
    type: String,
    required: true
  }
})
</script>