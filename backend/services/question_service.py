from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from models import Question, QuestionAttempt, User, Lesson, QuestionTypeEnum
import schemas
from datetime import datetime, timezone
import json
import re


class QuestionService:
    
    @staticmethod
    def create_question(db: Session, question_data: schemas.QuestionCreate) -> Question:
        """Create a new question"""
        db_question = Question(
            lesson_id=question_data.lesson_id,
            type=question_data.type,
            question_text=question_data.question_text,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            difficulty=question_data.difficulty,
            xp_reward=question_data.xp_reward
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question
    
    @staticmethod
    def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
        """Get a question by ID"""
        return db.query(Question).filter(Question.id == question_id).first()
    
    @staticmethod
    def get_questions_by_lesson(
        db: Session,
        lesson_id: int,
        question_type: Optional[QuestionTypeEnum] = None,
        difficulty: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Question]:
        """Get questions for a specific lesson with optional filtering"""
        query = db.query(Question).filter(Question.lesson_id == lesson_id)
        
        # Apply filters
        if question_type:
            query = query.filter(Question.type == question_type)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_question(
        db: Session,
        question_id: int,
        question_data: schemas.QuestionUpdate
    ) -> Optional[Question]:
        """Update a question"""
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None
        
        update_data = question_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        db.commit()
        db.refresh(db_question)
        return db_question
    
    @staticmethod
    def delete_question(db: Session, question_id: int) -> bool:
        """Delete a question"""
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return False
        
        db.delete(db_question)
        db.commit()
        return True
    
    @staticmethod
    def validate_answer(
        db: Session,
        question_id: int,
        user_answer: str
    ) -> Dict[str, Any]:
        """Validate user answer against correct answer"""
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return {
                "is_correct": False,
                "explanation": "Question not found",
                "xp_awarded": 0,
                "correct_answer": None
            }
        
        is_correct = False
        
        # Validate based on question type
        if question.type == QuestionTypeEnum.MCQ:
            is_correct = QuestionService._validate_mcq_answer(user_answer, question.correct_answer)
        elif question.type == QuestionTypeEnum.FILL_BLANK:
            is_correct = QuestionService._validate_fill_blank_answer(user_answer, question.correct_answer)
        elif question.type == QuestionTypeEnum.FLASHCARD:
            is_correct = QuestionService._validate_flashcard_answer(user_answer, question.correct_answer)
        elif question.type == QuestionTypeEnum.CODE:
            is_correct = QuestionService._validate_code_answer(user_answer, question.correct_answer)
        
        # Calculate XP awarded
        xp_awarded = question.xp_reward if is_correct else 0
        
        return {
            "is_correct": is_correct,
            "explanation": question.explanation,
            "xp_awarded": xp_awarded,
            "correct_answer": question.correct_answer if not is_correct else None
        }
    
    @staticmethod
    def _validate_mcq_answer(user_answer: str, correct_answer: str) -> bool:
        """Validate MCQ answer (exact match)"""
        return user_answer.strip().lower() == correct_answer.strip().lower()
    
    @staticmethod
    def _validate_fill_blank_answer(user_answer: str, correct_answer: str) -> bool:
        """Validate fill-in-the-blank answer (case-insensitive, whitespace normalized)"""
        user_normalized = re.sub(r'\s+', ' ', user_answer.strip().lower())
        correct_normalized = re.sub(r'\s+', ' ', correct_answer.strip().lower())
        return user_normalized == correct_normalized
    
    @staticmethod
    def _validate_flashcard_answer(user_answer: str, correct_answer: str) -> bool:
        """Validate flashcard answer (flexible matching)"""
        # For flashcards, we can be more lenient with matching
        user_words = set(user_answer.strip().lower().split())
        correct_words = set(correct_answer.strip().lower().split())
        
        # Check if user answer contains at least 50% of correct words
        if len(correct_words) == 0:
            return len(user_words) == 0
        
        overlap = len(user_words.intersection(correct_words))
        return overlap / len(correct_words) >= 0.5
    
    @staticmethod
    def _validate_code_answer(user_answer: str, correct_answer: str) -> bool:
        """Validate code answer (normalized whitespace and basic formatting)"""
        # Remove extra whitespace and normalize code formatting
        def normalize_code(code: str) -> str:
            # Remove comments and extra whitespace
            lines = []
            for line in code.split('\n'):
                # Remove inline comments (basic)
                line = re.sub(r'#.*', '', line)
                line = line.strip()
                if line:
                    lines.append(line)
            return '\n'.join(lines)
        
        user_normalized = normalize_code(user_answer)
        correct_normalized = normalize_code(correct_answer)
        
        return user_normalized == correct_normalized
    
    @staticmethod
    def create_question_attempt(
        db: Session,
        user_id: int,
        attempt_data: schemas.QuestionAttemptCreate,
        is_correct: bool
    ) -> QuestionAttempt:
        """Create a question attempt record"""
        db_attempt = QuestionAttempt(
            user_id=user_id,
            question_id=attempt_data.question_id,
            user_answer=attempt_data.user_answer,
            is_correct=is_correct,
            time_taken=attempt_data.time_taken
        )
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        return db_attempt
    
    @staticmethod
    def get_user_question_attempts(
        db: Session,
        user_id: int,
        question_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[QuestionAttempt]:
        """Get question attempts for a user"""
        query = db.query(QuestionAttempt).filter(QuestionAttempt.user_id == user_id)
        
        if question_id:
            query = query.filter(QuestionAttempt.question_id == question_id)
        
        return query.order_by(QuestionAttempt.created_at.desc())\
            .offset(skip).limit(limit).all()
    
    @staticmethod
    def get_question_statistics(db: Session, question_id: int) -> Dict[str, Any]:
        """Get statistics for a question"""
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return {}
        
        # Count total attempts
        total_attempts = db.query(QuestionAttempt).filter(
            QuestionAttempt.question_id == question_id
        ).count()
        
        # Count correct attempts
        correct_attempts = db.query(QuestionAttempt).filter(
            and_(
                QuestionAttempt.question_id == question_id,
                QuestionAttempt.is_correct == True
            )
        ).count()
        
        # Calculate average time taken
        attempts = db.query(QuestionAttempt).filter(
            QuestionAttempt.question_id == question_id
        ).all()
        
        avg_time = 0
        if attempts:
            total_time = sum(attempt.time_taken for attempt in attempts)
            avg_time = total_time / len(attempts)
        
        success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "question_id": question_id,
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "success_rate": round(success_rate, 2),
            "average_time_seconds": round(avg_time, 2)
        }
    
    @staticmethod
    def submit_answer(
        db: Session,
        user_id: int,
        submission: schemas.AnswerSubmissionRequest
    ) -> schemas.AnswerValidationResponse:
        """Submit and validate an answer"""
        from services.gamification_service import GamificationService
        
        # Validate the answer
        validation_result = QuestionService.validate_answer(
            db, submission.question_id, submission.user_answer
        )
        
        # Create attempt record
        attempt_data = schemas.QuestionAttemptCreate(
            question_id=submission.question_id,
            user_answer=submission.user_answer,
            time_taken=submission.time_taken
        )
        
        QuestionService.create_question_attempt(
            db, user_id, attempt_data, validation_result["is_correct"]
        )
        
        # Award XP using gamification service
        xp_awarded = 0
        if validation_result["is_correct"]:
            gamification_service = GamificationService(db)
            xp_awarded = gamification_service.award_question_xp(
                user_id=user_id,
                question_id=submission.question_id,
                is_correct=True,
                time_taken=submission.time_taken
            )
        
        return schemas.AnswerValidationResponse(
            is_correct=validation_result["is_correct"],
            explanation=validation_result["explanation"],
            xp_awarded=xp_awarded,
            correct_answer=validation_result["correct_answer"]
        )