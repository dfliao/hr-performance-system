import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
const DefaultLayout = () => import('@/layouts/DefaultLayout.vue')
const AuthLayout = () => import('@/layouts/AuthLayout.vue')

// Pages
const Login = () => import('@/views/auth/Login.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const Events = () => import('@/views/events/EventList.vue')
const EventCreate = () => import('@/views/events/EventCreate.vue')
const EventDetail = () => import('@/views/events/EventDetail.vue')
const Reports = () => import('@/views/reports/ReportList.vue')
const PersonalReport = () => import('@/views/reports/PersonalReport.vue')
const DepartmentReport = () => import('@/views/reports/DepartmentReport.vue')
const CompanyReport = () => import('@/views/reports/CompanyReport.vue')
const RulePacks = () => import('@/views/rules/RulePackList.vue')
const RulePackDetail = () => import('@/views/rules/RulePackDetail.vue')
const Users = () => import('@/views/admin/UserList.vue')
const Departments = () => import('@/views/admin/DepartmentList.vue')
const AuditLogs = () => import('@/views/admin/AuditLogList.vue')
const Profile = () => import('@/views/profile/UserProfile.vue')
const Settings = () => import('@/views/settings/SystemSettings.vue')

const routes: RouteRecordRaw[] = [
  // Authentication routes
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
        meta: {
          title: '登入',
          requiresAuth: false
        }
      }
    ]
  },

  // Main application routes
  {
    path: '/',
    component: DefaultLayout,
    meta: {
      requiresAuth: true
    },
    children: [
      // Dashboard
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: {
          title: '總覽',
          icon: 'House',
          showInMenu: true
        }
      },

      // Events management
      {
        path: '/events',
        name: 'Events',
        component: Events,
        meta: {
          title: '事件管理',
          icon: 'Document',
          showInMenu: true,
          permissions: ['events:read']
        }
      },
      {
        path: '/events/create',
        name: 'EventCreate',
        component: EventCreate,
        meta: {
          title: '新增事件',
          permissions: ['events:create']
        }
      },
      {
        path: '/events/:id',
        name: 'EventDetail',
        component: EventDetail,
        meta: {
          title: '事件詳情',
          permissions: ['events:read']
        }
      },

      // Reports
      {
        path: '/reports',
        name: 'Reports',
        component: Reports,
        meta: {
          title: '報表中心',
          icon: 'DataAnalysis',
          showInMenu: true,
          permissions: ['reports:read']
        }
      },
      {
        path: '/reports/personal',
        name: 'PersonalReport',
        component: PersonalReport,
        meta: {
          title: '個人績效',
          permissions: ['reports:read']
        }
      },
      {
        path: '/reports/department',
        name: 'DepartmentReport',
        component: DepartmentReport,
        meta: {
          title: '部門報表',
          permissions: ['reports:read']
        }
      },
      {
        path: '/reports/company',
        name: 'CompanyReport',
        component: CompanyReport,
        meta: {
          title: '公司總覽',
          permissions: ['reports:read'],
          roles: ['admin', 'auditor']
        }
      },

      // Rule management
      {
        path: '/rules',
        name: 'RulePacks',
        component: RulePacks,
        meta: {
          title: '規則管理',
          icon: 'Setting',
          showInMenu: true,
          permissions: ['rules:read'],
          roles: ['admin', 'manager']
        }
      },
      {
        path: '/rules/:id',
        name: 'RulePackDetail',
        component: RulePackDetail,
        meta: {
          title: '規則詳情',
          permissions: ['rules:read']
        }
      },

      // Administration (Admin only)
      {
        path: '/admin/users',
        name: 'Users',
        component: Users,
        meta: {
          title: '使用者管理',
          icon: 'User',
          showInMenu: true,
          permissions: ['users:read'],
          roles: ['admin'],
          group: 'admin'
        }
      },
      {
        path: '/admin/departments',
        name: 'Departments',
        component: Departments,
        meta: {
          title: '部門管理',
          icon: 'OfficeBuilding',
          showInMenu: true,
          permissions: ['users:read'],
          roles: ['admin'],
          group: 'admin'
        }
      },
      {
        path: '/admin/audit-logs',
        name: 'AuditLogs',
        component: AuditLogs,
        meta: {
          title: '審計日誌',
          icon: 'Document',
          showInMenu: true,
          permissions: ['audit:read'],
          roles: ['admin', 'auditor'],
          group: 'admin'
        }
      },
      {
        path: '/admin/settings',
        name: 'Settings',
        component: Settings,
        meta: {
          title: '系統設定',
          icon: 'Tools',
          showInMenu: true,
          roles: ['admin'],
          group: 'admin'
        }
      },

      // Profile
      {
        path: '/profile',
        name: 'Profile',
        component: Profile,
        meta: {
          title: '個人資料',
          showInMenu: false
        }
      }
    ]
  },

  // 404 catch all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: {
      title: '頁面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Set page title
  document.title = to.meta.title 
    ? `${to.meta.title} | HR 績效管理系統` 
    : 'HR 績效管理系統'
  
  // Check authentication
  if (to.meta.requiresAuth !== false) {
    if (!authStore.isAuthenticated) {
      // Redirect to login if not authenticated
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // Check role permissions
    if (to.meta.roles && !authStore.hasAnyRole(to.meta.roles as string[])) {
      console.warn('Access denied: insufficient role')
      next({ name: 'Dashboard' })
      return
    }
    
    // Check specific permissions
    if (to.meta.permissions && !authStore.hasAnyPermission(to.meta.permissions as string[])) {
      console.warn('Access denied: insufficient permissions')
      next({ name: 'Dashboard' })
      return
    }
  }
  
  // Redirect authenticated users away from auth pages
  if (to.path.startsWith('/auth') && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

// Error handling
router.onError((error) => {
  console.error('Router error:', error)
})

export default router