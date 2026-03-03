"""
Dashboard and statistics API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from app.models import Asset, Consumable, PurchaseRequest, AssetTransfer, PickRecord, BorrowRecord, User, Category
from app.utils.decorators import login_required
from app.utils.response import success_response
from app.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('', methods=['GET'])
@login_required
def get_dashboard():
    """Get dashboard data"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Basic counts
    asset_count = Asset.query.count()
    consumable_count = Consumable.query.count()
    
    # User-specific data
    my_borrows = BorrowRecord.query.filter_by(borrower_id=user_id, status='borrowed').count()
    my_requests = PurchaseRequest.query.filter_by(applicant_id=user_id).count()
    
    # Low stock items
    low_stock_items = Consumable.query.filter(Consumable.stock < Consumable.min_stock).all()
    low_stock_data = [
        {
            'id': item.id,
            'name': item.name,
            'stock': item.stock,
            'min_stock': item.min_stock
        }
        for item in low_stock_items
    ]
    
    data = {
        'asset_count': asset_count,
        'consumable_count': consumable_count,
        'my_borrows': my_borrows,
        'my_requests': my_requests,
        'low_stock_items': low_stock_data
    }
    
    # Admin-specific data
    if user and user.is_superuser:
        pending_purchases = PurchaseRequest.query.filter_by(status='pending').count()
        pending_transfers = AssetTransfer.query.filter_by(status='pending').count()
        pending_picks = PickRecord.query.filter_by(status='pending').count()
        
        data.update({
            'pending_purchases': pending_purchases,
            'pending_transfers': pending_transfers,
            'pending_picks': pending_picks
        })
    
    return success_response(data=data)


@dashboard_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """Get detailed statistics"""
    # Asset by status
    asset_by_status = db.session.query(
        Asset.status,
        func.count(Asset.id)
    ).group_by(Asset.status).all()
    asset_by_status_data = [
        {'status': status, 'count': count}
        for status, count in asset_by_status
    ]
    
    # Asset by category
    asset_by_category = db.session.query(
        Category.name,
        func.count(Asset.id)
    ).join(Category).group_by(Category.name).all()
    asset_by_category_data = [
        {'category': name, 'count': count}
        for name, count in asset_by_category
    ]
    
    # Consumable total value
    consumable_value = db.session.query(
        func.sum(Consumable.stock * Consumable.price)
    ).scalar() or 0
    
    # Low stock count
    low_stock_count = Consumable.query.filter(Consumable.stock < Consumable.min_stock).count()
    
    # Purchase by status
    purchase_by_status = db.session.query(
        PurchaseRequest.status,
        func.count(PurchaseRequest.id)
    ).group_by(PurchaseRequest.status).all()
    purchase_by_status_data = [
        {'status': status, 'count': count}
        for status, count in purchase_by_status
    ]
    
    # Total budget
    total_budget = db.session.query(
        func.sum(PurchaseRequest.estimated_price)
    ).scalar() or 0
    
    # Active borrows
    active_borrows = BorrowRecord.query.filter_by(status='borrowed').count()
    
    data = {
        'asset_by_status': asset_by_status_data,
        'asset_by_category': asset_by_category_data,
        'total_consumable_value': float(consumable_value),
        'low_stock_count': low_stock_count,
        'purchase_by_status': purchase_by_status_data,
        'total_budget': float(total_budget),
        'active_borrows': active_borrows
    }
    
    return success_response(data=data)
