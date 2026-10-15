"""
Security Examples
Занятие 11: Безопасность веб-приложения

Для запуска требуется: pip install flask flask-cors bcrypt python-dotenv
"""

import os
import secrets
import bcrypt
from flask import Flask, request, jsonify, render_template_string
from functools import wraps
from dotenv import load_dotenv
from html import escape

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Mock database
users_db = {}
posts_db = {}
next_user_id = 1
next_post_id = 1


# Password hashing
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# RBAC
class User:
    def __init__(self, user_id: int, username: str, password: str, roles: list):
        self.id = user_id
        self.username = username
        self.password_hash = hash_password(password)
        self.roles = roles
    
    @property
    def permissions(self):
        """Get permissions based on roles"""
        role_permissions = {
            'admin': ['users.read', 'users.write', 'users.delete', 'posts.read', 'posts.write', 'posts.delete'],
            'editor': ['posts.read', 'posts.write'],
            'user': ['posts.read'],
            'guest': ['posts.read']
        }
        
        permissions = set()
        for role in self.roles:
            permissions.update(role_permissions.get(role, []))
        
        return list(permissions)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has permission"""
        return permission in self.permissions


# Decorators
def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = int(token)  # Simplified - use JWT in production
        
        if user_id not in users_db:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.user = users_db[user_id]
        return f(*args, **kwargs)
    
    return wrapper


def require_permission(permission: str):
    """Require specific permission"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            if not request.user.has_permission(permission):
                return jsonify({'error': 'Forbidden'}), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def check_ownership(resource, resource_id: int):
    """Check if current user owns the resource"""
    if not hasattr(request, 'user'):
        return False
    
    # Admin can access everything
    if 'admin' in request.user.roles:
        return True
    
    # Check ownership
    if resource == 'post':
        post = posts_db.get(resource_id)
        if post and post['author_id'] == request.user.id:
            return True
    
    return False


# Routes
@app.route('/register', methods=['POST'])
def register():
    """Register new user with hashed password"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    roles = data.get('roles', ['user'])
    
    if not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
    
    if any(u['username'] == username for u in users_db.values()):
        return jsonify({'error': 'User already exists'}), 400
    
    global next_user_id
    user = User(next_user_id, username, password, roles)
    users_db[next_user_id] = user
    next_user_id += 1
    
    return jsonify({'message': 'User registered', 'user_id': user.id}), 201


@app.route('/login', methods=['POST'])
def login():
    """Login with password verification"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = next((u for u in users_db.values() if u.username == username), None)
    
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Simplified - use JWT in production
    token = str(user.id)
    
    return jsonify({
        'token': token,
        'user_id': user.id,
        'username': user.username,
        'roles': user.roles
    })


@app.route('/posts', methods=['GET'])
@require_auth
@require_permission('posts.read')
def list_posts():
    """List all posts"""
    return jsonify({'posts': list(posts_db.values())})


@app.route('/posts', methods=['POST'])
@require_auth
@require_permission('posts.write')
def create_post():
    """Create new post"""
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': 'Missing fields'}), 400
    
    global next_post_id
    post = {
        'id': next_post_id,
        'title': title,
        'content': content,
        'author_id': request.user.id,
        'author': request.user.username
    }
    posts_db[next_post_id] = post
    next_post_id += 1
    
    return jsonify(post), 201


@app.route('/posts/<int:post_id>', methods=['PUT'])
@require_auth
@require_permission('posts.write')
def update_post(post_id: int):
    """Update post (only author or admin)"""
    if not check_ownership('post', post_id):
        return jsonify({'error': 'Forbidden'}), 403
    
    post = posts_db.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']
    
    return jsonify(post)


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@require_auth
@require_permission('posts.delete')
def delete_post(post_id: int):
    """Delete post (only author or admin)"""
    if not check_ownership('post', post_id):
        return jsonify({'error': 'Forbidden'}), 403
    
    if post_id not in posts_db:
        return jsonify({'error': 'Post not found'}), 404
    
    del posts_db[post_id]
    return jsonify({'message': 'Post deleted'})


@app.route('/xss-demo')
def xss_demo():
    """XSS demonstration"""
    comment = request.args.get('comment', '')
    
    # Vulnerable (don't use in production!)
    vulnerable_html = f"<div>{comment}</div>"
    
    # Safe
    safe_html = f"<div>{escape(comment)}</div>"
    
    return render_template_string('''
        <h1>XSS Demo</h1>
        <h2>Vulnerable:</h2>
        {{ vulnerable_html|safe }}
        <h2>Safe:</h2>
        {{ safe_html }}
        <p>Try: ?comment=<script>alert('XSS')</script></p>
    ''', vulnerable_html=vulnerable_html, safe_html=safe_html)


@app.route('/csrf-demo')
def csrf_demo():
    """CSRF token demonstration"""
    csrf_token = secrets.token_hex(16)
    
    return render_template_string('''
        <h1>CSRF Demo</h1>
        <form action="/csrf-submit" method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <input type="text" name="message" placeholder="Message">
            <button>Submit</button>
        </form>
        <p>CSRF Token: {{ csrf_token }}</p>
    ''', csrf_token=csrf_token)


@app.route('/csrf-submit', methods=['POST'])
def csrf_submit():
    """CSRF token validation"""
    token = request.form.get('csrf_token')
    session_token = session.get('csrf_token')
    
    if not session_token:
        session['csrf_token'] = secrets.token_hex(16)
        session_token = session['csrf_token']
    
    if not secrets.compare_digest(token, session_token):
        return "CSRF token validation failed!", 400
    
    message = request.form.get('message')
    return f"Message received: {message}"


# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers"""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    print("=== Security Examples ===")
    print("Run: python security_examples.py")
    print("Open: http://localhost:5000")
    print()
    print("Test with curl:")
    print("# Register")
    print('curl -X POST http://localhost:5000/register \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username": "admin", "password": "admin123", "roles": ["admin"]}\'')
    print()
    print("# Login")
    print('curl -X POST http://localhost:5000/login \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username": "admin", "password": "admin123"}\'')
    print()
    print("# Create post")
    print('curl -X POST http://localhost:5000/posts \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "Authorization: Bearer YOUR_TOKEN" \\')
    print('  -d \'{"title": "Test", "content": "Test content"}\'')
    print()
    
    app.run(debug=True, port=5000)
