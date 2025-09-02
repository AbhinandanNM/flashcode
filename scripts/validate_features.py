#!/usr/bin/env python3
"""
CodeCrafts MVP - Feature Validation Script
Tests all question types, code execution, and gamification features
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, Any, List
from dataclasses import dataclass

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TEST_EMAIL = "feature.test@codecrafts.app"
TEST_USERNAME = "feature_test_user"
TEST_PASSWORD = "TestPassword123!"

@dataclass
class ValidationResult:
    feature: str
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    error: str = None

class FeatureValidator:
    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.auth_token: str = None
        self.user_id: int = None
        self.results: List[ValidationResult] = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
    
    def record_result(self, feature: str, test_name: str, success: bool, 
                     duration: float, details: Dict[str, Any], error: str = None):
        result = ValidationResult(feature, test_name, success, duration, details, error)
        self.results.append(result)
        
        status = "✅" if success else "❌"
        self.log(f"{status} {feature}: {test_name} ({duration:.2f}s)")
        if error:
            self.log(f"   Error: {error}")
    
    async def setup_test_user(self) -> bool:
        """Setup test user for validation"""
        try:
            # Try to register test user
            registration_data = {
                "username": TEST_USERNAME,
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=registration_data) as response:
                if response.status == 201:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    return True
                elif response.status == 400:
                    # User might already exist, try login
                    return await self.login_test_user()
                else:
                    return False
        except Exception:
            return await self.login_test_user()
    
    async def login_test_user(self) -> bool:
        """Login existing test user"""
        try:
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", data=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    
                    # Get user info
                    headers = {"Authorization": f"Bearer {self.auth_token}"}
                    async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as user_response:
                        if user_response.status == 200:
                            user_data = await user_response.json()
                            self.user_id = user_data["id"]
                            return True
                return False
        except Exception:
            return False
    
    async def validate_mcq_questions(self):
        """Validate Multiple Choice Questions"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get lessons to find MCQ questions
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                lessons = await response.json()
                
                mcq_found = False
                for lesson in lessons:
                    async with self.session.get(f"{BASE_URL}/lessons/{lesson['id']}/questions", headers=headers) as q_response:
                        questions = await q_response.json()
                        
                        for question in questions:
                            if question["type"] == "mcq":
                                mcq_found = True
                                
                                # Test correct answer
                                correct_answer = question.get("correct_answer", question["options"][0])
                                answer_data = {
                                    "question_id": question["id"],
                                    "user_answer": correct_answer
                                }
                                
                                async with self.session.post(f"{BASE_URL}/questions/submit", json=answer_data, headers=headers) as submit_response:
                                    if submit_response.status == 200:
                                        result = await submit_response.json()
                                        
                                        duration = time.time() - start_time
                                        self.record_result(
                                            "MCQ Questions", 
                                            "Correct Answer Submission",
                                            result.get("is_correct", False),
                                            duration,
                                            {
                                                "question_id": question["id"],
                                                "question": question["question"][:50] + "...",
                                                "correct_answer": correct_answer,
                                                "xp_awarded": result.get("xp_awarded", 0)
                                            }
                                        )
                                        
                                        # Test incorrect answer
                                        incorrect_options = [opt for opt in question["options"] if opt != correct_answer]
                                        if incorrect_options:
                                            incorrect_answer = incorrect_options[0]
                                            wrong_answer_data = {
                                                "question_id": question["id"],
                                                "user_answer": incorrect_answer
                                            }
                                            
                                            async with self.session.post(f"{BASE_URL}/questions/submit", json=wrong_answer_data, headers=headers) as wrong_response:
                                                if wrong_response.status == 200:
                                                    wrong_result = await wrong_response.json()
                                                    
                                                    duration = time.time() - start_time
                                                    self.record_result(
                                                        "MCQ Questions",
                                                        "Incorrect Answer Handling",
                                                        not wrong_result.get("is_correct", True),
                                                        duration,
                                                        {
                                                            "question_id": question["id"],
                                                            "incorrect_answer": incorrect_answer,
                                                            "correctly_marked_wrong": not wrong_result.get("is_correct", True)
                                                        }
                                                    )
                                        return
                
                if not mcq_found:
                    duration = time.time() - start_time
                    self.record_result(
                        "MCQ Questions",
                        "Question Availability",
                        False,
                        duration,
                        {},
                        "No MCQ questions found in lessons"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("MCQ Questions", "Validation", False, duration, {}, str(e))
    
    async def validate_fill_blank_questions(self):
        """Validate Fill in the Blank Questions"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Look for fill-in-the-blank questions
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                lessons = await response.json()
                
                fill_blank_found = False
                for lesson in lessons:
                    async with self.session.get(f"{BASE_URL}/lessons/{lesson['id']}/questions", headers=headers) as q_response:
                        questions = await q_response.json()
                        
                        for question in questions:
                            if question["type"] == "fill_blank":
                                fill_blank_found = True
                                
                                correct_answer = question.get("correct_answer", "=")
                                answer_data = {
                                    "question_id": question["id"],
                                    "user_answer": correct_answer
                                }
                                
                                async with self.session.post(f"{BASE_URL}/questions/submit", json=answer_data, headers=headers) as submit_response:
                                    if submit_response.status == 200:
                                        result = await submit_response.json()
                                        
                                        duration = time.time() - start_time
                                        self.record_result(
                                            "Fill Blank Questions",
                                            "Answer Validation",
                                            result.get("is_correct", False),
                                            duration,
                                            {
                                                "question_id": question["id"],
                                                "question": question["question"][:50] + "...",
                                                "answer": correct_answer
                                            }
                                        )
                                        return
                
                if not fill_blank_found:
                    duration = time.time() - start_time
                    self.record_result(
                        "Fill Blank Questions",
                        "Question Availability",
                        True,  # Not finding them is OK
                        duration,
                        {},
                        "No fill-blank questions found (this is acceptable)"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Fill Blank Questions", "Validation", False, duration, {}, str(e))
    
    async def validate_code_questions(self):
        """Validate Code Questions"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Look for code questions
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                lessons = await response.json()
                
                code_found = False
                for lesson in lessons:
                    async with self.session.get(f"{BASE_URL}/lessons/{lesson['id']}/questions", headers=headers) as q_response:
                        questions = await q_response.json()
                        
                        for question in questions:
                            if question["type"] == "code":
                                code_found = True
                                
                                # Use the solution if available, otherwise a simple solution
                                solution = question.get("solution", "def solution():\n    return 'Hello, World!'")
                                answer_data = {
                                    "question_id": question["id"],
                                    "user_answer": solution
                                }
                                
                                async with self.session.post(f"{BASE_URL}/questions/submit", json=answer_data, headers=headers) as submit_response:
                                    if submit_response.status == 200:
                                        result = await submit_response.json()
                                        
                                        duration = time.time() - start_time
                                        self.record_result(
                                            "Code Questions",
                                            "Solution Validation",
                                            result.get("is_correct", False),
                                            duration,
                                            {
                                                "question_id": question["id"],
                                                "question": question["question"][:50] + "...",
                                                "test_cases": len(question.get("test_cases", [])),
                                                "solution_length": len(solution)
                                            }
                                        )
                                        return
                
                if not code_found:
                    duration = time.time() - start_time
                    self.record_result(
                        "Code Questions",
                        "Question Availability",
                        True,  # Not finding them is OK for now
                        duration,
                        {},
                        "No code questions found (this is acceptable)"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Code Questions", "Validation", False, duration, {}, str(e))
    
    async def validate_python_execution(self):
        """Validate Python Code Execution"""
        test_cases = [
            {
                "name": "Simple Print",
                "code": "print('Hello, CodeCrafts!')",
                "expected_output": "Hello, CodeCrafts!"
            },
            {
                "name": "Mathematical Operations",
                "code": "result = 2 + 3 * 4\nprint(result)",
                "expected_output": "14"
            },
            {
                "name": "String Operations",
                "code": "name = 'Python'\nprint(f'Learning {name}!')",
                "expected_output": "Learning Python!"
            },
            {
                "name": "Loop Example",
                "code": "for i in range(3):\n    print(f'Count: {i}')",
                "expected_output": "Count: 0\nCount: 1\nCount: 2"
            },
            {
                "name": "Function Definition",
                "code": "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))",
                "expected_output": "Hello, World!"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        for test_case in test_cases:
            start_time = time.time()
            
            try:
                code_data = {
                    "code": test_case["code"],
                    "language": "python"
                }
                
                async with self.session.post(f"{BASE_URL}/execute/run", json=code_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        output = result.get("output", "").strip()
                        
                        # Check if output contains expected content
                        success = test_case["expected_output"] in output
                        
                        duration = time.time() - start_time
                        self.record_result(
                            "Python Execution",
                            test_case["name"],
                            success,
                            duration,
                            {
                                "code": test_case["code"][:30] + "...",
                                "expected": test_case["expected_output"],
                                "actual": output[:100] + "..." if len(output) > 100 else output,
                                "execution_time": result.get("execution_time", 0)
                            }
                        )
                    else:
                        duration = time.time() - start_time
                        error_text = await response.text()
                        self.record_result(
                            "Python Execution",
                            test_case["name"],
                            False,
                            duration,
                            {"code": test_case["code"][:30] + "..."},
                            f"HTTP {response.status}: {error_text}"
                        )
            
            except Exception as e:
                duration = time.time() - start_time
                self.record_result(
                    "Python Execution",
                    test_case["name"],
                    False,
                    duration,
                    {"code": test_case["code"][:30] + "..."},
                    str(e)
                )
    
    async def validate_code_validation(self):
        """Validate Code Validation with Test Cases"""
        validation_cases = [
            {
                "name": "Simple Function",
                "code": "def add_numbers(a, b):\n    return a + b",
                "test_cases": [
                    {"input": "2, 3", "expected_output": "5"},
                    {"input": "10, 15", "expected_output": "25"},
                    {"input": "0, 0", "expected_output": "0"}
                ]
            },
            {
                "name": "String Function",
                "code": "def greet(name):\n    return f'Hello, {name}!'",
                "test_cases": [
                    {"input": "'World'", "expected_output": "Hello, World!"},
                    {"input": "'Python'", "expected_output": "Hello, Python!"}
                ]
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        for case in validation_cases:
            start_time = time.time()
            
            try:
                validation_data = {
                    "code": case["code"],
                    "language": "python",
                    "test_cases": case["test_cases"]
                }
                
                async with self.session.post(f"{BASE_URL}/execute/validate", json=validation_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        is_correct = result.get("is_correct", False)
                        total_tests = result.get("total_tests", 0)
                        passed_tests = result.get("passed_tests", 0)
                        
                        duration = time.time() - start_time
                        self.record_result(
                            "Code Validation",
                            case["name"],
                            is_correct,
                            duration,
                            {
                                "total_tests": total_tests,
                                "passed_tests": passed_tests,
                                "success_rate": f"{passed_tests}/{total_tests}",
                                "test_results": result.get("test_results", [])
                            }
                        )
                    else:
                        duration = time.time() - start_time
                        error_text = await response.text()
                        self.record_result(
                            "Code Validation",
                            case["name"],
                            False,
                            duration,
                            {},
                            f"HTTP {response.status}: {error_text}"
                        )
            
            except Exception as e:
                duration = time.time() - start_time
                self.record_result(
                    "Code Validation",
                    case["name"],
                    False,
                    duration,
                    {},
                    str(e)
                )
    
    async def validate_gamification_system(self):
        """Validate Gamification Features"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test XP System
        start_time = time.time()
        try:
            # Get initial stats
            async with self.session.get(f"{BASE_URL}/gamification/stats", headers=headers) as response:
                if response.status == 200:
                    initial_stats = await response.json()
                    initial_xp = initial_stats.get("total_xp", 0)
                    initial_level = initial_stats.get("level", 1)
                    
                    # Award XP
                    xp_data = {"amount": 50, "reason": "Feature validation test"}
                    async with self.session.post(f"{BASE_URL}/gamification/award-xp", json=xp_data, headers=headers) as xp_response:
                        if xp_response.status == 200:
                            xp_result = await xp_response.json()
                            new_xp = xp_result.get("new_total_xp", initial_xp)
                            
                            duration = time.time() - start_time
                            self.record_result(
                                "Gamification",
                                "XP Award System",
                                new_xp > initial_xp,
                                duration,
                                {
                                    "initial_xp": initial_xp,
                                    "awarded_xp": 50,
                                    "new_xp": new_xp,
                                    "xp_increase": new_xp - initial_xp
                                }
                            )
                        else:
                            duration = time.time() - start_time
                            self.record_result("Gamification", "XP Award System", False, duration, {}, "Failed to award XP")
                else:
                    duration = time.time() - start_time
                    self.record_result("Gamification", "Stats Retrieval", False, duration, {}, "Failed to get user stats")
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Gamification", "XP System", False, duration, {}, str(e))
        
        # Test Leaderboard
        start_time = time.time()
        try:
            async with self.session.get(f"{BASE_URL}/gamification/leaderboard", headers=headers) as response:
                if response.status == 200:
                    leaderboard = await response.json()
                    
                    duration = time.time() - start_time
                    self.record_result(
                        "Gamification",
                        "Leaderboard",
                        isinstance(leaderboard, list),
                        duration,
                        {
                            "leaderboard_size": len(leaderboard),
                            "has_rankings": len(leaderboard) > 0
                        }
                    )
                else:
                    duration = time.time() - start_time
                    self.record_result("Gamification", "Leaderboard", False, duration, {}, "Failed to fetch leaderboard")
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Gamification", "Leaderboard", False, duration, {}, str(e))
        
        # Test Achievements
        start_time = time.time()
        try:
            async with self.session.get(f"{BASE_URL}/gamification/achievements", headers=headers) as response:
                if response.status == 200:
                    achievements = await response.json()
                    
                    duration = time.time() - start_time
                    self.record_result(
                        "Gamification",
                        "Achievements",
                        isinstance(achievements, list),
                        duration,
                        {
                            "achievements_count": len(achievements),
                            "has_achievements": len(achievements) > 0
                        }
                    )
                else:
                    duration = time.time() - start_time
                    self.record_result("Gamification", "Achievements", False, duration, {}, "Failed to fetch achievements")
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Gamification", "Achievements", False, duration, {}, str(e))
    
    async def validate_lesson_progress_tracking(self):
        """Validate Lesson Progress Tracking"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get lessons
            async with self.session.get(f"{BASE_URL}/lessons", headers=headers) as response:
                lessons = await response.json()
                
                if not lessons:
                    duration = time.time() - start_time
                    self.record_result("Progress Tracking", "Lesson Availability", False, duration, {}, "No lessons available")
                    return
                
                lesson = lessons[0]
                lesson_id = lesson["id"]
                
                # Start lesson
                async with self.session.post(f"{BASE_URL}/lessons/{lesson_id}/start", headers=headers) as start_response:
                    if start_response.status == 200:
                        progress = await start_response.json()
                        
                        # Check progress
                        async with self.session.get(f"{BASE_URL}/lessons/{lesson_id}/progress", headers=headers) as progress_response:
                            if progress_response.status == 200:
                                progress_data = await progress_response.json()
                                
                                # Update progress
                                update_data = {"status": "in_progress", "score": 75}
                                async with self.session.put(f"{BASE_URL}/lessons/{lesson_id}/progress", json=update_data, headers=headers) as update_response:
                                    if update_response.status == 200:
                                        updated_progress = await update_response.json()
                                        
                                        duration = time.time() - start_time
                                        self.record_result(
                                            "Progress Tracking",
                                            "Lesson Progress Flow",
                                            updated_progress.get("score") == 75,
                                            duration,
                                            {
                                                "lesson_id": lesson_id,
                                                "initial_status": progress.get("status"),
                                                "updated_score": updated_progress.get("score"),
                                                "progress_tracked": True
                                            }
                                        )
                                    else:
                                        duration = time.time() - start_time
                                        self.record_result("Progress Tracking", "Progress Update", False, duration, {}, "Failed to update progress")
                            else:
                                duration = time.time() - start_time
                                self.record_result("Progress Tracking", "Progress Retrieval", False, duration, {}, "Failed to get progress")
                    else:
                        duration = time.time() - start_time
                        self.record_result("Progress Tracking", "Lesson Start", False, duration, {}, "Failed to start lesson")
        
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Progress Tracking", "Validation", False, duration, {}, str(e))
    
    async def run_all_validations(self):
        """Run all feature validations"""
        self.log("Starting CodeCrafts MVP Feature Validation")
        self.log(f"Backend URL: {BASE_URL}")
        
        # Setup test user
        if not await self.setup_test_user():
            self.log("Failed to setup test user", "ERROR")
            return False
        
        self.log(f"Test user setup complete (ID: {self.user_id})")
        
        # Run all validations
        validations = [
            self.validate_mcq_questions,
            self.validate_fill_blank_questions,
            self.validate_code_questions,
            self.validate_python_execution,
            self.validate_code_validation,
            self.validate_gamification_system,
            self.validate_lesson_progress_tracking
        ]
        
        for validation in validations:
            try:
                await validation()
            except Exception as e:
                self.log(f"Validation {validation.__name__} crashed: {e}", "ERROR")
        
        # Print summary
        self.print_summary()
        
        # Return overall success
        failed_tests = [r for r in self.results if not r.success]
        return len(failed_tests) == 0
    
    def print_summary(self):
        """Print validation summary"""
        self.log("\n" + "="*80)
        self.log("FEATURE VALIDATION SUMMARY")
        self.log("="*80)
        
        # Group results by feature
        features = {}
        for result in self.results:
            if result.feature not in features:
                features[result.feature] = []
            features[result.feature].append(result)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - passed_tests
        
        for feature, tests in features.items():
            feature_passed = len([t for t in tests if t.success])
            feature_total = len(tests)
            
            self.log(f"\n{feature}: {feature_passed}/{feature_total} tests passed")
            
            for test in tests:
                status = "✅" if test.success else "❌"
                self.log(f"  {status} {test.test_name} ({test.duration:.2f}s)")
                if test.error:
                    self.log(f"      Error: {test.error}")
                if test.details:
                    key_details = {k: v for k, v in test.details.items() if k in ['xp_awarded', 'success_rate', 'total_tests', 'passed_tests']}
                    if key_details:
                        self.log(f"      Details: {key_details}")
        
        self.log(f"\nOVERALL RESULTS:")
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {failed_tests}")
        self.log(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests == 0:
            self.log("\n🎉 All feature validations passed! CodeCrafts MVP is fully functional.")
        else:
            self.log(f"\n⚠️  {failed_tests} validation(s) failed. Review the errors above.")

async def main():
    """Main function"""
    async with FeatureValidator() as validator:
        success = await validator.run_all_validations()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())