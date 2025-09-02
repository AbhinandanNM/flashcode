#!/usr/bin/env python3
"""
Script to add advanced Python Loops code challenges to the database.
This extends the existing lesson with more complex coding exercises.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Base, Lesson, Question
from lesson_content.python_loops_challenges import get_all_challenges, get_challenges_summary

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./codecrafts.db"

async def add_code_challenges():
    """Add advanced code challenges to the Python Loops lesson."""
    
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Find the Python Loops lesson
        result = await session.execute(
            select(Lesson).where(Lesson.title == "Python Loops: For and While")
        )
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            print("❌ Python Loops lesson not found!")
            print("Please run populate_sample_lesson.py first to create the base lesson.")
            return
        
        print(f"📚 Found lesson: {lesson.title} (ID: {lesson.id})")
        
        # Get all challenges
        challenges = get_all_challenges()
        summary = get_challenges_summary()
        
        print(f"🚀 Adding {summary['total_challenges']} advanced code challenges...")
        
        # Add each challenge as a question
        added_count = 0
        for challenge in challenges:
            # Check if question already exists (by question text)
            existing = await session.execute(
                select(Question).where(
                    Question.lesson_id == lesson.id,
                    Question.question_text == challenge['question_text']
                )
            )
            
            if existing.scalar_one_or_none():
                print(f"⚠️  Skipping duplicate challenge: {challenge.get('title', 'Untitled')}")
                continue
            
            # Prepare test cases as JSON if they exist
            options = None
            if 'test_cases' in challenge:
                options = json.dumps(challenge['test_cases'])
            
            # Create the question
            question = Question(
                lesson_id=lesson.id,
                type=challenge['type'],
                question_text=challenge['question_text'],
                options=options,  # Store test cases in options field
                correct_answer=challenge['correct_answer'],
                explanation=challenge.get('explanation', ''),
                difficulty=challenge.get('difficulty', 3),
                xp_reward=challenge.get('xp_reward', 50)
            )
            
            session.add(question)
            added_count += 1
            
            # Print progress
            title = challenge.get('title', f"Challenge {added_count}")
            difficulty_name = ["", "Beginner", "Easy", "Medium", "Hard", "Expert"][challenge.get('difficulty', 3)]
            print(f"  ✅ Added: {title} (Level {challenge.get('difficulty', 3)} - {difficulty_name}, {challenge.get('xp_reward', 50)} XP)")
        
        # Commit all changes
        await session.commit()
        
        print(f"\n🎉 Successfully added {added_count} code challenges!")
        
        # Update lesson XP reward to reflect new content
        total_lesson_xp = lesson.xp_reward + sum(c.get('xp_reward', 0) for c in challenges)
        print(f"📊 Updated lesson total XP potential: {total_lesson_xp}")
        
        # Print final summary
        print(f"\n📈 Challenge Summary:")
        print(f"  - Advanced Challenges: {summary['categories']['advanced']}")
        print(f"  - Debugging Exercises: {summary['categories']['debugging']}")
        print(f"  - Progressive Exercises: {summary['categories']['progressive']}")
        print(f"  - Total XP from Challenges: {summary['total_xp']}")
        
        print(f"\n🎯 Difficulty Distribution:")
        for difficulty, count in sorted(summary['difficulty_distribution'].items()):
            level_name = ["", "Beginner", "Easy", "Medium", "Hard", "Expert"][difficulty]
            print(f"  - Level {difficulty} ({level_name}): {count} challenges")

async def verify_challenges():
    """Verify that the challenges were added correctly."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get the lesson
        result = await session.execute(
            select(Lesson).where(Lesson.title == "Python Loops: For and While")
        )
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            print("❌ Lesson not found!")
            return False
        
        # Get all questions for this lesson
        result = await session.execute(
            select(Question).where(Question.lesson_id == lesson.id)
        )
        questions = result.scalars().all()
        
        # Count by type and difficulty
        type_counts = {}
        difficulty_counts = {}
        total_xp = lesson.xp_reward
        
        for question in questions:
            type_counts[question.type] = type_counts.get(question.type, 0) + 1
            difficulty_counts[question.difficulty] = difficulty_counts.get(question.difficulty, 0) + 1
            total_xp += question.xp_reward
        
        print(f"\n🔍 Verification Results:")
        print(f"  - Lesson: {lesson.title}")
        print(f"  - Total Questions: {len(questions)}")
        print(f"  - Total XP Available: {total_xp}")
        
        print(f"\n📊 Question Types:")
        for q_type, count in type_counts.items():
            print(f"  - {q_type.upper()}: {count}")
        
        print(f"\n🎯 Difficulty Levels:")
        for difficulty, count in sorted(difficulty_counts.items()):
            level_name = ["", "Beginner", "Easy", "Medium", "Hard", "Expert"][difficulty]
            print(f"  - Level {difficulty} ({level_name}): {count}")
        
        # Check for code challenges specifically
        code_questions = [q for q in questions if q.type == 'code']
        print(f"\n💻 Code Challenges: {len(code_questions)}")
        
        # Show some examples
        if code_questions:
            print(f"  Examples:")
            for i, question in enumerate(code_questions[:3], 1):
                title = question.question_text.split('\n')[0][:50] + "..."
                print(f"    {i}. {title} ({question.xp_reward} XP)")
        
        return True

async def main():
    """Main function to add and verify code challenges."""
    try:
        print("🚀 Adding Python Loops Code Challenges")
        print("=" * 45)
        
        await add_code_challenges()
        
        print("\n🔍 Verifying challenges...")
        success = await verify_challenges()
        
        if success:
            print("\n🎉 Code challenges successfully added and verified!")
            print("\n📋 What's New:")
            print("  - 🧩 Advanced algorithm challenges (FizzBuzz, Primes, Fibonacci)")
            print("  - 🐛 Debugging exercises with common loop errors")
            print("  - 📈 Progressive difficulty from beginner to expert")
            print("  - 🧪 Test cases for automated validation")
            print("  - 🏆 Higher XP rewards for complex challenges")
            
            print("\n🎮 Try These Features:")
            print("  1. Navigate to the Python Loops lesson")
            print("  2. Complete the theory and basic questions")
            print("  3. Challenge yourself with advanced coding exercises")
            print("  4. Debug broken code to learn common pitfalls")
            print("  5. Progress from simple loops to complex algorithms")
        else:
            print("\n❌ Verification failed. Please check the database.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())