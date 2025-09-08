<template>
  <div class="event-detail-page">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>
    
    <div v-else-if="event" class="event-content">
      <!-- Page header -->
      <div class="page-header">
        <div class="header-content">
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/events' }">事件管理</el-breadcrumb-item>
              <el-breadcrumb-item>事件詳情</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <h1>事件 #{{ event.id }}</h1>
        </div>
        <div class="header-actions">
          <el-button v-if="canEdit" type="primary" @click="editEvent">
            編輯
          </el-button>
          <el-button v-if="canApprove" type="success" @click="approveEvent">
            審核
          </el-button>
          <el-button @click="$router.go(-1)">返回</el-button>
        </div>
      </div>

      <!-- Event status and basic info -->
      <el-card class="event-summary">
        <div class="event-header">
          <div class="event-title">
            <h2>{{ event.title || event.rule_name }}</h2>
            <el-tag :type="getStatusType(event.status)" size="large">
              {{ getStatusLabel(event.status) }}
            </el-tag>
          </div>
          
          <div class="event-score">
            <div class="score-value" :class="getScoreClass(event.final_score)">
              {{ event.final_score > 0 ? '+' : '' }}{{ event.final_score }}
            </div>
            <div class="score-label">分數</div>
          </div>
        </div>
        
        <div class="event-meta">
          <div class="meta-row">
            <div class="meta-item">
              <span class="label">目標員工:</span>
              <span class="value">{{ event.user_name }} ({{ event.user_employee_id }})</span>
            </div>
            <div class="meta-item">
              <span class="label">建立者:</span>
              <span class="value">{{ event.reporter_name }}</span>
            </div>
          </div>
          
          <div class="meta-row">
            <div class="meta-item">
              <span class="label">發生日期:</span>
              <span class="value">{{ formatDate(event.occurred_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="label">建立時間:</span>
              <span class="value">{{ formatDateTime(event.created_at) }}</span>
            </div>
          </div>
          
          <div class="meta-row">
            <div class="meta-item">
              <span class="label">部門:</span>
              <span class="value">{{ event.department_name || '-' }}</span>
            </div>
            <div class="meta-item" v-if="event.project_name">
              <span class="label">專案:</span>
              <span class="value">{{ event.project_name }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Event details -->
      <el-row :gutter="20">
        <el-col :span="16">
          <!-- Description -->
          <el-card title="事件描述" class="detail-card">
            <div class="event-description">
              {{ event.description || '無描述' }}
            </div>
          </el-card>

          <!-- Rule information -->
          <el-card title="適用規則" class="detail-card">
            <div class="rule-info">
              <div class="rule-header">
                <h4>{{ event.rule_name }}</h4>
                <el-tag size="small">{{ event.rule_category }}</el-tag>
              </div>
              <div class="rule-details">
                <div class="detail-item">
                  <span class="label">規則代碼:</span>
                  <span class="value">{{ event.rule_code }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">基礎分數:</span>
                  <span class="value">{{ event.original_score }}</span>
                </div>
                <div class="detail-item" v-if="event.is_adjusted">
                  <span class="label">調整分數:</span>
                  <span class="value">{{ event.adjusted_score }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">最終分數:</span>
                  <span class="value" :class="getScoreClass(event.final_score)">
                    {{ event.final_score > 0 ? '+' : '' }}{{ event.final_score }}
                  </span>
                </div>
              </div>
              
              <div v-if="event.adjustment_reason" class="adjustment-reason">
                <h5>調整原因:</h5>
                <p>{{ event.adjustment_reason }}</p>
              </div>
            </div>
          </el-card>

          <!-- Evidence files -->
          <el-card v-if="event.evidence_urls && event.evidence_urls.length > 0" title="證據檔案" class="detail-card">
            <div class="evidence-list">
              <div 
                v-for="(url, index) in event.evidence_urls" 
                :key="index"
                class="evidence-item"
              >
                <div class="file-info">
                  <el-icon class="file-icon"><Document /></el-icon>
                  <span class="file-name">{{ getFileName(url) }}</span>
                </div>
                <div class="file-actions">
                  <el-button size="small" @click="previewFile(url)">預覽</el-button>
                  <el-button size="small" @click="downloadFile(url)">下載</el-button>
                </div>
              </div>
            </div>
          </el-card>
          
          <el-card v-else-if="event.needs_evidence" title="證據檔案" class="detail-card">
            <el-empty description="尚未上傳證據檔案">
              <el-button v-if="canEdit" type="primary" @click="uploadEvidence">
                上傳證據
              </el-button>
            </el-empty>
          </el-card>

          <!-- Review information -->
          <el-card v-if="event.reviewed_at" title="審核資訊" class="detail-card">
            <div class="review-info">
              <div class="review-header">
                <div class="reviewer">
                  <span class="label">審核者:</span>
                  <span class="value">{{ event.reviewer_name }}</span>
                </div>
                <div class="review-time">
                  <span class="label">審核時間:</span>
                  <span class="value">{{ formatDateTime(event.reviewed_at) }}</span>
                </div>
              </div>
              
              <div v-if="event.review_notes" class="review-notes">
                <h5>審核意見:</h5>
                <p>{{ event.review_notes }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- Sidebar -->
        <el-col :span="8">
          <!-- Quick actions -->
          <el-card title="快速操作" class="sidebar-card">
            <div class="quick-actions">
              <el-button 
                v-if="canEdit" 
                type="primary" 
                size="small" 
                block 
                @click="editEvent"
              >
                <el-icon><Edit /></el-icon>
                編輯事件
              </el-button>
              
              <el-button 
                v-if="canApprove" 
                type="success" 
                size="small" 
                block 
                @click="approveEvent"
              >
                <el-icon><Check /></el-icon>
                審核事件
              </el-button>
              
              <el-button 
                v-if="canDelete" 
                type="danger" 
                size="small" 
                block 
                @click="deleteEvent"
              >
                <el-icon><Delete /></el-icon>
                刪除事件
              </el-button>
              
              <el-button 
                size="small" 
                block 
                @click="exportEvent"
              >
                <el-icon><Download /></el-icon>
                匯出詳情
              </el-button>
            </div>
          </el-card>

          <!-- Event timeline -->
          <el-card title="事件時間軸" class="sidebar-card">
            <el-timeline>
              <el-timeline-item
                timestamp="建立時間"
                :hollow="false"
                type="primary"
              >
                <div class="timeline-content">
                  <p>{{ event.reporter_name }} 建立了這個事件</p>
                  <span class="timeline-time">{{ formatDateTime(event.created_at) }}</span>
                </div>
              </el-timeline-item>
              
              <el-timeline-item
                v-if="event.updated_at && event.updated_at !== event.created_at"
                timestamp="最後更新"
                :hollow="false"
                type="warning"
              >
                <div class="timeline-content">
                  <p>事件已更新</p>
                  <span class="timeline-time">{{ formatDateTime(event.updated_at) }}</span>
                </div>
              </el-timeline-item>
              
              <el-timeline-item
                v-if="event.reviewed_at"
                :timestamp="event.status === 'approved' ? '已核准' : '已拒絕'"
                :hollow="false"
                :type="event.status === 'approved' ? 'success' : 'danger'"
              >
                <div class="timeline-content">
                  <p>{{ event.reviewer_name }} {{ event.status === 'approved' ? '核准' : '拒絕' }}了這個事件</p>
                  <span class="timeline-time">{{ formatDateTime(event.reviewed_at) }}</span>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>

          <!-- Related information -->
          <el-card v-if="event.source_metadata" title="來源資訊" class="sidebar-card">
            <div class="source-info">
              <div class="info-item" v-if="event.source">
                <span class="label">來源系統:</span>
                <span class="value">{{ event.source }}</span>
              </div>
              <div class="info-item" v-if="event.external_id">
                <span class="label">外部 ID:</span>
                <span class="value">{{ event.external_id }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Approval dialog -->
    <el-dialog
      v-model="approvalDialog.visible"
      title="審核事件"
      width="500px"
      @close="closeApprovalDialog"
    >
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Edit,
  Check,
  Delete,
  Download
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(true)
const event = ref(null)

const approvalDialog = reactive({
  visible: false,
  loading: false
})

const approvalForm = reactive({
  status: 'approved',
  review_notes: ''
})

const approvalRules = {
  status: [{ required: true, message: '請選擇審核結果', trigger: 'change' }]
}

// Computed
const canEdit = computed(() => {
  if (!event.value) return false
  return (
    !event.value.is_locked &&
    (
      authStore.hasRole('admin') ||
      (event.value.status === 'draft' && event.value.reporter_id === authStore.user?.id)
    )
  )
})

const canApprove = computed(() => {
  if (!event.value) return false
  return (
    event.value.status === 'pending' &&
    authStore.hasAnyRole(['manager', 'admin']) &&
    event.value.can_approve
  )
})

const canDelete = computed(() => {
  if (!event.value) return false
  return (
    authStore.hasRole('admin') ||
    (event.value.status === 'draft' && event.value.reporter_id === authStore.user?.id)
  )
})

// Methods
const loadEvent = async () => {
  loading.value = true
  try {
    const eventId = route.params.id
    
    // TODO: Replace with actual API call
    // const response = await eventApi.getEvent(eventId)
    // event.value = response.data
    
    // Mock data for now
    event.value = {
      id: parseInt(eventId),
      title: '優秀專案表現',
      description: '在專案 A 中表現優異，獲得客戶好評，提前完成所有預定目標。',
      user_id: 1,
      user_name: '張三',
      user_employee_id: 'E001',
      reporter_id: 2,
      reporter_name: '李經理',
      reviewer_name: '王總監',
      department_name: '技術部',
      project_name: '專案 A',
      rule_id: 1,
      rule_name: '優秀表現',
      rule_code: 'GOOD_PERF',
      rule_category: 'positive',
      original_score: 10,
      adjusted_score: null,
      final_score: 10,
      status: 'approved',
      occurred_at: '2024-01-15T00:00:00Z',
      created_at: '2024-01-16T09:00:00Z',
      updated_at: '2024-01-16T09:00:00Z',
      reviewed_at: '2024-01-16T14:30:00Z',
      review_notes: '表現確實優秀，值得嘉獎',
      evidence_urls: [
        'https://drive.synology.com/hr-evidence/event_1/report.pdf',
        'https://drive.synology.com/hr-evidence/event_1/feedback.docx'
      ],
      evidence_count: 2,
      needs_evidence: true,
      has_sufficient_evidence: true,
      can_approve: false,
      is_adjusted: false,
      is_locked: true,
      source: 'manual',
      external_id: null,
      source_metadata: null
    }
    
  } catch (error) {
    ElMessage.error('載入事件詳情失敗')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD')
}

const formatDateTime = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
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

const getFileName = (url: string) => {
  return url.split('/').pop() || 'unknown'
}

const editEvent = () => {
  router.push(`/events/${event.value.id}/edit`)
}

const approveEvent = () => {
  approvalForm.status = 'approved'
  approvalForm.review_notes = ''
  approvalDialog.visible = true
}

const deleteEvent = async () => {
  try {
    await ElMessageBox.confirm('確定要刪除這個事件嗎？', '確認刪除', {
      confirmButtonText: '刪除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // TODO: Replace with actual API call
    // await eventApi.deleteEvent(event.value.id)
    
    ElMessage.success('事件已刪除')
    router.push('/events')
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('刪除失敗')
    }
  }
}

const exportEvent = () => {
  // TODO: Implement export functionality
  ElMessage.info('匯出功能開發中')
}

const uploadEvidence = () => {
  router.push(`/events/${event.value.id}/edit`)
}

const previewFile = (url: string) => {
  window.open(url, '_blank')
}

const downloadFile = (url: string) => {
  const link = document.createElement('a')
  link.href = url
  link.download = getFileName(url)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const closeApprovalDialog = () => {
  approvalDialog.visible = false
  approvalDialog.loading = false
}

const submitApproval = async () => {
  approvalDialog.loading = true
  try {
    // TODO: Replace with actual API call
    // await eventApi.approveEvent(event.value.id, approvalForm)
    
    ElMessage.success(
      approvalForm.status === 'approved' ? '事件已核准' : '事件已拒絕'
    )
    
    closeApprovalDialog()
    await loadEvent()
    
  } catch (error) {
    ElMessage.error('審核失敗')
  } finally {
    approvalDialog.loading = false
  }
}

// Lifecycle
onMounted(() => {
  loadEvent()
})
</script>

<style lang="scss" scoped>
.event-detail-page {
  .loading-container {
    padding: 2rem;
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    
    .header-content {
      .breadcrumb {
        margin-bottom: 0.5rem;
      }
      
      h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
      }
    }
  }
  
  .event-summary {
    margin-bottom: 1.5rem;
    
    .event-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1rem;
      
      .event-title {
        flex: 1;
        
        h2 {
          margin: 0 0 0.5rem;
          font-size: 1.25rem;
          color: #1f2937;
        }
      }
      
      .event-score {
        text-align: center;
        padding: 0.5rem;
        
        .score-value {
          font-size: 2rem;
          font-weight: bold;
          line-height: 1;
        }
        
        .score-label {
          font-size: 0.875rem;
          color: #6b7280;
          margin-top: 0.25rem;
        }
      }
    }
    
    .event-meta {
      .meta-row {
        display: flex;
        gap: 2rem;
        margin-bottom: 0.5rem;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
      
      .meta-item {
        display: flex;
        align-items: center;
        
        .label {
          font-weight: 500;
          color: #6b7280;
          margin-right: 0.5rem;
        }
        
        .value {
          color: #1f2937;
        }
      }
    }
  }
  
  .detail-card {
    margin-bottom: 1.5rem;
    
    .event-description {
      line-height: 1.6;
      color: #1f2937;
    }
    
    .rule-info {
      .rule-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        
        h4 {
          margin: 0;
          color: #1f2937;
        }
      }
      
      .rule-details {
        .detail-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
          
          .label {
            color: #6b7280;
          }
          
          .value {
            font-weight: 500;
          }
        }
      }
      
      .adjustment-reason {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
        
        h5 {
          margin: 0 0 0.5rem;
          color: #1f2937;
        }
        
        p {
          margin: 0;
          color: #6b7280;
          line-height: 1.6;
        }
      }
    }
    
    .evidence-list {
      .evidence-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .file-info {
          display: flex;
          align-items: center;
          
          .file-icon {
            margin-right: 0.5rem;
            color: #6b7280;
          }
          
          .file-name {
            color: #1f2937;
          }
        }
        
        .file-actions {
          display: flex;
          gap: 0.5rem;
        }
      }
    }
    
    .review-info {
      .review-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        
        .reviewer, .review-time {
          .label {
            color: #6b7280;
            margin-right: 0.5rem;
          }
          
          .value {
            color: #1f2937;
            font-weight: 500;
          }
        }
      }
      
      .review-notes {
        h5 {
          margin: 0 0 0.5rem;
          color: #1f2937;
        }
        
        p {
          margin: 0;
          color: #6b7280;
          line-height: 1.6;
        }
      }
    }
  }
  
  .sidebar-card {
    margin-bottom: 1.5rem;
    
    .quick-actions {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .timeline-content {
      p {
        margin: 0 0 0.25rem;
        color: #1f2937;
        font-size: 0.875rem;
      }
      
      .timeline-time {
        color: #6b7280;
        font-size: 0.75rem;
      }
    }
    
    .source-info {
      .info-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .label {
          color: #6b7280;
        }
        
        .value {
          color: #1f2937;
          font-weight: 500;
        }
      }
    }
  }
}

.text-success {
  color: #16a34a;
}

.text-danger {
  color: #dc2626;
}

.text-info {
  color: #6b7280;
}
</style>