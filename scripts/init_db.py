#!/usr/bin/env python3
"""Database initialization script"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api import create_app
from src.database import db

def main():
    """Initialize the database"""
    print("🔧 Initializing database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Print table information
        print("\n📊 Created tables:")
        for table in db.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        print(f"\n💾 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    main()
