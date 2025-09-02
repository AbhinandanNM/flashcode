#!/usr/bin/env python3
"""
Integration test for code questions and code execution
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, Lesson, Question, LanguageEnum, QuestionTypeEnum
from auth import AuthService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_code_question_integration.db"
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

def test_code_question_integration(client, db_session):
    """Test the integration between code questions and code execution"""
    
    # 1. Create a test user
    user = User(
        username="coder",
        email="coder@example.com",
        password_hash="hashed_password",
        xp=0
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # 2. Create a test lesson
    lesson = Lesson(
        language=LanguageEnum.PYTHON,
        title="Python Functions",
        theory="Learn about Python functions",
        difficulty=2,
        xp_reward=50,
        order_index=1
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    
    # 3. Create a code question
    question = Question(
        lesson_id=lesson.id,
        type=QuestionTypeEnum.CODE,
        question_text="Write a function that returns 'Hello World'",
        correct_answer='def hello():\n    return "Hello World"',
        explanation="A simple function that returns a string",
        difficulty=2,
        xp_reward=25
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    
    # 4. Get authentication token
    token = AuthService.create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 5. Test code execution endpoint (standalone)
    code_request = {
        "code": 'print("Hello World")',
        "language": "python"
    }
    
    exec_response = client.post("/execute/run", json=code_request, headers=headers)
    assert exec_response.status_code == 200
    exec_result = exec_response.json()
    print(f"Code execution result: {exec_result}")
    
    # 6. Test submitting a correct code answer through questions endpoint
    correct_submission = {
        "question_id": question.id,
        "user_answer": 'def hello():\n    return "Hello World"',
        "time_taken": 120
    }
    
    initial_xp = user.xp
    
    response = client.post("/questions/submit", json=correct_submission, headers=headers)
    assert response.status_code == 200
    
    result = response.json()
    assert result["is_correct"] == True
    assert result["xp_awarded"] == 25
    
    # Check XP was awarded
    db_session.refresh(user)
    assert user.xp == initial_xp + 25
    
    # 7. Test submitting an incorrect code answer
    incorrect_submission = {
        "question_id": question.id,
        "user_answer": 'def hello():\n    return "Wrong Answer"',
        "time_taken": 90
    }
    
    response = client.post("/questions/submit", json=incorrect_submission, headers=headers)
    assert response.status_code == 200
    
    result = response.json()
    assert result["is_correct"] == False
    assert result["xp_awarded"] == 0
    assert result["correct_answer"] == 'def hello():\n    return "Hello World"'
    
    # 8. Test code submission endpoint (for code questions)
    code_submission = {
        "question_id": question.id,
        "code": 'def hello():\n    return "Hello World"\nprint(hello())',
        "language": "python",
        "time_taken": 150
    }
    
    code_response = client.post("/execute/submit", json=code_submission, headers=headers)
    print(f"Code submission response status: {code_response.status_code}")
    if code_response.status_code == 200:
        code_result = code_response.json()
        print(f"Code submission result: {code_result}")
        # Note: This might fail if Docker is not available, which is expected
    
    print("✅ Code question integration test completed!")
    print(f"   - User gained {user.xp - initial_xp} XP from correct code answer")
    print(f"   - Code execution endpoint working: {exec_response.status_code == 200}")
    print(f"   - Question validation working for code questions")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])