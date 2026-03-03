"""
Consumable picking management API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.models import PickRecord, Consumable
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

picks_bp = Blueprint('picks', __name__)


@picks_bp.route('', methods=['GET'])
@login_required
def get_picks():
    """Get list of pick records with filtering and pagination"""
    # Get query parameters
    status = request.args.get('status')
    picker_id = request.args.get('picker_id', type=int)
    page, page_size = validate_pagination()

    # Build query
    query = PickRecord.query

    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if picker_id:
        query = query.filter_by(picker_id=picker_id)

    # Order by created_at descending
    query = query.order_by(PickRecord.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # Convert to dict
    items = [pick.to_dict() for pick in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@picks_bp.route('/<int:pick_id>', methods=['GET'])
@login_required
def get_pick_detail(pick_id):
    """Get pick record details"""
    pick = PickRecord.query.get(pick_id)

    if not pick:
        return error_response('Pick request not found', error_code='NOT_FOUND', status=404)

    return success_response(data=pick.to_dict())


@picks_bp.route('', methods=['POST'])
@login_required
def create_pick():
    """Create a pick request"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['item_id', 'quantity'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Get consumable
    consumable = Consumable.query.get(data['item_id'])
    if not consumable:
        return error_response('Consumable not found', error_code='NOT_FOUND', status=404)
    
    # Check if stock is sufficient
    if consumable.stock < data['quantity']:
        return error_response('Insufficient stock', error_code='INSUFFICIENT_STOCK', status=400)
    
    # Get current user
    user_id = get_jwt_identity()
    
    # Create pick record
    pick = PickRecord(
        item_id=data['item_id'],
        picker_id=user_id,
        quantity=data['quantity'],
        purpose=data.get('purpose'),
        status='pending'
    )
    
    try:
        from app.extensions import db
        db.session.add(pick)
        db.session.commit()
        
        return success_response(
            message='领料申请已提交',
            data={
                'id': pick.id,
                'status': pick.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to create pick request', error_code='INTERNAL_ERROR', status=500)


@picks_bp.route('/<int:pick_id>/approve', methods=['POST'])
@admin_required
def approve_pick(pick_id):
    """Approve or reject a pick request (admin only)"""
    pick = PickRecord.query.get(pick_id)
    
    if not pick:
        return error_response('Pick request not found', error_code='NOT_FOUND', status=404)
    
    if pick.status != 'pending':
        return error_response('Pick request has already been processed', error_code='INVALID_STATUS', status=400)
    
    data = request.get_json()
    action = data.get('action')
    
    if action not in ['approve', 'reject']:
        return error_response('Invalid action', error_code='VALIDATION_ERROR')
    
    # Get current user
    user_id = get_jwt_identity()
    
    try:
        from app.extensions import db
        
        if action == 'approve':
            # Check if stock is sufficient
            if pick.item.stock < pick.quantity:
                return error_response('Insufficient stock', error_code='INSUFFICIENT_STOCK', status=400)
            
            # Deduct stock
            pick.item.stock -= pick.quantity
            
            pick.status = 'approved'
            pick.approver_id = user_id
            pick.approved_at = datetime.utcnow()
            message = '领料申请已批准'
        else:
            pick.status = 'rejected'
            pick.approver_id = user_id
            message = '领料申请已拒绝'
        
        db.session.commit()
        
        return success_response(
            message=message,
            data={
                'id': pick.id,
                'status': pick.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to process pick request', error_code='INTERNAL_ERROR', status=500)


@picks_bp.route('/my', methods=['GET'])
@login_required
def get_my_picks():
    """Get current user's pick records"""
    user_id = get_jwt_identity()
    page, page_size = validate_pagination()
    
    # Build query
    query = PickRecord.query.filter_by(picker_id=user_id)
    
    # Order by created_at descending
    query = query.order_by(PickRecord.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [pick.to_dict() for pick in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)
