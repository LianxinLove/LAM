# 应用配置模块
#
# 认证方式：Session-Cookie
# - 使用 Flask-Session 管理服务端会话
# - 使用安全的 Cookie 存储会话 ID
# - 支持跨域请求携带凭证
#
# 配置环境：
# - DevelopmentConfig: 开发环境（调试模式开启）
# - ProductionConfig: 生产环境（安全加固）
# - TestingConfig: 测试环境（内存数据库）
#
# 技术要点：
# - 使用环境变量覆盖配置
# - 敏感信息通过环境变量传递
# - 支持多种数据库后端
import os
from datetime import timedelta


class Config:
    # 基础配置类 - 包含所有环境共用的配置

    # ========== Flask 基础配置 ==========

    # SECRET_KEY 用于签名会话 Cookie 和其他安全相关的操作
    # 技术要点：
    # - 生产环境必须设置为随机字符串
    # - 泄露会导致会话被伪造
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # ========== Session 配置（替代 JWT） ==========

    # 会话存储类型
    # 可选值：'filesystem'（文件系统）, 'redis'（Redis）, 'memcached'（Memcached）
    SESSION_TYPE = 'filesystem'

    # 会话持久化：True 表示会话在浏览器关闭后仍然有效
    SESSION_PERMANENT = True

    # 会话有效期：7 天
    # 技术要点：
    # - 配合 SESSION_PERMANENT 使用
    # - 到期后需要重新登录
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # 会话文件存储目录
    # 技术要点：
    # - SESSION_TYPE='filesystem' 时使用
    # - 自动创建（在 __init__.py 中处理）
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'flask_session')

    # Cookie 名称
    SESSION_COOKIE_NAME = 'lab_asset_session'

    # Cookie 安全设置
    SESSION_COOKIE_SECURE = False         # 是否仅 HTTPS 传输（生产环境应为 True）
    SESSION_COOKIE_HTTPONLY = True        # 防止 JavaScript 访问 Cookie（防 XSS）
    SESSION_COOKIE_SAMESITE = 'Lax'       # 防止 CSRF 攻击（'Lax' 或 'Strict'）

    # ========== 数据库配置 ==========

    # 数据库连接 URI
    # 技术要点：
    # - Docker 环境使用 /app/data 目录（通过 volume 持久化）
    # - 本地开发使用项目根目录
    # - 生产环境应使用 PostgreSQL 或 MySQL
    # - SQLite 适用于开发和测试
    # - SQLite 在多线程环境需要特殊配置
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Docker 环境检测
        if os.path.exists('/app/data'):
            # 使用绝对路径格式：sqlite:////path
            # Flask-SQLAlchemy 会自动在路径前添加 instance/
            # 所以需要使用相对路径从 instance 文件夹指向 data 目录
            SQLALCHEMY_DATABASE_URI = 'sqlite:///../../data/lab_asset_management.db?check_same_thread=False'
        else:
            _basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(_basedir, 'lab_asset_management.db')
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}?check_same_thread=False'

    # 禁用修改事件追踪
    # 技术要点：
    # - SQLAlchemy 的事件系统会消耗内存
    # - Flask-SQLAlchemy 默认需要此配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 是否输出 SQL 语句（开发环境可开启）
    SQLALCHEMY_ECHO = False

    # ========== CORS 跨域配置 ==========

    # 允许的跨域源
    # 技术要点：
    # - 生产环境应指定具体域名
    # - 开发环境使用 '*' 允许所有源（方便局域网访问）
    # - 支持 credentials 时不能使用 '*'，但开发环境通过前端直接请求后端 IP 可解决
    # - 可通过环境变量 CORS_ORIGINS 自定义
    default_origins = '*'
    if os.environ.get('CORS_ORIGINS'):
        default_origins = os.environ.get('CORS_ORIGINS')
    CORS_ORIGINS = default_origins

    # 是否支持跨域携带凭证（Cookie）
    # 技术要点：
    # - Session-Cookie 认证必须设为 True
    # - 启用后 CORS_ORIGINS 不能为 '*'
    CORS_SUPPORTS_CREDENTIALS = True

    # ========== 分页配置 ==========

    # 默认每页数量
    DEFAULT_PAGE_SIZE = 20

    # 最大每页数量（防止查询过多数据）
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    # 开发环境配置
    #
    # 特点：
    # - DEBUG = True: 显示详细错误信息，代码修改自动重载
    # - SQLALCHEMY_ECHO = True: 打印 SQL 语句，方便调试
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    # 生产环境配置
    #
    # 特点：
    # - DEBUG = False: 不显示详细错误信息
    # - SQLALCHEMY_ECHO = False: 不打印 SQL 语句
    # - SESSION_COOKIE_SECURE = True: Cookie 仅通过 HTTPS 传输
    #
    # 生产环境部署建议：
    # - 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
    # - 使用 Nginx 作为反向代理
    # - 配置 HTTPS（Let's Encrypt 免费证书）
    # - 使用 PostgreSQL 或 MySQL 数据库
    # - 设置强随机 SECRET_KEY
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True          # 生产环境启用 HTTPS only


class TestingConfig(Config):
    # 测试环境配置
    #
    # 特点：
    # - TESTING = True: 启用测试模式
    # - 使用内存数据库，测试后自动清理
    # - 禁用 CSRF 保护
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# 配置字典
# 技术要点：
# - 通过 FLASK_ENV 环境变量选择配置
# - 默认使用开发环境配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
