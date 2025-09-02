import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from models import Base, get_db
from auth import get_current_user
from schemas import UserResponse

# Test database URL - using SQLite in memory for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test user data
TEST_USER = {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
    "is_active": True,
    "total_xp": 1250,
    "level": 5,
    "streak": 7,
    "created_at": "2024-01-01T00:00:00Z"
}

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    """Override auth dependency for testing"""
    return UserResponse(**TEST_USER)

# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    """Create an authenticated test client"""
    # The override_get_current_user already provides authentication
    return client

@pytest.fixture
def sample_lesson_data():
    """Sample lesson data for testing"""
    return {
        "title": "Python Basics",
        "description": "Learn the fundamentals of Python programming",
        "language": "python",
        "difficulty": 1,
        "xp_reward": 100,
        "estimated_time": 30,
        "content": {
            "theory": "Python is a programming language...",
            "examples": ["print('Hello, World!')", "x = 5"],
            "exercises": []
        }
    }

@pytest.fixture
def sample_question_data():
    """Sample question data for testing"""
    return {
        "lesson_id": 1,
        "type": "mcq",
        "difficulty": 1,
        "question": "What is the correct way to declare a variable in Python?",
        "options": ["var x = 5", "x = 5", "int x = 5", "declare x = 5"],
        "correct_answer": "x = 5",
        "explanation": "In Python, variables are declared by simply assigning a value.",
        "xp_reward": 10
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }

@pytest.fixture
def sample_code_data():
    """Sample code execution data for testing"""
    return {
        "code": "print('Hello, World!')",
        "language": "python"
    }

@pytest.fixture
def sample_duel_data():
    """Sample duel data for testing"""
    return {
        "challenger_id": 1,
        "opponent_id": 2,
        "question_id": 1,
        "time_limit": 300
    }

# Mock external services
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mock external services for testing"""
    
    def mock_execute_code(code: str, language: str):
        return {
            "output": "Hello, World!\n",
            "execution_time": 0.05,
            "memory_used": 1024,
            "error": None
        }
    
    def mock_validate_code(code: str, test_cases: list):
        return {
            "is_correct": True,
            "total_tests": len(test_cases),
            "passed_tests": len(test_cases),
            "test_results": [
                {
                    "input": tc.get("input", ""),
                    "expected_output": tc.get("expected_output", ""),
                    "actual_output": tc.get("expected_output", ""),
                    "passed": True
                }
                for tc in test_cases
            ],
            "execution_time": 0.12
        }
    
    # Apply mocks
    monkeypatch.setattr("services.code_execution_service.execute_code", mock_execute_code)
    monkeypatch.setattr("services.code_validation_service.validate_code", mock_validate_code)

# Database fixtures with sample data
@pytest.fixture
def db_with_lessons(db_session, sample_lesson_data):
    """Database session with sample lessons"""
    from models import Lesson
    
    lesson = Lesson(**sample_lesson_data)
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    
    return db_session

@pytest.fixture
def db_with_questions(db_session, sample_question_data):
    """Database session with sample questions"""
    from models import Question
    
    question = Question(**sample_question_data)
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    
    return db_session

@pytest.fixture
def db_with_users(db_session):
    """Database session with sample users"""
    from models import User
    
    user = User(**TEST_USER)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return db_session