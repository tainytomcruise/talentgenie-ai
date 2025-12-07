<template>
  <div class="p-6">
    <div class="mb-8">
      <div class="flex items-center gap-2 mb-2">
        <i class="fas fa-brain text-indigo-600 text-xl"></i>
        <h1 class="text-2xl font-bold text-gray-800">Workforce Sentiment Analyzer</h1>
      </div>
      <p class="text-gray-600">AI-powered analysis of employee surveys and feedback into executive-friendly insights</p>
    </div>

    <!-- Overall Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Overall Sentiment -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500 mb-4">Overall Sentiment</h3>
        <div class="flex items-center gap-2">
          <span class="text-2xl font-bold text-gray-800">62%</span>
          <span class="text-sm text-green-600">
            <i class="fas fa-arrow-up"></i>
            5.3%
          </span>
          <i class="fas fa-smile text-green-500 text-2xl ml-auto"></i>
        </div>
      </div>

      <!-- Survey Responses -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500 mb-4">Survey Responses</h3>
        <div class="flex items-center gap-2">
          <span class="text-2xl font-bold text-gray-800">125</span>
          <i class="fas fa-comments text-blue-500 text-2xl ml-auto"></i>
        </div>
      </div>

      <!-- Response Rate -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500 mb-4">Response Rate</h3>
        <div class="flex items-center gap-2">
          <span class="text-2xl font-bold text-gray-800">88%</span>
          <div class="ml-auto w-16 h-16">
            <apexchart
              type="radialBar"
              :options="rateChartOptions"
              :series="[88]"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Sentiment Trend Chart -->
    <div class="bg-white p-6 rounded-lg shadow mb-8">
      <h3 class="text-lg font-medium text-gray-800 mb-4">Sentiment Trend Over Time</h3>
      <p class="text-sm text-gray-600 mb-4">Monthly sentiment distribution from employee feedback</p>
      <apexchart
        type="line"
        height="350"
        :options="trendChartOptions"
        :series="trendChartSeries"
      />
    </div>

    <!-- Key Themes Section -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h3 class="text-lg font-medium text-gray-800 mb-2">Key Themes from Employee Feedback</h3>
      <p class="text-sm text-gray-600 mb-6">AI-identified themes and sentiment analysis</p>
      
      <div class="space-y-6">
        <div v-for="theme in keyThemes" :key="theme.name" class="space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <i :class="getThemeIcon(theme.sentiment)" class="text-lg"></i>
              <span class="font-medium">{{ theme.name }}</span>
            </div>
            <span class="text-sm text-gray-500">{{ theme.mentions }} mentions</span>
          </div>
          <div class="relative w-full h-2 bg-gray-100 rounded">
            <div 
              class="absolute left-0 top-0 h-full rounded" 
              :style="{
                width: `${theme.positivePercent}%`,
                backgroundColor: getThemeColor(theme.sentiment)
              }"
            ></div>
          </div>
          <p class="text-sm text-gray-600 italic">{{ theme.quote }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Radial Chart Options for Response Rate
const rateChartOptions = {
  chart: {
    type: 'radialBar',
    sparkline: {
      enabled: true
    }
  },
  colors: ['#4F46E5'],
  plotOptions: {
    radialBar: {
      hollow: {
        size: '65%'
      },
      track: {
        background: '#E5E7EB'
      },
      dataLabels: {
        show: false
      }
    }
  }
}

// Trend Chart Options
const trendChartOptions = {
  chart: {
    type: 'line',
    toolbar: {
      show: false
    }
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  colors: ['#EF4444', '#F59E0B', '#10B981'],
  xaxis: {
    categories: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    labels: {
      style: {
        colors: '#6B7280'
      }
    }
  },
  yaxis: {
    labels: {
      style: {
        colors: '#6B7280'
      }
    }
  },
  grid: {
    borderColor: '#E5E7EB'
  },
  legend: {
    position: 'bottom',
    labels: {
      colors: '#6B7280'
    }
  }
}

// Trend Chart Data
const trendChartSeries = [
  {
    name: 'Negative %',
    data: [12, 11, 12, 11, 10, 9]
  },
  {
    name: 'Neutral %',
    data: [28, 29, 28, 27, 28, 28]
  },
  {
    name: 'Positive %',
    data: [60, 60, 60, 62, 62, 63]
  }
]

// Key Themes Data
const keyThemes = ref([
  {
    name: 'Work-Life Balance',
    mentions: 87,
    positivePercent: 65,
    sentiment: 'positive',
    quote: 'Great flexibility with remote work options and understanding management'
  },
  {
    name: 'Career Development',
    mentions: 72,
    positivePercent: 68,
    sentiment: 'positive',
    quote: 'Appreciate the learning budget and internal mobility opportunities'
  },
  {
    name: 'Compensation',
    mentions: 65,
    positivePercent: 45,
    sentiment: 'neutral',
    quote: 'Salary is competitive but could be more transparent about raises'
  },
  {
    name: 'Communication',
    mentions: 58,
    positivePercent: 52,
    sentiment: 'neutral',
    quote: 'Leadership is transparent but cross-team communication could improve'
  },
  {
    name: 'Workload',
    mentions: 43,
    positivePercent: 30,
    sentiment: 'negative',
    quote: 'Sometimes feel overwhelmed with multiple projects and tight deadlines'
  }
])

// Helper functions
function getThemeIcon(sentiment) {
  const icons = {
    positive: 'fas fa-smile text-green-500',
    neutral: 'fas fa-meh text-yellow-500',
    negative: 'fas fa-frown text-red-500'
  }
  return icons[sentiment]
}

function getThemeColor(sentiment) {
  const colors = {
    positive: '#10B981',
    neutral: '#F59E0B',
    negative: '#EF4444'
  }
  return colors[sentiment]
}
</script>