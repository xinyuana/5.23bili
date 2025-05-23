import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/search'
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/Search.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/data',
    children: [
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/components/admin/UserManagement.vue')
      },
      {
        path: 'data',
        name: 'AdminData',
        component: () => import('@/components/admin/DataManagement.vue')
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/components/admin/DataVisualization.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    next('/search')
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next('/search')
  } else {
    next()
  }
})

export default router 