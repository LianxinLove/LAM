"""
Asset borrowing management API routes
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app.models import BorrowRecord, Asset
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination

borrows_bp = Blueprint('borrows', __name__)


@borrows_bp.route('', methods=['GET'])
@login_required
def get_borrows():
    """Get list of borrow records with filtering and pagination"""
    from app.models import User
    # Get query parameters
    status = request.args.get('status')
    borrower_id = request.args.get('borrower_id', type=int)
    my = request.args.get('my', False)
    page, page_size = validate_pagination()

    # Get current user
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    # Build query
    query = BorrowRecord.query

    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if borrower_id:
        query = query.filter_by(borrower_id=borrower_id)

    # Filter by current user if 'my' parameter is True
    if my and not (current_user and current_user.is_superuser):
        query = query.filter_by(borrower_id=user_id)

    # Order by borrow_date descending
    query = query.order_by(BorrowRecord.borrow_date.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # Convert to dict
    items = [borrow.to_dict() for borrow in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@borrows_bp.route('/<int:record_id>', methods=['GET'])
@login_required
def get_borrow(record_id):
    """Get borrow record details"""
    borrow = BorrowRecord.query.get(record_id)

    if not borrow:
        return error_response('Borrow record not found', error_code='NOT_FOUND', status=404)

    return success_response(data=borrow.to_dict())


@borrows_bp.route('', methods=['POST'])
@login_required
def borrow_asset():
    """Borrow an asset"""
    data = request.get_json()
    
    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ['asset_id'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')
    
    # Get asset
    asset = Asset.query.get(data['asset_id'])
    if not asset:
        return error_response('Asset not found', error_code='NOT_FOUND', status=404)
    
    # Check if asset is available
    if not asset.is_available:
        return error_response('Asset is not available for borrowing', error_code='INVALID_STATUS', status=400)
    
    # Get current user
    user_id = int(get_jwt_identity())

    # Create borrow record
    borrow = BorrowRecord(
        asset_id=data['asset_id'],
        borrower_id=user_id,
        purpose=data.get('purpose'),
        status='borrowed'
    )
    
    try:
        from app.extensions import db
        
        # Update asset status
        asset.status = 'in_use'
        
        db.session.add(borrow)
        db.session.commit()
        
        return success_response(
            message='借用成功',
            data={
                'id': borrow.id,
                'asset': {
                    'id': asset.id,
                    'name': asset.name
                },
                'borrow_date': borrow.borrow_date.isoformat()
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to borrow asset', error_code='INTERNAL_ERROR', status=500)


@borrows_bp.route('/<int:record_id>/return', methods=['POST'])
@login_required
def return_asset(record_id):
    """Return a borrowed asset"""
    borrow = BorrowRecord.query.get(record_id)

    if not borrow:
        return error_response('Borrow record not found', error_code='NOT_FOUND', status=404)

    # Check if the record belongs to the current user
    user_id = int(get_jwt_identity())
    if borrow.borrower_id != user_id:
        return error_response('You can only return your own borrowed assets', error_code='PERMISSION_DENIED', status=403)

    # Check if already returned
    if borrow.status == 'returned':
        return error_response('Asset has already been returned', error_code='INVALID_STATUS', status=400)

    try:
        from app.extensions import db

        # Update borrow record
        borrow.return_date = datetime.utcnow()
        borrow.status = 'returned'

        # Update asset status
        if borrow.asset:
            borrow.asset.status = 'available'

        db.session.commit()

        return success_response(
            message='归还成功',
            data={
                'id': borrow.id,
                'return_date': borrow.return_date.isoformat(),
                'status': borrow.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response('Failed to return asset', error_code='INTERNAL_ERROR', status=500)


@borrows_bp.route('/my', methods=['GET'])
@login_required
def get_my_borrows():
    """Get current user's borrow records"""
    user_id = int(get_jwt_identity())
    page, page_size = validate_pagination()

    # Build query
    query = BorrowRecord.query.filter_by(borrower_id=user_id)

    # Order by borrow_date descending
    query = query.order_by(BorrowRecord.borrow_date.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # Convert to dict
    items = [borrow.to_dict() for borrow in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)
