from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from middleware import get_current_active_user
from models import User, LanguageEnum
from services.lesson_service import LessonService
import schemas

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("/", response_model=schemas.LessonResponse)
async def create_lesson(
    lesson_data: schemas.LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new lesson (admin functionality)
    """
    try:
        lesson = LessonService.create_lesson(db, lesson_data)
        return lesson
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lesson"
        )


@router.get("/", response_model=List[schemas.LessonWithProgressResponse])
async def get_lessons(
    skip: int = Query(0, ge=0, description="Number of lessons to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of lessons to return"),
    language: Optional[LanguageEnum] = Query(None, description="Filter by programming language"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty level"),
    include_progress: bool = Query(True, description="Include user progress information"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get lessons with optional filtering and user progress
    """
    try:
        if include_progress:
            lessons = LessonService.get_lessons_with_progress(
                db=db,
                user_id=current_user.id,
                skip=skip,
                limit=limit,
                language=language,
                difficulty=difficulty,
                is_published=True
            )
            return lessons
        else:
            lessons = LessonService.get_lessons(
                db=db,
                skip=skip,
                limit=limit,
                language=language,
                difficulty=difficulty,
                is_published=True
            )
            # Convert to response format without progress
            return [
                {
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
                for lesson in lessons
            ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lessons"
        )


@router.get("/{lesson_id}", response_model=schemas.LessonResponse)
async def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific lesson by ID
    """
    lesson = LessonService.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    if not lesson.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not available"
        )
    
    return lesson


@router.put("/{lesson_id}", response_model=schemas.LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: schemas.LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a lesson (admin functionality)
    """
    lesson = LessonService.update_lesson(db, lesson_id, lesson_data)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return lesson


@router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a lesson (admin functionality)
    """
    success = LessonService.delete_lesson(db, lesson_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return {"message": "Lesson deleted successfully"}


@router.get("/{lesson_id}/progress", response_model=schemas.ProgressResponse)
async def get_lesson_progress(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's progress for a specific lesson
    """
    # Verify lesson exists
    lesson = LessonService.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    progress = LessonService.get_user_progress(db, current_user.id, lesson_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this lesson"
        )
    
    return progress


@router.post("/{lesson_id}/progress", response_model=schemas.ProgressResponse)
async def update_lesson_progress(
    lesson_id: int,
    progress_data: schemas.ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create or update user's progress for a lesson
    """
    # Verify lesson exists
    lesson = LessonService.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    try:
        progress = LessonService.create_or_update_progress(
            db=db,
            user_id=current_user.id,
            lesson_id=lesson_id,
            progress_data=progress_data
        )
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update progress"
        )


@router.get("/{lesson_id}/statistics")
async def get_lesson_statistics(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics for a lesson (admin functionality)
    """
    lesson = LessonService.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    try:
        statistics = LessonService.get_lesson_statistics(db, lesson_id)
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lesson statistics"
        )


# Progress-related endpoints
@router.get("/progress/all", response_model=List[schemas.ProgressResponse])
async def get_user_progress(
    skip: int = Query(0, ge=0, description="Number of progress records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of progress records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all progress for the current user
    """
    try:
        progress_list = LessonService.get_user_all_progress(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return progress_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user progress"
        )