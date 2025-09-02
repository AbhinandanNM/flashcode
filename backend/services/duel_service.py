from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import random
import asyncio

from models import Duel, User, Question, QuestionAttempt, DuelStatusEnum
from schemas import (
    DuelCreate, DuelResponse, DuelWithDetailsResponse, DuelResultResponse,
    DuelListResponse, BotOpponentResponse, CodeExecutionResponse
)
from services.code_execution_service import CodeExecutionService
from services.gamification_service import GamificationService


class DuelService:
    def __init__(self, db: Session, code_execution_service=None):
        self.db = db
        self.code_execution_service = code_execution_service or CodeExecutionService()
        self.gamification_service = GamificationService(db)
    
    def create_duel(self, duel_data: DuelCreate, challenger_id: int) -> DuelResponse:
        """Create a new duel and attempt to find an opponent"""
        # Verify the question exists and is a code type
        question = self.db.query(Question).filter(Question.id == duel_data.question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        if question.type.value != "code":
            raise ValueError("Only code questions can be used for duels")
        
        # Check if user already has an active duel
        existing_duel = self.db.query(Duel).filter(
            and_(
                or_(
                    Duel.challenger_id == challenger_id,
                    Duel.opponent_id == challenger_id
                ),
                Duel.status.in_([DuelStatusEnum.WAITING, DuelStatusEnum.ACTIVE])
            )
        ).first()
        
        if existing_duel:
            raise ValueError("You already have an active duel")
        
        # Create the duel
        duel = Duel(
            challenger_id=challenger_id,
            question_id=duel_data.question_id,
            status=DuelStatusEnum.WAITING
        )
        
        self.db.add(duel)
        self.db.commit()
        self.db.refresh(duel)
        
        # Try to find an opponent
        try:
            self._attempt_matchmaking(duel.id)
        except Exception as e:
            # Log the error but don't fail duel creation
            print(f"Matchmaking failed: {e}")
            pass
        
        return DuelResponse.model_validate(duel)
    
    def join_duel(self, duel_id: int, user_id: int) -> DuelResponse:
        """Join an existing duel as opponent"""
        duel = self.db.query(Duel).filter(Duel.id == duel_id).first()
        if not duel:
            raise ValueError("Duel not found")
        
        if duel.status != DuelStatusEnum.WAITING:
            raise ValueError("Duel is not available for joining")
        
        if duel.challenger_id == user_id:
            raise ValueError("Cannot join your own duel")
        
        if duel.opponent_id is not None:
            raise ValueError("Duel already has an opponent")
        
        # Check if user already has an active duel
        existing_duel = self.db.query(Duel).filter(
            and_(
                or_(
                    Duel.challenger_id == user_id,
                    Duel.opponent_id == user_id
                ),
                Duel.status.in_([DuelStatusEnum.WAITING, DuelStatusEnum.ACTIVE])
            )
        ).first()
        
        if existing_duel:
            raise ValueError("You already have an active duel")
        
        # Join the duel
        duel.opponent_id = user_id
        duel.status = DuelStatusEnum.ACTIVE
        
        self.db.commit()
        self.db.refresh(duel)
        
        return DuelResponse.model_validate(duel)
    
    def get_duel(self, duel_id: int, user_id: Optional[int] = None) -> DuelWithDetailsResponse:
        """Get duel details with question and user information"""
        duel = self.db.query(Duel).filter(Duel.id == duel_id).first()
        if not duel:
            raise ValueError("Duel not found")
        
        # Check if user has access to this duel
        if user_id and duel.challenger_id != user_id and duel.opponent_id != user_id:
            raise ValueError("Access denied to this duel")
        
        # Get challenger info
        challenger = self.db.query(User).filter(User.id == duel.challenger_id).first()
        challenger_username = challenger.username if challenger else "Unknown"
        
        # Get opponent info
        opponent_username = None
        is_bot_opponent = False
        if duel.opponent_id:
            if duel.opponent_id < 0:  # Bot opponent (negative IDs)
                is_bot_opponent = True
                bot_info = self._get_bot_info(duel.opponent_id)
                opponent_username = bot_info.username
            else:
                opponent = self.db.query(User).filter(User.id == duel.opponent_id).first()
                opponent_username = opponent.username if opponent else "Unknown"
        
        # Get winner info
        winner_username = None
        if duel.winner_id:
            if duel.winner_id < 0:  # Bot winner
                bot_info = self._get_bot_info(duel.winner_id)
                winner_username = bot_info.username
            else:
                winner = self.db.query(User).filter(User.id == duel.winner_id).first()
                winner_username = winner.username if winner else "Unknown"
        
        # Get question info
        question = self.db.query(Question).filter(Question.id == duel.question_id).first()
        
        return DuelWithDetailsResponse(
            id=duel.id,
            challenger_id=duel.challenger_id,
            opponent_id=duel.opponent_id,
            question_id=duel.question_id,
            status=duel.status.value,
            winner_id=duel.winner_id,
            created_at=duel.created_at,
            completed_at=duel.completed_at,
            challenger_username=challenger_username,
            opponent_username=opponent_username,
            winner_username=winner_username,
            question=question,
            is_bot_opponent=is_bot_opponent
        )
    
    async def submit_solution(self, duel_id: int, user_id: int, code: str, language: str, time_taken: int = 0) -> DuelResultResponse:
        """Submit a solution for a duel"""
        duel = self.db.query(Duel).filter(Duel.id == duel_id).first()
        if not duel:
            raise ValueError("Duel not found")
        
        if duel.status != DuelStatusEnum.ACTIVE:
            raise ValueError("Duel is not active")
        
        if duel.challenger_id != user_id and duel.opponent_id != user_id:
            raise ValueError("You are not a participant in this duel")
        
        if duel.status == DuelStatusEnum.COMPLETED:
            raise ValueError("Duel is already completed")
        
        # Get the question
        question = self.db.query(Question).filter(Question.id == duel.question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        # Execute the code
        execution_result = await self.code_execution_service.execute_code(
            code=code,
            language=language,
            expected_output=question.correct_answer
        )
        
        # Record the attempt
        attempt = QuestionAttempt(
            user_id=user_id,
            question_id=question.id,
            user_answer=code,
            is_correct=execution_result.is_correct or False,
            time_taken=time_taken
        )
        self.db.add(attempt)
        
        # Check if this is the first correct solution or if both have submitted
        challenger_attempt = self.db.query(QuestionAttempt).filter(
            and_(
                QuestionAttempt.user_id == duel.challenger_id,
                QuestionAttempt.question_id == duel.question_id,
                QuestionAttempt.created_at >= duel.created_at
            )
        ).order_by(QuestionAttempt.created_at.desc()).first()
        
        opponent_attempt = None
        if duel.opponent_id and duel.opponent_id > 0:  # Not a bot
            opponent_attempt = self.db.query(QuestionAttempt).filter(
                and_(
                    QuestionAttempt.user_id == duel.opponent_id,
                    QuestionAttempt.question_id == duel.question_id,
                    QuestionAttempt.created_at >= duel.created_at
                )
            ).order_by(QuestionAttempt.created_at.desc()).first()
        
        # Determine winner
        winner_id = None
        xp_awarded = 0
        
        if execution_result.is_correct:
            # If this is the first correct solution, they win
            if user_id == duel.challenger_id:
                if not opponent_attempt or not opponent_attempt.is_correct:
                    winner_id = user_id
            else:  # opponent
                if not challenger_attempt or not challenger_attempt.is_correct:
                    winner_id = user_id
        
        # Handle bot opponent
        if duel.opponent_id and duel.opponent_id < 0:
            bot_result = self._simulate_bot_solution(duel.opponent_id, question, execution_result.is_correct)
            if execution_result.is_correct and not bot_result["is_correct"]:
                winner_id = user_id
            elif not execution_result.is_correct and bot_result["is_correct"]:
                winner_id = duel.opponent_id
            elif execution_result.is_correct and bot_result["is_correct"]:
                # Both correct, winner based on time
                if time_taken < bot_result["time_taken"]:
                    winner_id = user_id
                else:
                    winner_id = duel.opponent_id
        
        # Complete duel if we have a winner or both submitted
        if winner_id or (challenger_attempt and (opponent_attempt or duel.opponent_id < 0)):
            duel.status = DuelStatusEnum.COMPLETED
            duel.winner_id = winner_id
            duel.completed_at = datetime.now(timezone.utc)
            
            # Award XP to winner
            if winner_id and winner_id > 0:  # Not a bot
                base_xp = question.xp_reward
                bonus_xp = int(base_xp * 0.5)  # 50% bonus for winning duel
                xp_awarded = base_xp + bonus_xp
                self.gamification_service.award_xp(winner_id, xp_awarded)
        
        self.db.commit()
        
        return DuelResultResponse(
            duel_id=duel.id,
            winner_id=winner_id,
            winner_username=self._get_username(winner_id) if winner_id else None,
            challenger_result=execution_result if user_id == duel.challenger_id else None,
            opponent_result=execution_result if user_id == duel.opponent_id else None,
            xp_awarded=xp_awarded if winner_id == user_id else 0,
            completed_at=duel.completed_at or datetime.now(timezone.utc)
        )
    
    def get_available_duels(self, user_id: int, limit: int = 10) -> List[DuelListResponse]:
        """Get list of available duels to join"""
        duels = self.db.query(Duel).filter(
            and_(
                Duel.status == DuelStatusEnum.WAITING,
                Duel.challenger_id != user_id,
                Duel.opponent_id.is_(None)
            )
        ).order_by(Duel.created_at.desc()).limit(limit).all()
        
        result = []
        for duel in duels:
            challenger = self.db.query(User).filter(User.id == duel.challenger_id).first()
            question = self.db.query(Question).filter(Question.id == duel.question_id).first()
            
            result.append(DuelListResponse(
                id=duel.id,
                challenger_id=duel.challenger_id,
                challenger_username=challenger.username if challenger else "Unknown",
                opponent_id=None,
                opponent_username=None,
                status=duel.status.value,
                question_id=duel.question_id,
                question_text=question.question_text if question else "Unknown",
                created_at=duel.created_at,
                is_bot_opponent=False
            ))
        
        return result
    
    def get_user_duels(self, user_id: int, limit: int = 20) -> List[DuelListResponse]:
        """Get user's duel history"""
        duels = self.db.query(Duel).filter(
            or_(
                Duel.challenger_id == user_id,
                Duel.opponent_id == user_id
            )
        ).order_by(Duel.created_at.desc()).limit(limit).all()
        
        result = []
        for duel in duels:
            challenger = self.db.query(User).filter(User.id == duel.challenger_id).first()
            opponent_username = None
            is_bot_opponent = False
            
            if duel.opponent_id:
                if duel.opponent_id < 0:  # Bot
                    is_bot_opponent = True
                    bot_info = self._get_bot_info(duel.opponent_id)
                    opponent_username = bot_info.username
                else:
                    opponent = self.db.query(User).filter(User.id == duel.opponent_id).first()
                    opponent_username = opponent.username if opponent else "Unknown"
            
            question = self.db.query(Question).filter(Question.id == duel.question_id).first()
            
            result.append(DuelListResponse(
                id=duel.id,
                challenger_id=duel.challenger_id,
                challenger_username=challenger.username if challenger else "Unknown",
                opponent_id=duel.opponent_id,
                opponent_username=opponent_username,
                status=duel.status.value,
                question_id=duel.question_id,
                question_text=question.question_text if question else "Unknown",
                created_at=duel.created_at,
                is_bot_opponent=is_bot_opponent
            ))
        
        return result
    
    def _attempt_matchmaking(self, duel_id: int) -> bool:
        """Attempt to find an opponent for a duel"""
        duel = self.db.query(Duel).filter(Duel.id == duel_id).first()
        if not duel or duel.status != DuelStatusEnum.WAITING:
            return False
        
        # Look for other waiting duels with the same question
        potential_opponent_duel = self.db.query(Duel).filter(
            and_(
                Duel.status == DuelStatusEnum.WAITING,
                Duel.question_id == duel.question_id,
                Duel.challenger_id != duel.challenger_id,
                Duel.id != duel.id,
                Duel.opponent_id.is_(None)
            )
        ).first()
        
        if potential_opponent_duel:
            # Match the duels
            duel.opponent_id = potential_opponent_duel.challenger_id
            duel.status = DuelStatusEnum.ACTIVE
            
            # Cancel the other duel
            self.db.delete(potential_opponent_duel)
            self.db.commit()
            return True
        
        # If no human opponent found after 30 seconds, assign a bot
        created_at = duel.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        if (datetime.now(timezone.utc) - created_at).total_seconds() > 30:
            bot_id = self._assign_bot_opponent(duel)
            if bot_id:
                duel.opponent_id = bot_id
                duel.status = DuelStatusEnum.ACTIVE
                self.db.commit()
                return True
        
        return False
    
    def _assign_bot_opponent(self, duel: Duel) -> Optional[int]:
        """Assign a bot opponent to a duel"""
        # Get question difficulty to match bot difficulty
        question = self.db.query(Question).filter(Question.id == duel.question_id).first()
        if not question:
            return None
        
        # Bot IDs are negative numbers based on difficulty
        bot_id = -(question.difficulty)  # -1 to -5 based on difficulty
        return bot_id
    
    def _get_bot_info(self, bot_id: int) -> BotOpponentResponse:
        """Get bot information based on bot ID"""
        difficulty = abs(bot_id)
        bot_names = {
            1: "CodeBot Novice",
            2: "CodeBot Junior", 
            3: "CodeBot Expert",
            4: "CodeBot Master",
            5: "CodeBot Grandmaster"
        }
        
        # Response time based on difficulty (easier bots are slower)
        response_times = {
            1: 15000,  # 15 seconds
            2: 12000,  # 12 seconds
            3: 8000,   # 8 seconds
            4: 5000,   # 5 seconds
            5: 3000    # 3 seconds
        }
        
        return BotOpponentResponse(
            id=bot_id,
            username=bot_names.get(difficulty, f"CodeBot Level {difficulty}"),
            difficulty_level=difficulty,
            response_time_ms=response_times.get(difficulty, 10000)
        )
    
    def _simulate_bot_solution(self, bot_id: int, question: Question, user_is_correct: bool) -> Dict[str, Any]:
        """Simulate bot solution based on difficulty"""
        difficulty = abs(bot_id)
        
        # Bot success rate based on difficulty
        success_rates = {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.85, 5: 0.95}
        success_rate = success_rates.get(difficulty, 0.5)
        
        # If user got it wrong, bot has higher chance of success
        if not user_is_correct:
            success_rate = min(success_rate + 0.2, 0.95)
        
        is_correct = random.random() < success_rate
        
        # Bot response time based on difficulty
        base_times = {1: 15, 2: 12, 3: 8, 4: 5, 5: 3}
        base_time = base_times.get(difficulty, 10)
        
        # Add some randomness to response time
        time_taken = base_time + random.randint(-2, 3)
        time_taken = max(1, time_taken)  # Minimum 1 second
        
        return {
            "is_correct": is_correct,
            "time_taken": time_taken
        }
    
    def _get_username(self, user_id: int) -> Optional[str]:
        """Get username for a user or bot"""
        if user_id < 0:  # Bot
            bot_info = self._get_bot_info(user_id)
            return bot_info.username
        else:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user.username if user else None
    
    def cleanup_old_duels(self) -> int:
        """Clean up old waiting duels (older than 5 minutes)"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        # Handle timezone-naive datetimes from SQLite
        old_duels = []
        waiting_duels = self.db.query(Duel).filter(Duel.status == DuelStatusEnum.WAITING).all()
        
        for duel in waiting_duels:
            created_at = duel.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            if created_at < cutoff_time:
                old_duels.append(duel)
        
        count = len(old_duels)
        for duel in old_duels:
            self.db.delete(duel)
        
        self.db.commit()
        return count