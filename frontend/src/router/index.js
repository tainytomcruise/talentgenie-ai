import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginRegistrationView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import RecruitmentView from '../views/RecruitmentView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import EmployeeDashboard from '../views/EmployeeDashboard.vue'
import CandidateDashboard from '../views/CandidateDashboard.vue'
import PolicyView from '../views/PolicyView.vue'
import JobsView from '../views/JobsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/policy',
      name: 'policy',
      component: PolicyView
    },
    {
      path: '/candidate',
      name: 'candidate',
      component: CandidateDashboard,
    },
    {
      path: '/employee',
      component: EmployeeDashboard,
      children: [
        {
          path: 'personal-details',
          name: 'personal-details',
          component: () => import('../views/PersonalDetailsView.vue')
        },
        {
          path: 'dashboard',
          name: 'ask-hr',
          component: () => import('../views/AskHRView.vue')
        },
        {
          path: 'learning',
          name: 'learning',
          component: () => import('../views/MyLearningView.vue')
        },
        {
          path: 'wellness',
          name: 'employee-wellness',
          component: () => import('../views/WellnessView.vue')
        },
        {
          path: 'team',
          name: 'employee-team',
          component: () => import('../views/EmployeesView.vue')
        },
        {
          path: '',
          redirect: { name: 'ask-hr' }
        }
      ]
    },
    {
      path: '/admin',
      component: AdminDashboard,
      children: [
        {
          path: 'recruitment',
          name: 'recruitment',
          component: RecruitmentView
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: AnalyticsView
        },
        {
          path: 'wellness',
          name: 'wellness',
          component: () => import('../views/HRWellnessView.vue')
        },
        {
          path: 'employees',
          name: 'employees',
          component: () => import('../views/EmployeesView.vue')
        },
        {
          path: 'policy',
          name: 'policy',
          component: () => import('../views/PolicyView.vue')
        },
        {
          path: 'jobs',
          name: 'jobs',
          component: () => import('../views/JobsView.vue')
        },
        {
          path: 'sentiment',
          name: 'sentiment',
          component: () => import('../views/SentimentView.vue')
        },
        {
          path: 'notifications',
          name: 'notifications',
          component: () => import('../views/NotificationsView.vue')
        },
        {
          path: '',
          redirect: { name: 'recruitment' }
        }
      ]
    },
  ],
})

// global navigation guard enforcing JWT-based role access
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  // allow login page always
  if (to.path === '/login') {
    return next()
  }

  // require authentication for any other route
  if (!token) {
    alert('Please log in to access this page.')
    return next({ path: '/login' })
  }

  // Normalize role to lowercase for comparison
  const normalizedRole = role ? role.toLowerCase() : ''

  // admin pages require hr role (case-insensitive)
  if (to.path.startsWith('/admin') && normalizedRole !== 'hr' && normalizedRole !== 'hr manager') {
    alert('Access denied. HR role required to access this page.')
    return next(false)
  }

  // employee pages require employee role (case-insensitive)
  if (to.path.startsWith('/employee') && normalizedRole !== 'employee') {
    alert('Access denied. Employee role required to access this page.')
    return next(false)
  }

  // candidate pages require candidate role (case-insensitive)
  if (to.path.startsWith('/candidate') && normalizedRole !== 'candidate') {
    alert('Access denied. Candidate role required to access this page.')
    return next(false)
  }

  return next()
})

export default router
