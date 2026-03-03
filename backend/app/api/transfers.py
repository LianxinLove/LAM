"""
Asset transfer management API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.models import AssetTransfer, Asset
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

transfers_bp = Blueprint('transfers', __name__)


@transfers_bp.route('', methods=['GET'])
@login_required
def get_transfers():
    """Get list of transfer requests with filtering and pagination"""
    # Get query parameters
    status = request.args.get('status')
    applicant_id = request.args.get('applicant_id', type=int)
    page, page_size = validate_pagination()

    # Build query
    query = AssetTransfer.query

    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if applicant_id:
        query = query.filter_by(applicant_id=applicant_id)

    # Order by created_at descending
    query = query.order_by(AssetTransfer.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # Convert to dict
    items = [transfer.to_dict() for transfer in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@transfers_bp.route('/<int:transfer_id>', methods=['GET'])
@login_required
def get_transfer_detail(transfer_id):
    """Get transfer request details"""
    transfer = AssetTransfer.query.get(transfer_id)

    if not transfer:
        return error_response('Transfer request not found', error_code='NOT_FOUND', status=404)

    return success_response(data=transfer.to_dict())


@transfers_bp.route('', methods=['POST'])
@login_required
def create_transfer():
    """Create an asset transfer request"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['asset_id', 'to_location', 'reason'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Get asset
    asset = Asset.query.get(data['asset_id'])
    if not asset:
        return error_response('Asset not found', error_code='NOT_FOUND', status=404)
    
    # Get current user
    user_id = get_jwt_identity()
    
    # Create transfer request
    transfer = AssetTransfer(
        asset_id=data['asset_id'],
        from_location=asset.location or 'Unknown',
        to_location=data['to_location'],
        reason=data['reason'],
        applicant_id=user_id,
        status='pending'
    )
    
    try:
        from app.extensions import db
        db.session.add(transfer)
        db.session.commit()
        
        return success_response(
            message='资产转移申请已提交',
            data={
                'id': transfer.id,
                'status': transfer.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to create transfer request', error_code='INTERNAL_ERROR', status=500)


@transfers_bp.route('/<int:transfer_id>/approve', methods=['POST'])
@admin_required
def approve_transfer(transfer_id):
    """Approve or reject a transfer request (admin only)"""
    transfer = AssetTransfer.query.get(transfer_id)
    
    if not transfer:
        return error_response('Transfer request not found', error_code='NOT_FOUND', status=404)
    
    if transfer.status != 'pending':
        return error_response('Transfer request has already been processed', error_code='INVALID_STATUS', status=400)
    
    data = request.get_json()
    action = data.get('action')
    
    if action not in ['approve', 'reject']:
        return error_response('Invalid action', error_code='VALIDATION_ERROR')
    
    # Get current user
    user_id = get_jwt_identity()
    
    try:
        from app.extensions import db
        
        if action == 'approve':
            # Update asset location
            if transfer.asset:
                transfer.asset.location = transfer.to_location
            
            transfer.status = 'approved'
            transfer.approver_id = user_id
            transfer.approved_at = datetime.utcnow()
            message = '资产转移申请已批准'
        else:
            transfer.status = 'rejected'
            transfer.approver_id = user_id
            message = '资产转移申请已拒绝'
        
        db.session.commit()
        
        return success_response(
            message=message,
            data={
                'id': transfer.id,
                'status': transfer.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to process transfer request', error_code='INTERNAL_ERROR', status=500)


@transfers_bp.route('/my', methods=['GET'])
@login_required
def get_my_transfers():
    """Get current user's transfer requests"""
    user_id = get_jwt_identity()
    page, page_size = validate_pagination()
    
    # Build query
    query = AssetTransfer.query.filter_by(applicant_id=user_id)
    
    # Order by created_at descending
    query = query.order_by(AssetTransfer.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [transfer.to_dict() for transfer in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)
