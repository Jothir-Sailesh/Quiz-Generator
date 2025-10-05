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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Configuration (in production, use env vars)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_user(username: str, request: Request) -> Optional[UserInDB]:
    """Get user from MongoDB by username"""
    if not request or not hasattr(request, "app"):
        logger.error("get_user: Request or app missing")
        return None
    database = get_database(request.app)
    if database is None:
        logger.error("get_user: database is None")
        return None
    user_data = await database[Collections.USERS].find_one({"username": username})
    if user_data is None:
        return None
    # Convert ObjectId to str for Pydantic
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])
    try:
        return UserInDB(**user_data)
    except Exception as e:
        logger.warning(f"UserInDB validation failed: {e}")
        cleaned = dict(user_data)
        cleaned.pop("_id", None)
        return UserInDB(**cleaned)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str, request: Request) -> Optional[UserInDB]:
    """Authenticate user credentials from MongoDB"""
    user = await get_user(username, request)
    if user is None:
        logger.info(f"authenticate_user: user '{username}' not found")
        return None
    logger.info(f"authenticate_user: user found, username={user.username}, hashed_password={user.hashed_password}")
    password_valid = verify_password(password, user.hashed_password)
    logger.info(f"authenticate_user: password_valid={password_valid}")
    if not password_valid:
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> UserResponse:
    """
    Get current authenticated user from JWT token.
    Note: we require the Request so we can access app state and database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if request is None:
        logger.error("get_current_user: request is None")
        raise credentials_exception

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user(username, request)
    if user is None:
        raise credentials_exception

    # Convert UserInDB -> UserResponse safely
    data = user.dict()
    data.pop("hashed_password", None)
    return UserResponse(**data)


# ---------------------------
# ROUTES
# ---------------------------

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, request: Request):
    """Register a new user account in MongoDB"""
    try:
        logger.info(f"Attempting to register user: {user.username}")
        existing_user = await get_user(user.username, request)
        if existing_user is not None:
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
        logger.info(f"User {user.username} registered successfully, id={inserted_id}")

        # Return response model (ensure _id present when returning)
        user_data["_id"] = str(inserted_id)
        return UserResponse(**user_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.post("/login")
async def login_user(user_credentials: UserLogin, request: Request):
    """Authenticate user and return access token using MongoDB"""
    try:
        logger.info(f"Login attempt for user: {user_credentials.username}")
        user = await authenticate_user(user_credentials.username, user_credentials.password, request)
        if user is None:
            logger.info(f"Login failed for user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logger.info(f"Login successful for user: {user.username}")
        user_response = UserResponse(**user.dict())
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to login user")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@router.get("/verify-token")
async def verify_token(current_user: UserResponse = Depends(get_current_user)):
    """Verify if the provided token is valid"""
    return {"valid": True, "user": current_user.username, "message": "Token is valid"}


# ---------------------------
# DEBUG ROUTES
# ---------------------------

@router.get("/debug/users")
async def debug_list_users(request: Request):
    try:
        db = get_database(request.app)
        users = await db[Collections.USERS].find({}).to_list(length=100)
        for u in users:
            if "_id" in u:
                u["_id"] = str(u["_id"])
        return {"users": users}
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.get("/debug/db-health")
async def debug_db_health(request: Request):
    try:
        db = get_database(request.app)
        await db.command("ping")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"DB health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DB health check failed: {str(e)}")


@router.get("/debug/users-raw")
async def debug_list_users_raw(request: Request):
    try:
        db = get_database(request.app)
        users = await db[Collections.USERS].find({}).to_list(length=100)
        for u in users:
            if "_id" in u:
                u["_id"] = str(u["_id"])
        return {"users": users}
    except Exception as e:
        logger.error(f"Error listing raw users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list raw users: {str(e)}")


# ---------------------------
# TEST USER SETUP
# ---------------------------

@router.on_event("startup")
async def setup_database_and_test_user():
    try:
        await create_indexes()
        logger.info("Database indexes ensured.")
    except Exception as e:
        logger.error(f"Error during startup setup: {str(e)}")


@router.post("/create-test-user")
async def manual_create_test_user(request: Request):
    try:
        logger.info("Starting manual test user creation...")
        await create_test_user(request)
        user = await get_user("testuser", request)
        logger.info(f"Test user fetch after creation: {user}")
        if user is not None:
            logger.info("Manual test user creation succeeded.")
            user_dict = user.dict()
            # Fix ObjectId serialization
            if "id" in user_dict and hasattr(user_dict["id"], "__str__"):
                user_dict["id"] = str(user_dict["id"])
            return {"message": "Test user created or already exists.", "user": user_dict}
        else:
            logger.error("Manual test user creation failed: user not found after creation.")
            return {"message": "Test user creation failed.", "details": "User not found after creation. Check logs for errors."}
    except Exception as e:
        logger.error(f"Manual test user creation failed: {str(e)}")
        return {"message": "Test user creation failed.", "details": str(e)}


async def create_test_user(request: Request):
    """Create a test user for development purposes"""
    try:
        # Defensive: ensure global connection is established
        from backend.database.connection import db_connection
        if db_connection.database is None:
            logger.info("create_test_user: global db_connection not established, connecting...")
            await db_connection.connect()
        test_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        existing = await get_user("testuser", request)
        if existing is None:
            hashed_password = get_password_hash(test_user.password)
            logger.info(f"create_test_user: hashed_password for testuser={hashed_password}")
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
            logger.info(f"Test user created: username='testuser', id={inserted_id}")
        else:
            logger.info("Test user already exists in database.")
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
