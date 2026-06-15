"""
Validation Utilities

Common validation functions for data sanitization and validation.
"""

import re
from typing import Optional, Any


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid email format
        
    Example:
        if validate_email("user@example.com"):
            print("Valid email")
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Supports formats:
    - +232 12345678 (Sierra Leone)
    - 076123456
    - 076-123-456
    
    Args:
        phone: Phone string to validate
        
    Returns:
        bool: True if valid phone format
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if contains only digits
    if not cleaned.isdigit():
        return False
    
    # Check length (8-15 digits)
    return 8 <= len(cleaned) <= 15


def validate_price(price: float) -> bool:
    """
    Validate price value.
    
    Args:
        price: Price to validate
        
    Returns:
        bool: True if valid price
        
    Example:
        if validate_price(19.99):
            print("Valid price")
    """
    if not isinstance(price, (int, float)):
        return False
    
    return price > 0 and price <= 1000000


def validate_quantity(quantity: int, min_qty: int = 1, max_qty: int = 1000) -> bool:
    """
    Validate quantity value.
    
    Args:
        quantity: Quantity to validate
        min_qty: Minimum allowed quantity (default: 1)
        max_qty: Maximum allowed quantity (default: 1000)
        
    Returns:
        bool: True if valid quantity
    """
    if not isinstance(quantity, int):
        return False
    
    return min_qty <= quantity <= max_qty


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize string input.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (default: 500)
        
    Returns:
        str: Sanitized string
        
    Example:
        clean = sanitize_string("  Hello  World  ")
        # Returns: "Hello World"
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_sierra_leone_phone(phone: str) -> bool:
    """
    Validate Sierra Leone phone number specifically.
    
    Sierra Leone formats:
    - +232 76 123456
    - 076 123456
    - 076123456
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid Sierra Leone phone
    """
    if not phone:
        return False
    
    # Remove spaces
    cleaned = re.sub(r'[\s\-]', '', phone)
    
    # Check for +232 format
    if cleaned.startswith('+232'):
        cleaned = cleaned[4:]
    # Check for 0 at start
    elif cleaned.startswith('0'):
        cleaned = cleaned[1:]
    
    # Should be 7-8 digits for Sierra Leone
    if not cleaned.isdigit():
        return False
    
    return 7 <= len(cleaned) <= 8


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        dict: Validation result with score and feedback
        
    Example:
        result = validate_password_strength("MyPassword123")
        print(result["score"])  # 3
    """
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Password should contain at least one uppercase letter")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Password should contain at least one lowercase letter")
    
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Password should contain at least one number")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Password should contain at least one special character")
    
    # Determine strength
    if score >= 5:
        strength = "strong"
    elif score >= 3:
        strength = "medium"
    else:
        strength = "weak"
    
    return {
        "score": score,
        "max_score": 5,
        "strength": strength,
        "feedback": feedback
    }