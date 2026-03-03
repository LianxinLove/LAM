"""
API blueprints registration
"""
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
    """Register all API blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(assets_bp, url_prefix='/api/assets')
    app.register_blueprint(consumables_bp, url_prefix='/api/consumables')
    app.register_blueprint(purchases_bp, url_prefix='/api/purchases')
    app.register_blueprint(borrows_bp, url_prefix='/api/borrows')
    app.register_blueprint(picks_bp, url_prefix='/api/picks')
    app.register_blueprint(transfers_bp, url_prefix='/api/transfers')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
