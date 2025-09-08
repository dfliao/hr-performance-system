<template>
  <div class="login-form">
    <div class="form-header">
      <h2>登入系統</h2>
      <p>請輸入您的帳號密碼以存取 HR 績效管理系統</p>
    </div>
    
    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="loginRules"
      size="large"
      @submit.prevent="handleLogin"
    >
      <el-form-item prop="username">
        <el-input
          v-model="loginForm.username"
          :prefix-icon="User"
          placeholder="使用者帳號"
          clearable
          @keyup.enter="handleLogin"
        />
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          :prefix-icon="Lock"
          type="password"
          placeholder="密碼"
          show-password
          clearable
          @keyup.enter="handleLogin"
        />
      </el-form-item>
      
      <el-form-item>
        <div class="form-options">
          <el-checkbox v-model="rememberMe">記住我</el-checkbox>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          :loading="isLoading"
          :disabled="!isFormValid"
          class="login-button"
          @click="handleLogin"
        >
          <span v-if="!isLoading">登入</span>
          <span v-else>登入中...</span>
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- Error message -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="false"
      class="error-alert"
      show-icon
    />
    
    <!-- Login help -->
    <div class="login-help">
      <el-divider>需要協助？</el-divider>
      <p class="help-text">
        如果您忘記密碼或無法登入，請聯繫 IT 部門或系統管理員。
      </p>
      <p class="help-contact">
        <el-icon><Message /></el-icon>
        Email: it@gogopeaks.com
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Refs
const loginFormRef = ref<FormInstance>()

// State
const loginForm = reactive({
  username: '',
  password: ''
})

const rememberMe = ref(false)

// Computed
const isLoading = computed(() => authStore.isLoading)
const errorMessage = computed(() => authStore.loginError)
const isFormValid = computed(() => 
  loginForm.username.trim() && loginForm.password.trim()
)

// Form validation rules
const loginRules = {
  username: [
    { required: true, message: '請輸入使用者帳號', trigger: 'blur' },
    { min: 2, max: 50, message: '帳號長度應在 2 到 50 個字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '請輸入密碼', trigger: 'blur' },
    { min: 6, message: '密碼至少需要 6 個字符', trigger: 'blur' }
  ]
}

// Methods
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // Validate form
    await loginFormRef.value.validate()
    
    // Attempt login
    await authStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password
    })
    
    // Success message
    ElMessage.success({
      message: `歡迎回來，${authStore.user?.name}！`,
      duration: 2000
    })
    
    // Redirect to intended page or dashboard
    const redirectTo = (route.query.redirect as string) || '/'
    await router.push(redirectTo)
    
  } catch (error) {
    console.error('Login error:', error)
    // Error is handled by auth store and displayed in template
  }
}

// Auto-focus username input
onMounted(() => {
  // Focus on first input after a short delay
  setTimeout(() => {
    const usernameInput = document.querySelector('input[placeholder="使用者帳號"]') as HTMLInputElement
    if (usernameInput) {
      usernameInput.focus()
    }
  }, 300)
  
  // Check if already authenticated
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style lang="scss" scoped>
.login-form {
  width: 100%;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
  
  h2 {
    margin: 0 0 0.5rem;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }
  
  p {
    margin: 0;
    color: #64748b;
    font-size: 0.875rem;
    line-height: 1.5;
  }
}

.form-options {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
}

.error-alert {
  margin-top: 1rem;
  
  :deep(.el-alert__content) {
    text-align: left;
  }
}

.login-help {
  margin-top: 2rem;
  text-align: center;
  
  .help-text {
    margin: 1rem 0;
    color: #64748b;
    font-size: 0.875rem;
    line-height: 1.5;
  }
  
  .help-contact {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin: 0;
    color: #2563eb;
    font-size: 0.875rem;
    font-weight: 500;
  }
}

// Element Plus customizations
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:focus),
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

:deep(.el-button--primary) {
  background: linear-gradient(45deg, #2563eb, #3b82f6);
  border: none;
  border-radius: 6px;
  
  &:hover {
    background: linear-gradient(45deg, #1d4ed8, #2563eb);
  }
  
  &:active {
    background: linear-gradient(45deg, #1e40af, #1d4ed8);
  }
}

:deep(.el-divider__text) {
  color: #9ca3af;
  font-size: 0.875rem;
}

// Loading state
.login-button.is-loading {
  pointer-events: none;
}

// Animation for form appearance
.login-form {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Responsive adjustments
@media (max-width: 480px) {
  .form-header h2 {
    font-size: 1.25rem;
  }
  
  .login-button {
    height: 44px;
  }
}
</style>