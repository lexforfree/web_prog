"""
Flask Validation Examples
Занятие 4: Валидация, бизнес-правила и обработка ошибок

Для запуска требуется: pip install flask
"""

from flask import Flask, request, jsonify
from typing import Dict, Tuple, Optional


app = Flask(__name__)


# Custom exceptions
class ValidationError(Exception):
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__(f"Validation error: {errors}")


class BusinessRuleError(Exception):
    def __init__(self, message: str, code: str = "BUSINESS_RULE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError) -> Tuple[Dict, int]:
    return jsonify({
        "error": "Validation error",
        "details": e.errors
    }), 400


@app.errorhandler(BusinessRuleError)
def handle_business_rule_error(e: BusinessRuleError) -> Tuple[Dict, int]:
    return jsonify({
        "error": e.message,
        "code": e.code
    }), 409


@app.errorhandler(Exception)
def handle_generic_error(e: Exception) -> Tuple[Dict, int]:
    app.logger.error(f"Internal error: {e}", exc_info=True)
    return jsonify({
        "error": "Internal server error"
    }), 500


# Validators
def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    return True


def validate_user_create(data: Dict) -> Dict:
    """Validate user creation data"""
    errors = {}
    
    # Validate name
    name = data.get('name')
    if not name:
        errors['name'] = 'Name is required'
    elif len(name) < 2:
        errors['name'] = 'Name must be at least 2 characters'
    elif len(name) > 50:
        errors['name'] = 'Name must be at most 50 characters'
    elif not name.replace(' ', '').isalpha():
        errors['name'] = 'Name must contain only letters and spaces'
    
    # Validate email
    email = data.get('email')
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Invalid email format'
    
    # Validate age
    age = data.get('age')
    if age is None:
        errors['age'] = 'Age is required'
    elif not isinstance(age, int):
        errors['age'] = 'Age must be an integer'
    elif age < 18:
        errors['age'] = 'Age must be at least 18'
    elif age > 120:
        errors['age'] = 'Age must be at most 120'
    
    # Validate password
    password = data.get('password')
    if not password:
        errors['password'] = 'Password is required'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters'
    elif not any(c.isalpha() for c in password):
        errors['password'] = 'Password must contain letters'
    elif not any(c.isdigit() for c in password):
        errors['password'] = 'Password must contain digits'
    
    return errors


# Mock database
existing_emails = ['existing@example.com', 'test@test.com']
users_db = []
next_user_id = 1


# Routes
@app.route('/users', methods=['POST'])
def create_user():
    """Create user endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate
        errors = validate_user_create(data)
        if errors:
            raise ValidationError(errors)
        
        # Check business rule
        if data['email'] in existing_emails:
            raise BusinessRuleError(
                message="Email already exists",
                code="EMAIL_EXISTS"
            )
        
        # Create user
        global next_user_id
        user = {
            "id": next_user_id,
            "name": data['name'],
            "email": data['email'],
            "age": data['age']
        }
        users_db.append(user)
        next_user_id += 1
        
        return jsonify(user), 201
        
    except ValidationError:
        raise
    except BusinessRuleError:
        raise


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Get user by ID"""
    user = next((u for u in users_db if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user)


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    """Update user endpoint"""
    user = next((u for u in users_db if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Partial validation
        errors = {}
        
        if 'name' in data:
            name = data['name']
            if len(name) < 2:
                errors['name'] = 'Name must be at least 2 characters'
            elif not name.replace(' ', '').isalpha():
                errors['name'] = 'Name must contain only letters and spaces'
        
        if 'email' in data:
            email = data['email']
            if not validate_email(email):
                errors['email'] = 'Invalid email format'
            elif email in existing_emails and email != user['email']:
                errors['email'] = 'Email already exists'
        
        if 'age' in data:
            age = data['age']
            if not isinstance(age, int):
                errors['age'] = 'Age must be an integer'
            elif age < 18 or age > 120:
                errors['age'] = 'Age must be between 18 and 120'
        
        if errors:
            raise ValidationError(errors)
        
        # Update user
        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            user['email'] = data['email']
        if 'age' in data:
            user['age'] = data['age']
        
        return jsonify(user)
        
    except ValidationError:
        raise


@app.route('/users', methods=['GET'])
def list_users():
    """List all users"""
    return jsonify({"users": users_db, "total": len(users_db)})


if __name__ == '__main__':
    print("=== Flask Validation Examples ===")
    print("Run the following commands to test:")
    print()
    print("# Create valid user:")
    print('curl -X POST http://localhost:5000/users \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "John Doe", "email": "john@example.com", "age": 30, "password": "password123"}\'')
    print()
    print("# Create invalid user:")
    print('curl -X POST http://localhost:5000/users \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "J", "email": "invalid", "age": 15, "password": "123"}\'')
    print()
    print("# Get user:")
    print('curl http://localhost:5000/users/1')
    print()
    print("# Update user:")
    print('curl -X PUT http://localhost:5000/users/1 \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "Jane Doe"}\'')
    print()
    print("# List users:")
    print('curl http://localhost:5000/users')
    print()
    
    app.run(debug=True, port=5000)
