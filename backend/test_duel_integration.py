import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import User, Lesson, Question, LanguageEnum, QuestionTypeEnum
from auth import AuthService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_duel_integration.db"
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

def test_complete_duel_workflow(client, db_session):
    """Test complete duel workflow from creation to completion"""
    
    # Create test users
    user1 = User(
        username="player1",
        email="player1@test.com",
        password_hash=AuthService.get_password_hash("password123"),
        xp=0,
        streak=0
    )
    user2 = User(
        username="player2",
        email="player2@test.com",
        password_hash=AuthService.get_password_hash("password123"),
        xp=0,
        streak=0
    )
    
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    
    # Create test lesson and question
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
    
    # Create auth tokens
    player1_token = AuthService.create_access_token(data={"sub": user1.username})
    player2_token = AuthService.create_access_token(data={"sub": user2.username})
    
    player1_headers = {"Authorization": f"Bearer {player1_token}"}
    player2_headers = {"Authorization": f"Bearer {player2_token}"}
    
    # Step 1: Player 1 creates a duel
    response = client.post(
        "/duels/create",
        json={"question_id": question.id},
        headers=player1_headers
    )
    
    assert response.status_code == 200
    duel_data = response.json()
    duel_id = duel_data["id"]
    assert duel_data["challenger_id"] == user1.id
    assert duel_data["status"] == "waiting"
    
    # Step 2: Player 2 sees available duels
    response = client.get(
        "/duels/available/list",
        headers=player2_headers
    )
    
    assert response.status_code == 200
    available_duels = response.json()
    assert len(available_duels) == 1
    assert available_duels[0]["id"] == duel_id
    
    # Step 3: Player 2 joins the duel
    response = client.post(
        "/duels/join",
        json={"duel_id": duel_id},
        headers=player2_headers
    )
    
    assert response.status_code == 200
    join_data = response.json()
    assert join_data["opponent_id"] == user2.id
    assert join_data["status"] == "active"
    
    # Step 4: Get duel details
    response = client.get(
        f"/duels/{duel_id}",
        headers=player1_headers
    )
    
    assert response.status_code == 200
    duel_details = response.json()
    assert duel_details["challenger_username"] == "player1"
    assert duel_details["opponent_username"] == "player2"
    assert duel_details["is_bot_opponent"] is False
    
    # Step 5: Player 1 submits solution (mock will make it correct)
    from unittest.mock import patch
    from test_duels import MockCodeExecutionService
    
    with patch('services.duel_service.CodeExecutionService') as mock_service:
        mock_instance = MockCodeExecutionService()
        mock_service.return_value = mock_instance
        
        response = client.post(
            f"/duels/{duel_id}/submit",
            json={
                "duel_id": duel_id,
                "code": "print('Hello World')",  # This will be correct in mock
                "language": "python",
                "time_taken": 25
            },
            headers=player1_headers
        )
    
    assert response.status_code == 200
    result_data = response.json()
    assert result_data["duel_id"] == duel_id
    assert result_data["winner_id"] == user1.id
    assert result_data["winner_username"] == "player1"
    assert result_data["xp_awarded"] > 0
    
    # Step 6: Check user duel history
    response = client.get(
        "/duels/user/history",
        headers=player1_headers
    )
    
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["id"] == duel_id
    assert history[0]["status"] == "completed"
    
    # Step 7: Verify no more available duels
    response = client.get(
        "/duels/available/list",
        headers=player2_headers
    )
    
    assert response.status_code == 200
    available_duels = response.json()
    assert len(available_duels) == 0  # Duel is now completed

if __name__ == "__main__":
    pytest.main([__file__])