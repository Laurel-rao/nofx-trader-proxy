<template>
  <div class="whitelist-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>IP 白名单管理</span>
          <el-button type="primary" @click="handleAdd">添加白名单</el-button>
        </div>
      </template>
      
      <!-- 筛选 -->
      <el-form :model="filterForm" inline style="margin-bottom: 20px">
        <el-form-item label="类型">
          <el-select v-model="filterForm.is_global" placeholder="全部" clearable style="width: 150px">
            <el-option label="全局白名单" :value="true" />
            <el-option label="供应商白名单" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="filterForm.provider_id" placeholder="全部" clearable style="width: 200px">
            <el-option
              v-for="provider in providers"
              :key="provider.id"
              :label="provider.name"
              :value="provider.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchWhitelists">搜索</el-button>
          <el-button @click="handleResetFilter">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 表格 -->
      <el-table :data="whitelists" v-loading="loading" stripe>
        <el-table-column prop="ip_address" label="IP地址" width="200">
          <template #default="{ row }">
            <span style="font-family: monospace;">{{ row.ip_address }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="is_global" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_global ? 'success' : 'info'">
              {{ row.is_global ? '全局' : '供应商' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="provider_name" label="关联供应商" width="150">
          <template #default="{ row }">
            <span v-if="row.provider_name">{{ row.provider_name }}</span>
            <span v-else style="color: var(--el-text-color-placeholder)">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'info'">
              {{ row.is_enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.is_enabled ? 'warning' : 'success'"
              @click="handleToggle(row)"
            >
              {{ row.is_enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="formVisible"
      :title="currentWhitelist ? '编辑白名单' : '添加白名单'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="IP地址" prop="ip_address">
          <el-input
            v-model="formData.ip_address"
            placeholder="例如: 192.168.1.1 或 192.168.1.0/24"
            style="width: 100%"
          />
          <div style="margin-top: 5px; color: #909399; font-size: 12px">
            支持单个IP地址或CIDR格式（如 192.168.1.0/24）
          </div>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="可选，用于描述此白名单的用途"
          />
        </el-form-item>
        
        <el-form-item label="类型" prop="is_global">
          <el-radio-group v-model="formData.is_global" @change="handleTypeChange">
            <el-radio :label="true">全局白名单</el-radio>
            <el-radio :label="false">供应商白名单</el-radio>
          </el-radio-group>
          <div style="margin-top: 5px; color: #909399; font-size: 12px">
            全局白名单可访问所有供应商，供应商白名单只能访问指定供应商
          </div>
        </el-form-item>
        
        <el-form-item
          v-if="!formData.is_global"
          label="关联供应商"
          prop="provider_id"
        >
          <el-select
            v-model="formData.provider_id"
            placeholder="请选择供应商"
            style="width: 100%"
          >
            <el-option
              v-for="provider in providers"
              :key="provider.id"
              :label="provider.name"
              :value="provider.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="启用状态" prop="is_enabled">
          <el-switch v-model="formData.is_enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWhitelists, createWhitelist, deleteWhitelist, toggleWhitelist } from '../api/whitelist'
import { getProviders } from '../api/config'
import { formatTime } from '../utils/formatters'

const loading = ref(false)
const whitelists = ref([])
const providers = ref([])
const formVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentWhitelist = ref(null)

const filterForm = ref({
  is_global: null,
  provider_id: null
})

const formData = ref({
  ip_address: '',
  description: '',
  is_global: true,
  provider_id: null,
  is_enabled: true
})

const rules = {
  ip_address: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        try {
          if ('/' in value) {
            // CIDR格式
            const parts = value.split('/')
            if (parts.length !== 2) {
              callback(new Error('CIDR格式错误，应为 IP/掩码'))
              return
            }
            const mask = parseInt(parts[1])
            if (isNaN(mask) || mask < 0 || mask > 32) {
              callback(new Error('CIDR掩码必须在0-32之间'))
              return
            }
          }
          // 验证IP地址部分
          const ipPart = value.split('/')[0]
          const ip = ipPart.split('.')
          if (ip.length !== 4) {
            callback(new Error('IP地址格式错误'))
            return
          }
          for (const part of ip) {
            const num = parseInt(part)
            if (isNaN(num) || num < 0 || num > 255) {
              callback(new Error('IP地址格式错误'))
              return
            }
          }
          callback()
        } catch (error) {
          callback(new Error('IP地址格式错误'))
        }
      },
      trigger: 'blur'
    }
  ],
  provider_id: [
    {
      validator: (rule, value, callback) => {
        if (!formData.value.is_global && !value) {
          callback(new Error('供应商白名单必须选择供应商'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

async function fetchWhitelists() {
  loading.value = true
  try {
    const params = {}
    if (filterForm.value.is_global !== null) {
      params.is_global = filterForm.value.is_global
    }
    if (filterForm.value.provider_id) {
      params.provider_id = filterForm.value.provider_id
    }
    whitelists.value = await getWhitelists(params)
  } catch (error) {
    ElMessage.error('获取白名单列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchProviders() {
  try {
    providers.value = await getProviders(false, false)
  } catch (error) {
    console.error('获取供应商列表失败:', error)
  }
}

function handleAdd() {
  currentWhitelist.value = null
  formData.value = {
    ip_address: '',
    description: '',
    is_global: true,
    provider_id: null,
    is_enabled: true
  }
  formVisible.value = true
}

function handleTypeChange() {
  if (formData.value.is_global) {
    formData.value.provider_id = null
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (currentWhitelist.value) {
          // 编辑（当前版本不支持编辑，只能删除重建）
          ElMessage.warning('编辑功能暂不支持，请删除后重新添加')
        } else {
          await createWhitelist(formData.value)
          ElMessage.success('添加成功')
          formVisible.value = false
          fetchWhitelists()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

async function handleToggle(row) {
  try {
    await toggleWhitelist(row.id)
    ElMessage.success('操作成功')
    fetchWhitelists()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除这个白名单规则吗？', '提示', {
      type: 'warning'
    })
    await deleteWhitelist(row.id)
    ElMessage.success('删除成功')
    fetchWhitelists()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleResetFilter() {
  filterForm.value = {
    is_global: null,
    provider_id: null
  }
  fetchWhitelists()
}

onMounted(() => {
  fetchWhitelists()
  fetchProviders()
})
</script>

<style scoped>
.whitelist-view {
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
</style>

