"""Database initialization and migration utilities"""

import os
from flask import Flask
from .models import db


def init_database(app: Flask) -> None:
    """Initialize the database with the Flask app.
    
    Args:
        app: Flask application instance
    """
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Create all tables
    with app.app_context():
        db.create_all()
        print(f"✅ Database initialized at: {app.config.get('SQLALCHEMY_DATABASE_URI')}")


def reset_database(app: Flask) -> None:
    """Drop all tables and recreate them (use with caution!).
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("⚠️  Database reset complete - all data deleted!")
