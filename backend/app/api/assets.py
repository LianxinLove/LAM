# 资产管理 API 路由
from flask import Blueprint, request, session, g
from datetime import datetime
from app.models import Asset, Category, Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import (
    validate_required_fields,
    validate_pagination,
    validate_price_field
)


def parse_date(date_string):
    # 将日期字符串解析为日期对象
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

assets_bp = Blueprint('assets', __name__)


@assets_bp.route('', methods=['GET'])
@login_required
def get_assets():
    # 获取资产列表（支持过滤和分页）
    # 获取查询参数
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    page, page_size = validate_pagination()

    # 构建查询
    query = Asset.query

    # 应用过滤条件
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)

    # 按创建时间降序排列
    query = query.order_by(Asset.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [asset.to_dict() for asset in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@assets_bp.route('/<int:asset_id>', methods=['GET'])
@login_required
def get_asset(asset_id):
    # 获取资产详情
    asset = Asset.query.get(asset_id)

    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=asset.to_dict(include_details=True))


@assets_bp.route('', methods=['POST'])
@admin_required
def create_asset():
    # 创建新资产（仅管理员）
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['name', 'code', 'category_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证采购价格（如果提供）
    purchase_price = None
    if 'purchase_price' in data and data['purchase_price'] is not None:
        is_valid, error_msg, purchase_price = validate_price_field(data, 'purchase_price', required=False)
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 检查编码是否已存在
    if Asset.query.filter_by(code=data['code']).first():
        return error_response('资产编码已存在', error_code='DUPLICATE_ENTRY')

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

    # 获取保管人名称（简单字符串，无需验证）
    custodian = data.get('custodian')

    # 创建资产
    asset = Asset(
        name=data['name'],
        code=data['code'],
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        specifications=data.get('specifications'),
        purchase_date=parse_date(data.get('purchase_date')),
        purchase_price=purchase_price,
        status=data.get('status', 'available'),
        location=data.get('location'),
        custodian=custodian,
        remarks=data.get('remarks')
    )

    try:
        from app.extensions import db
        db.session.add(asset)
        db.session.commit()

        return success_response(
            message='资产创建成功',
            data={
                'id': asset.id,
                'name': asset.name,
                'code': asset.code
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        # 记录实际错误用于调试
        print(f"Asset creation error: {e}")
        print(f"Request data: {data}")
        print(traceback.format_exc())
        return error_response(f'资产创建失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@assets_bp.route('/<int:asset_id>', methods=['PUT'])
@admin_required
def update_asset(asset_id):
    # 更新资产（仅管理员）
    asset = Asset.query.get(asset_id)

    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 更新字段
    if 'name' in data:
        asset.name = data['name']
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return error_response('类别不存在', error_code='NOT_FOUND', status=404)
        asset.category_id = data['category_id']
    if 'supplier_id' in data:
        if data['supplier_id']:
            supplier = Supplier.query.get(data['supplier_id'])
            if not supplier:
                return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
        asset.supplier_id = data['supplier_id']
    if 'specifications' in data:
        asset.specifications = data['specifications']
    if 'purchase_date' in data:
        asset.purchase_date = parse_date(data['purchase_date'])
    if 'purchase_price' in data:
        if data['purchase_price'] is not None:
            is_valid, error_msg, purchase_price = validate_price_field(data, 'purchase_price', required=False)
            if not is_valid:
                return error_response(error_msg, error_code='VALIDATION_ERROR')
            asset.purchase_price = purchase_price
        else:
            asset.purchase_price = None
    if 'status' in data:
        asset.status = data['status']
    if 'location' in data:
        asset.location = data['location']
    if 'custodian' in data:
        asset.custodian = data['custodian']
    if 'remarks' in data:
        asset.remarks = data['remarks']

    try:
        from app.extensions import db
        db.session.commit()

        return success_response(
            message='资产更新成功',
            data={
                'id': asset.id,
                'name': asset.name
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('资产更新失败', error_code='INTERNAL_ERROR', status=500)


@assets_bp.route('/<int:asset_id>', methods=['DELETE'])
@admin_required
def delete_asset(asset_id):
    # 删除资产（仅管理员）
    asset = Asset.query.get(asset_id)

    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    try:
        from app.extensions import db
        db.session.delete(asset)
        db.session.commit()

        return success_response(message='资产删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('资产删除失败', error_code='INTERNAL_ERROR', status=500)
