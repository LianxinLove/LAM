# 自定义装饰器用于认证和授权
#
# 认证方式：Session-Cookie
# - 从 session 中获取用户 ID
# - 验证用户登录状态和权限
from functools import wraps
from flask import session, g
from app.models import User
from app.utils.response import error_response


def login_required(f):
    """
    登录验证装饰器
    #
    # 要求用户必须已登录，否则返回 401 错误
    #
    # 技术要点：
    # - 从 session 中获取 user_id
    # - session 由后端管理，前端通过 Cookie 自动携带
    # - 验证失败返回 401 状态码
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从 session 获取用户 ID
        user_id = session.get('user_id')

        if not user_id:
            return error_response('请先登录', error_code='AUTH_REQUIRED', status=401)

        # 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            # 用户不存在，清除 session
            session.pop('user_id', None)
            return error_response('用户不存在', error_code='AUTH_REQUIRED', status=401)

        # 将用户存储到 g 对象，方便后续使用
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    管理员权限验证装饰器
    #
    # 要求用户必须是管理员（超级用户），否则返回 403 错误
    #
    # 技术要点：
    # - 先验证登录状态
    # - 再验证用户是否为管理员
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从 session 获取用户 ID
        user_id = session.get('user_id')

        if not user_id:
            return error_response('请先登录', error_code='AUTH_REQUIRED', status=401)

        # 获取用户并验证权限
        user = User.query.get(user_id)
        if not user:
            session.pop('user_id', None)
            return error_response('用户不存在', error_code='AUTH_REQUIRED', status=401)

        if not user.is_superuser:
            return error_response('需要管理员权限', error_code='PERMISSION_DENIED', status=403)

        # 将用户存储到 g 对象
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """
    获取当前登录用户
    #
    # Returns:
    #     User: 当前登录用户对象，未登录时返回 None
    #
    # 技术要点：
    # - 从 session 获取用户 ID
    # - 返回用户对象或 None
    """
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None
