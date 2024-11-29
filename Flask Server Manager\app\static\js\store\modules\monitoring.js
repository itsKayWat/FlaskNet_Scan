import { WebSocketService } from '@/services/WebSocketService'

export default {
  namespaced: true,

  state: {
    metrics: {},
    alerts: [],
    wsConnected: false,
    lastUpdate: null,
    historicalData: {},
    thresholds: {
      cpu: { warning: 70, critical: 90 },
      memory: { warning: 80, critical: 95 },
      disk: { warning: 85, critical: 95 }
    }
  },

  mutations: {
    UPDATE_METRICS(state, { serverId, metrics }) {
      state.metrics = {
        ...state.metrics,
        [serverId]: {
          ...state.metrics[serverId],
          ...metrics,
          timestamp: Date.now()
        }
      }
    },
    
    ADD_HISTORICAL_DATA(state, { serverId, metric, value }) {
      if (!state.historicalData[serverId]) {
        state.historicalData[serverId] = {}
      }
      if (!state.historicalData[serverId][metric]) {
        state.historicalData[serverId][metric] = []
      }
      
      state.historicalData[serverId][metric].push({
        timestamp: Date.now(),
        value
      })
      
      // Keep last 100 data points
      if (state.historicalData[serverId][metric].length > 100) {
        state.historicalData[serverId][metric].shift()
      }
    },
    
    ADD_ALERT(state, alert) {
      state.alerts.unshift({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...alert
      })
      
      // Keep last 100 alerts
      if (state.alerts.length > 100) {
        state.alerts.pop()
      }
    },
    
    SET_WS_CONNECTED(state, status) {
      state.wsConnected = status
    },
    
    UPDATE_THRESHOLDS(state, thresholds) {
      state.thresholds = {
        ...state.thresholds,
        ...thresholds
      }
    }
  },

  actions: {
    initializeWebSocket({ commit, dispatch }) {
      const ws = new WebSocketService('/api/ws/monitoring')
      
      ws.on('connected', () => {
        commit('SET_WS_CONNECTED', true)
      })
      
      ws.on('disconnected', () => {
        commit('SET_WS_CONNECTED', false)
      })
      
      ws.on('message', (data) => {
        dispatch('handleWebSocketMessage', data)
      })
      
      return ws
    },
    
    handleWebSocketMessage({ commit, state }, message) {
      const { type, serverId, data } = message
      
      switch (type) {
        case 'metrics':
          commit('UPDATE_METRICS', { serverId, metrics: data })
          
          // Add to historical data
          Object.entries(data).forEach(([metric, value]) => {
            commit('ADD_HISTORICAL_DATA', { serverId, metric, value })
          })
          
          // Check thresholds and generate alerts
          Object.entries(data).forEach(([metric, value]) => {
            if (state.thresholds[metric]) {
              if (value >= state.thresholds[metric].critical) {
                commit('ADD_ALERT', {
                  type: 'critical',
                  metric,
                  serverId,
                  message: `${metric} usage is critical (${value}%)`
                })
              } else if (value >= state.thresholds[metric].warning) {
                commit('ADD_ALERT', {
                  type: 'warning',
                  metric,
                  serverId,
                  message: `${metric} usage is high (${value}%)`
                })
              }
            }
          })
          break
          
        case 'alert':
          commit('ADD_ALERT', data)
          break
      }
    },
    
    updateThresholds({ commit }, thresholds) {
      commit('UPDATE_THRESHOLDS', thresholds)
    }
  },

  getters: {
    getServerMetrics: (state) => (serverId) => {
      return state.metrics[serverId] || {}
    },
    
    getHistoricalData: (state) => (serverId, metric) => {
      return state.historicalData[serverId]?.[metric] || []
    },
    
    getRecentAlerts: (state) => (limit = 10) => {
      return state.alerts.slice(0, limit)
    },
    
    isServerHealthy: (state) => (serverId) => {
      const metrics = state.metrics[serverId]
      if (!metrics) return true
      
      return !Object.entries(metrics).some(([metric, value]) => {
        const threshold = state.thresholds[metric]
        return threshold && value >= threshold.warning
      })
    }
  }
} 