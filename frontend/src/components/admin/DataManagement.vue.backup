<template>
  <div class="data-management">
    <div class="page-header">
      <h2>数据管理</h2>
    </div>

    <!-- 数据统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon">📹</div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.videos }}</div>
              <div class="stat-label">视频数据</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon">💬</div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.comments }}</div>
              <div class="stat-label">评论数据</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon">📁</div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.projects }}</div>
              <div class="stat-label">项目数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.total }}</div>
              <div class="stat-label">总数据量</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 文件上传区域 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📤 文件上传</span>
              <el-button type="text" @click="loadStatistics">
                <el-icon><Refresh /></el-icon>
                刷新统计
              </el-button>
            </div>
          </template>
          
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="账号数据" name="account">
              <div class="upload-section">
                <el-upload
                  ref="accountUpload"
                  :auto-upload="false"
                  :on-change="(file) => handleFileSelect(file, 'account')"
                  :before-remove="() => handleFileRemove('account')"
                  accept=".csv"
                  :limit="1"
                >
                  <el-button type="primary">
                    <el-icon><Upload /></el-icon>
                    选择账号CSV文件
                  </el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      只能上传CSV文件，包含用户ID和项目映射关系
                    </div>
                  </template>
                </el-upload>
                <el-button 
                  v-if="uploadFiles.account"
                  type="success" 
                  @click="uploadFile('account')"
                  :loading="uploading.account"
                  style="margin-top: 10px;"
                >
                  开始上传账号数据
                </el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="视频数据" name="video">
              <div class="upload-section">
                <el-upload
                  ref="videoUpload"
                  :auto-upload="false"
                  :on-change="(file) => handleFileSelect(file, 'video')"
                  :before-remove="() => handleFileRemove('video')"
                  accept=".csv"
                  :limit="1"
                >
                  <el-button type="primary">
                    <el-icon><Upload /></el-icon>
                    选择视频CSV文件
                  </el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      只能上传CSV文件，包含视频信息数据
                    </div>
                  </template>
                </el-upload>
                <el-button 
                  v-if="uploadFiles.video"
                  type="success" 
                  @click="uploadFile('video')"
                  :loading="uploading.video"
                  style="margin-top: 10px;"
                >
                  开始上传视频数据
                </el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="评论数据" name="comment">
              <div class="upload-section">
                <el-upload
                  ref="commentUpload"
                  :auto-upload="false"
                  :on-change="(file) => handleFileSelect(file, 'comment')"
                  :before-remove="() => handleFileRemove('comment')"
                  accept=".csv"
                  :limit="1"
                >
                  <el-button type="primary">
                    <el-icon><Upload /></el-icon>
                    选择评论CSV文件
                  </el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      只能上传CSV文件，包含评论数据
                    </div>
                  </template>
                </el-upload>
                <el-button 
                  v-if="uploadFiles.comment"
                  type="success" 
                  @click="uploadFile('comment')"
                  :loading="uploading.comment"
                  style="margin-top: 10px;"
                >
                  开始上传评论数据
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <!-- 数据管理操作区域 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🗑️ 数据清空</span>
            </div>
          </template>
          
          <el-alert
            title="危险操作警告"
            type="error"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <p>以下操作会永久删除数据，无法恢复！请谨慎操作。</p>
            <p>建议在清空数据前先备份重要数据。</p>
          </el-alert>
          
          <el-space direction="vertical" style="width: 100%;">
            <el-button 
              type="danger" 
              @click="clearData('videos')"
              :loading="clearing.videos"
              style="width: 100%;"
            >
              <el-icon><Delete /></el-icon>
              清空视频数据 ({{ statistics.videos }} 条)
            </el-button>
            
            <el-button 
              type="danger" 
              @click="clearData('comments')"
              :loading="clearing.comments"
              style="width: 100%;"
            >
              <el-icon><Delete /></el-icon>
              清空评论数据 ({{ statistics.comments }} 条)
            </el-button>
            
            <el-button 
              type="danger" 
              @click="clearData('all')"
              :loading="clearing.all"
              style="width: 100%;"
            >
              <el-icon><Delete /></el-icon>
              清空所有数据 ({{ statistics.total }} 条)
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速导入区域 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>⚡ 快速导入</span>
            </div>
          </template>
          
          <el-alert
            title="快速导入说明"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <p>使用现有的CSV文件进行快速导入，请确保以下文件存在于服务器：</p>
            <ul style="margin: 10px 0; padding-left: 20px;">
              <li>账号文件：账号大整合3.2xlsx_已提取UID.csv</li>
              <li>视频文件：1747748467790_dbexport_209215447/bilibili_video_0.csv</li>
              <li>评论文件：1747748467790_dbexport_209215447/bilibili_video_comment_1.csv</li>
            </ul>
          </el-alert>
          
          <el-space>
            <el-button 
              type="primary" 
              @click="quickImport('videos')"
              :loading="importing.videos"
            >
              <el-icon><Upload /></el-icon>
              快速导入视频数据
            </el-button>
            
            <el-button 
              type="primary" 
              @click="quickImport('comments')"
              :loading="importing.comments"
            >
              <el-icon><Upload /></el-icon>
              快速导入评论数据
            </el-button>
            
            <el-button 
              type="primary" 
              @click="quickImport('all')"
              :loading="importing.all"
            >
              <el-icon><Upload /></el-icon>
              快速导入所有数据
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'

const activeTab = ref('account')
const loadingStats = ref(false)

// 上传状态
const uploading = reactive({
  account: false,
  video: false,
  comment: false
})

// 清空状态
const clearing = reactive({
  videos: false,
  comments: false,
  all: false
})

// 导入状态
const importing = reactive({
  videos: false,
  comments: false,
  all: false
})

// 上传文件
const uploadFiles = reactive({
  account: null,
  video: null,
  comment: null
})

// 统计数据
const statistics = reactive({
  videos: 0,
  comments: 0,
  projects: 0,
  total: 0
})

onMounted(() => {
  loadStatistics()
})

// 加载统计信息
const loadStatistics = async () => {
  loadingStats.value = true
  
  try {
    const response = await api.get('/admin/data/statistics')
    Object.assign(statistics, response.data)
    ElMessage.success('统计信息已更新')
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取统计信息失败: ' + (error.response?.data?.message || '网络错误'))
  } finally {
    loadingStats.value = false
  }
}

// 文件选择处理
const handleFileSelect = (file, type) => {
  uploadFiles[type] = file.raw
  ElMessage.info(`已选择 ${type} 文件: ${file.name}`)
}

// 文件移除处理
const handleFileRemove = (type) => {
  uploadFiles[type] = null
  return true
}

// 上传文件
const uploadFile = async (type) => {
  if (!uploadFiles[type]) {
    ElMessage.warning('请先选择文件')
    return
  }

  const typeMap = {
    account: '账号',
    video: '视频',
    comment: '评论'
  }

  try {
    await ElMessageBox.confirm(
      `确定要上传 ${typeMap[type]} 数据文件吗？这将替换现有文件并重新导入数据。`,
      '确认上传',
      {
        confirmButtonText: '开始上传',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    uploading[type] = true

    const formData = new FormData()
    formData.append('file', uploadFiles[type])
    formData.append('file_type', type)

    const response = await api.post('/admin/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      ElMessage.success(response.data.message)
      uploadFiles[type] = null
      // 清除上传组件中的文件
      const uploadRef = type === 'account' ? 'accountUpload' : 
                       type === 'video' ? 'videoUpload' : 'commentUpload'
      if (this.$refs[uploadRef]) {
        this.$refs[uploadRef].clearFiles()
      }
      // 刷新统计
      setTimeout(() => loadStatistics(), 2000)
    } else {
      ElMessage.error(response.data.message || '上传失败')
    }

  } catch (error) {
    if (error !== 'cancel') {
      console.error('文件上传失败:', error)
      ElMessage.error('上传失败: ' + (error.response?.data?.message || '网络错误'))
    }
  } finally {
    uploading[type] = false
  }
}

// 清空数据
const clearData = async (type) => {
  const typeMap = {
    videos: '视频',
    comments: '评论',
    all: '所有'
  }

  const currentCount = type === 'videos' ? statistics.videos :
                      type === 'comments' ? statistics.comments :
                      statistics.total

  try {
    await ElMessageBox.confirm(
      `确定要清空${typeMap[type]}数据吗？\n\n将删除 ${currentCount} 条数据，此操作不可恢复！`,
      '危险操作确认',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'error',
        dangerouslyUseHTMLString: true
      }
    )

    clearing[type] = true

    const response = await api.post('/admin/data/clear', {
      data_type: type
    })

    ElMessage.success(response.data.message)
    loadStatistics()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空数据失败:', error)
      ElMessage.error('清空失败: ' + (error.response?.data?.message || '网络错误'))
    }
  } finally {
    clearing[type] = false
  }
}

// 快速导入
const quickImport = async (type) => {
  const typeMap = {
    videos: '视频',
    comments: '评论',
    all: '所有'
  }

  try {
    await ElMessageBox.confirm(
      `确定要快速导入${typeMap[type]}数据吗？这可能需要几分钟时间。`,
      '确认导入',
      {
        confirmButtonText: '开始导入',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    importing[type] = true

    const response = await api.post('/admin/data/import', {
      data_type: type
    })

    ElMessage.success('数据导入任务已启动，请稍后刷新统计信息查看结果')

    // 15秒后自动刷新统计
    setTimeout(() => {
      loadStatistics()
    }, 15000)

  } catch (error) {
    if (error !== 'cancel') {
      console.error('导入失败:', error)
      ElMessage.error('导入失败: ' + (error.response?.data?.message || '网络错误'))
    }
  } finally {
    importing[type] = false
  }
}
</script>

<style lang="scss" scoped>
.data-management {
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      color: #333;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

// 统计卡片样式
.stat-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  
  :deep(.el-card__body) {
    padding: 20px;
  }
  
  .stat-item {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .stat-icon {
      font-size: 32px;
    }
    
    .stat-content {
      flex: 1;
      
      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #409eff;
        margin-bottom: 5px;
      }
      
      .stat-label {
        font-size: 14px;
        color: #666;
      }
    }
  }
}

// 上传区域样式
.upload-section {
  padding: 20px;
  text-align: center;
  
  .el-upload__tip {
    color: #999;
    font-size: 12px;
    margin-top: 10px;
  }
}

// 统计项样式（旧的，保留兼容）
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
  
  .stat-label {
    font-size: 14px;
    color: #666;
  }
  
  .stat-value {
    font-size: 20px;
    font-weight: bold;
    color: #409eff;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .stat-card {
    margin-bottom: 10px;
    
    .stat-item {
      .stat-icon {
        font-size: 24px;
      }
      
      .stat-content .stat-value {
        font-size: 20px;
      }
    }
  }
}
</style> 
