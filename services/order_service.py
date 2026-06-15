"""
Order Service

Handles business logic for order processing:
- Order creation and validation
- Order status management
- Order history retrieval
- Cancellation and refunds
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.product_model import Product
from app.models.user_model import User
from app.services.inventory_service import InventoryService


class OrderService:
    """
    Service class for order operations.
    """
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: int,
        items: List[Dict[str, int]]
    ) -> Order:
        """
        Create a new order from cart items.
        
        Args:
            db: Database session
            user_id: User ID
            items: List of {product_id, quantity}
            
        Returns:
            Order: Created order object
            
        Raises:
            HTTPException: If validation fails
        """
        
        # Verify user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create order
        new_order = Order(
            user_id=user_id,
            status=Order.STATUS_PENDING,
            total_amount=0
        )
        
        db.add(new_order)
        await db.flush()  # Get ID without committing
        
        total_amount = 0.0
        order_items = []
        
        # Process each item
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            
            # Get product
            result = await db.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )
            
            # Check stock
            if product.stock_quantity < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}"
                )
            
            # Reserve stock
            await InventoryService.reduce_stock(db, product_id, quantity)
            
            # Create order item
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product_id,
                quantity=quantity,
                price=product.price
            )
            
            db.add(order_item)
            order_items.append(order_item)
            total_amount += product.price * quantity
        
        # Update order total
        new_order.total_amount = total_amount
        new_order.items = order_items
        
        await db.commit()
        await db.refresh(new_order)
        
        return new_order
    
    @staticmethod
    async def get_order_by_id(
        db: AsyncSession,
        order_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> Optional[Order]:
        """
        Get order by ID with access control.
        
        Args:
            db: Database session
            order_id: Order ID
            user_id: User ID for access check
            is_admin: Whether user is admin
            
        Returns:
            Order: Order if found and accessible
            
        Raises:
            HTTPException: If order not found or access denied
        """
        
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        # Check access
        if not is_admin and order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Load items
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        order.items = result.scalars().all()
        
        return order
    
    @staticmethod
    async def get_user_orders(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Get all orders for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Pagination offset
            limit: Results per page
            
        Returns:
            List[Order]: User's orders
        """
        
        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        )
        
        orders = result.scalars().all()
        
        # Load items for each order
        for order in orders:
            result = await db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            order.items = result.scalars().all()
        
        return orders
    
    @staticmethod
    async def get_all_orders(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[Order]:
        """
        Get all orders (admin only).
        
        Args:
            db: Database session
            skip: Pagination offset
            limit: Results per page
            status_filter: Filter by status
            
        Returns:
            List[Order]: All orders
        """
        
        query = select(Order)
        
        if status_filter:
            query = query.where(Order.status == status_filter)
        
        query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
        
        result = await db.execute(query)
        orders = result.scalars().all()
        
        # Load items for each order
        for order in orders:
            result = await db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            order.items = result.scalars().all()
        
        return orders
    
    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: int,
        new_status: str
    ) -> Order:
        """
        Update order status.
        
        Args:
            db: Database session
            order_id: Order ID
            new_status: New status value
            
        Returns:
            Order: Updated order
            
        Raises:
            HTTPException: If status invalid
        """
        
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        if new_status not in Order.VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {Order.VALID_STATUSES}"
            )
        
        order.status = new_status
        await db.commit()
        await db.refresh(order)
        
        return order
    
    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order_id: int,
        user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> Order:
        """
        Cancel an order and restore stock.
        
        Args:
            db: Database session
            order_id: Order ID
            user_id: User ID for access check
            is_admin: Whether user is admin
            
        Returns:
            Order: Cancelled order
        """
        
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        # Check access
        if not is_admin and order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if cancellable
        if not order.can_cancel():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order with status '{order.status}' cannot be cancelled"
            )
        
        # Load items to restore stock
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        items = result.scalars().all()
        
        # Restore stock for each item
        for item in items:
            await InventoryService.increase_stock(db, item.product_id, item.quantity)
        
        # Cancel order
        order.status = Order.STATUS_CANCELLED
        await db.commit()
        await db.refresh(order)
        
        return order
    
    @staticmethod
    async def get_order_stats(
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get order statistics.
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            Dict: Order statistics
        """
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Total orders
        total_result = await db.execute(
            select(func.count()).select_from(Order)
        )
        total_orders = total_result.scalar() or 0
        
        # Orders in date range
        recent_result = await db.execute(
            select(func.count()).select_from(Order).where(
                Order.created_at >= start_date
            )
        )
        recent_orders = recent_result.scalar() or 0
        
        # Average order value
        avg_result = await db.execute(
            select(func.avg(Order.total_amount)).where(
                Order.status != Order.STATUS_CANCELLED
            )
        )
        avg_order_value = avg_result.scalar() or 0.0
        
        # Total revenue
        revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.status != Order.STATUS_CANCELLED
            )
        )
        total_revenue = revenue_result.scalar() or 0.0
        
        # Status breakdown
        status_result = await db.execute(
            select(Order.status, func.count()).group_by(Order.status)
        )
        status_breakdown = {status: count for status, count in status_result.all()}
        
        return {
            "total_orders": total_orders,
            f"recent_orders_{days}d": recent_orders,
            "average_order_value": round(avg_order_value, 2),
            "total_revenue": round(total_revenue, 2),
            "status_breakdown": status_breakdown
        }