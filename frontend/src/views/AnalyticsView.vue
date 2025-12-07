<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-800 flex items-center gap-2">
        <i class="fas fa-chart-line text-indigo-600"></i>
        Workforce Analytics Dashboard
      </h1>
      <p class="text-sm text-gray-500 mt-1">
        Real-time insights into workforce trends, training compliance, and retention risks
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-10 text-gray-500">
      Loading analytics...
    </div>

    <!-- Error State -->
    <div v-if="error" class="text-center py-10 text-red-600 font-medium">
      {{ error }}
    </div>

    <div v-if="!loading && !error">
      <!-- Metrics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricsCard
          title="Total Employees"
          :value="summary?.total_employees"
          :trend="summary?.trends.employees_vs_last_quarter"
          trendLabel="vs last quarter"
          icon="fa-users"
          value-color="text-blue-600"
        />

        <MetricsCard
          title="Avg Absenteeism"
          :value="summary?.avg_absenteeism"
          unit="%"
          :trend="summary?.trends.absenteeism_vs_last_month"
          trendLabel="vs last month"
          icon="fa-calendar-xmark"
          value-color="text-orange-600"
        />

        <MetricsCard
          title="Training Completion"
          :value="summary?.training_completion_rate"
          unit="%"
          :trend="summary?.trends.training_vs_last_quarter"
          trendLabel="vs last quarter"
          icon="fa-graduation-cap"
          value-color="text-emerald-600"
        />

        <MetricsCard
          title="High Retention Risk"
          :value="summary?.high_retention_risk_percent"
          unit="%"
          :trend="summary?.trends.retention_vs_last_quarter"
          trendLabel="vs last quarter"
          icon="fa-triangle-exclamation"
          value-color="text-red-600"
        />
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <BarChart
          v-if="absenteeism"
          title="Absenteeism Trends"
          subtitle="Monthly breakdown by reason"
          :categories="absenteeism.categories"
          :series="absenteeism.series"
        />

        <PieChart
          v-if="retentionRisk"
          title="Retention Risk Distribution"
          subtitle="Employee retention risk levels"
          :labels="retentionRisk.labels"
          :series="retentionRisk.series"
        />
      </div>

      <!-- Training Completion Chart -->
      <div class="mb-8">
        <BarChart
          v-if="trainingDept"
          title="Training Completion by Department"
          subtitle="Percentage of employees who completed required training"
          :categories="trainingDept.categories"
          :series="trainingDept.series"
        />
      </div>

      <!-- Department Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DepartmentCard
          v-for="dept in departments"
          :key="dept.department"
          :department="dept.department"
          :risk-level="dept.risk_level"
          :employee-count="dept.employee_count"
          :pending-training="dept.pending_training"
          :absenteeism="dept.absenteeism"
          :insights="dept.insights"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import MetricsCard from '../components/analytics/MetricsCard.vue'
import BarChart from '../components/analytics/BarChart.vue'
import PieChart from '../components/analytics/PieChart.vue'
import DepartmentCard from '../components/analytics/DepartmentCard.vue'

// State variables
const summary = ref(null)
const absenteeism = ref(null)
const retentionRisk = ref(null)
const trainingDept = ref(null)
const departments = ref([])
const loading = ref(true)
const error = ref(null)

// API base URL
const API = "http://127.0.0.1:5001"   // Change for production

onMounted(async () => {
  try {
    const [s, a, r, t, d] = await Promise.all([
      axios.get(`${API}/api/analytics/summary`),
      axios.get(`${API}/api/analytics/absenteeism-trends`),
      axios.get(`${API}/api/analytics/retention-risk`),
      axios.get(`${API}/api/analytics/training-completion`),
      axios.get(`${API}/api/analytics/departments`)
    ])

    summary.value = s.data
    absenteeism.value = a.data
    retentionRisk.value = r.data
    trainingDept.value = t.data
    departments.value = d.data || d

  } catch (err) {
    console.error(err)
    error.value = "Failed to load analytics data."
  }

  loading.value = false
})
</script>

