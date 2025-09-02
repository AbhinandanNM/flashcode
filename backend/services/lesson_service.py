from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from models import Lesson, Progress, User, LanguageEnum, ProgressStatusEnum
import schemas
from datetime import datetime, timezone


class LessonService:
    
    @staticmethod
    def create_lesson(db: Session, lesson_data: schemas.LessonCreate) -> Lesson:
        """Create a new lesson"""
        db_lesson = Lesson(
            language=lesson_data.language,
            title=lesson_data.title,
            theory=lesson_data.theory,
            difficulty=lesson_data.difficulty,
            xp_reward=lesson_data.xp_reward,
            order_index=lesson_data.order_index,
            is_published=lesson_data.is_published
        )
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    
    @staticmethod
    def get_lesson_by_id(db: Session, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by ID"""
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    @staticmethod
    def get_lessons(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        language: Optional[LanguageEnum] = None,
        difficulty: Optional[int] = None,
        is_published: bool = True
    ) -> List[Lesson]:
        """Get lessons with optional filtering"""
        query = db.query(Lesson)
        
        # Apply filters
        if language:
            query = query.filter(Lesson.language == language)
        if difficulty:
            query = query.filter(Lesson.difficulty == difficulty)
        if is_published is not None:
            query = query.filter(Lesson.is_published == is_published)
        
        # Order by order_index and created_at
        query = query.order_by(Lesson.order_index, Lesson.created_at)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_lessons_with_progress(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        language: Optional[LanguageEnum] = None,
        difficulty: Optional[int] = None,
        is_published: bool = True
    ) -> List[dict]:
        """Get lessons with user progress information"""
        query = db.query(Lesson).outerjoin(
            Progress, 
            and_(Progress.lesson_id == Lesson.id, Progress.user_id == user_id)
        )
        
        # Apply filters
        if language:
            query = query.filter(Lesson.language == language)
        if difficulty:
            query = query.filter(Lesson.difficulty == difficulty)
        if is_published is not None:
            query = query.filter(Lesson.is_published == is_published)
        
        # Order by order_index and created_at
        query = query.order_by(Lesson.order_index, Lesson.created_at)
        
        results = query.offset(skip).limit(limit).all()
        
        # Format results with progress
        lessons_with_progress = []
        for lesson in results:
            lesson_dict = {
                "id": lesson.id,
                "language": lesson.language,
                "title": lesson.title,
                "difficulty": lesson.difficulty,
                "xp_reward": lesson.xp_reward,
                "order_index": lesson.order_index,
                "is_published": lesson.is_published,
                "created_at": lesson.created_at,
                "progress": None
            }
            
            # Get progress for this lesson and user
            progress = db.query(Progress).filter(
                and_(Progress.lesson_id == lesson.id, Progress.user_id == user_id)
            ).first()
            
            if progress:
                lesson_dict["progress"] = {
                    "id": progress.id,
                    "user_id": progress.user_id,
                    "lesson_id": progress.lesson_id,
                    "status": progress.status,
                    "score": progress.score,
                    "attempts": progress.attempts,
                    "last_reviewed": progress.last_reviewed,
                    "next_review": progress.next_review,
                    "created_at": progress.created_at,
                    "updated_at": progress.updated_at
                }
            
            lessons_with_progress.append(lesson_dict)
        
        return lessons_with_progress
    
    @staticmethod
    def update_lesson(
        db: Session, 
        lesson_id: int, 
        lesson_data: schemas.LessonUpdate
    ) -> Optional[Lesson]:
        """Update a lesson"""
        db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not db_lesson:
            return None
        
        update_data = lesson_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lesson, field, value)
        
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    
    @staticmethod
    def delete_lesson(db: Session, lesson_id: int) -> bool:
        """Delete a lesson"""
        db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not db_lesson:
            return False
        
        db.delete(db_lesson)
        db.commit()
        return True
    
    @staticmethod
    def get_user_progress(db: Session, user_id: int, lesson_id: int) -> Optional[Progress]:
        """Get user progress for a specific lesson"""
        return db.query(Progress).filter(
            and_(Progress.user_id == user_id, Progress.lesson_id == lesson_id)
        ).first()
    
    @staticmethod
    def create_or_update_progress(
        db: Session,
        user_id: int,
        lesson_id: int,
        progress_data: schemas.ProgressUpdate
    ) -> Progress:
        """Create or update user progress for a lesson"""
        # Check if progress already exists
        existing_progress = db.query(Progress).filter(
            and_(Progress.user_id == user_id, Progress.lesson_id == lesson_id)
        ).first()
        
        if existing_progress:
            # Update existing progress
            update_data = progress_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_progress, field, value)
            
            existing_progress.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_progress)
            return existing_progress
        else:
            # Create new progress
            db_progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                status=progress_data.status or ProgressStatusEnum.NOT_STARTED,
                score=progress_data.score or 0.0,
                attempts=progress_data.attempts or 0
            )
            db.add(db_progress)
            db.commit()
            db.refresh(db_progress)
            return db_progress
    
    @staticmethod
    def get_user_all_progress(
        db: Session, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Progress]:
        """Get all progress for a user"""
        return db.query(Progress).filter(Progress.user_id == user_id)\
            .order_by(Progress.updated_at.desc())\
            .offset(skip).limit(limit).all()
    
    @staticmethod
    def get_lesson_statistics(db: Session, lesson_id: int) -> dict:
        """Get statistics for a lesson"""
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            return {}
        
        # Count total users who started this lesson
        total_started = db.query(Progress).filter(
            and_(
                Progress.lesson_id == lesson_id,
                Progress.status != ProgressStatusEnum.NOT_STARTED
            )
        ).count()
        
        # Count users who completed this lesson
        total_completed = db.query(Progress).filter(
            and_(
                Progress.lesson_id == lesson_id,
                Progress.status == ProgressStatusEnum.COMPLETED
            )
        ).count()
        
        # Calculate average score
        avg_score_result = db.query(Progress).filter(
            Progress.lesson_id == lesson_id
        ).all()
        
        avg_score = 0.0
        if avg_score_result:
            total_score = sum(p.score for p in avg_score_result)
            avg_score = total_score / len(avg_score_result)
        
        completion_rate = (total_completed / total_started * 100) if total_started > 0 else 0
        
        return {
            "lesson_id": lesson_id,
            "total_started": total_started,
            "total_completed": total_completed,
            "completion_rate": round(completion_rate, 2),
            "average_score": round(avg_score, 2)
        }