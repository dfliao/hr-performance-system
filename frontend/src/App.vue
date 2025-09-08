<template>
  <div id="app" v-cloak>
    <!-- Main application layout -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // Initialize authentication state from token
  await authStore.initializeAuth()
  
  // Hide loading screen
  const loadingContainer = document.querySelector('.loading-container')
  if (loadingContainer) {
    loadingContainer.remove()
  }
})
</script>

<style lang="scss">
// Global styles are imported in main.ts
// This file focuses on app-specific styles

#app {
  min-height: 100vh;
  font-family: 'Inter', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

// Vue directive to hide content until mounted
[v-cloak] {
  display: none !important;
}

// Custom scrollbar
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

// Element Plus theme customization
:root {
  --el-color-primary: #2563eb;
  --el-color-success: #16a34a;
  --el-color-warning: #d97706;
  --el-color-danger: #dc2626;
  --el-color-info: #6b7280;
}
</style>