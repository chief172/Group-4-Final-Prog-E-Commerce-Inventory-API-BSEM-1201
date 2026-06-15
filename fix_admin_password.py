# fix_admin_password.py
import bcrypt
import asyncio
import asyncpg

async def fix_admin():
    # Generate new hash for Admin@123
    password = "Admin@123"
    new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"New password hash: {new_hash}")
    
    # Connect and update
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='mylovelymom',
        database='ecommerce_inventory_db'
    )
    
    # Delete existing admin
    await conn.execute("DELETE FROM users WHERE email = 'admin@ecommerce.sl'")
    
    # Insert new admin
    await conn.execute("""
        INSERT INTO users (username, email, password, role, is_active, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
    """, 'admin', 'admin@ecommerce.sl', new_hash, 'admin', True)
    
    # Verify
    row = await conn.fetchrow("SELECT id, username, email, role FROM users WHERE email = 'admin@ecommerce.sl'")
    print(f"\n✅ Admin created:")
    print(f"   ID: {row['id']}")
    print(f"   Username: {row['username']}")
    print(f"   Email: {row['email']}")
    print(f"   Role: {row['role']}")
    
    await conn.close()

asyncio.run(fix_admin())
print("\n🔐 Login with: admin@ecommerce.sl / Admin@123")