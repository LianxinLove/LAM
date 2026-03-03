"""
供应商管理 API 路由

功能模块：
- 获取供应商列表（支持分页）
- 获取供应商详情
- 创建供应商
- 更新供应商
- 删除供应商

权限说明：
- 查询操作：所有登录用户
- 增删改操作：仅管理员

业务规则：
- 供应商名称必须唯一
- 被资产、耗材或采购单引用的供应商无法删除
"""
from flask import Blueprint, request
from app.models import Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('', methods=['GET'])
@login_required
def get_suppliers():
    """
    获取供应商列表（分页）

    Query参数：
        page: 页码（默认1）
        page_size: 每页数量（默认20）

    Returns:
        分页的供应商列表

    技术要点：
        - 按名称字母顺序排序
    """
    page, page_size = validate_pagination()

    # 构建查询
    query = Supplier.query

    # 按名称排序
    query = query.order_by(Supplier.name)

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典列表
    items = [supplier.to_dict() for supplier in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@login_required
def get_supplier(supplier_id):
    """
    获取供应商详情

    Args:
        supplier_id: 供应商 ID

    Returns:
        供应商详细信息
    """
    supplier = Supplier.query.get(supplier_id)

    if not supplier:
        return error_response('供应商不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=supplier.to_dict())


@suppliers_bp.route('', methods=['POST'])
@admin_required
def create_supplier():
    """
    创建新供应商（仅管理员）

    Request Body:
        name: 供应商名称（必填）
        contact: 联系人（可选）
        phone: 联系电话（可选）
        email: 电子邮箱（可选）
        address: 地址（可选）

    Returns:
        创建的供应商信息

    技术要点：
        - 供应商名称必须唯一
        - 所有可选字段根据业务需求填写
    """
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['name'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 检查名称是否已存在
    if Supplier.query.filter_by(name=data['name']).first():
        return error_response('供应商名称已存在', error_code='DUPLICATE_ENTRY')

    # 创建供应商
    supplier = Supplier(
        name=data['name'],
        contact=data.get('contact'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )

    try:
        from app.extensions import db
        db.session.add(supplier)
        db.session.commit()

        return success_response(
            message='供应商创建成功',
            data={
                'id': supplier.id,
                'name': supplier.name
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('创建供应商失败', error_code='INTERNAL_ERROR', status=500)


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@admin_required
def update_supplier(supplier_id):
    """
    更新供应商（仅管理员）

    Args:
        supplier_id: 供应商 ID

    Request Body:
        name: 供应商名称
        contact: 联系人
        phone: 联系电话
        email: 电子邮箱
        address: 地址

    Returns:
        更新后的供应商信息

    技术要点：
        - 只更新提供的字段
        - 名称修改时需要检查唯一性
    """
    supplier = Supplier.query.get(supplier_id)

    if not supplier:
        return error_response('供应商不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 更新字段
    if 'name' in data:
        # 检查新名称是否与其他供应商重复
        existing = Supplier.query.filter_by(name=data['name']).first()
        if existing and existing.id != supplier_id:
            return error_response('供应商名称已存在', error_code='DUPLICATE_ENTRY')
        supplier.name = data['name']
    if 'contact' in data:
        supplier.contact = data['contact']
    if 'phone' in data:
        supplier.phone = data['phone']
    if 'email' in data:
        supplier.email = data['email']
    if 'address' in data:
        supplier.address = data['address']

    try:
        from app.extensions import db
        db.session.commit()

        return success_response(
            message='供应商更新成功',
            data={
                'id': supplier.id,
                'name': supplier.name
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('更新供应商失败', error_code='INTERNAL_ERROR', status=500)


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@admin_required
def delete_supplier(supplier_id):
    """
    删除供应商（仅管理员）

    Args:
        supplier_id: 供应商 ID

    Returns:
        空

    技术要点：
        - 被资产、耗材或采购单引用的供应商无法删除
        - 需要先解除关联关系
    """
    supplier = Supplier.query.get(supplier_id)

    if not supplier:
        return error_response('供应商不存在', error_code='NOT_FOUND', status=404)

    # 检查供应商是否被使用
    if (supplier.assets.count() > 0 or
        supplier.consumables.count() > 0 or
        supplier.purchase_requests.count() > 0):
        return error_response(
            '该供应商已被使用，无法删除',
            error_code='IN_USE',
            status=400
        )

    try:
        from app.extensions import db
        db.session.delete(supplier)
        db.session.commit()

        return success_response(message='供应商删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('删除供应商失败', error_code='INTERNAL_ERROR', status=500)
