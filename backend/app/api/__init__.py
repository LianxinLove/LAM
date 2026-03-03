# API 蓝图注册模块
#
# 功能说明：
# - 集中管理所有 API 蓝图的注册
# - 统一配置 URL 前缀
# - 简化应用初始化流程
#
# 技术要点：
# - Flask Blueprint（蓝图）：模块化路由管理
# - url_prefix：统一添加 URL 前缀（如 /api/assets）
# - 便于团队协作：不同模块的路由在不同文件中开发
#
# API 路由结构：
# /api/auth        - 认证相关（登录、注册、登出）
# /api/assets      - 资产管理
# /api/consumables - 耗材管理
# /api/purchases   - 采购管理
# /api/borrows     - 资产借用
# /api/picks       - 耗材领用
# /api/transfers   - 资产调拨
# /api/dashboard   - 仪表盘统计
# /api/categories   - 资产类别
# /api/suppliers   - 供应商管理
# /api/logs        - 操作日志

# 导入各模块蓝图
from app.api.auth import auth_bp
from app.api.assets import assets_bp
from app.api.consumables import consumables_bp
from app.api.purchases import purchases_bp
from app.api.borrows import borrows_bp
from app.api.picks import picks_bp
from app.api.transfers import transfers_bp
from app.api.dashboard import dashboard_bp
from app.api.categories import categories_bp
from app.api.suppliers import suppliers_bp
from app.api.logs import logs_bp


def register_blueprints(app):
    # """
    # 注册所有 API 蓝图到 Flask 应用
    #
    # 技术要点：
    # - url_prefix：为整个蓝图添加 URL 前缀
    # - 统一前缀：/api/xxx，便于识别和代理配置
    # - 便于版本控制：可以添加 /api/v1/xxx
    #
    # Args:
    #     app (Flask): Flask 应用实例
    # """
    # 认证模块
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 核心业务模块
    app.register_blueprint(assets_bp, url_prefix='/api/assets')
    app.register_blueprint(consumables_bp, url_prefix='/api/consumables')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')

    # 业务流程模块
    app.register_blueprint(purchases_bp, url_prefix='/api/purchases')
    app.register_blueprint(borrows_bp, url_prefix='/api/borrows')
    app.register_blueprint(picks_bp, url_prefix='/api/picks')
    app.register_blueprint(transfers_bp, url_prefix='/api/transfers')

    # 统计和日志模块
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
