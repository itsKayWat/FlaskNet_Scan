from flask import current_app
from datetime import datetime, timedelta
import jwt
import bcrypt
from typing import Optional, Dict
import secrets
import redis
from dataclasses import dataclass

@dataclass
class AuthToken:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = 'Bearer'

class AuthenticationService:
    def __init__(self, app):
        self.app = app
        self.redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_AUTH_DB']
        )
        self.token_blacklist = set()

    def authenticate_user(self, username: str, password: str) -> Optional[AuthToken]:
        """Authenticate user and return tokens if valid."""
        user = self.app.db.users.find_one({'username': username})
        
        if not user or not self._verify_password(password, user['password_hash']):
            return None

        return self._generate_tokens(user['_id'])

    def refresh_token(self, refresh_token: str) -> Optional[AuthToken]:
        """Generate new access token using refresh token."""
        try:
            payload = jwt.decode(
                refresh_token, 
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            if self._is_token_blacklisted(refresh_token):
                return None

            user_id = payload['sub']
            return self._generate_tokens(user_id)
            
        except jwt.InvalidTokenError:
            return None

    def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding it to blacklist."""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            exp = datetime.fromtimestamp(payload['exp'])
            ttl = (exp - datetime.utcnow()).total_seconds()
            
            if ttl > 0:
                self.redis_client.setex(
                    f"blacklist:{token}",
                    int(ttl),
                    "1"
                )
            return True
        except jwt.InvalidTokenError:
            return False

    def _generate_tokens(self, user_id: str) -> AuthToken:
        """Generate access and refresh tokens."""
        access_token = self._create_access_token(user_id)
        refresh_token = self._create_refresh_token(user_id)
        
        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )

    def _create_access_token(self, user_id: str) -> str:
        """Create a new access token."""
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(minutes=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
            'type': 'access'
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    def _create_refresh_token(self, user_id: str) -> str:
        """Create a new refresh token."""
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id),
            'iat': now,
            'exp': now + timedelta(days=30),
            'type': 'refresh'
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return bool(self.redis_client.exists(f"blacklist:{token}"))

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)

    def verify_api_key(self, api_key: str) -> bool:
        """Verify an API key."""
        return bool(self.redis_client.exists(f"api_key:{api_key}")) 