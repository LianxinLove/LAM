"""
Lab Asset Management System - Flask Application
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.extensions import db, migrate
from app.api import register_blueprints


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app
