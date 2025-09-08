<template>
  <div class="event-create-page">
    <!-- Page header -->
    <div class="page-header">
      <div class="header-content">
        <h1>新增績效事件</h1>
        <p>建立新的績效事件記錄</p>
      </div>
      <div class="header-actions">
        <el-button @click="$router.go(-1)">返回</el-button>
      </div>
    </div>

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        @submit.prevent="submitForm"
      >
        <!-- User selection -->
        <el-form-item label="目標員工" prop="user_id">
          <el-select
            v-model="form.user_id"
            placeholder="選擇員工"
            filterable
            remote
            :remote-method="searchUsers"
            :loading="loadingUsers"
            style="width: 100%"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="`${user.name} (${user.employee_id})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <!-- Rule selection -->
        <el-form-item label="適用規則" prop="rule_id">
          <el-select
            v-model="form.rule_id"
            placeholder="選擇規則"
            @change="handleRuleChange"
            style="width: 100%"
          >
            <el-option
              v-for="rule in rules"
              :key="rule.id"
              :label="`${rule.name} (${rule.base_score > 0 ? '+' : ''}${rule.base_score}分)`"
              :value="rule.id"
            />
          </el-select>
        </el-form-item>

        <!-- Selected rule info -->
        <div v-if="selectedRule" class="rule-info">
          <el-alert
            :title="`${selectedRule.name}`"
            :description="selectedRule.description"
            type="info"
            show-icon
            :closable="false"
          >
            <template #default>
              <div class="rule-details">
                <p><strong>基礎分數：</strong>{{ selectedRule.base_score }}</p>
                <p><strong>權重：</strong>{{ selectedRule.weight }}</p>
                <p><strong>計算分數：</strong>{{ calculateScore }}</p>
                <p v-if="selectedRule.evidence_required" class="text-warning">
                  <el-icon><Warning /></el-icon>
                  此規則需要提供證據檔案
                </p>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- Event details -->
        <el-form-item label="事件標題" prop="title">
          <el-input
            v-model="form.title"
            placeholder="輸入事件標題"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="事件描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="詳細描述事件內容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="發生日期" prop="occurred_at">
          <el-date-picker
            v-model="form.occurred_at"
            type="date"
            placeholder="選擇發生日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            style="width: 200px"
          />
        </el-form-item>

        <!-- Project selection (optional) -->
        <el-form-item label="相關專案">
          <el-select
            v-model="form.project_id"
            placeholder="選擇專案（可選）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <!-- Evidence upload -->
        <el-form-item 
          label="證據檔案" 
          :prop="selectedRule?.evidence_required ? 'evidence_urls' : undefined"
        >
          <div class="upload-section">
            <el-upload
              ref="uploadRef"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :data="uploadData"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :on-remove="handleRemoveFile"
              :file-list="fileList"
              :accept="allowedFileTypes"
              :limit="maxFiles"
              multiple
              list-type="text"
            >
              <el-button type="primary" :icon="Upload">上傳檔案</el-button>
              <template #tip>
                <div class="upload-tip">
                  支援格式：{{ allowedFileTypesText }}，單檔最大 {{ maxFileSizeMB }}MB
                </div>
              </template>
            </el-upload>
          </div>
        </el-form-item>

        <!-- Source metadata (for system integrations) -->
        <el-form-item v-if="showAdvanced" label="來源資訊">
          <el-input
            v-model="form.external_id"
            placeholder="外部系統 ID"
          />
        </el-form-item>

        <!-- Form actions -->
        <el-form-item>
          <div class="form-actions">
            <el-button @click="$router.go(-1)">取消</el-button>
            <el-button 
              type="info" 
              @click="saveAsDraft"
              :loading="submitting"
            >
              儲存草稿
            </el-button>
            <el-button 
              type="primary" 
              @click="submitForm"
              :loading="submitting"
            >
              提交審核
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Upload, Warning } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

interface User {
  id: number
  name: string
  employee_id: string
  department_id: number
}

interface Rule {
  id: number
  name: string
  description: string
  base_score: number
  weight: number
  evidence_required: boolean
  category: string
}

interface Project {
  id: number
  name: string
  code: string
}

const router = useRouter()
const authStore = useAuthStore()

// State
const formRef = ref<FormInstance>()
const uploadRef = ref()
const submitting = ref(false)
const loadingUsers = ref(false)
const users = ref<User[]>([])
const rules = ref<Rule[]>([])
const projects = ref<Project[]>([])
const fileList = ref([])
const showAdvanced = ref(false)

const form = reactive({
  user_id: null,
  rule_id: null,
  title: '',
  description: '',
  occurred_at: dayjs().format('YYYY-MM-DD'),
  project_id: null,
  evidence_urls: [],
  external_id: ''
})

const selectedRule = computed(() => {
  return rules.value.find(rule => rule.id === form.rule_id)
})

const calculateScore = computed(() => {
  if (!selectedRule.value) return 0
  return selectedRule.value.base_score * selectedRule.value.weight
})

// Upload configuration
const uploadUrl = computed(() => `${import.meta.env.VITE_API_URL}/api/files/upload`)
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))
const uploadData = computed(() => ({
  event_id: 'new',
  user_id: form.user_id
}))
const allowedFileTypes = '.jpg,.jpeg,.png,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt'
const allowedFileTypesText = 'JPG, PNG, PDF, Word, Excel, PowerPoint, TXT'
const maxFiles = 10
const maxFileSizeMB = 10

// Form validation rules
const rules = {
  user_id: [
    { required: true, message: '請選擇目標員工', trigger: 'change' }
  ],
  rule_id: [
    { required: true, message: '請選擇適用規則', trigger: 'change' }
  ],
  title: [
    { required: true, message: '請輸入事件標題', trigger: 'blur' },
    { min: 2, max: 200, message: '標題長度應在 2 到 200 個字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '請輸入事件描述', trigger: 'blur' },
    { min: 10, max: 1000, message: '描述長度應在 10 到 1000 個字符', trigger: 'blur' }
  ],
  occurred_at: [
    { required: true, message: '請選擇發生日期', trigger: 'change' }
  ],
  evidence_urls: [
    {
      validator: (rule, value, callback) => {
        if (selectedRule.value?.evidence_required && (!value || value.length === 0)) {
          callback(new Error('此規則需要上傳證據檔案'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// Methods
const loadUsers = async () => {
  try {
    // TODO: Replace with actual API call
    // const response = await userApi.getUsers()
    // users.value = response.data
    
    // Mock data for now
    users.value = [
      { id: 1, name: '張三', employee_id: 'E001', department_id: 1 },
      { id: 2, name: '李四', employee_id: 'E002', department_id: 1 },
      { id: 3, name: '王五', employee_id: 'E003', department_id: 2 }
    ]
  } catch (error) {
    ElMessage.error('載入員工清單失敗')
  }
}

const searchUsers = async (query: string) => {
  if (query) {
    loadingUsers.value = true
    try {
      // TODO: Replace with actual API call
      // const response = await userApi.searchUsers(query)
      // users.value = response.data
      
      // Mock search for now
      await new Promise(resolve => setTimeout(resolve, 300))
      users.value = users.value.filter(user => 
        user.name.includes(query) || user.employee_id.includes(query)
      )
    } catch (error) {
      ElMessage.error('搜尋員工失敗')
    } finally {
      loadingUsers.value = false
    }
  }
}

const loadRules = async () => {
  try {
    // TODO: Replace with actual API call
    // const response = await ruleApi.getActiveRules()
    // rules.value = response.data
    
    // Mock data for now
    rules.value = [
      {
        id: 1,
        name: '優秀表現',
        description: '員工表現優異，值得嘉獎',
        base_score: 10,
        weight: 1.0,
        evidence_required: true,
        category: 'positive'
      },
      {
        id: 2,
        name: '遲到',
        description: '員工上班遲到',
        base_score: -5,
        weight: 1.0,
        evidence_required: false,
        category: 'negative'
      }
    ]
  } catch (error) {
    ElMessage.error('載入規則清單失敗')
  }
}

const loadProjects = async () => {
  try {
    // TODO: Replace with actual API call
    // const response = await projectApi.getProjects()
    // projects.value = response.data
    
    // Mock data for now
    projects.value = [
      { id: 1, name: '專案 A', code: 'PROJ001' },
      { id: 2, name: '專案 B', code: 'PROJ002' }
    ]
  } catch (error) {
    ElMessage.error('載入專案清單失敗')
  }
}

const handleRuleChange = () => {
  // Clear evidence files if rule doesn't require evidence
  if (selectedRule.value && !selectedRule.value.evidence_required) {
    fileList.value = []
    form.evidence_urls = []
  }
}

const handleUploadSuccess = (response: any, file: any) => {
  form.evidence_urls.push(response.url)
  ElMessage.success(`檔案 ${file.name} 上傳成功`)
}

const handleUploadError = (error: any, file: any) => {
  ElMessage.error(`檔案 ${file.name} 上傳失敗`)
}

const handleRemoveFile = (file: any, fileList: any[]) => {
  const index = form.evidence_urls.indexOf(file.response?.url)
  if (index > -1) {
    form.evidence_urls.splice(index, 1)
  }
}

const disabledDate = (time: Date) => {
  // Disable future dates and dates older than 1 year
  const today = new Date()
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(today.getFullYear() - 1)
  
  return time.getTime() > today.getTime() || time.getTime() < oneYearAgo.getTime()
}

const validateForm = async (): Promise<boolean> => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validate()
    return true
  } catch (error) {
    return false
  }
}

const saveAsDraft = async () => {
  const isValid = await validateForm()
  if (!isValid) return
  
  submitting.value = true
  try {
    const eventData = {
      ...form,
      status: 'draft'
    }
    
    // TODO: Replace with actual API call
    // await eventApi.createEvent(eventData)
    
    ElMessage.success('草稿已儲存')
    router.push('/events')
    
  } catch (error) {
    ElMessage.error('儲存草稿失敗')
  } finally {
    submitting.value = false
  }
}

const submitForm = async () => {
  const isValid = await validateForm()
  if (!isValid) return
  
  submitting.value = true
  try {
    const eventData = {
      ...form,
      status: authStore.hasRole('employee') ? 'pending' : 'approved'
    }
    
    // TODO: Replace with actual API call
    // await eventApi.createEvent(eventData)
    
    ElMessage.success('事件已提交')
    router.push('/events')
    
  } catch (error) {
    ElMessage.error('提交失敗')
  } finally {
    submitting.value = false
  }
}

// Set default user if creating for self
watch(() => authStore.user, (user) => {
  if (user && authStore.hasRole('employee') && !form.user_id) {
    form.user_id = user.id
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  loadUsers()
  loadRules()
  loadProjects()
})
</script>

<style lang="scss" scoped>
.event-create-page {
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
  
  .rule-info {
    margin-bottom: 1rem;
    
    .rule-details {
      margin-top: 0.5rem;
      
      p {
        margin: 0.25rem 0;
        font-size: 0.875rem;
        
        &.text-warning {
          color: #f59e0b;
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }
      }
    }
  }
  
  .upload-section {
    .upload-tip {
      font-size: 0.875rem;
      color: #6b7280;
      margin-top: 0.5rem;
    }
  }
  
  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }
}
</style>