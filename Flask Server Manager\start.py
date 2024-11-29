#!/usr/bin/env python3

import os
import sys
import subprocess
import socket
import platform
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
from datetime import datetime
import psutil

class ServerManager:
    def __init__(self):
        self.os_type = platform.system().lower()
        
    def scan_port(self, ip, port):
        """Scan a single port on an IP address"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_network(self):
        """Scan local network for active servers"""
        try:
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Get network prefix
            ip_parts = local_ip.split('.')
            network_prefix = '.'.join(ip_parts[:-1])
            
            servers = []
            common_ports = [80, 443, 22, 21, 3389, 3306]  # Web, SSH, FTP, RDP, MySQL
            
            # Scan local network
            for i in range(1, 255):
                ip = f"{network_prefix}.{i}"
                try:
                    # Try to get hostname
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = "Unknown"

                    # Check common ports
                    for port in common_ports:
                        if self.scan_port(ip, port):
                            servers.append({
                                'ip': ip,
                                'hostname': hostname,
                                'status': 'up'
                            })
                except:
                    pass
            return servers
        except Exception as e:
            print(f"Scan error: {e}")
            return []

    def get_system_info(self):
        """Get basic system information"""
        return {
            'hostname': socket.gethostname(),
            'ip': socket.gethostbyname(socket.gethostname()),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'os_version': platform.version()
        }

    def create_app(self):
        app = Flask(__name__)
        CORS(app)

        @app.route('/')
        def home():
            return render_template('index.html')

        @app.route('/api/scan')
        def scan():
            return jsonify({
                'system': self.get_system_info(),
                'network': self.scan_network(),
                'timestamp': datetime.now().isoformat()
            })

        @app.route('/api/connect', methods=['POST'])
        def connect():
            try:
                data = request.json
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    data['host'],
                    username=data['username'],
                    password=data['password']
                )
                return jsonify({'status': 'connected'})
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        @app.route('/api/system/info')
        def get_system_info(self):
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            return jsonify({
                'hostname': hostname,
                'ip': ip,
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'platform': platform.system(),
                'python_version': platform.python_version()
            })

        @app.route('/api/scan')
        def scan_network(self):
            try:
                # Get local network information
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                ip_parts = local_ip.split('.')
                base_ip = '.'.join(ip_parts[:-1])
                
                servers = []
                common_ports = [80, 443, 22, 3306, 5432]
                
                # Scan local network (limited range for speed)
                for i in range(1, 10):
                    ip = f"{base_ip}.{i}"
                    for port in common_ports:
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(0.1)
                            result = sock.connect_ex((ip, port))
                            if result == 0:
                                servers.append({
                                    'ip': ip,
                                    'port': port,
                                    'status': 'active'
                                })
                            sock.close()
                        except:
                            continue
                            
                return jsonify({'servers': servers})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/server/<int:server_id>/<action>', methods=['POST'])
        def server_action(server_id, action):
            if action not in ['start', 'stop']:
                return jsonify({'error': 'Invalid action'}), 400
            
            # Implement server start/stop logic here
            return jsonify({'status': 'success'})

        return app

    def create_required_files(self):
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static', exist_ok=True)
        
        # Create index.html
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Scanner</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Network Scanner</h1>
        
        <div class="system-info">
            <h2>System Information</h2>
            <div id="systemInfo" class="info-card"></div>
        </div>

        <div class="network-scan">
            <h2>Network Scan</h2>
            <button onclick="startScan()" class="btn primary">Start Scan</button>
            <div id="scanResults" class="server-grid"></div>
        </div>

        <div id="connectionModal" class="modal">
            <div class="modal-content">
                <h2>Connect to Server</h2>
                <input type="text" id="username" placeholder="Username">
                <input type="password" id="password" placeholder="Password">
                <button onclick="connect()" class="btn primary">Connect</button>
                <button onclick="closeModal()" class="btn secondary">Cancel</button>
            </div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
"""
        with open('templates/index.html', 'w') as f:
            f.write(html_content)

        # Create style.css
        css_content = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    background: #1a1a1a;
    color: #ffffff;
}

.container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 2rem;
}

h1, h2 {
    margin-bottom: 1rem;
    color: #00ff00;
}

.info-card, .server-card {
    background: #2a2a2a;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    border: 1px solid #00ff00;
}

.server-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    margin-right: 0.5rem;
    cursor: pointer;
    font-weight: bold;
    background: #00ff00;
    color: #000000;
}

.btn:hover {
    opacity: 0.9;
}

.btn.secondary {
    background: #666666;
    color: #ffffff;
}

.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.8);
}

.modal-content {
    background: #2a2a2a;
    padding: 2rem;
    border-radius: 8px;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border: 1px solid #00ff00;
}

input {
    display: block;
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 1rem;
    background: #1a1a1a;
    border: 1px solid #00ff00;
    color: #ffffff;
    border-radius: 4px;
}

.status {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    margin-top: 0.5rem;
}

.status.up {
    background: #00ff00;
    color: #000000;
}

.status.down {
    background: #ff0000;
    color: #ffffff;
}
"""
        with open('static/style.css', 'w') as f:
            f.write(css_content)

        # Create script.js
        js_content = """
let selectedServer = null;

function startScan() {
    const button = document.querySelector('.btn.primary');
    button.disabled = true;
    button.textContent = 'Scanning...';

    fetch('/api/scan')
        .then(response => response.json())
        .then(data => {
            displaySystemInfo(data.system);
            displayScanResults(data.network);
            button.disabled = false;
            button.textContent = 'Start Scan';
        })
        .catch(error => {
            console.error('Scan error:', error);
            button.disabled = false;
            button.textContent = 'Start Scan';
        });
}

function displaySystemInfo(info) {
    const container = document.getElementById('systemInfo');
    container.innerHTML = `
        <p><strong>Hostname:</strong> ${info.hostname}</p>
        <p><strong>IP Address:</strong> ${info.ip}</p>
        <p><strong>Platform:</strong> ${info.platform}</p>
        <p><strong>OS Version:</strong> ${info.os_version}</p>
        <p><strong>Python Version:</strong> ${info.python_version}</p>
    `;
}

function displayScanResults(servers) {
    const container = document.getElementById('scanResults');
    container.innerHTML = servers.map(server => `
        <div class="server-card" onclick="showConnectionModal('${server.ip}')">
            <h3>${server.hostname}</h3>
            <p><strong>IP:</strong> ${server.ip}</p>
            <p><strong>Status:</strong> 
                <span class="status ${server.status}">${server.status}</span>
            </p>
        </div>
    `).join('');
}

function showConnectionModal(ip) {
    selectedServer = ip;
    document.getElementById('connectionModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('connectionModal').style.display = 'none';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    selectedServer = null;
}

function connect() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/api/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            host: selectedServer,
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            closeModal();
            alert('Connected successfully!');
        }
    })
    .catch(error => {
        alert('Connection failed: ' + error);
    });
}

// Initial scan
startScan();
"""
        with open('static/script.js', 'w') as f:
            f.write(js_content)

    def start(self):
        print("Starting Network Scanner...")
        self.create_required_files()
        app = self.create_app()
        print("Server running at http://localhost:3000")
        app.run(host='0.0.0.0', port=3000)

if __name__ == "__main__":
    manager = ServerManager()
    manager.start()