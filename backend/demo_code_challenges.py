#!/usr/bin/env python3
"""
Demo script to showcase the Python Loops code challenges.
This demonstrates the code validation system with the new challenges.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Base, Lesson, Question
from services.code_validation_service import CodeValidationService
import json

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./codecrafts.db"

async def demo_code_challenges():
    """Demo the Python Loops code challenges with validation."""
    
    print("🚀 Python Loops Code Challenges Demo")
    print("=" * 50)
    
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get the Python Loops lesson
        result = await session.execute(
            select(Lesson).where(Lesson.title == "Python Loops: For and While")
        )
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            print("❌ Python Loops lesson not found!")
            return
        
        print(f"📚 Lesson: {lesson.title}")
        print(f"🎯 Total XP: {lesson.xp_reward}")
        
        # Get all code challenges
        result = await session.execute(
            select(Question).where(
                Question.lesson_id == lesson.id,
                Question.type == "code"
            ).order_by(Question.difficulty, Question.xp_reward)
        )
        code_questions = result.scalars().all()
        
        print(f"💻 Found {len(code_questions)} code challenges")
        print()
        
        # Initialize code validation service
        validator = CodeValidationService()
        
        # Demo a few challenges
        demo_challenges = [
            {
                "question": code_questions[0],  # Basic sum function
                "correct_code": """def sum_numbers(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total""",
                "test_input": "sum_numbers(5)",
                "expected": "15"
            },
            {
                "question": code_questions[5],  # FizzBuzz challenge
                "correct_code": """def fizz_buzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)""",
                "test_input": "fizz_buzz(5)",
                "expected": "1\n2\nFizz\n4\nBuzz"
            }
        ]
        
        for i, demo in enumerate(demo_challenges, 1):
            question = demo["question"]
            print(f"🧪 Demo Challenge {i}: {question.question_text[:50]}...")
            print(f"   Difficulty: Level {question.difficulty}")
            print(f"   XP Reward: {question.xp_reward}")
            
            # Parse test cases from options if available
            test_cases = []
            if question.options:
                try:
                    test_cases = json.loads(question.options)
                except:
                    # Fallback to manual test case
                    test_cases = [{
                        "input": demo["test_input"],
                        "expected_output": demo["expected"],
                        "description": f"Test {question.id}"
                    }]
            else:
                test_cases = [{
                    "input": demo["test_input"],
                    "expected_output": demo["expected"],
                    "description": f"Test {question.id}"
                }]
            
            # Test correct solution
            print("   Testing correct solution...")
            result = await validator.validate_code(demo["correct_code"], test_cases)
            
            status = "✅ PASSED" if result.is_correct else "❌ FAILED"
            print(f"   Result: {status} ({result.passed_tests}/{result.total_tests} tests)")
            
            if result.test_results:
                for test in result.test_results:
                    test_status = "✅" if test["passed"] else "❌"
                    print(f"     {test_status} {test['description']}")
            
            print()
        
        # Show challenge statistics
        print("📊 Challenge Statistics:")
        difficulty_counts = {}
        total_xp = 0
        
        for question in code_questions:
            diff = question.difficulty
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            total_xp += question.xp_reward
        
        print(f"   Total Code Challenges: {len(code_questions)}")
        print(f"   Total XP from Code: {total_xp}")
        print("   Difficulty Distribution:")
        
        difficulty_names = {1: "Beginner", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Expert"}
        for diff, count in sorted(difficulty_counts.items()):
            name = difficulty_names.get(diff, f"Level {diff}")
            print(f"     - Level {diff} ({name}): {count} challenges")
        
        print()
        print("🎮 Challenge Types Available:")
        
        # Categorize challenges by content
        categories = {
            "Basic Loops": 0,
            "Algorithm Challenges": 0,
            "Debugging Exercises": 0,
            "Advanced Patterns": 0
        }
        
        for question in code_questions:
            text = question.question_text.lower()
            if any(word in text for word in ["basic", "simple", "count", "sum"]):
                categories["Basic Loops"] += 1
            elif any(word in text for word in ["fizzbuzz", "prime", "fibonacci", "algorithm"]):
                categories["Algorithm Challenges"] += 1
            elif any(word in text for word in ["debug", "fix", "error"]):
                categories["Debugging Exercises"] += 1
            else:
                categories["Advanced Patterns"] += 1
        
        for category, count in categories.items():
            if count > 0:
                print(f"   - {category}: {count} challenges")
        
        print()
        print("🏆 Learning Path:")
        print("   1. Start with basic loop exercises (Level 1-2)")
        print("   2. Practice algorithm implementation (Level 3-4)")
        print("   3. Debug common loop errors")
        print("   4. Master advanced patterns (Level 5)")
        print("   5. Earn up to 1560 XP total!")

async def test_validation_system():
    """Test the code validation system with various scenarios."""
    print("\n🧪 Testing Code Validation System")
    print("=" * 40)
    
    validator = CodeValidationService()
    
    # Test cases
    test_scenarios = [
        {
            "name": "Correct FizzBuzz",
            "code": """def fizz_buzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)""",
            "test_cases": [{
                "input": "fizz_buzz(5)",
                "expected_output": "1\n2\nFizz\n4\nBuzz",
                "description": "FizzBuzz test"
            }]
        },
        {
            "name": "Syntax Error",
            "code": """def broken_function(n):
    for i in range(n)  # Missing colon
        print(i)""",
            "test_cases": [{
                "input": "broken_function(3)",
                "expected_output": "0\n1\n2",
                "description": "Basic test"
            }]
        },
        {
            "name": "Wrong Logic",
            "code": """def sum_numbers(n):
    total = 0
    for i in range(n):  # Should be range(1, n+1)
        total += i
    return total""",
            "test_cases": [{
                "input": "sum_numbers(5)",
                "expected_output": "15",
                "description": "Sum 1 to 5"
            }]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔍 Testing: {scenario['name']}")
        result = await validator.validate_code(scenario["code"], scenario["test_cases"])
        
        if result.execution_error:
            print(f"   ❌ Execution Error: {result.execution_error}")
        else:
            status = "✅ PASSED" if result.is_correct else "❌ FAILED"
            print(f"   Result: {status} ({result.passed_tests}/{result.total_tests})")
            
            for test in result.test_results:
                test_status = "✅" if test["passed"] else "❌"
                print(f"     {test_status} {test['description']}")
                if not test["passed"] and not result.execution_error:
                    print(f"       Expected: {repr(test['expected'])}")
                    print(f"       Got: {repr(test['actual'])}")

async def main():
    """Main demo function."""
    try:
        await demo_code_challenges()
        await test_validation_system()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Start the backend: python main.py")
        print("   2. Start the frontend: npm start")
        print("   3. Navigate to Python Loops lesson")
        print("   4. Try the new code challenges!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())