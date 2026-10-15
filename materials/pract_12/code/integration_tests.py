"""
Integration Tests Example
Занятие 12: Интеграционные проверки и диагностика

Для запуска требуется: pip install pytest pytest-flask psycopg2-binary python-dotenv prometheus-flask
"""

import os
import uuid
import time
import pytest
import psycopg2
from flask import Flask, g, jsonify, request
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics

load_dotenv()

# Test database URL
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL', 
                                'postgresql://test:test@localhost:5432/test_db')


class UserRepository:
    """User repository for database operations"""
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
    
    def create(self, name: str, email: str) -> int:
        self.cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
            (name, email)
        )
        user_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return user_id
    
    def find_by_id(self, user_id: int):
        self.cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2]}
        return None
    
    def find_by_email(self, email: str):
        self.cursor.execute("SELECT id, name, email FROM users WHERE email = %s", (email,))
        row = self.cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2]}
        return None
    
    def close(self):
        self.cursor.close()


class UserService:
    """User service with business logic"""
    
    def __init__(self, user_repo):
        self.user_repo = user_repo
    
    def create_user(self, name: str, email: str):
        if len(name) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        if not '@' in email:
            raise ValueError("Invalid email format")
        
        if self.user_repo.find_by_email(email):
            raise ValueError("Email already exists")
        
        user_id = self.user_repo.create(name, email)
        return {'id': user_id, 'name': name, 'email': email}


# Flask application
app = Flask(__name__)
app.config['TESTING'] = True

# Prometheus metrics
metrics = PrometheusMetrics(app)


@app.before_request
def add_request_id():
    """Generate and store request ID"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()


@app.after_request
def add_request_id_header(response):
    """Add Request ID to response headers"""
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
        
        # Log request duration
        duration = time.time() - g.start_time
        print(f"[{g.request_id}] {request.method} {request.path} - {response.status_code} - {duration:.3f}s")
    
    return response


@app.route('/users', methods=['POST'])
def create_user():
    """Create user endpoint with logging"""
    request_id = g.request_id
    data = request.get_json()
    
    print(f"[{request_id}] Creating user: {data}")
    
    try:
        conn = psycopg2.connect(TEST_DATABASE_URL)
        repo = UserRepository(conn)
        service = UserService(repo)
        
        user = service.create_user(data['name'], data['email'])
        
        print(f"[{request_id}] User created: {user['id']}")
        
        repo.close()
        conn.close()
        
        return jsonify(user), 201
        
    except ValueError as e:
        print(f"[{request_id}] Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"[{request_id}] Internal error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user endpoint with Request ID"""
    request_id = g.request_id
    
    print(f"[{request_id}] Getting user: {user_id}")
    
    try:
        conn = psycopg2.connect(TEST_DATABASE_URL)
        repo = UserRepository(conn)
        
        user = repo.find_by_id(user_id)
        
        repo.close()
        conn.close()
        
        if not user:
            print(f"[{request_id}] User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        print(f"[{request_id}] User found: {user_id}")
        return jsonify(user)
        
    except Exception as e:
        print(f"[{request_id}] Internal error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


# Pytest fixtures
@pytest.fixture
def test_db():
    """Setup test database with clean state"""
    conn = psycopg2.connect(TEST_DATABASE_URL)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    
    # Clean table
    cursor.execute("TRUNCATE TABLE users CASCADE")
    conn.commit()
    
    yield conn
    
    # Cleanup
    cursor.execute("TRUNCATE TABLE users CASCADE")
    conn.commit()
    cursor.close()
    conn.close()


@pytest.fixture
def test_app():
    """Setup test Flask app"""
    app.config['TESTING'] = True
    return app.test_client()


# Integration tests
def test_create_user_integration(test_db):
    """Integration test: create user with real database"""
    repo = UserRepository(test_db)
    service = UserService(repo)
    
    # Create user
    user = service.create_user("John Doe", "john@example.com")
    
    # Verify in database
    saved_user = repo.find_by_id(user['id'])
    assert saved_user is not None
    assert saved_user['name'] == "John Doe"
    assert saved_user['email'] == "john@example.com"
    
    repo.close()


def test_create_user_duplicate_email_integration(test_db):
    """Integration test: duplicate email error"""
    repo = UserRepository(test_db)
    service = UserService(repo)
    
    # Create first user
    service.create_user("John Doe", "john@example.com")
    
    # Try to create duplicate
    with pytest.raises(ValueError, match="Email already exists"):
        service.create_user("Jane Doe", "john@example.com")
    
    repo.close()


def test_create_user_via_api(test_app, test_db):
    """Integration test: create user via API"""
    response = test_app.post('/users', json={
        'name': 'John Doe',
        'email': 'john@example.com'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'John Doe'
    assert data['email'] == 'john@example.com'
    
    # Verify in database
    repo = UserRepository(test_db)
    user = repo.find_by_email('john@example.com')
    assert user is not None
    repo.close()


def test_get_user_via_api(test_app, test_db):
    """Integration test: get user via API"""
    # Create user
    repo = UserRepository(test_db)
    user_id = repo.create("John Doe", "john@example.com")
    repo.close()
    
    # Get user via API
    response = test_app.get(f'/users/{user_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == user_id
    assert data['name'] == 'John Doe'
    assert 'X-Request-ID' in response.headers


def test_request_id_in_logs(test_app, test_db, capsys):
    """Test that Request ID appears in logs"""
    response = test_app.post('/users', json={
        'name': 'John Doe',
        'email': 'john@example.com'
    })
    
    # Check Request ID in response
    assert 'X-Request-ID' in response.headers
    request_id = response.headers['X-Request-ID']
    
    # Check logs (captured by capsys)
    captured = capsys.readouterr()
    assert request_id in captured.out


def test_regression_price_calculation():
    """Regression test for price calculation bug"""
    
    class Product:
        def __init__(self, price, discount):
            self.price = price
            self.discount = discount
        
        def calculate_final_price_buggy(self):
            """Buggy version - returns discount amount instead of final price"""
            return self.price * self.discount / 100
        
        def calculate_final_price_fixed(self):
            """Fixed version - returns final price"""
            return self.price - (self.price * self.discount / 100)
    
    product = Product(price=100, discount=10)
    
    # Test would catch the bug
    assert product.calculate_final_price_fixed() == 90  # Correct
    assert product.calculate_final_price_buggy() != 90  # Bug: returns 10


if __name__ == '__main__':
    print("=== Integration Tests Example ===")
    print("Run: pytest integration_tests.py -v")
    print()
    print("Run with coverage:")
    print("pytest integration_tests.py --cov=. --cov-report=html")
    print()
    print("Run specific test:")
    print("pytest integration_tests.py::test_create_user_integration -v")
