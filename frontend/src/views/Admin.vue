<template>
  <div class="admin-container">
    <div class="admin-header">
      <div class="header-left">
        <h1>管理后台</h1>
      </div>
      <div class="header-right">
        <span>管理员：{{ authStore.user?.username }}</span>
        <el-button @click="$router.push('/search')">返回搜索</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <div class="admin-content">
      <div class="admin-sidebar">
        <el-menu
          :default-active="currentRoute"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/data">
            <el-icon><Folder /></el-icon>
            <span>数据管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据可视化</span>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="admin-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Folder, DataAnalysis } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const currentRoute = computed(() => route.path)

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.admin-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  
  .header-left h1 {
    margin: 0;
    color: #333;
    font-size: 20px;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
  }
}

.admin-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.admin-sidebar {
  width: 200px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.admin-main {
  flex: 1;
  padding: 20px;
  background: white;
  overflow: auto;
}
</style> 