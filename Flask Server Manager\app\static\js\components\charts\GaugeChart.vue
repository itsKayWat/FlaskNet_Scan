<template>
  <div class="gauge-chart" ref="chartContainer">
    <canvas ref="canvas"></canvas>
    <div class="gauge-value" :style="valueStyle">
      {{ formattedValue }}
    </div>
    <div class="gauge-label" v-if="label">
      {{ label }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'

export default {
  name: 'GaugeChart',
  
  props: {
    value: {
      type: Number,
      required: true,
      validator: value => value >= 0 && value <= 100
    },
    label: {
      type: String,
      default: ''
    },
    thresholds: {
      type: Object,
      default: () => ({
        warning: 70,
        critical: 90
      })
    }
  },

  setup(props) {
    const canvas = ref(null)
    const ctx = ref(null)
    const chartContainer = ref(null)

    const formattedValue = computed(() => `${Math.round(props.value)}%`)

    const valueStyle = computed(() => {
      let color = '#4CAF50' // Normal
      if (props.value >= props.thresholds.critical) {
        color = '#F44336' // Critical
      } else if (props.value >= props.thresholds.warning) {
        color = '#FFC107' // Warning
      }
      return { color }
    })

    const drawGauge = () => {
      if (!ctx.value) return

      const width = canvas.value.width
      const height = canvas.value.height
      const centerX = width / 2
      const centerY = height * 0.75
      const radius = Math.min(width, height) * 0.4

      // Clear canvas
      ctx.value.clearRect(0, 0, width, height)

      // Draw background arc
      ctx.value.beginPath()
      ctx.value.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI)
      ctx.value.lineWidth = 20
      ctx.value.strokeStyle = '#E0E0E0'
      ctx.value.stroke()

      // Draw value arc
      const valueAngle = Math.PI + (props.value / 100) * Math.PI
      const gradient = ctx.value.createLinearGradient(0, 0, width, 0)
      gradient.addColorStop(0, '#4CAF50')
      gradient.addColorStop(0.7, '#FFC107')
      gradient.addColorStop(1, '#F44336')

      ctx.value.beginPath()
      ctx.value.arc(centerX, centerY, radius, Math.PI, valueAngle)
      ctx.value.lineWidth = 20
      ctx.value.strokeStyle = gradient
      ctx.value.stroke()
    }

    onMounted(() => {
      ctx.value = canvas.value.getContext('2d')
      
      const resizeObserver = new ResizeObserver(() => {
        if (canvas.value && chartContainer.value) {
          canvas.value.width = chartContainer.value.clientWidth
          canvas.value.height = chartContainer.value.clientHeight
          drawGauge()
        }
      })
      
      if (chartContainer.value) {
        resizeObserver.observe(chartContainer.value)
      }
      
      drawGauge()
    })

    return {
      canvas,
      chartContainer,
      formattedValue,
      valueStyle
    }
  }
}
</script>

<style scoped>
.gauge-chart {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 150px;
}

.gauge-value {
  position: absolute;
  top: 60%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: bold;
  transition: color 0.3s ease;
}

.gauge-label {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  color: var(--text-secondary);
}
</style> 