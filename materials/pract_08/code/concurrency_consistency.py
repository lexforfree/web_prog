"""
Concurrency and Consistency Examples
Занятие 8: Работа с базой данных

Примеры демонстрируют:
- Race condition (гонка данных)
- Уровни изоляции транзакций
- SELECT FOR UPDATE (pessimistic locking)
- Optimistic locking с version
- Upsert (INSERT ... ON CONFLICT)
- Savepoints в транзакциях

Запуск с Docker:
1. docker-compose up -d
2. python code/concurrency_consistency.py
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
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()


db = Database()


def setup_accounts():
    """Create accounts table for concurrency examples"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS accounts CASCADE;
            CREATE TABLE accounts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                version INTEGER DEFAULT 1
            );
            
            INSERT INTO accounts (name, balance) VALUES 
            ('Alice', 1000.00),
            ('Bob', 500.00);
        """)
    print("Accounts table created")


# === Race Condition Example ===
def transfer_without_lock(from_id: int, to_id: int, amount: float):
    """
    ПЕРВЫЙ ПРИМЕР: Race Condition
    Демонстрирует проблему гонки данных при одновременном обновлении
    """
    with db.get_cursor() as cursor:
        # Чтение баланса
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (from_id,))
        balance = float(cursor.fetchone()[0])
        
        # Симуляция задержки (для демонстрации race condition)
        time.sleep(0.1)
        
        # Проверка достаточности средств
        if balance >= amount:
            # Обновление баланса
            new_balance = balance - amount
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, from_id)
            )
            
            # Зачисление получателю
            cursor.execute(
                "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                (amount, to_id)
            )
            print(f"Transferred {amount} from {from_id} to {to_id}")
        else:
            print(f"Insufficient funds for account {from_id}")


def simulate_race_condition():
    """
    Демонстрация race condition:
    Два потока одновременно читают баланс и обновляют его
    Результат: баланс может быть некорректным
    """
    print("\n=== Race Condition Example ===")
    setup_accounts()
    
    # Два потока пытаются перевести деньги одновременно
    def transfer_task():
        transfer_without_lock(1, 2, 100.0)
    
    thread1 = threading.Thread(target=transfer_task)
    thread2 = threading.Thread(target=transfer_task)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    # Проверка результата
    with db.get_cursor() as cursor:
        cursor.execute("SELECT id, name, balance FROM accounts")
        accounts = cursor.fetchall()
        for acc in accounts:
            print(f"Account {acc[0]} ({acc[1]}): {acc[2]}")


# === Pessimistic Locking (SELECT FOR UPDATE) ===
def transfer_with_lock(from_id: int, to_id: int, amount: float):
    """
    ВТОРОЙ ПРИМЕР: Pessimistic Locking
    SELECT FOR UPDATE блокирует строку на время транзакции
    """
    with db.get_cursor() as cursor:
        # Блокировка строки на чтение
        cursor.execute(
            "SELECT balance FROM accounts WHERE id = %s FOR UPDATE",
            (from_id,)
        )
        balance = float(cursor.fetchone()[0])
        
        # Симуляция задержки
        time.sleep(0.1)
        
        if balance >= amount:
            new_balance = balance - amount
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, from_id)
            )
            
            cursor.execute(
                "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                (amount, to_id)
            )
            print(f"Transferred {amount} from {from_id} to {to_id} (with lock)")
        else:
            print(f"Insufficient funds for account {from_id}")


def simulate_pessimistic_locking():
    """
    Демонстрация pessimistic locking:
    Второй поток будет ждать, пока первый не завершит транзакцию
    """
    print("\n=== Pessimistic Locking Example ===")
    setup_accounts()
    
    def transfer_task():
        transfer_with_lock(1, 2, 100.0)
    
    thread1 = threading.Thread(target=transfer_task)
    thread2 = threading.Thread(target=transfer_task)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    with db.get_cursor() as cursor:
        cursor.execute("SELECT id, name, balance FROM accounts")
        accounts = cursor.fetchall()
        for acc in accounts:
            print(f"Account {acc[0]} ({acc[1]}): {acc[2]}")


# === Optimistic Locking ===
def transfer_optimistic(from_id: int, to_id: int, amount: float):
    """
    ТРЕТИЙ ПРИМЕР: Optimistic Locking
    Использует version для обнаружения конфликтов
    """
    max_retries = 3
    for attempt in range(max_retries):
        with db.get_cursor() as cursor:
            # Чтение текущих данных и версии
            cursor.execute(
                "SELECT balance, version FROM accounts WHERE id = %s",
                (from_id,)
            )
            balance, version = cursor.fetchone()
            balance = float(balance)
            
            if balance >= amount:
                # Обновление с проверкой
                cursor.execute(
                    """
                    UPDATE accounts 
                    SET balance = balance - %s, version = version + 1
                    WHERE id = %s AND version = %s
                    """,
                    (amount, from_id, version)
                )
                
                if cursor.rowcount == 0:
                    # Конфликт: версия изменилась
                    print(f"Conflict detected, retry {attempt + 1}/{max_retries}")
                    time.sleep(0.1)
                    continue
                
                # Зачисление
                cursor.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                    (amount, to_id)
                )
                print(f"Transferred {amount} from {from_id} to {to_id} (optimistic)")
                return
            else:
                print(f"Insufficient funds for account {from_id}")
                return
    
    print(f"Failed after {max_retries} retries")


def simulate_optimistic_locking():
    """
    Демонстрация optimistic locking:
    При конфликте происходит повторная попытка
    """
    print("\n=== Optimistic Locking Example ===")
    setup_accounts()
    
    def transfer_task():
        transfer_optimistic(1, 2, 100.0)
    
    thread1 = threading.Thread(target=transfer_task)
    thread2 = threading.Thread(target=transfer_task)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    with db.get_cursor() as cursor:
        cursor.execute("SELECT id, name, balance FROM accounts")
        accounts = cursor.fetchall()
        for acc in accounts:
            print(f"Account {acc[0]} ({acc[1]}): {acc[2]}")


# === Upsert (INSERT ... ON CONFLICT) ===
def demonstrate_upsert():
    """
    ЧЕТВЁРТЫЙ ПРИМЕР: Upsert
    INSERT ... ON CONFLICT DO UPDATE
    """
    print("\n=== Upsert Example ===")
    
    with db.get_cursor() as cursor:
        # Создание таблицы
        cursor.execute("""
            DROP TABLE IF EXISTS products CASCADE;
            CREATE TABLE products (
                sku VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                quantity INTEGER,
                price DECIMAL(10, 2)
            );
        """)
    
    # Первая вставка
    with db.get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO products (sku, name, quantity, price)
            VALUES ('SKU001', 'Laptop', 10, 999.99)
            ON CONFLICT (sku) DO UPDATE SET
                name = EXCLUDED.name,
                quantity = EXCLUDED.quantity,
                price = EXCLUDED.price
        """)
        print("Product inserted")
    
    # Повторная вставка (обновление)
    with db.get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO products (sku, name, quantity, price)
            VALUES ('SKU001', 'Laptop Pro', 15, 1099.99)
            ON CONFLICT (sku) DO UPDATE SET
                name = EXCLUDED.name,
                quantity = EXCLUDED.quantity,
                price = EXCLUDED.price
        """)
        print("Product updated (upsert)")
    
    # Проверка
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM products WHERE sku = 'SKU001'")
        product = cursor.fetchone()
        print(f"Product: {product}")


# === Transaction Isolation Levels ===
def demonstrate_isolation_levels():
    """
    ПЯТЫЙ ПРИМЕР: Уровни изоляции транзакций
    READ COMMITTED, REPEATABLE READ, SERIALIZABLE
    """
    print("\n=== Transaction Isolation Levels ===")
    
    # READ COMMITTED (по умолчанию в PostgreSQL)
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


# === Savepoints ===
def demonstrate_savepoints():
    """
    ШЕСТОЙ ПРИМЕР: Savepoints
    Частичный откат внутри транзакции
    """
    print("\n=== Savepoints Example ===")
    
    with db.get_cursor() as cursor:
        # Создание таблицы
        cursor.execute("""
            DROP TABLE IF EXISTS transactions CASCADE;
            CREATE TABLE transactions (
                id SERIAL PRIMARY KEY,
                description TEXT,
                amount DECIMAL(10, 2)
            );
        """)
    
    with db.get_cursor() as cursor:
        # Начало транзакции
        cursor.execute("INSERT INTO transactions (description, amount) VALUES ('First', 100.00)")
        
        # Создание savepoint
        cursor.execute("SAVEPOINT my_savepoint")
        
        cursor.execute("INSERT INTO transactions (description, amount) VALUES ('Second', 200.00)")
        
        # Откат к savepoint
        cursor.execute("ROLLBACK TO SAVEPOINT my_savepoint")
        print("Rolled back to savepoint")
        
        # Продолжение транзакции
        cursor.execute("INSERT INTO transactions (description, amount) VALUES ('Third', 300.00)")
        
        # Commit
        print("Transaction committed")
    
    # Проверка
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        for t in transactions:
            print(f"Transaction: {t}")


# === Batch Insert ===
def demonstrate_batch_insert():
    """
    СЕДЬМОЙ ПРИМЕР: Batch Insert
    Массовая вставка для производительности
    """
    print("\n=== Batch Insert Example ===")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS batch_test CASCADE;
            CREATE TABLE batch_test (
                id SERIAL PRIMARY KEY,
                data TEXT
            );
        """)
    
    # Одиночная вставка (медленно)
    start = time.time()
    with db.get_cursor() as cursor:
        for i in range(100):
            cursor.execute("INSERT INTO batch_test (data) VALUES (%s)", (f"item_{i}",))
    single_time = time.time() - start
    print(f"Single insert time: {single_time:.3f}s")
    
    # Очистка
    with db.get_cursor() as cursor:
        cursor.execute("TRUNCATE batch_test")
    
    # Batch insert (быстро)
    start = time.time()
    with db.get_cursor() as cursor:
        data = [(f"item_{i}",) for i in range(100)]
        cursor.executemany("INSERT INTO batch_test (data) VALUES (%s)", data)
    batch_time = time.time() - start
    print(f"Batch insert time: {batch_time:.3f}s")
    print(f"Speedup: {single_time / batch_time:.2f}x")


if __name__ == "__main__":
    print("=== Concurrency and Consistency Examples ===\n")
    
    try:
        # 1. Race Condition
        simulate_race_condition()
        
        # 2. Pessimistic Locking
        simulate_pessimistic_locking()
        
        # 3. Optimistic Locking
        simulate_optimistic_locking()
        
        # 4. Upsert
        demonstrate_upsert()
        
        # 5. Isolation Levels
        demonstrate_isolation_levels()
        
        # 6. Savepoints
        demonstrate_savepoints()
        
        # 7. Batch Insert
        demonstrate_batch_insert()
        
        print("\n=== All examples completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
