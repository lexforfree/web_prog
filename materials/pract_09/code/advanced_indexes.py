"""
Advanced Index Examples with Docker
Занятие 9: Транзакции и индексы

Примеры демонстрируют:
- Partial indexes (индексы с условием WHERE)
- Functional indexes (индексы на выражениях)
- Covering indexes (INCLUDE для index-only scan)
- Index usage statistics (pg_stat_user_indexes)
- Index bloat detection
- REINDEX (перестроение индексов)
- VACUUM and ANALYZE

Запуск с Docker:
1. docker-compose up -d
2. python code/advanced_indexes.py
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
            user=os.getenv('DB_USER', 'webprog'),
            password=os.getenv('DB_PASSWORD', 'webprog123')
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


db = Database()


def setup_users_table():
    """Create users table for index examples"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS users CASCADE;
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW(),
                age INTEGER
            );
        """)
    
    # Insert test data
    with db.get_cursor() as cursor:
        for i in range(1000):
            status = 'active' if i % 3 == 0 else ('inactive' if i % 3 == 1 else 'deleted')
            cursor.execute(
                "INSERT INTO users (name, email, status, age) VALUES (%s, %s, %s, %s)",
                (f"User_{i}", f"user_{i}@example.com", status, 20 + (i % 50))
            )
    
    print("Users table created with 1000 rows")


# === Partial Index ===
def demonstrate_partial_index():
    """
    Демонстрация partial index:
    Индекс только для активных пользователей
    """
    print("\n=== Partial Index Example ===")
    setup_users_table()
    
    with db.get_cursor() as cursor:
        # Создание partial index
        cursor.execute("""
            CREATE INDEX idx_users_active 
            ON users (email) 
            WHERE status = 'active'
        """)
        print("Created partial index on active users")
    
    # Проверка использования
    with db.get_cursor() as cursor:
        # Запрос с использованием partial index
        start = time.time()
        cursor.execute("""
            EXPLAIN ANALYZE 
            SELECT * FROM users 
            WHERE status = 'active' AND email = 'user_3@example.com'
        """)
        plan = cursor.fetchall()
        duration = time.time() - start
        print(f"\nQuery with partial index (duration: {duration:.3f}s):")
        for line in plan:
            print(f"  {line[0]}")
        
        # Запрос без использования partial index
        start = time.time()
        cursor.execute("""
            EXPLAIN ANALYZE 
            SELECT * FROM users 
            WHERE status = 'inactive' AND email = 'user_1@example.com'
        """)
        plan = cursor.fetchall()
        duration = time.time() - start
        print(f"\nQuery without partial index (duration: {duration:.3f}s):")
        for line in plan:
            print(f"  {line[0]}")


# === Functional Index ===
def demonstrate_functional_index():
    """
    Демонстрация functional index:
    Индекс на выражении LOWER(email)
    """
    print("\n=== Functional Index Example ===")
    
    with db.get_cursor() as cursor:
        # Создание functional index
        cursor.execute("""
            CREATE INDEX idx_users_email_lower 
            ON users (LOWER(email))
        """)
        print("Created functional index on LOWER(email)")
    
    # Проверка использования
    with db.get_cursor() as cursor:
        # Запрос с использованием functional index
        start = time.time()
        cursor.execute("""
            EXPLAIN ANALYZE 
            SELECT * FROM users 
            WHERE LOWER(email) = 'user_10@example.com'
        """)
        plan = cursor.fetchall()
        duration = time.time() - start
        print(f"\nQuery with functional index (duration: {duration:.3f}s):")
        for line in plan:
            print(f"  {line[0]}")


# === Covering Index (INCLUDE) ===
def demonstrate_covering_index():
    """
    Демонстрация covering index:
    INCLUDE для index-only scan
    """
    print("\n=== Covering Index Example ===")
    
    with db.get_cursor() as cursor:
        # Создание covering index
        cursor.execute("""
            CREATE INDEX idx_users_covering 
            ON users (status) 
            INCLUDE (name, email)
        """)
        print("Created covering index with INCLUDE")
    
    # Проверка использования
    with db.get_cursor() as cursor:
        # Index-only scan
        start = time.time()
        cursor.execute("""
            EXPLAIN ANALYZE 
            SELECT status, name, email 
            FROM users 
            WHERE status = 'active'
            LIMIT 10
        """)
        plan = cursor.fetchall()
        duration = time.time() - start
        print(f"\nIndex-only scan query (duration: {duration:.3f}s):")
        for line in plan:
            print(f"  {line[0]}")


# === Index Usage Statistics ===
def demonstrate_index_statistics():
    """
    Демонстрация статистики использования индексов:
    pg_stat_user_indexes
    """
    print("\n=== Index Usage Statistics ===")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
        """)
        stats = cursor.fetchall()
        print("Index usage statistics:")
        for row in stats:
            print(f"  {row[2]}: scans={row[3]}, read={row[4]}, fetched={row[5]}")


# === Index Bloat Detection ===
def demonstrate_index_bloat():
    """
    Демонстрация обнаружения раздувания индексов:
    Сравнение реального и ожидаемого размера
    """
    print("\n=== Index Bloat Detection ===")
    
    with db.get_cursor() as cursor:
        # Размер индексов
        cursor.execute("""
            SELECT 
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        sizes = cursor.fetchall()
        print("Index sizes:")
        for row in sizes:
            print(f"  {row[0]}: {row[1]}")


# === REINDEX ===
def demonstrate_reindex():
    """
    Демонстрация перестроения индексов:
    REINDEX CONCURRENTLY (без блокировки)
    """
    print("\n=== REINDEX Example ===")
    
    with db.get_cursor() as cursor:
        # Обычный REINDEX (блокирует таблицу)
        cursor.execute("REINDEX INDEX idx_users_active")
        print("Reindexed idx_users_active (blocking)")
        
        # REINDEX CONCURRENTLY (без блокировки, PostgreSQL 12+)
        try:
            cursor.execute("REINDEX INDEX CONCURRENTLY idx_users_email_lower")
            print("Reindexed idx_users_email_lower (non-blocking)")
        except psycopg2.ProgrammingError as e:
            print(f"REINDEX CONCURRENTLY not available: {e}")


# === VACUUM and ANALYZE ===
def demonstrate_vacuum_analyze():
    """
    Демонстрация VACUUM и ANALYZE:
    Очистка мёртвых строк и обновление статистики
    """
    print("\n=== VACUUM and ANALYZE Example ===")
    
    with db.get_cursor() as cursor:
        # Удаление некоторых строк
        cursor.execute("DELETE FROM users WHERE status = 'deleted'")
        print(f"Deleted rows with status='deleted'")
        
        # ANALYZE - обновление статистики для оптимизатора
        cursor.execute("ANALYZE users")
        print("Analyzed users table (updated statistics)")
        
        # VACUUM - очистка мёртвых строк
        cursor.execute("VACUUM users")
        print("Vacuumed users table (cleaned dead rows)")


# === Concurrent Index Creation ===
def demonstrate_concurrent_index():
    """
    Демонстрация создания индекса без блокировки:
    CREATE INDEX CONCURRENTLY
    """
    print("\n=== Concurrent Index Creation ===")
    
    with db.get_cursor() as cursor:
        # Создание индекса без блокировки
        try:
            cursor.execute("""
                CREATE INDEX CONCURRENTLY idx_users_age
                ON users (age)
            """)
            print("Created index idx_users_age concurrently (non-blocking)")
        except psycopg2.ProgrammingError as e:
            print(f"CREATE INDEX CONCURRENTLY error: {e}")


if __name__ == "__main__":
    print("=== Advanced Index Examples ===\n")
    
    try:
        # 1. Partial Index
        demonstrate_partial_index()
        
        # 2. Functional Index
        demonstrate_functional_index()
        
        # 3. Covering Index
        demonstrate_covering_index()
        
        # 4. Index Statistics
        demonstrate_index_statistics()
        
        # 5. Index Bloat
        demonstrate_index_bloat()
        
        # 6. REINDEX
        demonstrate_reindex()
        
        # 7. VACUUM and ANALYZE
        demonstrate_vacuum_analyze()
        
        # 8. Concurrent Index Creation
        demonstrate_concurrent_index()
        
        print("\n=== All examples completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
