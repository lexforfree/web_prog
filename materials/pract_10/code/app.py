"""
Simple Flask Application for Nginx Reverse Proxy Demo
Занятие 10: Nginx и Reverse Proxy

Для запуска требуется: pip install flask gunicorn
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# Get container ID for identification
CONTAINER_ID = os.getenv('HOSTNAME', 'unknown')


@app.route('/')
def home():
    """Home page"""
    return render_template_string('''
        <h1>Backend Application</h1>
        <p>Container: {{ container_id }}</p>
        <p><a href="/api/time">API Time</a></p>
        <p><a href="/api/headers">Request Headers</a></p>
        <p><a href="/api/long-running">Long Running Request</a></p>
    ''', container_id=CONTAINER_ID)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "container": CONTAINER_ID})


@app.route('/api/time')
def get_time():
    """Get current time"""
    return jsonify({
        "time": datetime.now().isoformat(),
        "container": CONTAINER_ID,
        "timestamp": datetime.now().timestamp()
    })


@app.route('/api/headers')
def get_headers():
    """Get request headers"""
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ['host', 'connection']
    }
    return jsonify({
        "container": CONTAINER_ID,
        "headers": headers
    })


@app.route('/api/long-running')
def long_running():
    """Simulate long-running request"""
    import time
    duration = request.args.get('duration', 5, type=int)
    
    time.sleep(duration)
    
    return jsonify({
        "message": f"Completed after {duration} seconds",
        "container": CONTAINER_ID,
        "duration": duration
    })


@app.route('/api/info')
def info():
    """Get application info"""
    return jsonify({
        "container": CONTAINER_ID,
        "environment": dict(os.environ),
        "remote_addr": request.remote_addr,
        "headers": {
            "X-Real-IP": request.headers.get('X-Real-IP'),
            "X-Forwarded-For": request.headers.get('X-Forwarded-For'),
            "X-Forwarded-Proto": request.headers.get('X-Forwarded-Proto'),
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found", "container": CONTAINER_ID}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error", "container": CONTAINER_ID}), 500


if __name__ == '__main__':
    print(f"Starting application on container {CONTAINER_ID}")
    print("Available endpoints:")
    print("  - GET /")
    print("  - GET /health")
    print("  - GET /api/time")
    print("  - GET /api/headers")
    print("  - GET /api/long-running?duration=5")
    print("  - GET /api/info")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
