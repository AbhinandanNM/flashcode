#!/usr/bin/env python3
"""
Script to populate the database with the Python Loops sample lesson.
This creates a complete lesson that demonstrates the full CodeCrafts learning flow.
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
from lesson_content.python_loops_content import LESSON_DATA, QUESTIONS_DATA, get_lesson_summary

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./codecrafts.db"

async def populate_lesson():
    """Populate the database with the Python Loops lesson."""
    
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Check if lesson already exists
        result = await session.execute(
            select(Lesson).where(Lesson.title == LESSON_DATA["title"])
        )
        existing_lesson = result.scalar_one_or_none()
        
        if existing_lesson:
            print(f"⚠️  Lesson '{LESSON_DATA['title']}' already exists (ID: {existing_lesson.id})")
            print("Would you like to update it? (y/n): ", end="")
            
            # For automation, we'll skip the input and just update
            choice = "y"  # input().lower()
            
            if choice == "y":
                # Update existing lesson
                for key, value in LESSON_DATA.items():
                    if key != "created_at":  # Don't update creation time
                        setattr(existing_lesson, key, value)
                
                # Delete existing questions
                await session.execute(
                    select(Question).where(Question.lesson_id == existing_lesson.id)
                )
                existing_questions = (await session.execute(
                    select(Question).where(Question.lesson_id == existing_lesson.id)
                )).scalars().all()
                
                for question in existing_questions:
                    await session.delete(question)
                
                lesson = existing_lesson
                print(f"📝 Updated existing lesson")
            else:
                print("❌ Skipping lesson creation")
                return
        else:
            # Create new lesson
            lesson = Lesson(
                **LESSON_DATA,
                created_at=datetime.utcnow()
            )
            session.add(lesson)
            await session.flush()  # Get the lesson ID
            print(f"✅ Created new lesson: {lesson.title}")
        
        # Create questions
        questions_created = 0
        for question_data in QUESTIONS_DATA:
            question = Question(
                lesson_id=lesson.id,
                **question_data
            )
            session.add(question)
            questions_created += 1
        
        # Commit all changes
        await session.commit()
        
        print(f"✅ Successfully populated lesson with {questions_created} questions!")
        print(f"📚 Lesson ID: {lesson.id}")
        
        # Print summary
        summary = get_lesson_summary()
        print(f"\n📊 Lesson Summary:")
        print(f"  - Title: {summary['lesson_title']}")
        print(f"  - Total Questions: {summary['total_questions']}")
        print(f"  - Total XP Available: {summary['total_xp']}")
        print(f"  - Difficulty Range: {summary['difficulty_range']}")
        print(f"\n🎯 Question Types:")
        for q_type, count in summary['question_types'].items():
            print(f"  - {q_type.upper()}: {count} questions")

async def verify_lesson():
    """Verify that the lesson was created correctly."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get the lesson
        result = await session.execute(
            select(Lesson).where(Lesson.title == LESSON_DATA["title"])
        )
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            print("❌ Lesson not found!")
            return False
        
        # Get questions
        result = await session.execute(
            select(Question).where(Question.lesson_id == lesson.id)
        )
        questions = result.scalars().all()
        
        print(f"\n🔍 Verification Results:")
        print(f"  - Lesson found: ✅ {lesson.title}")
        print(f"  - Questions found: ✅ {len(questions)}")
        print(f"  - Expected questions: {len(QUESTIONS_DATA)}")
        
        if len(questions) == len(QUESTIONS_DATA):
            print("  - Question count matches: ✅")
        else:
            print("  - Question count mismatch: ❌")
            return False
        
        # Verify question types
        question_types = {}
        for question in questions:
            question_types[question.type] = question_types.get(question.type, 0) + 1
        
        expected_types = {}
        for q_data in QUESTIONS_DATA:
            expected_types[q_data["type"]] = expected_types.get(q_data["type"], 0) + 1
        
        print(f"  - Question types:")
        for q_type, count in question_types.items():
            expected_count = expected_types.get(q_type, 0)
            status = "✅" if count == expected_count else "❌"
            print(f"    - {q_type}: {count}/{expected_count} {status}")
        
        return True

async def main():
    """Main function to populate and verify the lesson."""
    try:
        print("🚀 Starting lesson population...")
        await populate_lesson()
        
        print("\n🔍 Verifying lesson creation...")
        success = await verify_lesson()
        
        if success:
            print("\n🎉 Python Loops lesson successfully created and verified!")
            print("\n📋 Next Steps:")
            print("  1. Start the backend server: python main.py")
            print("  2. Start the frontend: npm start")
            print("  3. Navigate to /lessons to see the new lesson")
            print("  4. Test the complete learning flow!")
        else:
            print("\n❌ Verification failed. Please check the database.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())