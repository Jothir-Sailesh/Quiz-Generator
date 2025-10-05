"""
Quiz Router - API endpoints for quiz management and generation
Handles quiz creation, question serving, answer submission, and progress tracking.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from backend.models.quiz import QuizCreate, QuizResponse, QuizSession, QuizStats, QuizConfiguration
from backend.models.question import QuestionResponse, DifficultyLevel, QuestionFilter
from backend.services.ai_service import AIQuestionGenerator
from backend.utils.tree_structure import QuestionTree
from backend.utils.queue_manager import QuestionQueue
from backend.database.connection import get_database
from backend.routers.auth import get_current_user
from backend.models.user import UserResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (in production, these should be managed differently)
question_tree = QuestionTree()
active_sessions: Dict[str, QuestionQueue] = {}

@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    quiz_data: QuizCreate,
    current_user: UserResponse = Depends(get_current_user),
    ai_api_key: Optional[str] = Query(None, description="OpenAI API Key for question generation")
):
    """
    Generate a new quiz from text input using AI
    Main workflow endpoint that demonstrates the complete system
    """
    try:
        logger.info(f"Generating quiz for user {current_user.username}")
        
        # Initialize AI service
        ai_service = AIQuestionGenerator(api_key=ai_api_key, provider="openai")
        
        # Extract configuration
        config = quiz_data.configuration
        
        # Generate questions from source text if provided
        questions = []
        if quiz_data.source_text:
            logger.info("Generating questions from source text using AI")
            ai_questions = await ai_service.generate_questions_from_text(
                text=quiz_data.source_text,
                question_count=config.question_count,
                subject=config.subject,
                difficulty_preference=config.difficulty_levels[0] if config.difficulty_levels else None
            )
            
            # Convert AI questions to QuestionResponse objects
            for ai_q in ai_questions:
                question_response = QuestionResponse(
                    text=ai_q.text,
                    question_type=ai_q.question_type,
                    subject=ai_q.subject,
                    topic=ai_q.topic,
                    difficulty=ai_q.difficulty,
                    options=ai_q.options,
                    correct_answer=ai_q.correct_answer,
                    explanation=ai_q.explanation,
                    created_by=str(current_user.id),
                    ai_generated=ai_q.ai_generated
                )
                questions.append(question_response)
                
                # Add question to tree structure
                question_tree.add_question(question_response)
        else:
            # Retrieve questions from existing tree based on criteria
            logger.info("Retrieving questions from question tree")
            filter_criteria = QuestionFilter(
                subject=config.subject if config.subject != "General" else None,
                difficulty=config.difficulty_levels[0] if config.difficulty_levels else None
            )
            
            questions = question_tree.get_questions_by_criteria(
                subject=filter_criteria.subject,
                difficulty=filter_criteria.difficulty,
                limit=config.question_count
            )
            
            # If no questions found, generate mock questions
            if not questions:
                logger.info("No existing questions found, generating mock questions")
                mock_text = f"This is sample content for {config.subject} quiz generation."
                ai_questions = await ai_service.generate_questions_from_text(
                    text=mock_text,
                    question_count=config.question_count,
                    subject=config.subject
                )
                
                for ai_q in ai_questions:
                    question_response = QuestionResponse(
                        text=ai_q.text,
                        question_type=ai_q.question_type,
                        subject=ai_q.subject,
                        topic=ai_q.topic,
                        difficulty=ai_q.difficulty,
                        options=ai_q.options,
                        correct_answer=ai_q.correct_answer,
                        explanation=ai_q.explanation,
                        created_by=str(current_user.id),
                        ai_generated=ai_q.ai_generated
                    )
                    questions.append(question_response)
                    question_tree.add_question(question_response)
        
        # Create quiz response object
        quiz = QuizResponse(
            title=quiz_data.title,
            description=quiz_data.description,
            configuration=config,
            created_by=str(current_user.id),
            questions=questions
        )
        
        # Initialize question queue for this quiz session
        session_id = str(quiz.id)
        question_queue = QuestionQueue(adaptive_mode=config.adaptive_difficulty)
        question_queue.add_questions(questions, randomize=config.randomize_questions)
        active_sessions[session_id] = question_queue
        
        logger.info(f"Quiz generated successfully with {len(questions)} questions")
        
        return quiz
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.get("/quiz/{quiz_id}/next-question")
async def get_next_question(
    quiz_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the next question from the quiz queue
    Demonstrates queue management and adaptive difficulty
    """
    try:
        # Get question queue for this session
        question_queue = active_sessions.get(quiz_id)
        if not question_queue:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        # Get next question from queue
        next_question = question_queue.get_next_question()
        if not next_question:
            return {
                "question": None,
                "message": "Quiz completed",
                "queue_status": question_queue.get_queue_status()
            }
        
        # Return question without revealing correct answer
        question_data = {
            "id": str(next_question.id),
            "text": next_question.text,
            "question_type": next_question.question_type,
            "options": [
                {"text": opt.text} for opt in next_question.options
            ] if next_question.options else None,
            "difficulty": next_question.difficulty,
            "topic": next_question.topic,
            "remaining_questions": len(question_queue.queue)
        }
        
        return {
            "question": question_data,
            "queue_status": question_queue.get_queue_status()
        }
        
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/{quiz_id}/submit-answer")
async def submit_answer(
    quiz_id: str,
    answer_data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Submit an answer and get immediate feedback
    Updates adaptive difficulty based on performance
    """
    try:
        # Get question queue for this session
        question_queue = active_sessions.get(quiz_id)
        if not question_queue:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        question_id = answer_data.get("question_id")
        user_answer = answer_data.get("answer")
        time_taken = answer_data.get("time_taken", 0)
        
        # Find the question in the tree to check correct answer
        all_questions = question_tree.get_questions_by_criteria()
        question = next((q for q in all_questions if str(q.id) == question_id), None)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Evaluate answer
        is_correct = False
        if question.question_type.value == "multiple_choice":
            # Find correct option
            correct_option = next((opt for opt in question.options if opt.is_correct), None)
            if correct_option:
                is_correct = user_answer == correct_option.text
        elif question.question_type.value == "true_false":
            is_correct = user_answer.lower() == question.correct_answer.lower()
        else:
            # For other types, simple string comparison
            is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
        
        # Record answer in queue for adaptive learning
        question_queue.record_answer(question, is_correct, time_taken)
        
        # Prepare feedback response
        feedback = {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer if question.correct_answer else None,
            "explanation": question.explanation,
            "time_taken": time_taken,
            "queue_status": question_queue.get_queue_status()
        }
        
        # Add correct option for multiple choice
        if question.question_type.value == "multiple_choice":
            correct_option = next((opt for opt in question.options if opt.is_correct), None)
            if correct_option:
                feedback["correct_option"] = correct_option.text
        
        return feedback
        
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quiz/{quiz_id}/stats")
async def get_quiz_stats(
    quiz_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get comprehensive quiz statistics and performance analytics
    """
    try:
        question_queue = active_sessions.get(quiz_id)
        if not question_queue:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        # Calculate performance statistics
        answered_questions = question_queue.answered_questions
        if not answered_questions:
            return {"message": "No answers submitted yet"}
        
        total_questions = len(answered_questions)
        correct_answers = sum(1 for ans in answered_questions if ans['is_correct'])
        incorrect_answers = total_questions - correct_answers
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        total_time = sum(ans['time_taken'] for ans in answered_questions)
        avg_time = total_time / total_questions if total_questions > 0 else 0
        
        # Difficulty breakdown
        difficulty_breakdown = {}
        topic_performance = {}
        
        for ans in answered_questions:
            diff = ans['difficulty'].value
            topic = ans['question'].topic
            
            # Difficulty breakdown
            if diff not in difficulty_breakdown:
                difficulty_breakdown[diff] = {'correct': 0, 'total': 0}
            difficulty_breakdown[diff]['total'] += 1
            if ans['is_correct']:
                difficulty_breakdown[diff]['correct'] += 1
            
            # Topic performance
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if ans['is_correct']:
                topic_performance[topic]['correct'] += 1
        
        # Convert to percentages for topic performance
        topic_percentages = {}
        for topic, stats in topic_performance.items():
            topic_percentages[topic] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        stats = QuizStats(
            total_questions=total_questions,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            accuracy=accuracy,
            average_time_per_question=avg_time,
            difficulty_breakdown=difficulty_breakdown,
            topic_performance=topic_percentages
        )
        
        return {
            "quiz_stats": stats,
            "performance_trend": question_queue.performance_history,
            "queue_status": question_queue.get_queue_status()
        }
        
    except Exception as e:
        logger.error(f"Error getting quiz stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/tree-structure")
async def get_question_tree_structure(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the complete question tree structure for navigation
    """
    try:
        structure = question_tree.get_tree_structure()
        stats = question_tree.get_statistics()
        
        return {
            "tree_structure": structure,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting tree structure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/search")
async def search_questions(
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    difficulty: Optional[DifficultyLevel] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Search questions using the tree structure with flexible criteria
    """
    try:
        questions = question_tree.get_questions_by_criteria(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            limit=limit
        )
        
        return {
            "questions": questions,
            "total_found": len(questions),
            "search_criteria": {
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty.value if difficulty else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/quiz/{quiz_id}/session")
async def end_quiz_session(
    quiz_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    End a quiz session and clean up resources
    """
    try:
        if quiz_id in active_sessions:
            del active_sessions[quiz_id]
            return {"message": "Quiz session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Quiz session not found")
            
    except Exception as e:
        logger.error(f"Error ending quiz session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))