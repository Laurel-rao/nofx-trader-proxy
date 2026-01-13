<template>
  <el-card class="filter-card">
    <el-form :model="filterForm" inline>
      <el-form-item label="供应商">
        <el-select v-model="filterForm.provider" placeholder="全部" clearable style="width: 150px">
          <el-option
            v-for="provider in providers"
            :key="provider"
            :label="provider"
            :value="provider"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="模型">
        <el-input
          v-model="filterForm.model"
          placeholder="模型名称"
          clearable
          style="width: 150px"
        />
      </el-form-item>
      
      <el-form-item label="状态">
        <el-select v-model="filterForm.status_code" placeholder="全部" clearable style="width: 120px">
          <el-option label="成功" :value="200" />
          <el-option label="失败" :value="500" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="时间范围">
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 400px"
        />
      </el-form-item>
      
      <el-form-item label="搜索">
        <el-input
          v-model="filterForm.search"
          placeholder="搜索请求ID/供应商请求ID/用户ID/输入文本/返回文本"
          clearable
          style="width: 300px"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  providers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['search'])

const filterForm = ref({
  provider: '',
  model: '',
  status_code: null,
  search: ''
})

const dateRange = ref(null)

watch(dateRange, (val) => {
  if (val && val.length === 2) {
    filterForm.value.start_time = val[0]
    filterForm.value.end_time = val[1]
  } else {
    filterForm.value.start_time = null
    filterForm.value.end_time = null
  }
})

function handleSearch() {
  emit('search', { ...filterForm.value })
}

function handleReset() {
  filterForm.value = {
    provider: '',
    model: '',
    status_code: null,
    search: ''
  }
  dateRange.value = null
  emit('search', { ...filterForm.value })
}
</script>

<style scoped>
.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

:deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
  margin-bottom: 16px;
}
</style>

