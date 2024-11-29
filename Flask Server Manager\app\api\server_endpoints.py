from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import Server, ServerLog
from app.security import require_api_key, admin_required
from app.monitoring import monitoring_service
from datetime import datetime
import docker
from paramiko import SSHClient, AutoAddPolicy
from ftplib import FTP
import os

api = Blueprint('api', __name__)

class ServerManager:
    def __init__(self):
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        
    def connect_ssh(self, host, username, password=None, key_filename=None):
        try:
            self.ssh_client.connect(
                host,
                username=username,
                password=password,
                key_filename=key_filename
            )
            return True
        except Exception as e:
            return str(e)
            
    def execute_command(self, command):
        if not self.ssh_client.get_transport().is_active():
            return {'error': 'Not connected'}
            
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return {
            'output': stdout.read().decode(),
            'error': stderr.read().decode()
        }
        
    def transfer_file(self, local_path, remote_path):
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            return str(e)

server_manager = ServerManager()

@api.route('/server', methods=['GET'])
@login_required
def get_servers():
    """Get all servers for the current user."""
    servers = Server.query.filter_by(owner_id=current_user.id).all()
    return jsonify([server.to_dict() for server in servers])

@api.route('/server/<int:server_id>', methods=['GET'])
@login_required
def get_server(server_id):
    """Get detailed server information."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Get additional metrics
    metrics = monitoring_service.get_server_metrics(server_id)
    response = server.to_dict()
    response.update(metrics)
    
    return jsonify(response)

@api.route('/server', methods=['POST'])
@login_required
def create_server():
    """Create a new server."""
    data = request.get_json()
    
    try:
        server = Server(
            name=data['name'],
            host=data['host'],
            port=data['port'],
            owner_id=current_user.id
        )
        db.session.add(server)
        db.session.commit()
        
        # Initialize Docker container if needed
        if data.get('use_docker', False):
            docker_client = docker.from_env()
            container = docker_client.containers.run(
                data['docker_image'],
                name=f"server_{server.id}",
                detach=True,
                ports={f"{data['port']}/tcp": data['port']},
                environment=data.get('environment', {})
            )
            server.container_id = container.id
            db.session.commit()
        
        return jsonify(server.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating server: {str(e)}")
        return jsonify({'error': str(e)}), 400

@api.route('/server/<int:server_id>', methods=['PUT'])
@login_required
def update_server(server_id):
    """Update server configuration."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(server, key):
                setattr(server, key, value)
        
        db.session.commit()
        return jsonify(server.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/server/<int:server_id>/action/<action>', methods=['POST'])
@login_required
def server_action(server_id, action):
    """Perform action on server (start/stop/restart)."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        if server.container_id:
            docker_client = docker.from_env()
            container = docker_client.containers.get(server.container_id)
            
            if action == 'start':
                container.start()
                server.status = 'running'
            elif action == 'stop':
                container.stop()
                server.status = 'stopped'
            elif action == 'restart':
                container.restart()
                server.status = 'running'
            else:
                return jsonify({'error': 'Invalid action'}), 400
                
            db.session.commit()
            return jsonify({'message': f'Server {action} successful'})
            
    except Exception as e:
        current_app.logger.error(f"Error performing server action: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/server/<int:server_id>/logs', methods=['GET'])
@login_required
def get_server_logs(server_id):
    """Get server logs."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logs = ServerLog.query.filter_by(server_id=server_id)\
            .order_by(ServerLog.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
            
        return jsonify([log.to_dict() for log in logs])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/server/<int:server_id>/metrics', methods=['GET'])
@login_required
def get_server_metrics(server_id):
    """Get server metrics."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        metrics = monitoring_service.get_server_metrics(server_id)
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/server/<int:server_id>/backup', methods=['POST'])
@login_required
def backup_server(server_id):
    """Create server backup."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        backup_service = current_app.backup_service
        backup_id = backup_service.create_backup(server)
        return jsonify({
            'message': 'Backup created successfully',
            'backup_id': backup_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/server/<int:server_id>/restore/<backup_id>', methods=['POST'])
@login_required
def restore_server(server_id, backup_id):
    """Restore server from backup."""
    server = Server.query.get_or_404(server_id)
    if server.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        backup_service = current_app.backup_service
        backup_service.restore_backup(server, backup_id)
        return jsonify({'message': 'Server restored successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/server/connect', methods=['POST'])
def connect_server():
    data = request.json
    result = server_manager.connect_ssh(
        data['host'],
        data['username'],
        data.get('password'),
        data.get('key_filename')
    )
    return jsonify({'success': result is True, 'error': result if isinstance(result, str) else None})

@api.route('/server/execute', methods=['POST'])
def execute_command():
    data = request.json
    result = server_manager.execute_command(data['command'])
    return jsonify(result)

@api.route('/server/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    remote_path = request.form.get('remote_path', '')
    
    # Save file temporarily
    temp_path = os.path.join('/tmp', file.filename)
    file.save(temp_path)
    
    result = server_manager.transfer_file(temp_path, remote_path)
    os.remove(temp_path)
    
    return jsonify({'success': result is True, 'error': result if isinstance(result, str) else None}) 