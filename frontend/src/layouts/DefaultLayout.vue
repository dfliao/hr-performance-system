<template>
  <el-container class="default-layout">
    <!-- Header -->
    <el-header class="layout-header">
      <div class="header-left">
        <el-button
          :icon="Expand"
          @click="toggleSidebar"
          circle
          size="default"
          class="sidebar-toggle"
        />
        <h1 class="app-title">HR 績效管理系統</h1>
      </div>
      
      <div class="header-right">
        <!-- Notifications -->
        <el-badge :value="notificationCount" :hidden="notificationCount === 0">
          <el-button :icon="Bell" circle size="default" />
        </el-badge>
        
        <!-- User dropdown -->
        <el-dropdown @command="handleUserCommand">
          <div class="user-info">
            <el-avatar :size="32" :src="user?.avatar_url">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="user-name">{{ user?.name }}</span>
            <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
          </div>
          
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                個人資料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                設定
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                登出
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container class="layout-body">
      <!-- Sidebar -->
      <el-aside :width="sidebarWidth" class="layout-sidebar">
        <el-scrollbar>
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapsed"
            router
            class="sidebar-menu"
          >
            <template v-for="route in menuRoutes" :key="route.name">
              <el-menu-item
                v-if="!route.children"
                :index="route.path"
                :disabled="!hasPermission(route)"
              >
                <el-icon><component :is="route.meta?.icon" /></el-icon>
                <template #title>{{ route.meta?.title }}</template>
              </el-menu-item>
              
              <el-sub-menu
                v-else
                :index="route.path"
                :disabled="!hasPermission(route)"
              >
                <template #title>
                  <el-icon><component :is="route.meta?.icon" /></el-icon>
                  <span>{{ route.meta?.title }}</span>
                </template>
                
                <el-menu-item
                  v-for="child in route.children"
                  :key="child.name"
                  :index="child.path"
                  :disabled="!hasPermission(child)"
                >
                  {{ child.meta?.title }}
                </el-menu-item>
              </el-sub-menu>
            </template>
          </el-menu>
        </el-scrollbar>
      </el-aside>
      
      <!-- Main content -->
      <el-main class="layout-main">
        <!-- Breadcrumb -->
        <div class="breadcrumb-container">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              <router-link v-if="item.path" :to="item.path">
                {{ item.title }}
              </router-link>
              <span v-else>{{ item.title }}</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <!-- Page content -->
        <div class="page-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Expand,
  Fold,
  Bell,
  User,
  ArrowDown,
  Setting,
  SwitchButton,
  House,
  Document,
  DataAnalysis,
  OfficeBuilding,
  Tools
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const isCollapsed = ref(false)
const notificationCount = ref(3)

// Computed
const user = computed(() => authStore.user)
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '240px')
const activeMenu = computed(() => route.path)

// Get routes for menu
const menuRoutes = computed(() => {
  const routes = router.getRoutes()
  return routes
    .filter(route => route.meta?.showInMenu)
    .sort((a, b) => {
      const aGroup = a.meta?.group || 'main'
      const bGroup = b.meta?.group || 'main'
      if (aGroup !== bGroup) {
        return aGroup === 'main' ? -1 : 1
      }
      return 0
    })
})

// Breadcrumbs
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  const breadcrumbs = matched.map(item => ({
    title: item.meta?.title,
    path: item.path
  }))
  
  // Remove current page from breadcrumb path
  if (breadcrumbs.length > 0) {
    breadcrumbs[breadcrumbs.length - 1].path = undefined
  }
  
  return breadcrumbs
})

// Methods
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      await router.push('/profile')
      break
    case 'settings':
      await router.push('/admin/settings')
      break
    case 'logout':
      await authStore.logout()
      await router.push('/auth/login')
      break
  }
}

const hasPermission = (route: any) => {
  if (!route.meta) return true
  
  // Check roles
  if (route.meta.roles && !authStore.hasAnyRole(route.meta.roles)) {
    return false
  }
  
  // Check permissions
  if (route.meta.permissions && !authStore.hasAnyPermission(route.meta.permissions)) {
    return false
  }
  
  return true
}

// Watch for route changes to update document title
watch(
  () => route.meta.title,
  (title) => {
    if (title) {
      document.title = `${title} | HR 績效管理系統`
    }
  },
  { immediate: true }
)
</script>

<style lang="scss" scoped>
.default-layout {
  height: 100vh;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  
  .app-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #f3f4f6;
  }
  
  .user-name {
    font-weight: 500;
    color: #374151;
  }
  
  .dropdown-icon {
    font-size: 12px;
    color: #9ca3af;
  }
}

.layout-body {
  flex: 1;
  overflow: hidden;
}

.layout-sidebar {
  background: white;
  border-right: 1px solid #e5e7eb;
  transition: width 0.3s;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.layout-main {
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  padding: 0;
  overflow: hidden;
}

.breadcrumb-container {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.page-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

// Responsive design
@media (max-width: 768px) {
  .layout-header {
    padding: 0 16px;
  }
  
  .header-left .app-title {
    display: none;
  }
  
  .page-content {
    padding: 16px;
  }
  
  .breadcrumb-container {
    padding: 12px 16px;
  }
}
</style>