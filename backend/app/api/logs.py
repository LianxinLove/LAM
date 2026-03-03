"""
Operation log API routes
"""
from flask import Blueprint, request
from app.models import OperationLog
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_pagination

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('', methods=['GET'])
@login_required
@admin_required
def get_logs():
    """Get operation logs (admin only)"""
    page, page_size = validate_pagination()
    
    # Limit to last 100 records
    query = OperationLog.query
    
    # Order by timestamp descending
    query = query.order_by(OperationLog.timestamp.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Convert to dict
    items = [log.to_dict() for log in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)
