class WebSocketService {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            reconnectAttempts: 5,
            reconnectDelay: 3000,
            heartbeatInterval: 30000,
            ...options
        };
        
        this.ws = null;
        this.reconnectCount = 0;
        this.heartbeatTimer = null;
        this.listeners = new Map();
        this.isConnecting = false;
    }

    connect() {
        if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
            return;
        }

        this.isConnecting = true;
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnecting = false;
            this.reconnectCount = 0;
            this.startHeartbeat();
            this.emit('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'heartbeat') {
                    this.handleHeartbeat();
                } else {
                    this.emit('message', data);
                }
            } catch (error) {
                console.error('WebSocket message parse error:', error);
            }
        };

        this.ws.onclose = () => {
            this.isConnecting = false;
            this.stopHeartbeat();
            this.emit('disconnected');
            this.handleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.stopHeartbeat();
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
    }

    off(event, callback) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).delete(callback);
        }
    }

    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => callback(data));
        }
    }

    send(data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    private handleReconnect() {
        if (this.reconnectCount < this.options.reconnectAttempts) {
            this.reconnectCount++;
            console.log(`Attempting to reconnect (${this.reconnectCount}/${this.options.reconnectAttempts})`);
            setTimeout(() => this.connect(), this.options.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.emit('maxReconnectAttempts');
        }
    }

    private startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            this.send({ type: 'heartbeat' });
        }, this.options.heartbeatInterval);
    }

    private stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    private handleHeartbeat() {
        this.emit('heartbeat');
    }
}

export default WebSocketService;
