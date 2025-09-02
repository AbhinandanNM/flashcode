from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class LanguageEnum(str, enum.Enum):
    PYTHON = "python"
    CPP = "cpp"


class QuestionTypeEnum(str, enum.Enum):
    MCQ = "mcq"
    FILL_BLANK = "fill_blank"
    FLASHCARD = "flashcard"
    CODE = "code"


class ProgressStatusEnum(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DuelStatusEnum(str, enum.Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    xp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    joined_on = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    progress = relationship("Progress", back_populates="user")
    question_attempts = relationship("QuestionAttempt", back_populates="user")
    challenger_duels = relationship("Duel", foreign_keys="Duel.challenger_id", back_populates="challenger")
    opponent_duels = relationship("Duel", foreign_keys="Duel.opponent_id", back_populates="opponent")
    won_duels = relationship("Duel", foreign_keys="Duel.winner_id", back_populates="winner")


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    language = Column(Enum(LanguageEnum), nullable=False)
    title = Column(String(200), nullable=False)
    theory = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-5 scale
    xp_reward = Column(Integer, nullable=False)
    order_index = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    questions = relationship("Question", back_populates="lesson")
    progress = relationship("Progress", back_populates="lesson")


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    type = Column(Enum(QuestionTypeEnum), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For MCQ questions
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(Integer, nullable=False)  # 1-5 scale
    xp_reward = Column(Integer, nullable=False)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question")
    duels = relationship("Duel", back_populates="question")


class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    status = Column(Enum(ProgressStatusEnum), default=ProgressStatusEnum.NOT_STARTED)
    score = Column(Float, default=0.0)  # 0.0-1.0
    attempts = Column(Integer, default=0)
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    next_review = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=False)  # seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="question_attempts")
    question = relationship("Question", back_populates="attempts")


class Duel(Base):
    __tablename__ = "duels"
    
    id = Column(Integer, primary_key=True, index=True)
    challenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opponent_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable for bots
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    status = Column(Enum(DuelStatusEnum), default=DuelStatusEnum.WAITING)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    challenger = relationship("User", foreign_keys=[challenger_id], back_populates="challenger_duels")
    opponent = relationship("User", foreign_keys=[opponent_id], back_populates="opponent_duels")
    winner = relationship("User", foreign_keys=[winner_id], back_populates="won_duels")
    question = relationship("Question", back_populates="duels")