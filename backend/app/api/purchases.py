# 采购申请管理 API 路由
from flask import Blueprint, request, session, g
from datetime import datetime, date
from app.models import PurchaseRequest, Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import (
    validate_required_fields,
    validate_pagination,
    validate_quantity_field,
    validate_price_field
)


def parse_date(date_string):
    """将日期字符串解析为日期对象"""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def get_current_user_id():
    """从 session 获取当前用户 ID"""
    return session.get('user_id')


purchases_bp = Blueprint('purchases', __name__)


@purchases_bp.route('', methods=['GET'])
@login_required
def get_purchases():
    """获取采购申请列表（支持过滤和分页）"""
    # 获取查询参数
    status = request.args.get('status')
    applicant_id = request.args.get('applicant_id', type=int)
    my_applications = request.args.get('my', type=bool)  # 获取我的申请
    page, page_size = validate_pagination()

    # 构建查询
    query = PurchaseRequest.query

    # 应用过滤条件
    if status:
        query = query.filter_by(status=status)
    if applicant_id:
        query = query.filter_by(applicant_id=applicant_id)
    if my_applications and g.user:
        query = query.filter_by(applicant_id=g.user.id)

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
    """获取采购申请详情"""
    purchase = PurchaseRequest.query.get(request_id)

    if not purchase:
        return error_response('采购申请不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=purchase.to_dict())


@purchases_bp.route('', methods=['POST'])
@login_required
def create_purchase():
    """创建采购申请"""
    data = request.get_json()

    # 验证必填字段
    required_fields = [
        'product_name', 'product_code', 'quantity',
        'purpose', 'project_name', 'delivery_info'
    ]
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证数量字段（必须为正整数）
    is_valid, error_msg, quantity = validate_quantity_field(data, 'quantity', required=True)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证价格字段（如果提供）
    query_price = None
    if 'query_price' in data and data['query_price'] is not None:
        is_valid, error_msg, query_price = validate_price_field(data, 'query_price', required=False)
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')

    order_price = None
    if 'order_price' in data and data['order_price'] is not None:
        is_valid, error_msg, order_price = validate_price_field(data, 'order_price', required=False)
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 生成序号
    from app.extensions import db
    last_purchase = PurchaseRequest.query.order_by(PurchaseRequest.id.desc()).first()
    if last_purchase and last_purchase.sequence_number:
        sequence_number = last_purchase.sequence_number + 1
    else:
        sequence_number = 1

    # 创建采购申请
    purchase = PurchaseRequest(
        sequence_number=sequence_number,
        product_name=data['product_name'],
        brand=data.get('brand'),
        product_code=data['product_code'],
        cas_number=data.get('cas_number'),
        form=data.get('form'),
        specifications=data.get('specifications'),
        quantity=quantity,
        purpose=data['purpose'],
        applicant_id=user_id,
        project_name=data['project_name'],
        application_date=date.today(),
        delivery_info=data['delivery_info'],
        query_price=query_price,
        order_price=order_price,
        order_quantity=data.get('order_quantity'),
        delivery_date=parse_date(data.get('delivery_date')),
        delivery_quantity=data.get('delivery_quantity'),
        campus=data.get('campus'),
        building=data.get('building'),
        room=data.get('room'),
        is_hazardous_platform=data.get('is_hazardous_platform', False),
        is_institute_center=data.get('is_institute_center', False),
        is_school_warehouse=data.get('is_school_warehouse', False),
        quality_issue_info=data.get('quality_issue_info'),
        remarks=data.get('remarks'),
        status=PurchaseRequest.STATUS_PENDING
    )

    try:
        db.session.add(purchase)
        db.session.commit()

        return success_response(
            message='采购申请已提交',
            data={
                'id': purchase.id,
                'sequence_number': purchase.sequence_number,
                'status': purchase.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        print(f"Purchase creation error: {e}")
        print(f"Request data: {data}")
        print(traceback.format_exc())
        return error_response(f'采购申请创建失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@purchases_bp.route('/<int:request_id>', methods=['PUT'])
@login_required
def update_purchase(request_id):
    """更新采购申请（仅申请人或管理员）"""
    purchase = PurchaseRequest.query.get(request_id)

    if not purchase:
        return error_response('采购申请不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    # 检查权限：只有申请人或管理员可以编辑
    if purchase.applicant_id != user_id and not (current_user and current_user.is_superuser):
        return error_response('无权编辑此申请', error_code='PERMISSION_DENIED', status=403)

    # 已审批的申请不能修改
    if purchase.status != PurchaseRequest.STATUS_PENDING:
        return error_response('已处理的申请不能修改', error_code='INVALID_OPERATION')

    # 可更新的字段
    updatable_fields = [
        'product_name', 'brand', 'product_code', 'cas_number', 'form',
        'specifications', 'quantity', 'purpose', 'project_name',
        'delivery_info', 'campus', 'building', 'room',
        'is_hazardous_platform', 'is_institute_center', 'is_school_warehouse',
        'quality_issue_info', 'remarks'
    ]

    for field in updatable_fields:
        if field in data:
            setattr(purchase, field, data[field])

    # 处理日期字段
    if 'delivery_date' in data:
        purchase.delivery_date = parse_date(data['delivery_date'])

    # 处理数量字段
    if 'order_quantity' in data:
        purchase.order_quantity = data['order_quantity']
    if 'delivery_quantity' in data:
        purchase.delivery_quantity = data['delivery_quantity']

    # 处理价格字段
    for price_field in ['query_price', 'order_price']:
        if price_field in data:
            if data[price_field] is not None:
                is_valid, error_msg, price = validate_price_field(data, price_field, required=False)
                if not is_valid:
                    return error_response(error_msg, error_code='VALIDATION_ERROR')
                setattr(purchase, price_field, price)
            else:
                setattr(purchase, price_field, None)

    try:
        from app.extensions import db
        db.session.commit()

        return success_response(
            message='采购申请更新成功',
            data={
                'id': purchase.id,
                'status': purchase.status
            }
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        print(f"Purchase update error: {e}")
        print(traceback.format_exc())
        return error_response(f'采购申请更新失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@purchases_bp.route('/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_purchase(request_id):
    """批准或拒绝采购申请（仅管理员）"""
    purchase = PurchaseRequest.query.get(request_id)

    if not purchase:
        return error_response('采购申请不存在', error_code='NOT_FOUND', status=404)

    if purchase.status != PurchaseRequest.STATUS_PENDING:
        return error_response('采购申请已处理', error_code='INVALID_STATUS', status=400)

    data = request.get_json()
    action = data.get('action', 'approve')

    if action not in ['approve', 'reject']:
        return error_response('无效的操作', error_code='VALIDATION_ERROR')

    # 从 g 或 session 获取当前用户 ID
    current_user = g.get('current_user')
    user_id = current_user.id if current_user else get_current_user_id()

    try:
        from app.extensions import db

        if action == 'approve':
            purchase.status = PurchaseRequest.STATUS_APPROVED
            purchase.approver_id = user_id
            purchase.approval_comment = data.get('approval_comment')
            purchase.approved_at = datetime.utcnow()
            message = '采购申请已批准'
        else:
            purchase.status = PurchaseRequest.STATUS_REJECTED
            purchase.approver_id = user_id
            purchase.approval_comment = data.get('approval_comment')
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
        import traceback
        db.session.rollback()
        print(f"Purchase approval error: {e}")
        print(traceback.format_exc())
        return error_response(f'采购申请处理失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)
