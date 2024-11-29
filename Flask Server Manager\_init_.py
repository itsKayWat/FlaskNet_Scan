from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from .config import Config
import logging
import os

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Setup logging
    if not os.path.exists(app.config['LOG_FOLDER']):
        os.makedirs(app.config['LOG_FOLDER'])
    
    logging.basicConfig(
        filename=os.path.join(app.config['LOG_FOLDER'], app.config['LOG_FILENAME']),
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Register blueprints
    from .routes import server_bp, file_bp, user_bp, monitoring_bp
    app.register_blueprint(server_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(monitoring_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app