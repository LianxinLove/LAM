"""
标准化响应工具模块

功能说明：
- 统一 API 响应格式
- 成功响应处理
- 错误响应处理
- 分页响应处理

响应格式规范：
成功响应：
{
    "success": true,
    "message": "操作成功",
    "data": { ... }  // 可选
}

错误响应：
{
    "success": false,
    "message": "错误描述",
    "error_code": "ERROR_CODE",  // 可选
    "details": { ... }  // 可选
}

分页响应：
{
    "success": true,
    "message": "操作成功",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}

技术要点：
- 统一响应格式，方便前端处理
- 使用 JSON 格式
- 支持 HTTP 状态码
"""
from flask import jsonify


def success_response(message='操作成功', data=None, status=200):
    """
    标准成功响应

    Args:
        message: 成功消息
        data: 响应数据（可选）
        status: HTTP 状态码（默认200）

    Returns:
        tuple: (json_response, status_code)

    技术要点：
        - success 固定为 true
        - data 为 None 时不包含在响应中
        - 支持自定义 HTTP 状态码（如 201 创建成功）
    """
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def error_response(message='操作失败', error_code=None, details=None, status=400):
    """
    标准错误响应

    Args:
        message: 错误消息
        error_code: 错误代码（可选），用于前端错误分类处理
        details: 详细信息（可选），可用于传递更多错误细节
        status: HTTP 状态码（默认400）

    Returns:
        tuple: (json_response, status_code)

    技术要点：
        - success 固定为 false
        - error_code 用于前端错误分类处理
        - details 可包含更详细的错误信息

    常用 error_code：
        - VALIDATION_ERROR: 参数验证失败
        - NOT_FOUND: 资源不存在
        - DUPLICATE_ENTRY: 重复数据
        - AUTH_REQUIRED: 需要登录
        - PERMISSION_DENIED: 权限不足
        - INTERNAL_ERROR: 服务器内部错误
    """
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
    """
    标准分页响应

    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量

    Returns:
        tuple: (json_response, status_code)

    技术要点：
        - 将分页信息包装在 data 字段中
        - 包含总记录数，方便前端显示分页控件
        - 使用 success_response 统一返回格式

    前端分页计算示例：
        total_pages = Math.ceil(total / page_size)
        has_next = page < total_pages
        has_prev = page > 1
    """
    return success_response(data={
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size
    })
