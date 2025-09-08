<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="logo">
            <h1>HR 績效管理系統</h1>
            <p class="subtitle">GOGOPEAKS.COM</p>
          </div>
        </div>
        <div class="auth-content">
          <router-view />
        </div>
        <div class="auth-footer">
          <p>&copy; 2024 GOGOPEAKS.COM. All rights reserved.</p>
        </div>
      </div>
    </div>
    
    <!-- Background decoration -->
    <div class="auth-background">
      <div class="bg-shape bg-shape-1"></div>
      <div class="bg-shape bg-shape-2"></div>
      <div class="bg-shape bg-shape-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Authentication layout for login page
</script>

<style lang="scss" scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.auth-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  z-index: 10;
  position: relative;
}

.auth-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.auth-header {
  padding: 2rem 2rem 1rem;
  text-align: center;
  background: linear-gradient(45deg, #f8fafc, #e2e8f0);
  
  .logo h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
  }
  
  .subtitle {
    margin: 0;
    color: #64748b;
    font-size: 0.875rem;
    font-weight: 500;
  }
}

.auth-content {
  padding: 2rem;
}

.auth-footer {
  padding: 1rem 2rem;
  text-align: center;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  
  p {
    margin: 0;
    color: #64748b;
    font-size: 0.75rem;
  }
}

.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
  
  &.bg-shape-1 {
    width: 200px;
    height: 200px;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &.bg-shape-2 {
    width: 150px;
    height: 150px;
    top: 60%;
    right: 10%;
    animation-delay: 2s;
  }
  
  &.bg-shape-3 {
    width: 100px;
    height: 100px;
    bottom: 20%;
    left: 60%;
    animation-delay: 4s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

// Responsive design
@media (max-width: 768px) {
  .auth-container {
    padding: 1rem;
    max-width: 100%;
  }
  
  .auth-content {
    padding: 1.5rem;
  }
  
  .auth-header {
    padding: 1.5rem 1.5rem 1rem;
    
    .logo h1 {
      font-size: 1.25rem;
    }
  }
}
</style>