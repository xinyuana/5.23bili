<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <el-card>
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'primary'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_access" label="项目权限">
          <template #default="scope">
            <div v-if="scope.row.role === 'admin'">
              <el-tag type="success">全部项目</el-tag>
            </div>
            <div v-else>
              <el-tag 
                v-for="project in scope.row.project_access" 
                :key="project"
                style="margin-right: 5px;"
              >
                {{ project }}
              </el-tag>
              <span v-if="!scope.row.project_access?.length" class="text-muted">无权限</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteUser(scope.row)"
              :disabled="scope.row.role === 'admin' && adminCount <= 1"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      :title="isEditing ? '编辑用户' : '添加用户'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="userForm.password" 
            type="password" 
            :placeholder="isEditing ? '留空则不修改密码' : '请输入密码'"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%;">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目权限" v-if="userForm.role === 'user'">
          <el-select 
            v-model="userForm.project_access" 
            multiple 
            placeholder="选择可访问的项目"
            style="width: 100%;"
          >
            <el-option 
              v-for="project in availableProjects" 
              :key="project" 
              :label="project" 
              :value="project" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">
          {{ isEditing ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const users = ref([])
const userFormRef = ref()

const availableProjects = ref(['巨书', '康江文'])

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  role: 'user',
  project_access: []
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur', validator: validatePassword }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

function validatePassword(rule, value, callback) {
  if (isEditing.value && !value) {
    callback() // 编辑时密码可以为空
  } else if (!value) {
    callback(new Error('请输入密码'))
  } else {
    callback()
  }
}

const adminCount = computed(() => {
  return users.value.filter(user => user.role === 'admin').length
})

onMounted(() => {
  loadUsers()
})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data.users
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEditing.value = false
  resetForm()
  dialogVisible.value = true
}

const editUser = (user) => {
  isEditing.value = true
  userForm.id = user.id
  userForm.username = user.username
  userForm.password = ''
  userForm.role = user.role
  userForm.project_access = user.project_access || []
  dialogVisible.value = true
}

const resetForm = () => {
  userForm.id = null
  userForm.username = ''
  userForm.password = ''
  userForm.role = 'user'
  userForm.project_access = []
}

const saveUser = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      
      try {
        const userData = { ...userForm }
        if (userData.role === 'admin') {
          userData.project_access = []
        }
        
        if (isEditing.value) {
          if (!userData.password) {
            delete userData.password
          }
          await api.put(`/admin/users/${userData.id}`, userData)
          ElMessage.success('用户更新成功')
        } else {
          await api.post('/admin/users', userData)
          ElMessage.success('用户创建成功')
        }
        
        dialogVisible.value = false
        loadUsers()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const deleteUser = async (user) => {
  if (user.role === 'admin' && adminCount.value <= 1) {
    ElMessage.warning('不能删除最后一个管理员')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.delete(`/admin/users/${user.id}`)
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}
</script>

<style lang="scss" scoped>
.user-management {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      color: #333;
    }
  }
}

.text-muted {
  color: #909399;
  font-size: 12px;
}
</style> 