"""
Standardized response utilities
"""
from flask import jsonify


def success_response(message='操作成功', data=None, status=200):
    """Standard success response"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def error_response(message='操作失败', error_code=None, details=None, status=400):
    """Standard error response"""
    response = {
        'success': False,
        'message': message
    }
    if error_code:
        response['error_code'] = error_code
    if details:
        response['details'] = details
    return jsonify(response), status


def paginated_response(items, total, page, page_size):
    """Standard paginated response"""
    return success_response(data={
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size
    })
