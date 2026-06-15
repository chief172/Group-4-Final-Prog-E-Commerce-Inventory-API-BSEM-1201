"""
Admin Routes - Complete System Control

This module provides full administrative access to:
- User management (view, create, update, delete, activate/deactivate)
- Product management (full CRUD, bulk operations)
- Category management (full CRUD)
- Order management (view all, status updates, cancel)
- System analytics and reports
- Inventory management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os

from app.config.database import get_db
from app.models.user_model import User
from app.models.product_model import Product
from app.models.category_model import Category
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.order_schema import OrderResponse, OrderUpdate
from app.auth.password_handler import hash_password
from app.auth.role import admin_required
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# USER MANAGEMENT (Full Control)
# ============================================================================

@router.get("/users", response_model=List[UserResponse])
async def admin_get_all_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Records per page"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    role: Optional[str] = Query(None, description="Filter by role (admin/customer)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    _: dict = Depends(admin_required)
):
    """
    Get all users with filtering and pagination (Admin only).
    
    - **search**: Search in username and email
    - **role**: Filter by 'admin' or 'customer'
    - **is_active**: Filter by active status
    """
    
    query = select(User)
    
    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    query = query.offset(skip).limit(limit).order_by(User.id)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def admin_get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Get specific user by ID (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Create a new user (Admin only). Can create admin accounts."""
    
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role if hasattr(user_data, 'role') else "customer",
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Update any user (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    if user_data.username:
        # Check if username is taken
        result = await db.execute(
            select(User).where(
                User.username == user_data.username,
                User.id != user_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_data.username
    
    if user_data.email:
        result = await db.execute(
            select(User).where(
                User.email == user_data.email,
                User.id != user_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email
    
    if user_data.role:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Permanently delete a user (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent deleting the last admin
    if user.role == "admin":
        admin_count = await db.execute(select(func.count()).select_from(User).where(User.role == "admin"))
        if admin_count.scalar() <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user"
            )
    
    await db.delete(user)
    await db.commit()


@router.put("/users/{user_id}/activate")
async def admin_activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Activate a user account (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user.is_active = True
    await db.commit()
    
    return {"message": f"User {user.username} activated successfully"}


@router.put("/users/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Deactivate a user account (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent deactivating yourself
    # (Would need current user ID from token)
    
    user.is_active = False
    await db.commit()
    
    return {"message": f"User {user.username} deactivated successfully"}


@router.put("/users/{user_id}/make-admin")
async def admin_make_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Promote a user to admin (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    user.role = "admin"
    await db.commit()
    
    return {"message": f"User {user.username} is now an admin"}


@router.put("/users/{user_id}/remove-admin")
async def admin_remove_admin_role(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Remove admin role from a user (Admin only)."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent removing your own admin role
    # (Would need current user ID from token)
    
    user.role = "customer"
    await db.commit()
    
    return {"message": f"Admin role removed from {user.username}"}


# ============================================================================
# PRODUCT MANAGEMENT (Full Control)
# ============================================================================

@router.get("/products", response_model=List[ProductResponse])
async def admin_get_all_products(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock_only: bool = False,
    out_of_stock_only: bool = False,
    _: dict = Depends(admin_required)
):
    """Get all products with advanced filtering (Admin only)."""
    
    query = select(Product)
    
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if low_stock_only:
        query = query.where(Product.stock_quantity <= 5, Product.stock_quantity > 0)
    
    if out_of_stock_only:
        query = query.where(Product.stock_quantity == 0)
    
    query = query.offset(skip).limit(limit).order_by(Product.id)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Create a new product (Admin only)."""
    
    # Verify category exists
    result = await db.execute(select(Category).where(Category.id == product.category_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {product.category_id} not found"
        )
    
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        is_active=True
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    return new_product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def admin_update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Update any product (Admin only)."""
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    if product_data.name:
        product.name = product_data.name
    if product_data.description:
        product.description = product_data.description
    if product_data.price:
        product.price = product_data.price
    if product_data.stock_quantity is not None:
        product.stock_quantity = product_data.stock_quantity
    if product_data.category_id:
        # Verify new category exists
        result = await db.execute(select(Category).where(Category.id == product_data.category_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_data.category_id} not found"
            )
        product.category_id = product_data.category_id
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Delete any product (Admin only)."""
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    await db.delete(product)
    await db.commit()


@router.post("/products/bulk-stock-update")
async def admin_bulk_stock_update(
    updates: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Bulk update product stock quantities (Admin only)."""
    
    results = {"success": [], "failed": []}
    
    for update in updates:
        product_id = update.get("product_id")
        new_stock = update.get("stock_quantity")
        
        if not product_id or new_stock is None:
            results["failed"].append({"product_id": product_id, "reason": "Missing product_id or stock_quantity"})
            continue
        
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            results["failed"].append({"product_id": product_id, "reason": "Product not found"})
            continue
        
        product.stock_quantity = new_stock
        results["success"].append({"product_id": product_id, "name": product.name, "new_stock": new_stock})
    
    await db.commit()
    
    return results


# ============================================================================
# CATEGORY MANAGEMENT (Full Control)
# ============================================================================

@router.get("/categories", response_model=List[CategoryResponse])
async def admin_get_all_categories(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Get all categories (Admin only)."""
    
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Create a new category (Admin only)."""
    
    # Check if category exists
    result = await db.execute(select(Category).where(Category.name == category.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category.name}' already exists"
        )
    
    new_category = Category(
        name=category.name,
        description=category.description
    )
    
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return new_category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def admin_update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Update any category (Admin only)."""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    if category_data.name:
        # Check if new name is taken
        result = await db.execute(
            select(Category).where(
                Category.name == category_data.name,
                Category.id != category_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_data.name}' already exists"
            )
        category.name = category_data.name
    
    if category_data.description:
        category.description = category_data.description
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Delete a category (Admin only). Products will have category_id set to NULL."""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    await db.delete(category)
    await db.commit()


# ============================================================================
# ORDER MANAGEMENT (Full Control)
# ============================================================================

@router.get("/orders", response_model=List[OrderResponse])
async def admin_get_all_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    _: dict = Depends(admin_required)
):
    """Get all orders with filtering (Admin only)."""
    
    query = select(Order)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    if user_id:
        query = query.where(Order.user_id == user_id)
    
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Load items for each order
    for order in orders:
        result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        order.items = result.scalars().all()
    
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def admin_get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Get any order by ID (Admin only)."""
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    # Load items
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    order.items = result.scalars().all()
    
    return order


@router.put("/orders/{order_id}/status")
async def admin_update_order_status(
    order_id: int,
    status_value: str = Query(..., description="New status"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Update any order status (Admin only)."""
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    valid_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    if status_value not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    order.status = status_value
    await db.commit()
    
    return {"message": f"Order #{order_id} status updated to {status_value}"}


@router.post("/orders/{order_id}/cancel")
async def admin_cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Cancel any order and restore stock (Admin only)."""
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    if order.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already cancelled"
        )
    
    # Restore stock for each item
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    items = result.scalars().all()
    
    for item in items:
        product_result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = product_result.scalar_one_or_none()
        if product:
            product.stock_quantity += item.quantity
    
    order.status = "Cancelled"
    await db.commit()
    
    return {"message": f"Order #{order_id} cancelled successfully"}


# ============================================================================
# DASHBOARD & ANALYTICS (Full Insights)
# ============================================================================

@router.get("/dashboard/stats")
async def admin_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Get comprehensive dashboard statistics (Admin only)."""
    
    # User stats
    total_users = await db.execute(select(func.count()).select_from(User))
    total_users = total_users.scalar() or 0
    
    active_users = await db.execute(select(func.count()).select_from(User).where(User.is_active == True))
    active_users = active_users.scalar() or 0
    
    admin_users = await db.execute(select(func.count()).select_from(User).where(User.role == "admin"))
    admin_users = admin_users.scalar() or 0
    
    # Product stats
    total_products = await db.execute(select(func.count()).select_from(Product))
    total_products = total_products.scalar() or 0
    
    active_products = await db.execute(select(func.count()).select_from(Product).where(Product.is_active == True))
    active_products = active_products.scalar() or 0
    
    low_stock = await db.execute(
        select(func.count()).select_from(Product).where(
            Product.stock_quantity <= 5,
            Product.stock_quantity > 0,
            Product.is_active == True
        )
    )
    low_stock = low_stock.scalar() or 0
    
    out_of_stock = await db.execute(
        select(func.count()).select_from(Product).where(
            Product.stock_quantity == 0,
            Product.is_active == True
        )
    )
    out_of_stock = out_of_stock.scalar() or 0
    
    total_stock_value = await db.execute(
        select(func.sum(Product.price * Product.stock_quantity))
    )
    total_stock_value = total_stock_value.scalar() or 0.0
    
    # Order stats
    total_orders = await db.execute(select(func.count()).select_from(Order))
    total_orders = total_orders.scalar() or 0
    
    total_revenue = await db.execute(
        select(func.sum(Order.total_amount)).where(Order.status != "Cancelled")
    )
    total_revenue = total_revenue.scalar() or 0.0
    
    # Order status breakdown
    status_result = await db.execute(
        select(Order.status, func.count()).group_by(Order.status)
    )
    order_status = {status: count for status, count in status_result.all()}
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    new_users_7d = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= seven_days_ago)
    )
    new_users_7d = new_users_7d.scalar() or 0
    
    new_orders_7d = await db.execute(
        select(func.count()).select_from(Order).where(Order.created_at >= seven_days_ago)
    )
    new_orders_7d = new_orders_7d.scalar() or 0
    
    revenue_7d = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.created_at >= seven_days_ago,
            Order.status != "Cancelled"
        )
    )
    revenue_7d = revenue_7d.scalar() or 0.0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users,
            "customers": total_users - admin_users,
            "new_last_7d": new_users_7d
        },
        "products": {
            "total": total_products,
            "active": active_products,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "healthy_stock": total_products - low_stock - out_of_stock,
            "total_inventory_value": round(total_stock_value, 2)
        },
        "orders": {
            "total": total_orders,
            "new_last_7d": new_orders_7d,
            "status_breakdown": order_status
        },
        "revenue": {
            "total": round(total_revenue, 2),
            "last_7_days": round(revenue_7d, 2)
        }
    }


@router.get("/dashboard/top-products")
async def admin_top_products(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
    days: Optional[int] = Query(None, description="Last N days"),
    _: dict = Depends(admin_required)
):
    """Get top selling products (Admin only)."""
    
    query = select(
        Product.id,
        Product.name,
        Product.price,
        func.sum(OrderItem.quantity).label("total_sold"),
        func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue"),
        func.count(Order.id.distinct()).label("unique_orders")
    ).join(
        OrderItem, Product.id == OrderItem.product_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).where(
        Order.status != "Cancelled"
    )
    
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
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
            "total_revenue": round(row.total_revenue or 0, 2),
            "unique_orders": row.unique_orders or 0
        }
        for row in rows
    ]


@router.get("/dashboard/sales-by-category")
async def admin_sales_by_category(
    db: AsyncSession = Depends(get_db),
    days: Optional[int] = Query(None, description="Last N days"),
    _: dict = Depends(admin_required)
):
    """Get sales breakdown by category (Admin only)."""
    
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
        Order.status != "Cancelled"
    )
    
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
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


@router.get("/dashboard/daily-sales")
async def admin_daily_sales(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=90),
    _: dict = Depends(admin_required)
):
    """Get daily sales for the last N days (Admin only)."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("total_sales")
        )
        .where(
            Order.created_at >= start_date,
            Order.status != "Cancelled"
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    
    rows = result.all()
    
    # Fill in missing dates
    sales_by_date = {str(row.date): {
        "order_count": row.order_count or 0,
        "total_sales": float(row.total_sales or 0)
    } for row in rows}
    
    sales_data = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        date_str = str(date)
        sales_data.append({
            "date": date_str,
            "order_count": sales_by_date.get(date_str, {}).get("order_count", 0),
            "total_sales": sales_by_date.get(date_str, {}).get("total_sales", 0.0)
        })
    
    return sorted(sales_data, key=lambda x: x["date"])


@router.get("/dashboard/revenue-summary")
async def admin_revenue_summary(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Get revenue summary for different time periods (Admin only)."""
    
    now = datetime.utcnow()
    
    # Today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # This week
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # This month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # This year
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    async def get_revenue(start_date):
        result = await db.execute(
            select(func.sum(Order.total_amount))
            .where(
                Order.created_at >= start_date,
                Order.status != "Cancelled"
            )
        )
        return result.scalar() or 0.0
    
    return {
        "today": round(await get_revenue(today_start), 2),
        "this_week": round(await get_revenue(week_start), 2),
        "this_month": round(await get_revenue(month_start), 2),
        "this_year": round(await get_revenue(year_start), 2),
        "all_time": round(await get_revenue(datetime.min), 2)
    }


# ============================================================================
# SYSTEM HEALTH & INFO
# ============================================================================

@router.get("/system/info")
async def admin_system_info(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Get system information (Admin only)."""
    import os
    
    # Database size
    db_size_result = await db.execute(
        text("SELECT pg_database_size(current_database())")
    )
    db_size = db_size_result.scalar() or 0
    
    # Table counts
    table_counts = {}
    tables = ["users", "categories", "products", "cart_items", "orders", "order_items"]
    
    for table in tables:
        result = await db.execute(select(func.count()).select_from(text(table)))
        table_counts[table] = result.scalar() or 0
    
    return {
        "api_version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": {
            "size_bytes": db_size,
            "size_mb": round(db_size / 1024 / 1024, 2),
            "table_counts": table_counts
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/system/seed-demo-data")
async def admin_seed_demo_data(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """Seed demo data for testing (Admin only)."""
    
    from database.seed_data import seed_database
    await seed_database()
    
    return {"message": "Demo data seeded successfully"}