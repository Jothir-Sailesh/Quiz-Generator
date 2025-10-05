"""
Database Connection Module - MongoDB connection and configuration
Handles database connectivity and provides connection utilities.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging
import os
from typing import Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    MongoDB connection manager using Motor (async PyMongo).
    Handles connection lifecycle and provides database access.
    """

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

        # MongoDB configuration (env vars → fallback defaults)
        self.mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "ai_quiz_generator")

    async def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.database = self.client[self.database_name]

            # Test connection
            await self.client.admin.command("ping")
            logger.info(f"✅ Successfully connected to MongoDB at {self.mongo_url}, db='{self.database_name}'")

        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {str(e)}")
            raise

    async def close(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("🔌 MongoDB connection closed")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.database is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return self.database

    def get_collection(self, collection_name: str):
        """Get collection from database"""
        return self.get_database()[collection_name]


# Global DB connection instance
db_connection = DatabaseConnection()


async def connect_to_mongo(app):
    """Connect to MongoDB - called during app startup"""
    await db_connection.connect()
    app.state.db_connection = db_connection


async def close_mongo_connection(app):
    """Close MongoDB connection - called during app shutdown"""
    await db_connection.close()
    if hasattr(app.state, "db_connection"):
        del app.state.db_connection


def get_database(app=None):
    """
    Get database instance for dependency injection or from FastAPI app state
    """
    if app is not None:
        db_conn = getattr(app.state, 'db_connection', None)
        if db_conn is not None:
            return db_conn.get_database()
    # Fallback to global connection
    if db_connection.database is not None:
        return db_connection.get_database()
    raise RuntimeError("Database connection not established. Call connect() first.")


# Collection names
class Collections:
    USERS = "users"
    QUESTIONS = "questions"
    QUIZZES = "quizzes"
    QUIZ_SESSIONS = "quiz_sessions"
    ANALYTICS = "analytics"


async def create_indexes():
    """
    Create database indexes for better performance
    """
    try:
        database = get_database()

        # Users
        users_collection = database[Collections.USERS]
        await users_collection.create_index("username", unique=True)
        await users_collection.create_index("email", unique=True)

        # Questions
        questions_collection = database[Collections.QUESTIONS]
        await questions_collection.create_index(
            [("subject", 1), ("topic", 1), ("difficulty", 1)]
        )
        await questions_collection.create_index("tags")
        await questions_collection.create_index("created_by")

        # Quizzes
        quizzes_collection = database[Collections.QUIZZES]
        await quizzes_collection.create_index("created_by")
        await quizzes_collection.create_index("status")
        await quizzes_collection.create_index("created_at")

        # Quiz sessions
        sessions_collection = database[Collections.QUIZ_SESSIONS]
        await sessions_collection.create_index([("user_id", 1), ("quiz_id", 1)])
        await sessions_collection.create_index("created_at")

        logger.info("✅ Database indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Error creating database indexes: {str(e)}")


async def health_check() -> dict[str, Any]:
    """
    Perform database health check
    """
    try:
        database = get_database()
        await database.command("ping")

        stats = {}
        for collection_name in [Collections.USERS, Collections.QUESTIONS, Collections.QUIZZES]:
            count = await database[collection_name].count_documents({})
            stats[collection_name] = count

        return {
            "status": "healthy",
            "database": db_connection.database_name,
            "collections": stats,
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


class DatabaseOperations:
    """Common database operations for collections"""

    @staticmethod
    async def insert_one(collection_name: str, document: dict) -> str:
        collection = db_connection.get_collection(collection_name)
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    @staticmethod
    async def find_one(collection_name: str, query: dict) -> Optional[dict]:
        collection = db_connection.get_collection(collection_name)
        return await collection.find_one(query)

    @staticmethod
    async def find_many(collection_name: str, query: dict = None, limit: int = None) -> list[dict]:
        collection = db_connection.get_collection(collection_name)
        cursor = collection.find(query or {})
        if limit:
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=None)

    @staticmethod
    async def update_one(collection_name: str, query: dict, update: dict) -> bool:
        collection = db_connection.get_collection(collection_name)
        result = await collection.update_one(query, {"$set": update})
        return result.modified_count > 0

    @staticmethod
    async def delete_one(collection_name: str, query: dict) -> bool:
        collection = db_connection.get_collection(collection_name)
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    @staticmethod
    async def count_documents(collection_name: str, query: dict = None) -> int:
        collection = db_connection.get_collection(collection_name)
        return await collection.count_documents(query or {})
