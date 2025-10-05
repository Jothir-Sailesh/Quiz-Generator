"""
Authentication Router - User authentication and authorization
Handles user registration, login, and JWT token management.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional, Dict, Any
import logging

from backend.models.user import UserCreate, UserResponse, UserLogin, UserInDB
from backend.database.connection import get_database, Collections, DatabaseOperations, create_indexes

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Password & security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
async def get_user(username: str, request: Request) -> Optional[UserInDB]:
    db = get_database(request.app)
    if db is None:
        logger.error("get_user: Database not initialized")
        return None
    user_data = await db[Collections.USERS].find_one({"username": username})
    if not user_data:
        return None
    user_data["_id"] = str(user_data["_id"])
    return UserInDB(**user_data)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str, request: Request) -> Optional[UserInDB]:
    user = await get_user(username, request)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> UserResponse:
    if request is None:
        raise HTTPException(status_code=401, detail="Request object required")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await get_user(username, request)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user_dict = user.dict()
    user_dict.pop("hashed_password", None)
    return UserResponse(**user_dict)


# ---------------------------
# ROUTES
# ---------------------------
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, request: Request):
    existing_user = await get_user(user.username, request)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "quiz_history": [],
        "performance_stats": {}
    }
    inserted_id = await DatabaseOperations.insert_one(Collections.USERS, user_data)
    user_data["_id"] = str(inserted_id)
    return UserResponse(**user_data)


@router.post("/login")
async def login_user(user_credentials: UserLogin, request: Request):
    user = await authenticate_user(user_credentials.username, user_credentials.password, request)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_response = UserResponse(**user.dict())
    return {"access_token": access_token, "token_type": "bearer", "user": user_response}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.get("/verify-token")
async def verify_token(current_user: UserResponse = Depends(get_current_user)):
    return {"valid": True, "user": current_user.username}


# ---------------------------
# TEST / DEBUG ROUTES
# ---------------------------
@router.on_event("startup")
async def setup_database_and_test_user():
    await create_indexes()


@router.post("/create-test-user")
async def manual_create_test_user(request: Request):
    from backend.models.user import UserCreate
    test_user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    existing = await get_user("testuser", request)
    if not existing:
        hashed_password = get_password_hash(test_user.password)
        user_data = {
            "username": test_user.username,
            "email": test_user.email,
            "full_name": test_user.full_name,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "quiz_history": [],
            "performance_stats": {}
        }
        inserted_id = await DatabaseOperations.insert_one(Collections.USERS, user_data)
        return {"message": "Test user created", "user_id": str(inserted_id)}
    return {"message": "Test user already exists"}
