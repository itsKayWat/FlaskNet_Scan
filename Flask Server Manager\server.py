from app import db
from datetime import datetime

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    host = db.Column(db.String(120), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='stopped')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_ssl_enabled = db.Column(db.Boolean, default=False)
    ssl_cert_path = db.Column(db.String(256))
    ssl_key_path = db.Column(db.String(256))
    auto_restart = db.Column(db.Boolean, default=False)
    debug_mode = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'status': self.status,
            'last_active': self.last_active.isoformat(),
            'is_ssl_enabled': self.is_ssl_enabled,
            'auto_restart': self.auto_restart,
            'debug_mode': self.debug_mode
        }