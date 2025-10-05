"""
Unit tests for dynamic programming implementation
Tests the adaptive difficulty optimization functionality.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.dynamic_programming import DifficultyOptimizer
from backend.models.question import DifficultyLevel

class TestDifficultyOptimizer:
    """Test cases for DifficultyOptimizer class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.optimizer = DifficultyOptimizer()
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        assert len(self.optimizer.difficulty_map) == 4
        assert self.optimizer.difficulty_map[DifficultyLevel.BEGINNER] == 0
        assert self.optimizer.difficulty_map[DifficultyLevel.INTERMEDIATE] == 1
        assert self.optimizer.difficulty_map[DifficultyLevel.ADVANCED] == 2
        assert self.optimizer.difficulty_map[DifficultyLevel.EXPERT] == 3
        
        assert self.optimizer.efficiency_matrix.shape == (4, 4)
        assert len(self.optimizer.transition_costs) > 0
    
    def test_get_optimal_next_difficulty_high_performance(self):
        """Test optimal difficulty selection for high performance"""
        current_difficulty = DifficultyLevel.BEGINNER
        high_performance = 0.9  # 90% correct
        
        optimal_difficulty = self.optimizer.get_optimal_next_difficulty(
            current_difficulty, high_performance
        )
        
        # With high performance on beginner, should suggest moving up
        assert optimal_difficulty in [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]
    
    def test_get_optimal_next_difficulty_low_performance(self):
        """Test optimal difficulty selection for low performance"""
        current_difficulty = DifficultyLevel.ADVANCED
        low_performance = 0.3  # 30% correct
        
        optimal_difficulty = self.optimizer.get_optimal_next_difficulty(
            current_difficulty, low_performance
        )
        
        # With low performance on advanced, should suggest staying same or moving down
        assert optimal_difficulty in [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED, DifficultyLevel.BEGINNER]
    
    def test_get_optimal_next_difficulty_medium_performance(self):
        """Test optimal difficulty selection for medium performance"""
        current_difficulty = DifficultyLevel.INTERMEDIATE
        medium_performance = 0.6  # 60% correct
        
        optimal_difficulty = self.optimizer.get_optimal_next_difficulty(
            current_difficulty, medium_performance
        )
        
        # With medium performance, should likely stay at similar level
        assert optimal_difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]
    
    def test_get_performance_category(self):
        """Test performance score categorization"""
        # Test high performance
        assert self.optimizer._get_performance_category(0.9) == 0
        assert self.optimizer._get_performance_category(0.8) == 0
        
        # Test good performance
        assert self.optimizer._get_performance_category(0.7) == 1
        assert self.optimizer._get_performance_category(0.6) == 1
        
        # Test average performance
        assert self.optimizer._get_performance_category(0.5) == 2
        assert self.optimizer._get_performance_category(0.4) == 2
        
        # Test poor performance
        assert self.optimizer._get_performance_category(0.3) == 3
        assert self.optimizer._get_performance_category(0.1) == 3
    
    def test_calculate_trend_factor(self):
        """Test performance trend calculation"""
        # Test improving trend
        improving_history = [0.5, 0.6, 0.7]
        trend_factor = self.optimizer._calculate_trend_factor(improving_history)
        assert trend_factor > 1.0  # Should be greater than 1 for improvement
        
        # Test declining trend
        declining_history = [0.8, 0.6, 0.4]
        trend_factor = self.optimizer._calculate_trend_factor(declining_history)
        assert trend_factor < 1.0  # Should be less than 1 for decline
        
        # Test stable trend
        stable_history = [0.7, 0.7, 0.7]
        trend_factor = self.optimizer._calculate_trend_factor(stable_history)
        assert 0.9 <= trend_factor <= 1.1  # Should be close to 1 for stable
        
        # Test insufficient data
        short_history = [0.5]
        trend_factor = self.optimizer._calculate_trend_factor(short_history)
        assert trend_factor == 1.0  # Should return 1.0 for insufficient data
    
    def test_optimize_quiz_difficulty_sequence(self):
        """Test generating optimal difficulty sequence for a quiz"""
        questions_count = 10
        starting_difficulty = DifficultyLevel.INTERMEDIATE
        target_performance = 0.7
        
        sequence = self.optimizer.optimize_quiz_difficulty_sequence(
            questions_count, starting_difficulty, target_performance
        )
        
        assert len(sequence) == questions_count
        assert sequence[0] == starting_difficulty
        
        # All elements should be valid difficulty levels
        for difficulty in sequence:
            assert difficulty in [
                DifficultyLevel.BEGINNER,
                DifficultyLevel.INTERMEDIATE, 
                DifficultyLevel.ADVANCED,
                DifficultyLevel.EXPERT
            ]
    
    def test_analyze_difficulty_progression(self):
        """Test analyzing the effectiveness of a difficulty progression"""
        # Create test sequence and performance
        sequence = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED
        ]
        performance_scores = [0.9, 0.7, 0.8, 0.6]
        
        analysis = self.optimizer.analyze_difficulty_progression(sequence, performance_scores)
        
        assert 'average_performance' in analysis
        assert 'performance_variance' in analysis
        assert 'difficulty_changes' in analysis
        assert 'optimal_efficiency' in analysis
        assert 'progression_smoothness' in analysis
        
        assert analysis['average_performance'] == 0.75  # (0.9 + 0.7 + 0.8 + 0.6) / 4
        assert analysis['difficulty_changes'] == 2  # beginner->intermediate, intermediate->advanced
        
        # Test with mismatched lengths
        mismatched_analysis = self.optimizer.analyze_difficulty_progression(
            sequence, [0.5, 0.6]  # Wrong length
        )
        assert 'error' in mismatched_analysis
    
    def test_get_difficulty_recommendations(self):
        """Test getting difficulty recommendations based on performance history"""
        # Test with good performance history
        good_history = [
            (DifficultyLevel.BEGINNER, 0.9),
            (DifficultyLevel.INTERMEDIATE, 0.8),
            (DifficultyLevel.INTERMEDIATE, 0.7)
        ]
        
        recommendations = self.optimizer.get_difficulty_recommendations(good_history)
        
        assert 'recommended_difficulty' in recommendations
        assert 'confidence' in recommendations
        assert 'reasoning' in recommendations
        assert 'performance_by_difficulty' in recommendations
        
        assert isinstance(recommendations['recommended_difficulty'], DifficultyLevel)
        assert 0.0 <= recommendations['confidence'] <= 1.0
        
        # Test with empty history
        empty_recommendations = self.optimizer.get_difficulty_recommendations([])
        assert empty_recommendations['recommended_difficulty'] == DifficultyLevel.INTERMEDIATE
        assert empty_recommendations['confidence'] == 0.5
    
    def test_memoization(self):
        """Test that results are cached for repeated calls"""
        current_difficulty = DifficultyLevel.INTERMEDIATE
        performance_score = 0.7
        
        # Clear cache first
        self.optimizer.transition_cache.clear()
        
        # First call
        result1 = self.optimizer.get_optimal_next_difficulty(current_difficulty, performance_score)
        assert len(self.optimizer.transition_cache) > 0
        
        # Second call with same parameters should use cache
        result2 = self.optimizer.get_optimal_next_difficulty(current_difficulty, performance_score)
        assert result1 == result2
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with perfect performance
        perfect_result = self.optimizer.get_optimal_next_difficulty(
            DifficultyLevel.BEGINNER, 1.0
        )
        assert perfect_result is not None
        
        # Test with zero performance
        zero_result = self.optimizer.get_optimal_next_difficulty(
            DifficultyLevel.EXPERT, 0.0
        )
        assert zero_result is not None
        
        # Test with expert level and high performance (should stay high or maintain)
        expert_result = self.optimizer.get_optimal_next_difficulty(
            DifficultyLevel.EXPERT, 0.9
        )
        assert expert_result in [DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]

if __name__ == "__main__":
    pytest.main([__file__])