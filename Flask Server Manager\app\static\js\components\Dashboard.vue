<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Server Dashboard</h1>
      <div class="dashboard-controls">
        <button @click="refreshData" :disabled="loading">
          <i class="fas fa-sync" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
        <button @click="showAddServerModal">
          <i class="fas fa-plus"></i>
          Add Server
        </button>
      </div>
    </div>

    <div class="dashboard-stats">
      <div class="stat-card">
        <div class="stat-title">Total Servers</div>
        <div class="stat-value">{{ stats.totalServers }}</div>
        <div class="stat-chart">
          <trend-chart
            :data="stats.serverTrend"
            :grid="true"
            :labels="{ xLabels: 7, yLabels: 5 }"
          />
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Active Servers</div>
        <div class="stat-value">{{ stats.activeServers }}</div>
        <div class="stat-percentage" :class="getStatusClass(stats.activePercentage)">
          {{ stats.activePercentage }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-title">System Load</div>
        <div class="stat-value">{{ stats.systemLoad.toFixed(2) }}</div>
        <div class="stat-chart">
          <line-chart :data="stats.loadTrend" />
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Memory Usage</div>
        <div class="stat-value">{{ stats.memoryUsage }}%</div>
        <div class="stat-chart">
          <progress-ring
            :progress="stats.memoryUsage"
            :radius="40"
            :stroke="4"
            :color="getMemoryColor(stats.memoryUsage)"
          />
        </div>
      </div>
    </div>

    <div class="server-grid">
      <server-card
        v-for="server in servers"
        :key="server.id"
        :server="server"
        @update="updateServer"
        @delete="deleteServer"
        @action="handleServerAction"
      />
    </div>

    <modal v-if="showModal" @close="showModal = false">
      <template #header>
        <h3>Add New Server</h3>
      </template>
      <template #body>
        <server-form @submit="createServer" @cancel="showModal = false" />
      </template>
    </modal>

    <websocket-connection
      :url="wsUrl"
      @message="handleWebSocketMessage"
      @error="handleWebSocketError"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import ServerCard from './ServerCard.vue'
import ServerForm from './ServerForm.vue'
import Modal from './Modal.vue'
import WebsocketConnection from './WebsocketConnection.vue'
import { TrendChart, LineChart, ProgressRing } from './charts'
import { fetchServers, createNewServer, updateServerDetails, deleteServerById } from '../api'

export default {
  name: 'Dashboard',
  components: {
    ServerCard,
    ServerForm,
    Modal,
    WebsocketConnection,
    TrendChart,
    LineChart,
    ProgressRing
  },

  setup() {
    const store = useStore()
    const servers = ref([])
    const stats = ref({
      totalServers: 0,
      activeServers: 0,
      activePercentage: 0,
      systemLoad: 0,
      memoryUsage: 0,
      serverTrend: [],
      loadTrend: []
    })
    const loading = ref(false)
    const showModal = ref(false)
    const wsUrl = `ws://${window.location.host}/ws/monitoring`

    const refreshData = async () => {
      loading.value = true
      try {
        const response = await fetchServers()
        servers.value = response.data
        updateStats()
      } catch (error) {
        store.dispatch('notifications/add', {
          type: 'error',
          message: 'Failed to fetch servers'
        })
      } finally {
        loading.value = false
      }
    }

    const updateStats = () => {
      stats.value.totalServers = servers.value.length
      stats.value.activeServers = servers.value.filter(s => s.status === 'running').length
      stats.value.activePercentage = Math.round(
        (stats.value.activeServers / stats.value.totalServers) * 100
      )
    }

    const createServer = async (serverData) => {
      try {
        const response = await createNewServer(serverData)
        servers.value.push(response.data)
        updateStats()
        showModal.value = false
        store.dispatch('notifications/add', {
          type: 'success',
          message: 'Server created successfully'
        })
      } catch (error) {
        store.dispatch('notifications/add', {
          type: 'error',
          message: 'Failed to create server'
        })
      }
    }

    const handleWebSocketMessage = (message) => {
      const data = JSON.parse(message)
      if (data.type === 'stats_update') {
        stats.value = { ...stats.value, ...data.payload }
      } else if (data.type === 'server_update') {
        const index = servers.value.findIndex(s => s.id === data.payload.id)
        if (index !== -1) {
          servers.value[index] = { ...servers.value[index], ...data.payload }
        }
      }
    }

    onMounted(() => {
      refreshData()
    })

    return {
      servers,
      stats,
      loading,
      showModal,
      wsUrl,
      refreshData,
      createServer,
      handleWebSocketMessage
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-controls {
  display: flex;
  gap: 10px;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-title {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 15px;
}

.server-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.stat-percentage {
  font-size: 16px;
  font-weight: 500;
}

.stat-percentage.success {
  color: var(--success);
}

.stat-percentage.warning {
  color: var(--warning);
}

.stat-percentage.error {
  color: var(--error);
}

.stat-chart {
  height: 100px;
  margin-top: 15px;
}
</style> 