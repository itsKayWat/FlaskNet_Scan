from flask import current_app, url_for, request, session
from authlib.integrations.flask_client import OAuth
from functools import wraps
import jwt
from datetime import datetime, timedelta

class OAuthManager:
    def __init__(self, app=None):
        self.oauth = OAuth()
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.oauth.init_app(app)
        
        # Configure OAuth providers
        self.oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

        self.oauth.register(
            name='github',
            client_id=app.config['GITHUB_CLIENT_ID'],
            client_secret=app.config['GITHUB_CLIENT_SECRET'],
            access_token_url='https://github.com/login/oauth/access_token',
            access_token_params=None,
            authorize_url='https://github.com/login/oauth/authorize',
            authorize_params=None,
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'}
        )

    def require_oauth(self, provider):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = session.get(f'{provider}_token')
                if not token:
                    return {'error': 'Authentication required'}, 401
                return f(*args, **kwargs)
            return decorated
        return decorator

    async def validate_token(self, token, provider):
        if provider == 'google':
            try:
                resp = await self.oauth.google.get('userinfo')
                user_info = resp.json()
                return user_info
            except Exception as e:
                current_app.logger.error(f"Token validation error: {str(e)}")
                return None
        return None

    def generate_tokens(self, user_info, provider):
        now = datetime.utcnow()
        
        # Access token
        access_token_payload = {
            'sub': user_info['email'],
            'iat': now,
            'exp': now + timedelta(minutes=60),
            'provider': provider,
            'scope': 'access'
        }
        
        # Refresh token
        refresh_token_payload = {
            'sub': user_info['email'],
            'iat': now,
            'exp': now + timedelta(days=30),
            'provider': provider,
            'scope': 'refresh'
        }

        access_token = jwt.encode(
            access_token_payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        refresh_token = jwt.encode(
            refresh_token_payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        } 