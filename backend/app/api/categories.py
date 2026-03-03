"""
Category management API routes
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
    """Get list of categories"""
    page, page_size = validate_pagination()
    
    # Build query
    query = Category.query
    
    # Order by name
    query = query.order_by(Category.name)
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [category.to_dict() for category in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)


@categories_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """Get category details"""
    category = Category.query.get(category_id)
    
    if not category:
        return error_response('Category not found', error_code='NOT_FOUND', status=404)
    
    return success_response(data=category.to_dict())


@categories_bp.route('', methods=['POST'])
@admin_required
def create_category():
    """Create a new category (admin only)"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['name'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Check if name already exists
    if Category.query.filter_by(name=data['name']).first():
        return error_response('Category name already exists', error_code='DUPLICATE_ENTRY')
    
    # Check if parent exists (if provided)
    parent = None
    if data.get('parent_id'):
        parent = Category.query.get(data['parent_id'])
        if not parent:
            return error_response('Parent category not found', error_code='NOT_FOUND', status=404)
    
    # Create category
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
        return error_response('Failed to create category', error_code='INTERNAL_ERROR', status=500)


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Update a category (admin only)"""
    category = Category.query.get(category_id)
    
    if not category:
        return error_response('Category not found', error_code='NOT_FOUND', status=404)
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        category.name = data['name']
    if 'parent_id' in data:
        if data['parent_id']:
            parent = Category.query.get(data['parent_id'])
            if not parent:
                return error_response('Parent category not found', error_code='NOT_FOUND', status=404)
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
        return error_response('Failed to update category', error_code='INTERNAL_ERROR', status=500)


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete a category (admin only)"""
    category = Category.query.get(category_id)
    
    if not category:
        return error_response('Category not found', error_code='NOT_FOUND', status=404)
    
    # Check if category is being used
    if category.assets.count() > 0 or category.consumables.count() > 0:
        return error_response('Cannot delete category that is in use', error_code='IN_USE', status=400)
    
    try:
        from app.extensions import db
        db.session.delete(category)
        db.session.commit()
        
        return success_response(message='类别删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to delete category', error_code='INTERNAL_ERROR', status=500)
