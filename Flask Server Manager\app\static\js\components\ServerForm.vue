<template>
  <form @submit.prevent="handleSubmit" class="server-form">
    <div class="form-group">
      <label for="serverName">Server Name</label>
      <input
        id="serverName"
        v-model="formData.name"
        type="text"
        required
        :class="{ 'error': errors.name }"
        @input="validateField('name')"
      >
      <span class="error-message" v-if="errors.name">{{ errors.name }}</span>
    </div>

    <div class="form-group">
      <label for="serverHost">Host</label>
      <input
        id="serverHost"
        v-model="formData.host"
        type="text"
        required
        :class="{ 'error': errors.host }"
        @input="validateField('host')"
      >
      <span class="error-message" v-if="errors.host">{{ errors.host }}</span>
    </div>

    <div class="form-group">
      <label for="serverPort">Port</label>
      <input
        id="serverPort"
        v-model.number="formData.port"
        type="number"
        required
        min="1"
        max="65535"
        :class="{ 'error': errors.port }"
        @input="validateField('port')"
      >
      <span class="error-message" v-if="errors.port">{{ errors.port }}</span>
    </div>

    <div class="form-group">
      <label class="checkbox-label">
        <input
          type="checkbox"
          v-model="formData.useDocker"
          @change="handleDockerToggle"
        >
        Use Docker
      </label>
    </div>

    <div v-if="formData.useDocker" class="docker-settings">
      <div class="form-group">
        <label for="dockerImage">Docker Image</label>
        <div class="input-with-suggestions">
          <input
            id="dockerImage"
            v-model="formData.dockerImage"
            type="text"
            required
            @input="searchDockerImages"
            :class="{ 'error': errors.dockerImage }"
          >
          <div v-if="showImageSuggestions" class="suggestions">
            <div
              v-for="image in dockerImageSuggestions"
              :key="image.name"
              class="suggestion-item"
              @click="selectDockerImage(image)"
            >
              <span class="image-name">{{ image.name }}</span>
              <span class="image-downloads">{{ formatDownloads(image.downloads) }}</span>
            </div>
          </div>
        </div>
        <span class="error-message" v-if="errors.dockerImage">{{ errors.dockerImage }}</span>
      </div>

      <div class="form-group">
        <label for="dockerEnv">Environment Variables</label>
        <div
          v-for="(env, index) in formData.environment"
          :key="index"
          class="env-variable"
        >
          <input
            type="text"
            v-model="env.key"
            placeholder="Key"
            @input="validateEnvVariable(index)"
          >
          <input
            type="text"
            v-model="env.value"
            placeholder="Value"
          >
          <button
            type="button"
            class="remove-env"
            @click="removeEnvVariable(index)"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <button
          type="button"
          class="add-env"
          @click="addEnvVariable"
        >
          Add Environment Variable
        </button>
      </div>
    </div>

    <div class="form-actions">
      <button type="button" class="secondary" @click="$emit('cancel')">
        Cancel
      </button>
      <button type="submit" :disabled="!isValid || isSubmitting">
        {{ isSubmitting ? 'Creating...' : 'Create Server' }}
      </button>
    </div>
  </form>
</template>

<script>
import { ref, computed } from 'vue'
import { searchDockerHub } from '../api/docker'
import { debounce } from 'lodash-es'

export default {
  name: 'ServerForm',
  
  emits: ['submit', 'cancel'],

  setup(props, { emit }) {
    const formData = ref({
      name: '',
      host: '',
      port: 8080,
      useDocker: false,
      dockerImage: '',
      environment: []
    })

    const errors = ref({})
    const isSubmitting = ref(false)
    const dockerImageSuggestions = ref([])
    const showImageSuggestions = ref(false)

    const validateField = (field) => {
      errors.value[field] = ''
      
      switch (field) {
        case 'name':
          if (formData.value.name.length < 3) {
            errors.value.name = 'Name must be at least 3 characters'
          }
          break
        case 'host':
          if (!/^[a-zA-Z0-9.-]+$/.test(formData.value.host)) {
            errors.value.host = 'Invalid host format'
          }
          break
        case 'port':
          if (formData.value.port < 1 || formData.value.port > 65535) {
            errors.value.port = 'Port must be between 1 and 65535'
          }
          break
      }
    }

    const isValid = computed(() => {
      return Object.keys(errors.value).length === 0 &&
        formData.value.name &&
        formData.value.host &&
        formData.value.port &&
        (!formData.value.useDocker || formData.value.dockerImage)
    })

    const searchDockerImages = debounce(async () => {
      if (formData.value.dockerImage.length < 2) {
        dockerImageSuggestions.value = []
        showImageSuggestions.value = false
        return
      }

      try {
        const results = await searchDockerHub(formData.value.dockerImage)
        dockerImageSuggestions.value = results
        showImageSuggestions.value = true
      } catch (error) {
        console.error('Failed to search Docker images:', error)
      }
    }, 300)

    const handleSubmit = async () => {
      if (!isValid.value || isSubmitting.value) return

      isSubmitting.value = true
      try {
        emit('submit', { ...formData.value })
      } catch (error) {
        console.error('Form submission error:', error)
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      formData,
      errors,
      isSubmitting,
      isValid,
      dockerImageSuggestions,
      showImageSuggestions,
      validateField,
      searchDockerImages,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.server-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

input[type="text"],
input[type="number"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-input);
  color: var(--text-primary);
}

input.error {
  border-color: var(--error);
}

.error-message {
  color: var(--error);
  font-size: 12px;
  margin-top: 4px;
}

.docker-settings {
  margin-top: 20px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.env-variable {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  margin-bottom: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

button {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

button[type="submit"] {
  background: var(--primary);
  color: white;
}

button.secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 