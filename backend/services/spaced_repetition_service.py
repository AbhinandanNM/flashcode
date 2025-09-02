from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from models import Question, QuestionAttempt, User, Progress
import schemas
from datetime import datetime, timezone, timedelta
import math


class SpacedRepetitionService:
    """
    Service for implementing spaced repetition using the SM-2 algorithm.
    
    The SM-2 algorithm calculates the next review interval based on:
    - Previous interval
    - Ease factor (difficulty of the item)
    - Quality of response (0-5 scale)
    """
    
    # SM-2 Algorithm constants
    MIN_EASE_FACTOR = 1.3
    INITIAL_EASE_FACTOR = 2.5
    INITIAL_INTERVAL = 1  # days
    
    @staticmethod
    def calculate_next_review(
        quality: int,
        repetition: int = 0,
        ease_factor: float = INITIAL_EASE_FACTOR,
        interval: int = INITIAL_INTERVAL
    ) -> Dict[str, Any]:
        """
        Calculate next review date using SM-2 algorithm.
        
        Args:
            quality: Quality of response (0-5)
                    0-2: incorrect response, reset interval
                    3: correct response with difficulty
                    4: correct response after hesitation
                    5: perfect response
            repetition: Number of consecutive correct responses
            ease_factor: Current ease factor for the item
            interval: Current interval in days
            
        Returns:
            Dict containing next_interval, ease_factor, repetition, next_review_date
        """
        if quality < 3:
            # Incorrect response - reset
            repetition = 0
            interval = 1
        else:
            # Correct response
            repetition += 1
            
            if repetition == 1:
                interval = 1
            elif repetition == 2:
                interval = 6
            else:
                interval = math.ceil(interval * ease_factor)
        
        # Update ease factor
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(ease_factor, SpacedRepetitionService.MIN_EASE_FACTOR)
        
        # Calculate next review date
        next_review_date = datetime.now(timezone.utc) + timedelta(days=interval)
        
        return {
            "next_interval": interval,
            "ease_factor": ease_factor,
            "repetition": repetition,
            "next_review_date": next_review_date
        }
    
    @staticmethod
    def convert_correctness_to_quality(is_correct: bool, time_taken: int, difficulty: int) -> int:
        """
        Convert answer correctness and performance metrics to SM-2 quality score.
        
        Args:
            is_correct: Whether the answer was correct
            time_taken: Time taken to answer (seconds)
            difficulty: Question difficulty (1-5)
            
        Returns:
            Quality score (0-5) for SM-2 algorithm
        """
        if not is_correct:
            return 1  # Incorrect answer
        
        # Base quality for correct answer
        quality = 3
        
        # Adjust based on time taken relative to difficulty
        # Expected time increases with difficulty
        expected_time = difficulty * 30  # 30 seconds per difficulty level
        
        if time_taken <= expected_time * 0.5:
            quality = 5  # Very fast, perfect response
        elif time_taken <= expected_time:
            quality = 4  # Fast response
        elif time_taken <= expected_time * 2:
            quality = 3  # Normal response
        else:
            quality = 3  # Slow but correct
        
        return quality
    
    @staticmethod
    def get_questions_due_for_review(
        db: Session,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get questions that are due for review for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of questions to return
            
        Returns:
            List of questions with review metadata
        """
        current_time = datetime.now(timezone.utc)
        
        # Query for questions that need review
        # This includes questions that:
        # 1. Have been answered incorrectly before
        # 2. Have a next_review date that has passed
        # 3. Haven't been reviewed recently
        
        # Get question attempts for incorrect answers or due for review
        subquery = db.query(QuestionAttempt.question_id).filter(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.is_correct == False
            )
        ).distinct().subquery()
        
        # Get progress records that are due for review
        progress_subquery = db.query(Progress.lesson_id).filter(
            and_(
                Progress.user_id == user_id,
                or_(
                    Progress.next_review <= current_time,
                    Progress.next_review.is_(None)
                )
            )
        ).subquery()
        
        # Get questions from lessons that need review or have incorrect attempts
        questions = db.query(Question).filter(
            or_(
                Question.id.in_(subquery),
                Question.lesson_id.in_(progress_subquery)
            )
        ).limit(limit).all()
        
        result = []
        for question in questions:
            # Get latest attempt for this question
            latest_attempt = db.query(QuestionAttempt).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.question_id == question.id
                )
            ).order_by(QuestionAttempt.created_at.desc()).first()
            
            # Get review metadata
            review_data = SpacedRepetitionService.get_question_review_data(
                db, user_id, question.id
            )
            
            result.append({
                "question": question,
                "latest_attempt": latest_attempt,
                "review_data": review_data,
                "is_due": review_data.get("next_review_date", current_time) <= current_time
            })
        
        # Sort by priority (due questions first, then by difficulty)
        result.sort(key=lambda x: (
            not x["is_due"],  # Due questions first
            x["question"].difficulty,  # Then by difficulty
            x["review_data"].get("repetition", 0)  # Then by repetition count
        ))
        
        return result
    
    @staticmethod
    def get_question_review_data(
        db: Session,
        user_id: int,
        question_id: int
    ) -> Dict[str, Any]:
        """
        Get review data for a specific question and user.
        
        Returns current spaced repetition state including:
        - repetition count
        - ease_factor
        - next_review_date
        - interval
        """
        # Get all attempts for this question by this user
        attempts = db.query(QuestionAttempt).filter(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.question_id == question_id
            )
        ).order_by(QuestionAttempt.created_at.asc()).all()
        
        if not attempts:
            return {
                "repetition": 0,
                "ease_factor": SpacedRepetitionService.INITIAL_EASE_FACTOR,
                "interval": SpacedRepetitionService.INITIAL_INTERVAL,
                "next_review_date": datetime.now(timezone.utc),
                "total_attempts": 0,
                "correct_attempts": 0,
                "success_rate": 0.0
            }
        
        # Calculate current state based on attempts
        repetition = 0
        ease_factor = SpacedRepetitionService.INITIAL_EASE_FACTOR
        interval = SpacedRepetitionService.INITIAL_INTERVAL
        
        # Count consecutive correct answers from the end
        for attempt in reversed(attempts):
            if attempt.is_correct:
                repetition += 1
            else:
                break
        
        # Get question for difficulty
        question = db.query(Question).filter(Question.id == question_id).first()
        difficulty = question.difficulty if question else 3
        
        # Calculate ease factor based on performance history
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        success_rate = correct_attempts / total_attempts if total_attempts > 0 else 0
        
        # Adjust ease factor based on success rate
        if success_rate >= 0.9:
            ease_factor = 2.8
        elif success_rate >= 0.7:
            ease_factor = 2.5
        elif success_rate >= 0.5:
            ease_factor = 2.2
        else:
            ease_factor = 1.8
        
        # Calculate interval based on repetition
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 1
        elif repetition == 2:
            interval = 6
        else:
            interval = math.ceil(interval * ease_factor)
        
        # Calculate next review date
        last_attempt_date = attempts[-1].created_at
        next_review_date = last_attempt_date + timedelta(days=interval)
        
        return {
            "repetition": repetition,
            "ease_factor": ease_factor,
            "interval": interval,
            "next_review_date": next_review_date,
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "success_rate": round(success_rate * 100, 2)
        }
    
    @staticmethod
    def update_review_schedule(
        db: Session,
        user_id: int,
        question_id: int,
        is_correct: bool,
        time_taken: int
    ) -> Dict[str, Any]:
        """
        Update the review schedule for a question based on user performance.
        
        Args:
            db: Database session
            user_id: User ID
            question_id: Question ID
            is_correct: Whether the answer was correct
            time_taken: Time taken to answer
            
        Returns:
            Updated review data
        """
        # Get question for difficulty
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return {}
        
        # Get current review data
        current_data = SpacedRepetitionService.get_question_review_data(
            db, user_id, question_id
        )
        
        # Convert performance to quality score
        quality = SpacedRepetitionService.convert_correctness_to_quality(
            is_correct, time_taken, question.difficulty
        )
        
        # Calculate next review using SM-2
        next_review_data = SpacedRepetitionService.calculate_next_review(
            quality=quality,
            repetition=current_data["repetition"],
            ease_factor=current_data["ease_factor"],
            interval=current_data["interval"]
        )
        
        # Update or create progress record for lesson
        progress = db.query(Progress).filter(
            and_(
                Progress.user_id == user_id,
                Progress.lesson_id == question.lesson_id
            )
        ).first()
        
        if progress:
            progress.last_reviewed = datetime.now(timezone.utc)
            progress.next_review = next_review_data["next_review_date"]
        else:
            # Create new progress record
            progress = Progress(
                user_id=user_id,
                lesson_id=question.lesson_id,
                status="in_progress",
                last_reviewed=datetime.now(timezone.utc),
                next_review=next_review_data["next_review_date"]
            )
            db.add(progress)
        
        db.commit()
        
        return {
            **next_review_data,
            "quality_score": quality,
            "question_id": question_id
        }
    
    @staticmethod
    def get_review_statistics(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get review statistics for a user.
        
        Returns:
            Statistics about the user's review performance
        """
        current_time = datetime.now(timezone.utc)
        
        # Count questions due for review
        due_questions = SpacedRepetitionService.get_questions_due_for_review(
            db, user_id, limit=1000
        )
        due_count = sum(1 for q in due_questions if q["is_due"])
        
        # Get all question attempts for the user
        attempts = db.query(QuestionAttempt).filter(
            QuestionAttempt.user_id == user_id
        ).all()
        
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        
        # Calculate average time per attempt
        avg_time = 0
        if attempts:
            total_time = sum(a.time_taken for a in attempts)
            avg_time = total_time / len(attempts)
        
        # Get attempts from last 7 days
        week_ago = current_time - timedelta(days=7)
        recent_attempts = [a for a in attempts if a.created_at >= week_ago]
        
        # Calculate streak (consecutive days with correct answers)
        streak = SpacedRepetitionService._calculate_review_streak(db, user_id)
        
        return {
            "total_questions_reviewed": len(set(a.question_id for a in attempts)),
            "questions_due_for_review": due_count,
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "success_rate": round((correct_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2),
            "average_time_seconds": round(avg_time, 2),
            "attempts_this_week": len(recent_attempts),
            "review_streak_days": streak
        }
    
    @staticmethod
    def _calculate_review_streak(db: Session, user_id: int) -> int:
        """
        Calculate the current review streak for a user.
        
        A streak is the number of consecutive days with at least one correct answer.
        """
        current_date = datetime.now(timezone.utc).date()
        streak = 0
        
        # Check each day going backwards
        for days_back in range(365):  # Check up to a year back
            check_date = current_date - timedelta(days=days_back)
            start_of_day = datetime.combine(check_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(check_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # Check if there were any correct attempts on this day
            correct_attempts = db.query(QuestionAttempt).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.is_correct == True,
                    QuestionAttempt.created_at >= start_of_day,
                    QuestionAttempt.created_at <= end_of_day
                )
            ).count()
            
            if correct_attempts > 0:
                streak += 1
            else:
                break
        
        return streak