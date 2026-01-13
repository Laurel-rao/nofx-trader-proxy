import dayjs from 'dayjs'

/**
 * 格式化时间
 */
export function formatTime(time, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!time) return '-'
  return dayjs(time).format(format)
}

/**
 * 格式化相对时间
 */
export function formatRelativeTime(time) {
  if (!time) return '-'
  return dayjs(time).fromNow()
}

/**
 * 格式化时长（毫秒）
 */
export function formatDuration(ms) {
  if (ms < 1000) {
    return `${ms}ms`
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(2)}s`
  } else {
    const minutes = Math.floor(ms / 60000)
    const seconds = ((ms % 60000) / 1000).toFixed(2)
    return `${minutes}m ${seconds}s`
  }
}

/**
 * 格式化数字（添加千分位）
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString()
}

/**
 * 格式化 Token 数量
 */
export function formatTokens(tokens) {
  if (!tokens) return '0'
  if (tokens < 1000) {
    return tokens.toString()
  } else if (tokens < 1000000) {
    return `${(tokens / 1000).toFixed(2)}K`
  } else {
    return `${(tokens / 1000000).toFixed(2)}M`
  }
}

