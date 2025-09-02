from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from models import User, Progress, QuestionAttempt, Lesson, Question
from schemas import UserResponse
import logging

logger = logging.getLogger(__name__)


class GamificationService:
    """Service for handling gamification features including XP, streaks, and leaderboards."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_lesson_xp(self, lesson: Lesson, completion_score: float) -> int:
        """
        Calculate XP reward for completing a lesson based on difficulty and score.
        
        Args:
            lesson: The lesson that was completed
            completion_score: Score from 0.0 to 1.0 representing completion quality
            
        Returns:
            XP points to award
        """
        base_xp = lesson.xp_reward
        
        # Apply score multiplier (minimum 50% XP for completion)
        score_multiplier = max(0.5, completion_score)
        
        # Apply difficulty bonus (higher difficulty = more XP)
        difficulty_bonus = 1.0 + (lesson.difficulty - 1) * 0.2  # 20% bonus per difficulty level
        
        total_xp = int(base_xp * score_multiplier * difficulty_bonus)
        
        logger.info(f"Calculated lesson XP: base={base_xp}, score={completion_score}, "
                   f"difficulty_bonus={difficulty_bonus}, total={total_xp}")
        
        return total_xp
    
    def calculate_question_xp(self, question: Question, is_correct: bool, time_taken: int) -> int:
        """
        Calculate XP reward for answering a question.
        
        Args:
            question: The question that was answered
            is_correct: Whether the answer was correct
            time_taken: Time taken to answer in seconds
            
        Returns:
            XP points to award
        """
        if not is_correct:
            return 0
        
        base_xp = question.xp_reward
        
        # Apply difficulty bonus
        difficulty_bonus = 1.0 + (question.difficulty - 1) * 0.15  # 15% bonus per difficulty level
        
        # Apply speed bonus (faster answers get more XP, up to 50% bonus)
        # Assume optimal time is 30 seconds for most questions
        optimal_time = 30
        if time_taken > 0 and time_taken <= optimal_time:
            speed_bonus = 1.0 + (optimal_time - time_taken) / optimal_time * 0.5
        else:
            speed_bonus = 1.0
        
        total_xp = int(base_xp * difficulty_bonus * speed_bonus)
        
        logger.info(f"Calculated question XP: base={base_xp}, difficulty_bonus={difficulty_bonus}, "
                   f"speed_bonus={speed_bonus}, total={total_xp}")
        
        return total_xp
    
    def award_xp(self, user_id: int, xp_amount: int, source: str = "unknown") -> bool:
        """
        Award XP to a user and update their total.
        
        Args:
            user_id: ID of the user to award XP to
            xp_amount: Amount of XP to award
            source: Source of the XP (for logging)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found for XP award")
                return False
            
            old_xp = user.xp
            user.xp += xp_amount
            self.db.commit()
            
            logger.info(f"Awarded {xp_amount} XP to user {user_id} from {source}. "
                       f"Total XP: {old_xp} -> {user.xp}")
            
            return True
        except Exception as e:
            logger.error(f"Error awarding XP to user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def update_user_activity(self, user_id: int) -> Dict[str, Any]:
        """
        Update user's last activity and streak.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with streak information
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found for activity update")
                return {"error": "User not found"}
            
            now = datetime.now(timezone.utc)
            last_activity = user.last_activity
            
            # Convert to UTC if timezone-naive
            if last_activity and last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=timezone.utc)
            
            streak_info = self._calculate_streak(last_activity, now, user.streak)
            
            # Update user
            user.last_activity = now
            user.streak = streak_info["new_streak"]
            self.db.commit()
            
            logger.info(f"Updated activity for user {user_id}: streak {user.streak}")
            
            return {
                "user_id": user_id,
                "new_streak": streak_info["new_streak"],
                "streak_maintained": streak_info["streak_maintained"],
                "streak_broken": streak_info["streak_broken"],
                "last_activity": now
            }
        except Exception as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _calculate_streak(self, last_activity: Optional[datetime], current_time: datetime, 
                         current_streak: int) -> Dict[str, Any]:
        """
        Calculate new streak based on last activity.
        
        Args:
            last_activity: User's last activity timestamp
            current_time: Current timestamp
            current_streak: User's current streak
            
        Returns:
            Dictionary with streak calculation results
        """
        if not last_activity:
            # First activity ever
            return {
                "new_streak": 1,
                "streak_maintained": True,
                "streak_broken": False
            }
        
        # Calculate days since last activity
        time_diff = current_time - last_activity
        days_since_activity = time_diff.days
        
        if days_since_activity == 0:
            # Same day activity - maintain streak
            return {
                "new_streak": current_streak,
                "streak_maintained": True,
                "streak_broken": False
            }
        elif days_since_activity == 1:
            # Next day activity - increment streak
            return {
                "new_streak": current_streak + 1,
                "streak_maintained": True,
                "streak_broken": False
            }
        else:
            # More than 1 day gap - reset streak
            return {
                "new_streak": 1,
                "streak_maintained": False,
                "streak_broken": True
            }
    
    def get_weekly_leaderboard(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get weekly leaderboard based on total XP.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of user leaderboard entries
        """
        try:
            # Get users ordered by XP (descending)
            users = (
                self.db.query(User)
                .filter(User.is_active == True)
                .order_by(desc(User.xp))
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            leaderboard = []
            for rank, user in enumerate(users, start=offset + 1):
                leaderboard.append({
                    "rank": rank,
                    "user_id": user.id,
                    "username": user.username,
                    "xp": user.xp,
                    "streak": user.streak,
                    "joined_on": user.joined_on
                })
            
            logger.info(f"Generated leaderboard with {len(leaderboard)} users")
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            return []
    
    def get_user_rank(self, user_id: int) -> Optional[int]:
        """
        Get a user's current rank on the leaderboard.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User's rank (1-based) or None if not found
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Count users with higher XP
            higher_xp_count = (
                self.db.query(User)
                .filter(and_(User.xp > user.xp, User.is_active == True))
                .count()
            )
            
            return higher_xp_count + 1
            
        except Exception as e:
            logger.error(f"Error getting user rank for {user_id}: {e}")
            return None
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive gamification stats for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with user's gamification statistics
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Get total lessons completed
            completed_lessons = (
                self.db.query(Progress)
                .filter(and_(
                    Progress.user_id == user_id,
                    Progress.status == "completed"
                ))
                .count()
            )
            
            # Get total questions answered
            total_attempts = (
                self.db.query(QuestionAttempt)
                .filter(QuestionAttempt.user_id == user_id)
                .count()
            )
            
            # Get correct answers
            correct_attempts = (
                self.db.query(QuestionAttempt)
                .filter(and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.is_correct == True
                ))
                .count()
            )
            
            # Calculate accuracy
            accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # Get user's rank
            rank = self.get_user_rank(user_id)
            
            return {
                "user_id": user_id,
                "username": user.username,
                "xp": user.xp,
                "streak": user.streak,
                "rank": rank,
                "completed_lessons": completed_lessons,
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "accuracy": round(accuracy, 2),
                "joined_on": user.joined_on,
                "last_activity": user.last_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {"error": str(e)}
    
    def award_lesson_completion_xp(self, user_id: int, lesson_id: int, score: float) -> int:
        """
        Award XP for lesson completion and update user activity.
        
        Args:
            user_id: ID of the user
            lesson_id: ID of the completed lesson
            score: Completion score (0.0 to 1.0)
            
        Returns:
            XP awarded
        """
        try:
            lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson:
                logger.error(f"Lesson {lesson_id} not found")
                return 0
            
            xp_amount = self.calculate_lesson_xp(lesson, score)
            
            if self.award_xp(user_id, xp_amount, f"lesson_completion_{lesson_id}"):
                self.update_user_activity(user_id)
                return xp_amount
            
            return 0
            
        except Exception as e:
            logger.error(f"Error awarding lesson completion XP: {e}")
            return 0
    
    def award_question_xp(self, user_id: int, question_id: int, is_correct: bool, 
                         time_taken: int) -> int:
        """
        Award XP for answering a question and update user activity.
        
        Args:
            user_id: ID of the user
            question_id: ID of the answered question
            is_correct: Whether the answer was correct
            time_taken: Time taken to answer in seconds
            
        Returns:
            XP awarded
        """
        try:
            question = self.db.query(Question).filter(Question.id == question_id).first()
            if not question:
                logger.error(f"Question {question_id} not found")
                return 0
            
            xp_amount = self.calculate_question_xp(question, is_correct, time_taken)
            
            if xp_amount > 0 and self.award_xp(user_id, xp_amount, f"question_{question_id}"):
                self.update_user_activity(user_id)
                return xp_amount
            
            return 0
            
        except Exception as e:
            logger.error(f"Error awarding question XP: {e}")
            return 0