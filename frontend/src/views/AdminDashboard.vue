<template>
  <div class="flex min-h-screen bg-gray-50">
    <Sidebar />

    <div class="flex-1 flex flex-col">
      <Navbar />

      <main class="flex-1 p-8">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from '../components/SideBar.vue'
import Navbar from '../components/NavBar.vue'
</script>
