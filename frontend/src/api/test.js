import api from './request'

/**
 * 发送测试请求到代理端点
 * @param {Object} data - 请求数据
 * @param {string} providerName - 供应商名称（可选），用于指定使用哪个供应商
 */
export function testChatCompletions(data, providerName = null) {
  const config = {
    headers: {},
    timeout: 0  // 无超时限制
  }
  
  // 如果指定了供应商名称，通过 Authorization header 传递
  if (providerName) {
    config.headers['Authorization'] = `Bearer ${providerName}`
  }
  
  return api.post('/v1/chat/completions', data, config)
}

