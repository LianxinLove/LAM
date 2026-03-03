# 使用正确的 Werkzeug 哈希修复数据库中的密码哈希
import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')

print("=" * 60)
print("修复数据库中的密码哈希")
print("=" * 60)
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 更新管理员密码
admin_hash = generate_password_hash('admin123')
cursor.execute('''
    UPDATE users SET password_hash = ? WHERE username = 'admin'
''', (admin_hash,))
print(f"Updated password for admin user")

# 更新测试用户密码
testuser_hash = generate_password_hash('test123')
cursor.execute('''
    UPDATE users SET password_hash = ? WHERE username = 'testuser'
''', (testuser_hash,))
print(f"Updated password for testuser user")

conn.commit()

# 验证更新
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
