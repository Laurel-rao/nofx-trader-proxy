<template>
  <div class="test-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>API 测试工具</span>
          <div style="display: flex; gap: 10px;">
            <el-button type="success" @click="handleLoadDecisionTest" :loading="loadingPrompts">
              <el-icon><DocumentCopy /></el-icon>
              决策测试
            </el-button>
            <el-button type="primary" @click="handleTest" :loading="loading">
              <el-icon><Promotion /></el-icon>
              发送请求
            </el-button>
          </div>
        </div>
      </template>

      <el-form :model="formData" label-width="120px" label-position="left">
        <!-- 供应商选择 -->
        <el-form-item label="选择供应商">
          <el-select
            v-model="formData.provider"
            placeholder="请选择供应商"
            style="width: 300px"
            @change="handleProviderChange"
          >
            <el-option
              v-for="provider in providers"
              :key="provider.id"
              :label="`${provider.name} (${provider.default_model})`"
              :value="provider.id"
              :disabled="!provider.is_enabled"
            >
              <span style="float: left">{{ provider.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ provider.default_model }}
                <el-tag
                  :type="provider.is_enabled ? 'success' : 'info'"
                  size="small"
                  style="margin-left: 8px"
                >
                  {{ provider.is_enabled ? '启用' : '禁用' }}
                </el-tag>
              </span>
            </el-option>
          </el-select>
          <el-button
            type="text"
            @click="fetchProviders"
            style="margin-left: 10px"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>

        <!-- 模型选择 -->
        <el-form-item label="模型">
          <el-input
            v-model="formData.model"
            placeholder="例如: gpt-3.5-turbo, gpt-4"
            style="width: 300px"
          />
          <span class="form-tip">留空则使用供应商默认模型</span>
        </el-form-item>

        <!-- 消息列表 -->
        <el-form-item label="消息">
          <div class="messages-container">
            <div
              v-for="(message, index) in formData.messages"
              :key="index"
              class="message-item"
            >
              <el-select
                v-model="message.role"
                style="width: 120px; margin-right: 10px"
              >
                <el-option label="system" value="system" />
                <el-option label="user" value="user" />
                <el-option label="assistant" value="assistant" />
              </el-select>
              <el-input
                v-model="message.content"
                type="textarea"
                :rows="3"
                placeholder="输入消息内容"
                style="flex: 1; margin-right: 10px"
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                @click="removeMessage(index)"
                :disabled="formData.messages.length <= 1"
              />
            </div>
            <el-button
              type="dashed"
              @click="addMessage"
              style="width: 100%"
            >
              <el-icon><Plus /></el-icon>
              添加消息
            </el-button>
          </div>
        </el-form-item>

        <!-- 高级参数 -->
        <el-collapse>
          <el-collapse-item title="高级参数" name="advanced">
            <el-form-item label="Temperature">
              <el-slider
                v-model="formData.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                show-input
                style="width: 400px"
              />
              <span class="form-tip">控制输出的随机性，值越大越随机</span>
            </el-form-item>

            <el-form-item label="Top K">
              <el-input-number
                v-model="formData.top_k"
                :min="1"
                :max="100"
                style="width: 200px"
              />
              <span class="form-tip">限制采样时的候选 token 数量</span>
            </el-form-item>

            <el-form-item label="Max Tokens">
              <el-input-number
                v-model="formData.max_tokens"
                :min="1"
                :max="4096"
                style="width: 200px"
              />
              <span class="form-tip">留空则不限制</span>
            </el-form-item>

            <el-form-item label="Top P">
              <el-slider
                v-model="formData.top_p"
                :min="0"
                :max="1"
                :step="0.01"
                show-input
                style="width: 400px"
              />
              <span class="form-tip">核采样，控制输出的多样性</span>
            </el-form-item>

            <el-form-item label="Frequency Penalty">
              <el-slider
                v-model="formData.frequency_penalty"
                :min="-2"
                :max="2"
                :step="0.1"
                show-input
                style="width: 400px"
              />
            </el-form-item>

            <el-form-item label="Presence Penalty">
              <el-slider
                v-model="formData.presence_penalty"
                :min="-2"
                :max="2"
                :step="0.1"
                show-input
                style="width: 400px"
              />
            </el-form-item>

            <el-form-item label="Stream">
              <el-switch v-model="formData.stream" />
              <span class="form-tip">流式响应（当前版本暂不支持）</span>
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form>
    </el-card>

    <!-- 响应结果 -->
    <el-card v-if="response" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>响应结果</span>
          <el-button
            type="text"
            @click="copyResponse"
          >
            <el-icon><Document /></el-icon>
            复制
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="决策表格" name="decision" v-if="parsedDecisions.length > 0">
          <el-table
            :data="parsedDecisions"
            stripe
            border
            style="width: 100%"
            :row-class-name="getRowClassName"
          >
            <el-table-column prop="symbol" label="交易对" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="large">{{ row.symbol }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="action" label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="getActionTagType(row.action)" size="large">
                  {{ formatAction(row.action) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="leverage" label="杠杆" width="100" align="center" v-if="hasLeverage">
              <template #default="{ row }">
                <span v-if="row.leverage">{{ row.leverage }}x</span>
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="position_size_usd" label="仓位(USD)" width="120" align="center" v-if="hasPositionSize">
              <template #default="{ row }">
                <span v-if="row.position_size_usd">${{ row.position_size_usd }}</span>
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="stop_loss" label="止损" width="120" align="center" v-if="hasStopLoss">
              <template #default="{ row }">
                <span v-if="row.stop_loss" class="text-danger">{{ row.stop_loss }}</span>
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="take_profit" label="止盈" width="120" align="center" v-if="hasTakeProfit">
              <template #default="{ row }">
                <span v-if="row.take_profit" class="text-success">{{ row.take_profit }}</span>
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="120" align="center" v-if="hasConfidence">
              <template #default="{ row }">
                <el-progress
                  v-if="row.confidence"
                  :percentage="row.confidence"
                  :color="getConfidenceColor(row.confidence)"
                  :stroke-width="20"
                  text-inside
                />
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="risk_usd" label="风险(USD)" width="120" align="center" v-if="hasRisk">
              <template #default="{ row }">
                <span v-if="row.risk_usd" class="text-warning">${{ row.risk_usd }}</span>
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" min-width="300" align="left" v-if="hasReason" show-overflow-tooltip>
              <template #default="{ row }">
                <div v-if="row.reason" class="reason-text">
                  {{ row.reason }}
                </div>
                <span v-else class="text-placeholder">-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="完整响应" name="full">
          <pre class="response-content">{{ JSON.stringify(response, null, 2) }}</pre>
        </el-tab-pane>
        <el-tab-pane label="消息内容" name="message">
          <div class="message-content">
            <div
              v-for="(choice, index) in response.choices"
              :key="index"
              class="choice-item"
            >
              <el-tag type="info" style="margin-bottom: 10px">
                {{ choice.message.role }}
              </el-tag>
              <div class="content-text">{{ choice.message.content }}</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="使用统计" name="usage" v-if="response.usage">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Prompt Tokens">
              {{ response.usage.prompt_tokens }}
            </el-descriptions-item>
            <el-descriptions-item label="Completion Tokens">
              {{ response.usage.completion_tokens }}
            </el-descriptions-item>
            <el-descriptions-item label="Total Tokens">
              {{ response.usage.total_tokens }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 错误信息 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="true"
      @close="error = null"
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Promotion,
  Refresh,
  Plus,
  Delete,
  Document,
  DocumentCopy
} from '@element-plus/icons-vue'
import { getProviders, getDecisionTestPrompts } from '../api/config'
import { testChatCompletions } from '../api/test'

const loading = ref(false)
const loadingPrompts = ref(false)
const providers = ref([])
const response = ref(null)
const error = ref(null)
const activeTab = ref('full')

// 解析 AI 返回的决策数据
const parsedDecisions = computed(() => {
  if (!response.value || !response.value.choices || response.value.choices.length === 0) {
    return []
  }
  
  try {
    // 获取 assistant 的消息内容
    const assistantMessage = response.value.choices.find(
      choice => choice.message.role === 'assistant'
    )
    
    if (!assistantMessage) {
      return []
    }
    
    const content = assistantMessage.message.content
    
    // 尝试从 <decision> 标签中提取 JSON
    let jsonStr = ''
    const decisionMatch = content.match(/<decision>([\s\S]*?)<\/decision>/i)
    if (decisionMatch) {
      jsonStr = decisionMatch[1].trim()
    } else {
      // 如果没有标签，尝试直接查找 JSON 数组
      const jsonArrayMatch = content.match(/\[[\s\S]*\]/)
      if (jsonArrayMatch) {
        jsonStr = jsonArrayMatch[0]
      } else {
        return []
      }
    }
    
    // 解析 JSON
    const decisions = JSON.parse(jsonStr)
    
    // 确保是数组
    if (!Array.isArray(decisions)) {
      return []
    }
    
    return decisions
  } catch (err) {
    console.error('解析决策数据失败:', err)
    return []
  }
})

// 检查是否有特定字段
const hasLeverage = computed(() => {
  return parsedDecisions.value.some(d => d.leverage !== undefined)
})

const hasPositionSize = computed(() => {
  return parsedDecisions.value.some(d => d.position_size_usd !== undefined)
})

const hasStopLoss = computed(() => {
  return parsedDecisions.value.some(d => d.stop_loss !== undefined)
})

const hasTakeProfit = computed(() => {
  return parsedDecisions.value.some(d => d.take_profit !== undefined)
})

const hasConfidence = computed(() => {
  return parsedDecisions.value.some(d => d.confidence !== undefined)
})

const hasRisk = computed(() => {
  return parsedDecisions.value.some(d => d.risk_usd !== undefined)
})

const hasReason = computed(() => {
  return parsedDecisions.value.some(d => d.reason !== undefined && d.reason !== null && d.reason !== '')
})

// 格式化操作类型
function formatAction(action) {
  const actionMap = {
    'open_long': '开多',
    'open_short': '开空',
    'close_long': '平多',
    'close_short': '平空',
    'wait': '等待',
    'hold': '持有'
  }
  return actionMap[action] || action
}

// 获取操作标签类型
function getActionTagType(action) {
  const typeMap = {
    'open_long': 'success',
    'open_short': 'danger',
    'close_long': 'warning',
    'close_short': 'warning',
    'wait': 'info',
    'hold': ''
  }
  return typeMap[action] || ''
}

// 获取行样式类名
function getRowClassName({ row }) {
  if (row.action === 'open_long') {
    return 'row-open-long'
  } else if (row.action === 'open_short') {
    return 'row-open-short'
  } else if (row.action === 'wait' || row.action === 'hold') {
    return 'row-wait'
  }
  return ''
}

// 获取置信度颜色
function getConfidenceColor(confidence) {
  if (confidence >= 90) {
    return '#67c23a' // 绿色
  } else if (confidence >= 70) {
    return '#e6a23c' // 橙色
  } else if (confidence >= 50) {
    return '#f56c6c' // 红色
  }
  return '#909399' // 灰色
}

const formData = ref({
  provider: null,
  model: '',
  messages: [
    {
      role: 'user',
      content: ''
    }
  ],
  temperature: 1.0,
  top_k: null,
  max_tokens: null,
  top_p: 1.0,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  stream: false
})

// 获取供应商列表
async function fetchProviders() {
  try {
    providers.value = await getProviders()
    if (providers.value.length > 0 && !formData.value.provider) {
      // 默认选择第一个启用的供应商
      const enabledProvider = providers.value.find(p => p.is_enabled)
      if (enabledProvider) {
        formData.value.provider = enabledProvider.id
        handleProviderChange(enabledProvider.id)
      }
    }
  } catch (err) {
    ElMessage.error('获取供应商列表失败')
  }
}

// 供应商改变时更新模型
function handleProviderChange(providerId) {
  const provider = providers.value.find(p => p.id === providerId)
  if (provider && !formData.value.model) {
    formData.value.model = provider.default_model
  }
}

// 添加消息
function addMessage() {
  formData.value.messages.push({
    role: 'user',
    content: ''
  })
}

// 删除消息
function removeMessage(index) {
  if (formData.value.messages.length > 1) {
    formData.value.messages.splice(index, 1)
  }
}

// 加载决策测试提示
async function handleLoadDecisionTest() {
  loadingPrompts.value = true
  try {
    const data = await getDecisionTestPrompts()
    
    // 清空现有消息
    formData.value.messages = []
    
    // 添加 system 消息
    if (data.system_prompt) {
      formData.value.messages.push({
        role: 'system',
        content: data.system_prompt
      })
    }
    
    // 添加 user 消息
    if (data.user_prompt) {
      formData.value.messages.push({
        role: 'user',
        content: data.user_prompt
      })
    }
    
    ElMessage.success('决策测试提示已加载')
  } catch (err) {
    ElMessage.error('加载决策测试提示失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    loadingPrompts.value = false
  }
}

// 发送测试请求
async function handleTest() {
  // 验证
  if (!formData.value.provider) {
    ElMessage.warning('请选择供应商')
    return
  }

  if (formData.value.messages.length === 0) {
    ElMessage.warning('请至少添加一条消息')
    return
  }

  const hasContent = formData.value.messages.some(
    msg => msg.content && msg.content.trim()
  )
  if (!hasContent) {
    ElMessage.warning('请填写消息内容')
    return
  }

  // 构建请求数据
  const requestData = {
    messages: formData.value.messages.map(msg => ({
      role: msg.role,
      content: msg.content.trim()
    })).filter(msg => msg.content)
  }

  // 添加可选参数
  if (formData.value.model) {
    requestData.model = formData.value.model
  }
  if (formData.value.temperature !== undefined) {
    requestData.temperature = formData.value.temperature
  }
  if (formData.value.top_k !== null && formData.value.top_k !== undefined) {
    requestData.top_k = formData.value.top_k
  }
  if (formData.value.max_tokens) {
    requestData.max_tokens = formData.value.max_tokens
  }
  if (formData.value.top_p !== undefined) {
    requestData.top_p = formData.value.top_p
  }
  if (formData.value.frequency_penalty !== undefined) {
    requestData.frequency_penalty = formData.value.frequency_penalty
  }
  if (formData.value.presence_penalty !== undefined) {
    requestData.presence_penalty = formData.value.presence_penalty
  }
  if (formData.value.stream) {
    requestData.stream = formData.value.stream
  }

  loading.value = true
  error.value = null
  response.value = null

  try {
    // 根据选择的 provider ID 获取 provider 名称
    const selectedProvider = providers.value.find(p => p.id === formData.value.provider)
    const providerName = selectedProvider ? selectedProvider.name : null
    
    const data = await testChatCompletions(requestData, providerName)
    response.value = data
    // 如果解析到决策数据，默认显示决策表格，否则显示消息内容
    const decisions = parseDecisionsFromResponse(data)
    activeTab.value = decisions.length > 0 ? 'decision' : 'message'
    ElMessage.success('请求成功')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || '请求失败'
    ElMessage.error('请求失败')
  } finally {
    loading.value = false
  }
}

// 解析决策数据（用于初始化时判断）
function parseDecisionsFromResponse(responseData) {
  if (!responseData || !responseData.choices || responseData.choices.length === 0) {
    return []
  }
  
  try {
    const assistantMessage = responseData.choices.find(
      choice => choice.message.role === 'assistant'
    )
    
    if (!assistantMessage) {
      return []
    }
    
    const content = assistantMessage.message.content
    let jsonStr = ''
    
    const decisionMatch = content.match(/<decision>([\s\S]*?)<\/decision>/i)
    if (decisionMatch) {
      jsonStr = decisionMatch[1].trim()
    } else {
      const jsonArrayMatch = content.match(/\[[\s\S]*\]/)
      if (jsonArrayMatch) {
        jsonStr = jsonArrayMatch[0]
      } else {
        return []
      }
    }
    
    const decisions = JSON.parse(jsonStr)
    return Array.isArray(decisions) ? decisions : []
  } catch (err) {
    return []
  }
}

// 复制响应
function copyResponse() {
  if (!response.value) return

  const text = JSON.stringify(response.value, null, 2)
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 加载重放数据
function loadReplayData() {
  try {
    const replayDataStr = localStorage.getItem('replay_request')
    if (!replayDataStr) {
      return false
    }
    
    const replayData = JSON.parse(replayDataStr)
    
    // 清除 localStorage 中的数据
    localStorage.removeItem('replay_request')
    
    // 填充供应商
    if (replayData.provider && providers.value.length > 0) {
      const provider = providers.value.find(p => p.name === replayData.provider)
      if (provider) {
        formData.value.provider = provider.id
        handleProviderChange(provider.id)
      }
    }
    
    // 填充模型
    if (replayData.model) {
      formData.value.model = replayData.model
    }
    
    // 填充消息
    if (replayData.request_params && replayData.request_params.messages) {
      formData.value.messages = replayData.request_params.messages.map(msg => ({
        role: msg.role,
        content: msg.content || ''
      }))
    }
    
    // 填充其他参数
    if (replayData.request_params) {
      const params = replayData.request_params
      if (params.temperature !== undefined) {
        formData.value.temperature = params.temperature
      }
      if (params.top_p !== undefined) {
        formData.value.top_p = params.top_p
      }
      if (params.top_k !== undefined) {
        formData.value.top_k = params.top_k
      }
      if (params.max_tokens !== undefined) {
        formData.value.max_tokens = params.max_tokens
      }
      if (params.frequency_penalty !== undefined) {
        formData.value.frequency_penalty = params.frequency_penalty
      }
      if (params.presence_penalty !== undefined) {
        formData.value.presence_penalty = params.presence_penalty
      }
      if (params.stream !== undefined) {
        formData.value.stream = params.stream
      }
    }
    
    ElMessage.success('已加载重放请求参数')
    return true
  } catch (err) {
    console.error('加载重放数据失败:', err)
    localStorage.removeItem('replay_request')
    return false
  }
}

onMounted(async () => {
  await fetchProviders()
  // 等待 providers 加载完成后再加载重放数据
  loadReplayData()
})
</script>

<style scoped>
.test-view {
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

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.messages-container {
  width: 100%;
}

.message-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.response-content {
  background-color: var(--el-fill-color-lighter);
  color: var(--el-text-color-primary);
  padding: 15px;
  border-radius: 8px;
  max-height: 600px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'Courier New', monospace;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.message-content {
  padding: 10px;
}

.choice-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.content-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

/* 表格行样式 */
:deep(.row-open-long) {
  background-color: rgba(103, 194, 58, 0.1) !important;
}

:deep(.row-open-long:hover) {
  background-color: rgba(103, 194, 58, 0.15) !important;
}

:deep(.row-open-short) {
  background-color: rgba(245, 108, 108, 0.1) !important;
}

:deep(.row-open-short:hover) {
  background-color: rgba(245, 108, 108, 0.15) !important;
}

:deep(.row-wait) {
  background-color: rgba(144, 147, 153, 0.1) !important;
}

:deep(.row-wait:hover) {
  background-color: rgba(144, 147, 153, 0.15) !important;
}

.text-placeholder {
  color: #c0c4cc;
  font-style: italic;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.text-warning {
  color: #e6a23c;
  font-weight: 500;
}

.reason-text {
  color: var(--el-text-color-regular);
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-word;
  padding: 4px 0;
  font-size: 13px;
}
</style>

<style>
/* 暗黑模式优化 */
.dark .choice-item {
  background-color: var(--el-fill-color-darker);
  border-color: var(--el-border-color);
}

.dark .content-text {
  color: var(--el-text-color-primary);
}

.dark .response-content {
  background-color: var(--el-fill-color-darker);
  color: var(--el-text-color-primary);
}

/* 确保文字在暗黑模式下有足够对比度 */
.dark .message-content {
  color: var(--el-text-color-primary);
}

.dark .reason-text {
  color: var(--el-text-color-regular);
}
</style>

