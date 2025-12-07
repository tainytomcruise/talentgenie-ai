<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-start gap-3">
      <div class="mt-1">
        <i class="fas fa-birthday-cake text-pink-500"></i>
      </div>
      <div class="flex-1">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-gray-800">{{ name }}</h3>
            <div class="text-sm text-gray-500">Turns {{ age }} on {{ date }}</div>
          </div>
          <div class="flex gap-2">
            <button class="px-3 py-1 bg-black text-white text-sm rounded-lg hover:bg-gray-800 transition">
              Send Wishes
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
  age: {
    type: Number,
    required: true
  },
  date: {
    type: String,
    required: true
  }
})
</script>