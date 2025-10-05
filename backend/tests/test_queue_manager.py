"""
Unit tests for queue manager implementation
Tests the deque-based question sequencing functionality.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.queue_manager import QuestionQueue
from backend.models.question import QuestionResponse, DifficultyLevel, QuestionType, QuestionOption

class TestQuestionQueue:
    """Test cases for QuestionQueue class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.queue = QuestionQueue(adaptive_mode=True)
        
        # Create sample questions with different difficulties
        self.beginner_question = QuestionResponse(
            text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            subject="Mathematics",
            topic="Basic Math",
            difficulty=DifficultyLevel.BEGINNER,
            options=[
                QuestionOption(text="3", is_correct=False),
                QuestionOption(text="4", is_correct=True),
                QuestionOption(text="5", is_correct=False),
                QuestionOption(text="6", is_correct=False)
            ]
        )
        
        self.intermediate_question = QuestionResponse(
            text="What is the quadratic formula?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            subject="Mathematics",
            topic="Algebra",
            difficulty=DifficultyLevel.INTERMEDIATE,
            options=[
                QuestionOption(text="ax² + bx + c", is_correct=False),
                QuestionOption(text="(-b ± √(b²-4ac))/2a", is_correct=True),
                QuestionOption(text="a² + b² = c²", is_correct=False),
                QuestionOption(text="y = mx + b", is_correct=False)
            ]
        )
        
        self.advanced_question = QuestionResponse(
            text="What is the derivative of ln(x)?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            subject="Mathematics",
            topic="Calculus",
            difficulty=DifficultyLevel.ADVANCED,
            options=[
                QuestionOption(text="1/x", is_correct=True),
                QuestionOption(text="x", is_correct=False),
                QuestionOption(text="ln(x)", is_correct=False),
                QuestionOption(text="e^x", is_correct=False)
            ]
        )
    
    def test_queue_initialization(self):
        """Test queue initialization"""
        assert len(self.queue.queue) == 0
        assert self.queue.adaptive_mode == True
        assert self.queue.stats['total_added'] == 0
        assert self.queue.stats['total_served'] == 0
    
    def test_add_questions(self):
        """Test adding multiple questions to queue"""
        questions = [self.beginner_question, self.intermediate_question, self.advanced_question]
        
        self.queue.add_questions(questions, randomize=False)
        
        assert len(self.queue.queue) == 3
        assert self.queue.stats['total_added'] == 3
        assert self.queue.stats['current_size'] == 3
        
        # Check difficulty distribution
        assert self.queue.stats['difficulty_distribution']['beginner'] == 1
        assert self.queue.stats['difficulty_distribution']['intermediate'] == 1
        assert self.queue.stats['difficulty_distribution']['advanced'] == 1
    
    def test_add_question_priority(self):
        """Test adding questions with priority"""
        self.queue.add_questions([self.intermediate_question], randomize=False)
        
        # Add high priority question (should go to front)
        self.queue.add_question_priority(self.beginner_question, priority="high")
        
        # Add low priority question (should go to back)  
        self.queue.add_question_priority(self.advanced_question, priority="low")
        
        assert len(self.queue.queue) == 3
        
        # Check order: high priority should be first
        first_question = self.queue.queue[0]
        assert first_question == self.beginner_question
        
        # Last should be low priority
        last_question = self.queue.queue[-1]
        assert last_question == self.advanced_question
    
    def test_get_next_question(self):
        """Test getting next question from queue"""
        questions = [self.beginner_question, self.intermediate_question]
        self.queue.add_questions(questions, randomize=False)
        
        # Get first question
        next_question = self.queue.get_next_question()
        assert next_question == self.beginner_question
        assert len(self.queue.queue) == 1
        assert self.queue.stats['total_served'] == 1
        
        # Get second question
        next_question = self.queue.get_next_question()
        assert next_question == self.intermediate_question
        assert len(self.queue.queue) == 0
        
        # Try to get question from empty queue
        next_question = self.queue.get_next_question()
        assert next_question is None
    
    def test_peek_next_question(self):
        """Test peeking at next question without removing it"""
        self.queue.add_questions([self.beginner_question, self.intermediate_question], randomize=False)
        
        # Peek at next question
        peeked_question = self.queue.peek_next_question()
        assert peeked_question == self.beginner_question
        assert len(self.queue.queue) == 2  # Should not remove question
        
        # Peek again, should be same question
        peeked_again = self.queue.peek_next_question()
        assert peeked_again == self.beginner_question
    
    def test_peek_questions(self):
        """Test peeking at multiple questions"""
        questions = [self.beginner_question, self.intermediate_question, self.advanced_question]
        self.queue.add_questions(questions, randomize=False)
        
        # Peek at first 2 questions
        peeked_questions = self.queue.peek_questions(2)
        assert len(peeked_questions) == 2
        assert peeked_questions[0] == self.beginner_question
        assert peeked_questions[1] == self.intermediate_question
        
        # Original queue should be unchanged
        assert len(self.queue.queue) == 3
    
    def test_record_answer(self):
        """Test recording answers for adaptive learning"""
        # Record a correct answer
        self.queue.record_answer(self.beginner_question, is_correct=True, time_taken=5.0)
        
        assert len(self.queue.answered_questions) == 1
        assert len(self.queue.performance_history) == 1
        assert self.queue.performance_history[0] == 1.0
        
        answer_record = self.queue.answered_questions[0]
        assert answer_record['question'] == self.beginner_question
        assert answer_record['is_correct'] == True
        assert answer_record['time_taken'] == 5.0
        assert answer_record['difficulty'] == DifficultyLevel.BEGINNER
        
        # Record an incorrect answer
        self.queue.record_answer(self.intermediate_question, is_correct=False, time_taken=10.0)
        
        assert len(self.queue.answered_questions) == 2
        assert len(self.queue.performance_history) == 2
        assert self.queue.performance_history[1] == 0.0
    
    def test_get_queue_status(self):
        """Test getting queue status"""
        questions = [self.beginner_question, self.intermediate_question]
        self.queue.add_questions(questions, randomize=False)
        
        # Record some performance
        self.queue.record_answer(self.beginner_question, is_correct=True, time_taken=5.0)
        
        status = self.queue.get_queue_status()
        
        assert status['queue_size'] == 2
        assert status['adaptive_mode'] == True
        assert len(status['performance_trend']) == 1
        assert status['performance_trend'][0] == 1.0
        assert 'stats' in status
        assert 'next_difficulties' in status
    
    def test_clear_queue(self):
        """Test clearing the queue"""
        questions = [self.beginner_question, self.intermediate_question]
        self.queue.add_questions(questions, randomize=False)
        self.queue.record_answer(self.beginner_question, is_correct=True, time_taken=5.0)
        
        # Clear queue
        self.queue.clear_queue()
        
        assert len(self.queue.queue) == 0
        assert len(self.queue.answered_questions) == 0
        assert len(self.queue.performance_history) == 0
        assert self.queue.stats['total_added'] == 0
        assert self.queue.stats['total_served'] == 0
    
    def test_shuffle_queue(self):
        """Test shuffling queue order"""
        questions = [self.beginner_question, self.intermediate_question, self.advanced_question]
        self.queue.add_questions(questions, randomize=False)
        
        # Get original order
        original_order = list(self.queue.queue)
        
        # Shuffle (may or may not change order, but should not crash)
        self.queue.shuffle_queue()
        
        # Queue size should remain the same
        assert len(self.queue.queue) == 3
        
        # All original questions should still be present
        shuffled_questions = list(self.queue.queue)
        for question in original_order:
            assert question in shuffled_questions
    
    def test_insert_at_position(self):
        """Test inserting question at specific position"""
        self.queue.add_questions([self.beginner_question, self.advanced_question], randomize=False)
        
        # Insert intermediate question at position 1
        self.queue.insert_at_position(self.intermediate_question, 1)
        
        assert len(self.queue.queue) == 3
        assert self.queue.queue[1] == self.intermediate_question
        
        # Test inserting at invalid position (should append to end)
        extra_question = QuestionResponse(
            text="Extra question",
            question_type=QuestionType.TRUE_FALSE,
            subject="Test",
            topic="Test",
            difficulty=DifficultyLevel.BEGINNER,
            correct_answer="true"
        )
        
        self.queue.insert_at_position(extra_question, 100)
        assert self.queue.queue[-1] == extra_question
    
    def test_adaptive_mode_disabled(self):
        """Test queue behavior with adaptive mode disabled"""
        non_adaptive_queue = QuestionQueue(adaptive_mode=False)
        questions = [self.beginner_question, self.intermediate_question, self.advanced_question]
        
        non_adaptive_queue.add_questions(questions, randomize=False)
        
        # Record some answers (should not affect order since adaptive mode is off)
        non_adaptive_queue.record_answer(self.beginner_question, is_correct=False, time_taken=5.0)
        non_adaptive_queue.record_answer(self.intermediate_question, is_correct=False, time_taken=5.0)
        
        # Get questions in original order
        first = non_adaptive_queue.get_next_question()
        second = non_adaptive_queue.get_next_question()
        third = non_adaptive_queue.get_next_question()
        
        assert first == self.beginner_question
        assert second == self.intermediate_question  
        assert third == self.advanced_question

if __name__ == "__main__":
    pytest.main([__file__])