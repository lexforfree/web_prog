"""
SQLAlchemy ORM Example with Docker
Занятие 8: Работа с базой данных

Для запуска требуется: pip install sqlalchemy python-dotenv

Запуск с Docker:
1. docker-compose up -d
2. python code/sqlalchemy_orm.py
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

# Database URL - подключение к Docker контейнеру
DATABASE_URL = f"postgresql://{os.getenv('DB_USER', 'webprog')}:{os.getenv('DB_PASSWORD', 'webprog123')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME', 'webprog')}"

# Create engine with connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=True  # Log SQL queries
)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    age = Column(Integer, CheckConstraint('age >= 18'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with orders
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class Order(Base):
    """Order model"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product = Column(String(100), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, product='{self.product}', total={self.total})>"


# Create tables
def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("Tables created")


def get_session():
    """Get database session"""
    return SessionLocal()


# CRUD Operations
def create_user(name: str, email: str, age: int) -> User:
    """Create new user"""
    session = get_session()
    try:
        user = User(name=name, email=email, age=age)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_user(user_id: int) -> User:
    """Get user by ID"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user
    finally:
        session.close()


def get_all_users() -> list:
    """Get all users"""
    session = get_session()
    try:
        users = session.query(User).order_by(User.id).all()
        return users
    finally:
        session.close()


def update_user(user_id: int, **kwargs) -> User:
    """Update user"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_user(user_id: int) -> bool:
    """Delete user"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        session.delete(user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def create_order(user_id: int, product: str, total: float) -> Order:
    """Create order for user"""
    session = get_session()
    try:
        order = Order(user_id=user_id, product=product, total=total)
        session.add(order)
        session.commit()
        session.refresh(order)
        return order
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_user_orders(user_id: int) -> list:
    """Get all orders for user using relationship"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user.orders
    finally:
        session.close()


def get_users_with_order_count() -> list:
    """Get users with order count using JOIN"""
    session = get_session()
    try:
        from sqlalchemy import func
        
        result = session.query(
            User.id,
            User.name,
            User.email,
            func.count(Order.id).label('order_count')
        ).outerjoin(Order).group_by(User.id).order_by(func.count(Order.id).desc()).all()
        
        return [
            {
                'id': row.id,
                'name': row.name,
                'email': row.email,
                'order_count': row.order_count
            }
            for row in result
        ]
    finally:
        session.close()


def search_user_by_email(email: str) -> User:
    """Search user by email"""
    session = get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found")
        return user
    finally:
        session.close()


def filter_users(min_age: int = None, max_age: int = None) -> list:
    """Filter users by age range"""
    session = get_session()
    try:
        query = session.query(User)
        
        if min_age is not None:
            query = query.filter(User.age >= min_age)
        
        if max_age is not None:
            query = query.filter(User.age <= max_age)
        
        return query.all()
    finally:
        session.close()


# Example usage
if __name__ == "__main__":
    print("=== SQLAlchemy ORM Example ===\n")
    
    try:
        # Initialize database
        init_db()
        
        # Create users
        user1 = create_user("John Doe", "john@example.com", 30)
        user2 = create_user("Jane Smith", "jane@example.com", 25)
        user3 = create_user("Bob Johnson", "bob@example.com", 35)
        
        print(f"Created users: {user1}, {user2}, {user3}")
        
        # Get user
        user = get_user(user1.id)
        print(f"Got user: {user}")
        
        # Get all users
        users = get_all_users()
        print(f"All users: {users}")
        
        # Update user
        updated = update_user(user1.id, age=31)
        print(f"Updated user: {updated}")
        
        # Create orders
        order1 = create_order(user1.id, "Laptop", 999.99)
        order2 = create_order(user1.id, "Mouse", 29.99)
        order3 = create_order(user2.id, "Keyboard", 79.99)
        order4 = create_order(user1.id, "Monitor", 299.99)
        
        print(f"Created orders: {order1}, {order2}, {order3}, {order4}")
        
        # Get user orders (using relationship)
        orders = get_user_orders(user1.id)
        print(f"User {user1.name} orders: {orders}")
        
        # Get users with order count
        users_with_orders = get_users_with_order_count()
        print(f"Users with order count: {users_with_orders}")
        
        # Search by email
        found = search_user_by_email("john@example.com")
        print(f"Found user: {found}")
        
        # Filter users
        filtered = filter_users(min_age=25, max_age=30)
        print(f"Users aged 25-30: {filtered}")
        
        # Delete user (cascade delete orders)
        delete_user(user3.id)
        print(f"Deleted user {user3.name} (and their orders)")
        
    except Exception as e:
        print(f"Error: {e}")
