"""
FastAPI Routing Example
URL patterns, path/query parameters, request body validation
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

app = FastAPI()


# Pydantic models for validation
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="User name")
    email: EmailStr
    age: int = Field(..., ge=18, le=120, description="User age")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=18, le=120)


class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True


# Mock database
users_db: List[User] = [
    User(id=1, name="John Doe", email="john@example.com", age=30),
    User(id=2, name="Jane Smith", email="jane@example.com", age=25),
]
next_id = 3


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "User Management API", "version": "1.0"}


@app.get("/users/", response_model=List[User])
def get_users(
    age_gt: Optional[int] = Query(None, ge=0, description="Filter by minimum age"),
    search: Optional[str] = Query(None, description="Search in name"),
    skip: int = Query(0, ge=0, description="Skip N users"),
    limit: int = Query(10, ge=1, le=100, description="Limit results")
):
    """GET /users/ - Get all users with filtering and pagination"""
    users = users_db.copy()
    
    # Filtering
    if age_gt is not None:
        users = [u for u in users if u.age > age_gt]
    
    if search:
        users = [u for u in users if search.lower() in u.name.lower()]
    
    # Pagination
    users = users[skip:skip + limit]
    
    return users


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """GET /users/{id} - Get specific user by ID"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """POST /users/ - Create new user with validation"""
    global next_id
    
    # Check for duplicate email
    if any(u.email == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = User(id=next_id, **user.model_dump())
    users_db.append(new_user)
    next_id += 1
    
    return new_user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate):
    """PUT /users/{id} - Update user (partial update)"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """DELETE /users/{id} - Delete user"""
    user_index = next((i for i, u in enumerate(users_db) if u.id == user_id), None)
    if user_index is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_user = users_db.pop(user_index)
    return {"message": "User deleted", "id": deleted_user.id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
