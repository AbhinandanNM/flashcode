#!/usr/bin/env python3
"""
Demo script to showcase the complete CodeCrafts learning flow.
This demonstrates how a user would progress through the Python Loops lesson.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Base, User, Lesson, Question, Progress, QuestionAttempt

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./codecrafts.db"

async def create_demo_user():
    """Create a demo user for testing the learning flow."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if demo user exists
        result = await session.execute(
            select(User).where(User.username == "demo_learner")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                username="demo_learner",
                email="demo@codecrafts.com",
                password_hash="demo_hash",  # In real app, this would be properly hashed
                xp=0,
                streak=0,
                last_activity=datetime.utcnow(),
                joined_on=datetime.utcnow()
            )
            session.add(user)
            await session.commit()
            print(f"✅ Created demo user: {user.username}")
        else:
            print(f"👤 Using existing demo user: {user.username}")
        
        return user

async def simulate_learning_flow():
    """Simulate a complete learning flow through the Python Loops lesson."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get demo user
        user = await create_demo_user()
        
        # Get the Python Loops lesson
        result = await session.execute(
            select(Lesson).where(Lesson.title == "Python Loops: For and While")
        )
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            print("❌ Python Loops lesson not found! Please run populate_sample_lesson.py first.")
            return
        
        print(f"\n📚 Starting learning flow for: {lesson.title}")
        print(f"👤 User: {user.username}")
        print(f"🎯 Lesson XP Reward: {lesson.xp_reward}")
        
        # Step 1: Create lesson progress
        progress = Progress(
            user_id=user.id,
            lesson_id=lesson.id,
            status="in_progress",
            score=0.0,
            attempts=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(progress)
        await session.flush()
        
        print(f"\n📖 Step 1: Started lesson (Progress ID: {progress.id})")
        
        # Step 2: Get lesson questions
        result = await session.execute(
            select(Question).where(Question.lesson_id == lesson.id).order_by(Question.id)
        )
        questions = result.scalars().all()
        
        print(f"❓ Step 2: Found {len(questions)} practice questions")
        
        # Step 3: Simulate answering questions
        correct_answers = 0
        total_xp_earned = 0
        
        for i, question in enumerate(questions, 1):
            # Simulate different success rates based on question difficulty
            success_rate = {1: 0.9, 2: 0.8, 3: 0.7, 4: 0.6, 5: 0.5}
            is_correct = __import__('random').random() < success_rate.get(question.difficulty, 0.7)
            
            # Create question attempt
            attempt = QuestionAttempt(
                user_id=user.id,
                question_id=question.id,
                user_answer="simulated_answer",
                is_correct=is_correct,
                time_taken=__import__('random').randint(10, 120),  # 10-120 seconds
                created_at=datetime.utcnow()
            )
            session.add(attempt)
            
            if is_correct:
                correct_answers += 1
                total_xp_earned += question.xp_reward
            
            status = "✅" if is_correct else "❌"
            print(f"  {status} Question {i} ({question.type}): {question.xp_reward} XP")
        
        # Step 4: Update progress and user XP
        final_score = correct_answers / len(questions)
        progress.score = final_score
        progress.status = "completed" if final_score >= 0.7 else "in_progress"
        progress.updated_at = datetime.utcnow()
        
        # Award lesson XP if completed
        if progress.status == "completed":
            total_xp_earned += lesson.xp_reward
        
        # Update user stats
        user.xp += total_xp_earned
        user.streak += 1  # Assume daily activity
        user.last_activity = datetime.utcnow()
        
        await session.commit()
        
        # Step 5: Display results
        print(f"\n🎉 Learning Flow Complete!")
        print(f"📊 Results Summary:")
        print(f"  - Questions Answered: {len(questions)}")
        print(f"  - Correct Answers: {correct_answers}")
        print(f"  - Success Rate: {final_score:.1%}")
        print(f"  - Lesson Status: {progress.status.title()}")
        print(f"  - XP Earned: {total_xp_earned}")
        print(f"  - User Total XP: {user.xp}")
        print(f"  - Current Streak: {user.streak}")
        
        # Step 6: Simulate spaced repetition scheduling
        print(f"\n🧠 Spaced Repetition Scheduling:")
        incorrect_questions = []
        for attempt in await session.execute(
            select(QuestionAttempt).where(
                QuestionAttempt.user_id == user.id,
                QuestionAttempt.is_correct == False
            )
        ):
            incorrect_questions.extend(attempt.scalars().all())
        
        if incorrect_questions:
            print(f"  - {len(incorrect_questions)} questions scheduled for review")
            for attempt in incorrect_questions:
                # Schedule for review (simplified SM-2 algorithm)
                next_review = datetime.utcnow() + timedelta(minutes=10)  # Review in 10 minutes
                progress.next_review = next_review
                print(f"    - Question {attempt.question_id}: Review at {next_review.strftime('%H:%M')}")
        else:
            print(f"  - All questions answered correctly! No immediate review needed.")
        
        await session.commit()
        
        return {
            "user": user,
            "lesson": lesson,
            "progress": progress,
            "total_questions": len(questions),
            "correct_answers": correct_answers,
            "xp_earned": total_xp_earned,
            "final_score": final_score
        }

async def generate_learning_report(results):
    """Generate a detailed learning report."""
    print(f"\n📋 Detailed Learning Report")
    print("=" * 50)
    print(f"Student: {results['user'].username}")
    print(f"Lesson: {results['lesson'].title}")
    print(f"Completion Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print(f"📈 Performance Metrics:")
    print(f"  - Questions Attempted: {results['total_questions']}")
    print(f"  - Correct Answers: {results['correct_answers']}")
    print(f"  - Accuracy: {results['final_score']:.1%}")
    print(f"  - Status: {results['progress'].status.title()}")
    print()
    
    print(f"🏆 Rewards Earned:")
    print(f"  - XP from Questions: {results['xp_earned'] - (results['lesson'].xp_reward if results['progress'].status == 'completed' else 0)}")
    if results['progress'].status == 'completed':
        print(f"  - Lesson Completion Bonus: {results['lesson'].xp_reward}")
    print(f"  - Total XP Earned: {results['xp_earned']}")
    print(f"  - New Total XP: {results['user'].xp}")
    print()
    
    print(f"🎯 Recommendations:")
    if results['final_score'] >= 0.9:
        print("  - Excellent work! You've mastered this topic.")
        print("  - Ready to move on to the next lesson.")
    elif results['final_score'] >= 0.7:
        print("  - Good job! You understand the basics.")
        print("  - Review the missed questions to strengthen your knowledge.")
    else:
        print("  - Keep practicing! Review the lesson theory.")
        print("  - Focus on the questions you missed.")
    
    print()
    print(f"🔄 Next Steps:")
    print("  - Review flashcards for long-term retention")
    print("  - Try coding challenges to apply your knowledge")
    print("  - Challenge friends to a coding duel!")

async def main():
    """Main function to run the learning flow demo."""
    try:
        print("🚀 CodeCrafts Learning Flow Demo")
        print("=" * 40)
        
        results = await simulate_learning_flow()
        await generate_learning_report(results)
        
        print(f"\n✨ Demo completed successfully!")
        print(f"💡 This demonstrates the complete CodeCrafts learning experience:")
        print(f"   1. 📚 Read theory content")
        print(f"   2. ❓ Answer practice questions")
        print(f"   3. 🏆 Earn XP and track progress")
        print(f"   4. 🧠 Schedule spaced repetition")
        print(f"   5. 📊 View detailed analytics")
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())