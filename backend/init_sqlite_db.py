"""
SQLite Database initialization script for Lab Asset Management System
Creates the SQLite database with all tables and initial data
"""
import os
import sys
from datetime import datetime, timedelta
from app import create_app
from app.config import config
from app.models import (
    User, Category, Supplier, Asset, Consumable,
    PurchaseRequest, AssetTransfer, BorrowRecord, PickRecord, OperationLog
)
from app.extensions import db


def init_database():
    """Initialize the SQLite database with tables and initial data"""
    print("=" * 60)
    print("Lab Asset Management System - SQLite Database Initialization")
    print("=" * 60)
    print()
    
    # Create Flask app
    app = create_app(config['default'])
    
    with app.app_context():
        # Get database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"Database location: {os.path.abspath(db_path)}")
        print()
        
        # Drop all existing tables (for clean initialization)
        print("Dropping existing tables (if any)...")
        db.drop_all()
        print("✓ Existing tables dropped")
        print()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        print()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@lab.com',
            is_superuser=True,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        
        # Create regular test user
        print("Creating test user...")
        test_user = User(
            username='testuser',
            email='test@lab.com',
            is_superuser=False,
            is_active=True
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        print("✓ Test user created")
        print("  Username: testuser")
        print("  Password: test123")
        print()
        
        # Create default categories
        print("Creating default categories...")
        categories_data = [
            {'name': '试剂', 'description': '各类实验试剂'},
            {'name': '耗材', 'description': '实验消耗品'},
            {'name': '仪器', 'description': '实验仪器设备'},
            {'name': '其他', 'description': '其他资产类别'}
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category(name=cat_data['name'])
            db.session.add(category)
            db.session.flush()  # Get the ID
            categories[cat_data['name']] = category
            print(f"  ✓ Created category: {cat_data['name']}")
        
        db.session.commit()
        print()
        
        # Create sample suppliers
        print("Creating sample suppliers...")
        suppliers_data = [
            {
                'name': '北京科学仪器有限公司',
                'contact': '张经理',
                'phone': '010-12345678',
                'email': 'zhang@beijing-instrument.com',
                'address': '北京市海淀区中关村大街1号'
            },
            {
                'name': '上海化学试剂厂',
                'contact': '李经理',
                'phone': '021-87654321',
                'email': 'li@shanghai-chemical.com',
                'address': '上海市浦东新区张江高科技园区'
            },
            {
                'name': '广州实验耗材有限公司',
                'contact': '王经理',
                'phone': '020-11112222',
                'email': 'wang@guangzhou-consumable.com',
                'address': '广州市天河区科学城'
            }
        ]
        
        suppliers = {}
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.session.add(supplier)
            db.session.flush()  # Get the ID
            suppliers[supplier_data['name']] = supplier
            print(f"  ✓ Created supplier: {supplier_data['name']}")
        
        db.session.commit()
        print()
        
        # Create sample assets
        print("Creating sample assets...")
        assets_data = [
            {
                'name': '电子天平',
                'code': 'AST-0001',
                'category_id': categories['仪器'].id,
                'supplier_id': suppliers['北京科学仪器有限公司'].id,
                'specifications': '量程: 0-500g, 精度: 0.01g',
                'purchase_date': datetime(2024, 1, 15).date(),
                'purchase_price': 2500.00,
                'status': 'available',
                'location': '实验室A-101',
                'custodian_id': admin.id,
                'remarks': '精密仪器，需定期校准'
            },
            {
                'name': '离心机',
                'code': 'AST-0002',
                'category_id': categories['仪器'].id,
                'supplier_id': suppliers['北京科学仪器有限公司'].id,
                'specifications': '转速: 0-15000rpm, 容量: 50ml x 4',
                'purchase_date': datetime(2024, 2, 20).date(),
                'purchase_price': 8500.00,
                'status': 'available',
                'location': '实验室A-102',
                'custodian_id': admin.id,
                'remarks': '高速离心机'
            },
            {
                'name': '显微镜',
                'code': 'AST-0003',
                'category_id': categories['仪器'].id,
                'supplier_id': suppliers['北京科学仪器有限公司'].id,
                'specifications': '放大倍数: 40x-1000x',
                'purchase_date': datetime(2024, 3, 10).date(),
                'purchase_price': 12000.00,
                'status': 'available',
                'location': '实验室B-201',
                'custodian_id': admin.id,
                'remarks': '生物显微镜'
            },
            {
                'name': '恒温培养箱',
                'code': 'AST-0004',
                'category_id': categories['仪器'].id,
                'supplier_id': suppliers['北京科学仪器有限公司'].id,
                'specifications': '温度范围: 室温+5~65°C',
                'purchase_date': datetime(2024, 4, 5).date(),
                'purchase_price': 6800.00,
                'status': 'maintenance',
                'location': '实验室B-202',
                'custodian_id': admin.id,
                'remarks': '定期维护中'
            }
        ]
        
        assets = {}
        for asset_data in assets_data:
            asset = Asset(**asset_data)
            db.session.add(asset)
            db.session.flush()
            assets[asset_data['code']] = asset
            print(f"  ✓ Created asset: {asset_data['name']} ({asset_data['code']})")
        
        db.session.commit()
        print()
        
        # Create sample consumables
        print("Creating sample consumables...")
        consumables_data = [
            {
                'name': '移液枪头',
                'code': 'CON-0001',
                'category_id': categories['耗材'].id,
                'supplier_id': suppliers['广州实验耗材有限公司'].id,
                'unit': '个',
                'stock': 1000,
                'min_stock': 200,
                'price': 0.50,
                'location': '耗材柜A-1'
            },
            {
                'name': '离心管',
                'code': 'CON-0002',
                'category_id': categories['耗材'].id,
                'supplier_id': suppliers['广州实验耗材有限公司'].id,
                'unit': '个',
                'stock': 500,
                'min_stock': 100,
                'price': 0.30,
                'location': '耗材柜A-2'
            },
            {
                'name': '培养皿',
                'code': 'CON-0003',
                'category_id': categories['耗材'].id,
                'supplier_id': suppliers['广州实验耗材有限公司'].id,
                'unit': '个',
                'stock': 200,
                'min_stock': 50,
                'price': 1.20,
                'location': '耗材柜A-3'
            },
            {
                'name': 'PBS缓冲液',
                'code': 'CON-0004',
                'category_id': categories['试剂'].id,
                'supplier_id': suppliers['上海化学试剂厂'].id,
                'unit': '瓶',
                'stock': 50,
                'min_stock': 10,
                'price': 45.00,
                'location': '试剂柜B-1'
            },
            {
                'name': 'Tris-HCl缓冲液',
                'code': 'CON-0005',
                'category_id': categories['试剂'].id,
                'supplier_id': suppliers['上海化学试剂厂'].id,
                'unit': '瓶',
                'stock': 30,
                'min_stock': 8,
                'price': 68.00,
                'location': '试剂柜B-2'
            },
            {
                'name': '乙醇',
                'code': 'CON-0006',
                'category_id': categories['试剂'].id,
                'supplier_id': suppliers['上海化学试剂厂'].id,
                'unit': '瓶',
                'stock': 15,
                'min_stock': 5,
                'price': 25.00,
                'location': '试剂柜B-3'
            }
        ]
        
        consumables = {}
        for consumable_data in consumables_data:
            consumable = Consumable(**consumable_data)
            db.session.add(consumable)
            db.session.flush()
            consumables[consumable_data['code']] = consumable
            print(f"  ✓ Created consumable: {consumable_data['name']} ({consumable_data['code']})")
        
        db.session.commit()
        print()
        
        # Create sample purchase requests
        print("Creating sample purchase requests...")
        purchase_requests_data = [
            {
                'title': '采购PCR仪',
                'item_name': 'PCR仪',
                'quantity': 1,
                'estimated_price': 35000.00,
                'supplier_id': suppliers['北京科学仪器有限公司'].id,
                'reason': '现有PCR仪老化，需要更换新设备',
                'status': 'pending',
                'applicant_id': test_user.id
            },
            {
                'title': '采购移液枪',
                'item_name': '移液枪',
                'quantity': 3,
                'estimated_price': 4500.00,
                'supplier_id': suppliers['北京科学仪器有限公司'].id,
                'reason': '实验室需要补充移液枪',
                'status': 'approved',
                'applicant_id': test_user.id,
                'approver_id': admin.id,
                'approved_at': datetime.now() - timedelta(days=2)
            }
        ]
        
        for pr_data in purchase_requests_data:
            purchase_request = PurchaseRequest(**pr_data)
            db.session.add(purchase_request)
            print(f"  ✓ Created purchase request: {pr_data['title']}")
        
        db.session.commit()
        print()
        
        # Create sample borrow records
        print("Creating sample borrow records...")
        borrow_records_data = [
            {
                'asset_id': assets['AST-0001'].id,
                'borrower_id': test_user.id,
                'borrow_date': datetime.now() - timedelta(days=5),
                'purpose': '称量实验样品',
                'status': 'borrowed'
            },
            {
                'asset_id': assets['AST-0002'].id,
                'borrower_id': test_user.id,
                'borrow_date': datetime.now() - timedelta(days=10),
                'return_date': datetime.now() - timedelta(days=8),
                'purpose': '离心实验',
                'status': 'returned'
            }
        ]
        
        for br_data in borrow_records_data:
            borrow_record = BorrowRecord(**br_data)
            db.session.add(borrow_record)
            print(f"  ✓ Created borrow record for asset: {br_data['asset_id']}")
        
        db.session.commit()
        print()
        
        # Create sample pick records
        print("Creating sample pick records...")
        pick_records_data = [
            {
                'item_id': consumables['CON-0001'].id,
                'picker_id': test_user.id,
                'quantity': 100,
                'purpose': '日常实验使用',
                'status': 'approved',
                'approver_id': admin.id,
                'approved_at': datetime.now() - timedelta(days=3)
            },
            {
                'item_id': consumables['CON-0002'].id,
                'picker_id': test_user.id,
                'quantity': 50,
                'purpose': '样品处理',
                'status': 'pending'
            }
        ]
        
        for pr_data in pick_records_data:
            pick_record = PickRecord(**pr_data)
            db.session.add(pick_record)
            print(f"  ✓ Created pick record for item: {pr_data['item_id']}")
        
        db.session.commit()
        print()
        
        # Create sample asset transfer
        print("Creating sample asset transfer...")
        asset_transfer = AssetTransfer(
            asset_id=assets['AST-0003'].id,
            from_location='实验室B-201',
            to_location='实验室A-103',
            reason='实验室调整，需要移动设备',
            applicant_id=test_user.id,
            status='pending'
        )
        db.session.add(asset_transfer)
        db.session.commit()
        print("  ✓ Created asset transfer request")
        print()
        
        # Create sample operation logs
        print("Creating sample operation logs...")
        operation_logs_data = [
            {
                'user_id': admin.id,
                'action': 'create',
                'model': 'Asset',
                'object_id': assets['AST-0001'].id,
                'object_repr': '电子天平 (AST-0001)',
                'details': '创建新资产'
            },
            {
                'user_id': test_user.id,
                'action': 'borrow',
                'model': 'Asset',
                'object_id': assets['AST-0001'].id,
                'object_repr': '电子天平 (AST-0001)',
                'details': '借用资产'
            },
            {
                'user_id': admin.id,
                'action': 'approve',
                'model': 'PickRecord',
                'object_id': 1,
                'object_repr': '移液枪头领用记录',
                'details': '批准领料申请'
            }
        ]
        
        for ol_data in operation_logs_data:
            operation_log = OperationLog(**ol_data)
            db.session.add(operation_log)
            print(f"  ✓ Created operation log: {ol_data['action']} {ol_data['model']}")
        
        db.session.commit()
        print()
        
        # Display summary
        print("=" * 60)
        print("Database Initialization Summary")
        print("=" * 60)
        print(f"✓ Users: {User.query.count()}")
        print(f"✓ Categories: {Category.query.count()}")
        print(f"✓ Suppliers: {Supplier.query.count()}")
        print(f"✓ Assets: {Asset.query.count()}")
        print(f"✓ Consumables: {Consumable.query.count()}")
        print(f"✓ Purchase Requests: {PurchaseRequest.query.count()}")
        print(f"✓ Borrow Records: {BorrowRecord.query.count()}")
        print(f"✓ Pick Records: {PickRecord.query.count()}")
        print(f"✓ Asset Transfers: {AssetTransfer.query.count()}")
        print(f"✓ Operation Logs: {OperationLog.query.count()}")
        print()
        print("=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        print()
        print("You can now start the application with:")
        print("  python run.py")
        print()
        print("Default login credentials:")
        print("  Admin: admin / admin123")
        print("  User:  testuser / test123")
        print()


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error during database initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
