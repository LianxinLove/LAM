# 测试数据库连接和简单查询
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')

print("=" * 60)
print("测试数据库连接")
print("=" * 60)
print()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 测试1：获取用户
    print("Test 1: 查询用户表...")
    cursor.execute("SELECT id, username, password_hash FROM users")
    users = cursor.fetchall()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Password hash: {user[2][:50]}...")
    print()

    # 测试2：获取类别
    print("Test 2: 查询类别表...")
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    print(f"Found {len(categories)} categories:")
    for cat in categories:
        print(f"  ID: {cat[0]}, Name: {cat[1]}")
    print()

    # 测试3：获取资产
    print("Test 3: 查询资产表...")
    cursor.execute("SELECT id, name, code, status FROM assets")
    assets = cursor.fetchall()
    print(f"Found {len(assets)} assets:")
    for asset in assets:
        print(f"  ID: {asset[0]}, Name: {asset[1]}, Code: {asset[2]}, Status: {asset[3]}")
    print()

    conn.close()
    print("=" * 60)
    print("数据库连接测试通过！")
    print("=" * 60)

except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)
    print("数据库连接测试失败！")
    print("=" * 60)
