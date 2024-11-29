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

    <div class="server-grid">
      <ServerCard
        v-for="server in servers"
        :key="server.id"
        :server="server"
        @update="updateServer"
        @delete="deleteServer"
      />
    </div>

    <div class="monitoring-section">
      <div class="chart-container">
        <h3>System Resources</h3>
        <canvas ref="resourceChart"></canvas>
      </div>
      <div class="stats-container">
        <div class="stat-card">
          <h4>CPU Usage</h4>
          <div class="stat-value">{{ cpuUsage }}%</div>
        </div>
        <div class="stat-card">
          <h4>Memory Usage</h4>
          <div class="stat-value">{{ memoryUsage }}%</div>
        </div>
        <div class="stat-card">
          <h4>Disk Usage</h4>
          <div class="stat-value">{{ diskUsage }}%</div>
        </div>
      </div>
    </div>

    <!-- Add Server Modal -->
    <Modal v-if="showModal" @close="closeModal">
      <template v-slot:header>
        <h2>Add New Server</h2>
      </template>
      <template v-slot:body>
        <form @submit.prevent="addServer">
          <div class="form-group">
            <label for="serverName">Server Name</label>
            <input
              type="text"
              id="serverName"
              v-model="newServer.name"
              required
            >
          </div>
          <div class="form-group">
            <label for="serverHost">Host</label>
            <input
              type="text"
              id="serverHost"
              v-model="newServer.host"
              required
            >
          </div>
          <div class="form-group">
            <label for="serverPort">Port</label>
            <input
              type="number"
              id="serverPort"
              v-model="newServer.port"
              required
            >
          </div>
        </form>
      </template>
      <template v-slot:footer>
        <button @click="submitServer" class="btn-primary">Add Server</button>
        <button @click="closeModal" class="btn-secondary">Cancel</button>
      </template>
    </Modal>
  </div>
</template>

<script>
import Chart from 'chart.js';
import ServerCard from './ServerCard.vue';
import Modal from './Modal.vue';

export default {
  name: 'Dashboard',
  components: {
    ServerCard,
    Modal
  },
  data() {
    return {
      servers: [],
      loading: false,
      showModal: false,
      newServer: {
        name: '',
        host: '',
        port: null
      },
      cpuUsage: 0,
      memoryUsage: 0,
      diskUsage: 0,
      chart: null
    };
  },
  methods: {
    async refreshData() {
      this.loading = true;
      try {
        await this.fetchServers();
        await this.fetchSystemStats();
      } catch (error) {
        console.error('Error refreshing data:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchServers() {
      const response = await fetch('/api/server/list');
      const data = await response.json();
      this.servers = data;
    },
    async fetchSystemStats() {
      const response = await fetch('/api/monitoring/stats');
      const data = await response.json();
      this.updateStats(data);
    },
    updateStats(data) {
      this.cpuUsage = data.cpu_percent;
      this.memoryUsage = data.memory_percent;
      this.diskUsage = data.disk_usage;
      this.updateChart(data);
    },
    updateChart(data) {
      if (this.chart) {
        this.chart.data.datasets[0].data = [
          data.cpu_percent,
          data.memory_percent,
          data.disk_usage
        ];
        this.chart.update();
      }
    },
    initChart() {
      const ctx = this.$refs.resourceChart.getContext('2d');
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['CPU', 'Memory', 'Disk'],
          datasets: [{
            label: 'System Resources',
            data: [0, 0, 0],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      });
    }
  },
  mounted() {
    this.initChart();
    this.refreshData();
    // Set up real-time updates
    const socket = io();
    socket.on('stats_update', (data) => {
      this.updateStats(data);
    });
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy();
    }
  }
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.server-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.monitoring-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-container {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 8px;
}

.stats-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--accent-primary);
}
</style>