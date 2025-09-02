from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from database import get_db
from middleware import get_current_active_user
from models import User, Question, QuestionAttempt
from schemas import (
    CodeExecutionRequest, 
    CodeExecutionResponse,
    CodeSubmissionRequest,
    CodeSubmissionResponse
)
from services.code_execution_service import code_execution_service

router = APIRouter(prefix="/execute", tags=["code-execution"])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/run", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute code without saving results (for testing/practice)
    """
    try:
        logger.info(f"User {current_user.username} executing {request.language} code")
        
        result = await code_execution_service.execute_code(
            code=request.code,
            language=request.language,
            input_data=request.input_data,
            expected_output=request.expected_output
        )
        
        return CodeExecutionResponse(**result)
        
    except Exception as e:
        logger.error(f"Code execution error for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/submit", response_model=CodeSubmissionResponse)
async def submit_code_solution(
    request: CodeSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit code solution for a specific question and save the attempt
    """
    try:
        # Get the question
        question = db.query(Question).filter(Question.id == request.question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Verify this is a code question
        if question.type.value != "code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is only for code questions"
            )
        
        logger.info(f"User {current_user.username} submitting code for question {question.id}")
        
        # Execute the code with expected output from question
        execution_result = await code_execution_service.execute_code(
            code=request.code,
            language=request.language,
            input_data="",  # TODO: Get input data from question if needed
            expected_output=question.correct_answer
        )
        
        # Determine if the solution is correct
        is_correct = execution_result.get("is_correct", False)
        
        # Save the question attempt
        attempt = QuestionAttempt(
            user_id=current_user.id,
            question_id=question.id,
            user_answer=request.code,
            is_correct=is_correct,
            time_taken=request.time_taken
        )
        db.add(attempt)
        db.commit()
        
        # Award XP using gamification service
        xp_awarded = 0
        if is_correct:
            from services.gamification_service import GamificationService
            gamification_service = GamificationService(db)
            xp_awarded = gamification_service.award_question_xp(
                user_id=current_user.id,
                question_id=question.id,
                is_correct=True,
                time_taken=request.time_taken
            )
        
        logger.info(f"Code submission result for user {current_user.username}: correct={is_correct}, xp={xp_awarded}")
        
        return CodeSubmissionResponse(
            is_correct=is_correct,
            execution_result=CodeExecutionResponse(**execution_result),
            xp_awarded=xp_awarded,
            explanation=question.explanation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code submission error for user {current_user.username}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code submission failed: {str(e)}"
        )


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported programming languages
    """
    return {
        "languages": [
            {
                "id": "python",
                "name": "Python 3",
                "version": "3.9+",
                "file_extension": ".py"
            },
            {
                "id": "cpp",
                "name": "C++",
                "version": "GCC 9+",
                "file_extension": ".cpp"
            }
        ]
    }


@router.get("/status")
async def get_execution_service_status():
    """
    Get status of code execution service
    """
    return {
        "service": "code_execution",
        "status": "healthy",
        "judge0_enabled": code_execution_service.use_judge0,
        "docker_fallback": not code_execution_service.use_judge0,
        "supported_languages": ["python", "cpp"]
    }