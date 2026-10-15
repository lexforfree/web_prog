"""
JWT Authentication Example
Занятие 7: Состояние пользователя (Cookies, сессии, токены)

Для запуска требуется: pip install flask flask-cors pyjwt bcrypt redis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import bcrypt
import redis
import secrets

app = Flask(__name__)
CORS(app)

# Configuration
SECRET_KEY = secrets.token_hex(32)
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Redis for blacklist
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Mock database
users_db = {
    'john': {
        'password_hash': bcrypt.hashpw(b'password123', bcrypt.gensalt()),
        'email': 'john@example.com',
        'user_id': 1
    }
}

refresh_tokens_db = {}  # In production, use database


def create_access_token(user_id: int, username: str) -> str:
    """Create JWT access token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def create_refresh_token(user_id: int) -> str:
    """Create refresh token"""
    token = secrets.token_urlsafe(32)
    refresh_tokens_db[token] = {
        'user_id': user_id,
        'expires': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return token


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        # Check blacklist
        if redis_client.exists(f'blacklist:{token}'):
            return None
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None


def require_auth(f):
    """Decorator for protected routes"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing fields'}), 400
    
    if username in users_db:
        return jsonify({'error': 'User already exists'}), 400
    
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users_db[username] = {
        'password_hash': password_hash,
        'email': email,
        'user_id': len(users_db) + 1
    }
    
    return jsonify({'message': 'User registered'}), 201


@app.route('/login', methods=['POST'])
def login():
    """Login and return tokens"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    
    if username not in users_db:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user = users_db[username]
    
    if not bcrypt.checkpw(password.encode(), user['password_hash']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create tokens
    access_token = create_access_token(user['user_id'], username)
    refresh_token = create_refresh_token(user['user_id'])
    
    print(f"User {username} logged in")
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60
    })


@app.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'Missing refresh token'}), 400
    
    # Check refresh token
    if refresh_token not in refresh_tokens_db:
        return jsonify({'error': 'Invalid refresh token'}), 401
    
    token_data = refresh_tokens_db[refresh_token]
    
    # Check expiration
    if datetime.utcnow() > token_data['expires']:
        del refresh_tokens_db[refresh_token]
        return jsonify({'error': 'Refresh token expired'}), 401
    
    # Get user
    user_id = token_data['user_id']
    username = next((u for u, d in users_db.items() if d['user_id'] == user_id), None)
    
    if not username:
        return jsonify({'error': 'User not found'}), 404
    
    # Create new access token
    access_token = create_access_token(user_id, username)
    
    # Rotate refresh token (optional)
    del refresh_tokens_db[refresh_token]
    new_refresh_token = create_refresh_token(user_id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': new_refresh_token
    })


@app.route('/profile')
@require_auth
def profile():
    """Protected profile endpoint"""
    user = request.user
    
    return jsonify({
        'user_id': user['user_id'],
        'username': user['username'],
        'message': 'This is protected data'
    })


@app.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout and blacklist token"""
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    
    # Add to blacklist
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    exp = payload['exp']
    ttl = exp - datetime.utcnow().timestamp()
    
    if ttl > 0:
        redis_client.setex(f'blacklist:{token}', int(ttl), '1')
    
    # Delete refresh token
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if refresh_token in refresh_tokens_db:
        del refresh_tokens_db[refresh_token]
    
    print(f"User {request.user['username']} logged out")
    
    return jsonify({'message': 'Logged out'})


@app.route('/protected')
@require_auth
def protected():
    """Another protected endpoint"""
    return jsonify({'message': 'Access granted', 'user': request.user})


if __name__ == '__main__':
    print("=== JWT Authentication ===")
    print("Run: python jwt_auth.py")
    print("Make sure Redis is running: redis-server")
    print()
    print("Test with curl:")
    print("# Register")
    print('curl -X POST http://localhost:5000/register \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username": "jane", "email": "jane@example.com", "password": "pass123"}\'')
    print()
    print("# Login")
    print('curl -X POST http://localhost:5000/login \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username": "john", "password": "password123"}\'')
    print()
    print("# Access protected endpoint")
    print('curl http://localhost:5000/profile \\')
    print('  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"')
    print()
    print("# Refresh token")
    print('curl -X POST http://localhost:5000/refresh \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"refresh_token": "YOUR_REFRESH_TOKEN"}\'')
    print()
    
    app.run(debug=True, port=5000)
