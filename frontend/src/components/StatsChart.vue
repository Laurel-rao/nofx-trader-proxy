<template>
  <div ref="chartRef" style="width: 100%; height: 300px"></div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: 'line' // line, bar, pie
  },
  metric: {
    type: String,
    default: 'requests' // requests, tokens, cost
  }
})

const chartRef = ref(null)
let chartInstance = null

// 检测是否为暗黑模式
const isDark = computed(() => {
  return document.documentElement.classList.contains('dark')
})

// 获取暗黑模式主题配置
function getThemeConfig() {
  if (isDark.value) {
    return {
      backgroundColor: 'transparent',
      textStyle: {
        color: '#e5eaf3'
      },
      grid: {
        borderColor: '#4a5568',
        backgroundColor: 'transparent'
      },
      xAxis: {
        axisLine: {
          lineStyle: {
            color: '#4a5568'
          }
        },
        axisLabel: {
          color: '#9ca3af'
        },
        splitLine: {
          lineStyle: {
            color: '#374151'
          }
        }
      },
      yAxis: {
        axisLine: {
          lineStyle: {
            color: '#4a5568'
          }
        },
        axisLabel: {
          color: '#9ca3af'
        },
        splitLine: {
          lineStyle: {
            color: '#374151'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(31, 41, 55, 0.95)',
        borderColor: '#4a5568',
        textStyle: {
          color: '#e5eaf3'
        }
      }
    }
  } else {
    return {
      backgroundColor: 'transparent',
      textStyle: {
        color: '#333'
      }
    }
  }
}

function initChart() {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value, isDark.value ? 'dark' : null)
  updateChart()
}

function updateChart() {
  if (!chartInstance) return
  
  const themeConfig = getThemeConfig()
  const primaryColor = isDark.value ? '#409eff' : '#409eff'
  
  const option = {
    ...themeConfig,
    tooltip: {
      ...themeConfig.tooltip,
      trigger: props.type === 'pie' ? 'item' : 'axis',
      axisPointer: props.type === 'pie' ? {} : {
        type: 'shadow'
      },
      formatter: props.type === 'pie' ? undefined : (params) => {
        if (Array.isArray(params)) {
          let result = params[0].axisValue + '<br/>'
          params.forEach(param => {
            const value = param.value
            let formattedValue = value
            if (props.metric === 'cost') {
              formattedValue = '$' + (value < 0.01 ? value.toFixed(6) : value.toFixed(2))
            } else if (props.metric === 'tokens') {
              formattedValue = value >= 1000 ? (value / 1000).toFixed(1) + 'K' : value
            } else {
              formattedValue = value
            }
            result += `${param.marker}${param.seriesName}: ${formattedValue}<br/>`
          })
          return result
        } else {
          const value = params.value
          let formattedValue = value
          if (props.metric === 'cost') {
            formattedValue = '$' + (value < 0.01 ? value.toFixed(6) : value.toFixed(2))
          } else if (props.metric === 'tokens') {
            formattedValue = value >= 1000 ? (value / 1000).toFixed(1) + 'K' : value
          }
          return `${params.name}<br/>${params.marker}${params.seriesName}: ${formattedValue}`
        }
      }
    },
    xAxis: props.type === 'pie' ? undefined : {
      ...themeConfig.xAxis,
      type: 'category',
      data: props.data.map(item => item.time || item.model || item.name),
      axisLine: {
        ...themeConfig.xAxis?.axisLine,
        lineStyle: {
          color: themeConfig.xAxis?.axisLine?.lineStyle?.color || '#e4e7ed'
        }
      },
      axisLabel: {
        ...themeConfig.xAxis?.axisLabel,
        color: themeConfig.xAxis?.axisLabel?.color || '#606266'
      }
    },
    yAxis: props.type === 'pie' ? undefined : {
      ...themeConfig.yAxis,
      type: 'value',
      axisLine: {
        ...themeConfig.yAxis?.axisLine,
        lineStyle: {
          color: themeConfig.yAxis?.axisLine?.lineStyle?.color || '#e4e7ed'
        }
      },
      axisLabel: {
        ...themeConfig.yAxis?.axisLabel,
        color: themeConfig.yAxis?.axisLabel?.color || '#606266',
        formatter: props.metric === 'cost' ? (value) => {
          if (value < 0.01) {
            return '$' + value.toFixed(4)
          } else if (value < 1) {
            return '$' + value.toFixed(2)
          } else {
            return '$' + value.toFixed(0)
          }
        } : props.metric === 'tokens' ? (value) => {
          return value >= 1000 ? (value / 1000).toFixed(1) + 'K' : value
        } : undefined
      },
      splitLine: {
        ...themeConfig.yAxis?.splitLine,
        lineStyle: {
          color: themeConfig.yAxis?.splitLine?.lineStyle?.color || '#ebeef5'
        }
      }
    },
    series: [
      {
        data: props.data.map(item => {
          if (props.metric === 'cost') {
            return item.cost || item.value || 0
          } else if (props.metric === 'tokens') {
            return item.tokens || item.value || 0
          } else {
            return item.requests || item.value || 0
          }
        }),
        name: props.metric === 'cost' ? '费用' : props.metric === 'tokens' ? 'Token' : '请求数',
        type: props.type === 'pie' ? 'pie' : props.type === 'bar' ? 'bar' : 'line',
        itemStyle: {
          color: primaryColor
        },
        lineStyle: props.type === 'line' ? {
          color: primaryColor
        } : undefined,
        areaStyle: props.type === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0,
              color: isDark.value ? 'rgba(64, 158, 255, 0.3)' : 'rgba(64, 158, 255, 0.2)'
            }, {
              offset: 1,
              color: isDark.value ? 'rgba(64, 158, 255, 0.05)' : 'rgba(64, 158, 255, 0.05)'
            }]
          }
        } : undefined
      }
    ]
  }
  
  if (props.type === 'pie') {
    option.series[0].data = props.data.map(item => ({
      value: props.metric === 'cost' ? (item.cost || item.value || 0) : 
             props.metric === 'tokens' ? (item.tokens || item.value || 0) :
             (item.requests || item.value || 0),
      name: item.time || item.model || item.name || item.provider
    }))
    option.series[0].itemStyle = undefined
    option.series[0].color = [
      '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
      '#36a3eb', '#ff9f40', '#ff6384', '#4bc0c0', '#9966ff'
    ]
    option.tooltip.formatter = (params) => {
      const value = params.value
      let formattedValue = value
      if (props.metric === 'cost') {
        formattedValue = '$' + (value < 0.01 ? value.toFixed(6) : value.toFixed(2))
      } else if (props.metric === 'tokens') {
        formattedValue = value >= 1000 ? (value / 1000).toFixed(1) + 'K' : value
      }
      return `${params.name}<br/>${params.marker}${formattedValue}`
    }
  }
  
  chartInstance.setOption(option, true)
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// 监听暗黑模式变化
watch(isDark, () => {
  if (chartInstance) {
    chartInstance.dispose()
    initChart()
  }
})

onMounted(() => {
  initChart()
  const handleResize = () => {
    chartInstance?.resize()
  }
  window.addEventListener('resize', handleResize)
  
  // 监听暗黑模式切换
  const observer = new MutationObserver(() => {
    if (chartInstance) {
      chartInstance.dispose()
      initChart()
    }
  })
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  })
  
  // 保存 observer 以便清理
  chartRef.value._observer = observer
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  if (chartRef.value?._observer) {
    chartRef.value._observer.disconnect()
  }
  const handleResize = () => {
    chartInstance?.resize()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

