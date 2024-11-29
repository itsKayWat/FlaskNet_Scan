<template>
  <div class="server-card" :class="{ 'server-offline': !isOnline }">
    <div class="server-header">
      <div class="server-title">
        <h3>{{ server.name }}</h3>
        <status-badge :status="server.status" />
      </div>
      <div class="server-actions">
        <button 
          class="icon-button"
          @click="toggleDetails"
          :title="showDetails ? 'Hide Details' : 'Show Details'"
        >
          <i class="fas" :class="showDetails ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </button>
        <button 
          class="icon-button"
          @click="showMenu = !showMenu"
          :title="'More Options'"
        >
          <i class="fas fa-ellipsis-v"></i>
        </button>
        <div v-if="showMenu" class="dropdown-menu">
          <button @click="handleAction('start')" :disabled="isRunning">Start</button>
          <button @click="handleAction('stop')" :disabled="!isRunning">Stop</button>
          <button @click="handleAction('restart')">Restart</button>
          <div class="divider"></div>
          <button @click="handleEdit">Edit</button>
          <button @click="handleBackup">Backup</button>
          <button @click="handleDelete" class="danger">Delete</button>
        </div>
      </div>
    </div>

    <div class="server-metrics">
      <div class="metric">
        <div class="metric-label">CPU Usage</div>
        <div class="progress-bar">
          <div 
            class="progress" 
            :style="{ width: `${metrics.cpu}%` }"
            :class="getResourceClass(metrics.cpu)"
          ></div>
        </div>
        <div class="metric-value">{{ metrics.cpu }}%</div>
      </div>

      <div class="metric">
        <div class="metric-label">Memory Usage</div>
        <div class="progress-bar">
          <div 
            class="progress" 
            :style="{ width: `${metrics.memory}%` }"
            :class="getResourceClass(metrics.memory)"
          ></div>
        </div>
        <div class="metric-value">{{ metrics.memory }}%</div>
      </div>

      <div class="metric">
        <div class="metric-label">Disk Usage</div>
        <div class="progress-bar">
          <div 
            class="progress" 
            :style="{ width: `${metrics.disk}%` }"
            :class="getResourceClass(metrics.disk)"
          ></div>
        </div>
        <div class="metric-value">{{ metrics.disk }}%</div>
      </div>
    </div>

    <transition name="slide">
      <div v-if="showDetails" class="server-details">
        <div class="details-grid">
          <div class="detail-item">
            <div class="detail-label">Host</div>
            <div class="detail-value">{{ server.host }}:{{ server.port }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Uptime</div>
            <div class="detail-value">{{ formatUptime }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Docker Image</div>
            <div class="detail-value">{{ server.docker_image || 'N/A' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">Last Backup</div>
            <div class="detail-value">{{ formatLastBackup }}</div>
          </div>
        </div>

        <div class="mini-chart">
          <line-chart 
            :data="metrics.history"
            :options="chartOptions"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import StatusBadge from './StatusBadge.vue'
import LineChart from './charts/LineChart.vue'
import { formatDistanceToNow } from 'date-fns'

export default {
  name: 'ServerCard',
  components: { StatusBadge, LineChart },

  props: {
    server: {
      type: Object,
      required: true
    }
  },

  setup(props) {
    const showDetails = ref(false)
    const showMenu = ref(false)
    const metrics = ref({
      cpu: 0,
      memory: 0,
      disk: 0,
      history: []
    })

    const isOnline = computed(() => props.server.status !== 'stopped')
    const isRunning = computed(() => props.server.status === 'running')

    const formatUptime = computed(() => {
      if (!props.server.started_at) return 'Not running'
      return formatDistanceToNow(new Date(props.server.started_at), { addSuffix: true })
    })

    const formatLastBackup = computed(() => {
      if (!props.server.last_backup) return 'Never'
      return formatDistanceToNow(new Date(props.server.last_backup), { addSuffix: true })
    })

    const chartOptions = {
      height: 100,
      showPoints: false,
      showArea: true,
      showLabels: false,
      showGrid: false
    }

    const getResourceClass = (value) => {
      if (value >= 90) return 'critical'
      if (value >= 75) return 'warning'
      return 'normal'
    }

    return {
      showDetails,
      showMenu,
      metrics,
      isOnline,
      isRunning,
      formatUptime,
      formatLastBackup,
      chartOptions,
      getResourceClass
    }
  }
}
</script>

<style scoped>
.server-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.server-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.server-offline {
  opacity: 0.7;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.server-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.server-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metric {
  display: grid;
  grid-template-columns: 100px 1fr 50px;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  transition: width 0.3s ease;
}

.progress.normal {
  background: var(--success);
}

.progress.warning {
  background: var(--warning);
}

.progress.critical {
  background: var(--error);
}

.server-details {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--bg-tertiary);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 12px;
}

.detail-value {
  font-size: 14px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 