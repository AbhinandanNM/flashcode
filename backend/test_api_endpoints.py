import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, client: TestClient, sample_user_data):
        """Test successful user registration"""
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == sample_user_data["username"]
        assert data["user"]["email"] == sample_user_data["email"]
    
    def test_register_user_duplicate_email(self, client: TestClient, sample_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/auth/register", json=sample_user_data)
        
        # Try to register with same email
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient):
        """Test successful login"""
        login_data = {
            "username": "test@example.com",
            "password": "secret"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_get_current_user(self, authenticated_client: TestClient):
        """Test getting current user info"""
        response = authenticated_client.get("/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

class TestLessonEndpoints:
    """Test lesson endpoints"""
    
    def test_get_lessons(self, authenticated_client: TestClient, db_with_lessons):
        """Test getting all lessons"""
        response = authenticated_client.get("/lessons")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Python Basics"
    
    def test_get_lessons_with_filters(self, authenticated_client: TestClient, db_with_lessons):
        """Test getting lessons with filters"""
        response = authenticated_client.get("/lessons?language=python&difficulty=1")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for lesson in data:
            assert lesson["language"] == "python"
            assert lesson["difficulty"] == 1
    
    def test_get_lesson_by_id(self, authenticated_client: TestClient, db_with_lessons):
        """Test getting a specific lesson"""
        response = authenticated_client.get("/lessons/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Python Basics"
    
    def test_get_lesson_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent lesson"""
        response = authenticated_client.get("/lessons/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_lesson_questions(self, authenticated_client: TestClient, db_with_questions):
        """Test getting questions for a lesson"""
        response = authenticated_client.get("/lessons/1/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_start_lesson(self, authenticated_client: TestClient, db_with_lessons):
        """Test starting a lesson"""
        response = authenticated_client.post("/lessons/1/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["lesson_id"] == 1
        assert data["status"] == "in_progress"
    
    def test_update_lesson_progress(self, authenticated_client: TestClient, db_with_lessons):
        """Test updating lesson progress"""
        progress_data = {
            "status": "completed",
            "score": 85
        }
        
        response = authenticated_client.put("/lessons/1/progress", json=progress_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["score"] == 85

class TestQuestionEndpoints:
    """Test question endpoints"""
    
    def test_get_question(self, authenticated_client: TestClient, db_with_questions):
        """Test getting a specific question"""
        response = authenticated_client.get("/questions/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "question" in data
    
    def test_submit_answer_correct(self, authenticated_client: TestClient, db_with_questions):
        """Test submitting correct answer"""
        answer_data = {
            "question_id": 1,
            "user_answer": "x = 5"
        }
        
        response = authenticated_client.post("/questions/submit", json=answer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert "xp_awarded" in data
    
    def test_submit_answer_incorrect(self, authenticated_client: TestClient, db_with_questions):
        """Test submitting incorrect answer"""
        answer_data = {
            "question_id": 1,
            "user_answer": "var x = 5"
        }
        
        response = authenticated_client.post("/questions/submit", json=answer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False
    
    def test_get_question_attempts(self, authenticated_client: TestClient, db_with_questions):
        """Test getting user's attempts for a question"""
        response = authenticated_client.get("/questions/1/attempts")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestCodeExecutionEndpoints:
    """Test code execution endpoints"""
    
    def test_execute_code(self, authenticated_client: TestClient, sample_code_data):
        """Test code execution"""
        response = authenticated_client.post("/execute/run", json=sample_code_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "output" in data
        assert "execution_time" in data
        assert data["output"] == "Hello, World!\n"
    
    def test_execute_code_with_error(self, authenticated_client: TestClient):
        """Test code execution with syntax error"""
        code_data = {
            "code": "print('Hello World'",  # Missing closing parenthesis
            "language": "python"
        }
        
        with patch('services.code_execution_service.execute_code') as mock_execute:
            mock_execute.return_value = {
                "output": "",
                "execution_time": 0,
                "memory_used": 0,
                "error": "SyntaxError: unexpected EOF while parsing"
            }
            
            response = authenticated_client.post("/execute/run", json=code_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "SyntaxError" in data["error"]
    
    def test_validate_code(self, authenticated_client: TestClient):
        """Test code validation against test cases"""
        validation_data = {
            "code": "def solution(n): return n * 3",
            "language": "python",
            "test_cases": [
                {"input": "5", "expected_output": "15"},
                {"input": "3", "expected_output": "9"}
            ]
        }
        
        response = authenticated_client.post("/execute/validate", json=validation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_correct" in data
        assert "test_results" in data
        assert data["is_correct"] is True

class TestGamificationEndpoints:
    """Test gamification endpoints"""
    
    def test_get_user_stats(self, authenticated_client: TestClient):
        """Test getting user gamification stats"""
        response = authenticated_client.get("/gamification/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_xp" in data
        assert "level" in data
        assert "streak" in data
    
    def test_get_leaderboard(self, authenticated_client: TestClient):
        """Test getting leaderboard"""
        response = authenticated_client.get("/gamification/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_achievements(self, authenticated_client: TestClient):
        """Test getting user achievements"""
        response = authenticated_client.get("/gamification/achievements")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_award_xp(self, authenticated_client: TestClient):
        """Test awarding XP to user"""
        xp_data = {
            "amount": 50,
            "reason": "Completed lesson"
        }
        
        response = authenticated_client.post("/gamification/award-xp", json=xp_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "new_total_xp" in data
        assert "level_up" in data

class TestDuelEndpoints:
    """Test duel endpoints"""
    
    def test_create_duel(self, authenticated_client: TestClient, sample_duel_data):
        """Test creating a new duel"""
        response = authenticated_client.post("/duels", json=sample_duel_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
    
    def test_get_user_duels(self, authenticated_client: TestClient):
        """Test getting user's duels"""
        response = authenticated_client.get("/duels/my-duels")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_join_duel(self, authenticated_client: TestClient):
        """Test joining a duel"""
        response = authenticated_client.post("/duels/1/join")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
    
    def test_submit_duel_answer(self, authenticated_client: TestClient):
        """Test submitting answer in a duel"""
        answer_data = {
            "answer": "x = 5",
            "time_taken": 45
        }
        
        response = authenticated_client.post("/duels/1/submit", json=answer_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_correct" in data
        assert "time_taken" in data

class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_unauthorized_access(self, client: TestClient):
        """Test accessing protected endpoints without authentication"""
        # Override to remove authentication
        from main import app
        from auth import get_current_user
        
        def no_auth():
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        app.dependency_overrides[get_current_user] = no_auth
        
        response = client.get("/lessons")
        assert response.status_code == 401
        
        # Restore authentication
        from conftest import override_get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
    
    def test_invalid_json_payload(self, authenticated_client: TestClient):
        """Test sending invalid JSON payload"""
        response = authenticated_client.post(
            "/questions/submit",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, authenticated_client: TestClient):
        """Test sending request with missing required fields"""
        incomplete_data = {
            "question_id": 1
            # Missing user_answer
        }
        
        response = authenticated_client.post("/questions/submit", json=incomplete_data)
        
        assert response.status_code == 422
        assert "validation error" in response.json()["detail"][0]["type"]
    
    def test_database_error_handling(self, authenticated_client: TestClient):
        """Test handling database errors"""
        with patch('models.get_db') as mock_db:
            mock_db.side_effect = Exception("Database connection error")
            
            response = authenticated_client.get("/lessons")
            
            assert response.status_code == 500

class TestRateLimiting:
    """Test rate limiting (if implemented)"""
    
    @pytest.mark.skip(reason="Rate limiting not implemented yet")
    def test_rate_limit_exceeded(self, authenticated_client: TestClient):
        """Test rate limiting on API endpoints"""
        # Make multiple rapid requests
        for _ in range(100):
            response = authenticated_client.get("/lessons")
            if response.status_code == 429:
                assert "rate limit" in response.json()["detail"].lower()
                break
        else:
            pytest.fail("Rate limit not triggered")

class TestPagination:
    """Test pagination on list endpoints"""
    
    def test_lessons_pagination(self, authenticated_client: TestClient, db_with_lessons):
        """Test pagination on lessons endpoint"""
        response = authenticated_client.get("/lessons?page=1&size=10")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if pagination metadata is included
        if isinstance(data, dict) and "items" in data:
            assert "total" in data
            assert "page" in data
            assert "size" in data
            assert isinstance(data["items"], list)
    
    def test_leaderboard_pagination(self, authenticated_client: TestClient):
        """Test pagination on leaderboard endpoint"""
        response = authenticated_client.get("/gamification/leaderboard?page=1&size=20")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or ("items" in data and isinstance(data["items"], list))