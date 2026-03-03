"""
Consumable management API routes
"""
from flask import Blueprint, request
from app.models import Consumable, Category, Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

consumables_bp = Blueprint('consumables', __name__)


@consumables_bp.route('', methods=['GET'])
@login_required
def get_consumables():
    """Get list of consumables with filtering and pagination"""
    # Get query parameters
    category_id = request.args.get('category_id', type=int)
    low_stock = request.args.get('low_stock', type=bool)
    page, page_size = validate_pagination()
    
    # Build query
    query = Consumable.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if low_stock:
        query = query.filter(Consumable.stock < Consumable.min_stock)
    
    # Order by created_at descending
    query = query.order_by(Consumable.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [consumable.to_dict() for consumable in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)


@consumables_bp.route('/<int:consumable_id>', methods=['GET'])
@login_required
def get_consumable(consumable_id):
    """Get consumable details"""
    consumable = Consumable.query.get(consumable_id)
    
    if not consumable:
        return error_response('Consumable not found', error_code='NOT_FOUND', status=404)
    
    return success_response(data=consumable.to_dict())


@consumables_bp.route('', methods=['POST'])
@admin_required
def create_consumable():
    """Create a new consumable (admin only)"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['name', 'category_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Check if category exists
    category = Category.query.get(data['category_id'])
    if not category:
        return error_response('Category not found', error_code='NOT_FOUND', status=404)
    
    # Check if supplier exists (if provided)
    supplier = None
    if data.get('supplier_id'):
        supplier = Supplier.query.get(data['supplier_id'])
        if not supplier:
            return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
    
    # Generate consumable code (CON-XXXX format)
    from app.extensions import db
    last_consumable = Consumable.query.order_by(Consumable.id.desc()).first()
    if last_consumable:
        last_id = last_consumable.id
    else:
        last_id = 0
    code = f"CON-{last_id + 1:04d}"
    
    # Create consumable
    consumable = Consumable(
        name=data['name'],
        code=code,
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        unit=data.get('unit', '个'),
        stock=data.get('stock', 0),
        min_stock=data.get('min_stock', 10),
        price=data.get('price'),
        location=data.get('location')
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
        return error_response(f'Failed to create consumable: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@consumables_bp.route('/<int:consumable_id>', methods=['PUT'])
@admin_required
def update_consumable(consumable_id):
    """Update a consumable (admin only)"""
    consumable = Consumable.query.get(consumable_id)
    
    if not consumable:
        return error_response('Consumable not found', error_code='NOT_FOUND', status=404)
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        consumable.name = data['name']
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return error_response('Category not found', error_code='NOT_FOUND', status=404)
        consumable.category_id = data['category_id']
    if 'supplier_id' in data:
        if data['supplier_id']:
            supplier = Supplier.query.get(data['supplier_id'])
            if not supplier:
                return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
        consumable.supplier_id = data['supplier_id']
    if 'unit' in data:
        consumable.unit = data['unit']
    if 'stock' in data:
        consumable.stock = data['stock']
    if 'min_stock' in data:
        consumable.min_stock = data['min_stock']
    if 'price' in data:
        consumable.price = data['price']
    if 'location' in data:
        consumable.location = data['location']
    
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
        return error_response(f'Failed to update consumable: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@consumables_bp.route('/<int:consumable_id>', methods=['DELETE'])
@admin_required
def delete_consumable(consumable_id):
    """Delete a consumable (admin only)"""
    consumable = Consumable.query.get(consumable_id)
    
    if not consumable:
        return error_response('Consumable not found', error_code='NOT_FOUND', status=404)
    
    try:
        from app.extensions import db
        db.session.delete(consumable)
        db.session.commit()
        
        return success_response(message='耗材删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to delete consumable', error_code='INTERNAL_ERROR', status=500)
