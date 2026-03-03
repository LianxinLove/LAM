"""
输入验证工具模块

功能说明：
- 分页参数验证
- 必填字段验证
- 数字字段验证（整数、金额）
- 日期格式验证

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
        (False, '缺少必填字段: email')
    """
    missing_fields = [
        field for field in required_fields
        if field not in data or data[field] is None
    ]

    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"

    return True, None


def validate_positive_integer(value, field_name, allow_zero=True, max_value=None):
    """
    验证正整数

    Args:
        value: 要验证的值
        field_name: 字段名称（用于错误提示）
        allow_zero: 是否允许 0（默认 True）
        max_value: 最大值限制（可选）

    Returns:
        tuple: (is_valid, error_message, validated_value)

    技术要点：
        - 验证值是否为整数
        - 验证值是否在允许范围内
        - 支持从字符串转换整数
    """
    # 尝试转换为整数
    try:
        if isinstance(value, float):
            # 检查是否为整数的浮点数（如 1.0）
            if not value.is_integer():
                return False, f"{field_name} 必须为整数", None
            value = int(value)
        elif isinstance(value, str):
            value = int(value)
        elif not isinstance(value, int):
            return False, f"{field_name} 必须为整数", None
    except (ValueError, TypeError):
        return False, f"{field_name} 必须为整数", None

    # 验证最小值
    if allow_zero:
        if value < 0:
            return False, f"{field_name} 不能为负数", None
    else:
        if value < 1:
            return False, f"{field_name} 必须大于 0", None

    # 验证最大值
    if max_value is not None and value > max_value:
        return False, f"{field_name} 不能超过 {max_value}", None

    return True, None, value


def validate_positive_decimal(value, field_name, allow_zero=True, max_value=None, precision=2):
    """
    验证正数金额/小数

    Args:
        value: 要验证的值
        field_name: 字段名称（用于错误提示）
        allow_zero: 是否允许 0（默认 True）
        max_value: 最大值限制（可选）
        precision: 小数位数限制（默认 2 位）

    Returns:
        tuple: (is_valid, error_message, validated_value)

    技术要点：
        - 验证值是否为数字
        - 验证小数位数是否超限
        - 验证值是否在允许范围内
    """
    # 尝试转换为浮点数
    try:
        if isinstance(value, str):
            value = float(value)
        elif not isinstance(value, (int, float)):
            return False, f"{field_name} 必须为数字", None
    except (ValueError, TypeError):
        return False, f"{field_name} 必须为数字", None

    # 检查小数位数
    if isinstance(value, float) and precision is not None:
        # 将浮点数转为字符串检查小数位数
        str_value = f"{value:.{precision}f}"
        if '.' in str_value:
            decimal_places = len(str_value.split('.')[1])
            # 处理精度问题（如 1.10 -> 1.1）
            actual_decimal = len(f"{value:.10f}".rstrip('0').split('.')[-1]) if '.' in f"{value:.10f}" else 0
            if actual_decimal > precision:
                return False, f"{field_name} 最多保留 {precision} 位小数", None

    # 验证最小值
    if allow_zero:
        if value < 0:
            return False, f"{field_name} 不能为负数", None
    else:
        if value <= 0:
            return False, f"{field_name} 必须大于 0", None

    # 验证最大值
    if max_value is not None and value > max_value:
        return False, f"{field_name} 不能超过 {max_value}", None

    return True, None, value


def validate_number_field(data, field_name, field_type='integer', **kwargs):
    """
    验证数据中的数字字段（便捷函数）

    Args:
        data (dict): 请求数据
        field_name (str): 字段名称
        field_type (str): 字段类型 ('integer' 或 'decimal')
        **kwargs: 传递给具体验证函数的参数

    Returns:
        tuple: (is_valid, error_message, validated_value)

    示例：
        >>> is_valid, msg, value = validate_number_field(data, 'quantity', 'integer', allow_zero=False)
    """
    if field_name not in data or data[field_name] is None:
        return True, None, None  # 字段不存在，由必填字段验证处理

    value = data[field_name]

    if field_type == 'integer':
        return validate_positive_integer(value, field_name, **kwargs)
    elif field_type == 'decimal':
        return validate_positive_decimal(value, field_name, **kwargs)
    else:
        return False, f"不支持的字段类型: {field_type}", None


def validate_stock_fields(data):
    """
    验证库存相关字段（stock, min_stock）

    Args:
        data (dict): 请求数据

    Returns:
        tuple: (is_valid, error_message)

    技术要点：
        - stock 必须为非负整数
        - min_stock 必须为非负整数
        - stock 不能小于 0
    """
    # 验证 stock
    if 'stock' in data and data['stock'] is not None:
        is_valid, msg, _ = validate_positive_integer(
            data['stock'],
            '当前库存',
            allow_zero=True
        )
        if not is_valid:
            return False, msg

    # 验证 min_stock
    if 'min_stock' in data and data['min_stock'] is not None:
        is_valid, msg, _ = validate_positive_integer(
            data['min_stock'],
            '最低库存',
            allow_zero=True
        )
        if not is_valid:
            return False, msg

    return True, None


def validate_price_field(data, field_name='price', required=False):
    """
    验证价格字段

    Args:
        data (dict): 请求数据
        field_name (str): 价格字段名称
        required (bool): 是否必填

    Returns:
        tuple: (is_valid, error_message, validated_value)
    """
    if field_name not in data or data[field_name] is None:
        if required:
            return False, f"{field_name} 不能为空", None
        return True, None, None

    value = data[field_name]
    return validate_positive_decimal(
        value,
        field_name,
        allow_zero=True,
        precision=2
    )


def validate_quantity_field(data, field_name='quantity', required=False):
    """
    验证数量字段（必须为正整数，不能为 0）

    Args:
        data (dict): 请求数据
        field_name (str): 数量字段名称
        required (bool): 是否必填

    Returns:
        tuple: (is_valid, error_message, validated_value)
    """
    if field_name not in data or data[field_name] is None:
        if required:
            return False, f"{field_name} 不能为空", None
        return True, None, None

    value = data[field_name]
    return validate_positive_integer(
        value,
        field_name,
        allow_zero=False  # 数量必须至少为 1
    )
