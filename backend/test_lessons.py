import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, Lesson, Progress, LanguageEnum, ProgressStatusEnum
from auth import AuthService
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_lessons.db"
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
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = AuthService.create_user(
        db=db_session,
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_lesson(db_session):
    """Create a sample lesson"""
    lesson = Lesson(
        language=LanguageEnum.PYTHON,
        title="Python Basics",
        theory="Introduction to Python programming",
        difficulty=1,
        xp_reward=100,
        order_index=1,
        is_published=True
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    return lesson

class TestLessonCRUD:
    
    def test_create_lesson(self, client, auth_headers):
        """Test creating a new lesson"""
        lesson_data = {
            "language": "python",
            "title": "Python Variables",
            "theory": "Learn about Python variables and data types",
            "difficulty": 2,
            "xp_reward": 150,
            "order_index": 2,
            "is_published": True
        }
        
        response = client.post("/lessons/", json=lesson_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == lesson_data["title"]
        assert data["language"] == lesson_data["language"]
        assert data["difficulty"] == lesson_data["difficulty"]
        assert data["xp_reward"] == lesson_data["xp_reward"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_lessons(self, client, auth_headers, sample_lesson):
        """Test retrieving lessons"""
        response = client.get("/lessons/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        lesson = data[0]
        assert lesson["id"] == sample_lesson.id
        assert lesson["title"] == sample_lesson.title
        assert lesson["language"] == sample_lesson.language.value
        assert "progress" in lesson
    
    def test_get_lesson_by_id(self, client, auth_headers, sample_lesson):
        """Test retrieving a specific lesson"""
        response = client.get(f"/lessons/{sample_lesson.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_lesson.id
        assert data["title"] == sample_lesson.title
        assert data["theory"] == sample_lesson.theory
    
    def test_get_nonexistent_lesson(self, client, auth_headers):
        """Test retrieving a non-existent lesson"""
        response = client.get("/lessons/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_lesson(self, client, auth_headers, sample_lesson):
        """Test updating a lesson"""
        update_data = {
            "title": "Updated Python Basics",
            "difficulty": 3
        }
        
        response = client.put(f"/lessons/{sample_lesson.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["difficulty"] == update_data["difficulty"]
        assert data["language"] == sample_lesson.language.value  # Should remain unchanged
    
    def test_delete_lesson(self, client, auth_headers, sample_lesson):
        """Test deleting a lesson"""
        response = client.delete(f"/lessons/{sample_lesson.id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify lesson is deleted
        response = client.get(f"/lessons/{sample_lesson.id}", headers=auth_headers)
        assert response.status_code == 404

class TestLessonFiltering:
    
    def test_filter_by_language(self, client, auth_headers, db_session):
        """Test filtering lessons by language"""
        # Create lessons with different languages
        python_lesson = Lesson(
            language=LanguageEnum.PYTHON,
            title="Python Lesson",
            theory="Python content",
            difficulty=1,
            xp_reward=100,
            order_index=1,
            is_published=True
        )
        cpp_lesson = Lesson(
            language=LanguageEnum.CPP,
            title="C++ Lesson",
            theory="C++ content",
            difficulty=1,
            xp_reward=100,
            order_index=2,
            is_published=True
        )
        db_session.add_all([python_lesson, cpp_lesson])
        db_session.commit()
        
        # Filter by Python
        response = client.get("/lessons/?language=python", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["language"] == "python"
        assert data[0]["title"] == "Python Lesson"
    
    def test_filter_by_difficulty(self, client, auth_headers, db_session):
        """Test filtering lessons by difficulty"""
        # Create lessons with different difficulties
        easy_lesson = Lesson(
            language=LanguageEnum.PYTHON,
            title="Easy Lesson",
            theory="Easy content",
            difficulty=1,
            xp_reward=50,
            order_index=1,
            is_published=True
        )
        hard_lesson = Lesson(
            language=LanguageEnum.PYTHON,
            title="Hard Lesson",
            theory="Hard content",
            difficulty=5,
            xp_reward=200,
            order_index=2,
            is_published=True
        )
        db_session.add_all([easy_lesson, hard_lesson])
        db_session.commit()
        
        # Filter by difficulty 1
        response = client.get("/lessons/?difficulty=1", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["difficulty"] == 1
        assert data[0]["title"] == "Easy Lesson"

class TestProgressTracking:
    
    def test_create_progress(self, client, auth_headers, sample_lesson):
        """Test creating lesson progress"""
        progress_data = {
            "status": "in_progress",
            "score": 0.75,
            "attempts": 2
        }
        
        response = client.post(f"/lessons/{sample_lesson.id}/progress", json=progress_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == progress_data["status"]
        assert data["score"] == progress_data["score"]
        assert data["attempts"] == progress_data["attempts"]
        assert data["lesson_id"] == sample_lesson.id
    
    def test_update_progress(self, client, auth_headers, sample_lesson, test_user, db_session):
        """Test updating existing lesson progress"""
        # Create initial progress
        initial_progress = Progress(
            user_id=test_user.id,
            lesson_id=sample_lesson.id,
            status=ProgressStatusEnum.IN_PROGRESS,
            score=0.5,
            attempts=1
        )
        db_session.add(initial_progress)
        db_session.commit()
        
        # Update progress
        update_data = {
            "status": "completed",
            "score": 0.9,
            "attempts": 3
        }
        
        response = client.post(f"/lessons/{sample_lesson.id}/progress", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["score"] == update_data["score"]
        assert data["attempts"] == update_data["attempts"]
    
    def test_get_progress(self, client, auth_headers, sample_lesson, test_user, db_session):
        """Test retrieving lesson progress"""
        # Create progress
        progress = Progress(
            user_id=test_user.id,
            lesson_id=sample_lesson.id,
            status=ProgressStatusEnum.COMPLETED,
            score=0.85,
            attempts=2
        )
        db_session.add(progress)
        db_session.commit()
        
        response = client.get(f"/lessons/{sample_lesson.id}/progress", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert data["score"] == 0.85
        assert data["attempts"] == 2
    
    def test_get_all_user_progress(self, client, auth_headers, test_user, db_session):
        """Test retrieving all user progress"""
        # Create multiple lessons and progress
        lesson1 = Lesson(
            language=LanguageEnum.PYTHON,
            title="Lesson 1",
            theory="Content 1",
            difficulty=1,
            xp_reward=100,
            order_index=1,
            is_published=True
        )
        lesson2 = Lesson(
            language=LanguageEnum.PYTHON,
            title="Lesson 2",
            theory="Content 2",
            difficulty=2,
            xp_reward=150,
            order_index=2,
            is_published=True
        )
        db_session.add_all([lesson1, lesson2])
        db_session.commit()
        
        progress1 = Progress(
            user_id=test_user.id,
            lesson_id=lesson1.id,
            status=ProgressStatusEnum.COMPLETED,
            score=0.9,
            attempts=1
        )
        progress2 = Progress(
            user_id=test_user.id,
            lesson_id=lesson2.id,
            status=ProgressStatusEnum.IN_PROGRESS,
            score=0.6,
            attempts=2
        )
        db_session.add_all([progress1, progress2])
        db_session.commit()
        
        response = client.get("/lessons/progress/all", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert any(p["lesson_id"] == lesson1.id for p in data)
        assert any(p["lesson_id"] == lesson2.id for p in data)

class TestLessonStatistics:
    
    def test_get_lesson_statistics(self, client, auth_headers, sample_lesson, test_user, db_session):
        """Test retrieving lesson statistics"""
        # Create some progress data
        progress1 = Progress(
            user_id=test_user.id,
            lesson_id=sample_lesson.id,
            status=ProgressStatusEnum.COMPLETED,
            score=0.8,
            attempts=2
        )
        
        # Create another user and progress
        user2 = AuthService.create_user(
            db=db_session,
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )
        
        progress2 = Progress(
            user_id=user2.id,
            lesson_id=sample_lesson.id,
            status=ProgressStatusEnum.IN_PROGRESS,
            score=0.6,
            attempts=1
        )
        
        db_session.add_all([progress1, progress2])
        db_session.commit()
        
        response = client.get(f"/lessons/{sample_lesson.id}/statistics", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["lesson_id"] == sample_lesson.id
        assert data["total_started"] == 2
        assert data["total_completed"] == 1
        assert data["completion_rate"] == 50.0
        assert data["average_score"] == 0.7  # (0.8 + 0.6) / 2

class TestAuthentication:
    
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated requests are rejected"""
        response = client.get("/lessons/")
        assert response.status_code == 403  # JWT middleware returns 403 for missing token
        
        response = client.post("/lessons/", json={})
        assert response.status_code == 403
        
        response = client.get("/lessons/1")
        assert response.status_code == 403