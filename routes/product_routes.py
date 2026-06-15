"""
Product Management Routes

Handles CRUD operations for inventory products.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.config.database import get_db
from app.models.product_model import Product
from app.models.category_model import Category
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.auth.role import admin_required

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Create a new product (Admin only).
    
    - **name**: Product name (2-255 characters)
    - **description**: Product description
    - **price**: Selling price (must be > 0)
    - **stock_quantity**: Initial inventory (>= 0)
    - **category_id**: Category this product belongs to
    """
    
    # Verify category exists
    result = await db.execute(select(Category).where(Category.id == product.category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {product.category_id} not found"
        )
    
    # Check if product name already exists in this category
    result = await db.execute(
        select(Product).where(
            Product.name == product.name,
            Product.category_id == product.category_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product '{product.name}' already exists in this category"
        )
    
    # Create new product
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


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    in_stock_only: bool = Query(False, description="Show only in-stock products")
):
    """
    Get all products with filtering and pagination.
    
    - **skip**: Pagination offset
    - **limit**: Results per page (max 200)
    - **category_id**: Filter by category
    - **search**: Search in name and description
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **in_stock_only**: Show only products with stock > 0
    """
    
    # Build query
    query = select(Product).where(Product.is_active == True)
    
    # Apply filters
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    if min_price:
        query = query.where(Product.price >= min_price)
    
    if max_price:
        query = query.where(Product.price <= max_price)
    
    if in_stock_only:
        query = query.where(Product.stock_quantity > 0)
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(Product.name)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products


@router.get("/low-stock")
async def get_low_stock_products(
    db: AsyncSession = Depends(get_db),
    threshold: int = Query(5, ge=1, le=50, description="Stock threshold"),
    _: dict = Depends(admin_required)
):
    """
    Get products with low stock (Admin only).
    
    - **threshold**: Stock level threshold (default: 5)
    """
    
    result = await db.execute(
        select(Product).where(
            Product.stock_quantity <= threshold,
            Product.stock_quantity > 0,
            Product.is_active == True
        ).order_by(Product.stock_quantity)
    )
    products = result.scalars().all()
    
    return {
        "threshold": threshold,
        "count": len(products),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "stock_quantity": p.stock_quantity,
                "price": p.price
            }
            for p in products
        ]
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product by ID.
    
    - **product_id**: ID of the product to retrieve
    """
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Product is no longer available"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Update product information (Admin only).
    
    - **product_id**: ID of the product to update
    """
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Verify new category exists if changed
    if product_data.category_id != product.category_id:
        result = await db.execute(
            select(Category).where(Category.id == product_data.category_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_data.category_id} not found"
            )
    
    # Update fields
    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.stock_quantity = product_data.stock_quantity
    product.category_id = product_data.category_id
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_required)
):
    """
    Delete a product (Admin only).
    
    This permanently removes the product from inventory.
    """
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    await db.delete(product)
    await db.commit()