"""
Custom Validators Examples
Занятие 4: Валидация, бизнес-правила и обработка ошибок
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ErrorCode(Enum):
    """Error codes for different validation types"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    EMAIL_EXISTS = "EMAIL_EXISTS"
    USERNAME_TAKEN = "USERNAME_TAKEN"
    AGE_RESTRICTION = "AGE_RESTRICTION"
    PASSWORD_WEAK = "PASSWORD_WEAK"


class CustomError(Exception):
    """Custom error with code and details"""
    def __init__(self, message: str, code: str, details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """Convert error to dictionary for API response"""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


class Validator:
    """Base validator class"""
    
    def validate(self, value) -> bool:
        """Validate value"""
        raise NotImplementedError
    
    def get_error_message(self) -> str:
        """Get error message"""
        raise NotImplementedError


class EmailValidator(Validator):
    """Email format validator"""
    
    def validate(self, email: str) -> bool:
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
    
    def get_error_message(self) -> str:
        return "Invalid email format"


class PasswordValidator(Validator):
    """Password strength validator"""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = False):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
    
    def validate(self, password: str) -> bool:
        if len(password) < self.min_length:
            return False
        if not any(c.isalpha() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        if self.require_uppercase and not any(c.isupper() for c in password):
            return False
        return True
    
    def get_error_message(self) -> str:
        msg = f"Password must be at least {self.min_length} characters"
        msg += ", contain letters and digits"
        if self.require_uppercase:
            msg += ", and uppercase letters"
        return msg


class AgeValidator(Validator):
    """Age range validator"""
    
    def __init__(self, min_age: int = 18, max_age: int = 120):
        self.min_age = min_age
        self.max_age = max_age
    
    def validate(self, age: int) -> bool:
        return self.min_age <= age <= self.max_age
    
    def get_error_message(self) -> str:
        return f"Age must be between {self.min_age} and {self.max_age}"


class ValidationContext:
    """Context for managing multiple validators"""
    
    def __init__(self):
        self.validators: Dict[str, List[Validator]] = {}
        self.errors: Dict[str, List[str]] = {}
    
    def add_validator(self, field: str, validator: Validator):
        """Add validator for a field"""
        if field not in self.validators:
            self.validators[field] = []
        self.validators[field].append(validator)
    
    def validate(self, data: Dict) -> bool:
        """Validate all fields"""
        self.errors = {}
        
        for field, validators in self.validators.items():
            value = data.get(field)
            field_errors = []
            
            for validator in validators:
                if not validator.validate(value):
                    field_errors.append(validator.get_error_message())
            
            if field_errors:
                self.errors[field] = field_errors
        
        return len(self.errors) == 0
    
    def get_errors(self) -> Dict[str, List[str]]:
        """Get all validation errors"""
        return self.errors


# Example usage
if __name__ == "__main__":
    print("=== Custom Validators Examples ===\n")
    
    # Create validation context
    context = ValidationContext()
    
    # Add validators
    context.add_validator('email', EmailValidator())
    context.add_validator('password', PasswordValidator(min_length=8))
    context.add_validator('age', AgeValidator(min_age=18, max_age=120))
    
    # Valid data
    valid_data = {
        "email": "john@example.com",
        "password": "password123",
        "age": 30
    }
    
    if context.validate(valid_data):
        print("✓ Valid data")
    else:
        print(f"✗ Invalid data: {context.get_errors()}")
    
    print()
    
    # Invalid data
    invalid_data = {
        "email": "invalid",
        "password": "123",
        "age": 15
    }
    
    if context.validate(invalid_data):
        print("✓ Valid data")
    else:
        print(f"✗ Invalid data: {context.get_errors()}")
    
    print()
    
    # Custom error example
    try:
        raise CustomError(
            message="Email already exists",
            code=ErrorCode.EMAIL_EXISTS.value,
            details={"email": "existing@example.com"}
        )
    except CustomError as e:
        print(f"Custom error: {e.to_dict()}")
