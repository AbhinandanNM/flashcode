"""
Simple test to verify database models work correctly
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Lesson, Question, Progress, QuestionAttempt, Duel
from models import LanguageEnum, QuestionTypeEnum, ProgressStatusEnum, DuelStatusEnum
import tempfile
import os

def test_models():
    """Test that all models can be created and relationships work"""
    # Create a temporary SQLite database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # Create test engine and session
        test_engine = create_engine(f"sqlite:///{temp_db.name}")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine)
        session = TestSession()
        
        # Test User model
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            xp=100,
            streak=5
        )
        session.add(user)
        session.commit()
        
        # Test Lesson model
        lesson = Lesson(
            language=LanguageEnum.PYTHON,
            title="Python Loops",
            theory="Learn about for and while loops in Python",
            difficulty=2,
            xp_reward=50,
            order_index=1
        )
        session.add(lesson)
        session.commit()
        
        # Test Question model
        question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.MCQ,
            question_text="What is a for loop?",
            options={"A": "A loop", "B": "Not a loop", "C": "Maybe", "D": "None"},
            correct_answer="A",
            explanation="A for loop is used for iteration",
            difficulty=1,
            xp_reward=10
        )
        session.add(question)
        session.commit()
        
        # Test Progress model
        progress = Progress(
            user_id=user.id,
            lesson_id=lesson.id,
            status=ProgressStatusEnum.IN_PROGRESS,
            score=0.8,
            attempts=2
        )
        session.add(progress)
        session.commit()
        
        # Test QuestionAttempt model
        attempt = QuestionAttempt(
            user_id=user.id,
            question_id=question.id,
            user_answer="A",
            is_correct=True,
            time_taken=30
        )
        session.add(attempt)
        session.commit()
        
        # Test Duel model
        duel = Duel(
            challenger_id=user.id,
            question_id=question.id,
            status=DuelStatusEnum.WAITING
        )
        session.add(duel)
        session.commit()
        
        # Test relationships
        assert len(user.progress) == 1
        assert len(user.question_attempts) == 1
        assert len(lesson.questions) == 1
        assert len(question.attempts) == 1
        
        print("✅ All models created successfully!")
        print(f"✅ User: {user.username} (XP: {user.xp}, Streak: {user.streak})")
        print(f"✅ Lesson: {lesson.title} (Language: {lesson.language.value})")
        print(f"✅ Question: {question.type.value} - {question.question_text}")
        print(f"✅ Progress: {progress.status.value} (Score: {progress.score})")
        print(f"✅ Attempt: {'Correct' if attempt.is_correct else 'Incorrect'} in {attempt.time_taken}s")
        print(f"✅ Duel: {duel.status.value}")
        print("✅ All relationships working correctly!")
        
        session.close()
        
    finally:
        # Clean up temporary database
        os.unlink(temp_db.name)

if __name__ == "__main__":
    test_models()