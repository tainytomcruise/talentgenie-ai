<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Employee Self-Service Chatbot</h1>
          <p class="text-gray-600">Ask me anything about HR policies, benefits, training, and more</p>
        </div>
        <button
          v-if="chatbotStore.messages.length > 0"
          @click="clearChat"
          class="px-4 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors flex items-center gap-2"
        >
          <i class="fas fa-trash-alt"></i>
          Clear Messages
        </button>
      </div>
    </div>

    <!-- Chat Interface -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <!-- Chat Messages -->
      <div class="p-6 space-y-6 max-h-[600px] overflow-y-auto" ref="messagesContainer">
        <!-- Welcome Message -->
        <div class="flex gap-4">
          <div class="flex-shrink-0 mt-1">
            <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <i class="fas fa-robot text-white text-sm"></i>
            </div>
          </div>
          <div class="flex-1">
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-gray-700">
                Hello! I'm your HR AI Assistant. I can help you with questions about salary, leave policies, health insurance, training courses, compliance forms, and more. How can I assist you today?
              </p>
              <!-- Quick Action Buttons -->
              <div class="mt-4 flex flex-wrap gap-2">
                <button
                  v-for="action in quickActions"
                  :key="action"
                  @click="handleQuickAction(action)"
                  class="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:border-indigo-500 hover:text-indigo-600 transition-colors"
                >
                  {{ action }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Message History from Store -->
        <div 
          v-for="(message, index) in chatbotStore.messages" 
          :key="index" 
          class="flex gap-4" 
          :class="message.role === 'user' ? 'justify-end' : ''"
          v-show="message.content || message.type === 'leave-card'"
        >
          <div v-if="message.role === 'assistant'" class="flex-shrink-0 mt-1">
            <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <i class="fas fa-robot text-white text-sm"></i>
            </div>
          </div>

          <div class="flex-1 max-w-3/4">
            <!-- Leave Request Card -->
            <div v-if="message.type === 'leave-card'" class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-semibold text-gray-800">Leave Request</h3>
                <span 
                  class="px-2 py-1 text-xs rounded-full font-medium"
                  :class="{
                    'bg-yellow-100 text-yellow-700': message.data?.status === 'Pending',
                    'bg-green-100 text-green-700': message.data?.status === 'Approved',
                    'bg-red-100 text-red-700': message.data?.status === 'Rejected'
                  }"
                >
                  {{ message.data?.status || 'Pending' }}
                </span>
              </div>
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex justify-between">
                  <span>Type:</span>
                  <span class="font-medium text-gray-800">{{ message.data?.leave_type }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Dates:</span>
                  <span class="font-medium text-gray-800">
                    {{ message.data?.start_date }} - {{ message.data?.end_date }}
                  </span>
                </div>
                <div v-if="message.data?.number_of_days" class="flex justify-between">
                  <span>Duration:</span>
                  <span class="font-medium text-gray-800">{{ message.data?.number_of_days }} days</span>
                </div>
                <div v-if="message.data?.reason" class="pt-2 border-t border-gray-100 mt-2">
                  <p class="italic">"{{ message.data?.reason }}"</p>
                </div>
              </div>
            </div>

            <!-- Normal Message -->
            <div
              v-else
              :class="[
                'rounded-lg p-4',
                message.role === 'user' ? 'bg-blue-600 text-white ml-auto' : 'bg-gray-50'
              ]"
            >
              <p :class="message.role === 'user' ? 'text-white' : 'text-gray-700'" v-html="formatMessage(message.content)"></p>
            </div>
          </div>

          <div v-if="message.role === 'user'" class="flex-shrink-0 mt-1">
            <div class="w-8 h-8 bg-blue-200 rounded-lg flex items-center justify-center">
              <i class="fas fa-user text-blue-600 text-sm"></i>
            </div>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="chatbotStore.loading" class="flex gap-4">
          <div class="flex-shrink-0 mt-1">
            <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <i class="fas fa-robot text-white text-sm"></i>
            </div>
          </div>
          <div class="flex-1">
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center gap-2 text-gray-600">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Error message -->
        <div v-if="chatbotStore.error" class="flex gap-4">
          <div class="flex-1">
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
              <div class="flex items-center gap-2 text-red-600">
                <i class="fas fa-exclamation-circle"></i>
                <span>{{ chatbotStore.error }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t border-gray-200 p-4">
        <div class="flex gap-4">
          <input
            v-model="userInput"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="Ask me anything about HR..."
            :disabled="chatbotStore.loading"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            @click="sendMessage"
            :disabled="chatbotStore.loading || !userInput.trim()"
            class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i class="fas fa-paper-plane"></i>
            <span>Send</span>
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          <i class="fas fa-info-circle"></i> Powered by AI - Responses are generated in real-time
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatbotStore } from '@/stores/chatbot'
import { useAuthStore } from '@/stores/auth'

const chatbotStore = useChatbotStore()
const authStore = useAuthStore()
const userInput = ref('')
const messagesContainer = ref(null)
const leaveStatusInterval = ref(null)

const quickActions = [
  "Leave request status",
  "What's my remaining leave balance?"
]

const handleQuickAction = async (action) => {
  userInput.value = action
  sendMessage()
}

const checkLeaveStatus = async () => {
  try {
    // Polling for status updates if needed
  } catch (error) {
    console.error('Error checking leave status:', error)
  }
}

const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message) return

  // Clear input immediately
  userInput.value = ''

  try {
    // Get user ID from auth store, fallback to 1
    const userId = authStore.user?.id || authStore.user?.user_id || 1

    // Send message through the store (which calls the backend API)
    await chatbotStore.sendMessage(message, userId)

    // Scroll to bottom after response
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
    // Error is already handled in the store and displayed in UI
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Format message content (convert newlines to <br> for better display)
const formatMessage = (content) => {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

// Load chat history on mount
onMounted(async () => {
  await initChat()
  
  // Poll for status every 60s
  leaveStatusInterval.value = setInterval(checkLeaveStatus, 60000)
})

// Watch for user changes (in case of late load or re-login)
import { watch } from 'vue'
watch(() => authStore.user, (newUser) => {
  if (newUser && chatbotStore.messages.length === 0 && !chatbotStore.loading) {
    initChat()
  }
})

const initChat = async () => {
  try {
    // Ensure user is loaded
    if (!authStore.user) {
        await authStore.fetchCurrentUser()
    }
    
    if (authStore.user) {
        const userId = authStore.user?.user_id || authStore.user?.id
        // await chatbotStore.fetchChatHistory(userId) // History disabled as per user request
    }
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

onUnmounted(() => {
  if (leaveStatusInterval.value) clearInterval(leaveStatusInterval.value)
})

// Clear chat history
const clearChat = async () => {
  try {
    const userId = authStore.user?.id || authStore.user?.user_id || 1
    await chatbotStore.clearMessages(userId)
    userInput.value = ''
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to clear chat:', error)
  }
}
</script>

<style scoped>
/* Custom scrollbar for chat messages */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
