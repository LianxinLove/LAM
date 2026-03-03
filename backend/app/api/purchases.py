"""
Purchase request management API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.models import PurchaseRequest, Supplier, User
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

purchases_bp = Blueprint('purchases', __name__)


@purchases_bp.route('', methods=['GET'])
@login_required
def get_purchases():
    """Get list of purchase requests with filtering and pagination"""
    # Get query parameters
    status = request.args.get('status')
    applicant_id = request.args.get('applicant_id', type=int)
    page, page_size = validate_pagination()
    
    # Build query
    query = PurchaseRequest.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if applicant_id:
        query = query.filter_by(applicant_id=applicant_id)
    
    # Order by created_at descending
    query = query.order_by(PurchaseRequest.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [purchase.to_dict() for purchase in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)


@purchases_bp.route('/<int:request_id>', methods=['GET'])
@login_required
def get_purchase(request_id):
    """Get purchase request details"""
    purchase = PurchaseRequest.query.get(request_id)
    
    if not purchase:
        return error_response('Purchase request not found', error_code='NOT_FOUND', status=404)
    
    return success_response(data=purchase.to_dict())


@purchases_bp.route('', methods=['POST'])
@login_required
def create_purchase():
    """Create a new purchase request"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['title', 'item_name', 'quantity', 'estimated_price', 'reason'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Check if supplier exists (if provided)
    supplier = None
    if data.get('supplier_id'):
        supplier = Supplier.query.get(data['supplier_id'])
        if not supplier:
            return error_response('Supplier not found', error_code='NOT_FOUND', status=404)
    
    # Get current user
    user_id = get_jwt_identity()
    
    # Create purchase request
    purchase = PurchaseRequest(
        title=data['title'],
        applicant_id=user_id,
        item_name=data['item_name'],
        quantity=data['quantity'],
        estimated_price=data['estimated_price'],
        supplier_id=data.get('supplier_id'),
        reason=data['reason'],
        status='pending'
    )
    
    try:
        from app.extensions import db
        db.session.add(purchase)
        db.session.commit()
        
        return success_response(
            message='采购申请已提交',
            data={
                'id': purchase.id,
                'status': purchase.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to create purchase request', error_code='INTERNAL_ERROR', status=500)


@purchases_bp.route('/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_purchase(request_id):
    """Approve or reject a purchase request (admin only)"""
    purchase = PurchaseRequest.query.get(request_id)
    
    if not purchase:
        return error_response('Purchase request not found', error_code='NOT_FOUND', status=404)
    
    if purchase.status != 'pending':
        return error_response('Purchase request has already been processed', error_code='INVALID_STATUS', status=400)
    
    data = request.get_json()
    action = data.get('action')
    
    if action not in ['approve', 'reject']:
        return error_response('Invalid action', error_code='VALIDATION_ERROR')
    
    # Get current user
    user_id = get_jwt_identity()
    
    try:
        from app.extensions import db
        
        if action == 'approve':
            purchase.status = 'approved'
            purchase.approver_id = user_id
            purchase.approved_at = datetime.utcnow()
            message = '采购申请已批准'
        else:
            purchase.status = 'rejected'
            purchase.approver_id = user_id
            message = '采购申请已拒绝'
        
        db.session.commit()
        
        return success_response(
            message=message,
            data={
                'id': purchase.id,
                'status': purchase.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to process purchase request', error_code='INTERNAL_ERROR', status=500)
