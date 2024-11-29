from functools import wraps
from flask import request, abort, current_app
from flask_login import current_user
import jwt
from datetime import datetime
import ipaddress
import re
from urllib.parse import urlparse
import hashlib
import hmac
import base64

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.whitelist = self.load_ip_whitelist()
        self.blacklist = self.load_ip_blacklist()
        self.rate_limits = {}
        self.csrf_tokens = {}

    def __call__(self, environ, start_response):
        request = environ.get('werkzeug.request')
        
        # Check IP restrictions
        if not self.check_ip_access(request):
            return self.forbidden(start_response)

        # Rate limiting
        if not self.check_rate_limit(request):
            return self.too_many_requests(start_response)

        # Security headers
        def custom_start_response(status, headers, exc_info=None):
            security_headers = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'DENY'),
                ('X-XSS-Protection', '1; mode=block'),
                ('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'),
                ('Content-Security-Policy', self.get_csp_header()),
                ('Referrer-Policy', 'strict-origin-when-cross-origin'),
                ('Feature-Policy', self.get_feature_policy())
            ]
            headers.extend(security_headers)
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)

    def check_ip_access(self, request):
        client_ip = ipaddress.ip_address(request.remote_addr)
        
        # Check blacklist first
        if any(client_ip in network for network in self.blacklist):
            return False
            
        # If whitelist is empty, allow all non-blacklisted IPs
        if not self.whitelist:
            return True
            
        # Check whitelist
        return any(client_ip in network for network in self.whitelist)

    def check_rate_limit(self, request):
        key = f"{request.remote_addr}:{request.path}"
        now = datetime.utcnow()
        
        # Clean up old entries
        self.rate_limits = {k: v for k, v in self.rate_limits.items()
                          if (now - v['timestamp']).seconds < 60}
        
        if key in self.rate_limits:
            self.rate_limits[key]['count'] += 1
            if self.rate_limits[key]['count'] > current_app.config['API_RATE_LIMIT']:
                return False
        else:
            self.rate_limits[key] = {'count': 1, 'timestamp': now}
        
        return True

    def get_csp_header(self):
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self' wss:",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'"
        ])

    def get_feature_policy(self):
        return "; ".join([
            "geolocation 'none'",
            "midi 'none'",
            "notifications 'none'",
            "push 'none'",
            "sync-xhr 'self'",
            "microphone 'none'",
            "camera 'none'",
            "magnetometer 'none'",
            "gyroscope 'none'",
            "speaker 'none'",
            "vibrate 'none'",
            "fullscreen 'self'",
            "payment 'none'"
        ])

    def verify_csrf_token(self, token, session_id):
        if session_id not in self.csrf_tokens:
            return False
        return hmac.compare_digest(self.csrf_tokens[session_id], token)

    def generate_csrf_token(self, session_id):
        token = base64.b64encode(os.urandom(32)).decode('utf-8')
        self.csrf_tokens[session_id] = token
        return token

    def forbidden(self, start_response):
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return [b'Forbidden']

    def too_many_requests(self, start_response):
        start_response('429 Too Many Requests', [('Content-Type', 'text/plain')])
        return [b'Too Many Requests']