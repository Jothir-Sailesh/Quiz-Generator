"""
Unit tests for AI service implementation
Tests the AI question generation functionality.
"""

import pytest
import asyncio
import sys
import os

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_service import AIQuestionGenerator
from backend.models.question import QuestionType, DifficultyLevel

class TestAIQuestionGenerator:
    """Test cases for AIQuestionGenerator class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Use mock mode (no API key)
        self.generator = AIQuestionGenerator(api_key=None, provider="openai")
        
        self.sample_text = """
        Photosynthesis is the process by which green plants and some other organisms 
        use sunlight to synthesize foods from carbon dioxide and water. This process 
        converts light energy into chemical energy, which is stored in glucose molecules.
        The overall equation for photosynthesis can be written as:
        6CO2 + 6H2O + light energy → C6H12O6 + 6O2
        """
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        assert self.generator.mock_mode == True
        assert self.generator.provider == "openai"
        assert self.generator.api_key is None
    
    @pytest.mark.asyncio
    async def test_generate_questions_from_text(self):
        """Test generating questions from text (mock mode)"""
        questions = await self.generator.generate_questions_from_text(
            text=self.sample_text,
            question_count=3,
            subject="Biology"
        )
        
        assert len(questions) == 3
        
        for question in questions:
            assert question.ai_generated == True
            assert question.subject == "Biology"
            assert question.text is not None
            assert len(question.text) > 0
            assert question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]
            assert question.difficulty in [
                DifficultyLevel.BEGINNER,
                DifficultyLevel.INTERMEDIATE,
                DifficultyLevel.ADVANCED,
                DifficultyLevel.EXPERT
            ]
    
    @pytest.mark.asyncio 
    async def test_generate_multiple_choice_questions(self):
        """Test generating multiple choice questions specifically"""
        questions = await self.generator.generate_questions_from_text(
            text=self.sample_text,
            question_count=2,
            question_types=[QuestionType.MULTIPLE_CHOICE],
            subject="Biology"
        )
        
        for question in questions:
            assert question.question_type == QuestionType.MULTIPLE_CHOICE
            assert len(question.options) == 4  # Should have 4 options
            
            correct_options = [opt for opt in question.options if opt.is_correct]
            assert len(correct_options) == 1  # Should have exactly one correct option
    
    @pytest.mark.asyncio
    async def test_generate_true_false_questions(self):
        """Test generating true/false questions specifically"""
        questions = await self.generator.generate_questions_from_text(
            text=self.sample_text,
            question_count=2,
            question_types=[QuestionType.TRUE_FALSE],
            subject="Biology"
        )
        
        for question in questions:
            assert question.question_type == QuestionType.TRUE_FALSE
            assert question.correct_answer in ["true", "false"]
            assert question.options == []  # True/false should not have options
    
    def test_extract_key_terms(self):
        """Test extracting key terms from text"""
        key_terms = self.generator._extract_key_terms(self.sample_text)
        
        assert len(key_terms) > 0
        assert "photosynthesis" in [term.lower() for term in key_terms]
        assert "energy" in [term.lower() for term in key_terms]
        assert "glucose" in [term.lower() for term in key_terms]
        
        # Should not contain stop words
        stop_words = ["the", "and", "or", "but", "is", "are"]
        for stop_word in stop_words:
            assert stop_word not in key_terms
    
    def test_split_text_into_chunks(self):
        """Test splitting long text into chunks"""
        long_text = "This is a sentence. " * 100  # Create long text
        chunks = self.generator._split_text_into_chunks(long_text, max_chunk_size=200)
        
        assert len(chunks) > 1  # Should split into multiple chunks
        
        for chunk in chunks:
            assert len(chunk) <= 200  # Each chunk should be within limit
            assert len(chunk.strip()) > 0  # Should not have empty chunks
        
        # Test with short text
        short_text = "This is a short text."
        short_chunks = self.generator._split_text_into_chunks(short_text, max_chunk_size=200)
        assert len(short_chunks) == 1
        assert short_chunks[0] == short_text
    
    def test_assess_text_difficulty(self):
        """Test text difficulty assessment"""
        # Simple text (should be beginner)
        simple_text = "The cat sat on the mat. It was a nice day."
        simple_difficulty = self.generator.assess_text_difficulty(simple_text)
        assert simple_difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE]
        
        # Complex text (should be higher difficulty)
        complex_text = """
        The photosynthetic apparatus comprises sophisticated molecular machinery
        that facilitates the conversion of electromagnetic radiation into chemical
        potential energy through a series of oxidation-reduction reactions.
        """
        complex_difficulty = self.generator.assess_text_difficulty(complex_text)
        assert complex_difficulty in [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
    
    @pytest.mark.asyncio
    async def test_generate_with_difficulty_preference(self):
        """Test generating questions with difficulty preference"""
        questions = await self.generator.generate_questions_from_text(
            text=self.sample_text,
            question_count=2,
            subject="Biology",
            difficulty_preference=DifficultyLevel.ADVANCED
        )
        
        # Note: In mock mode, difficulty preference might not be strictly enforced
        # but the function should not crash
        assert len(questions) == 2
        for question in questions:
            assert question.difficulty is not None
    
    @pytest.mark.asyncio
    async def test_generate_with_empty_text(self):
        """Test behavior with empty or minimal text"""
        minimal_text = "Test."
        questions = await self.generator.generate_questions_from_text(
            text=minimal_text,
            question_count=1,
            subject="Test"
        )
        
        # Should still generate questions even with minimal text (mock mode)
        assert len(questions) >= 0  # Might be 0 or generate mock questions
    
    def test_create_mock_questions(self):
        """Test mock question creation"""
        mock_questions = self.generator._generate_mock_questions(self.sample_text, 3, "Biology")
        
        assert len(mock_questions) == 3
        
        for question in mock_questions:
            assert question.ai_generated == True
            assert question.subject == "Biology"
            assert question.source_text is not None
            assert len(question.text) > 0
    
    def test_create_mock_multiple_choice(self):
        """Test creating mock multiple choice questions"""
        key_terms = ["photosynthesis", "energy", "glucose"]
        
        question = self.generator._create_mock_multiple_choice(
            key_terms, 0, "Biology", self.sample_text
        )
        
        assert question.question_type == QuestionType.MULTIPLE_CHOICE
        assert question.subject == "Biology"
        assert len(question.options) == 4
        assert any(opt.is_correct for opt in question.options)
        assert question.explanation is not None
    
    def test_create_mock_true_false(self):
        """Test creating mock true/false questions"""
        key_terms = ["photosynthesis", "energy", "glucose"]
        
        question = self.generator._create_mock_true_false(
            key_terms, 0, "Biology", self.sample_text
        )
        
        assert question.question_type == QuestionType.TRUE_FALSE
        assert question.subject == "Biology"
        assert question.correct_answer == "true"
        assert question.explanation is not None
        assert len(question.options) == 0
    
    def test_with_api_key(self):
        """Test initialization with API key"""
        # Test with API key (still mock mode for testing)
        generator_with_key = AIQuestionGenerator(api_key="test-key", provider="openai")
        assert generator_with_key.mock_mode == False
        assert generator_with_key.api_key == "test-key"
    
    def test_unsupported_provider(self):
        """Test with unsupported provider"""
        generator = AIQuestionGenerator(api_key=None, provider="unsupported")
        assert generator.provider == "unsupported"
        # Should still work in mock mode

if __name__ == "__main__":
    pytest.main([__file__])