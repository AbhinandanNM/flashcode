#!/usr/bin/env python3
"""
Integration test for the complete question system workflow
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_question_integration.db"
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

def test_complete_question_workflow(client, db_session):
    """Test the complete workflow: register user, create lesson, create questions, submit answers"""
    
    # 1. Register a user
    user_data = {
        "username": "testlearner",
        "email": "learner@example.com",
        "password": "password123"
    }
    
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200
    user_info = register_response.json()
    
    # 2. Login to get token
    login_response = client.post("/auth/login", json={
        "username": "testlearner",
        "password": "password123"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # 3. Create a lesson
    lesson_data = {
        "language": "python",
        "title": "Python Basics",
        "theory": "Python is a programming language with simple syntax.",
        "difficulty": 1,
        "xp_reward": 30,
        "order_index": 1,
        "is_published": True
    }
    
    lesson_response = client.post("/lessons/", json=lesson_data, headers=auth_headers)
    assert lesson_response.status_code == 200
    lesson = lesson_response.json()
    lesson_id = lesson["id"]
    
    # 4. Create different types of questions
    questions_data = [
        {
            "lesson_id": lesson_id,
            "type": "mcq",
            "question_text": "What is Python?",
            "options": {"A": "A snake", "B": "A programming language", "C": "A movie"},
            "correct_answer": "B",
            "explanation": "Python is a programming language",
            "difficulty": 1,
            "xp_reward": 10
        },
        {
            "lesson_id": lesson_id,
            "type": "fill_blank",
            "question_text": "Python uses _____ for indentation",
            "correct_answer": "spaces",
            "explanation": "Python uses spaces (or tabs) for indentation",
            "difficulty": 1,
            "xp_reward": 10
        },
        {
            "lesson_id": lesson_id,
            "type": "flashcard",
            "question_text": "What does 'print()' do?",
            "correct_answer": "displays output to console",
            "explanation": "print() function displays output",
            "difficulty": 1,
            "xp_reward": 5
        }
    ]
    
    created_questions = []
    for q_data in questions_data:
        q_response = client.post("/questions/", json=q_data, headers=auth_headers)
        assert q_response.status_code == 200
        created_questions.append(q_response.json())
    
    # 5. Get questions for the lesson
    questions_response = client.get(f"/questions/lesson/{lesson_id}", headers=auth_headers)
    assert questions_response.status_code == 200
    questions_list = questions_response.json()
    assert len(questions_list) == 3
    
    # Verify that correct answers are not exposed in the list
    for q in questions_list:
        assert "correct_answer" not in q
        assert "explanation" not in q
    
    # 6. Submit correct answers and track XP
    initial_profile = client.get("/auth/profile", headers=auth_headers).json()
    initial_xp = initial_profile["xp"]
    
    # Submit correct MCQ answer
    mcq_submission = {
        "question_id": created_questions[0]["id"],
        "user_answer": "B",
        "time_taken": 30
    }
    mcq_response = client.post("/questions/submit", json=mcq_submission, headers=auth_headers)
    assert mcq_response.status_code == 200
    mcq_result = mcq_response.json()
    assert mcq_result["is_correct"] == True
    assert mcq_result["xp_awarded"] == 10
    
    # Submit correct fill-blank answer
    fill_submission = {
        "question_id": created_questions[1]["id"],
        "user_answer": "spaces",
        "time_taken": 20
    }
    fill_response = client.post("/questions/submit", json=fill_submission, headers=auth_headers)
    assert fill_response.status_code == 200
    fill_result = fill_response.json()
    assert fill_result["is_correct"] == True
    assert fill_result["xp_awarded"] == 10
    
    # Submit correct flashcard answer
    flashcard_submission = {
        "question_id": created_questions[2]["id"],
        "user_answer": "displays output",
        "time_taken": 15
    }
    flashcard_response = client.post("/questions/submit", json=flashcard_submission, headers=auth_headers)
    assert flashcard_response.status_code == 200
    flashcard_result = flashcard_response.json()
    assert flashcard_result["is_correct"] == True
    assert flashcard_result["xp_awarded"] == 5
    
    # 7. Verify XP was awarded correctly
    updated_profile = client.get("/auth/profile", headers=auth_headers).json()
    expected_xp = initial_xp + 10 + 10 + 5  # Total XP from correct answers
    assert updated_profile["xp"] == expected_xp
    
    # 8. Submit an incorrect answer
    wrong_submission = {
        "question_id": created_questions[0]["id"],
        "user_answer": "A",  # Wrong answer
        "time_taken": 25
    }
    wrong_response = client.post("/questions/submit", json=wrong_submission, headers=auth_headers)
    assert wrong_response.status_code == 200
    wrong_result = wrong_response.json()
    assert wrong_result["is_correct"] == False
    assert wrong_result["xp_awarded"] == 0
    assert wrong_result["correct_answer"] == "B"  # Correct answer shown for wrong answers
    
    # 9. Check user's attempts
    attempts_response = client.get("/questions/attempts/me", headers=auth_headers)
    assert attempts_response.status_code == 200
    attempts = attempts_response.json()
    assert len(attempts) == 4  # 3 correct + 1 incorrect
    
    # 10. Get question statistics
    stats_response = client.get(f"/questions/{created_questions[0]['id']}/statistics", headers=auth_headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_attempts"] == 2  # MCQ was attempted twice
    assert stats["correct_attempts"] == 1
    assert stats["success_rate"] == 50.0
    
    print("✅ Complete question system workflow test passed!")
    print(f"   - User gained {expected_xp - initial_xp} XP from correct answers")
    print(f"   - Made {len(attempts)} total attempts")
    print(f"   - MCQ success rate: {stats['success_rate']}%")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])