"""
Backend Architecture Example
Занятие 5: Устройство backend-приложения
"""

from dataclasses import dataclass
from typing import Optional
import os


# Configuration
class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'mydb')
    SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))


# Models
@dataclass
class User:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email')
        )


# Repository Layer
class UserRepository:
    """Data access layer - no business logic"""
    
    def __init__(self, db):
        self.db = db
    
    def save(self, user: User) -> User:
        """Save user to database"""
        if user.id:
            # Update
            self.db.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                user.name, user.email, user.id
            )
        else:
            # Insert
            user.id = self.db.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                user.name, user.email
            )
        return user
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        data = self.db.query_one(
            "SELECT * FROM users WHERE id = ?",
            user_id
        )
        return User.from_dict(data) if data else None
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        data = self.db.query_one(
            "SELECT * FROM users WHERE email = ?",
            email
        )
        return User.from_dict(data) if data else None
    
    def email_exists(self, email: str) -> bool:
        """Check if email exists"""
        count = self.db.query_one(
            "SELECT COUNT(*) as count FROM users WHERE email = ?",
            email
        )
        return count['count'] > 0


# Service Layer
class UserService:
    """Business logic layer - no HTTP, no SQL"""
    
    def __init__(self, user_repo, email_service):
        self.user_repo = user_repo
        self.email_service = email_service
    
    def create_user(self, name: str, email: str) -> User:
        """Create user with business rules"""
        # Business rule: email must be unique
        if self.user_repo.email_exists(email):
            raise ValueError("Email already exists")
        
        # Business rule: name must be at least 2 characters
        if len(name) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        # Create user
        user = User(name=name, email=email)
        user = self.user_repo.save(user)
        
        # Send welcome email (side effect)
        self.email_service.send_welcome(email)
        
        return user
    
    def get_user(self, user_id: int) -> User:
        """Get user by ID"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user
    
    def update_user(self, user_id: int, name: str, email: str) -> User:
        """Update user"""
        user = self.get_user(user_id)
        
        # Business rule: email must be unique (if changed)
        if email != user.email and self.user_repo.email_exists(email):
            raise ValueError("Email already exists")
        
        user.name = name
        user.email = email
        user = self.user_repo.save(user)
        
        return user


# Handler Layer
class UserHandler:
    """HTTP handler - HTTP-specific logic only"""
    
    def __init__(self, user_service):
        self.user_service = user_service
    
    def create_user(self, request):
        """Handle POST /users"""
        try:
            # Extract data from HTTP request
            data = request.json
            name = data.get('name')
            email = data.get('email')
            
            # Validate format (not business rules)
            if not name:
                return {"error": "Name is required"}, 400
            if not email:
                return {"error": "Email is required"}, 400
            if '@' not in email:
                return {"error": "Invalid email format"}, 400
            
            # Call business logic
            user = self.user_service.create_user(name, email)
            
            # Format HTTP response
            return user.to_dict(), 201
            
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "Internal error"}, 500
    
    def get_user(self, request, user_id):
        """Handle GET /users/{id}"""
        try:
            user = self.user_service.get_user(user_id)
            return user.to_dict(), 200
        except ValueError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": "Internal error"}, 500


# Email Service (side effect)
class EmailService:
    """Email sending service"""
    
    def __init__(self, smtp_host, smtp_port):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
    
    def send_welcome(self, email: str):
        """Send welcome email"""
        # In real implementation, this would send actual email
        print(f"Sending welcome email to {email} via {self.smtp_host}:{self.smtp_port}")


# Dependency Injection Container
class Container:
    """DI Container - manages dependencies"""
    
    def __init__(self, config: Config):
        self.config = config
        self._db = None
        self._user_repo = None
        self._email_service = None
        self._user_service = None
        self._user_handler = None
    
    @property
    def db(self):
        """Database connection"""
        if self._db is None:
            self._db = Database(self.config.DB_HOST, self.config.DB_PORT)
        return self._db
    
    @property
    def user_repo(self):
        """User repository"""
        if self._user_repo is None:
            self._user_repo = UserRepository(self.db)
        return self._user_repo
    
    @property
    def email_service(self):
        """Email service"""
        if self._email_service is None:
            self._email_service = EmailService(
                self.config.SMTP_HOST,
                self.config.SMTP_PORT
            )
        return self._email_service
    
    @property
    def user_service(self):
        """User service"""
        if self._user_service is None:
            self._user_service = UserService(
                self.user_repo,
                self.email_service
            )
        return self._user_service
    
    @property
    def user_handler(self):
        """User handler"""
        if self._user_handler is None:
            self._user_handler = UserHandler(self.user_service)
        return self._user_handler


# Mock Database (for example)
class Database:
    """Mock database"""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._users = {}
        self._next_id = 1
    
    def execute(self, query, *args):
        """Execute SQL query"""
        print(f"Executing: {query} with args {args}")
        # Mock implementation
        return self._next_id
    
    def query_one(self, query, *args):
        """Query single row"""
        print(f"Querying: {query} with args {args}")
        # Mock implementation
        return None
    
    def query(self, query, *args):
        """Query multiple rows"""
        print(f"Querying: {query} with args {args}")
        # Mock implementation
        return []


# Example usage
if __name__ == "__main__":
    # Create container with config
    config = Config()
    container = Container(config)
    
    # Get handler (all dependencies injected)
    handler = container.user_handler
    
    # Mock request
    class Request:
        json = {"name": "John Doe", "email": "john@example.com"}
    
    # Handle request
    response, status = handler.create_user(Request())
    print(f"Response: {response}, Status: {status}")
