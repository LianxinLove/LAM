"""
Test database connection and simple queries
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')

print("=" * 60)
print("Testing Database Connection")
print("=" * 60)
print()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test 1: Get users
    print("Test 1: Query users table...")
    cursor.execute("SELECT id, username, password_hash FROM users")
    users = cursor.fetchall()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Password hash: {user[2][:50]}...")
    print()
    
    # Test 2: Get categories
    print("Test 2: Query categories table...")
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    print(f"Found {len(categories)} categories:")
    for cat in categories:
        print(f"  ID: {cat[0]}, Name: {cat[1]}")
    print()
    
    # Test 3: Get assets
    print("Test 3: Query assets table...")
    cursor.execute("SELECT id, name, code, status FROM assets")
    assets = cursor.fetchall()
    print(f"Found {len(assets)} assets:")
    for asset in assets:
        print(f"  ID: {asset[0]}, Name: {asset[1]}, Code: {asset[2]}, Status: {asset[3]}")
    print()
    
    conn.close()
    print("=" * 60)
    print("Database connection test PASSED!")
    print("=" * 60)
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)
    print("Database connection test FAILED!")
    print("=" * 60)
