# 资产管理 API 路由
from flask import Blueprint, request, session, g, Response, current_app
from datetime import datetime
import csv
import io
import os
import uuid
from werkzeug.utils import secure_filename
from app.models import Asset, AssetManagerTransfer, User
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import (
    validate_required_fields,
    validate_pagination,
    validate_price_field
)


# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """
    保存上传的文件并返回URL

    Args:
        file: FileStorage对象

    Returns:
        str: 文件访问URL，如果保存失败则返回None
    """
    if not file or file.filename == '':
        return None

    # 检查文件类型
    if not allowed_file(file.filename):
        return None

    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return None

    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    filename = f"{uuid.uuid4().hex}_{original_filename}"

    # 创建上传目录
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
    os.makedirs(upload_dir, exist_ok=True)

    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    # 返回访问URL
    return f"/uploads/images/{filename}"


def get_form_data():
    """
    获取请求数据，支持JSON和FormData两种格式

    Returns:
        dict: 解析后的数据字典
    """
    content_type = request.content_type or ''

    if 'multipart/form-data' in content_type:
        # FormData格式：使用request.form获取字段，request.files获取文件
        data = dict(request.form)

        # 处理文件字段
        for key in ['photo_full', 'photo_model', 'photo_tag']:
            if key in request.files:
                file = request.files[key]
                file_url = save_uploaded_file(file)
                if file_url:
                    data[f'{key}_url'] = file_url

        # 转换数值字段
        numeric_fields = ['purchase_price', 'manager_id']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    data[field] = float(data[field]) if field == 'purchase_price' else int(data[field])
                except (ValueError, TypeError):
                    pass

        return data
    else:
        # JSON格式
        return request.get_json() or {}


def parse_date(date_string):
    """将日期字符串解析为日期对象"""
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
    """获取资产列表（支持过滤和分页）"""
    # 获取查询参数
    asset_type = request.args.get('asset_type')  # equipment/software
    status = request.args.get('status')
    campus = request.args.get('campus')
    manager_id = request.args.get('manager_id', type=int)
    my_managed = request.args.get('my_managed', type=bool)  # 获取我保管的资产
    page, page_size = validate_pagination()

    # 构建查询
    query = Asset.query

    # 应用过滤条件
    if asset_type:
        query = query.filter_by(asset_type=asset_type)
    if status:
        query = query.filter_by(current_status=status)
    if campus:
        query = query.filter_by(campus=campus)
    if manager_id:
        query = query.filter_by(manager_id=manager_id)
    if my_managed and g.user:
        query = query.filter_by(manager_id=g.user.id)

    # 按创建时间降序排列
    query = query.order_by(Asset.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [asset.to_dict_lite() for asset in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@assets_bp.route('/<int:asset_id>', methods=['GET'])
@login_required
def get_asset(asset_id):
    """获取资产详情"""
    asset = Asset.query.get(asset_id)

    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=asset.to_dict(include_details=True))


@assets_bp.route('', methods=['POST'])
@admin_required
def create_asset():
    """创建新资产（仅管理员）"""
    data = get_form_data()

    # 验证必填字段
    required_fields = [
        'lab_asset_code', 'name', 'asset_type', 'model',
        'department', 'campus', 'building',
        'custodian_name', 'custodian_phone', 'manager_id'
    ]
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证采购价格（如果提供）
    purchase_price = None
    if 'purchase_price' in data and data['purchase_price'] is not None:
        is_valid, error_msg, purchase_price = validate_price_field(data, 'purchase_price', required=False)
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 检查资产编号是否已存在
    if Asset.query.filter_by(lab_asset_code=data['lab_asset_code']).first():
        return error_response('资产编号已存在', error_code='DUPLICATE_ENTRY')

    # 检查学校资产编号是否已存在（如果提供）
    if data.get('school_asset_code'):
        if Asset.query.filter_by(school_asset_code=data['school_asset_code']).first():
            return error_response('学校资产编号已存在', error_code='DUPLICATE_ENTRY')

    # 验证资产管理人是否存在
    manager = User.query.get(data['manager_id'])
    if not manager:
        return error_response('资产管理人不存在', error_code='NOT_FOUND', status=404)

    # 验证资产类型
    if data['asset_type'] not in [Asset.TYPE_EQUIPMENT, Asset.TYPE_SOFTWARE]:
        return error_response('资产类型无效', error_code='VALIDATION_ERROR')

    # 验证资产状态（如果提供）
    current_status = data.get('current_status', Asset.STATUS_IN_USE)
    valid_statuses = [
        Asset.STATUS_IN_USE, Asset.STATUS_SCRAPPED,
        Asset.STATUS_REPAIR, Asset.STATUS_RETURNED, Asset.STATUS_BORROWED
    ]
    if current_status not in valid_statuses:
        return error_response('资产状态无效', error_code='VALIDATION_ERROR')

    # 创建资产
    asset = Asset(
        lab_asset_code=data['lab_asset_code'],
        school_asset_code=data.get('school_asset_code'),
        name=data['name'],
        asset_type=data['asset_type'],
        model=data['model'],
        specifications=data.get('specifications'),
        manufacturer=data.get('manufacturer'),
        purchase_price=purchase_price,
        department=data['department'],
        current_status=current_status,
        campus=data['campus'],
        building=data['building'],
        room=data.get('room'),
        purchase_date=parse_date(data.get('purchase_date')),
        custodian_name=data['custodian_name'],
        custodian_phone=data['custodian_phone'],
        manager_id=data['manager_id'],
        photo_full_url=data.get('photo_full_url'),
        photo_model_url=data.get('photo_model_url'),
        photo_tag_url=data.get('photo_tag_url'),
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
                'lab_asset_code': asset.lab_asset_code
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        print(f"Asset creation error: {e}")
        print(f"Request data: {data}")
        print(traceback.format_exc())
        return error_response(f'资产创建失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@assets_bp.route('/<int:asset_id>', methods=['PUT'])
@admin_required
def update_asset(asset_id):
    """更新资产（仅管理员）"""
    asset = Asset.query.get(asset_id)

    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    data = get_form_data()

    # 可更新的字段列表
    updatable_fields = [
        'lab_asset_code', 'school_asset_code', 'name', 'asset_type',
        'model', 'specifications', 'manufacturer', 'department',
        'current_status', 'campus', 'building', 'room',
        'custodian_name', 'custodian_phone', 'manager_id',
        'photo_full_url', 'photo_model_url', 'photo_tag_url', 'remarks'
    ]

    # 更新字段
    for field in updatable_fields:
        if field in data:
            if field == 'lab_asset_code' and data[field] != asset.lab_asset_code:
                # 检查新编号是否已存在
                if Asset.query.filter_by(lab_asset_code=data[field]).first():
                    return error_response('资产编号已存在', error_code='DUPLICATE_ENTRY')
            if field == 'school_asset_code':
                if data[field] and Asset.query.filter_by(school_asset_code=data[field]).first():
                    return error_response('学校资产编号已存在', error_code='DUPLICATE_ENTRY')
            if field == 'manager_id':
                manager = User.query.get(data[field])
                if not manager:
                    return error_response('资产管理人不存在', error_code='NOT_FOUND', status=404)
            if field == 'asset_type' and data[field] not in [Asset.TYPE_EQUIPMENT, Asset.TYPE_SOFTWARE]:
                return error_response('资产类型无效', error_code='VALIDATION_ERROR')
            if field == 'current_status':
                valid_statuses = [
                    Asset.STATUS_IN_USE, Asset.STATUS_SCRAPPED,
                    Asset.STATUS_REPAIR, Asset.STATUS_RETURNED, Asset.STATUS_BORROWED
                ]
                if data[field] not in valid_statuses:
                    return error_response('资产状态无效', error_code='VALIDATION_ERROR')

            setattr(asset, field, data[field])

    # 处理日期字段
    if 'purchase_date' in data:
        asset.purchase_date = parse_date(data['purchase_date'])

    # 处理价格字段
    if 'purchase_price' in data:
        if data['purchase_price'] is not None:
            is_valid, error_msg, purchase_price = validate_price_field(data, 'purchase_price', required=False)
            if not is_valid:
                return error_response(error_msg, error_code='VALIDATION_ERROR')
            asset.purchase_price = purchase_price
        else:
            asset.purchase_price = None

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
    """删除资产（仅管理员）"""
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


@assets_bp.route('/<int:asset_id>/transfer-manager', methods=['POST'])
@login_required
def transfer_asset_manager(asset_id):
    """资产管理人交接"""
    asset = Asset.query.get(asset_id)

    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    data = get_form_data()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['new_manager_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证新管理人是否存在
    new_manager = User.query.get(data['new_manager_id'])
    if not new_manager:
        return error_response('新管理人不存在', error_code='NOT_FOUND', status=404)

    # 记录原管理人
    old_manager_id = asset.manager_id

    try:
        from app.extensions import db

        # 创建交接记录
        transfer = AssetManagerTransfer(
            asset_id=asset.id,
            old_manager_id=old_manager_id,
            new_manager_id=data['new_manager_id'],
            transfer_reason=data.get('transfer_reason'),
            remarks=data.get('remarks'),
            created_by_id=g.user.id
        )

        # 更新资产的管理人
        asset.manager_id = data['new_manager_id']

        db.session.add(transfer)
        db.session.commit()

        return success_response(
            message='资产管理人交接成功',
            data={
                'id': transfer.id,
                'old_manager_id': old_manager_id,
                'new_manager_id': data['new_manager_id']
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('资产管理人交接失败', error_code='INTERNAL_ERROR', status=500)


@assets_bp.route('/export', methods=['GET'])
@admin_required
def export_assets():
    """导出资产数据为CSV文件（仅管理员）"""
    # 获取所有资产
    assets = Asset.query.order_by(Asset.id).all()

    # 创建CSV文件
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头（UTF-8 BOM for Excel compatibility）
    headers = [
        '序号', '课题组资产编号', '学校资产编号', '名称', '型号', '规格',
        '生产厂家', '价格', '院系归属', '存放位置', '资产现状',
        '购买日期', '课题组保管人姓名', '课题组保管人联系电话', '备注'
    ]
    writer.writerow(headers)

    # 写入数据行
    for idx, asset in enumerate(assets, 1):
        # 组合存放位置
        location = f"{asset.campus} {asset.building}"
        if asset.room:
            location += f" {asset.room}"

        # 资产状态中文映射
        status_map = {
            'in_use': '在用',
            'scrapped': '报废',
            'repair': '报修',
            'returned': '退库',
            'borrowed': '外借'
        }

        writer.writerow([
            idx,
            asset.lab_asset_code or '',
            asset.school_asset_code or '',
            asset.name or '',
            asset.model or '',
            asset.specifications or '',
            asset.manufacturer or '',
            float(asset.purchase_price) if asset.purchase_price else '',
            asset.department or '',
            location,
            status_map.get(asset.current_status, asset.current_status),
            asset.purchase_date.isoformat() if asset.purchase_date else '',
            asset.custodian_name or '',
            asset.custodian_phone or '',
            asset.remarks or ''
        ])

    # 创建响应
    output.seek(0)
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=assets_export.csv'
        }
    )

    # 添加UTF-8 BOM以便Excel正确显示中文
    response.data = '\ufeff'.encode('utf-8') + output.getvalue().encode('utf-8')

    return response
