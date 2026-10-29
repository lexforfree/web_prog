"""
Advanced Transaction Examples with Docker
Занятие 9: Транзакции и индексы

Примеры демонстрируют:
- Deadlock detection (взаимная блокировка)
- Savepoints (частичный откат)
- Isolation levels (READ COMMITTED, REPEATABLE READ, SERIALIZABLE)
- Transaction monitoring (pg_stat_activity)
- Lock monitoring (pg_locks)

Запуск с Docker:
1. docker-compose up -d
2. python code/advanced_transactions.py
"""

import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv
import threading
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


def setup_accounts():
    """Create accounts table for deadlock demo"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS accounts CASCADE;
            CREATE TABLE accounts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                balance DECIMAL(10, 2) NOT NULL CHECK (balance >= 0)
            );
            
            INSERT INTO accounts (name, balance) VALUES 
            ('Alice', 1000.00),
            ('Bob', 1000.00);
        """)
    print("Accounts table created for deadlock demo")


# === Deadlock Detection ===
def transfer_a_to_b():
    """
    Поток 1: Alice -> Bob
    Блокирует Alice, затем пытается заблокировать Bob
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            print("Thread 1: Locking Alice")
            cursor.execute("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
            time.sleep(0.5)
            
            print("Thread 1: Trying to lock Bob (may cause deadlock)")
            cursor.execute("SELECT balance FROM accounts WHERE id = 2 FOR UPDATE")
            
            cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
            
            conn.commit()
            print("Thread 1: Transfer completed")
        except psycopg2.extensions.Deadlock:
            print("Thread 1: Deadlock detected! Rolling back...")
            conn.rollback()
        finally:
            cursor.close()


def transfer_b_to_a():
    """
    Поток 2: Bob -> Alice
    Блокирует Bob, затем пытается заблокировать Alice
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            print("Thread 2: Locking Bob")
            cursor.execute("SELECT balance FROM accounts WHERE id = 2 FOR UPDATE")
            time.sleep(0.5)
            
            print("Thread 2: Trying to lock Alice (may cause deadlock)")
            cursor.execute("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
            
            cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 2")
            cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 1")
            
            conn.commit()
            print("Thread 2: Transfer completed")
        except psycopg2.extensions.Deadlock:
            print("Thread 2: Deadlock detected! Rolling back...")
            conn.rollback()
        finally:
            cursor.close()


def demonstrate_deadlock():
    """
    Демонстрация deadlock:
    Thread 1 блокирует Alice, пытается заблокировать Bob
    Thread 2 блокирует Bob, пытается заблокировать Alice
    PostgreSQL автоматически обнаруживает и прерывает одну транзакцию
    """
    print("\n=== Deadlock Detection Example ===")
    setup_accounts()
    
    thread1 = threading.Thread(target=transfer_a_to_b)
    thread2 = threading.Thread(target=transfer_b_to_a)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    with db.get_cursor() as cursor:
        cursor.execute("SELECT id, name, balance FROM accounts")
        accounts = cursor.fetchall()
        for acc in accounts:
            print(f"Account {acc[0]} ({acc[1]}): {acc[2]}")


# === Savepoints ===
def demonstrate_savepoints():
    """
    Демонстрация savepoints:
    Частичный откат внутри транзакции
    """
    print("\n=== Savepoints Example ===")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS transactions CASCADE;
            CREATE TABLE transactions (
                id SERIAL PRIMARY KEY,
                description TEXT,
                amount DECIMAL(10, 2)
            );
        """)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            # Начало транзакции
            cursor.execute("INSERT INTO transactions (description, amount) VALUES ('First', 100.00)")
            print("Inserted First transaction")
            
            # Создание savepoint
            cursor.execute("SAVEPOINT sp1")
            print("Created savepoint sp1")
            
            cursor.execute("INSERT INTO transactions (description, amount) VALUES ('Second', 200.00)")
            print("Inserted Second transaction")
            
            # Откат к savepoint
            cursor.execute("ROLLBACK TO SAVEPOINT sp1")
            print("Rolled back to sp1 (Second transaction removed)")
            
            # Продолжение транзакции
            cursor.execute("INSERT INTO transactions (description, amount) VALUES ('Third', 300.00)")
            print("Inserted Third transaction")
            
            conn.commit()
            print("Transaction committed")
        finally:
            cursor.close()
    
    # Проверка
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        print("Remaining transactions:")
        for t in transactions:
            print(f"  {t}")


# === Isolation Levels ===
def demonstrate_isolation_levels():
    """
    Демонстрация уровней изоляции:
    READ COMMITTED, REPEATABLE READ, SERIALIZABLE
    """
    print("\n=== Transaction Isolation Levels ===")
    
    # READ COMMITTED (по умолчанию)
    with db.get_cursor() as cursor:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
        cursor.execute("SELECT current_setting('transaction_isolation')")
        level = cursor.fetchone()[0]
        print(f"Isolation level: {level}")
    
    # REPEATABLE READ
    with db.get_cursor() as cursor:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        cursor.execute("SELECT current_setting('transaction_isolation')")
        level = cursor.fetchone()[0]
        print(f"Isolation level: {level}")
    
    # SERIALIZABLE
    with db.get_cursor() as cursor:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        cursor.execute("SELECT current_setting('transaction_isolation')")
        level = cursor.fetchone()[0]
        print(f"Isolation level: {level}")


# === Transaction Monitoring ===
def demonstrate_transaction_monitoring():
    """
    Демонстрация мониторинга транзакций:
    pg_stat_activity - активные транзакции
    pg_locks - блокировки
    """
    print("\n=== Transaction Monitoring ===")
    
    with db.get_cursor() as cursor:
        # Активные транзакции
        cursor.execute("""
            SELECT pid, state, query, now() - query_start as duration
            FROM pg_stat_activity
            WHERE state = 'active'
            ORDER BY duration DESC
            LIMIT 5
        """)
        active = cursor.fetchall()
        print("Active transactions:")
        for row in active:
            print(f"  PID: {row[0]}, State: {row[1]}, Duration: {row[3]}")
        
        # Блокировки
        cursor.execute("""
            SELECT locktype, relation::regclass, mode
            FROM pg_locks
            WHERE pid != pg_backend_pid()
            LIMIT 5
        """)
        locks = cursor.fetchall()
        print("\nLocks:")
        for row in locks:
            print(f"  Type: {row[0]}, Relation: {row[1]}, Mode: {row[2]}")


# === Long-running Transactions ===
def demonstrate_long_transaction():
    """
    Демонстрация долгих транзакций:
    Влияние на производительность
    """
    print("\n=== Long-running Transaction Example ===")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS large_table CASCADE;
            CREATE TABLE large_table (
                id SERIAL PRIMARY KEY,
                data TEXT
            );
        """)
    
    # Вставка данных
    with db.get_cursor() as cursor:
        start = time.time()
        for i in range(1000):
            cursor.execute("INSERT INTO large_table (data) VALUES (%s)", (f"item_{i}",))
        duration = time.time() - start
        print(f"Inserted 1000 rows in {duration:.3f}s")
    
    # Долгая транзакция
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            start = time.time()
            cursor.execute("BEGIN")
            cursor.execute("SELECT * FROM large_table")
            time.sleep(2)  # Симуляция долгой обработки
            cursor.execute("COMMIT")
            duration = time.time() - start
            print(f"Long transaction completed in {duration:.3f}s")
        finally:
            cursor.close()


if __name__ == "__main__":
    print("=== Advanced Transaction Examples ===\n")
    
    try:
        # 1. Deadlock Detection
        demonstrate_deadlock()
        
        # 2. Savepoints
        demonstrate_savepoints()
        
        # 3. Isolation Levels
        demonstrate_isolation_levels()
        
        # 4. Transaction Monitoring
        demonstrate_transaction_monitoring()
        
        # 5. Long-running Transactions
        demonstrate_long_transaction()
        
        print("\n=== All examples completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
