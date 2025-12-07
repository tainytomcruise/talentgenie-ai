<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-start gap-3">
      <div class="mt-1">
        <i class="fas fa-calendar text-purple-500"></i>
      </div>
      <div class="flex-1">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-gray-800">{{ name }}</h3>
            <div class="text-sm text-gray-500">
              {{ milestone }}
              <span v-if="department" class="text-gray-400">• {{ department }}</span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-500">{{ date }}</div>
            <button class="text-sm text-indigo-600 hover:text-indigo-700 mt-1">
              Send Reminder
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
  milestone: {
    type: String,
    required: true
  },
  department: {
    type: String,
    default: ''
  },
  date: {
    type: String,
    required: true
  }
})
</script>