<template>
  <el-dialog
    v-model="visible"
    title="供应商详情"
    width="800px"
    @close="handleClose"
  >
    <el-descriptions :column="2" border v-if="provider">
      <el-descriptions-item label="供应商名称" :span="2">
        <el-tag type="info" size="large">{{ provider.name }}</el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="API Base URL" :span="2">
        <span style="font-family: monospace; word-break: break-all;">{{ provider.api_base_url }}</span>
      </el-descriptions-item>
      
      <el-descriptions-item label="API Key">
        <span style="font-family: monospace;">{{ provider.api_key }}</span>
      </el-descriptions-item>
      
      <el-descriptions-item label="默认模型">
        <el-tag size="small">{{ provider.default_model }}</el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="优先级">
        <el-tag size="small" type="info">{{ provider.priority }}</el-tag>
        <span style="margin-left: 8px; color: var(--el-text-color-secondary); font-size: 12px;">
          数字越小优先级越高
        </span>
      </el-descriptions-item>
      
      <el-descriptions-item label="状态">
        <el-tag :type="provider.is_enabled ? 'success' : 'info'">
          {{ provider.is_enabled ? '启用' : '禁用' }}
        </el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="创建时间">
        {{ formatTime(provider.created_at) }}
      </el-descriptions-item>
      
      <el-descriptions-item label="更新时间" v-if="provider.updated_at">
        {{ formatTime(provider.updated_at) }}
      </el-descriptions-item>
      
      <!-- 计费配置 -->
      <el-descriptions-item label="计费配置" :span="2">
        <el-divider style="margin: 10px 0;" />
      </el-descriptions-item>
      
      <el-descriptions-item label="模型倍率">
        {{ provider.model_rate || 1.0 }}
      </el-descriptions-item>
      
      <el-descriptions-item label="补全倍率">
        {{ provider.completion_rate || 1.0 }}
      </el-descriptions-item>
      
      <el-descriptions-item label="分组倍率">
        {{ provider.group_rate || 1.0 }}
      </el-descriptions-item>
      
      <el-descriptions-item label="充值转换率">
        {{ provider.recharge_rate || 1.0 }}
      </el-descriptions-item>
      
      <!-- 统计信息 -->
      <el-descriptions-item label="统计信息" :span="2" v-if="provider.statistics">
        <el-divider style="margin: 10px 0;" />
      </el-descriptions-item>
      
      <el-descriptions-item label="访问次数" v-if="provider.statistics">
        <span style="font-weight: bold; color: var(--el-color-primary);">
          {{ provider.statistics.total_requests || 0 }}
        </span>
      </el-descriptions-item>
      
      <el-descriptions-item label="计费总额" v-if="provider.statistics">
        <span style="font-weight: bold; color: var(--el-color-success);">
          ${{ (provider.statistics.total_cost || 0).toFixed(6) }}
        </span>
      </el-descriptions-item>
      
      <el-descriptions-item label="成功次数" v-if="provider.statistics">
        <el-tag type="success" size="small">
          {{ provider.statistics.success_count || 0 }}
        </el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="失败次数" v-if="provider.statistics">
        <el-tag type="danger" size="small">
          {{ provider.statistics.failure_count || 0 }}
        </el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="成功率" v-if="provider.statistics">
        <span 
          :style="{
            fontWeight: 'bold',
            color: getSuccessRateColor(provider.statistics.success_rate)
          }"
        >
          {{ provider.statistics.success_rate || 0 }}%
        </span>
      </el-descriptions-item>
      
      <el-descriptions-item label="最近访问" v-if="provider.statistics && provider.statistics.last_access_time">
        {{ formatTime(provider.statistics.last_access_time) }}
      </el-descriptions-item>
      
      <el-descriptions-item label="最近访问" v-else-if="provider.statistics && provider.statistics.total_requests === 0">
        <span style="color: var(--el-text-color-placeholder)">暂无访问记录</span>
      </el-descriptions-item>
    </el-descriptions>
    
    <div v-else style="text-align: center; padding: 40px; color: var(--el-text-color-placeholder);">
      加载中...
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { formatTime } from '../utils/formatters'
import { getProvider } from '../api/config'

const props = defineProps({
  modelValue: Boolean,
  providerName: String,  // 供应商名称（用于从日志表格点击时）
  providerId: String,    // 供应商 ID（用于从配置列表点击时）
  provider: Object       // 直接传入的供应商对象（可选）
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const provider = ref(null)
const loading = ref(false)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    fetchProvider()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function fetchProvider() {
  // 如果直接传入了 provider 对象，直接使用
  if (props.provider) {
    provider.value = props.provider
    return
  }
  
  loading.value = true
  try {
    // 如果有 providerId，使用 ID 获取
    if (props.providerId) {
      const data = await getProvider(props.providerId)
      provider.value = data
    } 
    // 如果有 providerName，需要从列表中查找（因为 API 没有根据名称获取的接口）
    // 这里我们需要从父组件传入完整的 provider 对象
    else if (props.providerName) {
      // 如果只有名称，提示需要传入完整对象
      console.warn('需要传入完整的 provider 对象或 providerId')
    }
  } catch (error) {
    console.error('获取供应商详情失败:', error)
  } finally {
    loading.value = false
  }
}

function handleClose() {
  visible.value = false
  provider.value = null
}

function getSuccessRateColor(rate) {
  if (rate >= 95) return 'var(--el-color-success)'
  if (rate >= 80) return 'var(--el-color-warning)'
  return 'var(--el-color-danger)'
}
</script>

<style scoped>
:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-dialog__header) {
  background-color: var(--el-bg-color-overlay);
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 15px 20px;
}

:deep(.el-dialog__title) {
  color: var(--el-text-color-primary);
  font-weight: bold;
}

:deep(.el-dialog__body) {
  padding: 20px;
  background-color: var(--el-bg-color);
}

:deep(.el-descriptions__label) {
  font-weight: bold;
  color: var(--el-text-color-secondary);
  width: 150px;
}

:deep(.el-descriptions__content) {
  color: var(--el-text-color-primary);
}
</style>

