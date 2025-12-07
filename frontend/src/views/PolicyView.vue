<template>
  <div class="p-6 bg-gray-50 min-h-full">
    <div class="max-w-3xl mx-auto">
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-2">
          <i class="fas fa-robot text-indigo-600 text-xl"></i>
          <h1 class="text-2xl font-bold text-gray-800">AI Policy & Job Description Writer</h1>
        </div>
        <p class="text-gray-600">Generate fair, bias-free job postings and workplace policies in compliance with local laws</p>
      </div>

      <div class="max-w-4xl mx-auto">
        <!-- POLICY DOCUMENT FORM -->
        <div class="space-y-6 p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
          <!-- Requirements & Details Textarea -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Policy Requirements & Details</label>
            <textarea
              v-model="policyRequirements"
              rows="6"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Describe the policy requirements, including scope, rules, exceptions, and any specific compliance needs..."
            ></textarea>
          </div>
        </div>

        <!-- Generate Button -->
        <button
          @click="generateDocument"
          class="w-full py-3 px-4 bg-black text-white font-medium rounded-lg hover:bg-gray-800 transition flex items-center justify-center gap-2"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="animate-spin">
            <i class="fas fa-circle-notch"></i>
          </span>
          <span v-else>
            Generate Document
          </span>
        </button>

        <!-- Generated Content -->
        <div v-if="generatedContent" class="mt-8 p-6 bg-white rounded-lg border border-gray-200">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="font-semibold text-lg text-gray-800">Generated Document</h3>
              <div v-if="selectedPolicy" class="mt-1">
                <h2 class="text-md font-bold text-indigo-1200">{{ selectedPolicy.title }}</h2>
                <span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded mt-1 inline-block">{{ selectedPolicy.category }}</span>
              </div>
            </div>
            <button
              @click="copyToClipboard"
              class="text-indigo-600 hover:text-indigo-700 text-sm flex items-center gap-1"
            >
              <i class="fas fa-copy"></i>
              {{ copyText }}
            </button>
          </div>
          <div class="prose max-w-none" v-html="generatedContent"></div>
        </div>

        <!-- Generated Policies List -->
        <div class="mt-12">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Generated Policies History</h2>
          <div v-if="policies.length === 0" class="text-gray-500 italic">No policies generated yet.</div>
          <div v-else class="space-y-4">
            <div v-for="policy in policies" :key="policy.policy_id" class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition cursor-pointer" @click="viewPolicy(policy)">
              <div class="flex justify-between items-center">
                <h3 class="font-semibold text-indigo-600">{{ policy.title }}</h3>
                <span class="text-xs text-gray-500">{{ new Date(policy.created_at || policy.updated_at).toLocaleDateString() }}</span>
              </div>
              <p class="text-sm text-gray-600 mt-1 line-clamp-2">{{ policy.content.replace(/<[^>]*>/g, '') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
})

// General state
const isLoading = ref(false)
const generatedContent = ref('')
const copyText = ref('Copy')
const policies = ref([])
const selectedPolicy = ref(null)

// State for Policy
const policyRequirements = ref('')

async function fetchPolicies() {
  try {
    const response = await apiClient.get('/api/policies')
    policies.value = response.data.policies
  } catch (error) {
    console.error('Error fetching policies:', error)
  }
}

function viewPolicy(policy) {
  selectedPolicy.value = policy
  generatedContent.value = policy.content
  // Scroll to generated content
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  fetchPolicies()
})

async function generateDocument() {
  isLoading.value = true
  generatedContent.value = ''
  
  try {
    // Send policy data to backend
    const response = await apiClient.post('/api/policy/generate/document', {
      requirements: policyRequirements.value
    })
    generatedContent.value = response.data.document
    selectedPolicy.value = {
      title: response.data.title,
      category: response.data.category,
      content: response.data.document
    }
    fetchPolicies() // Refresh list
  } catch (error) {
    console.error('Error generating document:', error)
    generatedContent.value = `<p class="text-red-500">An error occurred while generating the document: ${error.response?.data?.error || error.message}</p>`
  } finally {
    isLoading.value = false
  }
}

function copyToClipboard() {
  // Remove HTML tags for plain text copying
  const plainText = generatedContent.value.replace(/<[^>]*>/g, '\n').replace(/\n+/g, '\n').trim()
  
  navigator.clipboard.writeText(plainText)
    .then(() => {
      copyText.value = 'Copied!'
      setTimeout(() => { copyText.value = 'Copy' }, 2000)
    })
    .catch(err => {
      console.error('Failed to copy:', err)
      copyText.value = 'Failed!'
      setTimeout(() => { copyText.value = 'Copy' }, 2000)
    })
}
</script>

<style>
/* Styles for the generated content */
.prose {
  color: rgb(55 65 81);
  line-height: 1.6;
}
.prose h2 {
  font-size: 1.5rem;
  line-height: 2rem;
  font-weight: 600;
  color: rgb(17 24 39);
  margin-bottom: 1rem;
  margin-top: 1.5rem;
}
.prose h3 {
  font-size: 1.25rem;
  line-height: 1.75rem;
  font-weight: 600;
  color: rgb(31 41 55);
  margin-bottom: 0.5rem;
  margin-top: 1rem;
}
.prose p {
  margin-bottom: 1rem;
}
.prose ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}
.prose li {
  margin-bottom: 0.25rem;
}
</style>
