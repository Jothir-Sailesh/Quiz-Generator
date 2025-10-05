"""
AI-Enhanced Quiz Generator - Main FastAPI Application
Entry point for the quiz generation system with tree-based question organization.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from database.connection import connect_to_mongo, close_mongo_connection
from routers import auth, quiz, analytics

# Application lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Enable MongoDB connection
    await connect_to_mongo(app)
    print("🚀 Connected to MongoDB")
    yield
    # Shutdown: Enable MongoDB disconnection
    await close_mongo_connection(app)
    print("🔌 Disconnected from MongoDB")

# Initialize FastAPI app
app = FastAPI(
    title="AI-Enhanced Quiz Generator",
    description="A scalable quiz generation system using AI APIs, tree structures, and adaptive learning",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI-Enhanced Quiz Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-quiz-generator"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )