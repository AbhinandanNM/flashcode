from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import LanguageEnum, ProgressStatusEnum, QuestionTypeEnum, DuelStatusEnum

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    xp: int
    streak: int
    last_activity: datetime
    joined_on: datetime
    is_active: bool
    
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Lesson Schemas
class LessonBase(BaseModel):
    language: LanguageEnum
    title: str
    theory: str
    difficulty: int
    xp_reward: int
    order_index: int
    is_published: bool = True

class LessonCreate(LessonBase):
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Difficulty must be between 1 and 5')
        return v
    
    @field_validator('xp_reward')
    @classmethod
    def validate_xp_reward(cls, v):
        if v < 0:
            raise ValueError('XP reward must be non-negative')
        return v

class LessonUpdate(BaseModel):
    language: Optional[LanguageEnum] = None
    title: Optional[str] = None
    theory: Optional[str] = None
    difficulty: Optional[int] = None
    xp_reward: Optional[int] = None
    order_index: Optional[int] = None
    is_published: Optional[bool] = None
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('Difficulty must be between 1 and 5')
        return v
    
    @field_validator('xp_reward')
    @classmethod
    def validate_xp_reward(cls, v):
        if v is not None and v < 0:
            raise ValueError('XP reward must be non-negative')
        return v

class LessonResponse(LessonBase):
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class LessonListResponse(BaseModel):
    id: int
    language: LanguageEnum
    title: str
    difficulty: int
    xp_reward: int
    order_index: int
    is_published: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}

# Progress Schemas
class ProgressBase(BaseModel):
    status: ProgressStatusEnum
    score: float = 0.0
    attempts: int = 0

class ProgressCreate(ProgressBase):
    lesson_id: int

class ProgressUpdate(BaseModel):
    status: Optional[ProgressStatusEnum] = None
    score: Optional[float] = None
    attempts: Optional[int] = None
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Score must be between 0.0 and 1.0')
        return v

class ProgressResponse(ProgressBase):
    id: int
    user_id: int
    lesson_id: int
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class LessonWithProgressResponse(LessonListResponse):
    progress: Optional[ProgressResponse] = None

# Question Schemas
class QuestionBase(BaseModel):
    lesson_id: int
    type: QuestionTypeEnum
    question_text: str
    options: Optional[Dict[str, Any]] = None  # For MCQ questions
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: int
    xp_reward: int

class QuestionCreate(QuestionBase):
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Difficulty must be between 1 and 5')
        return v
    
    @field_validator('xp_reward')
    @classmethod
    def validate_xp_reward(cls, v):
        if v < 0:
            raise ValueError('XP reward must be non-negative')
        return v
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v, info):
        # For MCQ questions, options are required
        if info.data.get('type') == QuestionTypeEnum.MCQ and not v:
            raise ValueError('Options are required for MCQ questions')
        return v

class QuestionUpdate(BaseModel):
    lesson_id: Optional[int] = None
    type: Optional[QuestionTypeEnum] = None
    question_text: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None
    xp_reward: Optional[int] = None
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('Difficulty must be between 1 and 5')
        return v
    
    @field_validator('xp_reward')
    @classmethod
    def validate_xp_reward(cls, v):
        if v is not None and v < 0:
            raise ValueError('XP reward must be non-negative')
        return v

class QuestionResponse(QuestionBase):
    id: int
    
    model_config = {"from_attributes": True}

class QuestionListResponse(BaseModel):
    id: int
    type: QuestionTypeEnum
    question_text: str
    options: Optional[Dict[str, Any]] = None
    difficulty: int
    xp_reward: int
    
    model_config = {"from_attributes": True}

# Question Attempt Schemas
class QuestionAttemptBase(BaseModel):
    question_id: int
    user_answer: str
    time_taken: int  # seconds

class QuestionAttemptCreate(QuestionAttemptBase):
    @field_validator('time_taken')
    @classmethod
    def validate_time_taken(cls, v):
        if v < 0:
            raise ValueError('Time taken must be non-negative')
        return v

class QuestionAttemptResponse(QuestionAttemptBase):
    id: int
    user_id: int
    is_correct: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}

class AnswerSubmissionRequest(BaseModel):
    question_id: int
    user_answer: str
    time_taken: int = 0

class AnswerValidationResponse(BaseModel):
    is_correct: bool
    explanation: Optional[str] = None
    xp_awarded: int = 0
    correct_answer: Optional[str] = None  # Only shown if incorrect

# Code Execution Schemas
class CodeExecutionRequest(BaseModel):
    code: str
    language: str  # python, cpp
    input_data: str = ""
    expected_output: Optional[str] = None
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v not in ['python', 'cpp']:
            raise ValueError('Language must be either "python" or "cpp"')
        return v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 10000:  # 10KB limit
            raise ValueError('Code is too long (max 10KB)')
        return v

class CodeExecutionResponse(BaseModel):
    status: str  # success, error, timeout, compilation_error, runtime_error, wrong_answer
    stdout: str
    stderr: str
    execution_time: float
    memory: Optional[int] = None  # Memory usage in KB (Judge0 only)
    is_correct: Optional[bool] = None  # Only if expected_output provided
    error: Optional[str] = None
    compile_output: Optional[str] = None  # Compilation output (Judge0 only)

class CodeSubmissionRequest(BaseModel):
    question_id: int
    code: str
    language: str
    time_taken: int = 0
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v not in ['python', 'cpp']:
            raise ValueError('Language must be either "python" or "cpp"')
        return v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 10000:  # 10KB limit
            raise ValueError('Code is too long (max 10KB)')
        return v
    
    @field_validator('time_taken')
    @classmethod
    def validate_time_taken(cls, v):
        if v < 0:
            raise ValueError('Time taken must be non-negative')
        return v

class CodeSubmissionResponse(BaseModel):
    is_correct: bool
    execution_result: CodeExecutionResponse
    xp_awarded: int = 0
    explanation: Optional[str] = None

# Spaced Repetition Schemas
class ReviewQuestionResponse(BaseModel):
    question: QuestionResponse
    review_data: Dict[str, Any]
    is_due: bool
    latest_attempt: Optional[QuestionAttemptResponse] = None
    
    model_config = {"from_attributes": True}

class ReviewScheduleUpdate(BaseModel):
    question_id: int
    is_correct: bool
    time_taken: int = 0
    
    @field_validator('time_taken')
    @classmethod
    def validate_time_taken(cls, v):
        if v < 0:
            raise ValueError('Time taken must be non-negative')
        return v

class ReviewScheduleResponse(BaseModel):
    next_interval: int
    ease_factor: float
    repetition: int
    next_review_date: datetime
    quality_score: int
    question_id: int

class ReviewStatisticsResponse(BaseModel):
    total_questions_reviewed: int
    questions_due_for_review: int
    total_attempts: int
    correct_attempts: int
    success_rate: float
    average_time_seconds: float
    attempts_this_week: int
    review_streak_days: int

class FlashcardSessionRequest(BaseModel):
    limit: int = 20
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        if not 1 <= v <= 100:
            raise ValueError('Limit must be between 1 and 100')
        return v

# Gamification Schemas
class LeaderboardEntryResponse(BaseModel):
    rank: int
    user_id: int
    username: str
    xp: int
    streak: int
    joined_on: datetime
    
    model_config = {"from_attributes": True}

class UserStatsResponse(BaseModel):
    user_id: int
    username: str
    xp: int
    streak: int
    rank: Optional[int] = None
    completed_lessons: int
    total_attempts: int
    correct_attempts: int
    accuracy: float
    joined_on: datetime
    last_activity: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class UserRankResponse(BaseModel):
    user_id: int
    username: str
    rank: int
    xp: int
    
    model_config = {"from_attributes": True}

class ActivityUpdateResponse(BaseModel):
    user_id: int
    new_streak: int
    streak_maintained: bool
    streak_broken: bool
    last_activity: datetime
    
    model_config = {"from_attributes": True}

class XPAwardRequest(BaseModel):
    user_id: Optional[int] = None  # If None, awards to current user
    xp_amount: int
    source: Optional[str] = None
    
    @field_validator('xp_amount')
    @classmethod
    def validate_xp_amount(cls, v):
        if v < 0:
            raise ValueError('XP amount must be non-negative')
        if v > 10000:
            raise ValueError('XP amount too large (max 10000)')
        return v

class XPAwardResponse(BaseModel):
    success: bool
    xp_awarded: int
    total_xp: int
    message: str

# Duel Schemas
class DuelBase(BaseModel):
    question_id: int

class DuelCreate(DuelBase):
    @field_validator('question_id')
    @classmethod
    def validate_question_id(cls, v):
        if v <= 0:
            raise ValueError('Question ID must be positive')
        return v

class DuelJoin(BaseModel):
    duel_id: int
    
    @field_validator('duel_id')
    @classmethod
    def validate_duel_id(cls, v):
        if v <= 0:
            raise ValueError('Duel ID must be positive')
        return v

class DuelSubmission(BaseModel):
    duel_id: int
    code: str
    language: str
    time_taken: int = 0
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v not in ['python', 'cpp']:
            raise ValueError('Language must be either "python" or "cpp"')
        return v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 10000:  # 10KB limit
            raise ValueError('Code is too long (max 10KB)')
        return v
    
    @field_validator('time_taken')
    @classmethod
    def validate_time_taken(cls, v):
        if v < 0:
            raise ValueError('Time taken must be non-negative')
        return v

class DuelResponse(BaseModel):
    id: int
    challenger_id: int
    opponent_id: Optional[int] = None
    question_id: int
    status: str  # waiting, active, completed
    winner_id: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class DuelWithDetailsResponse(DuelResponse):
    challenger_username: str
    opponent_username: Optional[str] = None
    winner_username: Optional[str] = None
    question: QuestionResponse
    is_bot_opponent: bool = False

class DuelResultResponse(BaseModel):
    duel_id: int
    winner_id: Optional[int] = None
    winner_username: Optional[str] = None
    challenger_result: Optional[CodeExecutionResponse] = None
    opponent_result: Optional[CodeExecutionResponse] = None
    xp_awarded: int = 0
    completed_at: datetime
    
class DuelListResponse(BaseModel):
    id: int
    challenger_id: int
    challenger_username: str
    opponent_id: Optional[int] = None
    opponent_username: Optional[str] = None
    status: str
    question_id: int
    question_text: str
    created_at: datetime
    is_bot_opponent: bool = False
    
    model_config = {"from_attributes": True}

class BotOpponentResponse(BaseModel):
    id: int
    username: str
    difficulty_level: int
    response_time_ms: int