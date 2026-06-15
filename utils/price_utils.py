"""
Price Utilities

Helper functions for price calculations and formatting.
"""

from typing import Optional, Union


def format_price(
    price: Union[int, float],
    currency: str = "SLL",
    decimal_places: int = 2
) -> str:
    """
    Format price with currency symbol.
    
    Args:
        price: Price value
        currency: Currency code (SLL, USD, etc.)
        decimal_places: Number of decimal places
        
    Returns:
        str: Formatted price string
        
    Example:
        formatted = format_price(19.99, "SLL")
        # Returns: "SLL 19.99"
        
        formatted = format_price(100000, "SLL", 0)
        # Returns: "SLL 100,000"
    """
    
    if currency == "SLL":
        # Sierra Leonean Leone - no decimals typically
        decimal_places = 0
    
    # Format number with commas
    formatted_number = f"{price:,.{decimal_places}f}"
    
    return f"{currency} {formatted_number}"


def calculate_discount(
    original_price: float,
    discount_percent: float
) -> dict:
    """
    Calculate discounted price.
    
    Args:
        original_price: Original price
        discount_percent: Discount percentage (0-100)
        
    Returns:
        dict: Discount calculation results
        
    Example:
        result = calculate_discount(100.00, 20)
        # Returns: {
        #     "original_price": 100.00,
        #     "discount_percent": 20,
        #     "discount_amount": 20.00,
        #     "final_price": 80.00,
        #     "savings": 20.00
        # }
    """
    
    discount_percent = max(0, min(100, discount_percent))
    discount_amount = original_price * (discount_percent / 100)
    final_price = original_price - discount_amount
    
    return {
        "original_price": round(original_price, 2),
        "discount_percent": discount_percent,
        "discount_amount": round(discount_amount, 2),
        "final_price": round(final_price, 2),
        "savings": round(discount_amount, 2)
    }


def calculate_tax(
    price: float,
    tax_rate: float = 15.0  # 15% VAT in Sierra Leone
) -> dict:
    """
    Calculate tax on a price.
    
    Args:
        price: Price before tax
        tax_rate: Tax percentage (default: 15% for Sierra Leone)
        
    Returns:
        dict: Tax calculation results
        
    Example:
        result = calculate_tax(100.00, 15)
        # Returns: {
        #     "price_before_tax": 100.00,
        #     "tax_rate": 15,
        #     "tax_amount": 15.00,
        #     "price_after_tax": 115.00
        # }
    """
    
    tax_amount = price * (tax_rate / 100)
    price_after_tax = price + tax_amount
    
    return {
        "price_before_tax": round(price, 2),
        "tax_rate": tax_rate,
        "tax_amount": round(tax_amount, 2),
        "price_after_tax": round(price_after_tax, 2)
    }


def calculate_total_with_tax(
    items: list,
    tax_rate: float = 15.0
) -> dict:
    """
    Calculate total with tax for multiple items.
    
    Args:
        items: List of items with price and quantity
        tax_rate: Tax percentage
        
    Returns:
        dict: Total calculation results
        
    Example:
        items = [
            {"price": 50.00, "quantity": 2},
            {"price": 30.00, "quantity": 1}
        ]
        result = calculate_total_with_tax(items)
    """
    
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount
    
    return {
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate,
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2)
    }


def apply_bulk_discount(
    quantity: int,
    unit_price: float
) -> dict:
    """
    Apply bulk purchase discount.
    
    Args:
        quantity: Number of units
        unit_price: Price per unit
        
    Returns:
        dict: Discounted pricing
        
    Example:
        result = apply_bulk_discount(10, 100.00)
        # 10+ units get 10% discount
    """
    
    # Define discount tiers
    if quantity >= 50:
        discount_percent = 20
    elif quantity >= 20:
        discount_percent = 15
    elif quantity >= 10:
        discount_percent = 10
    elif quantity >= 5:
        discount_percent = 5
    else:
        discount_percent = 0
    
    original_total = quantity * unit_price
    
    if discount_percent > 0:
        discount_result = calculate_discount(original_total, discount_percent)
        final_total = discount_result["final_price"]
        savings = discount_result["savings"]
    else:
        final_total = original_total
        savings = 0
    
    return {
        "quantity": quantity,
        "unit_price": unit_price,
        "original_total": round(original_total, 2),
        "discount_percent": discount_percent,
        "final_total": round(final_total, 2),
        "savings": round(savings, 2),
        "effective_unit_price": round(final_total / quantity, 2)
    }