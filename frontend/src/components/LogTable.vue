<template>
  <el-table
    :data="logs"
    v-loading="loading"
    stripe
    class="log-table"
    :row-class-name="tableRowClassName"
    table-layout="auto"
  >
    <el-table-column prop="request_id" label="请求ID" width="200" show-overflow-tooltip>
      <template #default="{ row }">
        <el-tooltip :content="row.request_id" placement="top">
          <span class="request-id">{{ shortenRequestId(row.request_id) }}</span>
        </el-tooltip>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="时间" width="180">
      <template #default="{ row }">
        <span class="time-text">{{ formatTime(row.created_at) }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="provider" label="供应商" width="140">
      <template #default="{ row }">
        <el-tag 
          size="small" 
          type="info" 
          style="cursor: pointer;"
          @click="handleViewProvider(row.provider)"
        >
          {{ row.provider }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="model" label="模型" width="160">
      <template #default="{ row }">
        <span class="model-text">{{ row.model }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="client_ip" label="访问 IP" width="140">
      <template #default="{ row }">
        <span class="ip-text">{{ row.client_ip || '-' }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="status_code" label="状态" width="100" align="center">
      <template #default="{ row }">
        <el-tag 
          :type="row.status_code === 200 ? 'success' : row.status_code >= 500 ? 'danger' : 'warning'"
          size="small"
          effect="dark"
        >
          {{ row.status_code }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="prompt_tokens" label="输入 Token" width="120" align="right">
      <template #default="{ row }">
        <span class="token-text prompt-tokens">{{ formatTokens(row.prompt_tokens) }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="completion_tokens" label="返回 Token" width="120" align="right">
      <template #default="{ row }">
        <span class="token-text completion-tokens">{{ formatTokens(row.completion_tokens) }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="duration_ms" label="耗时" width="120" align="right">
      <template #default="{ row }">
        <span class="duration-text">{{ formatDuration(row.duration_ms) }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="actual_cost" label="计费金额" width="140" align="right">
      <template #default="{ row }">
        <el-tooltip
          v-if="row.actual_cost !== null && row.actual_cost !== undefined"
          effect="dark"
          placement="left"
          :content="getBillingTooltipContent(row)"
          raw-content
        >
          <span class="cost-text">${{ row.actual_cost.toFixed(6) }}</span>
        </el-tooltip>
        <span v-else class="cost-text">-</span>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="300" fixed="right" align="center">
      <template #default="{ row }">
        <el-button size="small" type="primary" @click="handleView(row)">查看</el-button>
        <el-button 
          size="small" 
          type="success" 
          @click="handleViewDecision(row)"
          v-if="hasDecision(row)"
        >
          查看决策
        </el-button>
        <el-button size="small" type="warning" @click="handleReplay(row)">
          <el-icon><RefreshRight /></el-icon>
          重放
        </el-button>
        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
  
  <ProviderDetailDialog
    v-model="providerDetailVisible"
    :provider="currentProvider"
  />
</template>

<script setup>
import { ref } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import { formatTime, formatDuration, formatTokens } from '../utils/formatters'
import ProviderDetailDialog from './ProviderDetailDialog.vue'
import { getProviders } from '../api/config'

defineProps({
  logs: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['view', 'delete', 'view-decision', 'replay'])

const providerDetailVisible = ref(false)
const currentProvider = ref(null)

async function handleViewProvider(providerName) {
  try {
    // 获取所有供应商，找到匹配的
    const providers = await getProviders(false, true)
    const provider = providers.find(p => p.name === providerName)
    if (provider) {
      currentProvider.value = provider
      providerDetailVisible.value = true
    }
  } catch (error) {
    console.error('获取供应商详情失败:', error)
  }
}

function handleView(row) {
  emit('view', row)
}

function handleDelete(row) {
  emit('delete', row)
}

function handleViewDecision(row) {
  emit('view-decision', row)
}

function handleReplay(row) {
  emit('replay', row)
}

// 缩短请求 ID 显示
function shortenRequestId(requestId) {
  if (!requestId) return '-'
  if (requestId.length <= 20) return requestId
  // 显示前8个字符和后8个字符，中间用省略号
  return `${requestId.substring(0, 8)}...${requestId.substring(requestId.length - 8)}`
}

// 检查日志是否包含决策数据
function hasDecision(row) {
  if (!row) return false
  
  // 检查 ai_response_text 或 response_content 中是否包含 decision
  const aiText = row.ai_response_text || ''
  const responseContent = row.response_content || {}
  
  // 检查文本中是否包含 <decision> 标签或 JSON 数组
  if (aiText.includes('<decision>') || aiText.match(/\[[\s\S]*\]/)) {
    return true
  }
  
  // 检查 response_content 中的 choices
  if (responseContent.choices && Array.isArray(responseContent.choices)) {
    for (const choice of responseContent.choices) {
      const content = choice?.message?.content || ''
      if (content.includes('<decision>') || content.match(/\[[\s\S]*\]/)) {
        return true
      }
    }
  }
  
  return false
}

// 获取计费公式提示内容
function getBillingTooltipContent(row) {
  if (row.actual_cost === null || row.actual_cost === undefined) {
    return '无计费信息'
  }
  
  const promptTokens = row.prompt_tokens || 0
  const completionTokens = row.completion_tokens || 0
  const modelRate = row.model_rate || 1.0
  const completionRate = row.completion_rate || 1.0
  const groupRate = row.group_rate || 1.0
  const rechargeRate = row.recharge_rate || 1.0
  const userDiscountRate = row.user_discount_rate || 1.0
  
  // 计算官方价格
  // 模型倍率 0.15 对应官方输入价格 $0.30 / 1M tokens，所以官方输入价格 = 模型倍率 × 2.0
  // 补全倍率 3 对应官方输出价格 $0.90 / 1M tokens，所以官方输出价格 = 补全倍率 × 0.3
  const officialInputPrice = modelRate * 2.0
  const officialOutputPrice = completionRate * 0.3
  
  // 计算过程
  const weightedTokens = promptTokens + completionTokens * completionRate
  const calculation = `(${promptTokens} + ${completionTokens} × ${completionRate}) × ${modelRate} × ${groupRate} × ${rechargeRate} × ${userDiscountRate} / 500000`
  const calculationResult = (weightedTokens * modelRate * groupRate * rechargeRate * userDiscountRate / 500000).toFixed(6)
  const result = row.actual_cost.toFixed(6)
  
  return `
    <div style="text-align: left; line-height: 1.8; font-size: 13px; max-width: 400px;">
      <div style="font-weight: bold; margin-bottom: 8px; color: #409eff; font-size: 14px;">文本对话计费详情</div>
      <div style="margin-bottom: 4px;"><strong>模型倍率:</strong> ${modelRate}</div>
      <div style="margin-bottom: 4px; margin-left: 20px; color: #909399; font-size: 12px;">对应官方输入价格: $${officialInputPrice.toFixed(2)} / 1M tokens</div>
      <div style="margin-bottom: 4px;"><strong>补全倍率:</strong> ${completionRate}</div>
      <div style="margin-bottom: 4px; margin-left: 20px; color: #909399; font-size: 12px;">对应官方输出价格: $${officialOutputPrice.toFixed(2)} / 1M tokens</div>
      <div style="margin-bottom: 4px;"><strong>分组倍率:</strong> ${groupRate}</div>
      <div style="margin-bottom: 4px;"><strong>充值转换率:</strong> ${rechargeRate}</div>
      <div style="margin-bottom: 4px;"><strong>用户折扣率:</strong> ${userDiscountRate}</div>
      <div style="margin-bottom: 4px;"><strong>输入 tokens:</strong> ${promptTokens}</div>
      <div style="margin-bottom: 4px;"><strong>输出 tokens:</strong> ${completionTokens}</div>
      <div style="margin-top: 8px; margin-bottom: 4px; border-top: 1px solid #e4e7ed; padding-top: 8px;"><strong>计算过程:</strong></div>
      <div style="margin-bottom: 4px; margin-left: 20px; font-family: 'Monaco', 'Menlo', 'Courier New', monospace; color: #67c23a; font-size: 12px; word-break: break-all;">${calculation}</div>
      <div style="margin-bottom: 4px; margin-left: 20px; font-family: 'Monaco', 'Menlo', 'Courier New', monospace; color: #67c23a; font-size: 12px;">= ${calculationResult}</div>
      <div style="margin-top: 8px; font-weight: bold; color: #409eff; font-size: 14px;">实际扣费: $${result}</div>
      <div style="margin-top: 8px; font-size: 12px; color: #909399; border-top: 1px solid #e4e7ed; padding-top: 8px;">仅供参考，以实际扣费为准</div>
    </div>
  `
}

// 表格行样式
function tableRowClassName({ row, rowIndex }) {
  if (row.status_code === 200) {
    return 'success-row'
  } else if (row.status_code >= 500) {
    return 'error-row'
  } else {
    return 'warning-row'
  }
}
</script>

<style scoped>
.log-table {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table) {
  width: 100% !important;
}

:deep(.el-table__body-wrapper) {
  width: 100%;
}

.request-id {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.time-text {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.model-text {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.token-text {
  font-weight: 500;
  font-size: 13px;
}

.prompt-tokens {
  color: var(--el-color-info);
}

.completion-tokens {
  color: var(--el-color-success);
}

.total-tokens {
  color: var(--el-color-primary);
  font-weight: 600;
}

.duration-text {
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.ip-text {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.cost-text {
  font-weight: 600;
  color: var(--el-color-success);
  font-size: 13px;
  cursor: pointer;
}

.cost-text:hover {
  color: var(--el-color-primary);
  text-decoration: underline;
}

/* 行样式 */
:deep(.success-row) {
  background-color: var(--el-color-success-light-9);
}

:deep(.error-row) {
  background-color: var(--el-color-danger-light-9);
}

:deep(.warning-row) {
  background-color: var(--el-color-warning-light-9);
}

/* 暗黑模式下的行样式 */

/* 表格优化 */
:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table__header) {
  background-color: var(--el-bg-color);
}

:deep(.el-table th) {
  background-color: var(--el-bg-color) !important;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--el-border-color-lighter);
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: var(--el-fill-color-lighter);
}
</style>

<style>
/* 暗黑模式下的行样式（全局样式） */
.dark .log-table :deep(.success-row) {
  background-color: rgba(103, 194, 58, 0.1);
}

.dark .log-table :deep(.error-row) {
  background-color: rgba(245, 108, 108, 0.1);
}

.dark .log-table :deep(.warning-row) {
  background-color: rgba(230, 162, 60, 0.1);
}
</style>

