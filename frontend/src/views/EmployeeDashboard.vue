<template>
  <div class="flex min-h-screen bg-gray-50">
    <SideBar :isEmployee="true" />

    <div class="flex-1 flex flex-col">
      <NavBar :isEmployee="true" />

      <main class="flex-1 p-8">
        <!-- Employee landing content: default to Ask HR -->
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import SideBar from '../components/SideBar.vue'
import NavBar from '../components/NavBar.vue'
</script>