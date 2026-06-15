"""
Shopping Cart Routes

Handles cart operations: add, remove, update quantities.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.config.database import get_db
from app.models.cart_model import CartItem
from app.models.product_model import Product
from app.models.user_model import User
from app.schemas.cart_schema import CartCreate, CartUpdate, CartResponse
from app.auth.auth_bearer import JWTBearer

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_item: CartCreate,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Add a product to user's shopping cart.
    
    - **user_id**: ID of the user
    - **product_id**: ID of the product
    - **quantity**: Number of units (1-100)
    """
    
    # Verify token matches user
    token_email = token_data.get("sub")
    result = await db.execute(select(User).where(User.email == token_email))
    token_user = result.scalar_one_or_none()
    
    if not token_user or token_user.id != cart_item.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add items to another user's cart"
        )
    
    # Verify product exists and has stock
    result = await db.execute(select(Product).where(Product.id == cart_item.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {cart_item.product_id} not found"
        )
    
    if product.stock_quantity < cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {product.stock_quantity} available"
    )
    
    # Check if item already in cart
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == cart_item.user_id,
            CartItem.product_id == cart_item.product_id
        )
    )
    existing_item = result.scalar_one_or_none()
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + cart_item.quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Only {product.stock_quantity} available"
            )
        
        existing_item.quantity = new_quantity
        await db.commit()
        await db.refresh(existing_item)
        return existing_item
    
    # Create new cart item
    new_cart_item = CartItem(
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    
    db.add(new_cart_item)
    await db.commit()
    await db.refresh(new_cart_item)
    
    return new_cart_item


@router.get("/{user_id}")
async def get_cart(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Get user's shopping cart with product details.
    
    - **user_id**: ID of the user (must match authenticated user)
    """
    
    # Verify token matches user
    token_email = token_data.get("sub")
    result = await db.execute(select(User).where(User.email == token_email))
    token_user = result.scalar_one_or_none()
    
    role = token_data.get("role")
    
    if token_user.id != user_id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view another user's cart"
        )
    
    # Get cart items
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    cart_items = result.scalars().all()
    
    # Enrich with product details
    cart_data = []
    total = 0
    
    for item in cart_items:
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        
        if product:
            subtotal = product.price * item.quantity
            total += subtotal
            
            cart_data.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name,
                "product_price": product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
                "in_stock": product.stock_quantity >= item.quantity
            })
    
    return {
        "user_id": user_id,
        "items": cart_data,
        "total_items": len(cart_data),
        "total_amount": total
    }


@router.put("/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    update_data: CartUpdate,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Update quantity of a cart item.
    
    - **item_id**: ID of the cart item
    - **quantity**: New quantity (1-100)
    """
    
    # Get cart item
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify ownership
    result = await db.execute(select(User).where(User.id == cart_item.user_id))
    user = result.scalar_one_or_none()
    token_email = token_data.get("sub")
    
    if user.email != token_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify another user's cart"
        )
    
    # Check stock availability
    result = await db.execute(select(Product).where(Product.id == cart_item.product_id))
    product = result.scalar_one_or_none()
    
    if product and product.stock_quantity < update_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {product.stock_quantity} available"
        )
    
    # Update quantity
    cart_item.quantity = update_data.quantity
    await db.commit()
    await db.refresh(cart_item)
    
    return cart_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Remove an item from cart.
    
    - **item_id**: ID of the cart item to remove
    """
    
    # Get cart item
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify ownership
    result = await db.execute(select(User).where(User.id == cart_item.user_id))
    user = result.scalar_one_or_none()
    token_email = token_data.get("sub")
    
    if user.email != token_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove from another user's cart"
        )
    
    await db.delete(cart_item)
    await db.commit()


@router.delete("/clear/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Clear all items from user's cart.
    
    - **user_id**: ID of the user
    """
    
    # Verify ownership
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    token_email = token_data.get("sub")
    role = token_data.get("role")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.email != token_email and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot clear another user's cart"
        )
    
    await db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await db.commit()