<template>
  <div class="config-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>供应商配置</span>
          <el-button type="primary" @click="handleAdd">添加供应商</el-button>
        </div>
      </template>
      
      <el-table 
        :data="providers" 
        v-loading="loading" 
        stripe 
        class="provider-table"
        table-layout="auto"
      >
        <el-table-column prop="name" label="供应商名称" width="150" />
        <el-table-column prop="api_base_url" label="API Base URL" show-overflow-tooltip min-width="200" />
        <el-table-column label="统计信息" width="280">
          <template #default="{ row }">
            <div v-if="row.statistics" class="statistics-info">
              <div class="stat-item">
                <span class="stat-label">访问次数:</span>
                <span class="stat-value">{{ row.statistics.total_requests }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">计费总额:</span>
                <span class="stat-value cost">${{ row.statistics.total_cost.toFixed(6) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">成功/失败:</span>
                <span class="stat-value">
                  <el-tag size="small" type="success" style="margin-right: 4px">
                    {{ row.statistics.success_count }}
                  </el-tag>
                  <el-tag size="small" type="danger">
                    {{ row.statistics.failure_count }}
                  </el-tag>
                </span>
              </div>
              <div class="stat-item">
                <span class="stat-label">成功率:</span>
                <span class="stat-value" :class="getSuccessRateClass(row.statistics.success_rate)">
                  {{ row.statistics.success_rate }}%
                </span>
              </div>
              <div class="stat-item" v-if="row.statistics.last_access_time">
                <span class="stat-label">最近访问:</span>
                <span class="stat-value time">{{ formatTime(row.statistics.last_access_time) }}</span>
              </div>
              <div class="stat-item" v-else-if="row.statistics.total_requests === 0">
                <span class="stat-value" style="color: var(--el-text-color-placeholder)">暂无访问记录</span>
              </div>
            </div>
            <span v-else style="color: var(--el-text-color-placeholder)">暂无数据</span>
          </template>
        </el-table-column>
        <el-table-column prop="default_model" label="默认模型" width="150" />
        <el-table-column prop="priority" label="优先级" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.priority }}</el-tag>
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
        <el-table-column label="操作" width="300" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleViewDetail(row)">查看</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
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
    
    <ProviderForm
      v-model="formVisible"
      :provider="currentProvider"
      @submit="handleSubmit"
    />
    
    <ProviderDetailDialog
      v-model="detailVisible"
      :provider="currentProvider"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProviders,
  createProvider,
  updateProvider,
  deleteProvider,
  toggleProvider
} from '../api/config'
import ProviderForm from '../components/ProviderForm.vue'
import ProviderDetailDialog from '../components/ProviderDetailDialog.vue'
import { formatTime } from '../utils/formatters'

const loading = ref(false)
const providers = ref([])
const formVisible = ref(false)
const detailVisible = ref(false)
const currentProvider = ref(null)

async function fetchProviders() {
  loading.value = true
  try {
    providers.value = await getProviders()
  } catch (error) {
    ElMessage.error('获取供应商列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  currentProvider.value = null
  formVisible.value = true
}

function handleViewDetail(row) {
  currentProvider.value = row
  detailVisible.value = true
}

function handleEdit(row) {
  currentProvider.value = row
  formVisible.value = true
}

async function handleSubmit(data) {
  try {
    if (data.id) {
      await updateProvider(data.id, data)
      ElMessage.success('更新成功')
    } else {
      await createProvider(data)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    fetchProviders()
  } catch (error) {
    ElMessage.error(data.id ? '更新失败' : '创建失败')
  }
}

async function handleToggle(row) {
  try {
    await toggleProvider(row.id)
    ElMessage.success('操作成功')
    fetchProviders()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除这个供应商配置吗？', '提示', {
      type: 'warning'
    })
    await deleteProvider(row.id)
    ElMessage.success('删除成功')
    fetchProviders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取成功率样式类
function getSuccessRateClass(rate) {
  if (rate >= 95) return 'success-rate-high'
  if (rate >= 80) return 'success-rate-medium'
  return 'success-rate-low'
}

onMounted(() => {
  fetchProviders()
})
</script>

<style scoped>
.config-view {
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

.provider-table {
  width: 100%;
}

:deep(.el-table) {
  width: 100% !important;
  border-radius: 8px;
}

:deep(.provider-table .el-table__body-wrapper) {
  width: 100%;
}

.statistics-info {
  padding: 8px 0;
  font-size: 12px;
  line-height: 1.8;
}

.stat-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-label {
  color: var(--el-text-color-secondary);
  margin-right: 8px;
  min-width: 60px;
  font-weight: 500;
}

.stat-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.stat-value.cost {
  color: var(--el-color-success);
  font-weight: 600;
}

.stat-value.time {
  color: var(--el-text-color-regular);
  font-size: 11px;
}

.success-rate-high {
  color: var(--el-color-success);
  font-weight: 600;
}

.success-rate-medium {
  color: var(--el-color-warning);
  font-weight: 600;
}

.success-rate-low {
  color: var(--el-color-danger);
  font-weight: 600;
}
</style>

