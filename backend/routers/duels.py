from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from middleware import get_current_active_user
from models import User
from schemas import (
    DuelCreate, DuelJoin, DuelSubmission, DuelResponse, 
    DuelWithDetailsResponse, DuelResultResponse, DuelListResponse
)
from services.duel_service import DuelService

router = APIRouter(prefix="/duels", tags=["duels"])


@router.post("/create", response_model=DuelResponse)
async def create_duel(
    duel_data: DuelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new duel"""
    try:
        duel_service = DuelService(db)
        return duel_service.create_duel(duel_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create duel"
        )


@router.post("/join", response_model=DuelResponse)
async def join_duel(
    join_data: DuelJoin,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join an existing duel as opponent"""
    try:
        duel_service = DuelService(db)
        return duel_service.join_duel(join_data.duel_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join duel"
        )


@router.get("/{duel_id}", response_model=DuelWithDetailsResponse)
async def get_duel(
    duel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get duel details"""
    try:
        duel_service = DuelService(db)
        return duel_service.get_duel(duel_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get duel"
        )


@router.post("/{duel_id}/submit", response_model=DuelResultResponse)
async def submit_duel_solution(
    duel_id: int,
    submission: DuelSubmission,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a solution for a duel"""
    if submission.duel_id != duel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duel ID mismatch"
        )
    
    try:
        duel_service = DuelService(db)
        return await duel_service.submit_solution(
            duel_id=duel_id,
            user_id=current_user.id,
            code=submission.code,
            language=submission.language,
            time_taken=submission.time_taken
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit solution"
        )


@router.get("/available/list", response_model=List[DuelListResponse])
async def get_available_duels(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of available duels to join"""
    try:
        duel_service = DuelService(db)
        return duel_service.get_available_duels(current_user.id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available duels"
        )


@router.get("/user/history", response_model=List[DuelListResponse])
async def get_user_duels(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's duel history"""
    try:
        duel_service = DuelService(db)
        return duel_service.get_user_duels(current_user.id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user duels"
        )


@router.delete("/cleanup")
async def cleanup_old_duels(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clean up old waiting duels (admin function)"""
    try:
        duel_service = DuelService(db)
        count = duel_service.cleanup_old_duels()
        return {"message": f"Cleaned up {count} old duels"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup duels"
        )