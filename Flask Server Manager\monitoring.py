from flask import Blueprint, jsonify, current_app
from flask_login import login_required
from app.models.logs import ServerLog, ActivityLog
from app import db, socketio
import psutil
import os
from datetime import datetime, timedelta

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

@monitoring_bp.route('/system')
@login_required
def system_stats():
    stats = {
        'cpu': {
            'percent': psutil.cpu_percent(interval=1),
            'cores': psutil.cpu_count(),
            'frequency': psutil.cpu_freq()._asdict()
        },
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
        'network': {
            nic: psutil.net_io_counters(pernic=True)[nic]._asdict()
            for nic in psutil.net_if_stats().keys()
        }
    }
    return jsonify(stats)

@monitoring_bp.route('/logs')
@login_required
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    logs = ServerLog.query.order_by(ServerLog.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    })

@monitoring_bp.route('/activity')
@login_required
def get_activity():
    days = request.args.get('days', 7, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    
    activities = ActivityLog.query\
        .filter(ActivityLog.timestamp >= since)\
        .order_by(ActivityLog.timestamp.desc())\
        .all()
        
    return jsonify([{
        'id': activity.id,
        'user_id': activity.user_id,
        'action': activity.action,
        'details': activity.details,
        'timestamp': activity.timestamp.isoformat(),
        'ip_address': activity.ip_address
    } for activity in activities])

# WebSocket events for real-time monitoring
@socketio.on('connect')
@login_required
def handle_connect():
    emit('connected', {'data': 'Connected to monitoring socket'})

@socketio.on('subscribe_stats')
def handle_stats_subscription():
    def send_stats():
        while True:
            stats = {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'timestamp': datetime.utcnow().isoformat()
            }
            emit('stats_update', stats)
            socketio.sleep(5)
            
    socketio.start_background_task(send_stats)