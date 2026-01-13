<template>
  <div class="stats-view">
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="4">
        <el-card>
          <div class="stat-card">
            <div class="stat-value">{{ formatNumber(summary.total_requests) }}</div>
            <div class="stat-label">总请求数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-card">
            <div class="stat-value">{{ formatTokens(summary.total_tokens) }}</div>
            <div class="stat-label">总 Token 数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-card">
            <div class="stat-value">{{ formatDuration(summary.avg_duration_ms) }}</div>
            <div class="stat-label">平均耗时</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-card">
            <div class="stat-value">
              {{ summary.total_requests > 0 
                ? ((summary.success_count / summary.total_requests) * 100).toFixed(2) 
                : 0 }}%
            </div>
            <div class="stat-label">成功率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-card">
            <div class="stat-value cost-value">${{ formatCost(summary.total_cost) }}</div>
            <div class="stat-label">总费用</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card>
          <div class="stat-card">
            <div class="stat-value cost-value">${{ formatCost(summary.avg_cost) }}</div>
            <div class="stat-label">平均费用</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 时间范围选择 -->
    <el-card style="margin-bottom: 20px">
      <el-form inline>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="分组方式">
          <el-radio-group v-model="groupBy" @change="handleGroupChange">
            <el-radio label="hour">按小时</el-radio>
            <el-radio label="day">按天</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 图表 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>请求量趋势</template>
          <StatsChart :data="timelineData" type="line" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>Token 使用趋势</template>
          <StatsChart :data="timelineData" type="bar" />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>费用趋势</template>
          <StatsChart :data="timelineData" type="line" metric="cost" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>供应商费用统计</template>
          <StatsChart :data="providerCostData" type="pie" />
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>模型使用情况</template>
          <StatsChart :data="modelData" type="pie" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>Token 统计详情</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="总 Prompt Tokens">
              {{ formatTokens(tokenStats.total_prompt_tokens) }}
            </el-descriptions-item>
            <el-descriptions-item label="总 Completion Tokens">
              {{ formatTokens(tokenStats.total_completion_tokens) }}
            </el-descriptions-item>
            <el-descriptions-item label="平均 Prompt Tokens">
              {{ formatTokens(tokenStats.avg_prompt_tokens) }}
            </el-descriptions-item>
            <el-descriptions-item label="平均 Completion Tokens">
              {{ formatTokens(tokenStats.avg_completion_tokens) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>费用统计详情</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="总费用">
              <el-text type="success" style="font-weight: bold; font-size: 16px">
                ${{ formatCost(summary.total_cost) }}
              </el-text>
            </el-descriptions-item>
            <el-descriptions-item label="平均费用">
              <el-text type="info" style="font-weight: bold">
                ${{ formatCost(summary.avg_cost) }}
              </el-text>
            </el-descriptions-item>
            <el-descriptions-item label="总请求数">
              {{ formatNumber(summary.total_requests) }}
            </el-descriptions-item>
            <el-descriptions-item label="平均每次请求费用">
              <el-text type="warning" style="font-weight: bold">
                ${{ formatCost(summary.total_requests > 0 ? summary.total_cost / summary.total_requests : 0) }}
              </el-text>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>供应商费用排行</template>
          <el-table :data="providerCostData" stripe border style="width: 100%">
            <el-table-column prop="name" label="供应商" width="150" />
            <el-table-column prop="value" label="费用" align="right">
              <template #default="{ row }">
                <el-text type="success" style="font-weight: bold">
                  ${{ formatCost(row.value) }}
                </el-text>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getSummary, getTimeline, getTokenStats, getModelStats, getProviderCostStats } from '../api/stats'
import StatsChart from '../components/StatsChart.vue'
import { formatNumber, formatTokens, formatDuration } from '../utils/formatters'
import dayjs from 'dayjs'

const summary = ref({
  total_requests: 0,
  total_tokens: 0,
  total_prompt_tokens: 0,
  total_completion_tokens: 0,
  avg_duration_ms: 0,
  success_count: 0,
  error_count: 0,
  total_cost: 0,
  avg_cost: 0
})

const timelineData = ref([])
const modelData = ref([])
const providerCostData = ref([])
const tokenStats = ref({
  total_prompt_tokens: 0,
  total_completion_tokens: 0,
  total_tokens: 0,
  avg_prompt_tokens: 0,
  avg_completion_tokens: 0
})

const dateRange = ref([
  dayjs().subtract(7, 'day').format('YYYY-MM-DDTHH:mm:ss'),
  dayjs().format('YYYY-MM-DDTHH:mm:ss')
])

const groupBy = ref('hour')

async function fetchSummary() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    summary.value = await getSummary(params)
  } catch (error) {
    ElMessage.error('获取统计摘要失败')
  }
}

async function fetchTimeline() {
  try {
    const params = { group_by: groupBy.value }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    timelineData.value = await getTimeline(params)
  } catch (error) {
    ElMessage.error('获取时间线数据失败')
  }
}

async function fetchTokenStats() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    tokenStats.value = await getTokenStats(params)
  } catch (error) {
    ElMessage.error('获取 Token 统计失败')
  }
}

async function fetchModelStats() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    const data = await getModelStats(params)
    modelData.value = data.map(item => ({
      name: item.model,
      value: item.requests
    }))
  } catch (error) {
    ElMessage.error('获取模型统计失败')
  }
}

async function fetchProviderCostStats() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    const data = await getProviderCostStats(params)
    providerCostData.value = data.map(item => ({
      name: item.provider,
      value: item.cost
    }))
  } catch (error) {
    ElMessage.error('获取供应商费用统计失败')
  }
}

function handleDateChange() {
  fetchAll()
}

function handleGroupChange() {
  fetchTimeline()
}

// 格式化费用
function formatCost(cost) {
  if (!cost || cost === 0) return '0.00'
  if (cost < 0.01) {
    return cost.toFixed(6)
  } else if (cost < 1) {
    return cost.toFixed(4)
  } else {
    return cost.toFixed(2)
  }
}

async function fetchAll() {
  await Promise.all([
    fetchSummary(),
    fetchTimeline(),
    fetchTokenStats(),
    fetchModelStats(),
    fetchProviderCostStats()
  ])
}

onMounted(() => {
  fetchAll()
})
</script>

<style scoped>
.stats-view {
  background-color: var(--el-bg-color);
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.stat-card {
  text-align: center;
  padding: 10px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--el-color-primary);
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  transition: color 0.3s ease;
}

.cost-value {
  color: var(--el-color-success) !important;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  background-color: var(--el-bg-color-overlay);
}

:deep(.el-card__header) {
  background-color: var(--el-bg-color-overlay);
  border-bottom: 1px solid var(--el-border-color-lighter);
  color: var(--el-text-color-primary);
  font-weight: bold;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  background-color: var(--el-bg-color-overlay);
  color: var(--el-text-color-primary);
}

:deep(.el-form-item__label) {
  color: var(--el-text-color-primary);
}

:deep(.el-radio__label) {
  color: var(--el-text-color-primary);
}

:deep(.el-descriptions__label) {
  color: var(--el-text-color-secondary);
  font-weight: bold;
}

:deep(.el-descriptions__content) {
  color: var(--el-text-color-primary);
}

:deep(.el-descriptions__table) {
  background-color: var(--el-bg-color-overlay);
}

:deep(.el-descriptions__table td),
:deep(.el-descriptions__table th) {
  border-color: var(--el-border-color-lighter);
  background-color: var(--el-bg-color-overlay);
}
</style>

