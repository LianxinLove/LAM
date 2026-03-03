"""
Authentication API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User
from app.utils.decorators import login_required
from app.utils.response import success_response, error_response
from app.utils.validators import validate_required_fields

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['username', 'password'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return error_response('Username already exists', error_code='DUPLICATE_ENTRY')
    
    # Check if email already exists
    if email and User.query.filter_by(email=email).first():
        return error_response('Email already exists', error_code='DUPLICATE_ENTRY')
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    try:
        from app.extensions import db
        db.session.add(user)
        db.session.commit()
        
        # Generate token (identity must be a string)
        access_token = create_access_token(identity=str(user.id))
        
        return success_response(
            message='注册成功',
            data={
                'user_id': user.id,
                'username': user.username,
                'token': access_token
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Registration failed', error_code='INTERNAL_ERROR', status=500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['username', 'password'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    username = data.get('username')
    password = data.get('password')
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    # Check password
    if not user or not user.check_password(password):
        return error_response('Invalid username or password', error_code='INVALID_CREDENTIALS', status=401)
    
    # Check if user is active
    if not user.is_active:
        return error_response('Account is inactive', error_code='ACCOUNT_INACTIVE', status=403)
    
    # Generate token (identity must be a string)
    access_token = create_access_token(identity=str(user.id))
    
    return success_response(
        message='登录成功',
        data={
            'user_id': user.id,
            'username': user.username,
            'is_superuser': user.is_superuser,
            'token': access_token
        }
    )


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    user_id = int(get_jwt_identity())  # Convert string to int
    user = User.query.get(user_id)
    
    if not user:
        return error_response('User not found', error_code='NOT_FOUND', status=404)
    
    return success_response(data=user.to_dict())


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout (client-side token removal)"""
    return success_response(message='登出成功')
