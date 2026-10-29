"""
Transaction Examples with Docker
Занятие 9: Транзакции и индексы

Для запуска требуется: pip install psycopg2-binary python-dotenv

Запуск с Docker:
1. docker-compose up -d
2. python code/transactions.py
"""

import os
import psycopg2
from psycopg2 import pool, sql
from contextlib import contextmanager
from dotenv import load_dotenv
import threading
import time

load_dotenv()


class Database:
    """Database connection manager"""
    
    def __init__(self):
        # Подключение к Docker контейнеру
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
        """Context manager for connection"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        """Context manager for cursor with transaction"""
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
        """Close all connections"""
        self.connection_pool.closeall()


db = Database()


def create_tables():
    """Create accounts and courses tables"""
    with db.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                balance DECIMAL(10, 2) NOT NULL CHECK (balance >= 0)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                seats INTEGER NOT NULL CHECK (seats >= 0)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                UNIQUE(user_id, course_id)
            );
        """)
    
    print("Tables created")


def transfer_money(from_id: int, to_id: int, amount: float) -> bool:
    """
    Transfer money between accounts using transaction
    
    This demonstrates atomicity - both updates succeed or both fail
    """
    with db.get_cursor() as cursor:
        # Check balance
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (from_id,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError("Source account not found")
        
        balance = result[0]
        
        if balance < amount:
            raise ValueError(f"Insufficient balance: {balance}")
        
        # Deduct from source
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE id = %s",
            (amount, from_id)
        )
        
        # Add to destination
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE id = %s",
            (amount, to_id)
        )
        
        print(f"Transferred {amount} from account {from_id} to {to_id}")
        return True


def transfer_without_transaction(from_id: int, to_id: int, amount: float) -> bool:
    """
    Transfer WITHOUT transaction - demonstrates the problem
    
    DO NOT USE THIS IN PRODUCTION!
    """
    conn = db.connection_pool.getconn()
    cursor = conn.cursor()
    
    try:
        # Check balance
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (from_id,))
        result = cursor.fetchone()
        balance = result[0]
        
        if balance < amount:
            raise ValueError(f"Insufficient balance: {balance}")
        
        # Deduct from source
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE id = %s",
            (amount, from_id)
        )
        conn.commit()  # Commit immediately!
        
        # Simulate error
        if to_id == 999:
            raise ValueError("Destination account not found")
        
        # Add to destination
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE id = %s",
            (amount, to_id)
        )
        conn.commit()
        
        print(f"Transferred {amount} from account {from_id} to {to_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise e
    finally:
        cursor.close()
        db.connection_pool.putconn(conn)


def register_course_atomic(course_id: int, user_id: int) -> bool:
    """
    Register for course using atomic UPDATE
    
    This solves race condition by making check and update atomic
    """
    with db.get_cursor() as cursor:
        # Atomic check and update
        cursor.execute(
            "UPDATE courses SET seats = seats - 1 WHERE id = %s AND seats > 0",
            (course_id,)
        )
        
        if cursor.rowcount == 0:
            print("No seats available")
            return False
        
        # Add registration
        cursor.execute(
            "INSERT INTO registrations (user_id, course_id) VALUES (%s, %s)",
            (user_id, course_id)
        )
        
        print(f"User {user_id} registered for course {course_id}")
        return True


def register_course_select_for_update(course_id: int, user_id: int) -> bool:
    """
    Register for course using SELECT FOR UPDATE
    
    This locks the row to prevent race conditions
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Begin transaction
            cursor.execute("BEGIN")
            
            # Lock the row
            cursor.execute(
                "SELECT seats FROM courses WHERE id = %s FOR UPDATE",
                (course_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                conn.rollback()
                raise ValueError("Course not found")
            
            seats = result[0]
            
            if seats <= 0:
                conn.rollback()
                print("No seats available")
                return False
            
            # Update seats
            cursor.execute(
                "UPDATE courses SET seats = seats - 1 WHERE id = %s",
                (course_id,)
            )
            
            # Add registration
            cursor.execute(
                "INSERT INTO registrations (user_id, course_id) VALUES (%s, %s)",
                (user_id, course_id)
            )
            
            conn.commit()
            print(f"User {user_id} registered for course {course_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            raise e
        finally:
            cursor.close()


def register_course_race_condition(course_id: int, user_id: int) -> bool:
    """
    Register WITHOUT proper locking - demonstrates race condition
    
    DO NOT USE THIS IN PRODUCTION!
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check seats (NOT locked!)
            cursor.execute(
                "SELECT seats FROM courses WHERE id = %s",
                (course_id,)
            )
            result = cursor.fetchone()
            seats = result[0]
            
            # Simulate delay to make race condition more likely
            time.sleep(0.01)
            
            if seats <= 0:
                print("No seats available")
                return False
            
            # Update seats
            cursor.execute(
                "UPDATE courses SET seats = seats - 1 WHERE id = %s",
                (course_id,)
            )
            
            # Add registration
            cursor.execute(
                "INSERT INTO registrations (user_id, course_id) VALUES (%s, %s)",
                (user_id, course_id)
            )
            
            conn.commit()
            print(f"User {user_id} registered for course {course_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            raise e
        finally:
            cursor.close()


def simulate_race_condition():
    """Simulate race condition with multiple threads"""
    print("\n=== Simulating Race Condition ===")
    
    # Reset course
    with db.get_cursor() as cursor:
        cursor.execute("UPDATE courses SET seats = 2 WHERE id = 1")
    
    def register_user(user_id):
        try:
            register_course_race_condition(1, user_id)
        except Exception as e:
            print(f"User {user_id} failed: {e}")
    
    # Create 5 threads trying to register for 2 seats
    threads = []
    for i in range(5):
        t = threading.Thread(target=register_user, args=(i,))
        threads.append(t)
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    # Check final state
    with db.get_cursor() as cursor:
        cursor.execute("SELECT seats FROM courses WHERE id = 1")
        seats = cursor.fetchone()[0]
        print(f"Final seats: {seats} (should be 0 or negative if race condition occurred)")


def register_with_unique_constraint(course_id: int, user_id: int) -> bool:
    """
    Register using UNIQUE constraint
    
    Database enforces uniqueness automatically
    """
    with db.get_cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO registrations (user_id, course_id) VALUES (%s, %s)",
                (user_id, course_id)
            )
            print(f"User {user_id} registered for course {course_id}")
            return True
        except psycopg2.IntegrityError:
            print(f"User {user_id} already registered for course {course_id}")
            return False


# Example usage
if __name__ == "__main__":
    print("=== Transaction Examples ===\n")
    
    try:
        # Create tables
        create_tables()
        
        # Create test accounts
        with db.get_cursor() as cursor:
            cursor.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", ("Alice", 1000.00))
            cursor.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", ("Bob", 500.00))
        
        # Create test course
        with db.get_cursor() as cursor:
            cursor.execute("INSERT INTO courses (name, seats) VALUES (%s, %s)", ("Python Course", 10))
        
        # Get IDs
        with db.get_cursor() as cursor:
            cursor.execute("SELECT id FROM accounts WHERE name = 'Alice'")
            alice_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM accounts WHERE name = 'Bob'")
            bob_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM courses WHERE name = 'Python Course'")
            course_id = cursor.fetchone()[0]
        
        print(f"Alice ID: {alice_id}, Bob ID: {bob_id}, Course ID: {course_id}")
        
        # Transfer with transaction
        print("\n=== Transfer with Transaction ===")
        transfer_money(alice_id, bob_id, 100.00)
        
        # Check balances
        with db.get_cursor() as cursor:
            cursor.execute("SELECT name, balance FROM accounts")
            for row in cursor.fetchall():
                print(f"{row[0]}: ${row[1]}")
        
        # Register with atomic UPDATE
        print("\n=== Register with Atomic UPDATE ===")
        register_course_atomic(course_id, alice_id)
        register_course_atomic(course_id, bob_id)
        
        # Check seats
        with db.get_cursor() as cursor:
            cursor.execute("SELECT seats FROM courses WHERE id = %s", (course_id,))
            seats = cursor.fetchone()[0]
            print(f"Remaining seats: {seats}")
        
        # Register with UNIQUE constraint
        print("\n=== Register with UNIQUE Constraint ===")
        register_with_unique_constraint(course_id, alice_id)  # Should fail
        register_with_unique_constraint(course_id, 999)  # Should succeed
        
        # Simulate race condition
        # simulate_race_condition()  # Uncomment to test
        
        # Register with SELECT FOR UPDATE
        print("\n=== Register with SELECT FOR UPDATE ===")
        register_course_select_for_update(course_id, 999)
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close_all()
