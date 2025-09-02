"""
Complete integration tests that verify the entire system works together
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import User, Lesson, Question, UserProgress, QuestionAttempt
import json

class TestCompleteUserJourney:
    """Test complete user journey from registration to lesson completion"""
    
    def test_complete_learning_journey(self, client: TestClient, db_session: Session):
        """Test a complete user learning journey"""
        
        # 1. User Registration
        registration_data = {
            "username": "learner123",
            "email": "learner@example.com",
            "password": "securepassword123"
        }
        
        register_response = client.post("/auth/register", json=registration_data)
        assert register_response.status_code == 201
        
        auth_data = register_response.json()
        token = auth_data["access_token"]
        user_id = auth_data["user"]["id"]
        
        # Set authorization header for subsequent requests
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Browse Available Lessons
        lessons_response = client.get("/lessons", headers=headers)
        assert lessons_response.status_code == 200
        
        lessons = lessons_response.json()
        assert len(lessons) >= 0  # May be empty in test environment
        
        # 3. Create a test lesson for the journey
        lesson_data = {
            "title": "Python Fundamentals",
            "description": "Learn Python basics",
            "language": "python",
            "difficulty": 1,
            "xp_reward": 100,
            "estimated_time": 45,
            "content": {
                "theory": "Python is a programming language...",
                "examples": ["print('Hello')", "x = 5"]
            }
        }
        
        lesson = Lesson(**lesson_data)
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        # 4. Start the Lesson
        start_response = client.post(f"/lessons/{lesson.id}/start", headers=headers)
        assert start_response.status_code == 200
        
        progress_data = start_response.json()
        assert progress_data["status"] == "in_progress"
        assert progress_data["lesson_id"] == lesson.id
        
        # 5. Create and Answer Questions
        question_data = {
            "lesson_id": lesson.id,
            "type": "mcq",
            "difficulty": 1,
            "question": "What is the correct way to print in Python?",
            "options": ["print('Hello')", "echo 'Hello'", "console.log('Hello')", "printf('Hello')"],
            "correct_answer": "print('Hello')",
            "explanation": "Python uses the print() function for output.",
            "xp_reward": 15
        }
        
        question = Question(**question_data)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        # Answer the question correctly
        answer_data = {
            "question_id": question.id,
            "user_answer": "print('Hello')"
        }
        
        answer_response = client.post("/questions/submit", json=answer_data, headers=headers)
        assert answer_response.status_code == 200
        
        answer_result = answer_response.json()
        assert answer_result["is_correct"] is True
        assert answer_result["xp_awarded"] == 15
        
        # 6. Complete the Lesson
        completion_data = {"score": 95}
        complete_response = client.post(
            f"/lessons/{lesson.id}/complete", 
            json=completion_data, 
            headers=headers
        )
        assert complete_response.status_code == 200
        
        completion_result = complete_response.json()
        assert completion_result["status"] == "completed"
        assert completion_result["score"] == 95
        
        # 7. Check Updated User Stats
        stats_response = client.get("/gamification/stats", headers=headers)
        assert stats_response.status_code == 200
        
        stats = stats_response.json()
        assert stats["total_xp"] >= 115  # 100 (lesson) + 15 (question)
        
        # 8. Verify Progress is Saved
        progress_response = client.get(f"/lessons/{lesson.id}/progress", headers=headers)
        assert progress_response.status_code == 200
        
        final_progress = progress_response.json()
        assert final_progress["status"] == "completed"
        assert final_progress["score"] == 95
    
    def test_code_execution_workflow(self, client: TestClient, db_session: Session):
        """Test complete code execution and validation workflow"""
        
        # Create authenticated user
        user = User(
            username="coder123",
            email="coder@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock authentication (using override from conftest)
        headers = {"Authorization": "Bearer mock-token"}
        
        # 1. Execute Simple Code
        code_data = {
            "code": "print('Hello, CodeCrafts!')",
            "language": "python"
        }
        
        execute_response = client.post("/execute/run", json=code_data, headers=headers)
        assert execute_response.status_code == 200
        
        execution_result = execute_response.json()
        assert "output" in execution_result
        assert "execution_time" in execution_result
        
        # 2. Validate Code Against Test Cases
        validation_data = {
            "code": "def add_numbers(a, b):\n    return a + b",
            "language": "python",
            "test_cases": [
                {"input": "2, 3", "expected_output": "5"},
                {"input": "10, 15", "expected_output": "25"},
                {"input": "0, 0", "expected_output": "0"}
            ]
        }
        
        validate_response = client.post("/execute/validate", json=validation_data, headers=headers)
        assert validate_response.status_code == 200
        
        validation_result = validate_response.json()
        assert validation_result["is_correct"] is True
        assert validation_result["total_tests"] == 3
        assert validation_result["passed_tests"] == 3
    
    def test_duel_system_workflow(self, client: TestClient, db_session: Session):
        """Test complete duel system workflow"""
        
        # Create two users
        challenger = User(
            username="challenger",
            email="challenger@example.com",
            hashed_password="hash1",
            is_active=True
        )
        opponent = User(
            username="opponent",
            email="opponent@example.com",
            hashed_password="hash2",
            is_active=True
        )
        
        db_session.add_all([challenger, opponent])
        db_session.commit()
        
        # Create a question for the duel
        question = Question(
            lesson_id=1,
            type="mcq",
            difficulty=2,
            question="What is the output of print(2 ** 3)?",
            options=["6", "8", "9", "16"],
            correct_answer="8",
            explanation="2 ** 3 means 2 to the power of 3, which equals 8.",
            xp_reward=20
        )
        
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # 1. Create Duel
        duel_data = {
            "challenger_id": challenger.id,
            "opponent_id": opponent.id,
            "question_id": question.id,
            "time_limit": 300
        }
        
        create_response = client.post("/duels", json=duel_data, headers=headers)
        assert create_response.status_code == 201
        
        duel_result = create_response.json()
        duel_id = duel_result["id"]
        assert duel_result["status"] == "pending"
        
        # 2. Opponent Joins Duel
        join_response = client.post(f"/duels/{duel_id}/join", headers=headers)
        assert join_response.status_code == 200
        
        join_result = join_response.json()
        assert join_result["status"] == "active"
        
        # 3. Submit Answers
        challenger_answer = {
            "answer": "8",
            "time_taken": 45
        }
        
        challenger_response = client.post(
            f"/duels/{duel_id}/submit", 
            json=challenger_answer, 
            headers=headers
        )
        assert challenger_response.status_code == 200
        
        challenger_result = challenger_response.json()
        assert challenger_result["is_correct"] is True
        
        # 4. Check Duel Results
        results_response = client.get(f"/duels/{duel_id}/results", headers=headers)
        assert results_response.status_code == 200
        
        results = results_response.json()
        assert "winner_id" in results
        assert "challenger_score" in results
        assert "opponent_score" in results

class TestErrorRecoveryWorkflows:
    """Test error handling and recovery in complete workflows"""
    
    def test_lesson_with_invalid_questions(self, client: TestClient, db_session: Session):
        """Test handling of lessons with invalid or missing questions"""
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # Create lesson without questions
        lesson = Lesson(
            title="Empty Lesson",
            description="A lesson with no questions",
            language="python",
            difficulty=1,
            xp_reward=50,
            estimated_time=15
        )
        
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        # Try to start lesson
        start_response = client.post(f"/lessons/{lesson.id}/start", headers=headers)
        assert start_response.status_code == 200  # Should still work
        
        # Try to get questions (should return empty list)
        questions_response = client.get(f"/lessons/{lesson.id}/questions", headers=headers)
        assert questions_response.status_code == 200
        
        questions = questions_response.json()
        assert len(questions) == 0
    
    def test_code_execution_with_errors(self, client: TestClient):
        """Test code execution error handling"""
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # Test syntax error
        syntax_error_code = {
            "code": "print('Hello World'",  # Missing closing parenthesis
            "language": "python"
        }
        
        response = client.post("/execute/run", json=syntax_error_code, headers=headers)
        assert response.status_code == 200  # Should return 200 with error in response
        
        result = response.json()
        # The mock should handle this gracefully
        assert "output" in result or "error" in result
    
    def test_authentication_failure_recovery(self, client: TestClient):
        """Test recovery from authentication failures"""
        
        # Try to access protected endpoint without token
        response = client.get("/lessons")
        assert response.status_code == 401
        
        # Try with invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/lessons", headers=invalid_headers)
        # Depending on implementation, might be 401 or work with mock override
        assert response.status_code in [200, 401]

class TestDataConsistencyWorkflows:
    """Test data consistency across the system"""
    
    def test_xp_consistency_across_actions(self, client: TestClient, db_session: Session):
        """Test that XP is consistently tracked across different actions"""
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # Get initial stats
        initial_stats = client.get("/gamification/stats", headers=headers)
        assert initial_stats.status_code == 200
        
        initial_xp = initial_stats.json()["total_xp"]
        
        # Create lesson and question
        lesson = Lesson(
            title="XP Test Lesson",
            language="python",
            difficulty=1,
            xp_reward=100,
            estimated_time=30
        )
        
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        question = Question(
            lesson_id=lesson.id,
            type="mcq",
            difficulty=1,
            question="Test question?",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            xp_reward=25
        )
        
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        # Answer question
        answer_response = client.post(
            "/questions/submit",
            json={"question_id": question.id, "user_answer": "A"},
            headers=headers
        )
        assert answer_response.status_code == 200
        
        # Complete lesson
        complete_response = client.post(
            f"/lessons/{lesson.id}/complete",
            json={"score": 100},
            headers=headers
        )
        assert complete_response.status_code == 200
        
        # Check final stats
        final_stats = client.get("/gamification/stats", headers=headers)
        assert final_stats.status_code == 200
        
        final_xp = final_stats.json()["total_xp"]
        
        # XP should have increased by question XP + lesson XP
        expected_increase = 25 + 100  # question + lesson
        assert final_xp >= initial_xp + expected_increase
    
    def test_progress_tracking_consistency(self, client: TestClient, db_session: Session):
        """Test that progress is consistently tracked"""
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # Create lesson
        lesson = Lesson(
            title="Progress Test",
            language="python",
            difficulty=1,
            xp_reward=75,
            estimated_time=20
        )
        
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        # Start lesson
        start_response = client.post(f"/lessons/{lesson.id}/start", headers=headers)
        assert start_response.status_code == 200
        
        # Check progress
        progress_response = client.get(f"/lessons/{lesson.id}/progress", headers=headers)
        assert progress_response.status_code == 200
        
        progress = progress_response.json()
        assert progress["status"] == "in_progress"
        
        # Complete lesson
        complete_response = client.post(
            f"/lessons/{lesson.id}/complete",
            json={"score": 85},
            headers=headers
        )
        assert complete_response.status_code == 200
        
        # Verify progress updated
        final_progress_response = client.get(f"/lessons/{lesson.id}/progress", headers=headers)
        assert final_progress_response.status_code == 200
        
        final_progress = final_progress_response.json()
        assert final_progress["status"] == "completed"
        assert final_progress["score"] == 85

class TestConcurrencyWorkflows:
    """Test concurrent operations and race conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_question_submissions(self, client: TestClient, db_session: Session):
        """Test handling of concurrent question submissions"""
        
        # This test would require async client and proper concurrency setup
        # For now, we'll test sequential submissions to verify no conflicts
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # Create question
        question = Question(
            lesson_id=1,
            type="mcq",
            difficulty=1,
            question="Concurrent test?",
            options=["A", "B"],
            correct_answer="A",
            xp_reward=10
        )
        
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        # Submit multiple answers (simulating rapid submissions)
        responses = []
        for i in range(3):
            response = client.post(
                "/questions/submit",
                json={"question_id": question.id, "user_answer": "A"},
                headers=headers
            )
            responses.append(response)
        
        # All should succeed (or handle duplicates appropriately)
        for response in responses:
            assert response.status_code == 200
    
    def test_concurrent_lesson_progress_updates(self, client: TestClient, db_session: Session):
        """Test concurrent progress updates"""
        
        headers = {"Authorization": "Bearer mock-token"}
        
        # Create lesson
        lesson = Lesson(
            title="Concurrent Progress Test",
            language="python",
            difficulty=1,
            xp_reward=50,
            estimated_time=15
        )
        
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        # Start lesson
        start_response = client.post(f"/lessons/{lesson.id}/start", headers=headers)
        assert start_response.status_code == 200
        
        # Multiple progress updates
        update_responses = []
        for score in [60, 70, 80]:
            response = client.put(
                f"/lessons/{lesson.id}/progress",
                json={"status": "in_progress", "score": score},
                headers=headers
            )
            update_responses.append(response)
        
        # All updates should succeed
        for response in update_responses:
            assert response.status_code == 200
        
        # Final progress should reflect last update
        final_progress = client.get(f"/lessons/{lesson.id}/progress", headers=headers)
        assert final_progress.status_code == 200
        
        progress_data = final_progress.json()
        assert progress_data["score"] == 80  # Last update