# 耗材管理 API 路由
from flask import Blueprint, request
from app.models import Consumable, Category, Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import (
    validate_required_fields,
    validate_pagination,
    validate_stock_fields,
    validate_price_field,
    validate_positive_integer
)

consumables_bp = Blueprint('consumables', __name__)


@consumables_bp.route('', methods=['GET'])
@login_required
def get_consumables():
    # 获取耗材列表（支持过滤和分页）
    # 获取查询参数
    category_id = request.args.get('category_id', type=int)
    low_stock = request.args.get('low_stock', type=bool)
    page, page_size = validate_pagination()

    # 构建查询
    query = Consumable.query

    # 应用过滤条件
    if category_id:
        query = query.filter_by(category_id=category_id)
    if low_stock:
        query = query.filter(Consumable.stock < Consumable.min_stock)

    # 按创建时间降序排列
    query = query.order_by(Consumable.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [consumable.to_dict() for consumable in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)


@consumables_bp.route('/<int:consumable_id>', methods=['GET'])
@login_required
def get_consumable(consumable_id):
    # 获取耗材详情
    consumable = Consumable.query.get(consumable_id)

    if not consumable:
        return error_response('耗材不存在', error_code='NOT_FOUND', status=404)
    
    return success_response(data=consumable.to_dict())


@consumables_bp.route('', methods=['POST'])
@admin_required
def create_consumable():
    # 创建新耗材（仅管理员）
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['name', 'category_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证库存字段
    is_valid, error_msg = validate_stock_fields(data)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证价格字段
    is_valid, error_msg, price = validate_price_field(data, 'price', required=False)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 检查类别是否存在
    category = Category.query.get(data['category_id'])
    if not category:
        return error_response('类别不存在', error_code='NOT_FOUND', status=404)

    # 检查供应商是否存在（如果提供）
    supplier = None
    if data.get('supplier_id'):
        supplier = Supplier.query.get(data['supplier_id'])
        if not supplier:
            return error_response('供应商不存在', error_code='NOT_FOUND', status=404)

    # 生成耗材编码（CON-XXXX 格式）
    from app.extensions import db
    last_consumable = Consumable.query.order_by(Consumable.id.desc()).first()
    if last_consumable:
        last_id = last_consumable.id
    else:
        last_id = 0
    code = f"CON-{last_id + 1:04d}"

    # 创建耗材
    consumable = Consumable(
        name=data['name'],
        code=code,
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        unit=data.get('unit', '个'),
        stock=data.get('stock', 0),
        min_stock=data.get('min_stock', 10),
        price=price,
        location=data.get('location')
    )

    try:
        db.session.add(consumable)
        db.session.commit()

        return success_response(
            message='耗材创建成功',
            data={
                'id': consumable.id,
                'name': consumable.name,
                'code': consumable.code
            },
            status=201
        )
    except Exception as e:
        import traceback
        db.session.rollback()
        print(f"Consumable creation error: {e}")
        print(f"Request data: {data}")
        print(traceback.format_exc())
        return error_response(f'耗材创建失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@consumables_bp.route('/<int:consumable_id>', methods=['PUT'])
@admin_required
def update_consumable(consumable_id):
    # 更新耗材（仅管理员）
    consumable = Consumable.query.get(consumable_id)

    if not consumable:
        return error_response('耗材不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 验证库存字段（如果提供）
    is_valid, error_msg = validate_stock_fields(data)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证价格字段（如果提供）
    if 'price' in data:
        is_valid, error_msg, price = validate_price_field(data, 'price', required=False)
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        consumable.price = price

    # 更新字段
    if 'name' in data:
        consumable.name = data['name']
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return error_response('类别不存在', error_code='NOT_FOUND', status=404)
        consumable.category_id = data['category_id']
    if 'supplier_id' in data:
        if data['supplier_id']:
            supplier = Supplier.query.get(data['supplier_id'])
            if not supplier:
                return error_response('供应商不存在', error_code='NOT_FOUND', status=404)
        consumable.supplier_id = data['supplier_id']
    if 'unit' in data:
        consumable.unit = data['unit']
    if 'stock' in data:
        is_valid, error_msg, validated_stock = validate_positive_integer(
            data['stock'], '当前库存', allow_zero=True
        )
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        consumable.stock = validated_stock
    if 'min_stock' in data:
        is_valid, error_msg, validated_min_stock = validate_positive_integer(
            data['min_stock'], '最低库存', allow_zero=True
        )
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        consumable.min_stock = validated_min_stock
    if 'location' in data:
        consumable.location = data['location']

    try:
        from app.extensions import db
        db.session.commit()

        return success_response(
            message='耗材更新成功',
            data={
                'id': consumable.id,
                'name': consumable.name
            }
        )
    except Exception as e:
        import traceback
        from app.extensions import db
        db.session.rollback()
        print(f"Consumable update error: {e}")
        print(traceback.format_exc())
        return error_response(f'耗材更新失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@consumables_bp.route('/<int:consumable_id>', methods=['DELETE'])
@admin_required
def delete_consumable(consumable_id):
    # 删除耗材（仅管理员）
    consumable = Consumable.query.get(consumable_id)

    if not consumable:
        return error_response('耗材不存在', error_code='NOT_FOUND', status=404)
    
    try:
        from app.extensions import db
        db.session.delete(consumable)
        db.session.commit()
        
        return success_response(message='耗材删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('耗材删除失败', error_code='INTERNAL_ERROR', status=500)
