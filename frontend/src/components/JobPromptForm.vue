<template>
  <div class="space-y-8">
    <!-- Section 1: Essential Details (Always Visible) -->
    <div class="p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">
        <i class="fas fa-briefcase text-indigo-600 mr-2"></i>
        Essential Details
      </h3>
      <div class="space-y-4">
        
        <!-- Job Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Job Title <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="formData.jobTitle" 
            placeholder="e.g., Senior Software Engineer, Product Manager, Operations Coordinator"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
            required
          />
          <p class="text-xs text-gray-500 mt-1">
            💡 AI will infer responsibilities, skills, and qualifications based on this title
          </p>
        </div>

        <!-- Experience Level -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Experience Level <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-2 gap-3">
            <select 
              v-model="formData.seniority"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option v-for="option in seniorityOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <input 
              v-model="formData.minExperience" 
              placeholder="e.g., 3-5 years"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
            />
          </div>
          <p class="text-xs text-gray-500 mt-1">
            💡 AI will tailor qualifications and responsibilities to this experience level
          </p>
        </div>

        <!-- Location -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              City <span class="text-red-500">*</span>
            </label>
            <select 
              v-model="formData.city"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select city...</option>
              <option v-for="city in cityOptions" :key="city" :value="city">{{ city }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Work Type <span class="text-red-500">*</span>
            </label>
            <select 
              v-model="formData.location"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option v-for="option in locationOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>

        <!-- Salary Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Salary Range <span class="text-gray-400">(Optional)</span>
          </label>
          <input 
            v-model="formData.salaryRange" 
            placeholder="e.g., $80,000 - $120,000 or Competitive"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
          />
        </div>

        <!-- Number of Openings -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Number of Openings
          </label>
          <input 
            v-model="formData.quantity" 
            type="number" 
            min="1"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="1"
          />
        </div>

      </div>
    </div>

    <!-- Collapsible Advanced Options -->
    <div class="p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
      <button 
        @click="showAdvanced = !showAdvanced"
        class="w-full flex items-center justify-between text-left"
      >
        <h3 class="text-lg font-semibold text-gray-800">
          <i class="fas fa-sliders-h text-indigo-600 mr-2"></i>
          Advanced Options
          <span class="text-sm font-normal text-gray-500 ml-2">(Optional - AI will infer if not provided)</span>
        </h3>
        <i :class="showAdvanced ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="text-gray-400"></i>
      </button>

      <div v-show="showAdvanced" class="mt-6 space-y-6">
        
        <!-- Specific Skills Override -->
        <div class="border-l-4 border-indigo-200 pl-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Specific Required Skills
            <span class="text-xs font-normal text-gray-500 ml-1">(Override AI's suggestions)</span>
          </label>
          <div v-for="(item, index) in formData.mustHaveSkills" :key="index" class="flex gap-2 mb-2">
            <input 
              v-model="formData.mustHaveSkills[index]"
              placeholder="e.g., Python, Flask, Vue.js, AWS"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
            />
            <button 
              @click="formData.mustHaveSkills.splice(index, 1)" 
              class="flex-shrink-0 p-3 text-red-600 hover:text-red-800"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
          <button 
            @click="formData.mustHaveSkills.push('')" 
            class="text-sm font-medium text-indigo-600 hover:text-indigo-800"
          >
            + Add Skill
          </button>
          <p class="text-xs text-gray-500 mt-2">
            💡 Leave empty for AI to infer skills based on job title and experience level
          </p>
        </div>

        <!-- Preferred Skills -->
        <div class="border-l-4 border-green-200 pl-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nice-to-Have Skills
          </label>
          <div v-for="(item, index) in formData.niceToHaveSkills" :key="index" class="flex gap-2 mb-2">
            <input 
              v-model="formData.niceToHaveSkills[index]"
              placeholder="e.g., Docker, Kubernetes, GraphQL"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
            />
            <button 
              @click="formData.niceToHaveSkills.splice(index, 1)" 
              class="flex-shrink-0 p-3 text-red-600 hover:text-red-800"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
          <button 
            @click="formData.niceToHaveSkills.push('')" 
            class="text-sm font-medium text-indigo-600 hover:text-indigo-800"
          >
            + Add Skill
          </button>
        </div>

        <!-- Special Requirements -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Special Requirements or Notes
          </label>
          <textarea 
            v-model="formData.specialRequirements" 
            placeholder="e.g., Must have startup experience, MBA preferred, need security clearance..."
            rows="3"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          ></textarea>
        </div>

        <!-- Tone -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Job Description Tone
          </label>
          <select 
            v-model="formData.tone"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option v-for="option in toneOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- Employment Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Employment Type
          </label>
          <select 
            v-model="formData.employmentType"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option v-for="option in employmentOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

      </div>
    </div>

    <!-- Company Context (Hidden - Auto-Filled) -->
    <div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
      <div class="flex items-start gap-3">
        <i class="fas fa-info-circle text-indigo-600 mt-1"></i>
        <div class="text-sm text-indigo-900">
          <p class="font-medium mb-1">Company details will be auto-filled</p>
          <p class="text-indigo-700">
            We'll use your default company information ({{ formData.companyName }}) for this job posting. 
            The AI will generate a compelling role description, responsibilities, and team context based on your e-commerce focus.
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { defineModel } from 'vue'

const showAdvanced = ref(false)

// This component uses v-model on itself
const formData = defineModel({ 
  type: Object, 
  required: true,
  default: () => ({
    // Essential fields
    jobTitle: '',
    seniority: 'Mid-Level',
    minExperience: '',
    city: '',
    location: 'Hybrid',
    salaryRange: '',
    quantity: 1,
    
    // Auto-filled company fields
    companyName: 'Acme Inc',
    coreMission: "To revolutionize the e-commerce experience by delivering seamless, personalized shopping journeys that connect millions of customers with the products they love. We leverage cutting-edge technology and data-driven insights to build the future of online retail.",
    companyBlurb: "Acme is a leading e-commerce platform transforming how people discover, evaluate, and purchase products online. With a customer-obsessed culture and commitment to innovation, we operate at the intersection of technology, logistics, and retail to deliver exceptional experiences at scale. Our diverse, world-class team is building solutions that shape the future of commerce for millions of users worldwide.",
    field: 'E-Commerce',
    companySize: '120',
    benefits: [
      "Competitive Compensation with Equity & Performance Bonuses",
      "Comprehensive Health & Wellness Benefits",
      "Flexible Work Options & Generous Time Off",
      "Career Growth with Learning & Development Support",
      "Direct Impact on Millions of Customers Worldwide",
      "Cutting-Edge Technology & Innovation-Driven Culture"
    ],
    
    // Advanced/optional fields
    mustHaveSkills: [],
    niceToHaveSkills: [],
    specialRequirements: '',
    tone: 'Startup-friendly',
    employmentType: 'Full-Time',
    
    // Removed fields (AI will infer these)
    // objectives, tools, teamStructure, applicationInstructions
  })
})

// Dropdown options
const toneOptions = [
  { value: 'Startup-friendly', label: 'Startup-friendly (Casual, impact-focused)' },
  { value: 'Professional', label: 'Professional (Corporate, structured)' },
  { value: 'Innovative', label: 'Innovative (Tech-forward, cutting-edge)' },
  { value: 'Creative', label: 'Creative (Design-focused, expressive)' },
]

const seniorityOptions = [
  { value: 'Intern', label: 'Intern' },
  { value: 'Entry-Level', label: 'Entry-Level' },
  { value: 'Mid-Level', label: 'Mid-Level' },
  { value: 'Senior', label: 'Senior' },
  { value: 'Lead', label: 'Lead' },
  { value: 'Principal', label: 'Principal/Staff' },
]

const locationOptions = [
  { value: 'On-site', label: 'On-site' },
  { value: 'Hybrid', label: 'Hybrid' },
  { value: 'Remote', label: 'Remote' },
]

const cityOptions = [
  'Bangalore',
  'Montreal',
  'Chennai',
  'Washington DC',
  'New York',
  'London',
  'San Francisco',
  'Toronto',
  'Mumbai',
  'Delhi',
  'Austin',
  'Seattle',
  'Boston'
]

const employmentOptions = [
  { value: 'Full-Time', label: 'Full-Time' },
  { value: 'Part-Time', label: 'Part-Time' },
  { value: 'Contract', label: 'Contract' },
  { value: 'Internship', label: 'Internship' },
]
</script>

<style scoped>
/* Add smooth transitions for collapsible section */
.space-y-6 > div {
  transition: all 0.3s ease;
}
</style>