import axios from 'axios'
import { ElMessage } from 'element-plus'

// 在生产环境中使用相对路径（通过 nginx 代理），开发环境使用完整 URL
const getBaseURL = () => {
  // 优先使用环境变量（如果明确设置了非空值）
  const envURL = import.meta.env.VITE_API_BASE_URL
  if (envURL && envURL.trim() !== '') {
    return envURL
  }
  
  // 检查是否为生产环境
  // 在构建时，Vite 会自动设置 import.meta.env.PROD 和 import.meta.env.MODE
  const isProduction = 
    import.meta.env.PROD === true || 
    import.meta.env.MODE === 'production' ||
    (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.port !== '5173')
  
  // 生产环境或部署环境使用相对路径（通过 nginx 代理）
  if (isProduction) {
    return ''
  }
  
  // 开发环境使用 localhost
  return 'http://localhost:8000'
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

