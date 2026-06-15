"""
Utils Module for E-Commerce Inventory API

This module contains helper utilities:
- Pagination: Handle paginated responses
- Date formatting: Standardize date/time operations
- Validation helpers: Common validation functions
- Response formatters: Standard API responses
- Price formatting: Currency and price utilities
"""

from .pagination import paginate, PaginatedResponse
from .date_utils import (
    utc_now,
    format_datetime,
    parse_datetime,
    get_date_range
)
from .validators import (
    validate_email,
    validate_phone,
    validate_price,
    validate_quantity,
    sanitize_string
)
from .response_formatter import (
    success_response,
    error_response,
    list_response
)
from .price_utils import (
    format_price,
    calculate_discount,
    calculate_tax
)

__all__ = [
    # Pagination
    "paginate",
    "PaginatedResponse",
    # Date utils
    "utc_now",
    "format_datetime",
    "parse_datetime",
    "get_date_range",
    # Validators
    "validate_email",
    "validate_phone",
    "validate_price",
    "validate_quantity",
    "sanitize_string",
    # Response formatter
    "success_response",
    "error_response",
    "list_response",
    # Price utils
    "format_price",
    "calculate_discount",
    "calculate_tax",
]