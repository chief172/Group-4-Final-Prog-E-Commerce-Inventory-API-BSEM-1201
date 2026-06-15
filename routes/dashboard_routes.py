"""
Dashboard Routes

Provides analytics and statistics for admin dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta

from app.config.database import get_db
from app.models.user_model import User
from app.models.category_model import Category
from app.models.product_model import Product
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.auth.role import admin_required

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Get dashboard statistics (Admin only).
    
    Returns counts and totals for monitoring the platform.
    """
    
    # Get total counts
    total_users_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_result.scalar() or 0
    
    total_categories_result = await db.execute(select(func.count()).select_from(Category))
    total_categories = total_categories_result.scalar() or 0
    
    total_products_result = await db.execute(select(func.count()).select_from(Product))
    total_products = total_products_result.scalar() or 0
    
    total_orders_result = await db.execute(select(func.count()).select_from(Order))
    total_orders = total_orders_result.scalar() or 0
    
    # Get sales metrics
    total_sales_result = await db.execute(
        select(func.sum(Order.total_amount)).where(Order.status != "Cancelled")
    )
    total_sales = total_sales_result.scalar() or 0.0
    
    # Get low stock products
    low_stock_result = await db.execute(
        select(func.count()).select_from(Product).where(
            Product.stock_quantity <= 5,
            Product.stock_quantity > 0
        )
    )
    low_stock_count = low_stock_result.scalar() or 0
    
    out_of_stock_result = await db.execute(
        select(func.count()).select_from(Product).where(Product.stock_quantity == 0)
    )
    out_of_stock_count = out_of_stock_result.scalar() or 0
    
    # Recent activity
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    recent_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= thirty_days_ago)
    )
    recent_users = recent_users_result.scalar() or 0
    
    recent_orders_result = await db.execute(
        select(func.count()).select_from(Order).where(Order.created_at >= thirty_days_ago)
    )
    recent_orders = recent_orders_result.scalar() or 0
    
    # Order status breakdown
    order_status_result = await db.execute(
        select(Order.status, func.count()).group_by(Order.status)
    )
    order_status = {status: count for status, count in order_status_result.all()}
    
    return {
        "summary": {
            "total_users": total_users,
            "total_categories": total_categories,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_sales": round(total_sales, 2)
        },
        "inventory": {
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "healthy_stock_count": total_products - low_stock_count - out_of_stock_count
        },
        "activity": {
            "new_users_30d": recent_users,
            "new_orders_30d": recent_orders
        },
        "order_status": order_status
    }


@router.get("/sales/top-products")
async def get_top_products(
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    _: dict = Depends(admin_required)
):
    """
    Get top-selling products (Admin only).
    
    - **limit**: Number of products to return (default: 10)
    """
    
    result = await db.execute(
        select(
            Product.id,
            Product.name,
            Product.price,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue")
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
    )
    
    products = []
    for row in result.all():
        products.append({
            "id": row.id,
            "name": row.name,
            "price": row.price,
            "total_sold": row.total_sold or 0,
            "total_revenue": round(row.total_revenue or 0, 2)
        })
    
    return products


@router.get("/sales/by-category")
async def get_sales_by_category(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Get sales breakdown by category (Admin only).
    """
    
    result = await db.execute(
        select(
            Category.id,
            Category.name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue")
        )
        .join(Product, Category.id == Product.category_id)
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Category.id)
        .order_by(func.sum(OrderItem.quantity).desc())
    )
    
    categories = []
    for row in result.all():
        categories.append({
            "id": row.id,
            "name": row.name,
            "total_sold": row.total_sold or 0,
            "total_revenue": round(row.total_revenue or 0, 2)
        })
    
    return categories


@router.get("/sales/daily")
async def get_daily_sales(
    db: AsyncSession = Depends(get_db),
    days: int = 7,
    _: dict = Depends(admin_required)
):
    """
    Get daily sales for the last N days (Admin only).
    
    - **days**: Number of days to analyze (default: 7)
    """
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("total_sales")
        )
        .where(Order.created_at >= start_date)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    
    sales_data = []
    for row in result.all():
        sales_data.append({
            "date": str(row.date),
            "order_count": row.order_count or 0,
            "total_sales": round(row.total_sales or 0, 2)
        })
    
    return {
        "period_days": days,
        "data": sales_data
    }