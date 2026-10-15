"""
Database Operations Example
Занятие 8: Работа с базой данных

Для запуска требуется: pip install psycopg2-binary python-dotenv
"""

import os
import psycopg2
from psycopg2 import pool, sql
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Database:
    """Database connection manager with pooling"""
    
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'webprog'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
    
    @contextmanager
    def get_connection(self):
        """Context manager for connection"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        """Context manager for cursor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def close_all(self):
        """Close all connections in pool"""
        self.connection_pool.closeall()


# Initialize database
db = Database()


def create_tables():
    """Create users and orders tables"""
    with db.get_cursor() as cursor:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                age INTEGER CHECK (age >= 18),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                product VARCHAR(100) NOT NULL,
                total DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
    
    print("Tables created successfully")


def create_user(name: str, email: str, age: int) -> dict:
    """Create a new user"""
    with db.get_cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (%s, %s, %s) RETURNING id, name, email, age, created_at",
                (name, email, age)
            )
            result = cursor.fetchone()
            print(f"User created: {result}")
            return {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'age': result[3],
                'created_at': result[4]
            }
        except psycopg2.IntegrityError as e:
            print(f"Error creating user: {e}")
            raise ValueError("Email already exists")


def get_user(user_id: int) -> dict:
    """Get user by ID"""
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, age, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("User not found")
        
        return {
            'id': result[0],
            'name': result[1],
            'email': result[2],
            'age': result[3],
            'created_at': result[4]
        }


def get_all_users() -> list:
    """Get all users"""
    with db.get_cursor() as cursor:
        cursor.execute("SELECT id, name, email, age FROM users ORDER BY id")
        results = cursor.fetchall()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            for row in results
        ]


def update_user(user_id: int, **kwargs) -> dict:
    """Update user"""
    if not kwargs:
        raise ValueError("No fields to update")
    
    # Build dynamic update query
    valid_fields = ['name', 'email', 'age']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in valid_fields:
            updates.append(f"{field} = %s")
            values.append(value)
    
    if not updates:
        raise ValueError("No valid fields to update")
    
    values.append(user_id)
    
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, name, email, age"
    
    with db.get_cursor() as cursor:
        cursor.execute(query, values)
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("User not found")
        
        return {
            'id': result[0],
            'name': result[1],
            'email': result[2],
            'age': result[3]
        }


def delete_user(user_id: int) -> bool:
    """Delete user"""
    with db.get_cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        if cursor.rowcount == 0:
            raise ValueError("User not found")
        
        print(f"User {user_id} deleted")
        return True


def create_order(user_id: int, product: str, total: float) -> dict:
    """Create order for user"""
    with db.get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO orders (user_id, product, total) VALUES (%s, %s, %s) RETURNING id, user_id, product, total, created_at",
            (user_id, product, total)
        )
        result = cursor.fetchone()
        
        return {
            'id': result[0],
            'user_id': result[1],
            'product': result[2],
            'total': float(result[3]),
            'created_at': result[4]
        }


def get_user_orders(user_id: int) -> list:
    """Get all orders for a user"""
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT id, product, total, created_at FROM orders WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        results = cursor.fetchall()
        
        return [
            {
                'id': row[0],
                'product': row[1],
                'total': float(row[2]),
                'created_at': row[3]
            }
            for row in results
        ]


def get_users_with_order_count() -> list:
    """Get users with order count using JOIN"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT u.id, u.name, u.email, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name, u.email
            ORDER BY order_count DESC
        """)
        results = cursor.fetchall()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'order_count': row[3]
            }
            for row in results
        ]


def search_user_by_email(email: str) -> dict:
    """Search user by email (demonstrates parameterized query)"""
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, age FROM users WHERE email = %s",
            (email,)
        )
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("User not found")
        
        return {
            'id': result[0],
            'name': result[1],
            'email': result[2],
            'age': result[3]
        }


# Example usage
if __name__ == "__main__":
    print("=== Database Operations Example ===\n")
    
    try:
        # Create tables
        create_tables()
        
        # Create users
        user1 = create_user("John Doe", "john@example.com", 30)
        user2 = create_user("Jane Smith", "jane@example.com", 25)
        
        # Get user
        user = get_user(user1['id'])
        print(f"Got user: {user}")
        
        # Get all users
        users = get_all_users()
        print(f"All users: {users}")
        
        # Update user
        updated = update_user(user1['id'], age=31)
        print(f"Updated user: {updated}")
        
        # Create orders
        order1 = create_order(user1['id'], "Laptop", 999.99)
        order2 = create_order(user1['id'], "Mouse", 29.99)
        order3 = create_order(user2['id'], "Keyboard", 79.99)
        
        # Get user orders
        orders = get_user_orders(user1['id'])
        print(f"User orders: {orders}")
        
        # Get users with order count
        users_with_orders = get_users_with_order_count()
        print(f"Users with order count: {users_with_orders}")
        
        # Search by email
        found = search_user_by_email("john@example.com")
        print(f"Found user: {found}")
        
        # Delete user
        delete_user(user(user2['id']))
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close_all()
