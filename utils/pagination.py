"""
Pagination Utility

Handles paginated responses for list endpoints.
"""

from typing import List, TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format.
    
    Attributes:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        pages: Total number of pages
        per_page: Items per page
        has_next: Whether there is a next page
        has_prev: Whether there is a previous page
    """
    
    items: List[T] = Field(..., description="Items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number", ge=1)
    pages: int = Field(..., description="Total number of pages")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "Item 1"}],
                "total": 100,
                "page": 1,
                "pages": 10,
                "per_page": 10,
                "has_next": True,
                "has_prev": False
            }
        }


def paginate(
    items: List[Any],
    total: int,
    page: int = 1,
    per_page: int = 10
) -> PaginatedResponse:
    """
    Create a paginated response.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (default: 1)
        per_page: Items per page (default: 10)
        
    Returns:
        PaginatedResponse: Formatted paginated response
        
    Example:
        items = [product1, product2, product3]
        response = paginate(items, total=100, page=2, per_page=10)
    """
    
    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        pages=pages,
        per_page=per_page,
        has_next=page < pages,
        has_prev=page > 1
    )


def calculate_pagination(
    page: int = 1,
    per_page: int = 10,
    max_per_page: int = 100
) -> tuple[int, int]:
    """
    Calculate skip and limit for database queries.
    
    Args:
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum allowed per_page value
        
    Returns:
        tuple: (skip, limit)
        
    Example:
        skip, limit = calculate_pagination(page=2, per_page=20)
        # Returns: (20, 20)
    """
    
    # Validate inputs
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    # Calculate skip
    skip = (page - 1) * per_page
    
    return skip, per_page