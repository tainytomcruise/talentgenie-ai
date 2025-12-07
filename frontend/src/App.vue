<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  console.log('App mounted. Token:', authStore.token)
  if (authStore.token) {
    console.log('Calling fetchCurrentUser from App.vue')
    authStore.fetchCurrentUser()
  } else {
    console.log('No token found in App.vue')
  }
})
</script>

<style>

</style>
