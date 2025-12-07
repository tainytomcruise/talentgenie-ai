<template>
  <div class="bg-white rounded-lg shadow p-6 flex flex-col">
    <h3 class="text-sm text-gray-600 mb-1">{{ title }}</h3>
    <div class="flex items-center justify-between">
      <div class="flex items-baseline">
        <span 
          class="text-2xl font-semibold"
          :class="valueColor"
        >{{ value }}</span>
        <span v-if="unit" class="ml-1 text-gray-600">{{ unit }}</span>
      </div>
      <div class="flex items-center">
        <i 
          class="fas"
          :class="[
            trend > 0 ? 'fa-arrow-up text-emerald-500' : 'fa-arrow-down text-red-500',
            icon
          ]"
        ></i>
      </div>
    </div>
    <div class="flex items-center mt-2 text-sm">
      <span 
        :class="trend > 0 ? 'text-emerald-500' : 'text-red-500'"
      >{{ Math.abs(trend) }}%</span>
      <span class="text-gray-500 ml-1">{{ trendLabel }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  trend: {
    type: Number,
    required: true
  },
  trendLabel: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  },
  valueColor: {
    type: String,
    default: 'text-gray-900'
  }
})
</script>