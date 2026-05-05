# 仪表盘统计 API 路由
from flask import Blueprint, request, session, g
from datetime import date
from sqlalchemy import func
from app.models import Asset, Consumable, PurchaseRequest, AssetTransfer, PickRecord, BorrowRecord, User
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
    """获取仪表盘数据"""
    # 从 g 获取当前用户（由 login_required 装饰器设置）
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()
    user = db.session.query(User).get(user_id)

    # 基础计数
    asset_count = db.session.query(Asset).count()
    consumable_count = db.session.query(Consumable).count()

    # 用户相关数据
    my_borrows = db.session.query(BorrowRecord).filter_by(borrower_id=user_id, status='borrowed').count()
    my_requests = db.session.query(PurchaseRequest).filter_by(applicant_id=user_id).count()

    # 低库存物品
    low_stock_items = db.session.query(Consumable).filter(
        Consumable.stock < Consumable.min_stock
    ).all()
    low_stock_data = [
        {
            'id': item.id,
            'name': item.name,
            'stock': item.stock,
            'min_stock': item.min_stock
        }
        for item in low_stock_items
    ]

    # 过期耗材
    today = date.today()
    expired_items = db.session.query(Consumable).filter(
        Consumable.expiration_date < today
    ).all()
    expired_data = [
        {
            'id': item.id,
            'name': item.name,
            'expiration_date': item.expiration_date.isoformat() if item.expiration_date else None
        }
        for item in expired_items
    ]

    data = {
        'asset_count': asset_count,
        'consumable_count': consumable_count,
        'my_borrows': my_borrows,
        'my_requests': my_requests,
        'low_stock_items': low_stock_data,
        'expired_items': expired_data
    }

    # 管理员专属数据
    if user and user.is_superuser:
        pending_purchases = db.session.query(PurchaseRequest).filter_by(status='pending').count()
        pending_transfers = db.session.query(AssetTransfer).filter_by(status='pending').count()
        pending_picks = db.session.query(PickRecord).filter_by(status='pending').count()

        data.update({
            'pending_purchases': pending_purchases,
            'pending_transfers': pending_transfers,
            'pending_picks': pending_picks
        })

    return success_response(data=data)


@dashboard_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """获取详细统计数据"""
    # 按状态统计资产（使用正确的字段名 current_status）
    asset_by_status = db.session.query(
        Asset.current_status,
        func.count(Asset.id)
    ).group_by(Asset.current_status).all()
    asset_by_status_data = [
        {'status': status, 'count': count}
        for status, count in asset_by_status
    ]

    # 按类型统计资产（仪器设备/软件）
    asset_by_type = db.session.query(
        Asset.asset_type,
        func.count(Asset.id)
    ).group_by(Asset.asset_type).all()
    asset_by_type_data = [
        {'type': asset_type, 'count': count}
        for asset_type, count in asset_by_type
    ]

    # 按院系统计资产
    asset_by_department = db.session.query(
        Asset.department,
        func.count(Asset.id)
    ).group_by(Asset.department).all()
    asset_by_department_data = [
        {'department': department, 'count': count}
        for department, count in asset_by_department
    ]

    # 按校区统计资产
    asset_by_campus = db.session.query(
        Asset.campus,
        func.count(Asset.id)
    ).group_by(Asset.campus).all()
    asset_by_campus_data = [
        {'campus': campus, 'count': count}
        for campus, count in asset_by_campus
    ]

    # 耗材总价值
    consumable_value = db.session.query(
        func.sum(Consumable.stock * Consumable.price)
    ).scalar() or 0

    # 低库存数量
    low_stock_count = db.session.query(Consumable).filter(
        Consumable.stock < Consumable.min_stock
    ).count()

    # 过期耗材数量
    today = date.today()
    expired_count = db.session.query(Consumable).filter(
        Consumable.expiration_date < today
    ).count()

    # 按状态统计采购申请
    purchase_by_status = db.session.query(
        PurchaseRequest.status,
        func.count(PurchaseRequest.id)
    ).group_by(PurchaseRequest.status).all()
    purchase_by_status_data = [
        {'status': status, 'count': count}
        for status, count in purchase_by_status
    ]

    # 总预算（使用正确的字段名 query_price）
    total_budget = db.session.query(
        func.sum(PurchaseRequest.query_price)
    ).scalar() or 0

    # 活跃借用数
    active_borrows = db.session.query(BorrowRecord).filter_by(status='borrowed').count()

    data = {
        'asset_by_status': asset_by_status_data,
        'asset_by_type': asset_by_type_data,
        'asset_by_department': asset_by_department_data,
        'asset_by_campus': asset_by_campus_data,
        'total_consumable_value': float(consumable_value),
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
        'purchase_by_status': purchase_by_status_data,
        'total_budget': float(total_budget),
        'active_borrows': active_borrows
    }

    return success_response(data=data)
