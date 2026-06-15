"""
Inventory Service

Handles business logic for inventory management:
- Stock tracking and updates
- Low stock alerts
- Product availability checks
- Stock reservations for orders
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional

from app.models.product_model import Product


class InventoryService:
    """
    Service class for inventory operations.
    """
    
    # Stock threshold for low stock alerts
    LOW_STOCK_THRESHOLD = 5
    
    @staticmethod
    async def check_stock_availability(
        db: AsyncSession,
        product_id: int,
        requested_quantity: int
    ) -> bool:
        """
        Check if product has sufficient stock.
        
        Args:
            db: Database session
            product_id: Product ID
            requested_quantity: Quantity requested
            
        Returns:
            bool: True if sufficient stock exists
        """
        
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            return False
        
        return product.stock_quantity >= requested_quantity
    
    @staticmethod
    async def reduce_stock(
        db: AsyncSession,
        product_id: int,
        quantity: int
    ) -> bool:
        """
        Reduce product stock by given quantity.
        
        Args:
            db: Database session
            product_id: Product ID
            quantity: Quantity to reduce
            
        Returns:
            bool: True if successful
            
        Raises:
            HTTPException: If insufficient stock
        """
        
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        if product.stock_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. "
                       f"Available: {product.stock_quantity}, Requested: {quantity}"
            )
        
        product.stock_quantity -= quantity
        await db.commit()
        
        return True
    
    @staticmethod
    async def increase_stock(
        db: AsyncSession,
        product_id: int,
        quantity: int
    ) -> bool:
        """
        Increase product stock (e.g., when order is cancelled).
        
        Args:
            db: Database session
            product_id: Product ID
            quantity: Quantity to add
            
        Returns:
            bool: True if successful
        """
        
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        product.stock_quantity += quantity
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_low_stock_products(
        db: AsyncSession,
        threshold: int = LOW_STOCK_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Get products with stock below threshold.
        
        Args:
            db: Database session
            threshold: Stock threshold
            
        Returns:
            List: Products with low stock
        """
        
        result = await db.execute(
            select(Product).where(
                Product.stock_quantity <= threshold,
                Product.stock_quantity > 0,
                Product.is_active == True
            ).order_by(Product.stock_quantity)
        )
        
        products = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "stock_quantity": p.stock_quantity,
                "price": p.price,
                "needs_reorder": p.stock_quantity <= 3
            }
            for p in products
        ]
    
    @staticmethod
    async def get_out_of_stock_products(
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get products that are out of stock.
        
        Args:
            db: Database session
            
        Returns:
            List: Out of stock products
        """
        
        result = await db.execute(
            select(Product).where(
                Product.stock_quantity == 0,
                Product.is_active == True
            ).order_by(Product.name)
        )
        
        products = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category_id": p.category_id
            }
            for p in products
        ]
    
    @staticmethod
    async def get_inventory_summary(
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get inventory summary statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dict: Inventory statistics
        """
        
        # Total products
        total_result = await db.execute(
            select(func.count()).select_from(Product)
        )
        total_products = total_result.scalar() or 0
        
        # Total stock value
        value_result = await db.execute(
            select(func.sum(Product.price * Product.stock_quantity))
        )
        total_value = value_result.scalar() or 0.0
        
        # Low stock count
        low_stock_result = await db.execute(
            select(func.count()).select_from(Product).where(
                Product.stock_quantity <= InventoryService.LOW_STOCK_THRESHOLD,
                Product.stock_quantity > 0
            )
        )
        low_stock_count = low_stock_result.scalar() or 0
        
        # Out of stock count
        out_of_stock_result = await db.execute(
            select(func.count()).select_from(Product).where(
                Product.stock_quantity == 0
            )
        )
        out_of_stock_count = out_of_stock_result.scalar() or 0
        
        # In stock count
        in_stock_result = await db.execute(
            select(func.count()).select_from(Product).where(
                Product.stock_quantity > 0
            )
        )
        in_stock_count = in_stock_result.scalar() or 0
        
        return {
            "total_products": total_products,
            "total_inventory_value": round(total_value, 2),
            "in_stock_count": in_stock_count,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "healthy_stock_count": total_products - low_stock_count - out_of_stock_count
        }