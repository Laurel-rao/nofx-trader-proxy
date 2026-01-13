<template>
  <el-dialog
    v-model="visible"
    title="决策详情"
    width="90%"
    :before-close="handleClose"
  >
    <el-table
      v-if="parsedDecisions.length > 0"
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
    <el-empty v-else description="未找到决策数据" />
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  log: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 解析决策数据
const parsedDecisions = computed(() => {
  if (!props.log) {
    return []
  }
  
  try {
    let content = ''
    
    // 优先使用 ai_response_text
    if (props.log.ai_response_text) {
      content = props.log.ai_response_text
    } else if (props.log.response_content) {
      // 从 response_content 中提取
      const choices = props.log.response_content.choices || []
      if (choices.length > 0) {
        const assistantMessage = choices.find(
          choice => choice.message?.role === 'assistant'
        )
        if (assistantMessage) {
          content = assistantMessage.message.content || ''
        }
      }
    }
    
    if (!content) {
      return []
    }
    
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

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
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

/* 暗黑模式优化 */
.dark .reason-text {
  color: var(--el-text-color-regular);
}
</style>

