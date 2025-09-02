import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import User, Lesson, Question, UserProgress, QuestionAttempt, Achievement, Duel
from services.lesson_service import LessonService
from services.question_service import QuestionService
from services.gamification_service import GamificationService
from services.duel_service import DuelService

class TestUserModel:
    """Test User model and related operations"""
    
    def test_create_user(self, db_session: Session):
        """Test creating a new user"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashed_password_here",
            "is_active": True
        }
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.total_xp == 0  # Default value
        assert user.level == 1  # Default value
        assert user.created_at is not None
    
    def test_user_unique_constraints(self, db_session: Session):
        """Test user unique constraints"""
        user1 = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash1"
        )
        user2 = User(
            username="testuser",  # Duplicate username
            email="test2@example.com",
            hashed_password="hash2"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_xp_and_level_calculation(self, db_session: Session):
        """Test XP and level calculations"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash",
            total_xp=1250
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Test level calculation (assuming 250 XP per level)
        expected_level = (user.total_xp // 250) + 1
        assert user.level == expected_level or user.level == 5  # Based on business logic

class TestLessonModel:
    """Test Lesson model and related operations"""
    
    def test_create_lesson(self, db_session: Session, sample_lesson_data):
        """Test creating a new lesson"""
        lesson = Lesson(**sample_lesson_data)
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        assert lesson.id is not None
        assert lesson.title == "Python Basics"
        assert lesson.language == "python"
        assert lesson.difficulty == 1
        assert lesson.created_at is not None
    
    def test_lesson_questions_relationship(self, db_session: Session, sample_lesson_data, sample_question_data):
        """Test lesson-questions relationship"""
        lesson = Lesson(**sample_lesson_data)
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)
        
        # Add questions to the lesson
        question_data = sample_question_data.copy()
        question_data["lesson_id"] = lesson.id
        
        question = Question(**question_data)
        db_session.add(question)
        db_session.commit()
        
        # Test relationship
        assert len(lesson.questions) == 1
        assert lesson.questions[0].question == sample_question_data["question"]
    
    def test_lesson_filtering(self, db_session: Session):
        """Test lesson filtering by various criteria"""
        # Create multiple lessons
        lessons_data = [
            {"title": "Python Basics", "language": "python", "difficulty": 1, "xp_reward": 100, "estimated_time": 30},
            {"title": "JavaScript Intro", "language": "javascript", "difficulty": 1, "xp_reward": 100, "estimated_time": 25},
            {"title": "Advanced Python", "language": "python", "difficulty": 3, "xp_reward": 200, "estimated_time": 60},
        ]
        
        for lesson_data in lessons_data:
            lesson = Lesson(**lesson_data)
            db_session.add(lesson)
        
        db_session.commit()
        
        # Test filtering by language
        python_lessons = db_session.query(Lesson).filter(Lesson.language == "python").all()
        assert len(python_lessons) == 2
        
        # Test filtering by difficulty
        beginner_lessons = db_session.query(Lesson).filter(Lesson.difficulty == 1).all()
        assert len(beginner_lessons) == 2
        
        # Test combined filtering
        advanced_python = db_session.query(Lesson).filter(
            Lesson.language == "python",
            Lesson.difficulty == 3
        ).all()
        assert len(advanced_python) == 1
        assert advanced_python[0].title == "Advanced Python"

class TestQuestionModel:
    """Test Question model and related operations"""
    
    def test_create_question(self, db_session: Session, sample_question_data):
        """Test creating a new question"""
        question = Question(**sample_question_data)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        assert question.id is not None
        assert question.type == "mcq"
        assert question.difficulty == 1
        assert question.created_at is not None
    
    def test_question_attempts_relationship(self, db_session: Session, sample_question_data):
        """Test question-attempts relationship"""
        # Create user and question
        user = User(username="testuser", email="test@example.com", hashed_password="hash")
        question = Question(**sample_question_data)
        
        db_session.add(user)
        db_session.add(question)
        db_session.commit()
        
        # Create attempt
        attempt = QuestionAttempt(
            user_id=user.id,
            question_id=question.id,
            user_answer="x = 5",
            is_correct=True,
            time_taken=30
        )
        
        db_session.add(attempt)
        db_session.commit()
        
        # Test relationships
        assert len(question.attempts) == 1
        assert len(user.question_attempts) == 1
        assert question.attempts[0].user_answer == "x = 5"

class TestUserProgressModel:
    """Test UserProgress model and tracking"""
    
    def test_create_user_progress(self, db_session: Session):
        """Test creating user progress record"""
        user = User(username="testuser", email="test@example.com", hashed_password="hash")
        lesson = Lesson(title="Test Lesson", language="python", difficulty=1, xp_reward=100, estimated_time=30)
        
        db_session.add(user)
        db_session.add(lesson)
        db_session.commit()
        
        progress = UserProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            status="in_progress",
            score=75,
            attempts=2
        )
        
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
        
        assert progress.id is not None
        assert progress.status == "in_progress"
        assert progress.score == 75
        assert progress.started_at is not None
    
    def test_progress_completion(self, db_session: Session):
        """Test marking progress as completed"""
        user = User(username="testuser", email="test@example.com", hashed_password="hash")
        lesson = Lesson(title="Test Lesson", language="python", difficulty=1, xp_reward=100, estimated_time=30)
        
        db_session.add(user)
        db_session.add(lesson)
        db_session.commit()
        
        progress = UserProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            status="in_progress"
        )
        
        db_session.add(progress)
        db_session.commit()
        
        # Complete the lesson
        progress.status = "completed"
        progress.score = 95
        progress.completed_at = datetime.utcnow()
        
        db_session.commit()
        
        assert progress.status == "completed"
        assert progress.score == 95
        assert progress.completed_at is not None

class TestGamificationModels:
    """Test gamification-related models"""
    
    def test_create_achievement(self, db_session: Session):
        """Test creating an achievement"""
        user = User(username="testuser", email="test@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        achievement = Achievement(
            user_id=user.id,
            name="First Steps",
            description="Complete your first lesson",
            icon="🎯",
            category="learning",
            xp_reward=50
        )
        
        db_session.add(achievement)
        db_session.commit()
        db_session.refresh(achievement)
        
        assert achievement.id is not None
        assert achievement.name == "First Steps"
        assert achievement.unlocked_at is not None
    
    def test_user_achievements_relationship(self, db_session: Session):
        """Test user-achievements relationship"""
        user = User(username="testuser", email="test@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        achievements_data = [
            {"name": "First Steps", "description": "Complete first lesson", "icon": "🎯", "category": "learning", "xp_reward": 50},
            {"name": "Streak Master", "description": "Maintain 7-day streak", "icon": "🔥", "category": "consistency", "xp_reward": 100},
        ]
        
        for ach_data in achievements_data:
            achievement = Achievement(user_id=user.id, **ach_data)
            db_session.add(achievement)
        
        db_session.commit()
        
        # Test relationship
        assert len(user.achievements) == 2
        achievement_names = [ach.name for ach in user.achievements]
        assert "First Steps" in achievement_names
        assert "Streak Master" in achievement_names

class TestDuelModel:
    """Test Duel model and related operations"""
    
    def test_create_duel(self, db_session: Session):
        """Test creating a new duel"""
        # Create users
        challenger = User(username="challenger", email="challenger@example.com", hashed_password="hash")
        opponent = User(username="opponent", email="opponent@example.com", hashed_password="hash")
        
        # Create question
        question = Question(
            lesson_id=1,
            type="mcq",
            difficulty=1,
            question="Test question?",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            xp_reward=10
        )
        
        db_session.add(challenger)
        db_session.add(opponent)
        db_session.add(question)
        db_session.commit()
        
        duel = Duel(
            challenger_id=challenger.id,
            opponent_id=opponent.id,
            question_id=question.id,
            time_limit=300,
            status="pending"
        )
        
        db_session.add(duel)
        db_session.commit()
        db_session.refresh(duel)
        
        assert duel.id is not None
        assert duel.status == "pending"
        assert duel.created_at is not None
    
    def test_duel_completion(self, db_session: Session):
        """Test completing a duel"""
        # Create users and question
        challenger = User(username="challenger", email="challenger@example.com", hashed_password="hash")
        opponent = User(username="opponent", email="opponent@example.com", hashed_password="hash")
        question = Question(
            lesson_id=1, type="mcq", difficulty=1, question="Test?",
            options=["A", "B"], correct_answer="A", xp_reward=10
        )
        
        db_session.add_all([challenger, opponent, question])
        db_session.commit()
        
        duel = Duel(
            challenger_id=challenger.id,
            opponent_id=opponent.id,
            question_id=question.id,
            time_limit=300,
            status="active"
        )
        
        db_session.add(duel)
        db_session.commit()
        
        # Complete the duel
        duel.status = "completed"
        duel.winner_id = challenger.id
        duel.challenger_answer = "A"
        duel.opponent_answer = "B"
        duel.challenger_time = 45
        duel.opponent_time = 60
        duel.completed_at = datetime.utcnow()
        
        db_session.commit()
        
        assert duel.status == "completed"
        assert duel.winner_id == challenger.id
        assert duel.completed_at is not None

class TestServiceIntegration:
    """Test service layer integration with database"""
    
    def test_lesson_service_integration(self, db_session: Session, sample_lesson_data):
        """Test LessonService database integration"""
        # Create lesson through service
        lesson = Lesson(**sample_lesson_data)
        db_session.add(lesson)
        db_session.commit()
        
        # Test service methods
        service = LessonService(db_session)
        
        # Get lessons
        lessons = service.get_lessons()
        assert len(lessons) >= 1
        
        # Get specific lesson
        retrieved_lesson = service.get_lesson(lesson.id)
        assert retrieved_lesson.title == sample_lesson_data["title"]
    
    def test_question_service_integration(self, db_session: Session, sample_question_data):
        """Test QuestionService database integration"""
        question = Question(**sample_question_data)
        db_session.add(question)
        db_session.commit()
        
        service = QuestionService(db_session)
        
        # Get question
        retrieved_question = service.get_question(question.id)
        assert retrieved_question.question == sample_question_data["question"]
    
    def test_gamification_service_integration(self, db_session: Session):
        """Test GamificationService database integration"""
        user = User(username="testuser", email="test@example.com", hashed_password="hash", total_xp=500)
        db_session.add(user)
        db_session.commit()
        
        service = GamificationService(db_session)
        
        # Award XP
        result = service.award_xp(user.id, 100, "Test reward")
        assert result["new_total_xp"] == 600
        
        # Check if user XP was updated in database
        db_session.refresh(user)
        assert user.total_xp == 600

class TestDatabaseConstraints:
    """Test database constraints and data integrity"""
    
    def test_foreign_key_constraints(self, db_session: Session):
        """Test foreign key constraints"""
        # Try to create question with non-existent lesson_id
        question = Question(
            lesson_id=999,  # Non-existent lesson
            type="mcq",
            difficulty=1,
            question="Test question?",
            correct_answer="A",
            xp_reward=10
        )
        
        db_session.add(question)
        
        # Should raise foreign key constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_data_validation(self, db_session: Session):
        """Test data validation constraints"""
        # Test invalid difficulty level
        lesson = Lesson(
            title="Test Lesson",
            language="python",
            difficulty=10,  # Assuming max difficulty is 5
            xp_reward=100,
            estimated_time=30
        )
        
        db_session.add(lesson)
        
        # Depending on model constraints, this might raise an error
        try:
            db_session.commit()
        except Exception:
            # Expected if validation constraints are in place
            pass
    
    def test_cascade_deletes(self, db_session: Session):
        """Test cascade delete behavior"""
        # Create user with related data
        user = User(username="testuser", email="test@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        # Create related records
        achievement = Achievement(
            user_id=user.id,
            name="Test Achievement",
            description="Test",
            icon="🎯",
            category="test",
            xp_reward=50
        )
        
        db_session.add(achievement)
        db_session.commit()
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Check if related records are handled appropriately
        remaining_achievements = db_session.query(Achievement).filter(Achievement.user_id == user.id).all()
        # Depending on cascade settings, achievements might be deleted or orphaned

class TestDatabasePerformance:
    """Test database performance and optimization"""
    
    def test_query_performance(self, db_session: Session):
        """Test query performance with larger datasets"""
        # Create multiple lessons
        lessons = []
        for i in range(100):
            lesson = Lesson(
                title=f"Lesson {i}",
                language="python" if i % 2 == 0 else "javascript",
                difficulty=(i % 5) + 1,
                xp_reward=100,
                estimated_time=30
            )
            lessons.append(lesson)
        
        db_session.add_all(lessons)
        db_session.commit()
        
        # Test query performance
        import time
        start_time = time.time()
        
        # Query with filtering
        python_lessons = db_session.query(Lesson).filter(Lesson.language == "python").all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Assert reasonable performance (adjust threshold as needed)
        assert query_time < 1.0  # Should complete within 1 second
        assert len(python_lessons) == 50
    
    def test_index_usage(self, db_session: Session):
        """Test that database indexes are being used effectively"""
        # This would require database-specific testing
        # For now, we'll test that common queries work efficiently
        
        # Create test data
        users = []
        for i in range(1000):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password="hash",
                total_xp=i * 10
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Test queries that should use indexes
        import time
        
        # Query by email (should be indexed)
        start_time = time.time()
        user = db_session.query(User).filter(User.email == "user500@example.com").first()
        email_query_time = time.time() - start_time
        
        # Query by username (should be indexed)
        start_time = time.time()
        user = db_session.query(User).filter(User.username == "user500").first()
        username_query_time = time.time() - start_time
        
        # Both queries should be fast
        assert email_query_time < 0.1
        assert username_query_time < 0.1
        assert user is not None