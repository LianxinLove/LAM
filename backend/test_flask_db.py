# 测试 Flask-SQLAlchemy 数据库连接
import sys
import os

# 将后端添加到路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.config import config
from app.models import User

print("=" * 60)
print("测试 Flask-SQLAlchemy 数据库连接")
print("=" * 60)
print()

try:
    # 创建 Flask 应用
    app = create_app(config['default'])

    with app.app_context():
        print("Test 1: 使用 Flask-SQLAlchemy 查询用户...")
        users = User.query.all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user.id}, Username: {user.username}")
        print()

        print("Test 2: 查找管理员用户...")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Found admin user: {admin.username}")
            print(f"Password hash: {admin.password_hash[:50]}...")
            print(f"Is superuser: {admin.is_superuser}")
            print(f"Is active: {admin.is_active}")
        else:
            print("Admin user not found!")
        print()

        print("Test 3: 测试密码检查...")
        if admin:
            result = admin.check_password('admin123')
            print(f"Password check result: {result}")
        print()

        print("=" * 60)
        print("Flask-SQLAlchemy 连接测试通过！")
        print("=" * 60)

except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)
    print("Flask-SQLAlchemy 连接测试失败！")
    print("=" * 60)
