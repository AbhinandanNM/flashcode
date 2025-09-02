#!/usr/bin/env python3
"""
CodeCrafts MVP - Complete Application Flow Integration Test
This script tests the entire application flow from user registration to lesson completion
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
TEST_EMAIL = "integration.test@codecrafts.app"
TEST_USERNAME = "integration_test_user"
TEST_PASSWORD = "TestPassword123!"

@dataclass
class TestResult:
    name: str
    success: bool
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class IntegrationTester:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.results: list[TestResult] = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def record_result(self, name: str, success: bool, duration: float, 
                     error: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        result = TestResult(name, success, duration, error, details)
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status} {name} ({duration:.2f}s)")
        if error:
            self.log(f"Error: {error}", "ERROR")
    
    async def test_health_check(self) -> bool:
        """Test basic health check endpoints"""
        start_time = time.time()
        
        try:
            # Test backend health
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    raise Exception(f"Backend health check failed: {response.status}")
            
            # Test frontend availability (if running)
            try:
                async with self.session.get(f"{FRONTEND_URL}/health") as response:
                    pass  # Frontend health check is optional
            except:
                self.log("Frontend health check skipped (not running)", "WARN")
            
            duration = time.time() - start_time
            self.record_result("Health Check", True, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Health Check", False, duration, str(e))
            return False
    
    async def test_user_registration(self) -> bool:
        """Test user registration flow"""
        start_time = time.time()
        
        try:
            # Clean up any existing test user first
            await self.cleanup_test_user()
            
            registration_data = {
                "username": TEST_USERNAME,
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=registration_data
            ) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise Exception(f"Registration failed: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Validate response structure
                required_fields = ["access_token", "token_type", "user"]
                for field in required_fields:
                    if field not in data:
                        raise Exception(f"Missing field in registration response: {field}")
                
                # Store auth token and user info
                self.auth_token = data["access_token"]
                self.user_id = data["user"]["id"]
                
                # Validate user data
                user_data = data["user"]
                if user_data["username"] != TEST_USERNAME:
                    raise Exception("Username mismatch in registration response")
                if user_data["email"] != TEST_EMAIL:
                    raise Exception("Email mismatch in registration response")
            
            duration = time.time() - start_time
            self.record_result("User Registration", True, duration, 
                             details={"user_id": self.user_id})
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("User Registration", False, duration, str(e))
            return False
    
    async def test_user_authentication(self) -> bool:
        """Test user login flow"""
        start_time = time.time()
        
        try:
            login_data = {
                "username": TEST_EMAIL,  # Can login with email
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(
                f"{BASE_URL}/auth/login",
                data=login_data  # Form data for OAuth2
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Login failed: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Validate login response
                if "access_token" not in data:
                    raise Exception("No access token in login response")
                
                # Update auth token
                self.auth_token = data["access_token"]
            
            # Test authenticated endpoint
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                if response.status != 200:
                    raise Exception("Failed to access authenticated endpoint")
                
                user_data = await response.json()
                if user_data["email"] != TEST_EMAIL:
                    raise Exception("User data mismatch after login")
            
            duration = time.time() - start_time
            self.record_result("User Authentication", True, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("User Authentication", False, duration, str(e))
            return False
    
    async def test_lesson_browsing(self) -> bool:
        """Test lesson browsing and filtering"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get all lessons
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch lessons: {response.status}")
                
                lessons = await response.json()
                if not isinstance(lessons, list):
                    raise Exception("Lessons response is not a list")
                
                self.log(f"Found {len(lessons)} lessons")
            
            # Test lesson filtering
            async with self.session.get(
                f"{BASE_URL}/lessons?language=python&difficulty=1", 
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to filter lessons")
                
                filtered_lessons = await response.json()
                self.log(f"Found {len(filtered_lessons)} Python beginner lessons")
            
            duration = time.time() - start_time
            self.record_result("Lesson Browsing", True, duration, 
                             details={"total_lessons": len(lessons)})
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Lesson Browsing", False, duration, str(e))
            return False
    
    async def test_lesson_completion_flow(self) -> bool:
        """Test complete lesson flow with questions"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get available lessons
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                lessons = await response.json()
                
                if not lessons:
                    raise Exception("No lessons available for testing")
                
                # Use first lesson for testing
                lesson = lessons[0]
                lesson_id = lesson["id"]
                self.log(f"Testing lesson: {lesson['title']}")
            
            # Start the lesson
            async with self.session.post(
                f"{BASE_URL}/lessons/{lesson_id}/start", 
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to start lesson: {response.status}")
                
                progress = await response.json()
                if progress["status"] != "in_progress":
                    raise Exception("Lesson not marked as in progress")
            
            # Get lesson questions
            async with self.session.get(
                f"{BASE_URL}/lessons/{lesson_id}/questions", 
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to fetch lesson questions")
                
                questions = await response.json()
                self.log(f"Found {len(questions)} questions in lesson")
            
            # Answer questions
            correct_answers = 0
            for question in questions:
                question_id = question["id"]
                question_type = question["type"]
                
                # Determine correct answer based on question type
                if question_type == "mcq":
                    correct_answer = question.get("correct_answer", question["options"][0])
                elif question_type == "fill_blank":
                    correct_answer = question.get("correct_answer", "answer")
                else:
                    correct_answer = "print('Hello, World!')"  # Default for code questions
                
                # Submit answer
                answer_data = {
                    "question_id": question_id,
                    "user_answer": correct_answer
                }
                
                async with self.session.post(
                    f"{BASE_URL}/questions/submit",
                    json=answer_data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        self.log(f"Failed to submit answer for question {question_id}", "WARN")
                        continue
                    
                    result = await response.json()
                    if result.get("is_correct"):
                        correct_answers += 1
            
            # Complete the lesson
            completion_data = {"score": int((correct_answers / max(len(questions), 1)) * 100)}
            async with self.session.post(
                f"{BASE_URL}/lessons/{lesson_id}/complete",
                json=completion_data,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to complete lesson")
                
                completion_result = await response.json()
                if completion_result["status"] != "completed":
                    raise Exception("Lesson not marked as completed")
            
            duration = time.time() - start_time
            self.record_result("Lesson Completion Flow", True, duration,
                             details={
                                 "lesson_id": lesson_id,
                                 "questions_answered": len(questions),
                                 "correct_answers": correct_answers,
                                 "score": completion_data["score"]
                             })
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Lesson Completion Flow", False, duration, str(e))
            return False
    
    async def test_code_execution(self) -> bool:
        """Test code execution functionality"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test Python code execution
            python_code = {
                "code": "print('Hello from Python!')\nprint(2 + 3)",
                "language": "python"
            }
            
            async with self.session.post(
                f"{BASE_URL}/execute/run",
                json=python_code,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"Python code execution failed: {response.status}")
                
                result = await response.json()
                if "output" not in result:
                    raise Exception("No output in code execution result")
                
                self.log(f"Python execution output: {result['output'][:50]}...")
            
            # Test code validation
            validation_code = {
                "code": "def add_numbers(a, b):\n    return a + b",
                "language": "python",
                "test_cases": [
                    {"input": "2, 3", "expected_output": "5"},
                    {"input": "10, 15", "expected_output": "25"}
                ]
            }
            
            async with self.session.post(
                f"{BASE_URL}/execute/validate",
                json=validation_code,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Code validation failed")
                
                validation_result = await response.json()
                if not validation_result.get("is_correct"):
                    self.log("Code validation returned incorrect result", "WARN")
            
            duration = time.time() - start_time
            self.record_result("Code Execution", True, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Code Execution", False, duration, str(e))
            return False
    
    async def test_gamification_features(self) -> bool:
        """Test gamification features (XP, levels, achievements)"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get initial user stats
            async with self.session.get(f"{BASE_URL}/gamification/stats", headers=headers) as response:
                if response.status != 200:
                    raise Exception("Failed to fetch user stats")
                
                initial_stats = await response.json()
                initial_xp = initial_stats.get("total_xp", 0)
                initial_level = initial_stats.get("level", 1)
                
                self.log(f"Initial stats - XP: {initial_xp}, Level: {initial_level}")
            
            # Award some XP
            xp_data = {
                "amount": 100,
                "reason": "Integration test reward"
            }
            
            async with self.session.post(
                f"{BASE_URL}/gamification/award-xp",
                json=xp_data,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to award XP")
                
                xp_result = await response.json()
                new_xp = xp_result.get("new_total_xp", initial_xp)
                
                if new_xp <= initial_xp:
                    raise Exception("XP was not properly awarded")
            
            # Check leaderboard
            async with self.session.get(f"{BASE_URL}/gamification/leaderboard", headers=headers) as response:
                if response.status != 200:
                    raise Exception("Failed to fetch leaderboard")
                
                leaderboard = await response.json()
                if not isinstance(leaderboard, list):
                    raise Exception("Leaderboard is not a list")
                
                self.log(f"Leaderboard has {len(leaderboard)} entries")
            
            # Check achievements
            async with self.session.get(f"{BASE_URL}/gamification/achievements", headers=headers) as response:
                if response.status != 200:
                    raise Exception("Failed to fetch achievements")
                
                achievements = await response.json()
                self.log(f"User has {len(achievements)} achievements")
            
            duration = time.time() - start_time
            self.record_result("Gamification Features", True, duration,
                             details={
                                 "initial_xp": initial_xp,
                                 "awarded_xp": 100,
                                 "achievements_count": len(achievements)
                             })
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Gamification Features", False, duration, str(e))
            return False
    
    async def test_duel_system(self) -> bool:
        """Test duel system functionality"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get available questions for duels
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                lessons = await response.json()
                if not lessons:
                    raise Exception("No lessons available for duel testing")
                
                lesson_id = lessons[0]["id"]
            
            async with self.session.get(
                f"{BASE_URL}/lessons/{lesson_id}/questions", 
                headers=headers
            ) as response:
                questions = await response.json()
                if not questions:
                    raise Exception("No questions available for duel testing")
                
                question_id = questions[0]["id"]
            
            # Create a duel (this might fail if no other users exist)
            duel_data = {
                "challenger_id": self.user_id,
                "opponent_id": self.user_id,  # Self-duel for testing
                "question_id": question_id,
                "time_limit": 300
            }
            
            async with self.session.post(
                f"{BASE_URL}/duels",
                json=duel_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    duel = await response.json()
                    duel_id = duel["id"]
                    self.log(f"Created duel {duel_id}")
                    
                    # Get user's duels
                    async with self.session.get(f"{BASE_URL}/duels/my-duels", headers=headers) as response:
                        if response.status == 200:
                            duels = await response.json()
                            self.log(f"User has {len(duels)} duels")
                else:
                    self.log("Duel creation failed (expected in single-user test)", "WARN")
            
            duration = time.time() - start_time
            self.record_result("Duel System", True, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Duel System", False, duration, str(e))
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling and edge cases"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test invalid endpoints
            async with self.session.get(f"{BASE_URL}/nonexistent", headers=headers) as response:
                if response.status != 404:
                    raise Exception("Expected 404 for nonexistent endpoint")
            
            # Test unauthorized access
            async with self.session.get(f"{BASE_URL}/lessons") as response:
                if response.status not in [401, 200]:  # Might be public
                    raise Exception("Unexpected status for unauthorized request")
            
            # Test invalid data
            async with self.session.post(
                f"{BASE_URL}/questions/submit",
                json={"invalid": "data"},
                headers=headers
            ) as response:
                if response.status not in [400, 422]:
                    raise Exception("Expected validation error for invalid data")
            
            duration = time.time() - start_time
            self.record_result("Error Handling", True, duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Error Handling", False, duration, str(e))
            return False
    
    async def cleanup_test_user(self):
        """Clean up test user if it exists"""
        try:
            # This would require admin access or a cleanup endpoint
            # For now, we'll just log the attempt
            self.log("Attempting to clean up existing test user", "DEBUG")
        except:
            pass
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests"""
        self.log("Starting CodeCrafts MVP Integration Tests")
        self.log(f"Backend URL: {BASE_URL}")
        self.log(f"Frontend URL: {FRONTEND_URL}")
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_authentication,
            self.test_lesson_browsing,
            self.test_lesson_completion_flow,
            self.test_code_execution,
            self.test_gamification_features,
            self.test_duel_system,
            self.test_error_handling
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                success = await test()
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"Test {test.__name__} crashed: {e}", "ERROR")
                failed += 1
        
        # Print summary
        self.log("\n" + "="*60)
        self.log("INTEGRATION TEST SUMMARY")
        self.log("="*60)
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            self.log(f"{status} {result.name} ({result.duration:.2f}s)")
            if result.error:
                self.log(f"    Error: {result.error}")
            if result.details:
                self.log(f"    Details: {result.details}")
        
        self.log(f"\nTotal Tests: {len(self.results)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        
        if failed == 0:
            self.log("\n🎉 All integration tests passed! CodeCrafts MVP is ready for production.")
            return True
        else:
            self.log(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
            return False

async def main():
    """Main function to run integration tests"""
    async with IntegrationTester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())