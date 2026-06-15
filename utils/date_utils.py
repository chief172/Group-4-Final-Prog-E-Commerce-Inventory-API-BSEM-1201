"""
Date and Time Utilities

Standardized date/time operations for the application.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple


def utc_now() -> datetime:
    """
    Get current UTC datetime with timezone.
    
    Returns:
        datetime: Current UTC datetime
        
    Example:
        now = utc_now()
        # Returns: 2026-06-13 10:30:00+00:00
    """
    return datetime.now(timezone.utc)


def format_datetime(
    dt: Optional[datetime],
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[str]:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object
        format_string: Format string (default: YYYY-MM-DD HH:MM:SS)
        
    Returns:
        str: Formatted datetime string or None
        
    Example:
        formatted = format_datetime(now)
        # Returns: "2026-06-13 10:30:00"
    """
    if dt is None:
        return None
    
    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format_string)


def parse_datetime(
    date_string: str,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Parse datetime from string.
    
    Args:
        date_string: Datetime string
        format_string: Format string
        
    Returns:
        datetime: Parsed datetime or None
        
    Example:
        dt = parse_datetime("2026-06-13 10:30:00")
    """
    try:
        dt = datetime.strptime(date_string, format_string)
        return dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def get_date_range(days: int = 7) -> Tuple[datetime, datetime]:
    """
    Get date range for last N days.
    
    Args:
        days: Number of days to go back
        
    Returns:
        tuple: (start_date, end_date)
        
    Example:
        start, end = get_date_range(30)
        # Returns: (30 days ago, now)
    """
    end_date = utc_now()
    start_date = end_date - timedelta(days=days)
    
    return start_date, end_date


def is_expired(expiration_date: Optional[datetime]) -> bool:
    """
    Check if a datetime has expired.
    
    Args:
        expiration_date: Expiration datetime
        
    Returns:
        bool: True if expired
        
    Example:
        if is_expired(token_expiry):
            print("Token expired")
    """
    if expiration_date is None:
        return False
    
    if expiration_date.tzinfo is None:
        expiration_date = expiration_date.replace(tzinfo=timezone.utc)
    
    return expiration_date < utc_now()


def days_between(date1: datetime, date2: datetime) -> int:
    """
    Calculate days between two dates.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        int: Number of days between
        
    Example:
        days = days_between(start_date, end_date)
    """
    if date1.tzinfo is None:
        date1 = date1.replace(tzinfo=timezone.utc)
    if date2.tzinfo is None:
        date2 = date2.replace(tzinfo=timezone.utc)
    
    delta = date2 - date1
    return abs(delta.days)


def to_iso_format(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to ISO 8601 format.
    
    Args:
        dt: Datetime object
        
    Returns:
        str: ISO formatted datetime string
        
    Example:
        iso = to_iso_format(now)
        # Returns: "2026-06-13T10:30:00+00:00"
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()