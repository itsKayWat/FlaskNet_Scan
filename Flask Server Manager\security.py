from functools import wraps
from flask import request, abort
from flask_login import current_user
import jwt
from datetime import datetime
import ipaddress
from app import app

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            abort(403)
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

def validate_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
            return False
        return True
    except:
        return False

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.whitelist = self.load_ip_whitelist()

    def load_ip_whitelist(self):
        # Load IP whitelist from configuration
        return [ipaddress.ip_network(ip) for ip in app.config.get('IP_WHITELIST', [])]

    def __call__(self, environ, start_response):
        request = environ.get('werkzeug.request')
        
        # Check IP whitelist
        if self.whitelist:
            client_ip = ipaddress.ip_address(request.remote_addr)
            if not any(client_ip in network for network in self.whitelist):
                return self.forbidden(start_response)

        # Check for required security headers
        headers = request.headers
        if not headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.forbidden(start_response)

        return self.app(environ, start_response)

    def forbidden(self, start_response):
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return [b'Forbidden']