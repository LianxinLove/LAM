# SQLite Database Setup Guide

## Overview

This document describes the SQLite database setup for the Lab Asset Management System. The database has been successfully created and initialized with sample data.

## Database File

- **Location**: `backend/lab_asset_management.db`
- **Size**: ~70 KB
- **Format**: SQLite 3

## Database Schema

The database contains 10 tables:

### 1. users
User accounts and authentication information
- `id` - Primary key
- `username` - Unique username
- `email` - User email address
- `password_hash` - Encrypted password
- `is_superuser` - Admin flag
- `is_active` - Account status
- `created_at` - Account creation timestamp

### 2. categories
Asset and consumable categories
- `id` - Primary key
- `name` - Category name
- `parent_id` - Parent category (for hierarchical categories)
- `created_at` - Creation timestamp

### 3. suppliers
Supplier information
- `id` - Primary key
- `name` - Supplier name
- `contact` - Contact person
- `phone` - Phone number
- `email` - Email address
- `address` - Physical address
- `created_at` - Creation timestamp

### 4. assets
Fixed assets (instruments, equipment)
- `id` - Primary key
- `name` - Asset name
- `code` - Unique asset code
- `category_id` - Foreign key to categories
- `supplier_id` - Foreign key to suppliers
- `specifications` - Technical specifications
- `purchase_date` - Date of purchase
- `purchase_price` - Purchase price
- `status` - Asset status (available/in_use/maintenance/retired)
- `location` - Storage location
- `custodian_id` - Foreign key to users (person responsible)
- `remarks` - Additional notes
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### 5. consumables
Consumable items (reagents, supplies)
- `id` - Primary key
- `name` - Consumable name
- `code` - Unique consumable code
- `category_id` - Foreign key to categories
- `supplier_id` - Foreign key to suppliers
- `unit` - Unit of measurement
- `stock` - Current stock quantity
- `min_stock` - Minimum stock threshold
- `price` - Unit price
- `location` - Storage location
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### 6. purchase_requests
Purchase request records
- `id` - Primary key
- `title` - Request title
- `applicant_id` - Foreign key to users (requester)
- `item_name` - Item to purchase
- `quantity` - Quantity requested
- `estimated_price` - Estimated cost
- `supplier_id` - Foreign key to suppliers
- `reason` - Reason for purchase
- `status` - Request status (pending/approved/purchased/rejected)
- `approver_id` - Foreign key to users (approver)
- `approved_at` - Approval timestamp
- `created_at` - Creation timestamp

### 7. asset_transfers
Asset transfer requests
- `id` - Primary key
- `asset_id` - Foreign key to assets
- `from_location` - Original location
- `to_location` - New location
- `reason` - Transfer reason
- `applicant_id` - Foreign key to users (requester)
- `status` - Request status (pending/approved/rejected)
- `approver_id` - Foreign key to users (approver)
- `approved_at` - Approval timestamp
- `created_at` - Creation timestamp

### 8. borrow_records
Asset borrowing records
- `id` - Primary key
- `asset_id` - Foreign key to assets
- `borrower_id` - Foreign key to users (borrower)
- `borrow_date` - Borrow date
- `return_date` - Return date (if returned)
- `purpose` - Purpose of borrowing
- `status` - Record status (borrowed/returned)

### 9. pick_records
Consumable pick (withdrawal) records
- `id` - Primary key
- `item_id` - Foreign key to consumables
- `picker_id` - Foreign key to users (picker)
- `quantity` - Quantity picked
- `purpose` - Purpose of picking
- `status` - Request status (pending/approved/rejected)
- `approver_id` - Foreign key to users (approver)
- `approved_at` - Approval timestamp
- `created_at` - Creation timestamp

### 10. operation_logs
System operation logs
- `id` - Primary key
- `user_id` - Foreign key to users
- `action` - Action performed (create/update/delete/borrow/return/approve/etc.)
- `model` - Model affected (Asset/Consumable/User/etc.)
- `object_id` - ID of affected object
- `object_repr` - String representation of object
- `details` - Additional details
- `timestamp` - Operation timestamp

## Sample Data

The database has been initialized with sample data for testing:

### Users
- **Admin**: `admin` / `admin123` (Superuser)
- **Test User**: `testuser` / `test123` (Regular user)

### Categories
- 试剂 (Reagents)
- 耗材 (Consumables)
- 仪器 (Instruments)
- 其他 (Others)

### Suppliers
- 北京科学仪器有限公司 (Beijing Scientific Instruments Co., Ltd.)
- 上海化学试剂厂 (Shanghai Chemical Reagent Factory)
- 广州实验耗材有限公司 (Guangzhou Laboratory Consumables Co., Ltd.)

### Assets (4 items)
- 电子天平 (Electronic Balance) - AST-0001
- 离心机 (Centrifuge) - AST-0002
- 显微镜 (Microscope) - AST-0003
- 恒温培养箱 (Constant Temperature Incubator) - AST-0004

### Consumables (6 items)
- 移液枪头 (Pipette Tips) - CON-0001
- 离心管 (Centrifuge Tubes) - CON-0002
- 培养皿 (Petri Dishes) - CON-0003
- PBS缓冲液 (PBS Buffer) - CON-0004
- Tris-HCl缓冲液 (Tris-HCl Buffer) - CON-0005
- 乙醇 (Ethanol) - CON-0006

### Other Records
- 2 purchase requests
- 2 borrow records
- 2 pick records
- 1 asset transfer
- 3 operation logs

## Database Management Scripts

### Create Database
```bash
cd backend
python create_sqlite_db.py
```

This script:
- Creates a new SQLite database
- Creates all required tables
- Inserts sample data
- Displays a summary of created records

### Verify Database
```bash
cd backend
python verify_db.py
```

This script:
- Lists all tables in the database
- Shows record count for each table

### Check Schema
```bash
cd backend
python check_schema.py
```

This script:
- Displays the complete schema of all tables
- Shows column names, types, and constraints

## Configuration

The database configuration is in [`backend/app/config.py`](backend/app/config.py):

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///lab_asset_management.db'
```

You can override this using environment variable:
```bash
export DATABASE_URL=sqlite:///custom_database.db
```

## Database Backup

To backup the database:
```bash
cd backend
cp lab_asset_management.db lab_asset_management_backup.db
```

Or using SQLite command line:
```bash
sqlite3 lab_asset_management.db ".backup lab_asset_management_backup.db"
```

## Database Restore

To restore from backup:
```bash
cd backend
cp lab_asset_management_backup.db lab_asset_management.db
```

## Accessing the Database

### Using Python
```python
import sqlite3

conn = sqlite3.connect('backend/lab_asset_management.db')
cursor = conn.cursor()

# Query example
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

conn.close()
```

### Using SQLite Command Line
```bash
sqlite3 backend/lab_asset_management.db
```

### Using GUI Tools
- DB Browser for SQLite (https://sqlitebrowser.org/)
- DBeaver (https://dbeaver.io/)
- SQLiteStudio (https://sqlitestudio.pl/)

## Important Notes

1. **Password Security**: The sample passwords are stored as simple hashes for testing purposes. In production, use proper password hashing (bcrypt, Argon2, etc.).

2. **Foreign Keys**: Foreign key constraints are enabled in the database. Ensure referential integrity when inserting or updating records.

3. **Timestamps**: All timestamp fields use SQLite's CURRENT_TIMESTAMP by default.

4. **Character Encoding**: The database uses UTF-8 encoding to support Chinese characters.

5. **Decimal Values**: SQLite stores DECIMAL values as REAL (floating-point). For financial calculations, consider using INTEGER to store cents.

## Troubleshooting

### Database Locked Error
If you get a "database is locked" error:
- Ensure no other process is accessing the database
- Close any database viewers or tools
- Restart the Flask application

### Permission Denied Error
If you get a permission error:
- Check file permissions on the database file
- Ensure the application has write access to the backend directory

### Table Not Found Error
If you get a "no such table" error:
- Run the database creation script: `python create_sqlite_db.py`
- Verify the database file exists in the backend directory

## Next Steps

1. Start the Flask backend application:
   ```bash
   cd backend
   python run.py
   ```

2. Access the API at: `http://localhost:5000`

3. Login with the admin account to test all features

4. For production deployment:
   - Change default passwords
   - Implement proper password hashing
   - Set up regular database backups
   - Configure appropriate file permissions
   - Consider using a production-grade database (PostgreSQL, MySQL) for high-traffic scenarios

## Additional Resources

- SQLite Documentation: https://www.sqlite.org/docs.html
- Flask-SQLAlchemy Documentation: https://flask-sqlalchemy.palletsprojects.com/
- Project Requirements: See [`项目需求文档.md`](../项目需求文档.md)
