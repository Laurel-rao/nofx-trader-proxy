import api from './request'

export function getLogs(params) {
  return api.get('/api/logs', { params })
}

export function getLogDetail(logId) {
  return api.get(`/api/logs/${logId}`)
}

export function deleteLog(logId) {
  return api.delete(`/api/logs/${logId}`)
}

