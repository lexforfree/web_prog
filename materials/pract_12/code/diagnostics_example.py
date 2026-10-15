"""
Diagnostics and Monitoring Example
Занятие 12: Интеграционные проверки и диагностика

Для запуска требуется: pip install flask prometheus-flask
"""

import uuid
import time
import logging
from flask import Flask, g, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ERROR_COUNT = Counter('app_errors_total', 'Total application errors', ['error_type'])

app = Flask(__name__)

# Setup Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')


@app.before_request
def add_request_id():
    """Generate Request ID for each request"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    
    logger.info(f"[{g.request_id}] Request started: {request.method} {request.path}")


@app.after_request
def log_request(response):
    """Log request with Request ID and metrics"""
    request_id = getattr(g, 'request_id', 'unknown')
    duration = time.time() - getattr(g, 'start_time', time.time())
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(duration)
    
    # Log
    logger.info(
        f"[{request_id}] Request completed: {request.method} {request.path} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    # Add Request ID to response
    response.headers['X-Request-ID'] = request_id
    
    return response


@app.errorhandler(Exception)
def handle_error(error):
    """Handle errors with logging and metrics"""
    request_id = getattr(g, 'request_id', 'unknown')
    error_type = type(error).__name__
    
    # Update error metrics
    ERROR_COUNT.labels(error_type=error_type).inc()
    
    # Log error
    logger.error(
        f"[{request_id}] Error: {error}",
        exc_info=True,
        extra={
            'request_id': request_id,
            'error_type': error_type,
            'path': request.path,
            'method': request.method
        }
    )
    
    return jsonify({
        'error': 'Internal server error',
        'request_id': request_id
    }), 500


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get users endpoint with diagnostics"""
    request_id = g.request_id
    
    logger.info(f"[{request_id}] Fetching users")
    
    # Simulate database query
    time.sleep(0.1)
    
    users = [
        {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
    ]
    
    logger.info(f"[{request_id}] Found {len(users)} users")
    
    return jsonify({'users': users, 'request_id': request_id})


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create user endpoint with validation and diagnostics"""
    request_id = g.request_id
    data = request.get_json()
    
    logger.info(f"[{request_id}] Creating user: {data.get('name')}")
    
    # Validation
    if not data or 'name' not in data or 'email' not in data:
        logger.warning(f"[{request_id}] Validation failed: missing fields")
        return jsonify({'error': 'Missing fields', 'request_id': request_id}), 400
    
    name = data['name']
    email = data['email']
    
    if len(name) < 2:
        logger.warning(f"[{request_id}] Validation failed: name too short")
        return jsonify({'error': 'Name too short', 'request_id': request_id}), 400
    
    if '@' not in email:
        logger.warning(f"[{request_id}] Validation failed: invalid email")
        return jsonify({'error': 'Invalid email', 'request_id': request_id}), 400
    
    # Simulate database insert
    time.sleep(0.05)
    
    user = {
        'id': 3,
        'name': name,
        'email': email
    }
    
    logger.info(f"[{request_id}] User created: {user['id']}")
    
    return jsonify(user), 201


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID with diagnostics"""
    request_id = g.request_id
    
    logger.info(f"[{request_id}] Fetching user: {user_id}")
    
    # Simulate database query
    time.sleep(0.05)
    
    if user_id == 999:
        logger.warning(f"[{request_id}] User not found: {user_id}")
        return jsonify({'error': 'User not found', 'request_id': request_id}), 404
    
    user = {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    }
    
    logger.info(f"[{request_id}] User found: {user_id}")
    
    return jsonify(user)


@app.route('/api/slow', methods=['GET'])
def slow_endpoint():
    """Slow endpoint for testing diagnostics"""
    request_id = g.request_id
    
    logger.warning(f"[{request_id}] Slow endpoint called")
    
    # Simulate slow operation
    time.sleep(2)
    
    logger.info(f"[{request_id}] Slow endpoint completed")
    
    return jsonify({'message': 'Done', 'request_id': request_id})


@app.route('/api/error', methods=['GET'])
def error_endpoint():
    """Endpoint that raises an error"""
    request_id = g.request_id
    
    logger.error(f"[{request_id}] Error endpoint called - will raise exception")
    
    raise ValueError("Simulated error for testing")


@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest
    from prometheus_client.core import CollectorRegistry
    
    registry = CollectorRegistry()
    registry.register(REQUEST_COUNT)
    registry.register(REQUEST_DURATION)
    registry.register(ERROR_COUNT)
    
    output = generate_latest(registry)
    return output, 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    print("=== Diagnostics and Monitoring Example ===")
    print("Run: python diagnostics_example.py")
    print("Open: http://localhost:5000")
    print()
    print("Endpoints:")
    print("  GET  /api/users")
    print("  POST /api/users")
    print("  GET  /api/users/<id>")
    print("  GET  /api/slow")
    print("  GET  /api/error")
    print("  GET  /metrics")
    print()
    print("Test with curl:")
    print('# Get users')
    print('curl http://localhost:5000/api/users')
    print()
    print('# Create user')
    print('curl -X POST http://localhost:5000/api/users \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "John", "email": "john@example.com"}\'')
    print()
    print('# Check Request ID')
    print('curl -i http://localhost:5000/api/users')
    print()
    print('# View metrics')
    print('curl http://localhost:5000/metrics')
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
