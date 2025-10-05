"""
Question Model - Defines question data structure for the quiz system
Supports multiple question types and difficulty levels with AI-generated content.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class DifficultyLevel(str, Enum):
    """Question difficulty levels for adaptive learning"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuestionType(str, Enum):
    """Supported question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_BLANK = "fill_blank"

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

class QuestionOption(BaseModel):
    """Individual question option for multiple choice questions"""
    text: str
    is_correct: bool = False
    explanation: Optional[str] = None

class QuestionBase(BaseModel):
    """Base question model"""
    text: str = Field(..., min_length=10)
    question_type: QuestionType
    subject: str
    topic: str
    difficulty: DifficultyLevel
    options: List[QuestionOption] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
class QuestionCreate(QuestionBase):
    """Question creation model"""
    source_text: Optional[str] = None  # Original text used to generate question
    ai_generated: bool = False
    
class QuestionResponse(QuestionBase):
    """Question response model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID who created the question
    usage_count: int = 0
    success_rate: float = 0.0  # Percentage of correct answers
    ai_generated: bool = False
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QuestionUpdate(BaseModel):
    """Question update model"""
    text: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    options: Optional[List[QuestionOption]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    tags: Optional[List[str]] = None

class QuestionFilter(BaseModel):
    """Question filtering model for search and organization"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    question_type: Optional[QuestionType] = None
    tags: Optional[List[str]] = None
    ai_generated: Optional[bool] = None