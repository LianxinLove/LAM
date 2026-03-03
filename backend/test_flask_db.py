"""
Test Flask-SQLAlchemy database connection
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.config import config
from app.models import User

print("=" * 60)
print("Testing Flask-SQLAlchemy Database Connection")
print("=" * 60)
print()

try:
    # Create Flask app
    app = create_app(config['default'])
    
    with app.app_context():
        print("Test 1: Query users using Flask-SQLAlchemy...")
        users = User.query.all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user.id}, Username: {user.username}")
        print()
        
        print("Test 2: Find admin user...")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Found admin user: {admin.username}")
            print(f"Password hash: {admin.password_hash[:50]}...")
            print(f"Is superuser: {admin.is_superuser}")
            print(f"Is active: {admin.is_active}")
        else:
            print("Admin user not found!")
        print()
        
        print("Test 3: Test password check...")
        if admin:
            result = admin.check_password('admin123')
            print(f"Password check result: {result}")
        print()
        
        print("=" * 60)
        print("Flask-SQLAlchemy connection test PASSED!")
        print("=" * 60)
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)
    print("Flask-SQLAlchemy connection test FAILED!")
    print("=" * 60)
