"""
User Model - Defines user data structure and validation
Handles user authentication and profile management for the quiz system.
"""

from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Custom ObjectId field for Pydantic models"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema.update(type="string")
        return schema


class UserBase(BaseModel):
    """Base user model with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model with password"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """User response model (without password)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    quiz_history: List[str] = Field(default_factory=list)
    performance_stats: Dict = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserInDB(UserResponse):
    """User model as stored in database (with hashed password)"""
    hashed_password: str


class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str
