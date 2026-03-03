# 课题组资产管理系统 (Lab Asset Management System)

基于 Flask 和 MySQL 的实验室资产管理系统，实现资产的全生命周期管理。

## 技术栈

- **后端框架**: Flask 3.0+
- **数据库**: MySQL 8.0+
- **认证系统**: JWT (JSON Web Token)
- **API设计**: RESTful API
- **ORM**: SQLAlchemy

## 功能特性

### 用户认证
- 用户注册和登录
- JWT token 认证
- 角色权限管理（管理员/普通用户）

### 资产管理
- 资产列表查看和筛选
- 资产增删改查（管理员）
- 资产状态管理（可用/使用中/维修中/已报废）

### 耗材管理
- 耗材列表查看和筛选
- 耗材增删改查（管理员）
- 库存预警功能

### 采购管理
- 采购申请提交
- 采购审批（管理员）
- 申请记录查询

### 资产借用
- 资产借用申请
- 资产归还
- 借用记录查询

### 领料管理
- 耗材领料申请
- 领料审批（管理员）
- 领料记录查询

### 资产转移
- 资产位置转移申请
- 转移审批（管理员）
- 转移记录查询

### 统计分析
- 仪表盘数据展示
- 资产统计（按状态、类别）
- 耗材统计（总价值、低库存）
- 采购统计（按状态、预算）

### 基础数据管理
- 资产类别管理
- 供应商管理

### 操作日志
- 系统操作日志记录
- 日志查询（管理员）

## 项目结构

```
backend/
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── config.py                # 配置文件
│   ├── extensions.py            # Flask 扩展初始化
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py            # 用户模型
│   │   ├── category.py        # 类别模型
│   │   ├── supplier.py        # 供应商模型
│   │   ├── asset.py          # 资产模型
│   │   ├── consumable.py      # 耗材模型
│   │   ├── purchase_request.py # 采购申请模型
│   │   ├── asset_transfer.py  # 资产转移模型
│   │   ├── borrow_record.py   # 借还记录模型
│   │   ├── pick_record.py     # 领料记录模型
│   │   └── operation_log.py   # 操作日志模型
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证接口
│   │   ├── assets.py          # 资产管理接口
│   │   ├── consumables.py     # 耗材管理接口
│   │   ├── purchases.py       # 采购管理接口
│   │   ├── borrows.py         # 借用管理接口
│   │   ├── picks.py           # 领料管理接口
│   │   ├── transfers.py       # 转移管理接口
│   │   ├── dashboard.py       # 仪表盘接口
│   │   ├── categories.py      # 类别管理接口
│   │   ├── suppliers.py       # 供应商管理接口
│   │   └── logs.py           # 日志接口
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── decorators.py       # 装饰器
│       ├── response.py         # 响应工具
│       ├── validators.py       # 验证工具
│       └── error_handlers.py  # 错误处理
├── init_db.py                # 数据库初始化脚本
├── run.py                    # 应用入口
├── requirements.txt           # Python 依赖
└── README.md                # 项目文档
```

## 安装步骤

### 1. 环境要求

- Python 3.11+
- MySQL 8.0+

### 2. 克隆项目

```bash
cd backend
```

### 3. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置数据库

#### 创建 MySQL 数据库

```sql
CREATE DATABASE lab_asset_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 配置数据库连接

编辑 `app/config.py` 文件，修改数据库连接信息：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost:3306/lab_asset_management?charset=utf8mb4'
```

或者使用环境变量：

```bash
# Windows
set DATABASE_URL=mysql+pymysql://username:password@localhost:3306/lab_asset_management?charset=utf8mb4

# Linux/Mac
export DATABASE_URL=mysql+pymysql://username:password@localhost:3306/lab_asset_management?charset=utf8mb4
```

### 6. 初始化数据库

```bash
python init_db.py
```

这将创建所有数据库表，并创建默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

### 7. 启动应用

```bash
python run.py
```

应用将在 `http://localhost:5000` 启动。

## API 接口文档

### 认证接口

#### 用户注册
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "email": "string (optional)"
}
```

#### 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

#### 获取当前用户信息
```
GET /api/auth/me
Authorization: Bearer <token>
```

#### 用户登出
```
POST /api/auth/logout
Authorization: Bearer <token>
```

### 资产管理接口

#### 获取资产列表
```
GET /api/assets?category_id=1&status=available&page=1&page_size=20
Authorization: Bearer <token>
```

#### 获取资产详情
```
GET /api/assets/<asset_id>
Authorization: Bearer <token>
```

#### 创建资产（管理员）
```
POST /api/assets
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "code": "string",
  "category_id": 1,
  "supplier_id": 1,
  "specifications": "string",
  "purchase_date": "2024-01-01",
  "purchase_price": 1000.00,
  "location": "string",
  "custodian_id": 1,
  "remarks": "string"
}
```

#### 更新资产（管理员）
```
PUT /api/assets/<asset_id>
Authorization: Bearer <token>
Content-Type: application/json
```

#### 删除资产（管理员）
```
DELETE /api/assets/<asset_id>
Authorization: Bearer <token>
```

### 耗材管理接口

#### 获取耗材列表
```
GET /api/consumables?category_id=1&low_stock=true&page=1&page_size=20
Authorization: Bearer <token>
```

#### 创建耗材（管理员）
```
POST /api/consumables
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "category_id": 1,
  "supplier_id": 1,
  "unit": "个",
  "stock": 100,
  "min_stock": 10,
  "price": 10.00,
  "location": "string"
}
```

### 采购管理接口

#### 创建采购申请
```
POST /api/purchases
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "string",
  "item_name": "string",
  "quantity": 10,
  "estimated_price": 1000.00,
  "supplier_id": 1,
  "reason": "string"
}
```

#### 审批采购申请（管理员）
```
POST /api/purchases/<request_id>/approve
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "approve"  // 或 "reject"
}
```

### 借用管理接口

#### 借用资产
```
POST /api/borrows
Authorization: Bearer <token>
Content-Type: application/json

{
  "asset_id": 1,
  "purpose": "string"
}
```

#### 归还资产
```
POST /api/borrows/<record_id>/return
Authorization: Bearer <token>
```

#### 获取我的借用记录
```
GET /api/borrows/my
Authorization: Bearer <token>
```

### 领料管理接口

#### 创建领料申请
```
POST /api/picks
Authorization: Bearer <token>
Content-Type: application/json

{
  "item_id": 1,
  "quantity": 10,
  "purpose": "string"
}
```

#### 审批领料申请（管理员）
```
POST /api/picks/<pick_id>/approve
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "approve"  // 或 "reject"
}
```

### 资产转移接口

#### 创建转移申请
```
POST /api/transfers
Authorization: Bearer <token>
Content-Type: application/json

{
  "asset_id": 1,
  "to_location": "string",
  "reason": "string"
}
```

#### 审批转移申请（管理员）
```
POST /api/transfers/<transfer_id>/approve
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "approve"  // 或 "reject"
}
```

### 仪表盘接口

#### 获取仪表盘数据
```
GET /api/dashboard
Authorization: Bearer <token>
```

#### 获取统计数据
```
GET /api/dashboard/statistics
Authorization: Bearer <token>
```

### 基础数据接口

#### 获取类别列表
```
GET /api/categories
Authorization: Bearer <token>
```

#### 创建类别（管理员）
```
POST /api/categories
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "parent_id": 1
}
```

#### 获取供应商列表
```
GET /api/suppliers
Authorization: Bearer <token>
```

#### 创建供应商（管理员）
```
POST /api/suppliers
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "contact": "string",
  "phone": "string",
  "email": "string",
  "address": "string"
}
```

### 操作日志接口

#### 获取操作日志（管理员）
```
GET /api/logs?page=1&page_size=20
Authorization: Bearer <token>
```

## 响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误信息",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

### 常见错误码
- `AUTH_REQUIRED`: 需要登录
- `INVALID_TOKEN`: 无效的token
- `PERMISSION_DENIED`: 权限不足
- `VALIDATION_ERROR`: 参数验证失败
- `NOT_FOUND`: 资源不存在
- `INSUFFICIENT_STOCK`: 库存不足
- `DUPLICATE_ENTRY`: 重复数据

## 开发说明

### 添加新的 API 端点

1. 在 `app/api/` 目录下创建新的蓝图文件
2. 在 `app/api/__init__.py` 中注册蓝图
3. 使用 `@login_required` 或 `@admin_required` 装饰器保护端点

### 添加新的数据模型

1. 在 `app/models/` 目录下创建新的模型文件
2. 在 `app/models/__init__.py` 中导入模型
3. 运行 `python init_db.py` 更新数据库

### 环境变量

可以通过环境变量配置应用：

- `SECRET_KEY`: Flask 密钥
- `JWT_SECRET_KEY`: JWT 密钥
- `DATABASE_URL`: 数据库连接字符串
- `CORS_ORIGINS`: CORS 允许的源

## 部署

### 生产环境配置

1. 修改 `app/config.py` 使用 `ProductionConfig`
2. 设置强密码的 `SECRET_KEY` 和 `JWT_SECRET_KEY`
3. 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
4. 配置 Nginx 作为反向代理
5. 启用 HTTPS

### Docker 部署（可选）

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: lab_asset_management
    volumes:
      - mysql_data:/var/lib/mysql

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: mysql+pymysql://root:rootpassword@db:3306/lab_asset_management?charset=utf8mb4
    depends_on:
      - db

volumes:
  mysql_data:
```

运行：

```bash
docker-compose up -d
```

## 测试

### 运行测试

```bash
pytest tests/
```

### API 测试

可以使用 Postman 或 curl 测试 API：

```bash
# 注册用户
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

## 常见问题

### 数据库连接失败

检查 MySQL 服务是否运行，以及连接字符串是否正确。

### JWT Token 过期

默认 token 有效期为 24 小时，过期后需要重新登录。

### 权限不足

确保使用管理员账户登录，或检查用户权限设置。

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题，请联系项目维护者。
