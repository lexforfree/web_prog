"""
SQL Injection Demonstration
Занятие 11: Безопасность веб-приложения

Для запуска требуется: pip install psycopg2-binary python-dotenv
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class SQLInjectionDemo:
    """Demonstrate SQL injection vulnerabilities and fixes"""
    
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'webprog'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create test tables"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100)
            );
        """)
        
        self.cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                         ('admin', 'hashed_password', 'admin@example.com'))
        self.cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                         ('user1', 'hashed_password', 'user1@example.com'))
        
        self.conn.commit()
        print("Tables created and test data inserted")
    
    # VULNERABLE - DO NOT USE IN PRODUCTION
    def search_user_vulnerable(self, email: str):
        """
        VULNERABLE: Direct string interpolation
        DO NOT USE THIS IN PRODUCTION!
        """
        query = f"SELECT * FROM users WHERE email = '{email}'"
        print(f"Query: {query}")
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results
    
    # SAFE - Use this in production
    def search_user_safe(self, email: str):
        """
        SAFE: Parameterized query
        Use this in production
        """
        query = "SELECT * FROM users WHERE email = %s"
        print(f"Query: {query}")
        print(f"Parameters: {email}")
        
        self.cursor.execute(query, (email,))
        results = self.cursor.fetchall()
        return results


def demonstrate_attacks():
    """Demonstrate SQL injection attacks"""
    demo = SQLInjectionDemo()
    
    try:
        demo.create_tables()
        
        print("\n=== Attack 1: Bypass email search ===")
        print("Normal search:")
        results = demo.search_user_vulnerable("admin@example.com")
        print(f"Results: {results}")
        
        print("\nMalicious search (OR '1'='1'):")
        results = demo.search_user_vulnerable("' OR '1'='1")
        print(f"Results: {results} (returns all users!)")
        
        print("\nSafe search:")
        results = demo.search_user_safe("' OR '1'='1")
        print(f"Results: {results} (returns nothing - safe!)")
        
    except Exception as e:
        print(f"Error: {e}")
        demo.conn.rollback()
    
    finally:
        demo.close()


if __name__ == "__main__":
    print("=== SQL Injection Demonstration ===")
    print("WARNING: This demonstrates vulnerabilities for educational purposes only!")
    print("NEVER use vulnerable code in production!\n")
    
    demonstrate_attacks()
