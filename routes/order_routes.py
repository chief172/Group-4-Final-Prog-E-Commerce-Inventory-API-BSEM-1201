"""
Order Management Routes

Handles order creation, retrieval, and status updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.config.database import get_db
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.product_model import Product
from app.models.user_model import User
from app.schemas.order_schema import OrderCreate, OrderResponse
from app.auth.auth_bearer import JWTBearer
from app.auth.role import admin_required

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Create a new order from cart items.
    
    This demonstrates async I/O with background email notifications.
    """
    
    # Verify user exists and matches token
    result = await db.execute(select(User).where(User.id == order.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    token_email = token_data.get("sub")
    if user.email != token_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create order for another user"
        )
    
    # Create order
    new_order = Order(
        user_id=order.user_id,
        status=Order.STATUS_PENDING,
        total_amount=0
    )
    
    db.add(new_order)
    await db.flush()  # Get ID without committing
    
    total_amount = 0
    items_count = 0
    
    # Process each order item
    for item in order.items:
        # Get product
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        
        # Check stock
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
        
        # Reduce stock
        product.stock_quantity -= item.quantity
        
        # Create order item
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        
        db.add(order_item)
        total_amount += product.price * item.quantity
        items_count += 1
    
    # Update order total
    new_order.total_amount = total_amount
    
    await db.commit()
    await db.refresh(new_order)
    
    # Load items for response
    result = await db.execute(
        select(OrderItem).where(OrderItem.order_id == new_order.id)
    )
    new_order.items = result.scalars().all()
    
    # Async I/O demonstration - would send email in background
    # background_tasks.add_task(send_order_confirmation, user.email, new_order.id)
    
    return new_order


@router.get("/", response_model=List[OrderResponse])
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(admin_required)
):
    """
    Get all orders (Admin only).
    
    - **skip**: Pagination offset
    - **limit**: Results per page
    """
    
    result = await db.execute(
        select(Order).offset(skip).limit(limit).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    
    # Load items for each order
    for order in orders:
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order.items = result.scalars().all()
    
    return orders


@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Get orders for a specific user.
    
    - **user_id**: ID of the user
    """
    
    # Verify user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify access
    token_email = token_data.get("sub")
    role = token_data.get("role")
    
    if user.email != token_email and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view another user's orders"
        )
    
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    
    # Load items for each order
    for order in orders:
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order.items = result.scalars().all()
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(JWTBearer())
):
    """
    Get order by ID.
    
    - **order_id**: ID of the order
    """
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify access
    result = await db.execute(select(User).where(User.id == order.user_id))
    user = result.scalar_one_or_none()
    token_email = token_data.get("sub")
    role = token_data.get("role")
    
    if user.email != token_email and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Load items
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    order.items = result.scalars().all()
    
    return order


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_value: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Update order status (Admin only).
    
    - **order_id**: ID of the order
    - **status_value**: New status (Pending/Processing/Shipped/Delivered/Cancelled)
    """
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if status_value not in Order.VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {Order.VALID_STATUSES}"
        )
    
    order.status = status_value
    await db.commit()
    
    return {
        "message": f"Order #{order_id} status updated to {status_value}",
        "order_id": order_id,
        "status": status_value
    }