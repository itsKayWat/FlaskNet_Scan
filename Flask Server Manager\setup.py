from flask import Flask, render_template, jsonify, request, send_file
import psutil
import os
import logging
import json
import datetime
import subprocess
from werkzeug.utils import secure_filename
import ssl
import secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Logging setup
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Server state
servers = {}
active_sessions = {}
server_status = "stopped"

# Basic auth decorator (you should implement proper authentication)
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Implement proper authentication here
        return f(*args, **kwargs)
    return decorated

# Server Management Routes
@app.route('/api/server/<action>')
def manage_server(action):
    global server_status
    try:
        if action == "start":
            server_status = "running"
            logging.info("Server started")
            return jsonify({"status": "Server started successfully"})
        elif action == "stop":
            server_status = "stopped"
            logging.info("Server stopped")
            return jsonify({"status": "Server stopped successfully"})
        elif action == "restart":
            server_status = "restarting"
            logging.info("Server restarting")
            return jsonify({"status": "Server restarting"})
        elif action == "status":
            return jsonify({
                "status": server_status,
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent
            })
    except Exception as e:
        logging.error(f"Server management error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# File Management Routes
@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"status": "File uploaded successfully"})

@app.route('/api/files/list')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify({"files": files})

# Monitoring Routes
@app.route('/api/logs')
def get_logs():
    try:
        with open('server.log', 'r') as log_file:
            logs = log_file.readlines()[-100:]  # Last 100 lines
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/stats')
def system_stats():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage('/')._asdict()
    })

# Main route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Start the server
    app.run(debug=True, ssl_context='adhoc')
