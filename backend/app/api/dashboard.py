# 仪表盘统计 API 路由
from flask import Blueprint, request, session, g
from sqlalchemy import func
from app.models import Asset, Consumable, PurchaseRequest, AssetTransfer, PickRecord, BorrowRecord, User, Category
from app.utils.decorators import login_required
from app.utils.response import success_response
from app.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


def get_current_user_id():
    """从 session 获取当前用户 ID"""
    return session.get('user_id')


@dashboard_bp.route('', methods=['GET'])
@login_required
def get_dashboard():
    # 获取仪表盘数据
    # 从 g 获取当前用户（由 login_required 装饰器设置）
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()
    user = User.query.get(user_id)

    # 基础计数
    asset_count = Asset.query.count()
    consumable_count = Consumable.query.count()

    # 用户相关数据
    my_borrows = BorrowRecord.query.filter_by(borrower_id=user_id, status='borrowed').count()
    my_requests = PurchaseRequest.query.filter_by(applicant_id=user_id).count()

    # 低库存物品
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

    # 管理员专属数据
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
    # 获取详细统计数据
    # 按状态统计资产
    asset_by_status = db.session.query(
        Asset.status,
        func.count(Asset.id)
    ).group_by(Asset.status).all()
    asset_by_status_data = [
        {'status': status, 'count': count}
        for status, count in asset_by_status
    ]

    # 按类别统计资产
    asset_by_category = db.session.query(
        Category.name,
        func.count(Asset.id)
    ).join(Category).group_by(Category.name).all()
    asset_by_category_data = [
        {'category': name, 'count': count}
        for name, count in asset_by_category
    ]

    # 耗材总价值
    consumable_value = db.session.query(
        func.sum(Consumable.stock * Consumable.price)
    ).scalar() or 0

    # 低库存数量
    low_stock_count = Consumable.query.filter(Consumable.stock < Consumable.min_stock).count()

    # 按状态统计采购申请
    purchase_by_status = db.session.query(
        PurchaseRequest.status,
        func.count(PurchaseRequest.id)
    ).group_by(PurchaseRequest.status).all()
    purchase_by_status_data = [
        {'status': status, 'count': count}
        for status, count in purchase_by_status
    ]

    # 总预算
    total_budget = db.session.query(
        func.sum(PurchaseRequest.estimated_price)
    ).scalar() or 0

    # 活跃借用数
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
