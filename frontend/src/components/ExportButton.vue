<template>
  <el-dropdown @command="handleExport">
    <el-button type="primary">
      导出数据<el-icon class="el-icon--right"><arrow-down /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="csv">导出为 CSV</el-dropdown-item>
        <el-dropdown-item command="json">导出为 JSON</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  filename: {
    type: String,
    default: 'export'
  }
})

function exportToCSV(data) {
  if (data.length === 0) return
  
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      headers.map(header => {
        const value = row[header]
        if (value === null || value === undefined) return ''
        if (typeof value === 'object') return JSON.stringify(value)
        return String(value).replace(/"/g, '""')
      }).map(v => `"${v}"`).join(',')
    )
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${props.filename}_${new Date().getTime()}.csv`
  link.click()
}

function exportToJSON(data) {
  const jsonContent = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${props.filename}_${new Date().getTime()}.json`
  link.click()
}

function handleExport(command) {
  if (props.data.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  if (command === 'csv') {
    exportToCSV(props.data)
  } else if (command === 'json') {
    exportToJSON(props.data)
  }
}
</script>

