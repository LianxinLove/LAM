"""
Custom decorators for authentication and authorization
"""
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
from app.utils.response import error_response


def login_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception:
            return error_response('Authentication required', error_code='AUTH_REQUIRED', status=401)
    return decorated_function


def admin_required(f):
    """Decorator to require admin/superuser privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())  # Convert string to int
            user = User.query.get(user_id)

            if not user or not user.is_superuser:
                return error_response('Admin privileges required', error_code='PERMISSION_DENIED', status=403)

            return f(*args, **kwargs)
        except Exception:
            return error_response('Authentication required', error_code='AUTH_REQUIRED', status=401)
    return decorated_function


def get_current_user():
    """Get the current authenticated user"""
    try:
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())  # Convert string to int
        return User.query.get(user_id)
    except:
        return None
