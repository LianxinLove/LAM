# 检查 SQLite 数据库结构的脚本
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')

print("=" * 60)
print("SQLite 数据库结构检查")
print("=" * 60)
print(f"Database: {os.path.abspath(db_path)}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表（排除 sqlite_sequence）
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    print("-" * 60)

    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        pk_str = " [PK]" if pk else ""
        null_str = " NOT NULL" if notnull else ""
        default_str = f" DEFAULT {default}" if default else ""
        print(f"  {name:20} {type_:15}{null_str}{default_str}{pk_str}")

print()
print("=" * 60)
print("结构检查完成！")
print("=" * 60)

conn.close()
