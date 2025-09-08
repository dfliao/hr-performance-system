<template>
  <div class="dashboard">
    <!-- Welcome section -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>歡迎回來，{{ user?.name }}</h1>
        <p>今天是 {{ currentDate }}，以下是您的績效概況</p>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" :icon="Plus" @click="$router.push('/events/create')">
          新增事件
        </el-button>
      </div>
    </div>

    <!-- Key metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon success">
          <el-icon><TrendChartUp /></el-icon>
        </div>
        <div class="metric-content">
          <h3>本月總分</h3>
          <div class="metric-value">{{ monthlyScore }}</div>
          <div class="metric-change positive">
            <el-icon><ArrowUp /></el-icon>
            +5.2 與上月比較
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon warning">
          <el-icon><Document /></el-icon>
        </div>
        <div class="metric-content">
          <h3>待審核事件</h3>
          <div class="metric-value">{{ pendingEvents }}</div>
          <div class="metric-change">
            本月新增 {{ newEventsThisMonth }} 筆
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon info">
          <el-icon><User /></el-icon>
        </div>
        <div class="metric-content">
          <h3>部門排名</h3>
          <div class="metric-value">{{ departmentRank }}/{{ totalDepartmentUsers }}</div>
          <div class="metric-change">
            在 {{ user?.department_name || '未設定部門' }}
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon primary">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="metric-content">
          <h3>績效等級</h3>
          <div class="metric-value grade-display" :class="gradeClass">{{ performanceGrade }}</div>
          <div class="metric-change">
            目標: A 級以上
          </div>
        </div>
      </div>
    </div>

    <!-- Content sections -->
    <el-row :gutter="24" class="content-row">
      <!-- Recent events -->
      <el-col :lg="12" :md="24">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>最近事件</h3>
              <el-button text @click="$router.push('/events')">
                查看全部 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div v-if="recentEvents.length === 0" class="empty-state">
            <el-icon class="empty-icon"><DocumentCopy /></el-icon>
            <p>暫無最近事件</p>
            <el-button type="primary" @click="$router.push('/events/create')">
              建立第一個事件
            </el-button>
          </div>
          
          <div v-else class="events-list">
            <div
              v-for="event in recentEvents"
              :key="event.id"
              class="event-item"
              @click="$router.push(`/events/${event.id}`)"
            >
              <div class="event-info">
                <div class="event-title">{{ event.title || event.rule_name }}</div>
                <div class="event-meta">
                  {{ formatDate(event.occurred_at) }} · {{ event.source_label }}
                </div>
              </div>
              <div class="event-score" :class="event.score_class">
                {{ event.score > 0 ? '+' : '' }}{{ event.score }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Performance trend chart -->
      <el-col :lg="12" :md="24">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>績效趨勢</h3>
              <el-button text @click="$router.push('/reports/personal')">
                詳細報表 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="chart-container">
            <div v-if="trendData.length === 0" class="empty-state">
              <el-icon class="empty-icon"><DataAnalysis /></el-icon>
              <p>暫無績效數據</p>
            </div>
            <div v-else class="trend-chart">
              <!-- This would be replaced with actual chart component -->
              <div class="chart-placeholder">
                <p>績效趨勢圖表</p>
                <p class="chart-note">最近 6 個月的績效變化</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quick actions -->
    <el-card class="quick-actions-card">
      <template #header>
        <h3>快速操作</h3>
      </template>
      
      <div class="quick-actions">
        <div class="action-item" @click="$router.push('/events/create')">
          <el-icon class="action-icon"><Plus /></el-icon>
          <div class="action-content">
            <h4>新增績效事件</h4>
            <p>記錄工作表現和成就</p>
          </div>
        </div>
        
        <div class="action-item" @click="$router.push('/reports/personal')">
          <el-icon class="action-icon"><DataAnalysis /></el-icon>
          <div class="action-content">
            <h4>檢視個人報表</h4>
            <p>查看詳細的績效分析</p>
          </div>
        </div>
        
        <div 
          v-if="user?.role === 'manager' || user?.role === 'admin'"
          class="action-item" 
          @click="$router.push('/events?status=pending')"
        >
          <el-icon class="action-icon"><DocumentChecked /></el-icon>
          <div class="action-content">
            <h4>審核待辦事項</h4>
            <p>處理團隊成員的事件申請</p>
          </div>
        </div>
        
        <div 
          v-if="user?.role === 'admin'"
          class="action-item" 
          @click="$router.push('/admin/settings')"
        >
          <el-icon class="action-icon"><Setting /></el-icon>
          <div class="action-content">
            <h4>系統管理</h4>
            <p>管理規則、用戶和系統設定</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'
import {
  Plus,
  TrendChartUp,
  Document,
  User,
  Medal,
  ArrowRight,
  ArrowUp,
  DocumentCopy,
  DataAnalysis,
  DocumentChecked,
  Setting
} from '@element-plus/icons-vue'

const authStore = useAuthStore()

// State
const monthlyScore = ref(78.5)
const pendingEvents = ref(3)
const newEventsThisMonth = ref(8)
const departmentRank = ref(5)
const totalDepartmentUsers = ref(23)
const performanceGrade = ref('B+')
const recentEvents = ref([])
const trendData = ref([])

// Computed
const user = computed(() => authStore.user)
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))
const gradeClass = computed(() => {
  const grade = performanceGrade.value
  if (grade.includes('A')) return 'grade-a'
  if (grade.includes('B')) return 'grade-b'
  if (grade.includes('C')) return 'grade-c'
  return 'grade-d'
})

// Methods
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('MM/DD')
}

const loadDashboardData = async () => {
  try {
    // Load dashboard data from API
    // This is placeholder - will be replaced with actual API calls
    console.log('Loading dashboard data...')
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  
  .welcome-text {
    h1 {
      margin: 0 0 0.5rem;
      font-size: 1.75rem;
      font-weight: 600;
    }
    
    p {
      margin: 0;
      opacity: 0.9;
      font-size: 1rem;
    }
  }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  
  &.success {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
  }
  
  &.warning {
    background: rgba(251, 191, 36, 0.1);
    color: #fbbf24;
  }
  
  &.info {
    background: rgba(107, 114, 128, 0.1);
    color: #6b7280;
  }
  
  &.primary {
    background: rgba(37, 99, 235, 0.1);
    color: #2563eb;
  }
}

.metric-content {
  flex: 1;
  
  h3 {
    margin: 0 0 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }
  
  .metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.25rem;
    
    &.grade-display {
      &.grade-a { color: #22c55e; }
      &.grade-b { color: #fbbf24; }
      &.grade-c { color: #f59e0b; }
      &.grade-d { color: #ef4444; }
    }
  }
  
  .metric-change {
    font-size: 0.875rem;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    
    &.positive {
      color: #22c55e;
    }
  }
}

.content-row {
  margin-bottom: 2rem;
}

.section-card {
  height: 400px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 600;
      color: #1f2937;
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #6b7280;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 1rem;
    opacity: 0.5;
  }
  
  p {
    margin: 0 0 1rem;
    font-size: 1rem;
  }
}

.events-list {
  .event-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #f3f4f6;
    cursor: pointer;
    transition: background-color 0.2s;
    border-radius: 6px;
    
    &:hover {
      background-color: #f9fafb;
    }
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .event-info {
    flex: 1;
    
    .event-title {
      font-weight: 500;
      color: #1f2937;
      margin-bottom: 0.25rem;
    }
    
    .event-meta {
      font-size: 0.875rem;
      color: #6b7280;
    }
  }
  
  .event-score {
    font-size: 1.125rem;
    font-weight: 600;
    
    &.positive { color: #22c55e; }
    &.negative { color: #ef4444; }
    &.neutral { color: #6b7280; }
  }
}

.chart-container {
  height: 250px;
  
  .chart-placeholder {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    
    p {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 500;
    }
    
    .chart-note {
      font-size: 0.875rem;
      opacity: 0.7;
    }
  }
}

.quick-actions-card {
  .quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }
  
  .action-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: #2563eb;
      background-color: #f8fafc;
    }
  }
  
  .action-icon {
    width: 40px;
    height: 40px;
    background: #f3f4f6;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #2563eb;
  }
  
  .action-content {
    h4 {
      margin: 0 0 0.25rem;
      font-size: 1rem;
      font-weight: 500;
      color: #1f2937;
    }
    
    p {
      margin: 0;
      font-size: 0.875rem;
      color: #6b7280;
    }
  }
}

// Responsive design
@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-card {
    padding: 1rem;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>