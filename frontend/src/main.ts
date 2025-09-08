import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// Styles
import 'element-plus/dist/index.css'
import '@/styles/main.scss'

// App components
import App from './App.vue'
import router from './router'

// Create app instance
const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  // Element Plus configuration
  size: 'default',
  zIndex: 3000,
})

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Global error handler
app.config.errorHandler = (error, vm, info) => {
  console.error('Global error:', error)
  console.error('Vue instance:', vm)  
  console.error('Error info:', info)
  
  // You can send error to monitoring service here
  // e.g., Sentry, LogRocket, etc.
}

// Mount app
app.mount('#app')