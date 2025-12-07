<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-start mb-4">
      <h3 class="text-lg font-semibold text-gray-800">{{ department }}</h3>
      <span 
        class="px-2 py-1 text-sm rounded-full"
        :class="riskLevel === 'Low Risk' ? 'bg-emerald-100 text-emerald-700' : 
                riskLevel === 'Medium Risk' ? 'bg-orange-100 text-orange-700' :
                'bg-red-100 text-red-700'"
      >
        {{ riskLevel }}
      </span>
    </div>

    <div class="grid grid-cols-3 gap-4 mb-4">
      <div>
        <div class="text-sm text-gray-600">Employees</div>
        <div class="text-lg font-semibold">{{ employeeCount }}</div>
      </div>
      <div>
        <div class="text-sm text-gray-600">Pending Training</div>
        <div class="text-lg font-semibold">{{ pendingTraining }}</div>
      </div>
      <div>
        <div class="text-sm text-gray-600">Avg Absenteeism</div>
        <div class="text-lg font-semibold">{{ absenteeism }}%</div>
      </div>
    </div>

    <div class="space-y-2">
      <div 
        v-for="(insight, index) in insights" 
        :key="index"
        class="flex items-start gap-2 text-sm text-gray-600"
      >
        <i class="fas fa-triangle-exclamation mt-1"></i>
        <span>{{ insight }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  department: {
    type: String,
    required: true
  },
  riskLevel: {
    type: String,
    required: true
  },
  employeeCount: {
    type: Number,
    required: true
  },
  pendingTraining: {
    type: Number,
    required: true
  },
  absenteeism: {
    type: Number,
    required: true
  },
  insights: {
    type: Array,
    default: () => []
  }
})
</script>