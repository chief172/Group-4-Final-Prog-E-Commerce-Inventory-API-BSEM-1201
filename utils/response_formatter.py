"""
Response Formatter Utilities

Standardized API response formats.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .date_utils import utc_now, to_iso_format


def success_response(
    data: Any,
    message: str = "Success",
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Format success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        dict: Formatted success response
        
    Example:
        response = success_response({"id": 1, "name": "Product"})
    """
    return {
        "success": True,
        "status_code": status_code,
        "message": message,
        "data": data,
        "timestamp": to_iso_format(utc_now())
    }


def error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Any] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Format error response.
    
    Args:
        message: Error message
        error_code: Error code (optional)
        details: Additional error details (optional)
        status_code: HTTP status code
        
    Returns:
        dict: Formatted error response
        
    Example:
        response = error_response(
            "Product not found",
            error_code="PRODUCT_404",
            status_code=404
        )
    """
    response = {
        "success": False,
        "status_code": status_code,
        "message": message,
        "timestamp": to_iso_format(utc_now())
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return response


def list_response(
    items: List[Any],
    total: Optional[int] = None,
    page: int = 1,
    per_page: int = 10,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Format list response with pagination.
    
    Args:
        items: List of items
        total: Total number of items (optional)
        page: Current page number
        per_page: Items per page
        message: Success message
        
    Returns:
        dict: Formatted list response
        
    Example:
        response = list_response(products, total=100, page=2, per_page=10)
    """
    if total is None:
        total = len(items)
    
    return {
        "success": True,
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page if total > 0 else 1
            }
        },
        "timestamp": to_iso_format(utc_now())
    }


def created_response(
    data: Any,
    message: str = "Resource created successfully"
) -> Dict[str, Any]:
    """
    Format 201 Created response.
    
    Args:
        data: Created resource data
        message: Success message
        
    Returns:
        dict: Formatted created response
    """
    return success_response(data, message, status_code=201)


def deleted_response(
    message: str = "Resource deleted successfully"
) -> Dict[str, Any]:
    """
    Format 204 Deleted response.
    
    Args:
        message: Success message
        
    Returns:
        dict: Formatted deleted response
    """
    return {
        "success": True,
        "status_code": 204,
        "message": message,
        "timestamp": to_iso_format(utc_now())
    }