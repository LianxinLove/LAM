"""
Input validation utilities
"""
from flask import request
from app.config import Config


def validate_pagination():
    """Validate and return pagination parameters"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', Config.DEFAULT_PAGE_SIZE, type=int)
    
    # Validate page
    if page < 1:
        page = 1
    
    # Validate page_size
    if page_size < 1:
        page_size = Config.DEFAULT_PAGE_SIZE
    elif page_size > Config.MAX_PAGE_SIZE:
        page_size = Config.MAX_PAGE_SIZE
    
    return page, page_size


def validate_required_fields(data, required_fields):
    """Validate that required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None
