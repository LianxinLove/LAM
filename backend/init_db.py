# 数据库初始化脚本
#
# 用途：
# 1. 重新创建所有表
# 2. 创建默认管理员账户
#
# 使用方法：
#   python init_db.py

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User


def init_database():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 检查并创建所有表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if existing_tables:
            print(f"! 数据库已存在 {len(existing_tables)} 个表: {existing_tables}")
            print("! 如需重建数据库，请先停止后端服务并删除 lab_asset_management.db 文件")
        else:
            db.create_all()
            print("✓ 数据库表创建成功")

        # 创建默认管理员账户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@lam.local',
                is_superuser=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ 默认管理员账户创建成功")
            print("  用户名: admin")
            print("  密码: admin123")
            print("  请在登录后立即修改密码！")
        else:
            print("! 管理员账户已存在")

        # 创建测试普通用户
        test_user = User.query.filter_by(username='test').first()
        if not test_user:
            test_user = User(
                username='test',
                email='test@lam.local',
                is_superuser=False
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print("✓ 测试用户账户创建成功")
            print("  用户名: test")
            print("  密码: test123")

        print("\n" + "=" * 50)
        print("初始化完成！")
        print("=" * 50)
        print("管理员登录信息：")
        print("  用户名: admin")
        print("  密码: admin123")
        print("=" * 50)


if __name__ == '__main__':
    init_database()
