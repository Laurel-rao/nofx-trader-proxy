import api from './request'

export function getSummary(params) {
  return api.get('/api/stats/summary', { params })
}

export function getTimeline(params) {
  return api.get('/api/stats/timeline', { params })
}

export function getTokenStats(params) {
  return api.get('/api/stats/tokens', { params })
}

export function getModelStats(params) {
  return api.get('/api/stats/models', { params })
}

export function getProviderCostStats(params) {
  return api.get('/api/stats/costs', { params })
}

