<template>
  <div class="search-container">
    <!-- 顶部导航 -->
    <div class="header">
      <div class="header-left">
        <h1>B站评论检索系统</h1>
      </div>
      <div class="header-right">
        <span>欢迎，{{ authStore.user?.username }}</span>
        <el-button 
          v-if="authStore.isAdmin" 
          type="primary" 
          @click="$router.push('/admin')"
          size="small"
        >
          管理后台
        </el-button>
        <el-button @click="handleLogout" size="small">退出登录</el-button>
      </div>
    </div>

    <!-- 紧凑的搜索区域 -->
    <div class="search-section">
      <el-card class="search-card">
        <el-form :model="searchForm" class="search-form" size="small">
          <el-row :gutter="15">
            <el-col :span="6">
              <el-form-item label="搜索类型" label-width="70px">
                <el-radio-group v-model="searchForm.searchType" size="small">
                  <el-radio label="videos">视频</el-radio>
                  <el-radio label="comments">评论</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="项目" label-width="50px">
                <el-select v-model="searchForm.project_id" placeholder="选择项目" clearable size="small">
                  <el-option
                    v-for="project in projects"
                    :key="project.id"
                    :label="project.name"
                    :value="project.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="关键词" label-width="50px">
                <el-input
                  v-model="searchForm.keywords"
                  placeholder="输入搜索关键词"
                  clearable
                  size="small"
                  @keyup.enter="() => handleSearch(true)"
                />
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item>
                <el-button type="primary" @click="() => handleSearch(true)" :loading="loading" size="small">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
                <el-button @click="resetForm" size="small">重置</el-button>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 高级搜索选项（可折叠） -->
          <el-collapse v-model="activeCollapse" accordion>
            <el-collapse-item title="高级搜索选项" name="advanced">
              <!-- 视频搜索特有字段 -->
              <template v-if="searchForm.searchType === 'videos'">
                <el-row :gutter="15">
                  <el-col :span="8">
                    <el-form-item label="视频标题" label-width="70px">
                      <el-input v-model="searchForm.video_title" placeholder="视频标题" clearable size="small" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="UP主昵称" label-width="70px">
                      <el-input v-model="searchForm.uploader_nickname" placeholder="UP主昵称" clearable size="small" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="UP主UID" label-width="70px">
                      <el-input v-model="searchForm.uploader_uid" placeholder="UP主UID" clearable size="small" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </template>

              <!-- 评论搜索特有字段 -->
              <template v-if="searchForm.searchType === 'comments'">
                <el-row :gutter="15">
                  <el-col :span="8">
                    <el-form-item label="评论者UID" label-width="80px">
                      <el-input v-model="searchForm.commenter_uid" placeholder="评论者UID" clearable size="small" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="评论者昵称" label-width="80px">
                      <el-input v-model="searchForm.commenter_nickname" placeholder="评论者昵称" clearable size="small" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </template>

              <el-row :gutter="15">
                <el-col :span="12">
                  <el-form-item label="时间范围" label-width="70px">
                    <div class="time-range-container">
                      <el-date-picker
                        v-model="timeRange"
                        type="datetimerange"
                        range-separator="至"
                        start-placeholder="开始时间"
                        end-placeholder="结束时间"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="X"
                        size="small"
                      />
                      <div class="time-range-hint">
                        <small>{{ getTimeRangeHint() }}</small>
                      </div>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="排序方式" label-width="70px">
                    <el-select v-model="searchForm.sort_by" size="small" style="width: 120px;">
                      <el-option label="发布时间" value="create_time" />
                      <el-option v-if="searchForm.searchType === 'videos'" label="播放量" value="video_play_count" />
                      <el-option v-if="searchForm.searchType === 'comments'" label="点赞数" value="like_count" />
                    </el-select>
                    <el-select v-model="searchForm.sort_order" style="margin-left: 10px; width: 80px;" size="small">
                      <el-option label="降序" value="desc" />
                      <el-option label="升序" value="asc" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-collapse-item>
          </el-collapse>
        </el-form>
      </el-card>
    </div>

    <!-- 结果区域 -->
    <div class="results-section" v-if="searchResults.length > 0 || hasSearched">
      <el-card class="results-card">
        <template #header>
          <div class="card-header">
            <span>搜索结果 (共 {{ totalResults }} 条)</span>
            <div class="header-actions">
              <span class="current-project" v-if="searchForm.project_id">
                当前项目: {{ getCurrentProjectName() }}
              </span>
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="totalResults"
                layout="total, prev, pager, next"
                @current-change="handlePageChange"
                size="small"
                style="margin-left: 20px;"
                :disabled="loading"
              />
            </div>
          </div>
        </template>

        <div v-if="searchResults.length === 0 && hasSearched" class="no-results">
          <el-empty description="暂无搜索结果" />
        </div>

        <div v-else class="results-content">
          <!-- 视频结果 -->
          <div v-if="searchForm.searchType === 'videos'" class="video-results">
            <div v-for="item in searchResults" :key="item._id" class="result-item">
              <div class="result-header">
                <h3 v-html="item.highlight?.title?.[0] || item.title"></h3>
                <div class="result-meta">
                  <span>UP主: {{ item.nickname }}</span>
                  <span>播放量: {{ formatNumber(item.video_play_count) }}</span>
                  <span>发布时间: {{ formatTime(item.create_time) }}</span>
                  <span class="project-tag">{{ item.project_id }}</span>
                </div>
              </div>
              <div class="result-content">
                <p v-html="item.highlight?.desc?.[0] || item.desc"></p>
              </div>
              <div class="result-actions">
                <el-button type="text" @click="openVideo(item.video_url)" size="small">查看视频</el-button>
              </div>
            </div>
          </div>

          <!-- 评论结果 -->
          <div v-if="searchForm.searchType === 'comments'" class="comment-results">
            <div v-for="item in searchResults" :key="item._id" class="result-item comment-item">
              <div class="result-header">
                <span class="commenter">{{ item.nickname }}</span>
                <div class="comment-type-badge">
                  <el-tag v-if="item.is_main_comment" type="primary" size="small">主评论</el-tag>
                  <el-tag v-else type="info" size="small">回复评论</el-tag>
                </div>
                <div class="result-meta">
                  <span class="comment-time">🕒 {{ formatTime(item.create_time) }}</span>
                  <span class="like-count">👍 {{ item.like_count }}</span>
                  <span class="project-tag">{{ item.project_id }}</span>
                </div>
              </div>
              
              <!-- 视频信息 -->
              <div class="video-info-section">
                <div class="video-info">
                  <span class="video-title">📹 {{ item.video_title || '无标题' }}</span>
                  <span class="video-uploader">👤 UP主: {{ item.video_uploader_nickname }}</span>
                  <el-button 
                    v-if="item.video_url" 
                    type="text" 
                    size="small" 
                    @click="openVideo(item.video_url)"
                    class="video-link-btn"
                  >
                    🔗 查看视频
                  </el-button>
                </div>
              </div>
              
              <!-- 父评论信息（如果是回复评论） -->
              <div v-if="!item.is_main_comment && item.parent_comment_info" class="parent-comment-section">
                <div class="parent-comment">
                  <div class="parent-header">
                    <span class="parent-label">回复</span>
                    <span class="parent-commenter">{{ item.parent_comment_info.nickname }}</span>
                    <span class="parent-time">{{ formatTime(item.parent_comment_info.create_time) }}</span>
                    <span class="parent-likes">👍 {{ item.parent_comment_info.like_count }}</span>
                  </div>
                  <div class="parent-content">
                    {{ item.parent_comment_info.content }}
                  </div>
                </div>
              </div>
              
              <!-- 主评论时间强调显示 -->
              <div v-if="item.is_main_comment" class="main-comment-time-section">
                <div class="main-comment-time">
                  <span class="time-icon">📅</span>
                  <span class="time-text">发布于 {{ formatTimeDetailed(item.create_time) }}</span>
                  <span class="like-info">💛 {{ item.like_count }} 赞</span>
                </div>
              </div>
              
              <!-- 当前评论内容 -->
              <div class="result-content">
                <p v-html="item.highlight?.content?.[0] || item.content"></p>
              </div>
              
              <div class="result-actions">
                <el-button type="text" @click="findSimilar(item._id)" size="small">查找相似评论</el-button>
                <el-button type="text" @click="copyCommentInfo(item)" size="small">复制详细信息</el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import dayjs from 'dayjs'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const hasSearched = ref(false)
const projects = ref([])
const searchResults = ref([])
const totalResults = ref(0)
const currentPage = ref(1)
const pageSize = ref(100)
const timeRange = ref([])
const activeCollapse = ref([])
const dataTimeRange = ref({
  comment_range: { min: 0, max: 0 },
  video_range: { min: 0, max: 0 }
})

const searchForm = reactive({
  searchType: 'videos',
  keywords: '',
  project_id: '',
  video_title: '',
  uploader_nickname: '',
  uploader_uid: '',
  video_url: '',
  commenter_uid: '',
  commenter_nickname: '',
  sort_by: 'create_time',
  sort_order: 'desc'
})

// 监听时间范围变化
watch(timeRange, (newVal) => {
  console.log('时间范围变化:', newVal)
  if (newVal && newVal.length === 2) {
    const startTime = newVal[0]
    const endTime = newVal[1]
    searchForm.time_range = {
      start: startTime,
      end: endTime
    }
    console.log('设置时间范围:', {
      start: startTime,
      end: endTime,
      start_readable: new Date(startTime * 1000).toLocaleString(),
      end_readable: new Date(endTime * 1000).toLocaleString()
    })
  } else {
    searchForm.time_range = {}
    console.log('清空时间范围')
  }
})

// 监听搜索类型变化，重新加载时间范围
watch(() => searchForm.searchType, () => {
  loadTimeRange()
})

onMounted(() => {
  loadProjects()
  loadTimeRange()
})

const loadProjects = async () => {
  try {
    const response = await api.get('/projects')
    projects.value = response.data.projects
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

const loadTimeRange = async () => {
  try {
    const response = await api.get('/time-range')
    dataTimeRange.value = response.data.time_range
  } catch (error) {
    console.error('加载时间范围失败:', error)
  }
}

const getCurrentProjectName = () => {
  const project = projects.value.find(p => p.id === searchForm.project_id)
  return project ? project.name : searchForm.project_id
}

const getTimeRangeHint = () => {
  const range = searchForm.searchType === 'videos' 
    ? dataTimeRange.value.video_range 
    : dataTimeRange.value.comment_range
  
  if (range && range.min && range.max) {
    const minDate = dayjs.unix(range.min).format('YYYY年MM月DD日')
    const maxDate = dayjs.unix(range.max).format('YYYY年MM月DD日')
    return `💡 数据时间范围: ${minDate} - ${maxDate}`
  }
  return '💡 正在加载时间范围...'
}

const handleSearch = async (resetPage = false) => {
  loading.value = true
  hasSearched.value = true
  
  // 如果是新搜索，重置页码
  if (resetPage) {
    currentPage.value = 1
  }
  
  try {
    // 构建搜索参数，过滤掉空值
    const searchData = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 添加搜索类型
    searchData.searchType = searchForm.searchType
    
    // 只添加有值的搜索参数
    Object.keys(searchForm).forEach(key => {
      const value = searchForm[key]
      console.log(`检查字段 ${key}:`, value, typeof value)
      if (value !== '' && value !== null && value !== undefined) {
        // 特殊处理time_range对象
        if (key === 'time_range' && typeof value === 'object') {
          if (Object.keys(value).length > 0) {
            console.log(`添加时间范围:`, value)
            searchData[key] = value
          }
        } else if (typeof value === 'object') {
          // 跳过其他空对象
          if (Object.keys(value).length > 0) {
            console.log(`添加对象字段 ${key}:`, value)
            searchData[key] = value
          }
        } else {
          console.log(`添加字段 ${key}:`, value)
          searchData[key] = value
        }
      }
    })
    
    console.log('搜索参数:', searchData)
    
    const endpoint = searchForm.searchType === 'videos' ? '/search/videos' : '/search/comments'
    const response = await api.post(endpoint, searchData)
    
    console.log('搜索结果:', response.data)
    
    searchResults.value = response.data.results || []
    totalResults.value = response.data.total || 0
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败: ' + (error.response?.data?.message || error.message))
    searchResults.value = []
    totalResults.value = 0
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  console.log('页面跳转到:', page)
  currentPage.value = page
  // 确保立即触发搜索
  handleSearch()
}

const resetForm = () => {
  Object.assign(searchForm, {
    searchType: 'videos',
    keywords: '',
    project_id: '',
    video_title: '',
    uploader_nickname: '',
    uploader_uid: '',
    video_url: '',
    commenter_uid: '',
    commenter_nickname: '',
    sort_by: 'create_time',
    sort_order: 'desc',
    time_range: {}
  })
  timeRange.value = []
  searchResults.value = []
  totalResults.value = 0
  hasSearched.value = false
  currentPage.value = 1
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const now = dayjs()
  const time = dayjs.unix(timestamp)
  const diffInDays = now.diff(time, 'day')
  
  if (diffInDays === 0) {
    return time.format('今天 HH:mm')
  } else if (diffInDays === 1) {
    return time.format('昨天 HH:mm')
  } else if (diffInDays < 7) {
    return `${diffInDays}天前`
  } else if (diffInDays < 30) {
    return `${Math.floor(diffInDays / 7)}周前`
  } else {
    return time.format('YYYY-MM-DD HH:mm')
  }
}

const formatTimeDetailed = (timestamp) => {
  if (!timestamp) return ''
  return dayjs.unix(timestamp).format('YYYY年MM月DD日 HH:mm:ss')
}

const formatNumber = (num) => {
  if (!num) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const openVideo = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

const copyCommentInfo = (item) => {
  const info = [
    `评论者: ${item.nickname}`,
    `评论时间: ${formatTimeDetailed(item.create_time)}`,
    `评论类型: ${item.is_main_comment ? '主评论' : '回复评论'}`,
    `点赞数: ${item.like_count}`,
    `项目: ${item.project_id}`,
    ``,
    `视频信息:`,
    `视频标题: ${item.video_title || '无标题'}`,
    `UP主: ${item.video_uploader_nickname}`,
    `视频链接: ${item.video_url || '无链接'}`,
    ``,
    `评论内容: ${item.content}`
  ]
  
  // 如果是回复评论，添加父评论信息
  if (!item.is_main_comment && item.parent_comment_info) {
    info.splice(-2, 0, 
      ``,
      `回复的评论:`,
      `父评论者: ${item.parent_comment_info.nickname}`,
      `父评论时间: ${formatTimeDetailed(item.parent_comment_info.create_time)}`,
      `父评论点赞: ${item.parent_comment_info.like_count}`,
      `父评论内容: ${item.parent_comment_info.content}`
    )
  }
  
  const text = info.join('\n')
  
  // 复制到剪贴板
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success('详细信息已复制到剪贴板')
    }).catch(() => {
      fallbackCopy(text)
    })
  } else {
    fallbackCopy(text)
  }
}

const fallbackCopy = (text) => {
  const textarea = document.createElement('textarea')
  textarea.value = text
  document.body.appendChild(textarea)
  textarea.select()
  try {
    document.execCommand('copy')
    ElMessage.success('详细信息已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
    console.error('复制失败:', err)
  }
  document.body.removeChild(textarea)
}

const findSimilar = async (commentId) => {
  try {
    const response = await api.get(`/comments/${commentId}/similar`)
    // 这里可以打开一个对话框显示相似评论
    console.log('相似评论:', response.data)
    ElMessage.info('相似评论功能正在开发中')
  } catch (error) {
    ElMessage.error('查找相似评论失败')
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.search-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 50px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  
  .header-left h1 {
    margin: 0;
    color: #333;
    font-size: 18px;
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 14px;
  }
}

.search-section {
  padding: 15px 20px;
  flex-shrink: 0;
  
  .search-card {
    :deep(.el-card__body) {
      padding: 15px;
    }
  }
}

.search-form {
  .el-row {
    margin-bottom: 0;
  }
  
  .el-form-item {
    margin-bottom: 8px;
  }
  
  :deep(.el-collapse-item__header) {
    font-size: 13px;
    padding-left: 0;
  }
  
  :deep(.el-collapse-item__content) {
    padding-bottom: 10px;
  }
}

.results-section {
  flex: 1;
  padding: 0 20px 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  .results-card {
    flex: 1;
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__body) {
      flex: 1;
      padding: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  
  .header-actions {
    display: flex;
    align-items: center;
    
    .current-project {
      font-size: 12px;
      color: #666;
      background: #e6f7ff;
      padding: 2px 8px;
      border-radius: 3px;
    }
  }
}

.results-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px;
}

.result-item {
  padding: 15px 0;
  border-bottom: 1px solid #e4e7ed;
  
  &:last-child {
    border-bottom: none;
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  
  h3 {
    margin: 0;
    color: #333;
    font-size: 16px;
    flex: 1;
    margin-right: 20px;
  }
  
  .commenter {
    font-weight: bold;
    color: #409eff;
    margin-right: 20px;
  }
  
  .result-meta {
    display: flex;
    gap: 15px;
    font-size: 12px;
    color: #666;
    flex-shrink: 0;
    
    .comment-time {
      color: #409eff;
      font-weight: 500;
      background: #ecf5ff;
      padding: 2px 6px;
      border-radius: 3px;
    }
    
    .like-count {
      color: #f56c6c;
    }
    
    .project-tag {
      background: #e1f5fe;
      color: #0277bd;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 11px;
    }
  }
}

.result-content {
  margin-bottom: 10px;
  
  p {
    margin: 0;
    line-height: 1.6;
    color: #333;
    font-size: 14px;
  }
}

.result-actions {
  display: flex;
  gap: 10px;
}

.no-results {
  text-align: center;
  padding: 60px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(em) {
  background: yellow;
  font-style: normal;
  padding: 1px 2px;
}

// 响应式设计
@media (max-width: 1200px) {
  .search-form {
    .el-col:nth-child(4) {
      margin-top: 10px;
    }
  }
}

// 评论相关样式
.comment-item {
  .result-header {
    align-items: center;
    
    .commenter {
      margin-right: 10px;
    }
    
    .comment-type-badge {
      margin-right: auto;
    }
  }
}

.video-info-section {
  margin: 8px 0;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  
  .video-info {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
    font-size: 13px;
    
    .video-title {
      color: #333;
      font-weight: 500;
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .video-uploader {
      color: #666;
    }
    
    .video-link-btn {
      padding: 0;
      font-size: 12px;
    }
  }
}

.parent-comment-section {
  margin: 8px 0;
  padding: 10px;
  background: #fff9e6;
  border-radius: 4px;
  border-left: 3px solid #e6a23c;
  
  .parent-comment {
    .parent-header {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 5px;
      font-size: 12px;
      
      .parent-label {
        color: #e6a23c;
        font-weight: 500;
      }
      
      .parent-commenter {
        color: #409eff;
        font-weight: 500;
      }
      
      .parent-time, .parent-likes {
        color: #999;
      }
    }
    
    .parent-content {
      font-size: 13px;
      color: #666;
      line-height: 1.4;
      max-height: 60px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
    }
  }
}

.main-comment-time-section {
  margin: 8px 0;
  padding: 10px;
  background: #fff9e6;
  border-radius: 4px;
  border-left: 3px solid #e6a23c;
  
  .main-comment-time {
    display: flex;
    gap: 10px;
    align-items: center;
    font-size: 12px;
    
    .time-icon {
      color: #e6a23c;
      font-weight: 500;
    }
    
    .time-text {
      color: #666;
    }
    
    .like-info {
      color: #f56c6c;
    }
  }
}

.time-range-container {
  position: relative;
  
  .time-range-hint {
    margin-top: 5px;
    padding: 4px 8px;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 4px;
    color: #0369a1;
    font-size: 12px;
    line-height: 1.4;
  }
}
</style> 