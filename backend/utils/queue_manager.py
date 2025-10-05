"""
Queue Manager - Implements Deque-based question sequencing
Manages question ordering, adaptive difficulty adjustment, and quiz flow.
"""

from collections import deque
from typing import List, Optional, Dict, Any
from backend.models.question import QuestionResponse, DifficultyLevel
from backend.utils.dynamic_programming import DifficultyOptimizer
import random

class QuestionQueue:
    """
    Deque-based question queue for efficient question sequencing
    Supports priority insertion, adaptive reordering, and performance tracking
    """
    
    def __init__(self, adaptive_mode: bool = True):
        self.queue = deque()
        self.adaptive_mode = adaptive_mode
        self.difficulty_optimizer = DifficultyOptimizer()
        self.answered_questions = []
        self.performance_history = []
        
        # Queue statistics
        self.stats = {
            'total_added': 0,
            'total_served': 0,
            'current_size': 0,
            'difficulty_distribution': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0,
                'expert': 0
            }
        }
    
    def add_questions(self, questions: List[QuestionResponse], randomize: bool = True):
        """
        Add multiple questions to the queue
        Optionally randomizes order for variety
        """
        question_list = questions.copy()
        
        if randomize:
            random.shuffle(question_list)
        
        for question in question_list:
            self.queue.append(question)
            self.stats['total_added'] += 1
            self.stats['difficulty_distribution'][question.difficulty.value] += 1
        
        self._update_stats()
    
    def add_question_priority(self, question: QuestionResponse, priority: str = "high"):
        """
        Add a question with priority positioning
        'high' priority adds to front, 'low' priority adds to back
        """
        if priority == "high":
            self.queue.appendleft(question)
        else:
            self.queue.append(question)
        
        self.stats['total_added'] += 1
        self.stats['difficulty_distribution'][question.difficulty.value] += 1
        self._update_stats()
    
    def get_next_question(self) -> Optional[QuestionResponse]:
        """
        Get the next question from the queue
        Applies adaptive difficulty adjustments if enabled
        """
        if not self.queue:
            return None
        
        # If adaptive mode is enabled and we have performance history
        if self.adaptive_mode and self.performance_history:
            self._apply_adaptive_ordering()
        
        question = self.queue.popleft()
        self.stats['total_served'] += 1
        self._update_stats()
        
        return question
    
    def peek_next_question(self) -> Optional[QuestionResponse]:
        """
        Preview the next question without removing it from queue
        """
        if not self.queue:
            return None
        return self.queue[0]
    
    def peek_questions(self, count: int) -> List[QuestionResponse]:
        """
        Preview multiple upcoming questions without removing them
        """
        return list(self.queue)[:count]
    
    def record_answer(self, question: QuestionResponse, is_correct: bool, time_taken: float):
        """
        Record an answer for adaptive difficulty optimization
        """
        answer_record = {
            'question': question,
            'is_correct': is_correct,
            'time_taken': time_taken,
            'difficulty': question.difficulty
        }
        
        self.answered_questions.append(answer_record)
        self.performance_history.append(1.0 if is_correct else 0.0)
        
        # Keep only recent performance for adaptive adjustments
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)
    
    def _apply_adaptive_ordering(self):
        """
        Apply adaptive difficulty ordering based on performance
        Uses Dynamic Programming for optimal difficulty progression
        """
        if len(self.performance_history) < 3:
            return
        
        # Calculate current performance trend
        recent_performance = sum(self.performance_history[-3:]) / 3
        
        # Get optimal next difficulty from DP algorithm
        current_difficulty = self._get_current_difficulty_level()
        optimal_difficulty = self.difficulty_optimizer.get_optimal_next_difficulty(
            current_difficulty, recent_performance
        )
        
        # Reorder queue to prioritize optimal difficulty questions
        self._reorder_by_difficulty(optimal_difficulty)
    
    def _reorder_by_difficulty(self, target_difficulty: DifficultyLevel):
        """
        Reorder queue to prioritize questions of target difficulty
        """
        queue_list = list(self.queue)
        self.queue.clear()
        
        # Separate questions by difficulty match
        target_questions = []
        other_questions = []
        
        for question in queue_list:
            if question.difficulty == target_difficulty:
                target_questions.append(question)
            else:
                other_questions.append(question)
        
        # Add target difficulty questions first
        for question in target_questions:
            self.queue.append(question)
        
        # Add remaining questions
        for question in other_questions:
            self.queue.append(question)
    
    def _get_current_difficulty_level(self) -> DifficultyLevel:
        """
        Determine current difficulty level based on recent questions
        """
        if not self.answered_questions:
            return DifficultyLevel.INTERMEDIATE
        
        # Use the difficulty of the most recent question
        return self.answered_questions[-1]['difficulty']
    
    def _update_stats(self):
        """Update queue statistics"""
        self.stats['current_size'] = len(self.queue)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get comprehensive queue status and statistics
        """
        return {
            'queue_size': len(self.queue),
            'performance_trend': self.performance_history[-5:] if self.performance_history else [],
            'adaptive_mode': self.adaptive_mode,
            'stats': self.stats,
            'next_difficulties': [q.difficulty.value for q in list(self.queue)[:5]]
        }
    
    def clear_queue(self):
        """Clear all questions from the queue"""
        self.queue.clear()
        self.answered_questions.clear()
        self.performance_history.clear()
        self._reset_stats()
    
    def _reset_stats(self):
        """Reset queue statistics"""
        self.stats = {
            'total_added': 0,
            'total_served': 0,
            'current_size': 0,
            'difficulty_distribution': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0,
                'expert': 0
            }
        }
    
    def shuffle_queue(self):
        """Randomly shuffle the current queue"""
        queue_list = list(self.queue)
        random.shuffle(queue_list)
        self.queue = deque(queue_list)
    
    def insert_at_position(self, question: QuestionResponse, position: int):
        """Insert a question at a specific position in the queue"""
        if position < 0 or position > len(self.queue):
            position = len(self.queue)
        
        queue_list = list(self.queue)
        queue_list.insert(position, question)
        self.queue = deque(queue_list)
        
        self.stats['total_added'] += 1
        self.stats['difficulty_distribution'][question.difficulty.value] += 1
        self._update_stats()