"""
Session-based Authentication Example
Занятие 7: Состояние пользователя (Cookies, сессии, токены)

Для запуска требуется: pip install flask bcrypt
"""

from flask import Flask, request, session, make_response, render_template_string
import bcrypt
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Для подписи session cookie

# Mock database
users_db = {
    'john': {
        'password_hash': bcrypt.hashpw(b'password123', bcrypt.gensalt()),
        'email': 'john@example.com',
        'user_id': 1
    }
}


@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return f"Welcome, user {session['user_id']}! <a href='/logout'>Logout</a>"
    return "Welcome! <a href='/login'>Login</a> | <a href='/register'>Register</a>"


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'GET':
        return '''
            <h2>Register</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="email" name="email" placeholder="Email" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <button>Register</button>
            </form>
        '''
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check if user exists
    if username in users_db:
        return "User already exists", 400
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Save user
    users_db[username] = {
        'password_hash': password_hash,
        'email': email,
        'user_id': len(users_db) + 1
    }
    
    return f"User {username} registered! <a href='/login'>Login</a>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if request.method == 'GET':
        return '''
            <h2>Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <button>Login</button>
            </form>
        '''
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Check user
    if username not in users_db:
        return "Invalid credentials", 401
    
    user = users_db[username]
    
    # Check password
    if not bcrypt.checkpw(password.encode(), user['password_hash']):
        return "Invalid credentials", 401
    
    # Save session
    session['user_id'] = user['user_id']
    session['username'] = username
    session['login_time'] = datetime.now().isoformat()
    
    print(f"User {username} logged in at {session['login_time']}")
    
    return f"Logged in as {username}! <a href='/profile'>Profile</a>"


@app.route('/profile')
def profile():
    """Protected profile page"""
    if 'user_id' not in session:
        return "Unauthorized. <a href='/login'>Login</a>", 401
    
    user_id = session['user_id']
    username = session['username']
    login_time = session.get('login_time')
    
    return f'''
        <h2>Profile</h2>
        <p>User ID: {user_id}</p>
        <p>Username: {username}</p>
        <p>Login time: {login_time}</p>
        <a href='/logout'>Logout</a>
    '''


@app.route('/logout')
def logout():
    """Logout user"""
    username = session.get('username')
    session.clear()
    print(f"User {username} logged out")
    return "Logged out! <a href='/login'>Login</a>"


@app.route('/set-cookie')
def set_cookie():
    """Set custom cookie"""
    resp = make_response("Cookie set!")
    
    # Session cookie (expires when browser closes)
    resp.set_cookie('session_data', 'value123')
    
    # Persistent cookie (30 days)
    resp.set_cookie('user_preference', 'dark_mode', max_age=30*24*60*60)
    
    # Secure cookie attributes
    resp.set_cookie('auth_token', 'token123', httponly=True, secure=True, samesite='Strict')
    
    return resp


@app.route('/get-cookie')
def get_cookie():
    """Read cookies"""
    session_data = request.cookies.get('session_data')
    user_preference = request.cookies.get('user_preference')
    auth_token = request.cookies.get('auth_token')
    
    return f"""
        session_data: {session_data}<br>
        user_preference: {user_preference}<br>
        auth_token: {auth_token}
    """


@app.route('/delete-cookie')
def delete_cookie():
    """Delete cookie"""
    resp = make_response("Cookie deleted!")
    resp.set_cookie('session_data', '', expires=0)
    return resp


if __name__ == '__main__':
    print("=== Session-based Authentication ===")
    print("Run: python session_auth.py")
    print("Open: http://localhost:5000")
    print()
    print("Test with curl:")
    print("# Login")
    print('curl -c cookies.txt -X POST http://localhost:5000/login \\')
    print('  -d "username=john&password=password123"')
    print()
    print("# Access protected page")
    print('curl -b cookies.txt http://localhost:5000/profile')
    print()
    print("# Logout")
    print('curl -b cookies.txt http://localhost:5000/logout')
    print()
    
    app.run(debug=True, port=5000)
