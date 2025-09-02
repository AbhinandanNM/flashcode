import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

from main import app
from database import Base, get_db
from models import User, Lesson, Question, Duel, QuestionAttempt, LanguageEnum, QuestionTypeEnum, DuelStatusEnum
from auth import AuthService

# Mock code execution service for testing
class MockCodeExecutionService:
    async def execute_code(self, code: str, language: str, expected_output: str = None):
        # Simple mock that returns success if code contains expected output
        is_correct = expected_output and expected_output.lower() in code.lower()
        
        # Return a proper CodeExecutionResponse-like object
        from schemas import CodeExecutionResponse
        return CodeExecutionResponse(
            status='success',
            stdout=expected_output if is_correct else 'Wrong output',
            stderr='',
            execution_time=0.1,
            is_correct=is_correct,
            error=None
        )

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_duels.db"
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
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_users(db_session):
    """Create test users"""
    user1 = User(
        username="challenger",
        email="challenger@test.com",
        password_hash=AuthService.get_password_hash("password123"),
        xp=100,
        streak=5
    )
    user2 = User(
        username="opponent",
        email="opponent@test.com", 
        password_hash=AuthService.get_password_hash("password123"),
        xp=150,
        streak=3
    )
    
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    
    return {"challenger": user1, "opponent": user2}

@pytest.fixture
def test_lesson_and_question(db_session):
    """Create test lesson and code question"""
    lesson = Lesson(
        language=LanguageEnum.PYTHON,
        title="Test Lesson",
        theory="Test theory content",
        difficulty=3,
        xp_reward=50,
        order_index=1
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    
    question = Question(
        lesson_id=lesson.id,
        type=QuestionTypeEnum.CODE,
        question_text="Write a function that returns 'Hello World'",
        correct_answer="Hello World",
        explanation="Simple function implementation",
        difficulty=3,
        xp_reward=30
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    
    return {"lesson": lesson, "question": question}

@pytest.fixture
def auth_headers(test_users):
    """Create authentication headers for test users"""
    challenger_token = AuthService.create_access_token(data={"sub": test_users["challenger"].username})
    opponent_token = AuthService.create_access_token(data={"sub": test_users["opponent"].username})
    
    return {
        "challenger": {"Authorization": f"Bearer {challenger_token}"},
        "opponent": {"Authorization": f"Bearer {opponent_token}"}
    }

class TestDuelCreation:
    def test_create_duel_success(self, client, test_users, test_lesson_and_question, auth_headers):
        """Test successful duel creation"""
        response = client.post(
            "/duels/create",
            json={"question_id": test_lesson_and_question["question"].id},
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["challenger_id"] == test_users["challenger"].id
        assert data["question_id"] == test_lesson_and_question["question"].id
        assert data["status"] == "waiting"
        assert data["opponent_id"] is None
        assert data["winner_id"] is None
    
    def test_create_duel_invalid_question(self, client, auth_headers):
        """Test duel creation with invalid question ID"""
        response = client.post(
            "/duels/create",
            json={"question_id": 99999},
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 400
        assert "Question not found" in response.json()["detail"]
    
    def test_create_duel_non_code_question(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test duel creation with non-code question"""
        # Create a non-code question
        lesson = test_lesson_and_question["lesson"]
        mcq_question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.MCQ,
            question_text="What is Python?",
            options={"a": "Language", "b": "Snake"},
            correct_answer="a",
            difficulty=1,
            xp_reward=10
        )
        db_session.add(mcq_question)
        db_session.commit()
        
        response = client.post(
            "/duels/create",
            json={"question_id": mcq_question.id},
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 400
        assert "Only code questions can be used for duels" in response.json()["detail"]
    
    def test_create_duel_already_active(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test creating duel when user already has active duel"""
        # Create an existing active duel
        existing_duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.ACTIVE
        )
        db_session.add(existing_duel)
        db_session.commit()
        
        response = client.post(
            "/duels/create",
            json={"question_id": test_lesson_and_question["question"].id},
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 400
        assert "You already have an active duel" in response.json()["detail"]

class TestDuelJoining:
    def test_join_duel_success(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test successful duel joining"""
        # Create a waiting duel
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        response = client.post(
            "/duels/join",
            json={"duel_id": duel.id},
            headers=auth_headers["opponent"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == duel.id
        assert data["opponent_id"] == test_users["opponent"].id
        assert data["status"] == "active"
    
    def test_join_nonexistent_duel(self, client, auth_headers):
        """Test joining non-existent duel"""
        response = client.post(
            "/duels/join",
            json={"duel_id": 99999},
            headers=auth_headers["opponent"]
        )
        
        assert response.status_code == 400
        assert "Duel not found" in response.json()["detail"]
    
    def test_join_own_duel(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test joining own duel"""
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        response = client.post(
            "/duels/join",
            json={"duel_id": duel.id},
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 400
        assert "Cannot join your own duel" in response.json()["detail"]
    
    def test_join_completed_duel(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test joining completed duel"""
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.COMPLETED,
            winner_id=test_users["challenger"].id
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        response = client.post(
            "/duels/join",
            json={"duel_id": duel.id},
            headers=auth_headers["opponent"]
        )
        
        assert response.status_code == 400
        assert "Duel is not available for joining" in response.json()["detail"]

class TestDuelDetails:
    def test_get_duel_success(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test getting duel details"""
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            opponent_id=test_users["opponent"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.ACTIVE
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        response = client.get(
            f"/duels/{duel.id}",
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == duel.id
        assert data["challenger_username"] == test_users["challenger"].username
        assert data["opponent_username"] == test_users["opponent"].username
        assert data["question"]["id"] == test_lesson_and_question["question"].id
        assert data["is_bot_opponent"] is False
    
    def test_get_duel_unauthorized(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test getting duel details without access"""
        # Create third user
        third_user = User(
            username="third_user",
            email="third@test.com",
            password_hash=AuthService.get_password_hash("password123")
        )
        db_session.add(third_user)
        db_session.commit()
        
        third_user_token = AuthService.create_access_token(data={"sub": third_user.username})
        third_user_headers = {"Authorization": f"Bearer {third_user_token}"}
        
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            opponent_id=test_users["opponent"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.ACTIVE
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        response = client.get(
            f"/duels/{duel.id}",
            headers=third_user_headers
        )
        
        assert response.status_code == 404
        assert "Access denied to this duel" in response.json()["detail"]

class TestDuelSubmission:
    def test_submit_solution_success(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test successful solution submission"""
        # Patch the duel service to use mock code execution
        from unittest.mock import patch
        
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            opponent_id=test_users["opponent"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.ACTIVE
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        # Mock the code execution service
        with patch('services.duel_service.CodeExecutionService') as mock_service:
            mock_instance = MockCodeExecutionService()
            mock_service.return_value = mock_instance
            
            # Submit correct solution
            response = client.post(
                f"/duels/{duel.id}/submit",
                json={
                    "duel_id": duel.id,
                    "code": "print('Hello World')",
                    "language": "python",
                    "time_taken": 30
                },
                headers=auth_headers["challenger"]
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["duel_id"] == duel.id
        # Note: Winner determination depends on code execution result
    
    def test_submit_to_nonexistent_duel(self, client, auth_headers):
        """Test submitting to non-existent duel"""
        response = client.post(
            "/duels/99999/submit",
            json={
                "duel_id": 99999,
                "code": "print('Hello World')",
                "language": "python",
                "time_taken": 30
            },
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 400
        assert "Duel not found" in response.json()["detail"]
    
    def test_submit_to_waiting_duel(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test submitting to waiting duel"""
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        response = client.post(
            f"/duels/{duel.id}/submit",
            json={
                "duel_id": duel.id,
                "code": "print('Hello World')",
                "language": "python",
                "time_taken": 30
            },
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 400
        assert "Duel is not active" in response.json()["detail"]

class TestDuelListing:
    def test_get_available_duels(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test getting available duels"""
        # Create waiting duel
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING
        )
        db_session.add(duel)
        db_session.commit()
        
        response = client.get(
            "/duels/available/list",
            headers=auth_headers["opponent"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == duel.id
        assert data[0]["challenger_username"] == test_users["challenger"].username
        assert data[0]["status"] == "waiting"
    
    def test_get_user_duels(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test getting user's duel history"""
        # Create completed duel
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            opponent_id=test_users["opponent"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.COMPLETED,
            winner_id=test_users["challenger"].id,
            completed_at=datetime.now(timezone.utc)
        )
        db_session.add(duel)
        db_session.commit()
        
        response = client.get(
            "/duels/user/history",
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == duel.id
        assert data[0]["challenger_username"] == test_users["challenger"].username
        assert data[0]["opponent_username"] == test_users["opponent"].username
        assert data[0]["status"] == "completed"

class TestBotOpponents:
    def test_bot_opponent_assignment(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test bot opponent functionality"""
        # Create duel that should get bot opponent
        duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING,
            created_at=datetime.now(timezone.utc) - timedelta(seconds=35)  # Old enough for bot assignment
        )
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        # Manually assign bot (simulating the matchmaking process)
        duel.opponent_id = -3  # Bot with difficulty 3
        duel.status = DuelStatusEnum.ACTIVE
        db_session.commit()
        
        response = client.get(
            f"/duels/{duel.id}",
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_bot_opponent"] is True
        assert data["opponent_username"] == "CodeBot Expert"
        assert data["opponent_id"] == -3

class TestDuelCleanup:
    def test_cleanup_old_duels(self, client, test_users, test_lesson_and_question, auth_headers, db_session):
        """Test cleanup of old waiting duels"""
        # Create old waiting duel
        old_duel = Duel(
            challenger_id=test_users["challenger"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
        
        # Create recent waiting duel
        recent_duel = Duel(
            challenger_id=test_users["opponent"].id,
            question_id=test_lesson_and_question["question"].id,
            status=DuelStatusEnum.WAITING,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2)
        )
        
        db_session.add(old_duel)
        db_session.add(recent_duel)
        db_session.commit()
        
        response = client.delete(
            "/duels/cleanup",
            headers=auth_headers["challenger"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Cleaned up 1 old duels" in data["message"]
        
        # Verify old duel was deleted but recent one remains
        remaining_duels = db_session.query(Duel).all()
        assert len(remaining_duels) == 1
        assert remaining_duels[0].id == recent_duel.id

if __name__ == "__main__":
    pytest.main([__file__])