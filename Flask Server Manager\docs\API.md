# Server Manager API Documentation

## Authentication

All API endpoints require authentication using either:
- Bearer token in Authorization header
- API key in X-API-Key header

### Obtaining Authentication Token
POST /api/auth/login
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "password"
}

Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600
}

## Server Management

### List Servers
GET /api/server
Authorization: Bearer <token>

### Create Server
POST /api/server
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "My Server",
    "host": "localhost",
    "port": 8080,
    "use_docker": true,
    "docker_image": "nginx:latest"
}

### Server Actions
POST /api/server/{server_id}/action/{action}
Authorization: Bearer <token>

Available actions: start, stop, restart