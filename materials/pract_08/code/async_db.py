"""
Async Database Access Example with Docker
Занятие 8: Работа с базой данных

Для запуска требуется: pip install asyncpg python-dotenv

Запуск с Docker:
1. docker-compose up -d
2. python code/async_db.py
"""

import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()


class AsyncDatabase:
    """Async database connection manager"""
    
    def __init__(self):
        self.pool = None
    
    async def init_pool(self):
        """Initialize connection pool - подключение к Docker контейнеру"""
        self.pool = await asyncpg.create_pool(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'webprog'),
            user=os.getenv('DB_USER', 'webprog'),
            password=os.getenv('DB_PASSWORD', 'webprog123'),
            min_size=1,
            max_size=10
        )
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def execute(self, query: str, *args):
        """Execute query (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)


# Initialize database
db = AsyncDatabase()


async def create_tables():
    """Create users and orders tables"""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER CHECK (age >= 18),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            product VARCHAR(100) NOT NULL,
            total DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    print("Tables created")


async def create_user(name: str, email: str, age: int) -> dict:
    """Create a new user"""
    try:
        result = await db.fetchrow(
            "INSERT INTO users (name, email, age) VALUES ($1, $2, $3) RETURNING id, name, email, age, created_at",
            name, email, age
        )
        print(f"User created: {result}")
        return dict(result)
    except asyncpg.UniqueViolationError:
        raise ValueError("Email already exists")


async def get_user(user_id: int) -> dict:
    """Get user by ID"""
    result = await db.fetchrow(
        "SELECT id, name, email, age, created_at FROM users WHERE id = $1",
        user_id
    )
    
    if not result:
        raise ValueError("User not found")
    
    return dict(result)


async def get_all_users() -> list:
    """Get all users"""
    results = await db.fetch("SELECT id, name, email, age FROM users ORDER BY id")
    return [dict(row) for row in results]


async def update_user(user_id: int, **kwargs) -> dict:
    """Update user"""
    if not kwargs:
        raise ValueError("No fields to update")
    
    valid_fields = ['name', 'email', 'age']
    updates = []
    values = []
    param_num = 1
    
    for field, value in kwargs.items():
        if field in valid_fields:
            updates.append(f"{field} = ${param_num}")
            values.append(value)
            param_num += 1
    
    if not updates:
        raise ValueError("No valid fields to update")
    
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ${param_num} RETURNING id, name, email, age"
    
    result = await db.fetchrow(query, *values)
    
    if not result:
        raise ValueError("User not found")
    
    return dict(result)


async def delete_user(user_id: int) -> bool:
    """Delete user"""
    result = await db.execute("DELETE FROM users WHERE id = $1", user_id)
    
    if result == "DELETE 0":
        raise ValueError("User not found")
    
    print(f"User {user_id} deleted")
    return True


async def create_order(user_id: int, product: str, total: float) -> dict:
    """Create order for user"""
    result = await db.fetchrow(
        "INSERT INTO orders (user_id, product, total) VALUES ($1, $2, $3) RETURNING id, user_id, product, total, created_at",
        user_id, product, total
    )
    
    return dict(result)


async def get_user_orders(user_id: int) -> list:
    """Get all orders for a user"""
    results = await db.fetch(
        "SELECT id, product, total, created_at FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
        user_id
    )
    
    return [dict(row) for row in results]


async def get_users_with_order_count() -> list:
    """Get users with order count using JOIN"""
    results = await db.fetch("""
        SELECT u.id, u.name, u.email, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.name, u.email
        ORDER BY order_count DESC
    """)
    
    return [dict(row) for row in results]


async def search_user_by_email(email: str) -> dict:
    """Search user by email"""
    result = await db.fetchrow(
        "SELECT id, name, email, age FROM users WHERE email = $1",
        email
    )
    
    if not result:
        raise ValueError("User not found")
    
    return dict(result)


async def batch_create_users(users: list) -> list:
    """Create multiple users in one transaction"""
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            results = []
            for user in users:
                result = await conn.fetchrow(
                    "INSERT INTO users (name, email, age) VALUES ($1, $2, $3) RETURNING id, name, email",
                    user['name'], user['email'], user['age']
                )
                results.append(dict(result))
            return results


# Example usage
import asyncio


async def main():
    print("=== Async Database Access Example ===\n")
    
    try:
        # Initialize pool
        await db.init_pool()
        
        # Create tables
        await create_tables()
        
        # Create users
        user1 = await create_user("John Doe", "john@example.com", 30)
        user2 = await create_user("Jane Smith", "jane@example.com", 25)
        
        # Get user
        user = await get_user(user1['id'])
        print(f"Got user: {user}")
        
        # Get all users
        users = await get_all_users()
        print(f"All users: {users}")
        
        # Update user
        updated = await update_user(user1['id'], age=31)
        print(f"Updated user: {updated}")
        
        # Create orders
        order1 = await create_order(user1['id'], "Laptop", 999.99)
        order2 = await create_order(user1['id'], "Mouse", 29.99)
        order3 = await create_order(user2['id'], "Keyboard", 79.99)
        
        # Get user orders
        orders = await get_user_orders(user1['id'])
        print(f"User orders: {orders}")
        
        # Get users with order count
        users_with_orders = await get_users_with_order_count()
        print(f"Users with order count: {users_with_orders}")
        
        # Batch create users
        new_users = await batch_create_users([
            {'name': 'Alice', 'email': 'alice@example.com', 'age': 28},
            {'name': 'Bob', 'email': 'bob@example.com', 'age': 32}
        ])
        print(f"Batch created users: {new_users}")
        
        # Delete user
        await delete_user(user2['id'])
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
