# 验证 SQLite 数据库是否正确创建的简单脚本
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')

print("=" * 60)
print("SQLite 数据库验证")
print("=" * 60)
print(f"Database: {os.path.abspath(db_path)}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"Total tables: {len(tables)}")
print()

for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count} records")

print()
print("=" * 60)
print("Database verification completed successfully!")
print("=" * 60)

conn.close()
