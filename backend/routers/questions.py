from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from middleware import get_current_active_user
from models import User, QuestionTypeEnum
from services.question_service import QuestionService
import schemas

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/", response_model=schemas.QuestionResponse)
def create_question(
    question: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new question (admin only for now)"""
    # Note: In a real application, you'd want to add admin role checking here
    return QuestionService.create_question(db, question)


@router.get("/{question_id}", response_model=schemas.QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific question by ID"""
    question = QuestionService.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@router.get("/lesson/{lesson_id}", response_model=List[schemas.QuestionListResponse])
def get_questions_by_lesson(
    lesson_id: int,
    question_type: Optional[QuestionTypeEnum] = None,
    difficulty: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get questions for a specific lesson"""
    questions = QuestionService.get_questions_by_lesson(
        db, lesson_id, question_type, difficulty, skip, limit
    )
    
    # Convert to list response format (without correct answers)
    return [
        schemas.QuestionListResponse(
            id=q.id,
            type=q.type,
            question_text=q.question_text,
            options=q.options,
            difficulty=q.difficulty,
            xp_reward=q.xp_reward
        )
        for q in questions
    ]


@router.put("/{question_id}", response_model=schemas.QuestionResponse)
def update_question(
    question_id: int,
    question_update: schemas.QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a question (admin only for now)"""
    # Note: In a real application, you'd want to add admin role checking here
    question = QuestionService.update_question(db, question_id, question_update)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a question (admin only for now)"""
    # Note: In a real application, you'd want to add admin role checking here
    success = QuestionService.delete_question(db, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return {"message": "Question deleted successfully"}


@router.post("/submit", response_model=schemas.AnswerValidationResponse)
def submit_answer(
    submission: schemas.AnswerSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit an answer for validation"""
    # Verify question exists
    question = QuestionService.get_question_by_id(db, submission.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return QuestionService.submit_answer(db, current_user.id, submission)


@router.get("/attempts/me", response_model=List[schemas.QuestionAttemptResponse])
def get_my_attempts(
    question_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's question attempts"""
    attempts = QuestionService.get_user_question_attempts(
        db, current_user.id, question_id, skip, limit
    )
    return attempts


@router.get("/{question_id}/statistics")
def get_question_statistics(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics for a question (admin only for now)"""
    # Note: In a real application, you'd want to add admin role checking here
    question = QuestionService.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return QuestionService.get_question_statistics(db, question_id)