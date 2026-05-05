# 用户管理 API 路由
from flask import Blueprint, request, g
from app.models import User
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_pagination

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@login_required
def get_users():
    """获取用户列表（支持分页和搜索）"""
    # 获取查询参数
    search = request.args.get('search', '')  # 用户名搜索
    is_active = request.args.get('is_active')  # 是否激活
    page, page_size = validate_pagination()

    # 构建查询
    query = User.query

    # 搜索过滤
    if search:
        query = query.filter(User.username.ilike(f'%{search}%'))

    # 状态过滤
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)

    # 按创建时间降序排列
    query = query.order_by(User.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [user.to_dict() for user in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get(user_id)

    if not user:
        return error_response('用户不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=user.to_dict())


@users_bp.route('/simple', methods=['GET'])
@login_required
def get_users_simple():
    """获取用户简单列表（用于下拉选择，不分页）"""
    # 获取查询参数
    is_active = request.args.get('is_active', 'true').lower() == 'true'

    # 构建查询
    query = User.query

    # 只返回激活用户
    if is_active:
        query = query.filter_by(is_active=True)

    # 按用户名排序
    query = query.order_by(User.username)

    # 获取所有用户
    users = query.all()

    # 返回简化信息
    items = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        for user in users
    ]

    return success_response(data=items)


@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """更新用户信息（仅管理员）"""
    user = User.query.get(user_id)

    if not user:
        return error_response('用户不存在', error_code='NOT_FOUND', status=404)

    data = request.get_json()

    # 可更新的字段
    updatable_fields = ['email', 'is_active', 'is_superuser']

    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])

    try:
        from app.extensions import db
        db.session.commit()

        return success_response(
            message='用户更新成功',
            data=user.to_dict()
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('用户更新失败', error_code='INTERNAL_ERROR', status=500)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户（仅管理员）"""
    user = User.query.get(user_id)

    if not user:
        return error_response('用户不存在', error_code='NOT_FOUND', status=404)

    # 不允许删除自己
    if g.user and g.user.id == user_id:
        return error_response('不能删除自己', error_code='FORBIDDEN', status=403)

    try:
        from app.extensions import db
        db.session.delete(user)
        db.session.commit()

        return success_response(message='用户删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('用户删除失败', error_code='INTERNAL_ERROR', status=500)
