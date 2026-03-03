"""
资产类别管理 API 路由

功能模块：
- 获取类别列表（支持分页）
- 获取类别详情
- 创建类别
- 更新类别
- 删除类别

数据结构：
- 支持树形结构（通过 parent_id 关联父类别）
- 类别名称唯一

权限说明：
- 查询操作：所有登录用户
- 增删改操作：仅管理员
"""
from flask import Blueprint, request
from app.models import Category
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
@login_required
def get_categories():
    """
    获取类别列表（分页）

    Query参数：
        page: 页码（默认1）
        page_size: 每页数量（默认20）

    Returns:
        分页的类别列表
    """
    page, page_size = validate_pagination()

    # 构建查询
    query = Category.query

    # 按名称排序
    query = query.order_by(Category.name)

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典列表
    items = [category.to_dict() for category in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@categories_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """
    获取类别详情

    Args:
        category_id: 类别 ID

    Returns:
        类别详细信息
    """
    category = Category.query.get(category_id)

    if not category:
        return error_response('类别不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=category.to_dict())


@categories_bp.route('', methods=['POST'])
@admin_required
def create_category():
    """
    创建新类别（仅管理员）

    Request Body:
        name: 类别名称（必填）
        parent_id: 父类别 ID（可选）

    Returns:
        创建的类别信息

    技术要点：
        - 类别名称必须唯一
        - 父类别必须存在
    """
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['name'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 检查名称是否已存在
    if Category.query.filter_by(name=data['name']).first():
        return error_response('类别名称已存在', error_code='DUPLICATE_ENTRY')

    # 检查父类别是否存在（如果提供了）
    parent = None
    if data.get('parent_id'):
        parent = Category.query.get(data['parent_id'])
        if not parent:
            return error_response('父类别不存在', error_code='NOT_FOUND', status=404)

    # 创建类别
    category = Category(
        name=data['name'],
        parent_id=data.get('parent_id')
    )

    try:
        from app.extensions import db
        db.session.add(category)
        db.session.commit()

        return success_response(
            message='类别创建成功',
            data={
                'id': category.id,
                'name': category.name
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('创建类别失败', error_code='INTERNAL_ERROR', status=500)


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """
    更新类别（仅管理员）

    Args:
        category_id: 类别 ID

    Request Body:
        name: 类别名称
        parent_id: 父类别 ID

    Returns:
        更新后的类别信息

    技术要点：
        - 父类别不能设置为自己
        - 父类别必须存在
    """
    category = Category.query.get(category_id)

    if not category:
        return error_response('类别不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 更新字段
    if 'name' in data:
        category.name = data['name']
    if 'parent_id' in data:
        if data['parent_id']:
            # 检查父类别是否存在
            parent = Category.query.get(data['parent_id'])
            if not parent:
                return error_response('父类别不存在', error_code='NOT_FOUND', status=404)
            # 检查是否将自己设置为父类别（防止循环引用）
            if data['parent_id'] == category.id:
                return error_response('不能将自己设置为父类别', error_code='INVALID_REFERENCE', status=400)
        category.parent_id = data['parent_id']

    try:
        from app.extensions import db
        db.session.commit()

        return success_response(
            message='类别更新成功',
            data={
                'id': category.id,
                'name': category.name
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('更新类别失败', error_code='INTERNAL_ERROR', status=500)


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """
    删除类别（仅管理员）

    Args:
        category_id: 类别 ID

    Returns:
        空

    技术要点：
        - 如果类别下有关联的资产或耗材，不允许删除
        - 需要先删除或转移这些数据
    """
    category = Category.query.get(category_id)

    if not category:
        return error_response('类别不存在', error_code='NOT_FOUND', status=404)

    # 检查类别是否被使用
    if category.assets.count() > 0 or category.consumables.count() > 0:
        return error_response('该类别下还有资产或耗材，无法删除', error_code='IN_USE', status=400)

    try:
        from app.extensions import db
        db.session.delete(category)
        db.session.commit()

        return success_response(message='类别删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('删除类别失败', error_code='INTERNAL_ERROR', status=500)
