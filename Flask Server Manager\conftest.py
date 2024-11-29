import pytest
from app import create_app, db
from app.models import User, Server
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(app):
    user = User(
        username='test_user',
        email='test@example.com',
        role='admin'
    )
    user.set_password('test_password')
    
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/api/user/login', json={
            'email': 'test@example.com',
            'password': 'test_password'
        })
        
        token = response.json['token']
        return {'Authorization': f'Bearer {token}'}