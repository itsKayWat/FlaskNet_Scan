<template>
  <div class="logs-viewer">
    <div class="logs-header">
      <h2>System Logs</h2>
      <div class="logs-controls">
        <select v-model="selectedLevel" @change="filterLogs">
          <option value="ALL">All Levels</option>
          <option value="ERROR">Errors</option>
          <option value="WARNING">Warnings</option>
          <option value="INFO">Info</option>
          <option value="DEBUG">Debug</option>
        </select>
        <select v-model="selectedServer" @change="filterLogs">
          <option value="ALL">All Servers</option>
          <option v-for="server in servers" :key="server.id" :value="server.id">
            {{ server.name }}
          </option>
        </select>
        <input 
          type="text" 
          v-model="searchQuery" 
          @input="filterLogs" 
          placeholder="Search logs..."
        >
        <button @click="refreshLogs" :disabled="loading">
          <i class="fas fa-sync" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
        <button @click="exportLogs">
          <i class="fas fa-download"></i>
          Export
        </button>
      </div>
    </div>

    <div class="logs-container" ref="logsContainer">
      <virtual-scroller
        class="scroller"
        :items="filteredLogs"
        :item-height="40"
        v-slot="{ item }"
      >
        <div class="log-entry" :class="getLogClass(item)">
          <div class="log-timestamp">{{ formatTimestamp(item.timestamp) }}</div>
          <div class="log-level">{{ item.level }}</div>
          <div class="log-server">{{ getServerName(item.server_id) }}</div>
          <div class="log-message">{{ item.message }}</div>
        </div>
      </virtual-scroller>
    </div>

    <div class="logs-footer">
      <div class="logs-stats">
        Showing {{ filteredLogs.length }} of {{ logs.length }} logs
      </div>
      <div class="auto-scroll">
        <label>
          <input type="checkbox" v-model="autoScroll">
          Auto-scroll
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import { VirtualScroller } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';

export default {
  name: 'LogsViewer',
  components: {
    VirtualScroller
  },
  data() {
    return {
      logs: [],
      servers: [],
      selectedLevel: 'ALL',
      selectedServer: 'ALL',
      searchQuery: '',
      loading: false,
      autoScroll: true,
      socket: null
    };
  },
  computed: {
    filteredLogs() {
      return this.logs.filter(log => {
        const levelMatch = this.selectedLevel === 'ALL' || log.level === this.selectedLevel;
        const serverMatch = this.selectedServer === 'ALL' || log.server_id === this.selectedServer;
        const searchMatch = !this.searchQuery || 
          log.message.toLowerCase().includes(this.searchQuery.toLowerCase());
        return levelMatch && serverMatch && searchMatch;
      });
    }
  },
  methods: {
    async fetchLogs() {
      this.loading = true;
      try {
        const response = await fetch('/api/monitoring/logs');
        const data = await response.json();
        this.logs = data.logs;
        if (this.autoScroll) {
          this.scrollToBottom();
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchServers() {
      try {
        const response = await fetch('/api/server/list');
        const data = await response.json();
        this.servers = data;
      } catch (error) {
        console.error('Error fetching servers:', error);
      }
    },
    getLogClass(log) {
      return {
        'log-error': log.level === 'ERROR',
        'log-warning': log.level === 'WARNING',
        'log-info': log.level === 'INFO',
        'log-debug': log.level === 'DEBUG'
      };
    },
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    getServerName(serverId) {
      const server = this.servers.find(s => s.id === serverId);
      return server ? server.name : 'Unknown';
    },
    scrollToBottom() {
      if (this.$refs.logsContainer) {
        this.$refs.logsContainer.scrollTop = this.$refs.logsContainer.scrollHeight;
      }
    },
    async exportLogs() {
      try {
        const response = await fetch('/api/monitoring/logs/export');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs-${new Date().toISOString()}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error) {
        console.error('Error exporting logs:', error);
      }
    },
    initializeWebSocket() {
      this.socket = io('/logs');
      this.socket.on('log_update', (log) => {
        this.logs.push(log);
        if (this.autoScroll) {
          this.scrollToBottom();
        }
      });
    }
  },
  mounted() {
    this.fetchServers();
    this.fetchLogs();
    this.initializeWebSocket();
  },
  beforeDestroy() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
};
</script>

<style scoped>
.logs-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow: hidden;
}

.logs-header {
  padding: 15px;
  border-bottom: 1px solid var(--bg-tertiary);
}

.logs-controls {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.logs-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.scroller {
  height: 100%;
}

.log-entry {
  display: grid;
  grid-template-columns: 180px 80px 120px 1fr;
  gap: 10px;
  padding: 8px 15px;
  border-bottom: 1px solid var(--bg-tertiary);
  font-family: monospace;
}

.log-error {
  background: rgba(var(--error-rgb), 0.1);
}

.log-warning {
  background: rgba(var(--warning-rgb), 0.1);
}

.log-timestamp {
  color: var(--text-secondary);
}

.log-level {
  font-weight: bold;
}

.log-message {
  white-space: pre-wrap;
  word-break: break-word;
}

.logs-footer {
  padding: 10px 15px;
  border-top: 1px solid var(--bg-tertiary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 