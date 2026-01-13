<template>
  <el-dialog
    v-model="visible"
    :title="formData.id ? '编辑供应商' : '添加供应商'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="供应商名称" prop="name">
        <el-input v-model="formData.name" placeholder="例如: OpenAI" />
      </el-form-item>
      
      <el-form-item label="API Base URL" prop="api_base_url">
        <el-input v-model="formData.api_base_url" placeholder="https://api.openai.com" />
      </el-form-item>
      
      <el-form-item label="API Key" prop="api_key">
        <el-input
          v-model="formData.api_key"
          type="password"
          show-password
          :placeholder="formData.id ? '留空则不修改 API Key' : '输入 API Key'"
        />
        <div v-if="formData.id" style="margin-top: 5px; color: #909399; font-size: 12px">
          留空则保留原有 API Key
        </div>
      </el-form-item>
      
      <el-form-item label="默认模型" prop="default_model">
        <div style="display: flex; gap: 10px; width: 100%;">
          <el-select
            v-model="formData.default_model"
            placeholder="请选择或输入模型名称"
            filterable
            allow-create
            style="flex: 1"
            :loading="loadingModels"
          >
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.id"
              :value="model.id"
            >
              <div style="display: flex; justify-content: space-between;">
                <span>{{ model.id }}</span>
                <span style="color: #909399; font-size: 12px;">{{ model.owned_by || '' }}</span>
              </div>
            </el-option>
          </el-select>
          <el-button
            type="primary"
            :loading="loadingModels"
            :disabled="!formData.api_base_url || !formData.api_key"
            @click="fetchModels"
          >
            获取模型列表
          </el-button>
        </div>
        <div style="margin-top: 5px; color: #909399; font-size: 12px">
          填写 API Base URL 和 API Key 后，点击"获取模型列表"按钮获取可用模型
        </div>
      </el-form-item>
      
      <el-form-item label="优先级" prop="priority">
        <el-input-number v-model="formData.priority" :min="0" />
        <span style="margin-left: 10px; color: #909399; font-size: 12px">
          数字越小优先级越高
        </span>
      </el-form-item>
      
      <el-form-item label="启用状态" prop="is_enabled">
        <el-switch v-model="formData.is_enabled" />
      </el-form-item>
      
      <!-- 计费配置 -->
      <el-divider>计费配置</el-divider>
      
      <el-form-item label="快速配置">
        <el-input
          v-model="billingConfigText"
          type="textarea"
          :rows="3"
          placeholder="粘贴计费配置文本，系统会自动识别并填充倍率字段&#10;例如：模型倍率: 0.15, 补全倍率: 3, 分组倍率: 1, 充值转换率: 0.88"
          @paste="handleBillingPaste"
        />
        <span class="form-tip">粘贴配置文本后会自动填充下方的倍率字段</span>
      </el-form-item>
      
      <el-form-item label="模型倍率" prop="model_rate">
        <el-input-number
          v-model="formData.model_rate"
          :min="0"
          :precision="4"
          :step="0.01"
          style="width: 200px"
        />
        <span class="form-tip">对应官方输入价格倍率</span>
      </el-form-item>
      
      <el-form-item label="补全倍率" prop="completion_rate">
        <el-input-number
          v-model="formData.completion_rate"
          :min="0"
          :precision="4"
          :step="0.01"
          style="width: 200px"
        />
        <span class="form-tip">对应官方输出价格倍率</span>
      </el-form-item>
      
      <el-form-item label="分组倍率" prop="group_rate">
        <el-input-number
          v-model="formData.group_rate"
          :min="0"
          :precision="4"
          :step="0.01"
          style="width: 200px"
        />
        <span class="form-tip">分组倍率</span>
      </el-form-item>
      
      <el-form-item label="充值转换率" prop="recharge_rate">
        <el-input-number
          v-model="formData.recharge_rate"
          :min="0"
          :precision="4"
          :step="0.01"
          style="width: 200px"
        />
        <span class="form-tip">充值转换率</span>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchModelsList } from '../api/config'

const props = defineProps({
  modelValue: Boolean,
  provider: Object
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const billingConfigText = ref('')

const formData = ref({
  name: '',
  api_base_url: '',
  api_key: '',
  default_model: '',
  priority: 0,
  is_enabled: true,
  // 计费配置
  model_rate: 1.0,
  completion_rate: 1.0,
  group_rate: 1.0,
  recharge_rate: 1.0
})

const models = ref([])
const loadingModels = ref(false)

// 动态验证规则：编辑时 API Key 可选，新建时必填
const rules = computed(() => {
  const baseRules = {
    name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
    api_base_url: [{ required: true, message: '请输入 API Base URL', trigger: 'blur' }],
    default_model: [{ required: true, message: '请输入默认模型', trigger: 'blur' }]
  }
  
  // 如果是编辑模式，API Key 可选；如果是新建，API Key 必填
  if (formData.value.id) {
    baseRules.api_key = []
  } else {
    baseRules.api_key = [{ required: true, message: '请输入 API Key', trigger: 'blur' }]
  }
  
  return baseRules
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.provider) {
    formData.value = {
      id: props.provider.id,
      name: props.provider.name,
      api_base_url: props.provider.api_base_url,
      api_key: '', // 不显示已保存的 key
      default_model: props.provider.default_model,
      priority: props.provider.priority,
      is_enabled: props.provider.is_enabled,
      // 计费配置
      model_rate: props.provider.model_rate ?? 1.0,
      completion_rate: props.provider.completion_rate ?? 1.0,
      group_rate: props.provider.group_rate ?? 1.0,
      recharge_rate: props.provider.recharge_rate ?? 1.0
    }
    billingConfigText.value = ''
  } else if (val) {
    formData.value = {
      name: '',
      api_base_url: '',
      api_key: '',
      default_model: '',
      priority: 0,
      is_enabled: true,
      // 计费配置
      model_rate: 1.0,
      completion_rate: 1.0,
      group_rate: 1.0,
      recharge_rate: 1.0
    }
    billingConfigText.value = ''
    models.value = []
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

function handleClose() {
  visible.value = false
  formRef.value?.resetFields()
}

// 解析计费配置文本
function parseBillingConfig(text) {
  const result = {}
  
  // 移除多余的空格和换行
  text = text.trim()
  
  // 匹配模型倍率
  const modelRateMatch = text.match(/(?:模型倍率|model[_-]?rate)[\s:=：]+([0-9\.]+)/i)
  if (modelRateMatch) {
    result.model_rate = parseFloat(modelRateMatch[1])
  }
  
  // 匹配补全倍率
  const completionRateMatch = text.match(/(?:补全倍率|completion[_-]?rate)[\s:=：]+([0-9\.]+)/i)
  if (completionRateMatch) {
    result.completion_rate = parseFloat(completionRateMatch[1])
  }
  
  // 匹配分组倍率
  const groupRateMatch = text.match(/(?:分组倍率|group[_-]?rate)[\s:=：]+([0-9\.]+)/i)
  if (groupRateMatch) {
    result.group_rate = parseFloat(groupRateMatch[1])
  }
  
  // 匹配充值转换率
  const rechargeRateMatch = text.match(/(?:充值转换率|recharge[_-]?rate)[\s:=：]+([0-9\.]+)/i)
  if (rechargeRateMatch) {
    result.recharge_rate = parseFloat(rechargeRateMatch[1])
  }
  
  return result
}

// 获取模型列表
async function fetchModels() {
  if (!formData.value.api_base_url || !formData.value.api_key) {
    ElMessage.warning('请先填写 API Base URL 和 API Key')
    return
  }
  
  loadingModels.value = true
  try {
    const modelList = await fetchModelsList({
      api_base_url: formData.value.api_base_url,
      api_key: formData.value.api_key
    })
    models.value = modelList.data || []
    if (models.value.length > 0) {
      ElMessage.success(`成功获取 ${models.value.length} 个模型`)
      // 如果当前没有选择模型，自动选择第一个
      if (!formData.value.default_model && models.value.length > 0) {
        formData.value.default_model = models.value[0].id
      }
    } else {
      ElMessage.warning('未获取到可用模型，请检查 API Base URL 和 API Key')
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取模型列表失败，请检查 API Base URL 和 API Key')
    models.value = []
  } finally {
    loadingModels.value = false
  }
}

// 处理计费配置粘贴
function handleBillingPaste(event) {
  // 延迟执行，让浏览器先填充默认值
  setTimeout(() => {
    try {
      // 从事件中获取粘贴的文本
      const text = event.clipboardData?.getData('text') || billingConfigText.value
      if (text && text.length > 5) {
        const parsed = parseBillingConfig(text)
        const parsedKeys = Object.keys(parsed)
        
        if (parsedKeys.length > 0) {
          // 自动填充识别到的字段
          parsedKeys.forEach(key => {
            formData.value[key] = parsed[key]
          })
          
          ElMessage.success(`已自动填充 ${parsedKeys.length} 个倍率字段`)
        } else {
          ElMessage.warning('未识别到有效的倍率配置，请检查格式')
        }
      }
    } catch (err) {
      ElMessage.error('解析配置失败')
    }
  }, 100)
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      submitting.value = true
      
      // 准备提交数据
      const submitData = { ...formData.value }
      
      // 如果是编辑模式且 API Key 为空，则不提交该字段
      if (submitData.id && !submitData.api_key) {
        delete submitData.api_key
      }
      
      emit('submit', submitData)
      setTimeout(() => {
        submitting.value = false
      }, 500)
    }
  })
}
</script>

