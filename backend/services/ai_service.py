"""
AI Service - Integration with OpenAI/Gemini APIs
Handles question generation, difficulty assessment, and content processing.
"""

import openai
import json
import re
from typing import List, Dict, Optional, Tuple
from backend.models.question import QuestionCreate, QuestionOption, DifficultyLevel, QuestionType
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIQuestionGenerator:
    """
    AI-powered question generator using OpenAI/Gemini APIs
    Generates questions from text content with difficulty assessment
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.mock_mode = not api_key  # Use mock responses if no API key
        
        if self.api_key and self.provider == "openai":
            openai.api_key = api_key
        
        # Question generation prompts
        self.generation_prompts = {
            "multiple_choice": """
            Based on the following text, generate a multiple-choice question with 4 options.
            Text: {text}
            
            Requirements:
            - Create one clear, specific question about the main concepts
            - Provide exactly 4 answer options (A, B, C, D)
            - Only one option should be correct
            - Include brief explanations for why the correct answer is right
            - Assess difficulty level: beginner, intermediate, advanced, or expert
            - Identify the main topic/subject area
            
            Format your response as JSON:
            {{
                "question": "Your question here?",
                "options": [
                    {{"text": "Option A", "is_correct": false}},
                    {{"text": "Option B", "is_correct": true}},
                    {{"text": "Option C", "is_correct": false}},
                    {{"text": "Option D", "is_correct": false}}
                ],
                "explanation": "Why the correct answer is right",
                "difficulty": "intermediate",
                "subject": "Subject area",
                "topic": "Specific topic"
            }}
            """,
            
            "true_false": """
            Based on the following text, generate a true/false question.
            Text: {text}
            
            Create a statement that can be definitively marked as true or false based on the content.
            
            Format your response as JSON:
            {{
                "question": "Your statement here",
                "correct_answer": "true",
                "explanation": "Explanation of the answer",
                "difficulty": "beginner",
                "subject": "Subject area",
                "topic": "Specific topic"
            }}
            """
        }
    
    async def generate_questions_from_text(self, 
                                         text: str, 
                                         question_count: int = 5,
                                         question_types: List[QuestionType] = None,
                                         subject: str = "General",
                                         difficulty_preference: Optional[DifficultyLevel] = None) -> List[QuestionCreate]:
        """
        Generate multiple questions from input text using AI
        """
        if self.mock_mode:
            return self._generate_mock_questions(text, question_count, subject)
        
        if not question_types:
            question_types = [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]
        
        questions = []
        
        # Split text into chunks if it's too long
        text_chunks = self._split_text_into_chunks(text)
        
        for i, chunk in enumerate(text_chunks[:question_count]):
            # Cycle through question types
            question_type = question_types[i % len(question_types)]
            
            try:
                question = await self._generate_single_question(
                    chunk, question_type, subject, difficulty_preference
                )
                if question:
                    questions.append(question)
            except Exception as e:
                logger.error(f"Error generating question {i+1}: {str(e)}")
                continue
        
        return questions
    
    async def _generate_single_question(self,
                                      text: str,
                                      question_type: QuestionType,
                                      subject: str,
                                      difficulty_preference: Optional[DifficultyLevel] = None) -> Optional[QuestionCreate]:
        """Generate a single question using AI API"""
        
        if self.provider == "openai":
            return await self._generate_with_openai(text, question_type, subject, difficulty_preference)
        elif self.provider == "gemini":
            return await self._generate_with_gemini(text, question_type, subject, difficulty_preference)
        else:
            logger.error(f"Unsupported AI provider: {self.provider}")
            return None
    
    async def _generate_with_openai(self,
                                  text: str,
                                  question_type: QuestionType,
                                  subject: str,
                                  difficulty_preference: Optional[DifficultyLevel] = None) -> Optional[QuestionCreate]:
        """Generate question using OpenAI API"""
        
        try:
            prompt = self.generation_prompts.get(question_type.value, self.generation_prompts["multiple_choice"])
            formatted_prompt = prompt.format(text=text)
            
            if difficulty_preference:
                formatted_prompt += f"\nPreferred difficulty level: {difficulty_preference.value}"
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates high-quality quiz questions."},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            question_data = self._parse_ai_response(ai_response, question_type)
            
            if question_data:
                return self._create_question_from_data(question_data, text, question_type, subject)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
        
        return None
    
    async def _generate_with_gemini(self,
                                  text: str,
                                  question_type: QuestionType,
                                  subject: str,
                                  difficulty_preference: Optional[DifficultyLevel] = None) -> Optional[QuestionCreate]:
        """Generate question using Gemini API (placeholder implementation)"""
        
        # TODO: Implement Gemini API integration
        logger.info("Gemini API integration not yet implemented, using mock response")
        return await self._generate_mock_single_question(text, question_type, subject)
    
    def _generate_mock_questions(self, text: str, count: int, subject: str) -> List[QuestionCreate]:
        """Generate mock questions for testing without API key"""
        
        mock_questions = []
        key_terms = self._extract_key_terms(text)
        
        for i in range(count):
            # Alternate between question types
            if i % 2 == 0:
                question = self._create_mock_multiple_choice(key_terms, i, subject, text)
            else:
                question = self._create_mock_true_false(key_terms, i, subject, text)
            
            mock_questions.append(question)
        
        return mock_questions
    
    async def _generate_mock_single_question(self, text: str, question_type: QuestionType, subject: str) -> QuestionCreate:
        """Generate a single mock question"""
        key_terms = self._extract_key_terms(text)
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return self._create_mock_multiple_choice(key_terms, 0, subject, text)
        else:
            return self._create_mock_true_false(key_terms, 0, subject, text)
    
    def _create_mock_multiple_choice(self, key_terms: List[str], index: int, subject: str, text: str) -> QuestionCreate:
        """Create mock multiple choice question"""
        
        term = key_terms[index % len(key_terms)] if key_terms else "concept"
        
        return QuestionCreate(
            text=f"What is the significance of {term} in the context of {subject}?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            subject=subject,
            topic=term.title(),
            difficulty=DifficultyLevel.INTERMEDIATE,
            options=[
                QuestionOption(text=f"It is fundamental to understanding {subject}", is_correct=True),
                QuestionOption(text=f"It has no relevance to {subject}", is_correct=False),
                QuestionOption(text=f"It only applies in advanced {subject}", is_correct=False),
                QuestionOption(text=f"It is outdated in modern {subject}", is_correct=False)
            ],
            explanation=f"The term {term} is indeed significant in {subject} based on the provided text content.",
            source_text=text[:200] + "..." if len(text) > 200 else text,
            ai_generated=True
        )
    
    def _create_mock_true_false(self, key_terms: List[str], index: int, subject: str, text: str) -> QuestionCreate:
        """Create mock true/false question"""
        
        term = key_terms[index % len(key_terms)] if key_terms else "concept"
        
        return QuestionCreate(
            text=f"{term.title()} is a fundamental concept in {subject}.",
            question_type=QuestionType.TRUE_FALSE,
            subject=subject,
            topic=term.title(),
            difficulty=DifficultyLevel.BEGINNER,
            correct_answer="true",
            explanation=f"Based on the provided text, {term} appears to be relevant to {subject}.",
            source_text=text[:200] + "..." if len(text) > 200 else text,
            ai_generated=True
        )
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text using simple NLP techniques"""
        
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        # Simple word extraction and filtering
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        key_terms = [word for word in words if word not in stop_words]
        
        # Remove duplicates and return top terms
        unique_terms = list(dict.fromkeys(key_terms))
        return unique_terms[:10]  # Return top 10 key terms
    
    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Split long text into manageable chunks for question generation"""
        
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by sentences or paragraphs
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _parse_ai_response(self, response: str, question_type: QuestionType) -> Optional[Dict]:
        """Parse AI response and extract question data"""
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
        
        return None
    
    def _create_question_from_data(self, 
                                 data: Dict, 
                                 source_text: str,
                                 question_type: QuestionType,
                                 subject: str) -> QuestionCreate:
        """Create QuestionCreate object from parsed AI data"""
        
        # Parse difficulty level
        difficulty_str = data.get('difficulty', 'intermediate').lower()
        try:
            difficulty = DifficultyLevel(difficulty_str)
        except ValueError:
            difficulty = DifficultyLevel.INTERMEDIATE
        
        # Create question options for multiple choice
        options = []
        if question_type == QuestionType.MULTIPLE_CHOICE and 'options' in data:
            for opt_data in data['options']:
                options.append(QuestionOption(
                    text=opt_data.get('text', ''),
                    is_correct=opt_data.get('is_correct', False),
                    explanation=opt_data.get('explanation')
                ))
        
        return QuestionCreate(
            text=data.get('question', ''),
            question_type=question_type,
            subject=data.get('subject', subject),
            topic=data.get('topic', 'General'),
            difficulty=difficulty,
            options=options,
            correct_answer=data.get('correct_answer'),
            explanation=data.get('explanation', ''),
            source_text=source_text[:200] + "..." if len(source_text) > 200 else source_text,
            ai_generated=True
        )
    
    def assess_text_difficulty(self, text: str) -> DifficultyLevel:
        """
        Assess the difficulty level of input text
        Uses simple heuristics like sentence length, vocabulary complexity
        """
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Calculate metrics
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
        
        # Simple difficulty assessment
        if avg_word_length <= 4 and avg_sentence_length <= 10:
            return DifficultyLevel.BEGINNER
        elif avg_word_length <= 6 and avg_sentence_length <= 15:
            return DifficultyLevel.INTERMEDIATE
        elif avg_word_length <= 8 and avg_sentence_length <= 20:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT