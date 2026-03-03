# 操作日志 API 路由
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
    # 获取操作日志（仅管理员）
    page, page_size = validate_pagination()

    # 限制查询最近 100 条记录
    query = OperationLog.query

    # 按时间戳降序排列
    query = query.order_by(OperationLog.timestamp.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [log.to_dict() for log in pagination.items]
    
    return paginated_response(items, pagination.total, page, page_size)
