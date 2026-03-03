"""
Script to fix password hashes in the database using proper Werkzeug hashing
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')

print("=" * 60)
print("Fixing Password Hashes in Database")
print("=" * 60)
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update admin password
admin_hash = generate_password_hash('admin123')
cursor.execute('''
    UPDATE users SET password_hash = ? WHERE username = 'admin'
''', (admin_hash,))
print(f"Updated password for admin user")

# Update testuser password
testuser_hash = generate_password_hash('test123')
cursor.execute('''
    UPDATE users SET password_hash = ? WHERE username = 'testuser'
''', (testuser_hash,))
print(f"Updated password for testuser user")

conn.commit()

# Verify the updates
cursor.execute('SELECT username, password_hash FROM users')
users = cursor.fetchall()

print()
print("Updated users:")
for username, password_hash in users:
    print(f"  {username}: {password_hash[:50]}...")

print()
print("=" * 60)
print("Password hashes updated successfully!")
print("=" * 60)

conn.close()
