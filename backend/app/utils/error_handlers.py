"""
错误处理器模块

功能说明：
- 统一注册各类错误处理器
- 捕获并转换各类异常为标准 JSON 响应
- 记录错误日志便于调试

处理的异常类型：
- HTTPException: HTTP 标准异常（404, 405, 500等）
- IntegrityError: 数据库完整性约束异常
- Exception: 未捕获的通用异常

技术要点：
- 使用 @app.errorhandler 装饰器注册异常处理器
- 所有异常返回统一的 JSON 格式
- 生产环境应使用日志系统而非 print
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from app.utils.response import error_response


def register_error_handlers(app):
    """
    注册所有错误处理器

    Args:
        app (Flask): Flask 应用实例

    处理的错误类型：
        - 404: 资源不存在
        - 405: 方法不允许
        - 500: 服务器内部错误
        - IntegrityError: 数据库完整性错误
        - Exception: 未预期的异常
    """

    @app.errorhandler(404)
    def not_found(error):
        """
        处理 404 Not Found 错误

        当请求的路由或资源不存在时触发
        """
        return error_response('请求的资源不存在', error_code='NOT_FOUND', status=404)

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        处理 405 Method Not Allowed 错误

        当 HTTP 方法不匹配时触发（如对 GET 请求的端点使用 POST）
        """
        return error_response('请求方法不允许', error_code='METHOD_NOT_ALLOWED', status=405)

    @app.errorhandler(500)
    def internal_error(error):
        """
        处理 500 Internal Server Error 错误

        服务器内部错误，通常是未预期的异常
        """
        return error_response('服务器内部错误', error_code='INTERNAL_ERROR', status=500)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """
        处理数据库完整性约束错误

        常见场景：
        - 唯一约束违反（重复数据）
        - 外键约束违反（引用的数据不存在）
        - 非空约束违反

        Args:
            error: SQLAlchemy IntegrityError 异常对象

        技术要点：
            - 解析错误消息判断具体类型
            - 返回友好的中文错误提示
        """
        error_str = str(error.orig)

        if 'Duplicate entry' in error_str or 'UNIQUE constraint failed' in error_str:
            return error_response('数据重复', error_code='DUPLICATE_ENTRY', status=400)
        if 'FOREIGN KEY constraint failed' in error_str:
            return error_response('引用的数据不存在', error_code='FOREIGN_KEY_ERROR', status=400)
        if 'NOT NULL constraint failed' in error_str:
            return error_response('必填字段不能为空', error_code='NOT_NULL_ERROR', status=400)

        return error_response('数据完整性错误', error_code='INTEGRITY_ERROR', status=400)

    @app.errorhandler(Exception)
    def handle_exception(error):
        """
        处理所有未捕获的异常

        这是最后的错误处理保障，捕获所有未被上面处理器处理的异常

        Args:
            error: Exception 异常对象

        技术要点：
            - 记录完整的错误堆栈信息
            - 生产环境应使用 logging 模块而非 print
            - 隐藏内部实现细节，返回通用错误消息
        """
        # 记录错误日志
        import traceback
        print(f"ERROR: {str(error)}")
        print(traceback.format_exc())

        # 如果是 HTTP 异常，返回其描述
        if isinstance(error, HTTPException):
            return error_response(
                error.description,
                error_code='HTTP_ERROR',
                status=error.code
            )

        # 其他异常返回通用错误消息
        # 生产环境不应暴露内部错误细节
        return error_response(
            '服务器发生未预期的错误',
            error_code='UNEXPECTED_ERROR',
            status=500
        )
