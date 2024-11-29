<template>
  <div class="line-chart" ref="chartContainer">
    <canvas ref="canvas"></canvas>
    <div v-if="loading" class="chart-loader">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'LineChart',
  
  props: {
    data: {
      type: Array,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },

  setup(props) {
    const canvas = ref(null);
    const chart = ref(null);
    const chartContainer = ref(null);

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 750,
        easing: 'easeInOutQuart'
      },
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(200, 200, 200, 0.1)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1
        }
      }
    };

    const createChart = () => {
      if (!canvas.value) return;

      const ctx = canvas.value.getContext('2d');
      const mergedOptions = { ...defaultOptions, ...props.options };

      chart.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: props.data.map(d => d.label),
          datasets: [{
            data: props.data.map(d => d.value),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
          }]
        },
        options: mergedOptions
      });
    };

    const updateChart = () => {
      if (!chart.value) return;

      chart.value.data.labels = props.data.map(d => d.label);
      chart.value.data.datasets[0].data = props.data.map(d => d.value);
      chart.value.update('none');
    };

    onMounted(() => {
      createChart();
      
      const resizeObserver = new ResizeObserver(() => {
        if (chart.value) {
          chart.value.resize();
        }
      });
      
      if (chartContainer.value) {
        resizeObserver.observe(chartContainer.value);
      }
    });

    onUnmounted(() => {
      if (chart.value) {
        chart.value.destroy();
      }
    });

    watch(() => props.data, updateChart, { deep: true });

    return {
      canvas,
      chartContainer
    };
  }
}
</script>

<style scoped>
.line-chart {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-loader {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 