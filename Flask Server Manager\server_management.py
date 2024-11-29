from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.server import Server
from app.models.logs import ServerLog, ActivityLog
from app import db
import psutil
import os
import subprocess
import signal

server_bp = Blueprint('server', __name__, url_prefix='/api/server')

@server_bp.route('/create', methods=['POST'])
@login_required
def create_server():
    data = request.get_json()
    
    server = Server(
        name=data['name'],
        host=data['host'],
        port=data['port'],
        owner_id=current_user.id
    )
    
    try:
        db.session.add(server)
        db.session.commit()
        
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Created server {server.name}",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(server.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@server_bp.route('/<int:server_id>/<action>', methods=['POST'])
@login_required
def manage_server(server_id, action):
    server = Server.query.get_or_404(server_id)
    
    if action == 'start':
        try:
            # Implementation of server start logic
            server.status = 'running'
            db.session.commit()
            return jsonify({'message': 'Server started successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    elif action == 'stop':
        try:
            # Implementation of server stop logic
            server.status = 'stopped'
            db.session.commit()
            return jsonify({'message': 'Server stopped successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    elif action == 'restart':
        try:
            # Implementation of server restart logic
            server.status = 'restarting'
            db.session.commit()
            return jsonify({'message': 'Server restarting'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid action'}), 400

@server_bp.route('/<int:server_id>/status')
@login_required
def server_status(server_id):
    server = Server.query.get_or_404(server_id)
    
    status_info = {
        'server': server.to_dict(),
        'system': {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict()
        }
    }
    
    return jsonify(status_info)