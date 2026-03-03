"""
Database initialization script
Creates the database tables and initial data
"""
from app import create_app
from app.config import config
from app.models import User, Category, Supplier
from app.extensions import db

def init_database():
    """Initialize the database with tables and initial data"""
    app = create_app(config['default'])
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                is_superuser=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists.")
        
        # Create default categories
        default_categories = ['试剂', '耗材', '仪器', '其他']
        for cat_name in default_categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                print(f"Creating category: {cat_name}")
                category = Category(name=cat_name)
                db.session.add(category)
        
        db.session.commit()
        print("Default categories created successfully!")
        
        # Create a sample supplier
        supplier = Supplier.query.filter_by(name='示例供应商').first()
        if not supplier:
            print("Creating sample supplier...")
            supplier = Supplier(
                name='示例供应商',
                contact='张三',
                phone='13800138000',
                email='supplier@example.com',
                address='北京市朝阳区'
            )
            db.session.add(supplier)
            db.session.commit()
            print("Sample supplier created successfully!")
        
        print("\nDatabase initialization completed!")
        print("\nYou can now start the application with: python run.py")

if __name__ == '__main__':
    init_database()
