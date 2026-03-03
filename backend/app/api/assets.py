"""
Asset management API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.models import Asset, Category, Supplier
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination


def parse_date(date_string):
    """Parse date string to date object"""
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
    """Get list of assets with filtering and pagination"""
    # Get query parameters
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    page, page_size = validate_pagination()
    
    # Build query
    query = Asset.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)
    
    # Order by created_at descending
    query = query.order_by(Asset.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [asset.to_dict() for asset in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)


@assets_bp.route('/<int:asset_id>', methods=['GET'])
@login_required
def get_asset(asset_id):
    """Get asset details"""
    asset = Asset.query.get(asset_id)
    
    if not asset:
        return error_response('Asset not found', error_code='NOT_FOUND', status=404)
    
    return success_response(data=asset.to_dict(include_details=True))


@assets_bp.route('', methods=['POST'])
@admin_required
def create_asset():
    """Create a new asset (admin only)"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['name', 'code', 'category_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Check if code already exists
    if Asset.query.filter_by(code=data['code']).first():
        return error_response('Asset code already exists', error_code='DUPLICATE_ENTRY')
    
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

    # Get custodian name (simple string, no validation needed)
    custodian = data.get('custodian')

    # Create asset
    asset = Asset(
        name=data['name'],
        code=data['code'],
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        specifications=data.get('specifications'),
        purchase_date=parse_date(data.get('purchase_date')),
        purchase_price=data.get('purchase_price'),
        status=data.get('status', 'available'),
        location=data.get('location'),
        custodian=custodian,
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
                'code': asset.code
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        # Log the actual error for debugging
        print(f"Asset creation error: {e}")
        print(f"Request data: {data}")
        print(traceback.format_exc())
        return error_response(f'Failed to create asset: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@assets_bp.route('/<int:asset_id>', methods=['PUT'])
@admin_required
def update_asset(asset_id):
    """Update an asset (admin only)"""
    asset = Asset.query.get(asset_id)
    
    if not asset:
        return error_response('Asset not found', error_code='NOT_FOUND', status=404)
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        asset.name = data['name']
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return error_response('Category not found', error_code='NOT_FOUND', status=404)
        asset.category_id = data['category_id']
    if 'supplier_id' in data:
        if data['supplier_id']:
            supplier = Supplier.query.get(data['supplier_id'])
            if not supplier:
                return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
        asset.supplier_id = data['supplier_id']
    if 'specifications' in data:
        asset.specifications = data['specifications']
    if 'purchase_date' in data:
        asset.purchase_date = parse_date(data['purchase_date'])
    if 'purchase_price' in data:
        asset.purchase_price = data['purchase_price']
    if 'status' in data:
        asset.status = data['status']
    if 'location' in data:
        asset.location = data['location']
    if 'custodian' in data:
        asset.custodian = data['custodian']
    if 'remarks' in data:
        asset.remarks = data['remarks']
    
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
        return error_response('Failed to update asset', error_code='INTERNAL_ERROR', status=500)


@assets_bp.route('/<int:asset_id>', methods=['DELETE'])
@admin_required
def delete_asset(asset_id):
    """Delete an asset (admin only)"""
    asset = Asset.query.get(asset_id)
    
    if not asset:
        return error_response('Asset not found', error_code='NOT_FOUND', status=404)
    
    try:
        from app.extensions import db
        db.session.delete(asset)
        db.session.commit()
        
        return success_response(message='资产删除成功')
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to delete asset', error_code='INTERNAL_ERROR', status=500)
