"""
Pydantic Validation Examples
Занятие 4: Валидация, бизнес-правила и обработка ошибок

Для запуска требуется: pip install pydantic email-validator
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User creation model with Pydantic validation"""
    name: str = Field(..., min_length=2, max_length=50, description="User name")
    email: EmailStr = Field(..., description="User email")
    age: int = Field(..., ge=18, le=120, description="User age")
    password: str = Field(..., min_length=8, description="User password")
    
    @field_validator('name')
    @classmethod
    def name_must_contain_letters(cls, v: str) -> str:
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain letters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digits')
        return v


class UserUpdate(BaseModel):
    """User update model - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=18, le=120)
    
    @field_validator('name')
    @classmethod
    def name_must_contain_letters(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        return v


class UserResponse(BaseModel):
    """User response model"""
    id: int
    name: str
    email: str
    age: int
    created_at: datetime


# Example usage
if __name__ == "__main__":
    print("=== Pydantic Validation Examples ===\n")
    
    # Valid user creation
    try:
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            age=30,
            password="password123"
        )
        print(f"✓ Valid user: {user}")
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    
    print()
    
    # Invalid email
    try:
        user = UserCreate(
            name="John Doe",
            email="invalid-email",
            age=30,
            password="password123"
        )
        print(f"✓ Valid user: {user}")
    except ValidationError as e:
        print(f"✗ Invalid email: {e.errors()}")
    
    print()
    
    # Invalid age
    try:
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            age=15,
            password="password123"
        )
        print(f"✓ Valid user: {user}")
    except ValidationError as e:
        print(f"✗ Invalid age: {e.errors()}")
    
    print()
    
    # Weak password
    try:
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            age=30,
            password="123"
        )
        print(f"✓ Valid user: {user}")
    except ValidationError as e:
        print(f"✗ Weak password: {e.errors()}")
    
    print()
    
    # Partial update (valid)
    try:
        update = UserUpdate(name="Jane Doe")
        print(f"✓ Valid update: {update}")
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    
    print()
    
    # Partial update (invalid)
    try:
        update = UserUpdate(name="J")
        print(f"✓ Valid update: {update}")
    except ValidationError as e:
        print(f"✗ Invalid update: {e.errors()}")
