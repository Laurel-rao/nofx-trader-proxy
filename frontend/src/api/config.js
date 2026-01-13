import api from './request'

export function getProviders(enabledOnly = false, includeStats = true) {
  return api.get('/api/config/providers', { 
    params: { 
      enabled_only: enabledOnly,
      include_stats: includeStats
    } 
  })
}

export function getProvider(providerId) {
  return api.get(`/api/config/providers/${providerId}`)
}

export function createProvider(data) {
  return api.post('/api/config/providers', data)
}

export function updateProvider(providerId, data) {
  return api.put(`/api/config/providers/${providerId}`, data)
}

export function deleteProvider(providerId) {
  return api.delete(`/api/config/providers/${providerId}`)
}

export function toggleProvider(providerId) {
  return api.put(`/api/config/providers/${providerId}/toggle`)
}

export function fetchModelsList(params) {
  return api.post('/api/config/models', params)
}

export function getDecisionTestPrompts() {
  return api.get('/api/config/prompts/decision-test')
}

