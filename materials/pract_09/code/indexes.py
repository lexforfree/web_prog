"""
Index Examples
Занятие 9: Транзакции и индексы

Для запуска требуется: pip install psycopg2-binary python-dotenv
"""

import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv
import time

load_dotenv()


class Database:
    """Database connection manager"""
    
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
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
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
        self.connection_pool.closeall()


db = Database()


def create_users_table():
    """Create users table"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                email VARCHAR(100),
                age INTEGER,
                city VARCHAR(50),
                active BOOLEAN DEFAULT true
            );
        """)
    print("Users table created")


def create_indexes():
    """Create various types of indexes"""
    with db.get_cursor() as cursor:
        # Simple index on email
        cursor.execute("DROP INDEX IF EXISTS idx_users_email")
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")
        print("Created index on email")
        
        # Composite index on name and age
        cursor.execute("DROP INDEX IF EXISTS idx_users_name_age")
        cursor.execute("CREATE INDEX idx_users_name_age ON users(name, age)")
        print("Created composite index on name, age")
        
        # Partial index on active users
        cursor.execute("DROP INDEX IF EXISTS idx_users_active_city")
        cursor.execute("CREATE INDEX idx_users_active_city ON users(city) WHERE active = true")
        print("Created partial index on city for active users")
        
        # Unique index on email
        cursor.execute("DROP INDEX IF EXISTS idx_users_email_unique")
        cursor.execute("CREATE UNIQUE INDEX idx_users_email_unique ON users(email)")
        print("Created unique index on email")


def drop_indexes():
    """Drop all indexes"""
    with db.get_cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS idx_users_email")
        cursor.execute("DROP INDEX IF EXISTS idx_users_name_age")
        cursor.execute("DROP INDEX IF EXISTS idx_users_active_city")
        cursor.execute("DROP INDEX IF EXISTS idx_users_email_unique")
    print("Dropped all indexes")


def generate_test_data(count=10000):
    """Generate test data"""
    print(f"Generating {count} test users...")
    cities = ['Moscow', 'St. Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan']
    
    with db.get_cursor() as cursor:
        for i in range(count):
            name = f"User{i}"
            email = f"user{i}@example.com"
            age = 18 + (i % 60)
            city = cities[i % len(cities)]
            active = i % 2 == 0
            
            cursor.execute(
                "INSERT INTO users (name, email, age, city, active) VALUES (%s, %s, %s, %s, %s)",
                (name, email, age, city, active)
            )
    
    print(f"Generated {count} users")


def explain_query(query: str, params=None):
    """Run EXPLAIN on a query"""
    with db.get_cursor() as cursor:
        cursor.execute(f"EXPLAIN {query}", params or ())
        results = cursor.fetchall()
        
        print(f"\nQuery: {query}")
        print("EXPLAIN:")
        for row in results:
            print(f"  {row[0]}")


def measure_query_time(query: str, params=None, iterations=10):
    """Measure query execution time"""
    with db.get_cursor() as cursor:
        times = []
        
        for _ in range(iterations):
            start = time.time()
            cursor.execute(query, params or ())
            cursor.fetchall()
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        print(f"Average time ({iterations} iterations): {avg_time:.4f}s")
        return avg_time


def test_email_search():
    """Test email search with and without index"""
    print("\n=== Testing Email Search ===")
    
    query = "SELECT * FROM users WHERE email = 'user5000@example.com'"
    
    # Without index
    print("\nWithout index:")
    drop_indexes()
    explain_query(query)
    time_without = measure_query_time(query)
    
    # With index
    print("\nWith index:")
    create_indexes()
    explain_query(query)
    time_with = measure_query_time(query)
    
    improvement = (time_without - time_with) / time_without * 100
    print(f"\nImprovement: {improvement:.1f}%")


def test_composite_index():
    """Test composite index (leftmost prefix rule)"""
    print("\n=== Testing Composite Index (name, age) ===")
    
    queries = [
        ("SELECT * FROM users WHERE name = 'User100'", None),
        ("SELECT * FROM users WHERE name = 'User100' AND age = 30", None),
        ("SELECT * FROM users WHERE age = 30", None),
        ("SELECT * FROM users WHERE age = 30 AND name = 'User100'", None),
    ]
    
    for query, params in queries:
        explain_query(query, params)


def test_partial_index():
    """Test partial index on active users"""
    print("\n=== Testing Partial Index (city WHERE active = true) ===")
    
    queries = [
        ("SELECT * FROM users WHERE active = true AND city = 'Moscow'", None),
        ("SELECT * FROM users WHERE active = false AND city = 'Moscow'", None),
        ("SELECT * FROM users WHERE city = 'Moscow'", None),
    ]
    
    for query, params in queries:
        explain_query(query, params)


def test_n_plus_1():
    """Demonstrate N+1 problem"""
    print("\n=== N+1 Problem Demonstration ===")
    
    # Create orders table
    with db.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                product VARCHAR(100),
                total DECIMAL(10, 2)
            );
        """)
        
        # Create orders for first 100 users
        for i in range(100):
            cursor.execute(
                "INSERT INTO orders (user_id, product, total) VALUES (%s, %s, %s)",
                (i + 1, f"Product{i}", 100.00)
            )
    
    # N+1 approach
    print("\nN+1 approach:")
    start = time.time()
    
    with db.get_cursor() as cursor:
        # Get users
        cursor.execute("SELECT id, name FROM users WHERE id <= 100")
        users = cursor.fetchall()
        
        # For each user, get orders (N queries)
        for user_id, name in users:
            cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
            orders = cursor.fetchall()
    
    n_plus_1_time = time.time() - start
    print(f"Time: {n_plus_1_time:.4f}s")
    
    # JOIN approach
    print("\nJOIN approach:")
    start = time.time()
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT u.id, u.name, o.id, o.product, o.total
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.id <= 100
            ORDER BY u.id
        """)
        results = cursor.fetchall()
    
    join_time = time.time() - start
    print(f"Time: {join_time:.4f}s")
    
    improvement = (n_plus_1_time - join_time) / n_plus_1_time * 100
    print(f"\nImprovement: {improvement:.1f}%")


def test_in_approach():
    """Test IN approach for N+1"""
    print("\n=== IN Approach ===")
    
    start = time.time()
    
    with db.get_cursor() as cursor:
        # Get users
        cursor.execute("SELECT id FROM users WHERE id <= 100")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # Get all orders in one query
        cursor.execute(
            "SELECT * FROM orders WHERE user_id = ANY(%s)",
            (user_ids,)
        )
        orders = cursor.fetchall()
    
    in_time = time.time() - start
    print(f"Time: {in_time:.4f}s")


# Example usage
if __name__ == "__main__":
    print("=== Index Examples ===\n")
    
    try:
        # Create table
        create_users_table()
        
        # Generate test data
        generate_test_data(10000)
        
        # Test email search
        test_email_search()
        
        # Test composite index
        test_composite_index()
        
        # Test partial index
        test_partial_index()
        
        # Test N+1
        test_n_plus_1()
        
        # Test IN approach
        test_in_approach()
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close_all()
