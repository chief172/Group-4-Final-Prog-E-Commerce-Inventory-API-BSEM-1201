"""
Database Seeding Utility

This module provides functions to populate the database with initial data:
- Users (admin and regular customers)
- Categories (product categories)
- Products (sample products with Sierra Leone context)
- Orders (sample orders)

Use for:
- Development environment setup
- Testing data
- Demo purposes
"""

import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import AsyncSessionLocal, init_db
from app.auth.password_handler import hash_password
from app.models.user_model import User
from app.models.category_model import Category
from app.models.product_model import Product
from app.models.order_model import Order
from app.models.order_item_model import OrderItem


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def utc_now():
    """Get current UTC time with timezone"""
    return datetime.now(timezone.utc)


async def clear_database() -> None:
    """
    Clear all data from database tables.
    
    ⚠️ WARNING: This will delete all existing data!
    Use with caution, primarily for testing.
    """
    async with AsyncSessionLocal() as db:
        # Delete in reverse order to avoid foreign key constraints
        await db.execute("TRUNCATE TABLE order_items CASCADE")
        await db.execute("TRUNCATE TABLE orders CASCADE")
        await db.execute("TRUNCATE TABLE products CASCADE")
        await db.execute("TRUNCATE TABLE categories CASCADE")
        await db.execute("TRUNCATE TABLE users CASCADE")
        await db.commit()
    
    print("🗑️  Database cleared successfully")


# ============================================================================
# SEED USERS
# ============================================================================

async def seed_users(db: AsyncSession) -> list[User]:
    """
    Seed initial users into the database.
    
    Creates:
    - 1 Admin user
    - 3 Regular customers
    
    Returns:
        List of created User objects
    """
    print("👥 Seeding users...")
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@ecommerce.sl",
            "password": "Admin@123",
            "role": "admin"
        },
        {
            "username": "john_kabia",
            "email": "john@example.com",
            "password": "Customer@123",
            "role": "customer"
        },
        {
            "username": "fatmata_kamara",
            "email": "fatmata@example.com",
            "password": "Customer@123",
            "role": "customer"
        },
        {
            "username": "mohamed_bangura",
            "email": "mohamed@example.com",
            "password": "Customer@123",
            "role": "customer"
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=hash_password(user_data["password"]),
                role=user_data["role"],
                created_at=utc_now()
            )
            db.add(user)
            created_users.append(user)
            print(f"  ✅ Created user: {user_data['username']} ({user_data['role']})")
        else:
            created_users.append(existing)
            print(f"  ⏭️  User already exists: {user_data['username']}")
    
    await db.commit()
    
    # Refresh objects
    for user in created_users:
        await db.refresh(user)
    
    print(f"  📊 Total users: {len(created_users)}")
    return created_users


# ============================================================================
# SEED CATEGORIES
# ============================================================================

async def seed_categories(db: AsyncSession) -> list[Category]:
    """
    Seed product categories relevant to Sierra Leone.
    
    Creates categories for:
    - Local Food & Produce
    - Handicrafts & Art
    - Clothing & Textiles
    - Electronics
    - Home & Living
    
    Returns:
        List of created Category objects
    """
    print("\n📁 Seeding categories...")
    
    categories_data = [
        {
            "name": "Local Food & Produce",
            "description": "Fresh local produce including cassava, rice, vegetables, and fruits from Sierra Leonean farmers"
        },
        {
            "name": "Handicrafts & Art",
            "description": "Traditional Sierra Leonean crafts, wood carvings, tie-dye fabrics, and local artwork"
        },
        {
            "name": "Clothing & Textiles",
            "description": "Traditional and modern clothing, including country cloth, gowns, and accessories"
        },
        {
            "name": "Electronics",
            "description": "Mobile phones, accessories, and small electronics for everyday use"
        },
        {
            "name": "Home & Living",
            "description": "Household items, furniture, and home decor for modern Sierra Leonean homes"
        },
        {
            "name": "Health & Beauty",
            "description": "Natural beauty products, shea butter, black soap, and health supplements"
        }
    ]
    
    created_categories = []
    
    for category_data in categories_data:
        result = await db.execute(
            select(Category).where(Category.name == category_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            category = Category(
                name=category_data["name"],
                description=category_data["description"],
                created_at=utc_now()
            )
            db.add(category)
            created_categories.append(category)
            print(f"  ✅ Created category: {category_data['name']}")
        else:
            created_categories.append(existing)
            print(f"  ⏭️  Category already exists: {category_data['name']}")
    
    await db.commit()
    
    for category in created_categories:
        await db.refresh(category)
    
    print(f"  📊 Total categories: {len(created_categories)}")
    return created_categories


# ============================================================================
# SEED PRODUCTS
# ============================================================================

async def seed_products(db: AsyncSession, categories: list[Category]) -> list[Product]:
    """
    Seed sample products with Sierra Leone context.
    
    Args:
        db: Database session
        categories: List of existing categories
    
    Returns:
        List of created Product objects
    """
    print("\n📦 Seeding products...")
    
    # Create category lookup dictionary
    category_map = {cat.name: cat for cat in categories}
    
    products_data = [
        # Local Food & Produce
        {
            "name": "Organic Cassava (5kg)",
            "description": "Fresh organic cassava from local farms in Kenema. Perfect for fufu and other traditional dishes.",
            "price": 25.00,
            "stock_quantity": 100,
            "category_name": "Local Food & Produce"
        },
        {
            "name": "Sierra Leone Brown Rice (2kg)",
            "description": "Locally grown brown rice from the rice fields of Bo. Rich in nutrients and supports local farmers.",
            "price": 15.00,
            "stock_quantity": 200,
            "category_name": "Local Food & Produce"
        },
        {
            "name": "Fresh Vegetables Bundle",
            "description": "Mixed vegetables including cabbage, carrots, peppers, and garden eggs. Delivered fresh from Freetown farms.",
            "price": 20.00,
            "stock_quantity": 50,
            "category_name": "Local Food & Produce"
        },
        
        # Handicrafts & Art
        {
            "name": "Traditional Wood Carving - Lion",
            "description": "Hand-carved wooden lion symbolizing strength. Made by artisans in Makeni using sustainable wood.",
            "price": 45.00,
            "stock_quantity": 15,
            "category_name": "Handicrafts & Art"
        },
        {
            "name": "Tie-Dye Fabric (6 yards)",
            "description": "Beautiful tie-dye fabric made using traditional techniques. Perfect for clothing or home decor.",
            "price": 35.00,
            "stock_quantity": 30,
            "category_name": "Handicrafts & Art"
        },
        {
            "name": "Basket Weave Tray",
            "description": "Handwoven basket tray made from local grasses. Available in multiple colors. Supports women artisans.",
            "price": 18.00,
            "stock_quantity": 40,
            "category_name": "Handicrafts & Art"
        },
        
        # Clothing & Textiles
        {
            "name": "Country Cloth - Traditional",
            "description": "Authentic country cloth woven by local artisans. Perfect for ceremonies and special occasions.",
            "price": 65.00,
            "stock_quantity": 10,
            "category_name": "Clothing & Textiles"
        },
        {
            "name": "African Print Dress",
            "description": "Modern African print dress available in sizes S-XXL. Comfortable and stylish for everyday wear.",
            "price": 50.00,
            "stock_quantity": 25,
            "category_name": "Clothing & Textiles"
        },
        
        # Electronics
        {
            "name": "Smartphone - Basic",
            "description": "Affordable smartphone with 4G connectivity. Perfect for mobile money and online shopping.",
            "price": 120.00,
            "stock_quantity": 5,
            "category_name": "Electronics"
        },
        {
            "name": "Portable Power Bank (10000mAh)",
            "description": "High-capacity power bank to keep your devices charged during power outages.",
            "price": 25.00,
            "stock_quantity": 30,
            "category_name": "Electronics"
        },
        
        # Home & Living
        {
            "name": "Solar-Powered Lamp",
            "description": "Eco-friendly solar lamp with 8 hours of light. Essential for areas with unreliable electricity.",
            "price": 30.00,
            "stock_quantity": 50,
            "category_name": "Home & Living"
        },
        {
            "name": "Water Filter System",
            "description": "Portable water filter system providing clean drinking water. Supports health and hygiene.",
            "price": 40.00,
            "stock_quantity": 20,
            "category_name": "Home & Living"
        },
        
        # Health & Beauty
        {
            "name": "Organic Shea Butter (500g)",
            "description": "100% pure shea butter from northern Sierra Leone. Great for skin and hair care.",
            "price": 12.00,
            "stock_quantity": 80,
            "category_name": "Health & Beauty"
        },
        {
            "name": "African Black Soap",
            "description": "Traditional black soap made from plantain skins and shea butter. Natural and chemical-free.",
            "price": 8.00,
            "stock_quantity": 100,
            "category_name": "Health & Beauty"
        }
    ]
    
    created_products = []
    
    for product_data in products_data:
        category = category_map.get(product_data["category_name"])
        
        if not category:
            print(f"  ⚠️  Category not found for product: {product_data['name']}")
            continue
        
        result = await db.execute(
            select(Product).where(
                Product.name == product_data["name"],
                Product.category_id == category.id
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                stock_quantity=product_data["stock_quantity"],
                category_id=category.id,
                created_at=utc_now(),
                updated_at=utc_now()
            )
            db.add(product)
            created_products.append(product)
            print(f"  ✅ Created product: {product_data['name']} (${product_data['price']})")
        else:
            created_products.append(existing)
            print(f"  ⏭️  Product already exists: {product_data['name']}")
    
    await db.commit()
    
    for product in created_products:
        await db.refresh(product)
    
    print(f"  📊 Total products: {len(created_products)}")
    return created_products


# ============================================================================
# SEED ORDERS
# ============================================================================

async def seed_orders(db: AsyncSession, users: list[User], products: list[Product]) -> list[Order]:
    """
    Seed sample orders for demonstration.
    
    Args:
        db: Database session
        users: List of existing users
        products: List of existing products
    
    Returns:
        List of created Order objects
    """
    print("\n📋 Seeding orders...")
    
    created_orders = []
    
    # Find regular customers (not admin)
    customers = [user for user in users if user.role == "customer"]
    
    if not customers or not products:
        print("  ⚠️  No customers or products found. Skipping order seeding.")
        return []
    
    orders_data = [
        {
            "user": customers[0] if len(customers) > 0 else None,
            "items": [
                {"product": products[0], "quantity": 2},  # Organic Cassava
                {"product": products[4], "quantity": 1},  # Traditional Wood Carving
            ],
            "status": "Delivered"
        },
        {
            "user": customers[1] if len(customers) > 1 else None,
            "items": [
                {"product": products[1], "quantity": 1},  # Sierra Leone Brown Rice
                {"product": products[12], "quantity": 3},  # Shea Butter
            ],
            "status": "Processing"
        },
        {
            "user": customers[2] if len(customers) > 2 else None,
            "items": [
                {"product": products[7], "quantity": 1},  # African Print Dress
                {"product": products[10], "quantity": 2},  # Solar Lamp
            ],
            "status": "Pending"
        }
    ]
    
    for order_data in orders_data:
        user = order_data["user"]
        
        if not user:
            continue
        
        # Calculate total amount
        total_amount = sum(
            item["product"].price * item["quantity"]
            for item in order_data["items"]
        )
        
        order = Order(
            user_id=user.id,
            total_amount=total_amount,
            status=order_data["status"],
            created_at=utc_now()
        )
        
        db.add(order)
        await db.flush()  # Get order ID
        
        # Create order items
        for item_data in order_data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price=item_data["product"].price
            )
            db.add(order_item)
            
            # Reduce product stock
            item_data["product"].stock_quantity -= item_data["quantity"]
        
        created_orders.append(order)
        print(f"  ✅ Created order #{order.id} for {user.username} - ${total_amount}")
    
    await db.commit()
    
    for order in created_orders:
        await db.refresh(order)
    
    print(f"  📊 Total orders: {len(created_orders)}")
    return created_orders


# ============================================================================
# MAIN SEED FUNCTION
# ============================================================================

async def seed_database() -> dict:
    """
    Main function to seed complete database with all initial data.
    
    Returns:
        Dictionary containing created objects count
    """
    print("\n" + "=" * 60)
    print("🌱 SEEDING DATABASE")
    print("=" * 60)
    
    # Initialize database tables
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Seed in correct order (respecting foreign keys)
        users = await seed_users(db)
        categories = await seed_categories(db)
        products = await seed_products(db, categories)
        orders = await seed_orders(db, users, products)
    
    print("\n" + "=" * 60)
    print("✅ DATABASE SEEDING COMPLETE")
    print("=" * 60)
    print(f"   Users:     {len(users)}")
    print(f"   Categories: {len(categories)}")
    print(f"   Products:  {len(products)}")
    print(f"   Orders:    {len(orders)}")
    print("=" * 60 + "\n")
    
    return {
        "users": len(users),
        "categories": len(categories),
        "products": len(products),
        "orders": len(orders)
    }


# ============================================================================
# COMMAND-LINE EXECUTION
# ============================================================================

def run_seed():
    """Run seed function from command line"""
    asyncio.run(seed_database())


if __name__ == "__main__":
    run_seed()