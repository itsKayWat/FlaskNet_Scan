<template>
  <div class="server-settings">
    <div class="settings-header">
      <h2>Server Settings - {{ server.name }}</h2>
      <div class="settings-actions">
        <button @click="saveSettings" :disabled="!hasChanges || saving">
          <i class="fas fa-save"></i>
          Save Changes
        </button>
      </div>
    </div>

    <div class="settings-content">
      <div class="settings-section">
        <h3>General Settings</h3>
        <form @submit.prevent="saveSettings">
          <div class="form-group">
            <label for="serverName">Server Name</label>
            <input
              type="text"
              id="serverName"
              v-model="settings.name"
              @input="checkChanges"
            >
          </div>

          <div class="form-group">
            <label for="serverHost">Host</label>
            <input
              type="text"
              id="serverHost"
              v-model="settings.host"
              @input="checkChanges"
            >
          </div>

          <div class="form-group">
            <label for="serverPort">Port</label>
            <input
              type="number"
              id="serverPort"
              v-model="settings.port"
              @input="checkChanges"
            >
          </div>

          <div class="form-group">
            <label>
              <input
                type="checkbox"
                v-model="settings.autoRestart"
                @change="checkChanges"
              >
              Auto Restart on Failure
            </label>
          </div>

          <div class="form-group">
            <label>
              <input
                type="checkbox"
                v-model="settings.debugMode"
                @change="checkChanges"
              >
              Debug Mode
            </label>
          </div>
        </form>
      </div>

      <div class="settings-section">
        <h3>Resource Limits</h3>
        <div class="form-group">
          <label for="maxMemory">Maximum Memory (MB)</label>
          <input
            type="number"
            id="maxMemory"
            v-model="settings.maxMemory"
            @input="checkChanges"
          >
        </div>

        <div class="form-group">
          <label for="maxCpu">CPU Limit (%)</label>
          <input
            type="number"
            id="maxCpu"
            v-model="settings.maxCpu"
            @input="checkChanges"
          >
        </div>
      </div>

      <div class="settings-section">
        <h3>Backup Settings</h3>
        <div class="form-group">
          <label for="backupInterval">Backup Interval (hours)</label>
          <input
            type="number"
            id="backupInterval"
            v-model="settings.backupInterval"
            @input="checkChanges"
          >
        </div>

        <div class="form-group">
          <label for="backupRetention">Backup Retention (days)</label>
          <input
            type="number"
            id="backupRetention"
            v-model="settings.backupRetention"
            @input="checkChanges"
          >
        </div>
      </div>

      <div class="settings-section">
        <h3>SSL Configuration</h3>
        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="settings.sslEnabled"
              @change="checkChanges"
            >
            Enable SSL
          </label>
        </div>

        <template v-if="settings.sslEnabled">
          <div class="form-group">
            <label for="sslCert">SSL Certificate Path</label>
            <input
              type="text"
              id="sslCert"
              v-model="settings.sslCertPath"
              @input="checkChanges"
            >
          </div>

          <div class="form-group">
            <label for="sslKey">SSL Key Path</label>
            <input
              type="text"
              id="sslKey"
              v-model="settings.sslKeyPath"
              @input="checkChanges"
            >
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ServerSettings',
  props: {
    server: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      settings: {
        name: '',
        host: '',
        port: null,
        autoRestart: false,
        debugMode: false,
        maxMemory: 1024,
        maxCpu: 100,
        backupInterval: 24,
        backupRetention: 7,
        sslEnabled: false,
        sslCertPath: '',
        sslKeyPath: ''
      },
      originalSettings: null,
      saving: false
    };
  },
  computed: {
    hasChanges() {
      return JSON.stringify(this.settings) !== JSON.stringify(this.originalSettings);
    }
  },
  methods: {
    initializeSettings() {
      this.settings = { ...this.server };
      this.originalSettings = { ...this.settings };
    },
    checkChanges() {
      this.$emit('changes', this.hasChanges);
    },
    async saveSettings() {
      this.saving = true;
      try {
        const response = await fetch(`/api/server/${this.server.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.settings)
        });

        if (!response.ok) {
          throw new Error('Failed to save settings');
        }

        this.originalSettings = { ...this.settings };
        this.$emit('saved');
        this.$emit('changes', false);
      } catch (error) {
        console.error('Error saving settings:', error);
        this.$emit('error', error.message);
      } finally {
        this.saving = false;
      }
    }
  },
  created() {
    this.initializeSettings();
  },
  watch: {
    server: {
      handler() {
        this.initializeSettings();
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.server-settings {
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.settings-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.settings-section {
  background: var(--bg-tertiary);
  padding: 20px;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--text-secondary);
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--bg-tertiary);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

button {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  background: var(--accent-primary);
  color: var(--bg-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button i {
  font-size: 14px;
}
</style> 