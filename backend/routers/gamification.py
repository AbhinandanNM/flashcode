from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from middleware import get_current_active_user
from models import User
from services.gamification_service import GamificationService
import schemas

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntryResponse])
def get_leaderboard(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get weekly leaderboard rankings"""
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 10
    
    gamification_service = GamificationService(db)
    leaderboard = gamification_service.get_weekly_leaderboard(limit=limit, offset=offset)
    
    return [
        schemas.LeaderboardEntryResponse(
            rank=entry["rank"],
            user_id=entry["user_id"],
            username=entry["username"],
            xp=entry["xp"],
            streak=entry["streak"],
            joined_on=entry["joined_on"]
        )
        for entry in leaderboard
    ]


@router.get("/stats/me", response_model=schemas.UserStatsResponse)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's gamification statistics"""
    gamification_service = GamificationService(db)
    stats = gamification_service.get_user_stats(current_user.id)
    
    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=stats["error"]
        )
    
    return schemas.UserStatsResponse(**stats)


@router.get("/stats/{user_id}", response_model=schemas.UserStatsResponse)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get gamification statistics for a specific user"""
    gamification_service = GamificationService(db)
    stats = gamification_service.get_user_stats(user_id)
    
    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=stats["error"]
        )
    
    return schemas.UserStatsResponse(**stats)


@router.get("/rank/me", response_model=schemas.UserRankResponse)
def get_my_rank(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's leaderboard rank"""
    gamification_service = GamificationService(db)
    rank = gamification_service.get_user_rank(current_user.id)
    
    if rank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return schemas.UserRankResponse(
        user_id=current_user.id,
        username=current_user.username,
        rank=rank,
        xp=current_user.xp
    )


@router.post("/activity", response_model=schemas.ActivityUpdateResponse)
def update_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user activity and streak (called when user performs learning activities)"""
    gamification_service = GamificationService(db)
    result = gamification_service.update_user_activity(current_user.id)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return schemas.ActivityUpdateResponse(**result)


@router.post("/award-xp", response_model=schemas.XPAwardResponse)
def award_xp_manual(
    request: schemas.XPAwardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually award XP (admin only - for testing/special events)"""
    # Note: In a real application, you'd want to add admin role checking here
    gamification_service = GamificationService(db)
    
    success = gamification_service.award_xp(
        user_id=request.user_id or current_user.id,
        xp_amount=request.xp_amount,
        source=request.source or "manual_award"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or XP award failed"
        )
    
    # Get updated user info
    updated_user = db.query(User).filter(User.id == (request.user_id or current_user.id)).first()
    
    return schemas.XPAwardResponse(
        success=True,
        xp_awarded=request.xp_amount,
        total_xp=updated_user.xp,
        message=f"Awarded {request.xp_amount} XP"
    )