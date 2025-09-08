<template>
  <div class="event-list-page">
    <!-- Page header -->
    <div class="page-header">
      <div class="header-content">
        <h1>事件管理</h1>
        <p>管理績效事件，包括建立、審核和追蹤</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="$router.push('/events/create')">
          新增事件
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="狀態">
          <el-select v-model="filters.status" placeholder="所有狀態" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="待審核" value="pending" />
            <el-option label="已核准" value="approved" />
            <el-option label="已拒絕" value="rejected" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期範圍">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="開始日期"
            end-placeholder="結束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="搜尋">
          <el-input
            v-model="filters.search"
            placeholder="事件標題或描述"
            :prefix-icon="Search"
            style="width: 200px"
            clearable
            @keyup.enter="loadEvents"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadEvents">搜尋</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Events table -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="events"
        stripe
        @row-click="handleRowClick"
        style="cursor: pointer"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="事件資訊" min-width="200">
          <template #default="{ row }">
            <div class="event-info">
              <div class="event-title">{{ row.title || row.rule_name }}</div>
              <div class="event-meta">
                {{ row.user_name }} · {{ formatDate(row.occurred_at) }}
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="department_name" label="部門" width="120" />
        
        <el-table-column label="分數" width="80" align="center">
          <template #default="{ row }">
            <span :class="getScoreClass(row.final_score)">
              {{ row.final_score > 0 ? '+' : '' }}{{ row.final_score }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="狀態" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="證據" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.evidence_count > 0" color="#67c23a">
              <DocumentChecked />
            </el-icon>
            <el-icon v-else-if="row.needs_evidence" color="#f56c6c">
              <Document />
            </el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="建立時間" width="120">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button
              v-if="canApprove(row)"
              type="success"
              size="small"
              @click.stop="approveEvent(row)"
            >
              審核
            </el-button>
            <el-button
              v-if="canEdit(row)"
              type="primary"
              size="small"
              @click.stop="editEvent(row)"
            >
              編輯
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :small="false"
          :disabled="loading"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="loadEvents"
          @current-change="loadEvents"
        />
      </div>
    </el-card>

    <!-- Approval dialog -->
    <el-dialog
      v-model="approvalDialog.visible"
      title="審核事件"
      width="500px"
      @close="closeApprovalDialog"
    >
      <div v-if="approvalDialog.event" class="approval-content">
        <div class="event-summary">
          <h4>{{ approvalDialog.event.title || approvalDialog.event.rule_name }}</h4>
          <p>{{ approvalDialog.event.description }}</p>
          <div class="event-details">
            <span>員工: {{ approvalDialog.event.user_name }}</span>
            <span>分數: {{ approvalDialog.event.final_score }}</span>
            <span>日期: {{ formatDate(approvalDialog.event.occurred_at) }}</span>
          </div>
        </div>
        
        <el-form :model="approvalForm" :rules="approvalRules">
          <el-form-item label="審核結果" prop="status">
            <el-radio-group v-model="approvalForm.status">
              <el-radio label="approved">核准</el-radio>
              <el-radio label="rejected">拒絕</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="審核備註">
            <el-input
              v-model="approvalForm.review_notes"
              type="textarea"
              :rows="3"
              placeholder="請輸入審核意見（可選）"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeApprovalDialog">取消</el-button>
          <el-button
            type="primary"
            :loading="approvalDialog.loading"
            @click="submitApproval"
          >
            提交審核
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Document,
  DocumentChecked
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(false)
const events = ref([])

const filters = reactive({
  status: '',
  dateRange: null,
  search: ''
})

const pagination = reactive({
  current: 1,
  size: 20,
  total: 0
})

const approvalDialog = reactive({
  visible: false,
  event: null,
  loading: false
})

const approvalForm = reactive({
  status: 'approved',
  review_notes: ''
})

const approvalRules = {
  status: [{ required: true, message: '請選擇審核結果', trigger: 'change' }]
}

// Methods
const loadEvents = async () => {
  loading.value = true
  try {
    // TODO: Call API to load events
    // const response = await eventApi.getEvents({
    //   skip: (pagination.current - 1) * pagination.size,
    //   limit: pagination.size,
    //   status_filter: filters.status || undefined,
    //   date_from: filters.dateRange?.[0],
    //   date_to: filters.dateRange?.[1],
    //   search: filters.search || undefined
    // })
    
    // Mock data for now
    events.value = []
    pagination.total = 0
    
  } catch (error) {
    ElMessage.error('載入事件列表失敗')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.status = ''
  filters.dateRange = null
  filters.search = ''
  pagination.current = 1
  loadEvents()
}

const handleRowClick = (row: any) => {
  router.push(`/events/${row.id}`)
}

const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD')
}

const formatDateTime = (dateString: string) => {
  return dayjs(dateString).format('MM-DD HH:mm')
}

const getScoreClass = (score: number) => {
  if (score > 0) return 'text-success'
  if (score < 0) return 'text-danger'
  return 'text-info'
}

const getStatusType = (status: string) => {
  const statusMap = {
    draft: '',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    archived: 'info'
  }
  return statusMap[status] || ''
}

const getStatusLabel = (status: string) => {
  const labelMap = {
    draft: '草稿',
    pending: '待審核',
    approved: '已核准',
    rejected: '已拒絕',
    archived: '已封存'
  }
  return labelMap[status] || status
}

const canApprove = (event: any) => {
  return (
    event.status === 'pending' &&
    authStore.hasAnyRole(['manager', 'admin']) &&
    event.can_approve
  )
}

const canEdit = (event: any) => {
  return (
    !event.is_locked &&
    (
      authStore.hasRole('admin') ||
      (event.status === 'draft' && event.reporter_id === authStore.user?.id)
    )
  )
}

const approveEvent = (event: any) => {
  approvalDialog.event = event
  approvalForm.status = 'approved'
  approvalForm.review_notes = ''
  approvalDialog.visible = true
}

const editEvent = (event: any) => {
  router.push(`/events/${event.id}/edit`)
}

const closeApprovalDialog = () => {
  approvalDialog.visible = false
  approvalDialog.event = null
  approvalDialog.loading = false
}

const submitApproval = async () => {
  if (!approvalDialog.event) return
  
  approvalDialog.loading = true
  try {
    // TODO: Call API to approve/reject event
    // await eventApi.approveEvent(approvalDialog.event.id, approvalForm)
    
    ElMessage.success(
      approvalForm.status === 'approved' ? '事件已核准' : '事件已拒絕'
    )
    
    closeApprovalDialog()
    await loadEvents()
    
  } catch (error) {
    ElMessage.error('審核失敗')
    console.error(error)
  } finally {
    approvalDialog.loading = false
  }
}

// Lifecycle
onMounted(() => {
  loadEvents()
})
</script>

<style lang="scss" scoped>
.event-list-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    
    .header-content {
      h1 {
        margin: 0 0 0.5rem;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
      }
      
      p {
        margin: 0;
        color: #6b7280;
      }
    }
  }
  
  .filter-card {
    margin-bottom: 1.5rem;
  }
  
  .event-info {
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
  
  .pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
  }
  
  .approval-content {
    .event-summary {
      background: #f9fafb;
      padding: 1rem;
      border-radius: 6px;
      margin-bottom: 1rem;
      
      h4 {
        margin: 0 0 0.5rem;
        font-size: 1rem;
        color: #1f2937;
      }
      
      p {
        margin: 0 0 0.75rem;
        color: #4b5563;
        font-size: 0.875rem;
      }
      
      .event-details {
        display: flex;
        gap: 1rem;
        font-size: 0.875rem;
        color: #6b7280;
      }
    }
  }
}

.text-success {
  color: #16a34a;
  font-weight: 500;
}

.text-danger {
  color: #dc2626;
  font-weight: 500;
}

.text-info {
  color: #6b7280;
  font-weight: 500;
}
</style>