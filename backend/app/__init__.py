# 实验室资产管理系统 - Flask 应用入口
#
# 认证方式：Session-Cookie
# - 使用 Flask-Session 管理服务端会话
# - 使用安全的 Cookie 存储会话 ID
# - 支持跨域请求携带凭证
#
# 技术架构：
# - Flask: Web 框架
# - SQLAlchemy: ORM 数据库操作
# - Flask-Migrate: 数据库迁移管理
# - Flask-Session: 服务端会话管理
# - Flask-CORS: 跨域资源共享

from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, session
from app.api import register_blueprints


def create_app(config_class=Config):
    # """
    # 应用工厂函数
    #
    # 技术要点：
    # - 工厂模式：允许创建多个不同配置的应用实例
    # - 延迟初始化：扩展在应用创建后才初始化
    # - 配置分离：通过 config_class 参数指定配置类
    #
    # 初始化流程：
    # 1. 创建 Flask 应用实例
    # 2. 加载配置
    # 3. 初始化扩展（数据库、迁移、会话）
    # 4. 配置 CORS 跨域支持
    # 5. 注册蓝图（路由）
    # 6. 注册错误处理器
    # 7. 创建会话文件目录
    #
    # Args:
    #     config_class: 配置类，默认为 Config
    #
    # Returns:
    #     Flask: 配置完成的 Flask 应用实例
    # """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ========== 确保必要的目录存在 ==========
    import os

    # 确保会话目录存在
    session_dir = app.config.get('SESSION_FILE_DIR')
    if session_dir and not os.path.exists(session_dir):
        os.makedirs(session_dir, exist_ok=True)

    # 确保数据库目录存在
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_path.startswith('sqlite:///'):
        db_file = db_path.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    # ========== 初始化扩展 ==========

    # SQLAlchemy ORM - 数据库操作
    # 技术要点：使用 init_app 模式，支持多应用
    db.init_app(app)

    # Flask-Migrate - 数据库迁移管理
    # 技术要点：基于 Alembic，提供数据库版本控制
    migrate.init_app(app, db)

    # Flask-Session - 服务端会话管理
    # 技术要点：
    # - 将会话数据存储在服务端文件系统
    # - 客户端只存储 session_id（通过 Cookie）
    # - 更加安全，避免客户端篡改会话数据
    session.init_app(app)

    # ========== 配置 CORS 跨域支持 ==========

    # 技术要点：
    # - supports_credentials=True: 允许跨域携带 Cookie
    # - Session-Cookie 认证必须启用此选项
    # - origins: 明确指定允许的源，增强安全性
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,  # 允许跨域携带 Cookie（Session 认证必需）
         allow_headers=['Content-Type'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # ========== 注册蓝图 ==========

    # 技术要点：
    # - 蓝图是 Flask 模块化路由的方式
    # - 将不同功能模块的路由分离到独立文件中管理
    register_blueprints(app)

    # ========== 注册错误处理器 ==========

    # 技术要点：
    # - 统一处理各种 HTTP 错误
    # - 返回标准化的 JSON 错误响应
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # ========== 自动创建数据库表 ==========

    # 技术要点：
    # - 检测数据库文件是否存在
    # - 如果不存在，使用 db.create_all() 创建所有表
    # - 适用于开发环境和小型部署
    # - 生产环境应使用 Flask-Migrate 进行版本控制
    with app.app_context():
        try:
            # 尝试连接数据库，如果失败则创建表
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            if not existing_tables:
                # 数据库为空，创建所有表
                db.create_all()
                app.logger.info('Database tables created successfully')
        except Exception as e:
            # 如果连接失败，尝试创建表（可能是新数据库）
            try:
                db.create_all()
                app.logger.info('Database tables created successfully')
            except Exception as create_error:
                app.logger.error(f'Failed to create database tables: {create_error}')

    # ========== 健康检查端点 ==========
    # 用于 Docker 健康检查和负载均衡器探测

    @app.route('/api/health')
    def health_check():
        """健康检查端点，返回服务状态"""
        return {'status': 'healthy', 'service': 'Lab Asset Management API'}

    return app
