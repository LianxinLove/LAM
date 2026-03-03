"""
Supplier management API routes
"""
from flask import Blueprint, request
from app.models import Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('', methods=['GET'])
@login_required
def get_suppliers():
    """Get list of suppliers"""
    page, page_size = validate_pagination()
    
    # Build query
    query = Supplier.query
    
    # Order by name
    query = query.order_by(Supplier.name)
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [supplier.to_dict() for supplier in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@login_required
def get_supplier(supplier_id):
    """Get supplier details"""
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
    
    return success_response(data=supplier.to_dict())


@suppliers_bp.route('', methods=['POST'])
@admin_required
def create_supplier():
    """Create a new supplier (admin only)"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['name'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Check if name already exists
    if Supplier.query.filter_by(name=data['name']).first():
        return error_response('Supplier name already exists', error_code='DUPLICATE_ENTRY')
    
    # Create supplier
    supplier = Supplier(
        name=data['name'],
        contact=data.get('contact'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )
    
    try:
        from app.extensions import db
        db.session.add(supplier)
        db.session.commit()
        
        return success_response(
            message='供应商创建成功',
            data={
                'id': supplier.id,
                'name': supplier.name
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to create supplier', error_code='INTERNAL_ERROR', status=500)


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@admin_required
def update_supplier(supplier_id):
    """Update a supplier (admin only)"""
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        supplier.name = data['name']
    if 'contact' in data:
        supplier.contact = data['contact']
    if 'phone' in data:
        supplier.phone = data['phone']
    if 'email' in data:
        supplier.email = data['email']
    if 'address' in data:
        supplier.address = data['address']
    
    try:
        from app.extensions import db
        db.session.commit()
        
        return success_response(
            message='供应商更新成功',
            data={
                'id': supplier.id,
                'name': supplier.name
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to update supplier', error_code='INTERNAL_ERROR', status=500)


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@admin_required
def delete_supplier(supplier_id):
    """Delete a supplier (admin only)"""
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
    
    # Check if supplier is being used
    if supplier.assets.count() > 0 or supplier.consumables.count() > 0 or supplier.purchase_requests.count() > 0:
        return error_response('Cannot delete supplier that is in use', error_code='IN_USE', status=400)
    
    try:
        from app.extensions import db
        db.session.delete(supplier)
        db.session.commit()
        
        return success_response(message='供应商删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to delete supplier', error_code='INTERNAL_ERROR', status=500)
