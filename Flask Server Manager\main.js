// Socket.IO connection
const socket = io();

// Theme toggling
const themeToggle = document.querySelector('.btn-theme-toggle');
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
    themeToggle.textContent = document.body.classList.contains('light-theme') ? '🌙' : '☀️';
});

// Real-time monitoring
class MonitoringDashboard {
    constructor() {
        this.charts = {};
        this.initializeCharts();
        this.connectWebSocket();
    }

    initializeCharts() {
        // CPU Usage Chart
        const cpuCtx = document.getElementById('cpuChart')?.getContext('2d');
        if (cpuCtx) {
            this.charts.cpu = new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU Usage %',
                        data: [],
                        borderColor: '#bb86fc',
                        tension: 0.4
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

        // Memory Usage Chart
        const memoryCtx = document.getElementById('memoryChart')?.getContext('2d');
        if (memoryCtx) {
            this.charts.memory = new Chart(memoryCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Memory Usage %',
                        data: [],
                        borderColor: '#03dac6',
                        tension: 0.4
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
    }

    connectWebSocket() {
        socket.on('connect', () => {
            console.log('Connected to WebSocket');
            socket.emit('subscribe_stats');
        });

        socket.on('stats_update', (data) => {
            this.updateCharts(data);
        });
    }

    updateCharts(data) {
        const timestamp = new Date(data.timestamp).toLocaleTimeString();

        // Update CPU chart
        if (this.charts.cpu) {
            this.charts.cpu.data.labels.push(timestamp);
            this.charts.cpu.data.datasets[0].data.push(data.cpu);

            if (this.charts.cpu.data.labels.length > 20) {
                this.charts.cpu.data.labels.shift();
                this.charts.cpu.data.datasets[0].data.shift();
            }

            this.charts.cpu.update();
        }

        // Update Memory chart
        if (this.charts.memory) {
            this.charts.memory.data.labels.push(timestamp);
            this.charts.memory.data.datasets[0].data.push(data.memory);

            if (this.charts.memory.data.labels.length > 20) {
                this.charts.memory.data.labels.shift();
                this.charts.memory.data.datasets[0].data.shift();
            }

            this.charts.memory.update();
        }
    }
}

// Initialize monitoring if on monitoring page
if (document.getElementById('monitoring-dashboard')) {
    new MonitoringDashboard();
}

// Server management functions
const serverManager = {
    async startServer(serverId) {
        try {
            const response = await fetch(`/api/server/${serverId}/start`, {
                method: 'POST'
            });
            const data = await response.json();
            this.showNotification(data.message, 'success');
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    },

    async stopServer(serverId) {
        try {
            const response = await fetch(`/api/server/${serverId}/stop`, {
                method: 'POST'
            });
            const data = await response.json();
            this.showNotification(data.message, 'success');
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    },

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        
        document.querySelector('.content-area').prepend(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
};

// File upload handling
const fileUploader = {
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/file/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }
};

// Initialize file upload listeners
const fileInput = document.querySelector('#file-upload');
if (fileInput) {
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        try {
            const result = await fileUploader.uploadFile(file);
            serverManager.showNotification('File uploaded successfully', 'success');
        } catch (error) {
            serverManager.showNotification('Upload failed', 'error');
        }
    });
}