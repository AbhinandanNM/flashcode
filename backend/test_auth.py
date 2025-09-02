import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from auth import AuthService
import os

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

class TestAuthService:
    """Test the AuthService class"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Verification should work
        assert AuthService.verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert AuthService.verify_password("wrongpassword", hashed) is False
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        data = {"sub": "testuser"}
        token = AuthService.create_access_token(data)
        
        # Token should be created
        assert token is not None
        assert isinstance(token, str)
        
        # Token should be verifiable
        payload = AuthService.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        
        # Invalid token should return None
        invalid_payload = AuthService.verify_token("invalid.token.here")
        assert invalid_payload is None
    
    def test_refresh_token_creation(self):
        """Test refresh token creation"""
        data = {"sub": "testuser"}
        refresh_token = AuthService.create_refresh_token(data)
        
        # Token should be created
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        
        # Token should be verifiable and have refresh type
        payload = AuthService.verify_token(refresh_token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"

class TestAuthRoutes:
    """Test authentication API routes"""
    
    def test_user_registration_success(self, client, test_db):
        """Test successful user registration"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["xp"] == 0
        assert data["streak"] == 0
        assert data["is_active"] is True
        assert "password" not in data
    
    def test_user_registration_duplicate_username(self, client, test_db):
        """Test registration with duplicate username"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration with same username should fail
        user_data2 = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123"
        }
        response2 = client.post("/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "Username already registered" in response2.json()["detail"]
    
    def test_user_registration_duplicate_email(self, client, test_db):
        """Test registration with duplicate email"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        user_data2 = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "password123"
        }
        response2 = client.post("/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
    
    def test_user_registration_invalid_data(self, client, test_db):
        """Test registration with invalid data"""
        # Short password
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Short username
        user_data = {
            "username": "ab",
            "email": "test@example.com",
            "password": "password123"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Invalid email
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_user_login_success(self, client, test_db):
        """Test successful user login"""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        client.post("/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_user_login_invalid_credentials(self, client, test_db):
        """Test login with invalid credentials"""
        # Register a user first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        client.post("/auth/register", json=user_data)
        
        # Try login with wrong password
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
        
        # Try login with non-existent user
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_get_user_profile_authenticated(self, client, test_db):
        """Test getting user profile with valid token"""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/profile", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_get_user_profile_unauthenticated(self, client, test_db):
        """Test getting user profile without token"""
        response = client.get("/auth/profile")
        assert response.status_code == 403  # No Authorization header
    
    def test_get_user_profile_invalid_token(self, client, test_db):
        """Test getting user profile with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/auth/profile", headers=headers)
        assert response.status_code == 401
    
    def test_refresh_token_success(self, client, test_db):
        """Test successful token refresh"""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        login_response = client.post("/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client, test_db):
        """Test token refresh with invalid refresh token"""
        refresh_data = {"refresh_token": "invalid.refresh.token"}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

if __name__ == "__main__":
    # Clean up test database if it exists
    if os.path.exists("./test_auth.db"):
        os.remove("./test_auth.db")