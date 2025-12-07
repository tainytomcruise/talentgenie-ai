<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ title }}</h3>
    <p class="text-sm text-gray-500 mb-4">{{ subtitle }}</p>
    <apexchart
      type="bar"
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
  categories: {
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
    type: 'bar',
    stacked: true,
    toolbar: {
      show: false
    }
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      endingShape: 'rounded'
    },
  },
  dataLabels: {
    enabled: false
  },
  xaxis: {
    categories: props.categories,
    labels: {
      style: {
        colors: '#666',
        fontSize: '12px'
      }
    }
  },
  yaxis: {
    labels: {
      style: {
        colors: '#666',
        fontSize: '12px'
      }
    }
  },
  legend: {
    position: 'bottom',
    offsetY: 0,
    fontSize: '12px'
  },
  grid: {
    borderColor: '#f3f4f6',
    strokeDashArray: 4
  },
  colors: ['#10b981', '#f59e0b', '#ef4444']
}))
</script>