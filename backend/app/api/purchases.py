# 采购申请管理 API 路由
from flask import Blueprint, request, session, g
from datetime import datetime
from app.models import PurchaseRequest, Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

purchases_bp = Blueprint('purchases', __name__)


def get_current_user_id():
    """从 session 获取当前用户 ID"""
    return session.get('user_id')


@purchases_bp.route('', methods=['GET'])
@login_required
def get_purchases():
    # 获取采购申请列表（支持过滤和分页）
    # 获取查询参数
    status = request.args.get('status')
    applicant_id = request.args.get('applicant_id', type=int)
    page, page_size = validate_pagination()

    # 构建查询
    query = PurchaseRequest.query

    # 应用过滤条件
    if status:
        query = query.filter_by(status=status)
    if applicant_id:
        query = query.filter_by(applicant_id=applicant_id)

    # 按创建时间降序排列
    query = query.order_by(PurchaseRequest.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [purchase.to_dict() for purchase in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@purchases_bp.route('/<int:request_id>', methods=['GET'])
@login_required
def get_purchase(request_id):
    # 获取采购申请详情
    purchase = PurchaseRequest.query.get(request_id)

    if not purchase:
        return error_response('采购申请不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=purchase.to_dict())


@purchases_bp.route('', methods=['POST'])
@login_required
def create_purchase():
    # 创建采购申请
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['title', 'item_name', 'quantity', 'estimated_price', 'reason'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 检查供应商是否存在（如果提供）
    supplier = None
    if data.get('supplier_id'):
        supplier = Supplier.query.get(data['supplier_id'])
        if not supplier:
            return error_response('供应商不存在', error_code='NOT_FOUND', status=404)

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 创建采购申请
    purchase = PurchaseRequest(
        title=data['title'],
        applicant_id=user_id,
        item_name=data['item_name'],
        quantity=data['quantity'],
        estimated_price=data['estimated_price'],
        supplier_id=data.get('supplier_id'),
        reason=data['reason'],
        status='pending'
    )

    try:
        from app.extensions import db
        db.session.add(purchase)
        db.session.commit()

        return success_response(
            message='采购申请已提交',
            data={
                'id': purchase.id,
                'status': purchase.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('采购申请创建失败', error_code='INTERNAL_ERROR', status=500)


@purchases_bp.route('/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_purchase(request_id):
    # 批准或拒绝采购申请（仅管理员）
    purchase = PurchaseRequest.query.get(request_id)

    if not purchase:
        return error_response('采购申请不存在', error_code='NOT_FOUND', status=404)

    if purchase.status != 'pending':
        return error_response('采购申请已处理', error_code='INVALID_STATUS', status=400)

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
            purchase.status = 'approved'
            purchase.approver_id = user_id
            purchase.approved_at = datetime.utcnow()
            message = '采购申请已批准'
        else:
            purchase.status = 'rejected'
            purchase.approver_id = user_id
            message = '采购申请已拒绝'

        db.session.commit()

        return success_response(
            message=message,
            data={
                'id': purchase.id,
                'status': purchase.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('采购申请处理失败', error_code='INTERNAL_ERROR', status=500)
