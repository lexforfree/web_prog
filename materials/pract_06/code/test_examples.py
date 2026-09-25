"""
Test Examples
Занятие 6: Основы автоматического тестирования
"""

import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass


# System under test
@dataclass
class User:
    id: int = None
    name: str = ""
    email: str = ""


class UserRepository:
    def email_exists(self, email: str) -> bool:
        pass
    
    def save(self, user: User) -> User:
        pass
    
    def find_by_id(self, user_id: int) -> User:
        pass


class EmailService:
    def send_welcome(self, email: str):
        pass


class UserService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service
    
    def create_user(self, name: str, email: str) -> User:
        if len(name) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        if self.user_repo.email_exists(email):
            raise ValueError("Email already exists")
        
        user = User(name=name, email=email)
        user = self.user_repo.save(user)
        
        self.email_service.send_welcome(email)
        
        return user
    
    def get_user(self, user_id: int) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user


# Unit Tests
class TestUserService:
    """Unit tests for UserService"""
    
    def test_create_user_success(self):
        """Test successful user creation - happy path"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_repo.email_exists.return_value = False
        mock_repo.save.return_value = User(id=1, name="John", email="john@example.com")
        mock_email = Mock(spec=EmailService)
        service = UserService(mock_repo, mock_email)
        
        # Act
        user = service.create_user("John", "john@example.com")
        
        # Assert
        assert user.id == 1
        assert user.name == "John"
        assert user.email == "john@example.com"
        mock_repo.email_exists.assert_called_once_with("john@example.com")
        mock_repo.save.assert_called_once()
        mock_email.send_welcome.assert_called_once_with("john@example.com")
    
    def test_create_user_duplicate_email(self):
        """Test error when email already exists"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_repo.email_exists.return_value = True
        mock_email = Mock(spec=EmailService)
        service = UserService(mock_repo, mock_email)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user("John", "john@example.com")
        
        mock_repo.email_exists.assert_called_once_with("john@example.com")
        mock_repo.save.assert_not_called()
        mock_email.send_welcome.assert_not_called()
    
    def test_create_user_name_too_short(self):
        """Test error when name is too short"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_email = Mock(spec=EmailService)
        service = UserService(mock_repo, mock_email)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Name must be at least 2 characters"):
            service.create_user("J", "john@example.com")
        
        mock_repo.email_exists.assert_not_called()
    
    def test_create_user_min_name_length(self):
        """Test edge case: minimum name length"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_repo.email_exists.return_value = False
        mock_repo.save.return_value = User(id=1, name="Jo", email="john@example.com")
        mock_email = Mock(spec=EmailService)
        service = UserService(mock_repo, mock_email)
        
        # Act
        user = service.create_user("Jo", "john@example.com")
        
        # Assert
        assert user.name == "Jo"
    
    def test_get_user_success(self):
        """Test successful user retrieval"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_id.return_value = User(id=1, name="John", email="john@example.com")
        service = UserService(mock_repo, Mock())
        
        # Act
        user = service.get_user(1)
        
        # Assert
        assert user.id == 1
        assert user.name == "John"
        mock_repo.find_by_id.assert_called_once_with(1)
    
    def test_get_user_not_found(self):
        """Test error when user not found"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_id.return_value = None
        service = UserService(mock_repo, Mock())
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            service.get_user(999)
        
        mock_repo.find_by_id.assert_called_once_with(999)


# Email Validation Tests
def validate_email(email: str) -> bool:
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


class TestEmailValidation:
    """Unit tests for email validation"""
    
    def test_valid_email(self):
        """Test valid email"""
        assert validate_email("john@example.com") is True
    
    def test_email_without_at(self):
        """Test email without @ symbol"""
        assert validate_email("johnexample.com") is False
    
    def test_email_multiple_at(self):
        """Test email with multiple @ symbols"""
        assert validate_email("john@@example.com") is False
    
    def test_email_empty_local(self):
        """Test email with empty local part"""
        assert validate_email("@example.com") is False
    
    def test_email_empty_domain(self):
        """Test email with empty domain"""
        assert validate_email("john@") is False
    
    def test_email_domain_without_dot(self):
        """Test email domain without dot"""
        assert validate_email("john@example") is False


# Integration Test Example
class TestUserServiceIntegration:
    """Integration tests for UserService with real repository"""
    
    @pytest.fixture
    def test_db(self):
        """Setup test database"""
        # In real implementation, setup test DB
        db = Mock()
        db.users = {}
        db.next_id = 1
        yield db
        # Cleanup
        db.users.clear()
    
    @pytest.fixture
    def user_repo(self, test_db):
        """Create repository with test DB"""
        repo = UserRepository()
        repo.db = test_db
        repo.email_exists = lambda email: any(u['email'] == email for u in test_db.users.values())
        repo.save = lambda user: self._save_user(test_db, user)
        repo.find_by_id = lambda user_id: self._find_user(test_db, user_id)
        return repo
    
    def _save_user(self, db, user):
        user.id = db.next_id
        db.users[db.next_id] = user.__dict__
        db.next_id += 1
        return user
    
    def _find_user(self, db, user_id):
        data = db.users.get(user_id)
        return User(**data) if data else None
    
    def test_create_user_integration(self, user_repo):
        """Integration test: create user with real repository"""
        # Arrange
        mock_email = Mock(spec=EmailService)
        service = UserService(user_repo, mock_email)
        
        # Act
        user = service.create_user("John", "john@example.com")
        
        # Assert
        assert user.id is not None
        assert user.name == "John"
        
        # Verify in repository
        saved_user = user_repo.find_by_id(user.id)
        assert saved_user is not None
        assert saved_user.email == "john@example.com"
    
    def test_create_user_duplicate_integration(self, user_repo):
        """Integration test: duplicate email"""
        # Arrange
        mock_email = Mock(spec=EmailService)
        service = UserService(user_repo, mock_email)
        
        # Create first user
        service.create_user("John", "john@example.com")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user("Jane", "john@example.com")


# Regression Test Example
class TestRegression:
    """Regression tests for bug fixes"""
    
    def test_discount_calculation_bug_fix(self):
        """
        Regression test for discount calculation bug
        Bug: function returned discount amount instead of final price
        """
        # Original buggy code
        def calculate_discount_buggy(price: float, discount_percent: float) -> float:
            return price * discount_percent / 100  # Bug: returns discount amount
        
        # Fixed code
        def calculate_discount_fixed(price: float, discount_percent: float) -> float:
            return price - (price * discount_percent / 100)
        
        # Test that would catch the bug
        assert calculate_discount_fixed(100, 10) == 90  # 100 - 10% = 90
        
        # Buggy version would return 10, not 90
        assert calculate_discount_buggy(100, 10) != 90  # This fails, catching the bug


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
