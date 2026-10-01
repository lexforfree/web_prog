"""
FastAPI Validation Examples
Занятие 4: Валидация, бизнес-правила и обработка ошибок

Для запуска требуется: pip install fastapi uvicorn pydantic email-validator
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from enum import Enum


app = FastAPI(title="User API", version="1.0.0")


# Enums
class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    EMAIL_EXISTS = "EMAIL_EXISTS"
    USERNAME_TAKEN = "USERNAME_TAKEN"
    AGE_RESTRICTION = "AGE_RESTRICTION"


# Models
class UserCreate(BaseModel):
    """User creation model with validation"""
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
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    code: Optional[str] = None
    details: Optional[dict] = None


# Mock database
class UserDB:
    def __init__(self):
        self.users: List[dict] = []
        self.next_id = 1
        self.existing_emails = ['existing@example.com', 'test@test.com']
    
    def create(self, user_data: UserCreate) -> dict:
        """Create user"""
        if user_data.email in self.existing_emails:
            raise ValueError("Email already exists")
        
        user = {
            "id": self.next_id,
            "name": user_data.name,
            "email": user_data.email,
            "age": user_data.age
        }
        self.users.append(user)
        self.existing_emails.append(user_data.email)
        self.next_id += 1
        return user
    
    def get_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        return next((u for u in self.users if u['id'] == user_id), None)
    
    def update(self, user_id: int, update_data: UserUpdate) -> Optional[dict]:
        """Update user"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        if update_data.name is not None:
            user['name'] = update_data.name
        if update_data.email is not None:
            if update_data.email in self.existing_emails and update_data.email != user['email']:
                raise ValueError("Email already exists")
            self.existing_emails.remove(user['email'])
            user['email'] = update_data.email
            self.existing_emails.append(update_data.email)
        if update_data.age is not None:
            user['age'] = update_data.age
        
        return user
    
    def list_all(self) -> List[dict]:
        """List all users"""
        return self.users


db = UserDB()


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Handle ValueError (business rules)"""
    if "Email already exists" in str(exc):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Email already exists",
                "code": ErrorCode.EMAIL_EXISTS.value
            }
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": str(exc)}
    )


# Routes
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create user endpoint"""
    try:
        user = db.create(user_data)
        return user
    except ValueError as e:
        raise  # Handled by exception handler


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    user = db.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"}
        )
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, update_data: UserUpdate):
    """Update user endpoint"""
    try:
        user = db.update(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "User not found"}
            )
        return user
    except ValueError as e:
        raise  # Handled by exception handler


@app.get("/users", response_model=List[UserResponse])
async def list_users():
    """List all users"""
    return db.list_all()


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete user endpoint"""
    user = db.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"}
        )
    db.users = [u for u in db.users if u['id'] != user_id]
    return None


if __name__ == '__main__':
    import uvicorn
    
    print("=== FastAPI Validation Examples ===")
    print("Run the following commands to test:")
    print()
    print("# Start server:")
    print("uvicorn fastapi_validation:app --reload")
    print()
    print("# Create valid user:")
    print('curl -X POST http://localhost:8000/users \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "John Doe", "email": "john@example.com", "age": 30, "password": "password123"}\'')
    print()
    print("# Create invalid user (Pydantic will handle validation):")
    print('curl -X POST http://localhost:8000/users \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "J", "email": "invalid", "age": 15, "password": "123"}\'')
    print()
    print("# Get user:")
    print('curl http://localhost:8000/users/1')
    print()
    print("# Update user:")
    print('curl -X PUT http://localhost:8000/users/1 \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"name": "Jane Doe"}\'')
    print()
    print("# List users:")
    print('curl http://localhost:8000/users')
    print()
    print("# Delete user:")
    print('curl -X DELETE http://localhost:8000/users/1')
    print()
    print("# Open API docs:")
    print("http://localhost:8000/docs")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
