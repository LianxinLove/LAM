# 认证相关 API 路由
#
# 认证方式：Session-Cookie
#
# 功能模块：
# - 用户注册
# - 用户登录
# - 获取当前用户信息
# - 用户登出

from flask import Blueprint, request, session, g
from app.models import User
from app.utils.decorators import login_required
from app.utils.response import success_response, error_response
from app.utils.validators import validate_required_fields

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    # 用户注册
    #
    # 请求体：
    #     username: 用户名（必填）
    #     password: 密码（必填）
    #     email: 邮箱（可选）
    #
    # Returns:
    #     注册成功后自动登录，创建会话
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['username', 'password'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return error_response('用户名已存在', error_code='DUPLICATE_ENTRY')

    # 检查邮箱是否已存在
    if email and User.query.filter_by(email=email).first():
        return error_response('邮箱已被使用', error_code='DUPLICATE_ENTRY')

    # 创建新用户
    user = User(username=username, email=email)
    user.set_password(password)

    try:
        from app.extensions import db
        db.session.add(user)
        db.session.commit()

        # 注册成功后自动登录，将用户 ID 存入 session
        session['user_id'] = user.id
        session.permanent = True  # 启用持久化会话

        return success_response(
            message='注册成功',
            data={
                'user_id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('注册失败', error_code='INTERNAL_ERROR', status=500)


@auth_bp.route('/login', methods=['POST'])
def login():
    # 用户登录
    #
    # 请求体：
    #     username: 用户名
    #     password: 密码
    #
    # Returns:
    #     登录成功后创建会话，通过 Cookie 返回 session_id
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['username', 'password'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    username = data.get('username')
    password = data.get('password')

    # 查找用户
    user = User.query.filter_by(username=username).first()

    # 验证密码
    if not user or not user.check_password(password):
        return error_response('用户名或密码错误', error_code='INVALID_CREDENTIALS', status=401)

    # 检查用户是否激活
    if not user.is_active:
        return error_response('账户已被禁用', error_code='ACCOUNT_INACTIVE', status=403)

    # 登录成功，将用户 ID 存入 session
    session['user_id'] = user.id
    session.permanent = True  # 启用持久化会话

    return success_response(
        message='登录成功',
        data={
            'user_id': user.id,
            'username': user.username,
            'is_superuser': user.is_superuser
        }
    )


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    # 获取当前登录用户信息
    #
    # Returns:
    #     当前用户的详细信息
    #
    # 技术要点：
    #     - @login_required 装饰器验证会话
    #     - 从 g.current_user 获取用户对象
    user = g.get('current_user')

    if not user:
        return error_response('用户不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=user.to_dict())


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    # 用户登出
    #
    # Returns:
    #     登出成功
    #
    # 技术要点：
    #     - 清除服务端 session
    #     - 前端 Cookie 中的 session_id 会被浏览器自动清理（过期后）
    #     - 设置 session 为过期状态
    # 清除 session 中的用户信息
    session.pop('user_id', None)
    session.clear()  # 完全清除 session

    return success_response(message='登出成功')
