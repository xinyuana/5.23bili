<template>
  <div class="data-visualization">
    <div class="page-header">
      <h2>📊 数据可视化面板</h2>
    </div>

    <!-- 筛选控制区域 -->
    <el-card class="filter-card" style="margin-bottom: 20px;">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="选择项目" label-width="80px">
            <el-select v-model="filters.project_id" placeholder="全部项目" clearable @change="loadData">
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
          <el-form-item label="时间范围" label-width="80px">
            <el-select v-model="filters.time_range" @change="handleTimeRangeChange">
              <el-option label="最近一天" value="1d" />
              <el-option label="最近一周" value="7d" />
              <el-option label="最近一个月" value="30d" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8" v-if="filters.time_range === 'custom'">
          <el-form-item label="自定义时间" label-width="80px">
            <el-date-picker
              v-model="customTimeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              value-format="X"
              @change="loadData"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 概览卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-item">
            <div class="overview-icon" style="background: #409eff;">📹</div>
            <div class="overview-content">
              <div class="overview-value">{{ formatNumber(overviewData.total_videos) }}</div>
              <div class="overview-label">总视频数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-item">
            <div class="overview-icon" style="background: #67c23a;">▶️</div>
            <div class="overview-content">
              <div class="overview-value">{{ formatNumber(overviewData.total_plays) }}</div>
              <div class="overview-label">总播放量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-item">
            <div class="overview-icon" style="background: #e6a23c;">📈</div>
            <div class="overview-content">
              <div class="overview-value">{{ formatNumber(overviewData.avg_plays) }}</div>
              <div class="overview-label">平均播放量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-item">
            <div class="overview-icon" style="background: #f56c6c;">🔥</div>
            <div class="overview-content">
              <div class="overview-value">{{ overviewData.viral_rate }}%</div>
              <div class="overview-label">爆文率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 时间段统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📅 时间段投放统计</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="time-stat-item">
                <div class="time-stat-value">{{ timePeriodStats['1d'] || 0 }}</div>
                <div class="time-stat-label">最近一天</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="time-stat-item">
                <div class="time-stat-value">{{ timePeriodStats['7d'] || 0 }}</div>
                <div class="time-stat-label">最近一周</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="time-stat-item">
                <div class="time-stat-value">{{ timePeriodStats['30d'] || 0 }}</div>
                <div class="time-stat-label">最近一个月</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🎯 项目分布</span>
            </div>
          </template>
          <v-chart class="chart" :option="projectDistributionOption" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📈 项目播放总量</span>
            </div>
          </template>
          <v-chart class="chart" :option="playDistributionOption" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🔥 各项目爆文率</span>
            </div>
          </template>
          <v-chart class="chart" :option="viralRateOption" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import {
  CanvasRenderer
} from 'echarts/renderers'
import {
  LineChart,
  BarChart,
  PieChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import api from '@/utils/api'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const loading = ref(false)
const projects = ref([])
const customTimeRange = ref([])

const filters = reactive({
  project_id: '',
  time_range: '30d'
})

const overviewData = reactive({
  total_videos: 0,
  total_plays: 0,
  avg_plays: 0,
  viral_rate: 0
})

const timePeriodStats = reactive({
  '1d': 0,
  '7d': 0,
  '30d': 0
})

const chartData = reactive({
  projectStats: [],
  playStats: { distribution: [], ranges: [], project_data: [] },
  viralStats: { project_stats: {} }
})

onMounted(() => {
  loadProjects()
  loadData()
})

const loadProjects = async () => {
  try {
    const response = await api.get('/projects')
    projects.value = response.data.projects
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

const handleTimeRangeChange = () => {
  if (filters.time_range !== 'custom') {
    customTimeRange.value = []
  }
  loadData()
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      project_id: filters.project_id,
      time_range: filters.time_range
    }

    if (filters.time_range === 'custom' && customTimeRange.value.length === 2) {
      params.start_time = customTimeRange.value[0]
      params.end_time = customTimeRange.value[1]
      delete params.time_range
    }

    const response = await api.post('/admin/data/visualization', params)
    
    if (response.data.success) {
      const data = response.data
      
      // 更新概览数据
      Object.assign(overviewData, {
        total_videos: data.play_stats.project_data.reduce((sum, project) => sum + project.video_count, 0),
        total_plays: data.play_stats.total_plays,
        avg_plays: data.play_stats.avg_plays,
        viral_rate: data.viral_stats.viral_rate
      })
      
      // 更新时间段统计
      Object.assign(timePeriodStats, data.time_period_stats)
      
      // 更新图表数据
      Object.assign(chartData, {
        projectStats: data.project_stats,
        playStats: data.play_stats,
        viralStats: data.viral_stats
      })
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const formatNumber = (num) => {
  if (!num) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 项目分布饼图配置
const projectDistributionOption = computed(() => {
  const data = chartData.projectStats || []
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '项目分布',
      type: 'pie',
      radius: '50%',
      data: data.map(item => ({
        value: item.video_count,
        name: item.name
      }))
    }]
  }
})

// 播放量分布柱状图配置
const playDistributionOption = computed(() => {
  const projectData = chartData.playStats.project_data || []
  
  // 生成颜色系列
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
  
  return {
    title: {
      text: '各项目播放总量',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const item = params[0]
        const data = projectData.find(p => p.name === item.name)
        return `${item.name}<br/>
                播放总量: ${formatNumber(item.value)}<br/>
                视频数量: ${data?.video_count || 0}<br/>
                平均播放量: ${formatNumber(data?.avg_plays || 0)}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: projectData.map(item => item.name),
      axisLabel: {
        rotate: 45,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '播放总量',
      axisLabel: {
        formatter: function(value) {
          if (value >= 10000) {
            return (value / 10000).toFixed(1) + 'w'
          }
          return value.toString()
        }
      }
    },
    series: [{
      name: '播放总量',
      type: 'bar',
      data: projectData.map((item, index) => ({
        value: item.total_plays,
        name: item.name,
        itemStyle: {
          color: colors[index % colors.length]
        }
      })),
      label: {
        show: true,
        position: 'top',
        formatter: function(params) {
          const value = params.value
          if (value >= 10000) {
            return (value / 10000).toFixed(1) + 'w'
          }
          return value.toString()
        }
      }
    }]
  }
})

// 各项目爆文率柱状图配置
const viralRateOption = computed(() => {
  const data = chartData.viralStats.project_stats || {}
  const projectNames = Object.keys(data)
  const rates = projectNames.map(name => data[name].rate)
  
  // 动态计算Y轴最大值
  const maxRate = Math.max(...rates, 0)
  const yAxisMax = maxRate > 0 ? Math.max(maxRate * 1.2, 20) : 20 // 至少显示20%
  
  return {
    title: {
      text: '各项目爆文率 (播放量>1000)',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const item = params[0]
        const projectData = data[item.name]
        return `${item.name}<br/>爆文率: ${item.value}%<br/>爆文数: ${projectData?.viral || 0}<br/>总视频: ${projectData?.total || 0}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: projectNames,
      axisLabel: {
        rotate: 45,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      max: yAxisMax,
      min: 0,
      name: '爆文率 (%)',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '爆文率',
      type: 'bar',
      data: rates,
      itemStyle: {
        color: function(params) {
          // 根据数值渐变颜色
          const value = params.value
          if (value >= 15) return '#ff4757'      // 高爆文率：红色
          else if (value >= 10) return '#ffa502' // 中等爆文率：橙色  
          else if (value >= 5) return '#f9ca24'  // 较低爆文率：黄色
          else return '#54a0ff'                  // 低爆文率：蓝色
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}%'
      }
    }]
  }
})
</script>

<style lang="scss" scoped>
.data-visualization {
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      color: #333;
    }
  }
}

.filter-card {
  :deep(.el-card__body) {
    padding: 15px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

// 概览卡片样式
.overview-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  
  :deep(.el-card__body) {
    padding: 20px;
  }
  
  .overview-item {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .overview-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: white;
    }
    
    .overview-content {
      flex: 1;
      
      .overview-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
      }
      
      .overview-label {
        font-size: 14px;
        color: #666;
      }
    }
  }
}

// 时间段统计样式
.time-stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  
  .time-stat-value {
    font-size: 32px;
    font-weight: bold;
    color: #409eff;
    margin-bottom: 8px;
  }
  
  .time-stat-label {
    font-size: 14px;
    color: #666;
  }
}

// 图表样式
.chart {
  height: 350px;
  width: 100%;
}

// 响应式设计
@media (max-width: 768px) {
  .overview-card {
    margin-bottom: 15px;
    
    .overview-item {
      .overview-icon {
        width: 40px;
        height: 40px;
        font-size: 20px;
      }
      
      .overview-content .overview-value {
        font-size: 20px;
      }
    }
  }
  
  .chart {
    height: 250px;
  }
}
</style> 