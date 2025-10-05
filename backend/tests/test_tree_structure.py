"""
Unit tests for tree structure implementation
Tests the hierarchical question organization functionality.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.tree_structure import QuestionTree, QuestionNode
from backend.models.question import QuestionResponse, DifficultyLevel, QuestionType, QuestionOption

class TestQuestionNode:
    """Test cases for QuestionNode class"""
    
    def test_node_creation(self):
        """Test basic node creation"""
        node = QuestionNode("Mathematics", "subject")
        assert node.value == "Mathematics"
        assert node.node_type == "subject"
        assert len(node.children) == 0
        assert len(node.questions) == 0
        assert node.metadata['count'] == 0
    
    def test_add_child(self):
        """Test adding child nodes"""
        parent = QuestionNode("Mathematics", "subject")
        child = QuestionNode("Algebra", "topic")
        
        parent.add_child("algebra", child)
        
        assert len(parent.children) == 1
        assert parent.get_child("algebra") == child
        assert parent.metadata['count'] == 1
    
    def test_get_all_questions(self):
        """Test getting all questions from a node and its children"""
        # Create mock question
        question = QuestionResponse(
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
        
        parent = QuestionNode("Mathematics", "subject")
        child = QuestionNode("Basic Math", "topic")
        child.questions.append(question)
        parent.add_child("basic_math", child)
        
        all_questions = parent.get_all_questions()
        assert len(all_questions) == 1
        assert all_questions[0] == question

class TestQuestionTree:
    """Test cases for QuestionTree class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.tree = QuestionTree()
        
        # Create sample questions
        self.math_question = QuestionResponse(
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
        
        self.physics_question = QuestionResponse(
            text="What is the speed of light?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            subject="Physics",
            topic="Constants",
            difficulty=DifficultyLevel.INTERMEDIATE,
            options=[
                QuestionOption(text="300,000 km/s", is_correct=True),
                QuestionOption(text="150,000 km/s", is_correct=False),
                QuestionOption(text="450,000 km/s", is_correct=False),
                QuestionOption(text="600,000 km/s", is_correct=False)
            ]
        )
    
    def test_tree_initialization(self):
        """Test tree initialization"""
        assert self.tree.root.node_type == "root"
        assert self.tree.total_questions == 0
    
    def test_add_question(self):
        """Test adding questions to the tree"""
        self.tree.add_question(self.math_question)
        
        assert self.tree.total_questions == 1
        
        # Check tree structure
        math_subject = self.tree.root.get_child("Mathematics")
        assert math_subject is not None
        assert math_subject.value == "Mathematics"
        
        basic_math_topic = math_subject.get_child("Basic Math")
        assert basic_math_topic is not None
        assert basic_math_topic.value == "Basic Math"
        
        beginner_difficulty = basic_math_topic.get_child("beginner")
        assert beginner_difficulty is not None
        assert len(beginner_difficulty.questions) == 1
        assert beginner_difficulty.questions[0] == self.math_question
    
    def test_get_questions_by_subject(self):
        """Test retrieving questions by subject"""
        self.tree.add_question(self.math_question)
        self.tree.add_question(self.physics_question)
        
        math_questions = self.tree.get_questions_by_criteria(subject="Mathematics")
        assert len(math_questions) == 1
        assert math_questions[0] == self.math_question
        
        physics_questions = self.tree.get_questions_by_criteria(subject="Physics")
        assert len(physics_questions) == 1
        assert physics_questions[0] == self.physics_question
    
    def test_get_questions_by_difficulty(self):
        """Test retrieving questions by difficulty"""
        self.tree.add_question(self.math_question)
        self.tree.add_question(self.physics_question)
        
        beginner_questions = self.tree.get_questions_by_criteria(
            difficulty=DifficultyLevel.BEGINNER
        )
        assert len(beginner_questions) == 1
        assert beginner_questions[0] == self.math_question
        
        intermediate_questions = self.tree.get_questions_by_criteria(
            difficulty=DifficultyLevel.INTERMEDIATE
        )
        assert len(intermediate_questions) == 1
        assert intermediate_questions[0] == self.physics_question
    
    def test_get_questions_by_multiple_criteria(self):
        """Test retrieving questions with multiple criteria"""
        self.tree.add_question(self.math_question)
        self.tree.add_question(self.physics_question)
        
        # Add another math question with different difficulty
        advanced_math_question = QuestionResponse(
            text="What is the derivative of x^2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            subject="Mathematics",
            topic="Calculus",
            difficulty=DifficultyLevel.ADVANCED,
            options=[
                QuestionOption(text="2x", is_correct=True),
                QuestionOption(text="x", is_correct=False),
                QuestionOption(text="x^2", is_correct=False),
                QuestionOption(text="2", is_correct=False)
            ]
        )
        self.tree.add_question(advanced_math_question)
        
        # Test multiple criteria
        math_beginner_questions = self.tree.get_questions_by_criteria(
            subject="Mathematics",
            difficulty=DifficultyLevel.BEGINNER
        )
        assert len(math_beginner_questions) == 1
        assert math_beginner_questions[0] == self.math_question
        
        math_advanced_questions = self.tree.get_questions_by_criteria(
            subject="Mathematics",
            difficulty=DifficultyLevel.ADVANCED
        )
        assert len(math_advanced_questions) == 1
        assert math_advanced_questions[0] == advanced_math_question
    
    def test_get_tree_structure(self):
        """Test getting tree structure representation"""
        self.tree.add_question(self.math_question)
        self.tree.add_question(self.physics_question)
        
        structure = self.tree.get_tree_structure()
        
        assert structure['type'] == 'root'
        assert 'children' in structure
        assert 'Mathematics' in structure['children']
        assert 'Physics' in structure['children']
    
    def test_get_statistics(self):
        """Test getting tree statistics"""
        self.tree.add_question(self.math_question)
        self.tree.add_question(self.physics_question)
        
        stats = self.tree.get_statistics()
        
        assert stats['total_questions'] == 2
        assert stats['subjects'] == 2
        assert 'Mathematics' in stats['subjects_detail']
        assert 'Physics' in stats['subjects_detail']
        
        math_stats = stats['subjects_detail']['Mathematics']
        assert math_stats['topics'] == 1
        assert math_stats['total_questions'] == 1
    
    def test_remove_question(self):
        """Test removing questions from the tree"""
        self.tree.add_question(self.math_question)
        question_id = str(self.math_question.id)
        
        assert self.tree.total_questions == 1
        
        # Remove the question
        removed = self.tree.remove_question(question_id)
        assert removed == True
        assert self.tree.total_questions == 0
        
        # Try to remove non-existent question
        removed = self.tree.remove_question("non-existent-id")
        assert removed == False
    
    def test_limit_questions(self):
        """Test limiting number of returned questions"""
        # Add multiple questions
        for i in range(5):
            question = QuestionResponse(
                text=f"Question {i}",
                question_type=QuestionType.TRUE_FALSE,
                subject="TestSubject",
                topic="TestTopic",
                difficulty=DifficultyLevel.BEGINNER,
                correct_answer="true"
            )
            self.tree.add_question(question)
        
        # Test limit
        limited_questions = self.tree.get_questions_by_criteria(limit=3)
        assert len(limited_questions) == 3
        
        all_questions = self.tree.get_questions_by_criteria()
        assert len(all_questions) == 5

if __name__ == "__main__":
    pytest.main([__file__])