"""
Error handlers for the application
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from app.utils.response import error_response


def register_error_handlers(app):
    """Register all error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response('Resource not found', error_code='NOT_FOUND', status=404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response('Method not allowed', error_code='METHOD_NOT_ALLOWED', status=405)
    
    @app.errorhandler(500)
    def internal_error(error):
        return error_response('Internal server error', error_code='INTERNAL_ERROR', status=500)
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        if 'Duplicate entry' in str(error.orig):
            return error_response('Duplicate entry', error_code='DUPLICATE_ENTRY', status=400)
        return error_response('Database integrity error', error_code='INTEGRITY_ERROR', status=400)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Log the error for debugging
        import traceback
        print(f"ERROR: {str(error)}")
        print(traceback.format_exc())
        
        if isinstance(error, HTTPException):
            return error_response(error.description, status=error.code)
        return error_response('An unexpected error occurred', error_code='UNEXPECTED_ERROR', status=500)
