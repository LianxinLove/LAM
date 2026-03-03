# Flask 扩展初始化模块
#
# 认证方式：Session-Cookie（使用 Flask-Session）
#
# 扩展说明：
# 1. SQLAlchemy - ORM 数据库操作框架
# 2. Flask-Migrate - 数据库迁移管理工具
# 3. Flask-Session - 服务端会话管理
#
# 技术要点：
# - 使用 init_app 模式支持应用工厂
# - 扩展对象在模块级别创建，在应用创建后初始化
# - 支持多应用场景

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

# ========== SQLAlchemy ORM ==========
#
# 技术要点：
# - db 对象提供 ORM 接口
# - 使用 db.Model 作为模型基类
# - db.session 提供数据库会话（事务管理）
db = SQLAlchemy()

# ========== Flask-Migrate 数据库迁移 ==========
#
# 技术要点：
# - 基于 Alembic 提供 Flask 集成
# - 自动生成迁移脚本
# - 支持数据库版本升级和降级
# - 使用方式：flask db migrate/upgrade/downgrade
migrate = Migrate()

# ========== Flask-Session 会话管理 ==========
#
# 技术要点：
# - 替代 Flask 默认的客户端 Cookie 会话
# - 将会话数据存储在服务端
# - 客户端 Cookie 只存储 session_id
# - 更加安全，防止会话数据被篡改
# - 支持多种存储后端：filesystem/redis/memcached
session = Session()
