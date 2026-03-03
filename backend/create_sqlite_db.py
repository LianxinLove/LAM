# 实验室资产管理系统 - 独立 SQLite 数据库创建脚本
# 创建包含所有表和初始数据的 SQLite 数据库（无需 Flask）
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# 为 Windows 控制台设置 UTF-8 编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def create_database():
    # 创建包含所有表和初始数据的 SQLite 数据库
    print("=" * 60)
    print("Lab Asset Management System - SQLite Database Creation")
    print("=" * 60)
    print()

    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'lab_asset_management.db')
    print(f"Database location: {os.path.abspath(db_path)}")
    print()

    # 如果数据库已存在则删除
    if os.path.exists(db_path):
        print("Removing existing database...")
        os.remove(db_path)
        print("[OK] Existing database removed")
        print()

    # 创建数据库连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 启用外键
    cursor.execute("PRAGMA foreign_keys = ON")

    # 创建表
    print("Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120),
            password_hash VARCHAR(255) NOT NULL,
            is_superuser BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  [OK] Created table: users")
    
    # Categories table
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )
    ''')
    print("  [OK] Created table: categories")
    
    # Suppliers table
    cursor.execute('''
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            contact VARCHAR(100),
            phone VARCHAR(20),
            email VARCHAR(120),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  [OK] Created table: suppliers")
    
    # Assets table
    cursor.execute('''
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            category_id INTEGER NOT NULL,
            supplier_id INTEGER,
            specifications TEXT,
            purchase_date DATE,
            purchase_price DECIMAL(12,2),
            status VARCHAR(20) NOT NULL DEFAULT 'available',
            location VARCHAR(100),
            custodian_id INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
            FOREIGN KEY (custodian_id) REFERENCES users (id)
        )
    ''')
    print("  [OK] Created table: assets")
    
    # Consumables table
    cursor.execute('''
        CREATE TABLE consumables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            category_id INTEGER NOT NULL,
            supplier_id INTEGER,
            unit VARCHAR(20) NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            min_stock INTEGER NOT NULL DEFAULT 10,
            price DECIMAL(10,2),
            location VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')
    print("  [OK] Created table: consumables")
    
    # Purchase requests table
    cursor.execute('''
        CREATE TABLE purchase_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            applicant_id INTEGER NOT NULL,
            item_name VARCHAR(200) NOT NULL,
            quantity INTEGER NOT NULL,
            estimated_price DECIMAL(12,2) NOT NULL,
            supplier_id INTEGER,
            reason TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            approver_id INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (applicant_id) REFERENCES users (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
            FOREIGN KEY (approver_id) REFERENCES users (id)
        )
    ''')
    print("  [OK] Created table: purchase_requests")
    
    # Asset transfers table
    cursor.execute('''
        CREATE TABLE asset_transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            from_location VARCHAR(100) NOT NULL,
            to_location VARCHAR(100) NOT NULL,
            reason TEXT NOT NULL,
            applicant_id INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            approver_id INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (applicant_id) REFERENCES users (id),
            FOREIGN KEY (approver_id) REFERENCES users (id)
        )
    ''')
    print("  [OK] Created table: asset_transfers")
    
    # Borrow records table
    cursor.execute('''
        CREATE TABLE borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            borrower_id INTEGER NOT NULL,
            borrow_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            purpose TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'borrowed',
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (borrower_id) REFERENCES users (id)
        )
    ''')
    print("  [OK] Created table: borrow_records")
    
    # Pick records table
    cursor.execute('''
        CREATE TABLE pick_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            picker_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            purpose TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            approver_id INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES consumables (id),
            FOREIGN KEY (picker_id) REFERENCES users (id),
            FOREIGN KEY (approver_id) REFERENCES users (id)
        )
    ''')
    print("  [OK] Created table: pick_records")
    
    # Operation logs table
    cursor.execute('''
        CREATE TABLE operation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action VARCHAR(50) NOT NULL,
            model VARCHAR(50) NOT NULL,
            object_id INTEGER NOT NULL,
            object_repr VARCHAR(200) NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("  [OK] Created table: operation_logs")
    print()

    # Insert initial data
    print("Inserting initial data...")

    # Insert users (password hashes are for 'admin123' and 'test123')
    # Note: In production, use proper password hashing
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, is_superuser, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@lab.com', 'pbkdf2:sha256:260000$admin123$admin123', True, True))
    print("  [OK] Created admin user")
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, is_superuser, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('testuser', 'test@lab.com', 'pbkdf2:sha256:260000$test123$test123', False, True))
    print("  [OK] Created test user")
    
    # Insert categories
    categories = [
        ('试剂', None),
        ('耗材', None),
        ('仪器', None),
        ('其他', None)
    ]
    for cat_name, parent_id in categories:
        cursor.execute('INSERT INTO categories (name, parent_id) VALUES (?, ?)', (cat_name, parent_id))
    print("  [OK] Created 4 default categories")
    
    # Insert suppliers
    suppliers = [
        ('北京科学仪器有限公司', '张经理', '010-12345678', 'zhang@beijing-instrument.com', '北京市海淀区中关村大街1号'),
        ('上海化学试剂厂', '李经理', '021-87654321', 'li@shanghai-chemical.com', '上海市浦东新区张江高科技园区'),
        ('广州实验耗材有限公司', '王经理', '020-11112222', 'wang@guangzhou-consumable.com', '广州市天河区科学城')
    ]
    for supplier_data in suppliers:
        cursor.execute('''
            INSERT INTO suppliers (name, contact, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
        ''', supplier_data)
    print("  [OK] Created 3 sample suppliers")
    
    # Insert assets
    assets = [
        ('电子天平', 'AST-0001', 3, 1, '量程: 0-500g, 精度: 0.01g', '2024-01-15', 2500.00, 'available', '实验室A-101', 1, '精密仪器，需定期校准'),
        ('离心机', 'AST-0002', 3, 1, '转速: 0-15000rpm, 容量: 50ml x 4', '2024-02-20', 8500.00, 'available', '实验室A-102', 1, '高速离心机'),
        ('显微镜', 'AST-0003', 3, 1, '放大倍数: 40x-1000x', '2024-03-10', 12000.00, 'available', '实验室B-201', 1, '生物显微镜'),
        ('恒温培养箱', 'AST-0004', 3, 1, '温度范围: 室温+5~65°C', '2024-04-05', 6800.00, 'maintenance', '实验室B-202', 1, '定期维护中')
    ]
    for asset_data in assets:
        cursor.execute('''
            INSERT INTO assets (name, code, category_id, supplier_id, specifications, purchase_date, purchase_price, status, location, custodian_id, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', asset_data)
    print("  [OK] Created 4 sample assets")
    
    # Insert consumables
    consumables = [
        ('移液枪头', 'CON-0001', 2, 3, '个', 1000, 200, 0.50, '耗材柜A-1'),
        ('离心管', 'CON-0002', 2, 3, '个', 500, 100, 0.30, '耗材柜A-2'),
        ('培养皿', 'CON-0003', 2, 3, '个', 200, 50, 1.20, '耗材柜A-3'),
        ('PBS缓冲液', 'CON-0004', 1, 2, '瓶', 50, 10, 45.00, '试剂柜B-1'),
        ('Tris-HCl缓冲液', 'CON-0005', 1, 2, '瓶', 30, 8, 68.00, '试剂柜B-2'),
        ('乙醇', 'CON-0006', 1, 2, '瓶', 15, 5, 25.00, '试剂柜B-3')
    ]
    for consumable_data in consumables:
        cursor.execute('''
            INSERT INTO consumables (name, code, category_id, supplier_id, unit, stock, min_stock, price, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', consumable_data)
    print("  [OK] Created 6 sample consumables")
    
    # Insert purchase requests
    now = datetime.now()
    two_days_ago = now - timedelta(days=2)
    cursor.execute('''
        INSERT INTO purchase_requests (title, applicant_id, item_name, quantity, estimated_price, supplier_id, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('采购PCR仪', 2, 'PCR仪', 1, 35000.00, 1, '现有PCR仪老化，需要更换新设备', 'pending'))
    
    cursor.execute('''
        INSERT INTO purchase_requests (title, applicant_id, item_name, quantity, estimated_price, supplier_id, reason, status, approver_id, approved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('采购移液枪', 2, '移液枪', 3, 4500.00, 1, '实验室需要补充移液枪', 'approved', 1, two_days_ago))
    print("  [OK] Created 2 sample purchase requests")
    
    # Insert borrow records
    five_days_ago = now - timedelta(days=5)
    ten_days_ago = now - timedelta(days=10)
    eight_days_ago = now - timedelta(days=8)
    
    cursor.execute('''
        INSERT INTO borrow_records (asset_id, borrower_id, borrow_date, purpose, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (1, 2, five_days_ago, '称量实验样品', 'borrowed'))
    
    cursor.execute('''
        INSERT INTO borrow_records (asset_id, borrower_id, borrow_date, return_date, purpose, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (2, 2, ten_days_ago, eight_days_ago, '离心实验', 'returned'))
    print("  [OK] Created 2 sample borrow records")
    
    # Insert pick records
    three_days_ago = now - timedelta(days=3)
    cursor.execute('''
        INSERT INTO pick_records (item_id, picker_id, quantity, purpose, status, approver_id, approved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (1, 2, 100, '日常实验使用', 'approved', 1, three_days_ago))
    
    cursor.execute('''
        INSERT INTO pick_records (item_id, picker_id, quantity, purpose, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (2, 2, 50, '样品处理', 'pending'))
    print("  [OK] Created 2 sample pick records")
    
    # Insert asset transfer
    cursor.execute('''
        INSERT INTO asset_transfers (asset_id, from_location, to_location, reason, applicant_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (3, '实验室B-201', '实验室A-103', '实验室调整，需要移动设备', 2, 'pending'))
    print("  [OK] Created 1 sample asset transfer")
    
    # Insert operation logs
    cursor.execute('''
        INSERT INTO operation_logs (user_id, action, model, object_id, object_repr, details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (1, 'create', 'Asset', 1, '电子天平 (AST-0001)', '创建新资产'))
    
    cursor.execute('''
        INSERT INTO operation_logs (user_id, action, model, object_id, object_repr, details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (2, 'borrow', 'Asset', 1, '电子天平 (AST-0001)', '借用资产'))
    
    cursor.execute('''
        INSERT INTO operation_logs (user_id, action, model, object_id, object_repr, details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (1, 'approve', 'PickRecord', 1, '移液枪头领用记录', '批准领料申请'))
    print("  [OK] Created 3 sample operation logs")
    print()
    
    # Commit all changes
    conn.commit()

    # Display summary
    print("=" * 60)
    print("Database Creation Summary")
    print("=" * 60)

    tables = ['users', 'categories', 'suppliers', 'assets', 'consumables',
              'purchase_requests', 'asset_transfers', 'borrow_records',
              'pick_records', 'operation_logs']

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"[OK] {table}: {count}")

    print()
    print("=" * 60)
    print("Database created successfully!")
    print("=" * 60)
    print()
    print("Database file: " + os.path.abspath(db_path))
    print()
    print("Default login credentials:")
    print("  Admin: admin / admin123")
    print("  User:  testuser / test123")
    print()
    print("Note: Passwords are stored as simple hashes for testing.")
    print("In production, use proper password hashing (bcrypt, etc.)")
    print()

    # Close connection
    conn.close()


if __name__ == '__main__':
    try:
        create_database()
    except Exception as e:
        print(f"\n[ERROR] Error during database creation: {str(e)}")
        import traceback
        traceback.print_exc()
