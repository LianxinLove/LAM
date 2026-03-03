"""
输入验证工具模块

功能说明：
- 分页参数验证
- 必填字段验证

技术要点：
- 统一验证逻辑，避免重复代码
- 提供友好的错误提示
- 参数边界检查
"""
from flask import request
from app.config import Config


def validate_pagination():
    """
    验证并返回分页参数

    Query参数：
        page: 页码（默认1）
        page_size: 每页数量（默认为配置的 DEFAULT_PAGE_SIZE）

    Returns:
        tuple: (page, page_size) 验证后的分页参数

    技术要点：
        - page 小于 1 时重置为 1
        - page_size 小于 1 时使用默认值
        - page_size 超过 MAX_PAGE_SIZE 时限制为最大值
        - 防止恶意用户请求过多数据
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', Config.DEFAULT_PAGE_SIZE, type=int)

    # 验证页码
    if page < 1:
        page = 1

    # 验证每页数量
    if page_size < 1:
        page_size = Config.DEFAULT_PAGE_SIZE
    elif page_size > Config.MAX_PAGE_SIZE:
        page_size = Config.MAX_PAGE_SIZE

    return page, page_size


def validate_required_fields(data, required_fields):
    """
    验证必填字段是否存在

    Args:
        data (dict): 请求数据
        required_fields (list): 必填字段名称列表

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: 是否验证通过
            - error_message: 错误信息（验证失败时）

    技术要点：
        - 检查字段是否存在且不为 None
        - 空字符串 "" 被视为有效值（如需验证空字符串，请在前端处理）
        - 返回友好的错误提示，列出所有缺失的字段

    示例：
        >>> is_valid, msg = validate_required_fields({'name': 'test'}, ['name', 'email'])
        >>> print(is_valid, msg)
        (False, 'Missing required fields: email')
    """
    missing_fields = [
        field for field in required_fields
        if field not in data or data[field] is None
    ]

    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"

    return True, None
