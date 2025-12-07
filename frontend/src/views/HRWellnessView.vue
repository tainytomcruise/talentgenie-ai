<template>
  <div class="p-6">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-800">Employee Wellness</h1>
      <p class="text-gray-600">Monitor and support employee well-being initiatives</p>
    </div>

    <!-- Tab Navigation -->
    <div class="flex gap-4 mb-6 border-b">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        :class="[
          'px-4 py-2 text-sm font-medium transition-colors',
          currentTab === tab.id 
            ? 'text-blue-600 border-b-2 border-blue-600' 
            : 'text-gray-600 hover:text-blue-600'
        ]"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- Resources Section -->
    <div v-if="currentTab === 'resources'" class="grid md:grid-cols-2 gap-4">
      <ResourceCard
        v-for="resource in resources"
        :key="resource.id"
        :title="resource.title"
        :type="resource.type"
        :link="resource.link"
      />
    </div>

    <!-- Alerts Section -->
    <div v-if="currentTab === 'alerts'" class="grid md:grid-cols-2 gap-4">
      <AlertCard
        v-for="alert in alerts"
        :key="alert.id"
        :name="alert.name"
        :department="alert.department"
        :duration="alert.duration"
        :startDate="alert.startDate"
      />
    </div>

    <!-- Milestones Section -->
    <div v-if="currentTab === 'milestones'" class="grid md:grid-cols-2 gap-4">
      <MilestoneCard
        v-for="milestone in milestones"
        :key="milestone.id"
        :name="milestone.name"
        :achievement="milestone.achievement"
        :date="milestone.date"
      />
    </div>

    <!-- Awards Section -->
    <div v-if="currentTab === 'awards'" class="grid md:grid-cols-2 gap-4">
      <AwardCard
        v-for="award in awards"
        :key="award.id"
        :name="award.name"
        :achievement="award.achievement"
        :quarter="award.quarter"
      />
    </div>

    <!-- Birthdays Section -->
    <div v-if="currentTab === 'birthdays'" class="grid md:grid-cols-2 gap-4">
      <BirthdayCard
        v-for="birthday in birthdays"
        :key="birthday.id"
        :name="birthday.name"
        :age="birthday.age"
        :date="birthday.date"
      />
    </div>

    <!-- Surveys Section -->
    <div v-if="currentTab === 'surveys'" class="grid md:grid-cols-2 gap-4">
      <SurveyCard
        v-for="survey in surveys"
        :key="survey.id"
        :title="survey.title"
        :description="survey.description"
        :deadline="survey.deadline"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ResourceCard from '../components/wellness/ResourceCard.vue'
import AlertCard from '../components/wellness/AlertCard.vue'
import MilestoneCard from '../components/wellness/MilestoneCard.vue'
import AwardCard from '../components/wellness/AwardCard.vue'
import BirthdayCard from '../components/wellness/BirthdayCard.vue'
import SurveyCard from '../components/wellness/SurveyCard.vue'

const currentTab = ref('resources')

const tabs = [
  { id: 'resources', name: 'Resources' },
  { id: 'alerts', name: 'Absence Alerts' },
  { id: 'milestones', name: 'Milestones' },
  { id: 'awards', name: 'Awards' },
  { id: 'birthdays', name: 'Birthdays' },
  { id: 'surveys', name: 'Surveys' }
]

// Sample data - replace with actual data from your API
const resources = [
  {
    id: 1,
    title: 'Mental Health Support',
    type: 'External Resource',
    link: 'https://example.com/mental-health'
  },
  {
    id: 2,
    title: 'Work-Life Balance Guide',
    type: 'Internal Document',
    link: '/documents/work-life-balance'
  }
]

const alerts = [
  {
    id: 1,
    name: 'John Doe',
    department: 'Engineering',
    duration: '2 weeks',
    startDate: '2025-11-01'
  }
]

const milestones = [
  {
    id: 1,
    name: 'Jane Smith',
    achievement: '5 Years at Company',
    date: '2025-11-15'
  }
]

const awards = [
  {
    id: 1,
    name: 'Mike Johnson',
    achievement: 'Outstanding Performance',
    quarter: 'Q4 2025'
  }
]

const birthdays = [
  {
    id: 1,
    name: 'Sarah Wilson',
    age: 30,
    date: 'Nov 5, 2025'
  }
]

const surveys = [
  {
    id: 1,
    title: 'Employee Satisfaction Survey',
    description: 'Help us improve your work experience',
    deadline: 'Nov 15, 2025'
  }
]
</script>