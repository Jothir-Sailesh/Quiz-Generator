"""
Quiz Model - Defines quiz session structure and management
Handles quiz creation, sequencing, and performance tracking.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId
from .question import QuestionResponse, DifficultyLevel

class QuizStatus(str, Enum):
    """Quiz session status"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"

class PyObjectId(ObjectId):
    """Custom ObjectId field for Pydantic models"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class QuizAnswer(BaseModel):
    """Individual quiz answer"""
    question_id: str
    user_answer: Any  # Can be string, list, or boolean depending on question type
    is_correct: bool
    time_taken: float  # Time in seconds
    answered_at: datetime = Field(default_factory=datetime.utcnow)

class QuizConfiguration(BaseModel):
    """Quiz configuration settings"""
    subject: str
    topics: List[str] = Field(default_factory=list)
    difficulty_levels: List[DifficultyLevel] = Field(default_factory=list)
    question_count: int = Field(default=5, ge=1, le=50)
    time_limit: Optional[int] = None  # Time limit in minutes
    randomize_questions: bool = True
    randomize_options: bool = True
    adaptive_difficulty: bool = True

class QuizBase(BaseModel):
    """Base quiz model"""
    title: str
    description: Optional[str] = None
    configuration: QuizConfiguration

class QuizCreate(QuizBase):
    """Quiz creation model"""
    source_text: Optional[str] = None  # Text used for AI question generation

class QuizResponse(QuizBase):
    """Quiz response model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # User ID
    status: QuizStatus = QuizStatus.CREATED
    questions: List[QuestionResponse] = Field(default_factory=list)
    current_question_index: int = 0
    answers: List[QuizAnswer] = Field(default_factory=list)
    score: float = 0.0
    total_time: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QuizSession(BaseModel):
    """Active quiz session model"""
    quiz_id: str
    user_id: str
    current_question: Optional[QuestionResponse] = None
    remaining_questions: int = 0
    elapsed_time: float = 0.0
    performance_trend: List[float] = Field(default_factory=list)  # For adaptive difficulty

class QuizStats(BaseModel):
    """Quiz performance statistics"""
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    accuracy: float
    average_time_per_question: float
    difficulty_breakdown: Dict[str, int]
    topic_performance: Dict[str, float]