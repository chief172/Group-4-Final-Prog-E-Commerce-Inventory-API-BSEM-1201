"""
Analytics Service

Handles business logic for analytics and reporting:
- Sales reports
- Product performance
- Category analysis
- Dashboard statistics
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.product_model import Product
from app.models.category_model import Category
from app.models.user_model import User


class AnalyticsService:
    """
    Service class for analytics operations.
    """
    
    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get main dashboard statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dict: Dashboard statistics
        """
        
        # User counts
        total_users_result = await db.execute(
            select(func.count()).select_from(User)
        )
        total_users = total_users_result.scalar() or 0
        
        active_users_result = await db.execute(
            select(func.count()).select_from(User).where(User.is_active == True)
        )
        active_users = active_users_result.scalar() or 0
        
        # Product counts
        total_products_result = await db.execute(
            select(func.count()).select_from(Product)
        )
        total_products = total_products_result.scalar() or 0
        
        # Order counts
        total_orders_result = await db.execute(
            select(func.count()).select_from(Order)
        )
        total_orders = total_orders_result.scalar() or 0
        
        # Revenue
        revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.status != Order.STATUS_CANCELLED
            )
        )
        total_revenue = revenue_result.scalar() or 0.0
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        recent_orders_result = await db.execute(
            select(func.count()).select_from(Order).where(
                Order.created_at >= seven_days_ago
            )
        )
        recent_orders = recent_orders_result.scalar() or 0
        
        recent_users_result = await db.execute(
            select(func.count()).select_from(User).where(
                User.created_at >= seven_days_ago
            )
        )
        recent_users = recent_users_result.scalar() or 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "new_last_7d": recent_users
            },
            "products": {
                "total": total_products
            },
            "orders": {
                "total": total_orders,
                "new_last_7d": recent_orders
            },
            "revenue": {
                "total": round(total_revenue, 2)
            }
        }
    
    @staticmethod
    async def get_top_products(
        db: AsyncSession,
        limit: int = 10,
        days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top selling products.
        
        Args:
            db: Database session
            limit: Number of products to return
            days: Only consider orders within last N days
            
        Returns:
            List: Top products with sales data
        """
        
        query = select(
            Product.id,
            Product.name,
            Product.price,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue")
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).where(
            Order.status != Order.STATUS_CANCELLED
        )
        
        if days:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.where(Order.created_at >= start_date)
        
        query = query.group_by(Product.id).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "price": float(row.price),
                "total_sold": row.total_sold or 0,
                "total_revenue": round(row.total_revenue or 0, 2)
            }
            for row in rows
        ]
    
    @staticmethod
    async def get_sales_by_category(
        db: AsyncSession,
        days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sales breakdown by category.
        
        Args:
            db: Database session
            days: Only consider orders within last N days
            
        Returns:
            List: Category sales data
        """
        
        query = select(
            Category.id,
            Category.name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue")
        ).join(
            Product, Category.id == Product.category_id
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).where(
            Order.status != Order.STATUS_CANCELLED
        )
        
        if days:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.where(Order.created_at >= start_date)
        
        query = query.group_by(Category.id).order_by(
            func.sum(OrderItem.quantity).desc()
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "total_sold": row.total_sold or 0,
                "total_revenue": round(row.total_revenue or 0, 2)
            }
            for row in rows
        ]
    
    @staticmethod
    async def get_daily_sales(
        db: AsyncSession,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get daily sales for the last N days.
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            List: Daily sales data
        """
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        result = await db.execute(
            select(
                func.date(Order.created_at).label("date"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.total_amount).label("total_sales")
            )
            .where(
                Order.created_at >= start_date,
                Order.status != Order.STATUS_CANCELLED
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
        )
        
        rows = result.all()
        
        # Fill in missing dates with zeros
        sales_by_date = {str(row.date): {
            "order_count": row.order_count or 0,
            "total_sales": float(row.total_sales or 0)
        } for row in rows}
        
        sales_data = []
        for i in range(days):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).date()
            date_str = str(date)
            if date_str in sales_by_date:
                sales_data.append({
                    "date": date_str,
                    "order_count": sales_by_date[date_str]["order_count"],
                    "total_sales": sales_by_date[date_str]["total_sales"]
                })
            else:
                sales_data.append({
                    "date": date_str,
                    "order_count": 0,
                    "total_sales": 0.0
                })
        
        return sorted(sales_data, key=lambda x: x["date"])
    
    @staticmethod
    async def get_revenue_summary(
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get revenue summary for different time periods.
        
        Args:
            db: Database session
            
        Returns:
            Dict: Revenue by period
        """
        
        now = datetime.now(timezone.utc)
        
        # Today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # This week
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # This month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Helper function to get revenue for period
        async def get_revenue(start_date):
            result = await db.execute(
                select(func.sum(Order.total_amount))
                .where(
                    Order.created_at >= start_date,
                    Order.status != Order.STATUS_CANCELLED
                )
            )
            return result.scalar() or 0.0
        
        # Get revenues
        today_revenue = await get_revenue(today_start)
        week_revenue = await get_revenue(week_start)
        month_revenue = await get_revenue(month_start)
        
        # All time revenue
        all_time_result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.status != Order.STATUS_CANCELLED
            )
        )
        all_time_revenue = all_time_result.scalar() or 0.0
        
        return {
            "today": round(today_revenue, 2),
            "this_week": round(week_revenue, 2),
            "this_month": round(month_revenue, 2),
            "all_time": round(all_time_revenue, 2)
        }
    
    @staticmethod
    async def get_order_status_summary(
        db: AsyncSession
    ) -> Dict[str, int]:
        """
        Get summary of orders by status.
        
        Args:
            db: Database session
            
        Returns:
            Dict: Order counts by status
        """
        
        result = await db.execute(
            select(Order.status, func.count()).group_by(Order.status)
        )
        
        return {status: count for status, count in result.all()}