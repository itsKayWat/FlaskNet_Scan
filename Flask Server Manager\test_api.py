import pytest
from app.models import User, Server

def test_user_registration(client):
    response = client.post('/api/user/register', json={
        'username': 'new_user',
        'email': 'new@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_server_creation(client, auth_headers):
    response = client.post('/api/server/create', 
        json={
            'name': 'test_server',
            'host': 'localhost',
            'port': 8000
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json['name'] == 'test_server'

def test_server_management(client, auth_headers):
    # Create a server first
    server_response = client.post('/api/server/create',
        json={
            'name': 'test_server',
            'host': 'localhost',
            'port': 8000
        },
        headers=auth_headers
    )
    
    server_id = server_response.json['id']
    
    # Test starting the server
    start_response = client.post(f'/api/server/{server_id}/start',
        headers=auth_headers
    )
    assert start_response.status_code == 200
    
    # Test stopping the server
    stop_response = client.post(f'/api/server/{server_id}/stop',
        headers=auth_headers
    )
    assert stop_response.status_code == 200