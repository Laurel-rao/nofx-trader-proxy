<template>
  <div class="logs-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>请求日志</span>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-switch
              v-model="autoRefreshEnabled"
              active-text="自动刷新"
              @change="handleAutoRefreshChange"
            />
            <el-select
              v-model="refreshInterval"
              :disabled="!autoRefreshEnabled"
              style="width: 100px"
              size="small"
            >
              <el-option label="5秒" :value="5" />
              <el-option label="10秒" :value="10" />
              <el-option label="15秒" :value="15" />
              <el-option label="30秒" :value="30" />
              <el-option label="60秒" :value="60" />
            </el-select>
            <ExportButton :data="logList" filename="logs" style="margin-right: 10px" />
            <el-button type="danger" @click="handleBatchDelete" :disabled="selectedLogs.length === 0">
              批量删除
            </el-button>
          </div>
        </div>
      </template>
      
      <LogFilter :providers="providers" @search="handleFilter" />
      
      <LogTable
        :logs="logList"
        :loading="loading"
        @view="handleViewDetail"
        @delete="handleDelete"
        @view-decision="handleViewDecision"
        @replay="handleReplay"
      />
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 决策对话框 -->
    <DecisionDialog
      v-model="decisionVisible"
      :log="currentDecisionLog"
    />
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="日志详情"
      width="80%"
    >
      <el-descriptions :column="2" border v-if="currentLog">
        <el-descriptions-item label="请求ID">{{ currentLog.request_id }}</el-descriptions-item>
        <el-descriptions-item label="供应商请求ID" v-if="currentLog.provider_request_id">
          <el-tag type="info" size="small">{{ currentLog.provider_request_id }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="访问 IP" v-if="currentLog.client_ip">
          <el-tag type="info" size="small">{{ currentLog.client_ip }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentLog.provider }}</el-descriptions-item>
        <el-descriptions-item label="模型">{{ currentLog.model }}</el-descriptions-item>
        <el-descriptions-item label="状态码">
          <el-tag :type="currentLog.status_code === 200 ? 'success' : 'danger'">
            {{ currentLog.status_code }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">{{ formatDuration(currentLog.duration_ms) }}</el-descriptions-item>
        <el-descriptions-item label="Prompt Tokens">{{ formatTokens(currentLog.prompt_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="Completion Tokens">{{ formatTokens(currentLog.completion_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="Total Tokens">{{ formatTokens(currentLog.total_tokens) }}</el-descriptions-item>
        
        <!-- 计费信息 -->
        <el-descriptions-item label="实际扣费" v-if="currentLog.actual_cost">
          <el-text type="success" style="font-weight: bold">${{ currentLog.actual_cost.toFixed(6) }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="模型倍率" v-if="currentLog.model_rate">
          {{ currentLog.model_rate }}
        </el-descriptions-item>
        <el-descriptions-item label="补全倍率" v-if="currentLog.completion_rate">
          {{ currentLog.completion_rate }}
        </el-descriptions-item>
        <el-descriptions-item label="分组倍率" v-if="currentLog.group_rate">
          {{ currentLog.group_rate }}
        </el-descriptions-item>
        <el-descriptions-item label="充值转换率" v-if="currentLog.recharge_rate">
          {{ currentLog.recharge_rate }}
        </el-descriptions-item>
        <el-descriptions-item label="用户折扣率" v-if="currentLog.user_discount_rate">
          {{ currentLog.user_discount_rate }}
        </el-descriptions-item>
        
        <el-descriptions-item label="用户ID" :span="2">{{ currentLog.user_id || '-' }}</el-descriptions-item>
        
        <!-- 请求参数详情 -->
        <el-descriptions-item label="Temperature" v-if="currentLog.temperature">
          {{ currentLog.temperature }}
        </el-descriptions-item>
        <el-descriptions-item label="Top P" v-if="currentLog.top_p">
          {{ currentLog.top_p }}
        </el-descriptions-item>
        <el-descriptions-item label="Top K" v-if="currentLog.top_k">
          {{ currentLog.top_k }}
        </el-descriptions-item>
        <el-descriptions-item label="Max Tokens" v-if="currentLog.max_tokens">
          {{ currentLog.max_tokens }}
        </el-descriptions-item>
        
        <el-descriptions-item label="错误信息" :span="2" v-if="currentLog.error_message">
          <el-text type="danger">{{ currentLog.error_message }}</el-text>
        </el-descriptions-item>
        
        <!-- 用户输入文本 -->
        <el-descriptions-item label="用户输入" :span="2" v-if="currentLog.user_input_text">
          <div class="text-content user-input">
            <pre class="text-pre">{{ currentLog.user_input_text }}</pre>
          </div>
        </el-descriptions-item>
        
        <!-- AI返回文本 -->
        <el-descriptions-item label="AI返回" :span="2" v-if="currentLog.ai_response_text">
          <div class="text-content ai-response">
            <pre class="text-pre">{{ currentLog.ai_response_text }}</pre>
          </div>
        </el-descriptions-item>
        
        <!-- 完整JSON（可折叠） -->
        <el-descriptions-item label="完整请求参数" :span="2">
          <el-collapse>
            <el-collapse-item title="查看完整JSON" name="request">
              <pre class="json-view">{{ formatJSON(currentLog.request_params) }}</pre>
            </el-collapse-item>
          </el-collapse>
        </el-descriptions-item>
        <el-descriptions-item label="完整响应内容" :span="2" v-if="currentLog.response_content">
          <el-collapse>
            <el-collapse-item title="查看完整JSON" name="response">
              <pre class="json-view">{{ formatJSON(currentLog.response_content) }}</pre>
            </el-collapse-item>
          </el-collapse>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogs, deleteLog } from '../api/logs'
import LogTable from '../components/LogTable.vue'
import LogFilter from '../components/LogFilter.vue'
import ExportButton from '../components/ExportButton.vue'
import DecisionDialog from '../components/DecisionDialog.vue'
import { formatTime, formatDuration, formatTokens } from '../utils/formatters'

const router = useRouter()
const loading = ref(false)
const logList = ref([])
const selectedLogs = ref([])
const providers = ref([])
const detailVisible = ref(false)
const currentLog = ref(null)
const decisionVisible = ref(false)
const currentDecisionLog = ref(null)

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const filterParams = ref({})

// 自动刷新相关
const autoRefreshEnabled = ref(false)
const refreshInterval = ref(60) // 默认60秒
let refreshTimer = null

async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      ...filterParams.value
    }
    const data = await getLogs(params)
    logList.value = data.items
    pagination.value.total = data.total
  } catch (error) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

function handleFilter(params) {
  filterParams.value = params
  pagination.value.page = 1
  fetchLogs()
}

function handlePageChange(page) {
  pagination.value.page = page
  fetchLogs()
}

function handleSizeChange(size) {
  pagination.value.pageSize = size
  pagination.value.page = 1
  fetchLogs()
}

function handleViewDetail(row) {
  currentLog.value = row
  detailVisible.value = true
}

function handleViewDecision(row) {
  currentDecisionLog.value = row
  decisionVisible.value = true
}

function handleReplay(row) {
  // 将请求参数保存到 localStorage
  const replayData = {
    provider: row.provider,
    model: row.model,
    request_params: row.request_params
  }
  localStorage.setItem('replay_request', JSON.stringify(replayData))
  
  // 跳转到测试页面
  router.push('/test')
  ElMessage.success('已加载请求参数，正在跳转到测试页面...')
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除这条日志吗？', '提示', {
      type: 'warning'
    })
    await deleteLog(row.id)
    ElMessage.success('删除成功')
    fetchLogs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleBatchDelete() {
  ElMessage.warning('批量删除功能待实现')
}

// 格式化 JSON
function formatJSON(obj) {
  if (!obj) return ''
  try {
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return String(obj)
  }
}

// 提取供应商列表
function extractProviders() {
  const providerSet = new Set()
  logList.value.forEach(log => {
    if (log.provider) {
      providerSet.add(log.provider)
    }
  })
  providers.value = Array.from(providerSet)
}

// 自动刷新处理
function handleAutoRefreshChange(enabled) {
  if (enabled) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

function startAutoRefresh() {
  stopAutoRefresh() // 先清除可能存在的定时器
  refreshTimer = setInterval(() => {
    if (!loading.value) {
      fetchLogs()
    }
  }, refreshInterval.value * 1000)
}

function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听刷新间隔变化
watch(refreshInterval, () => {
  if (autoRefreshEnabled.value) {
    startAutoRefresh()
  }
})

onMounted(() => {
  fetchLogs()
})

onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.logs-view {
  background-color: var(--el-bg-color);
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 16px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

.json-view {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  max-height: 600px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'Courier New', monospace;
}

.text-content {
  background-color: var(--el-fill-color-lighter);
  padding: 20px;
  border-radius: 8px;
  min-height: 200px;
  max-height: 600px;
  overflow: auto;
  border-left: 4px solid var(--el-color-primary);
  transition: all 0.3s ease;
}

.text-content.user-input {
  border-left-color: var(--el-color-success);
  background-color: var(--el-color-success-light-9);
}

.text-content.ai-response {
  border-left-color: var(--el-color-primary);
  background-color: var(--el-fill-color-lighter);
}

.text-pre {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  color: var(--el-text-color-primary);
}

/* 暗黑模式下的文本内容 */
.dark .text-content.user-input {
  background-color: rgba(103, 194, 58, 0.1);
}

.dark .text-content.ai-response {
  background-color: rgba(64, 158, 255, 0.1);
}

.json-view {
  background-color: var(--el-fill-color-lighter);
  transition: background-color 0.3s ease;
}

/* 对话框优化 */
:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 20px 24px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

/* 描述列表优化 */
:deep(.el-descriptions) {
  border-radius: 8px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

:deep(.el-descriptions__content) {
  color: var(--el-text-color-regular);
}
</style>

