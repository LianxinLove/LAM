# 耗材领用管理 API 路由
from flask import Blueprint, request, session, g
from datetime import datetime
from app.models import PickRecord, Consumable
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

picks_bp = Blueprint('picks', __name__)


def get_current_user_id():
    """从 session 获取当前用户 ID"""
    return session.get('user_id')


@picks_bp.route('', methods=['GET'])
@login_required
def get_picks():
    # 获取领用记录列表（支持过滤和分页）
    # 获取查询参数
    status = request.args.get('status')
    picker_id = request.args.get('picker_id', type=int)
    page, page_size = validate_pagination()

    # 构建查询
    query = PickRecord.query

    # 应用过滤条件
    if status:
        query = query.filter_by(status=status)
    if picker_id:
        query = query.filter_by(picker_id=picker_id)

    # 按创建时间降序排列
    query = query.order_by(PickRecord.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [pick.to_dict() for pick in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@picks_bp.route('/<int:pick_id>', methods=['GET'])
@login_required
def get_pick_detail(pick_id):
    # 获取领用记录详情
    pick = PickRecord.query.get(pick_id)

    if not pick:
        return error_response('领用申请不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=pick.to_dict())


@picks_bp.route('', methods=['POST'])
@login_required
def create_pick():
    # 创建领用申请
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['item_id', 'quantity'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 获取耗材
    consumable = Consumable.query.get(data['item_id'])
    if not consumable:
        return error_response('耗材不存在', error_code='NOT_FOUND', status=404)

    # 检查库存是否充足
    if consumable.stock < data['quantity']:
        return error_response('库存不足', error_code='INSUFFICIENT_STOCK', status=400)

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 创建领用记录
    pick = PickRecord(
        item_id=data['item_id'],
        picker_id=user_id,
        quantity=data['quantity'],
        purpose=data.get('purpose'),
        status='pending'
    )

    try:
        from app.extensions import db
        db.session.add(pick)
        db.session.commit()

        return success_response(
            message='领料申请已提交',
            data={
                'id': pick.id,
                'status': pick.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('领用申请创建失败', error_code='INTERNAL_ERROR', status=500)


@picks_bp.route('/<int:pick_id>/approve', methods=['POST'])
@admin_required
def approve_pick(pick_id):
    # 批准或拒绝领用申请（仅管理员）
    pick = PickRecord.query.get(pick_id)

    if not pick:
        return error_response('领用申请不存在', error_code='NOT_FOUND', status=404)

    if pick.status != 'pending':
        return error_response('领用申请已处理', error_code='INVALID_STATUS', status=400)

    data = request.get_json()
    action = data.get('action')

    if action not in ['approve', 'reject']:
        return error_response('无效的操作', error_code='VALIDATION_ERROR')

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    try:
        from app.extensions import db

        if action == 'approve':
            # 检查库存是否充足
            if pick.item.stock < pick.quantity:
                return error_response('库存不足', error_code='INSUFFICIENT_STOCK', status=400)

            # 扣除库存
            pick.item.stock -= pick.quantity

            pick.status = 'approved'
            pick.approver_id = user_id
            pick.approved_at = datetime.utcnow()
            message = '领料申请已批准'
        else:
            pick.status = 'rejected'
            pick.approver_id = user_id
            message = '领料申请已拒绝'

        db.session.commit()

        return success_response(
            message=message,
            data={
                'id': pick.id,
                'status': pick.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('领用申请处理失败', error_code='INTERNAL_ERROR', status=500)


@picks_bp.route('/my', methods=['GET'])
@login_required
def get_my_picks():
    # 获取当前用户的领用记录
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()
    page, page_size = validate_pagination()

    # 构建查询
    query = PickRecord.query.filter_by(picker_id=user_id)

    # 按创建时间降序排列
    query = query.order_by(PickRecord.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [pick.to_dict() for pick in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)
