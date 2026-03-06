# 耗材管理 API 路由
from flask import Blueprint, request
from datetime import datetime
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


def parse_date(date_string):
    """将日期字符串解析为日期对象"""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


consumables_bp = Blueprint('consumables', __name__)


@consumables_bp.route('', methods=['GET'])
@login_required
def get_consumables():
    """获取耗材列表（支持过滤和分页）"""
    # 获取查询参数
    category_id = request.args.get('category_id', type=int)
    consumable_type = request.args.get('consumable_type')  # consumable/reagent
    low_stock = request.args.get('low_stock', type=bool)
    is_expired = request.args.get('is_expired', type=bool)
    page, page_size = validate_pagination()

    # 构建查询
    query = Consumable.query

    # 应用过滤条件
    if category_id:
        query = query.filter_by(category_id=category_id)
    if consumable_type:
        query = query.filter_by(consumable_type=consumable_type)
    if low_stock:
        query = query.filter(Consumable.stock < Consumable.min_stock)
    if is_expired:
        from datetime import date
        query = query.filter(Consumable.expiration_date < date.today())

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
    """获取耗材详情"""
    consumable = Consumable.query.get(consumable_id)

    if not consumable:
        return error_response('耗材不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=consumable.to_dict())


@consumables_bp.route('', methods=['POST'])
@admin_required
def create_consumable():
    """创建新耗材（仅管理员）"""
    data = request.get_json()

    # 验证必填字段
    required_fields = ['name', 'category_id', 'product_code', 'custodian_name', 'custodian_phone']
    is_valid, error_msg = validate_required_fields(data, required_fields)
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

    # 验证耗材类型
    consumable_type = data.get('consumable_type', Consumable.TYPE_CONSUMABLE)
    if consumable_type not in [Consumable.TYPE_CONSUMABLE, Consumable.TYPE_REAGENT]:
        return error_response('耗材类型无效', error_code='VALIDATION_ERROR')

    # 验证形态
    form = data.get('form')
    if form and form not in [Consumable.FORM_SOLID, Consumable.FORM_LIQUID, Consumable.FORM_GAS]:
        return error_response('形态无效', error_code='VALIDATION_ERROR')

    # 生成耗材编码（CON-XXXX 格式）
    from app.extensions import db
    last_consumable = Consumable.query.order_by(Consumable.id.desc()).first()
    if last_consumable:
        last_id = last_consumable.id
    else:
        last_id = 0
    code = f"CON-{last_id + 1:04d}"

    # 计算是否过期
    expiration_date = parse_date(data.get('expiration_date'))
    is_expired = False
    if expiration_date:
        from datetime import date
        is_expired = expiration_date < date.today()

    # 创建耗材
    consumable = Consumable(
        name=data['name'],
        code=code,
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        brand=data.get('brand'),
        product_code=data['product_code'],
        cas_number=data.get('cas_number'),
        form=form,
        consumable_type=consumable_type,
        is_hazardous=data.get('is_hazardous', False),
        specifications=data.get('specifications'),
        stock=data.get('stock', 0),
        min_stock=data.get('min_stock', 10),
        custodian_name=data['custodian_name'],
        custodian_phone=data['custodian_phone'],
        production_date=parse_date(data.get('production_date')),
        expiration_date=expiration_date,
        is_expired=is_expired,
        storage_area=data.get('storage_area'),
        room=data.get('room'),
        building=data.get('building'),
        campus=data.get('campus'),
        price=price,
        remarks=data.get('remarks')
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
    """更新耗材（仅管理员）"""
    consumable = Consumable.query.get(consumable_id)

    if not consumable:
        return error_response('耗材不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 可更新的字段列表
    updatable_fields = [
        'name', 'category_id', 'supplier_id', 'brand', 'product_code',
        'cas_number', 'form', 'consumable_type', 'is_hazardous',
        'specifications', 'custodian_name', 'custodian_phone',
        'storage_area', 'room', 'building', 'campus', 'remarks'
    ]

    # 更新字段
    for field in updatable_fields:
        if field in data:
            if field == 'category_id':
                category = Category.query.get(data[field])
                if not category:
                    return error_response('类别不存在', error_code='NOT_FOUND', status=404)
            if field == 'supplier_id':
                if data[field]:
                    supplier = Supplier.query.get(data[field])
                    if not supplier:
                        return error_response('供应商不存在', error_code='NOT_FOUND', status=404)
            if field == 'consumable_type' and data[field] not in [Consumable.TYPE_CONSUMABLE, Consumable.TYPE_REAGENT]:
                return error_response('耗材类型无效', error_code='VALIDATION_ERROR')
            if field == 'form' and data[field] and data[field] not in [Consumable.FORM_SOLID, Consumable.FORM_LIQUID, Consumable.FORM_GAS]:
                return error_response('形态无效', error_code='VALIDATION_ERROR')

            setattr(consumable, field, data[field])

    # 处理日期字段
    for date_field in ['production_date', 'expiration_date']:
        if date_field in data:
            setattr(consumable, date_field, parse_date(data[date_field]))

    # 更新过期状态
    if 'expiration_date' in data:
        from datetime import date
        if consumable.expiration_date and consumable.expiration_date < date.today():
            consumable.is_expired = True
        else:
            consumable.is_expired = False

    # 验证库存字段（如果提供）
    is_valid, error_msg = validate_stock_fields(data)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

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

    # 验证价格字段（如果提供）
    if 'price' in data:
        is_valid, error_msg, price = validate_price_field(data, 'price', required=False)
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        consumable.price = price

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
    """删除耗材（仅管理员）"""
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
