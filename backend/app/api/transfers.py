# 资产调拨管理 API 路由
from flask import Blueprint, request, session, g
from datetime import datetime
from app.models import AssetTransfer, Asset, User
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

transfers_bp = Blueprint('transfers', __name__)


def get_current_user_id():
    """从 session 获取当前用户 ID"""
    return session.get('user_id')


@transfers_bp.route('', methods=['GET'])
@login_required
def get_transfers():
    """获取调拨申请列表（支持过滤和分页）"""
    status = request.args.get('status')
    applicant_id = request.args.get('applicant_id', type=int)
    page, page_size = validate_pagination()

    # 构建查询
    query = AssetTransfer.query

    # 应用过滤条件
    if status:
        query = query.filter_by(status=status)
    if applicant_id:
        query = query.filter_by(applicant_id=applicant_id)

    # 按创建时间降序排列
    query = query.order_by(AssetTransfer.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [transfer.to_dict() for transfer in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@transfers_bp.route('/<int:transfer_id>', methods=['GET'])
@login_required
def get_transfer_detail(transfer_id):
    """获取调拨申请详情"""
    transfer = AssetTransfer.query.get(transfer_id)

    if not transfer:
        return error_response('调拨申请不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=transfer.to_dict())


@transfers_bp.route('', methods=['POST'])
@login_required
def create_transfer():
    """创建资产调拨申请"""
    data = request.get_json()

    # 验证必填字段
    required_fields = ['asset_id', 'to_campus', 'to_building', 'reason']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 获取资产
    asset = Asset.query.get(data['asset_id'])
    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 创建调拨申请（从资产获取原位置）
    transfer = AssetTransfer(
        asset_id=data['asset_id'],
        from_campus=asset.campus,
        from_building=asset.building,
        from_room=asset.room,
        to_campus=data['to_campus'],
        to_building=data['to_building'],
        to_room=data.get('to_room'),
        reason=data['reason'],
        applicant_id=user_id,
        status='pending'
    )

    try:
        from app.extensions import db
        db.session.add(transfer)
        db.session.commit()

        return success_response(
            message='资产转移申请已提交',
            data={
                'id': transfer.id,
                'status': transfer.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('调拨申请创建失败', error_code='INTERNAL_ERROR', status=500)


@transfers_bp.route('/<int:transfer_id>/approve', methods=['POST'])
@admin_required
def approve_transfer(transfer_id):
    """批准或拒绝调拨申请（仅管理员）"""
    transfer = AssetTransfer.query.get(transfer_id)

    if not transfer:
        return error_response('调拨申请不存在', error_code='NOT_FOUND', status=404)

    if transfer.status != 'pending':
        return error_response('调拨申请已处理', error_code='INVALID_STATUS', status=400)

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
            # 更新资产位置
            if transfer.asset:
                transfer.asset.campus = transfer.to_campus
                transfer.asset.building = transfer.to_building
                transfer.asset.room = transfer.to_room

            transfer.status = 'approved'
            transfer.approver_id = user_id
            transfer.approved_at = datetime.utcnow()

            # 设置接收确认人（如果提供）
            if data.get('receiver_id'):
                receiver = User.query.get(data['receiver_id'])
                if receiver:
                    transfer.receiver_id = data['receiver_id']

            message = '资产转移申请已批准'
        else:
            transfer.status = 'rejected'
            transfer.approver_id = user_id
            message = '资产转移申请已拒绝'

        db.session.commit()

        return success_response(
            message=message,
            data={
                'id': transfer.id,
                'status': transfer.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('调拨申请处理失败', error_code='INTERNAL_ERROR', status=500)


@transfers_bp.route('/my', methods=['GET'])
@login_required
def get_my_transfers():
    """获取当前用户的调拨申请"""
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()
    page, page_size = validate_pagination()

    # 构建查询
    query = AssetTransfer.query.filter_by(applicant_id=user_id)

    # 按创建时间降序排列
    query = query.order_by(AssetTransfer.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [transfer.to_dict() for transfer in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@transfers_bp.route('/<int:transfer_id>/confirm', methods=['POST'])
@login_required
def confirm_transfer(transfer_id):
    """确认接收转移的资产"""
    transfer = AssetTransfer.query.get(transfer_id)

    if not transfer:
        return error_response('调拨申请不存在', error_code='NOT_FOUND', status=404)

    if transfer.status != 'approved':
        return error_response('只能确认已批准的调拨', error_code='INVALID_STATUS', status=400)

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    try:
        from app.extensions import db

        # 设置接收确认人
        transfer.receiver_id = user_id
        db.session.commit()

        return success_response(
            message='已确认接收资产',
            data={'id': transfer.id}
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('确认接收失败', error_code='INTERNAL_ERROR', status=500)
