import axios from 'axios'
import { ElMessage } from 'element-plus'

// 在生产环境中使用相对路径（通过 nginx 代理），开发环境使用完整 URL
const getBaseURL = () => {
  return ''
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 0, // 0 表示无超时限制
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api

