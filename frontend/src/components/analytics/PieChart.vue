<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ title }}</h3>
    <p class="text-sm text-gray-500 mb-4">{{ subtitle }}</p>
    <apexchart
      type="pie"
      height="350"
      :options="chartOptions"
      :series="series"
    ></apexchart>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  },
  labels: {
    type: Array,
    required: true
  },
  series: {
    type: Array,
    required: true
  }
})

const chartOptions = computed(() => ({
  chart: {
    type: 'pie'
  },
  labels: props.labels,
  colors: ['#10b981', '#f59e0b', '#ef4444'],
  legend: {
    position: 'bottom',
    fontSize: '12px'
  },
  dataLabels: {
    enabled: true,
    formatter: function (val) {
      return val.toFixed(0) + '%'
    }
  }
}))
</script>