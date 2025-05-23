import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    isAuthenticated: false
  }),
  
  getters: {
    isAdmin: (state) => state.user?.role === 'admin'
  },
  
  actions: {
    async login(credentials) {
      try {
        const response = await api.post('/auth/login', credentials)
        const { token, user } = response.data
        
        this.token = token
        this.user = user
        this.isAuthenticated = true
        
        localStorage.setItem('token', token)
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.message || '登录失败' 
        }
      }
    },
    
    async logout() {
      this.token = null
      this.user = null
      this.isAuthenticated = false
      
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    },
    
    async checkAuth() {
      if (!this.token) {
        return false
      }
      
      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        const response = await api.get('/auth/me')
        
        this.user = response.data.user
        this.isAuthenticated = true
        return true
      } catch (error) {
        this.logout()
        return false
      }
    }
  }
})