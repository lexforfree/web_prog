"""
CSRF Protection Example
Занятие 7: Состояние пользователя (Cookies, сессии, токены)

Для запуска требуется: pip install flask
"""

from flask import Flask, request, session, render_template_string
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def generate_csrf_token():
    """Generate CSRF token"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']


def validate_csrf_token(token):
    """Validate CSRF token"""
    session_token = session.get('csrf_token')
    if not session_token or not secrets.compare_digest(session_token, token):
        return False
    return True


@app.route('/')
def index():
    """Home page with links"""
    return '''
        <h1>CSRF Protection Demo</h1>
        <ul>
            <li><a href="/form">Form with CSRF protection</a></li>
            <li><a href="/vulnerable">Form without CSRF protection</a></li>
        </ul>
    '''


@app.route('/form')
def form():
    """Form with CSRF protection"""
    csrf_token = generate_csrf_token()
    
    return render_template_string('''
        <h2>Protected Form</h2>
        <form action="/submit" method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <input type="text" name="message" placeholder="Enter message" required><br><br>
            <button>Submit</button>
        </form>
        <p>CSRF Token: {{ csrf_token }}</p>
    ''', csrf_token=csrf_token)


@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission with CSRF validation"""
    csrf_token = request.form.get('csrf_token')
    
    if not validate_csrf_token(csrf_token):
        print("CSRF attack detected!")
        return "CSRF token validation failed! Possible attack.", 400
    
    message = request.form.get('message')
    print(f"Valid submission: {message}")
    
    return f"Message received: {message}"


@app.route('/vulnerable')
def vulnerable_form():
    """Form without CSRF protection (for demonstration)"""
    return render_template_string('''
        <h2>Vulnerable Form (No CSRF Protection)</h2>
        <form action="/vulnerable-submit" method="POST">
            <input type="text" name="message" placeholder="Enter message" required><br><br>
            <button>Submit</button>
        </form>
        <p style="color: red;">Warning: This form is vulnerable to CSRF attacks!</p>
    ''')


@app.route('/vulnerable-submit', methods=['POST'])
def vulnerable_submit():
    """Handle form submission without CSRF validation"""
    message = request.form.get('message')
    print(f"Submission (no CSRF check): {message}")
    
    return f"Message received: {message} (no CSRF protection)"


@app.route('/attack')
def attack_page():
    """Simulated CSRF attack page"""
    return render_template_string('''
        <h2>Simulated CSRF Attack</h2>
        <p>This page simulates a CSRF attack on the vulnerable form.</p>
        <p>When you visit this page while logged into the main app, it will automatically submit a form.</p>
        
        <h3>Attack on Vulnerable Form</h3>
        <form action="http://localhost:5000/vulnerable-submit" method="POST" id="attack-form">
            <input type="hidden" name="message" value="CSRF ATTACK!">
        </form>
        <script>
            // Auto-submit on page load
            document.getElementById('attack-form').submit();
        </script>
        
        <h3>Attack on Protected Form (Will Fail)</h3>
        <p>The protected form requires a valid CSRF token, so this attack will fail.</p>
        <form action="http://localhost:5000/submit" method="POST">
            <input type="hidden" name="message" value="CSRF ATTACK!">
        </form>
        <button onclick="this.previousElementSibling.submit()">Try to attack</button>
    ''')


@app.route('/api/protected', methods=['POST'])
def api_protected():
    """API endpoint with CSRF token validation"""
    csrf_token = request.headers.get('X-CSRF-Token')
    
    if not validate_csrf_token(csrf_token):
        return {'error': 'Invalid CSRF token'}, 400
    
    data = request.get_json()
    return {'message': 'Success', 'data': data}


@app.route('/api/csrf-token')
def get_csrf_token():
    """Get CSRF token for API"""
    token = generate_csrf_token()
    return {'csrf_token': token}


if __name__ == '__main__':
    print("=== CSRF Protection Demo ===")
    print("Run: python csrf_protection.py")
    print("Open: http://localhost:5000")
    print()
    print("Test CSRF attack:")
    print("1. Login to the main app")
    print("2. Visit http://localhost:5000/attack")
    print("3. Observe that the vulnerable form is attacked but the protected form is not")
    print()
    print("API usage:")
    print("# Get CSRF token")
    print('curl http://localhost:5000/api/csrf-token -c cookies.txt')
    print()
    print("# Make protected request")
    print('curl -X POST http://localhost:5000/api/protected \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "X-CSRF-Token: YOUR_TOKEN" \\')
    print('  -b cookies.txt \\')
    print('  -d \'{"data": "test"}\'')
    print()
    
    app.run(debug=True, port=5000)
