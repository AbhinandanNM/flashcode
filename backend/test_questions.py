import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, Lesson, Question, QuestionAttempt, LanguageEnum, QuestionTypeEnum
from auth import AuthService
import json

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_questions.db"
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
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        xp=100,
        streak=5
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_lesson(db_session):
    lesson = Lesson(
        language=LanguageEnum.PYTHON,
        title="Test Lesson",
        theory="This is test theory content",
        difficulty=2,
        xp_reward=50,
        order_index=1,
        is_published=True
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    return lesson

@pytest.fixture
def auth_headers(test_user):
    token = AuthService.create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mcq_question(db_session, test_lesson):
    question = Question(
        lesson_id=test_lesson.id,
        type=QuestionTypeEnum.MCQ,
        question_text="What is the output of print('Hello')?",
        options={"A": "Hello", "B": "hello", "C": "HELLO", "D": "Error"},
        correct_answer="A",
        explanation="print() outputs exactly what's in the string",
        difficulty=1,
        xp_reward=10
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def fill_blank_question(db_session, test_lesson):
    question = Question(
        lesson_id=test_lesson.id,
        type=QuestionTypeEnum.FILL_BLANK,
        question_text="Complete the code: for i in _____(5):",
        options=None,
        correct_answer="range",
        explanation="range() function generates a sequence of numbers",
        difficulty=2,
        xp_reward=15
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def flashcard_question(db_session, test_lesson):
    question = Question(
        lesson_id=test_lesson.id,
        type=QuestionTypeEnum.FLASHCARD,
        question_text="What does the 'len()' function do?",
        options=None,
        correct_answer="returns the length of an object",
        explanation="len() returns the number of items in an object",
        difficulty=1,
        xp_reward=5
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def code_question(db_session, test_lesson):
    question = Question(
        lesson_id=test_lesson.id,
        type=QuestionTypeEnum.CODE,
        question_text="Write a function that returns the sum of two numbers:",
        options=None,
        correct_answer="def add(a, b):\n    return a + b",
        explanation="A simple function that adds two parameters",
        difficulty=3,
        xp_reward=25
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question


class TestQuestionCRUD:
    
    def test_create_question(self, client, auth_headers, test_lesson):
        question_data = {
            "lesson_id": test_lesson.id,
            "type": "mcq",
            "question_text": "What is Python?",
            "options": {"A": "A snake", "B": "A programming language", "C": "A movie", "D": "A game"},
            "correct_answer": "B",
            "explanation": "Python is a programming language",
            "difficulty": 2,
            "xp_reward": 15
        }
        
        response = client.post("/questions/", json=question_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["lesson_id"] == test_lesson.id
        assert data["type"] == "mcq"
        assert data["question_text"] == "What is Python?"
        assert data["difficulty"] == 2
        assert data["xp_reward"] == 15
    
    def test_get_question(self, client, auth_headers, mcq_question):
        response = client.get(f"/questions/{mcq_question.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == mcq_question.id
        assert data["question_text"] == mcq_question.question_text
        assert data["type"] == "mcq"
    
    def test_get_nonexistent_question(self, client, auth_headers):
        response = client.get("/questions/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_questions_by_lesson(self, client, auth_headers, mcq_question, fill_blank_question):
        response = client.get(f"/questions/lesson/{mcq_question.lesson_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Check that correct_answer is not included in list response
        for question in data:
            assert "correct_answer" not in question
            assert "explanation" not in question
    
    def test_get_questions_by_lesson_with_type_filter(self, client, auth_headers, mcq_question, fill_blank_question):
        response = client.get(
            f"/questions/lesson/{mcq_question.lesson_id}?question_type=mcq",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "mcq"
    
    def test_update_question(self, client, auth_headers, mcq_question):
        update_data = {
            "question_text": "Updated question text",
            "difficulty": 3
        }
        
        response = client.put(f"/questions/{mcq_question.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["question_text"] == "Updated question text"
        assert data["difficulty"] == 3
    
    def test_delete_question(self, client, auth_headers, mcq_question):
        response = client.delete(f"/questions/{mcq_question.id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify question is deleted
        get_response = client.get(f"/questions/{mcq_question.id}", headers=auth_headers)
        assert get_response.status_code == 404


class TestAnswerValidation:
    
    def test_submit_correct_mcq_answer(self, client, auth_headers, mcq_question, test_user, db_session):
        submission = {
            "question_id": mcq_question.id,
            "user_answer": "A",
            "time_taken": 30
        }
        
        initial_xp = test_user.xp
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_correct"] == True
        assert data["xp_awarded"] == mcq_question.xp_reward
        assert data["correct_answer"] is None  # Not shown for correct answers
        
        # Check XP was awarded
        db_session.refresh(test_user)
        assert test_user.xp == initial_xp + mcq_question.xp_reward
    
    def test_submit_incorrect_mcq_answer(self, client, auth_headers, mcq_question, test_user, db_session):
        submission = {
            "question_id": mcq_question.id,
            "user_answer": "B",
            "time_taken": 45
        }
        
        initial_xp = test_user.xp
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_correct"] == False
        assert data["xp_awarded"] == 0
        assert data["correct_answer"] == "A"  # Shown for incorrect answers
        
        # Check XP was not awarded
        db_session.refresh(test_user)
        assert test_user.xp == initial_xp
    
    def test_submit_correct_fill_blank_answer(self, client, auth_headers, fill_blank_question):
        submission = {
            "question_id": fill_blank_question.id,
            "user_answer": "range",
            "time_taken": 20
        }
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_correct"] == True
        assert data["xp_awarded"] == fill_blank_question.xp_reward
    
    def test_submit_fill_blank_answer_case_insensitive(self, client, auth_headers, fill_blank_question):
        submission = {
            "question_id": fill_blank_question.id,
            "user_answer": "RANGE",
            "time_taken": 25
        }
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_correct"] == True
    
    def test_submit_flashcard_answer_partial_match(self, client, auth_headers, flashcard_question):
        submission = {
            "question_id": flashcard_question.id,
            "user_answer": "returns the length of object",  # Partial but sufficient match (5/6 words = 83%)
            "time_taken": 15
        }
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_correct"] == True
    
    def test_submit_code_answer_normalized(self, client, auth_headers, code_question):
        submission = {
            "question_id": code_question.id,
            "user_answer": "def add(a, b):\n    return a + b  # Simple addition",
            "time_taken": 120
        }
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_correct"] == True
    
    def test_submit_answer_nonexistent_question(self, client, auth_headers):
        submission = {
            "question_id": 999,
            "user_answer": "test",
            "time_taken": 30
        }
        
        response = client.post("/questions/submit", json=submission, headers=auth_headers)
        assert response.status_code == 404


class TestQuestionAttempts:
    
    def test_get_my_attempts(self, client, auth_headers, mcq_question):
        # Submit an answer first
        submission = {
            "question_id": mcq_question.id,
            "user_answer": "A",
            "time_taken": 30
        }
        client.post("/questions/submit", json=submission, headers=auth_headers)
        
        # Get attempts
        response = client.get("/questions/attempts/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["question_id"] == mcq_question.id
        assert data[0]["user_answer"] == "A"
        assert data[0]["is_correct"] == True
    
    def test_get_attempts_for_specific_question(self, client, auth_headers, mcq_question, fill_blank_question):
        # Submit answers for both questions
        client.post("/questions/submit", json={
            "question_id": mcq_question.id,
            "user_answer": "A",
            "time_taken": 30
        }, headers=auth_headers)
        
        client.post("/questions/submit", json={
            "question_id": fill_blank_question.id,
            "user_answer": "range",
            "time_taken": 20
        }, headers=auth_headers)
        
        # Get attempts for specific question
        response = client.get(f"/questions/attempts/me?question_id={mcq_question.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["question_id"] == mcq_question.id


class TestQuestionStatistics:
    
    def test_get_question_statistics(self, client, auth_headers, mcq_question, test_user, db_session):
        # Create some attempts
        attempt1 = QuestionAttempt(
            user_id=test_user.id,
            question_id=mcq_question.id,
            user_answer="A",
            is_correct=True,
            time_taken=30
        )
        attempt2 = QuestionAttempt(
            user_id=test_user.id,
            question_id=mcq_question.id,
            user_answer="B",
            is_correct=False,
            time_taken=45
        )
        
        db_session.add_all([attempt1, attempt2])
        db_session.commit()
        
        response = client.get(f"/questions/{mcq_question.id}/statistics", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["question_id"] == mcq_question.id
        assert data["total_attempts"] == 2
        assert data["correct_attempts"] == 1
        assert data["success_rate"] == 50.0
        assert data["average_time_seconds"] == 37.5


class TestQuestionValidation:
    
    def test_create_question_invalid_difficulty(self, client, auth_headers, test_lesson):
        question_data = {
            "lesson_id": test_lesson.id,
            "type": "mcq",
            "question_text": "Test question",
            "options": {"A": "Option A", "B": "Option B"},
            "correct_answer": "A",
            "difficulty": 6,  # Invalid difficulty
            "xp_reward": 10
        }
        
        response = client.post("/questions/", json=question_data, headers=auth_headers)
        assert response.status_code == 422
    
    def test_create_mcq_without_options(self, client, auth_headers, test_lesson):
        question_data = {
            "lesson_id": test_lesson.id,
            "type": "mcq",
            "question_text": "Test question",
            "options": None,  # Missing options for MCQ
            "correct_answer": "A",
            "difficulty": 2,
            "xp_reward": 10
        }
        
        response = client.post("/questions/", json=question_data, headers=auth_headers)
        assert response.status_code == 422


class TestAuthentication:
    
    def test_create_question_without_auth(self, client, test_lesson):
        question_data = {
            "lesson_id": test_lesson.id,
            "type": "mcq",
            "question_text": "Test question",
            "options": {"A": "Option A", "B": "Option B"},
            "correct_answer": "A",
            "difficulty": 2,
            "xp_reward": 10
        }
        
        response = client.post("/questions/", json=question_data)
        assert response.status_code == 403
    
    def test_submit_answer_without_auth(self, client, mcq_question):
        submission = {
            "question_id": mcq_question.id,
            "user_answer": "A",
            "time_taken": 30
        }
        
        response = client.post("/questions/submit", json=submission)
        assert response.status_code == 403