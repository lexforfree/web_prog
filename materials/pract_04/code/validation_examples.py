"""
Validation Examples
Занятие 4: Валидация, бизнес-правила и обработка ошибок
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


class ValidationError(Exception):
    """Validation error with details"""
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__(f"Validation error: {errors}")


class BusinessRuleError(Exception):
    """Business rule violation error"""
    def __init__(self, message: str, code: str = "BUSINESS_RULE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


@dataclass
class UserCreate:
    name: str
    email: str
    age: int
    password: str


def validate_email_format(email: str) -> bool:
    """Validate email format"""
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


def validate_user_create(data: Dict) -> UserCreate:
    """
    Validate user creation data
    
    Rules:
    - name: 2-50 characters, letters and spaces only
    - email: valid format
    - age: 18-120, integer
    - password: minimum 8 characters, letters and digits
    """
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
    elif not validate_email_format(email):
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
    
    if errors:
        raise ValidationError(errors)
    
    return UserCreate(
        name=name,
        email=email,
        age=age,
        password=password
    )


def check_email_unique(email: str) -> bool:
    """
    Check if email is unique (business rule)
    In real application, this would check database
    """
    existing_emails = [
        'existing@example.com',
        'test@test.com'
    ]
    return email not in existing_emails


def create_user(data: Dict) -> Dict:
    """
    Create user with validation and business rules
    """
    try:
        # Step 1: Validate format
        user_data = validate_user_create(data)
        
        # Step 2: Validate business rules
        if not check_email_unique(user_data.email):
            raise BusinessRuleError(
                message="Email already exists",
                code="EMAIL_EXISTS"
            )
        
        # Step 3: Create user (database operation)
        # user = User.create(**user_data.__dict__)
        
        return {
            "id": 123,
            "name": user_data.name,
            "email": user_data.email,
            "age": user_data.age,
            "created_at": "2024-01-01T00:00:00Z"
        }, 201
        
    except ValidationError as e:
        return {
            "error": "Validation error",
            "details": e.errors
        }, 400
        
    except BusinessRuleError as e:
        return {
            "error": e.message,
            "code": e.code
        }, 409
        
    except Exception as e:
        # Log error here
        print(f"ERROR: {e}")
        return {
            "error": "Internal server error"
        }, 500


# Example usage
if __name__ == "__main__":
    # Valid data
    valid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "password": "password123"
    }
    print("Valid data:", create_user(valid_data))
    
    # Invalid data
    invalid_data = {
        "name": "J",
        "email": "invalid-email",
        "age": 15,
        "password": "123"
    }
    print("Invalid data:", create_user(invalid_data))
    
    # Duplicate email
    duplicate_data = {
        "name": "John Doe",
        "email": "existing@example.com",
        "age": 30,
        "password": "password123"
    }
    print("Duplicate email:", create_user(duplicate_data))
