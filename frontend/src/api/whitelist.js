import api from './request'

export function getWhitelists(params) {
  return api.get('/api/whitelist', { params })
}

export function createWhitelist(data) {
  return api.post('/api/whitelist', data)
}

export function deleteWhitelist(whitelistId) {
  return api.delete(`/api/whitelist/${whitelistId}`)
}

export function toggleWhitelist(whitelistId) {
  return api.put(`/api/whitelist/${whitelistId}/toggle`)
}

