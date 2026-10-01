"""
Validation with Logging Examples
Занятие 4: Валидация, бизнес-правила и обработка ошибок
"""

import logging
from typing import Dict
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ValidationErrorLogger:
    """Logger for validation errors"""
    
    def __init__(self):
        self.logger = logger
    
    def log_validation_error(self, field: str, value: any, error: str):
        """Log validation error"""
        self.logger.warning(
            f"Validation failed for field '{field}': {error}. Value: {value}"
        )
    
    def log_business_rule_error(self, rule: str, details: str):
        """Log business rule violation"""
        self.logger.error(f"Business rule violation: {rule}. Details: {details}")
    
    def log_validation_success(self, data: Dict):
        """Log successful validation"""
        self.logger.info(f"Validation successful for data: {data}")
    
    def log_internal_error(self, error: Exception, context: str):
        """Log internal error"""
        self.logger.error(
            f"Internal error in {context}: {error}",
            exc_info=True
        )


def validate_user_with_logging(data: Dict, validator_logger: ValidationErrorLogger) -> Dict:
    """
    Validate user data with logging
    """
    errors = {}
    
    # Validate name
    name = data.get('name')
    if not name:
        errors['name'] = 'Name is required'
        validator_logger.log_validation_error('name', name, 'Name is required')
    elif len(name) < 2:
        errors['name'] = 'Name must be at least 2 characters'
        validator_logger.log_validation_error('name', name, 'Name too short')
    
    # Validate email
    email = data.get('email')
    if not email:
        errors['email'] = 'Email is required'
        validator_logger.log_validation_error('email', email, 'Email is required')
    elif '@' not in email:
        errors['email'] = 'Invalid email format'
        validator_logger.log_validation_error('email', email, 'Invalid format')
    
    # Validate age
    age = data.get('age')
    if age is None:
        errors['age'] = 'Age is required'
        validator_logger.log_validation_error('age', age, 'Age is required')
    elif age < 18:
        errors['age'] = 'Age must be at least 18'
        validator_logger.log_validation_error('age', age, 'Age restriction')
    
    if errors:
        return {
            "success": False,
            "errors": errors
        }
    
    validator_logger.log_validation_success(data)
    
    return {
        "success": True,
        "data": data
    }


def check_business_rule_with_logging(email: str, validator_logger: ValidationErrorLogger) -> bool:
    """
    Check business rule with logging
    """
    existing_emails = ['existing@example.com', 'test@test.com']
    
    if email in existing_emails:
        validator_logger.log_business_rule_error(
            rule="Email uniqueness",
            details=f"Email {email} already exists"
        )
        return False
    
    return True


def create_user_with_logging(data: Dict) -> Dict:
    """
    Create user with comprehensive logging
    """
    validator_logger = ValidationErrorLogger()
    
    try:
        validator_logger.logger.info(f"Starting user creation: {data.get('email')}")
        
        # Step 1: Validate format
        validation_result = validate_user_with_logging(data, validator_logger)
        
        if not validation_result['success']:
            return {
                "error": "Validation error",
                "details": validation_result['errors']
            }, 400
        
        # Step 2: Validate business rules
        if not check_business_rule_with_logging(data['email'], validator_logger):
            return {
                "error": "Email already exists",
                "code": "EMAIL_EXISTS"
            }, 409
        
        # Step 3: Create user (simulated)
        validator_logger.logger.info(f"User created successfully: {data['email']}")
        
        return {
            "id": 123,
            "name": data['name'],
            "email": data['email'],
            "created_at": datetime.now().isoformat()
        }, 201
        
    except Exception as e:
        validator_logger.log_internal_error(e, "user creation")
        return {
            "error": "Internal server error"
        }, 500


# Example usage
if __name__ == "__main__":
    print("=== Validation with Logging Examples ===\n")
    print("Check validation.log for detailed logs\n")
    
    # Valid user
    valid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }
    
    result, status = create_user_with_logging(valid_data)
    print(f"Valid user: {result}, Status: {status}")
    
    print()
    
    # Invalid user
    invalid_data = {
        "name": "J",
        "email": "invalid",
        "age": 15
    }
    
    result, status = create_user_with_logging(invalid_data)
    print(f"Invalid user: {result}, Status: {status}")
    
    print()
    
    # Duplicate email
    duplicate_data = {
        "name": "Jane Doe",
        "email": "existing@example.com",
        "age": 25
    }
    
    result, status = create_user_with_logging(duplicate_data)
    print(f"Duplicate email: {result}, Status: {status}")
