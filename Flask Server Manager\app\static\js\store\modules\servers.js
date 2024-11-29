import api from './index'

export const fetchServers = (params = {}) => {
  return api.get('/servers', { params })
}

export const getServerById = (id) => {
  return api.get(`/servers/${id}`)
}

export const createServer = (data) => {
  return api.post('/servers', data)
}

export const updateServer = (id, data) => {
  return api.put(`/servers/${id}`, data)
}

export const deleteServer = (id) => {
  return api.delete(`/servers/${id}`)
}

export const startServer = (id) => {
  return api.post(`/servers/${id}/start`)
}

export const stopServer = (id) => {
  return api.post(`/servers/${id}/stop`)
}

export const restartServer = (id) => {
  return api.post(`/servers/${id}/restart`)
}

export const getServerMetrics = (id, params = {}) => {
  return api.get(`/servers/${id}/metrics`, { params })
}

export const getServerLogs = (id, params = {}) => {
  return api.get(`/servers/${id}/logs`, { params })
}

export const createBackup = (id) => {
  return api.post(`/servers/${id}/backup`)
}

export const restoreBackup = (id, backupId) => {
  return api.post(`/servers/${id}/restore/${backupId}`)
}

export const getServerBackups = (id) => {
  return api.get(`/servers/${id}/backups`)
} 