import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User

def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("数据库表创建成功")
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@lam.local', is_superuser=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("管理员账户创建成功: admin / admin123")
        else:
            print("管理员账户已存在")

        test = User.query.filter_by(username='test').first()
        if not test:
            test = User(username='test', email='test@lam.local', is_superuser=False)
            test.set_password('test123')
            db.session.add(test)
            db.session.commit()
            print("测试用户创建成功: test / test123")

if __name__ == '__main__':
    init_database()
