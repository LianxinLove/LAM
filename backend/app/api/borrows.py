# 资产借用管理 API 路由
from flask import Blueprint, request, session, g
from datetime import datetime
from app.models import BorrowRecord, Asset, User
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

borrows_bp = Blueprint('borrows', __name__)


def get_current_user_id():
    """从 session 获取当前用户 ID"""
    return session.get('user_id')


@borrows_bp.route('', methods=['GET'])
@login_required
def get_borrows():
    # 获取借用记录列表（支持过滤和分页）
    # 获取查询参数
    status = request.args.get('status')
    borrower_id = request.args.get('borrower_id', type=int)
    my = request.args.get('my', False)
    page, page_size = validate_pagination()

    # 从 g 获取当前用户（由 login_required 装饰器设置）
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 构建查询
    query = BorrowRecord.query

    # 应用过滤条件
    if status:
        query = query.filter_by(status=status)
    if borrower_id:
        query = query.filter_by(borrower_id=borrower_id)

    # 如果 'my' 参数为 True，则过滤当前用户
    if my and not (current_user and current_user.is_superuser):
        query = query.filter_by(borrower_id=user_id)

    # 按借用日期降序排列
    query = query.order_by(BorrowRecord.borrow_date.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [borrow.to_dict() for borrow in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@borrows_bp.route('/<int:record_id>', methods=['GET'])
@login_required
def get_borrow(record_id):
    # 获取借用记录详情
    borrow = BorrowRecord.query.get(record_id)

    if not borrow:
        return error_response('借用记录不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=borrow.to_dict())


@borrows_bp.route('', methods=['POST'])
@login_required
def borrow_asset():
    # 借用资产
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['asset_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 获取资产
    asset = Asset.query.get(data['asset_id'])
    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    # 检查资产是否可用
    if not asset.is_available:
        return error_response('资产当前不可借用', error_code='INVALID_STATUS', status=400)

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 创建借用记录
    borrow = BorrowRecord(
        asset_id=data['asset_id'],
        borrower_id=user_id,
        purpose=data.get('purpose'),
        status='borrowed'
    )

    try:
        from app.extensions import db

        # 更新资产状态
        asset.status = 'in_use'

        db.session.add(borrow)
        db.session.commit()

        return success_response(
            message='借用成功',
            data={
                'id': borrow.id,
                'asset': {
                    'id': asset.id,
                    'name': asset.name
                },
                'borrow_date': borrow.borrow_date.isoformat()
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('资产借用失败', error_code='INTERNAL_ERROR', status=500)


@borrows_bp.route('/<int:record_id>/return', methods=['POST'])
@login_required
def return_asset(record_id):
    # 归还借用的资产
    borrow = BorrowRecord.query.get(record_id)

    if not borrow:
        return error_response('借用记录不存在', error_code='NOT_FOUND', status=404)

    # 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 检查记录是否属于当前用户
    if borrow.borrower_id != user_id:
        return error_response('只能归还自己借用的资产', error_code='PERMISSION_DENIED', status=403)

    # 检查是否已归还
    if borrow.status == 'returned':
        return error_response('资产已经归还', error_code='INVALID_STATUS', status=400)

    try:
        from app.extensions import db

        # 更新借用记录
        borrow.return_date = datetime.utcnow()
        borrow.status = 'returned'

        # 更新资产状态
        if borrow.asset:
            borrow.asset.status = 'available'

        db.session.commit()

        return success_response(
            message='归还成功',
            data={
                'id': borrow.id,
                'return_date': borrow.return_date.isoformat(),
                'status': borrow.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('资产归还失败', error_code='INTERNAL_ERROR', status=500)


@borrows_bp.route('/my', methods=['GET'])
@login_required
def get_my_borrows():
    # 获取当前用户的借用记录
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()
    page, page_size = validate_pagination()

    # 构建查询
    query = BorrowRecord.query.filter_by(borrower_id=user_id)

    # 按借用日期降序排列
    query = query.order_by(BorrowRecord.borrow_date.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [borrow.to_dict() for borrow in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)
