<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-start gap-3">
      <div class="mt-1">
        <i class="fas fa-trophy text-amber-500"></i>
      </div>
      <div class="flex-1">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-gray-800">{{ name }}</h3>
            <div class="text-sm text-gray-500">{{ achievement }}</div>
          </div>
          <div class="flex gap-2">
            <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm">
              {{ quarter }}
            </span>
            <button class="px-3 py-1 bg-black text-white text-sm rounded-lg hover:bg-gray-800 transition">
              Approve & Send
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  achievement: {
    type: String,
    required: true
  },
  quarter: {
    type: String,
    required: true
  }
})
</script>