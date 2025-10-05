"""
Dynamic Programming Module - Adaptive Difficulty Optimization
Uses DP algorithms to optimize question difficulty progression based on user performance.
"""

from typing import Dict, List, Tuple, Optional
from backend.models.question import DifficultyLevel
import numpy as np

class DifficultyOptimizer:
    """
    Dynamic Programming-based difficulty optimizer
    Optimizes question difficulty progression for maximum learning efficiency
    """
    
    def __init__(self):
        # Difficulty levels mapping for DP calculations
        self.difficulty_map = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 1,
            DifficultyLevel.ADVANCED: 2,
            DifficultyLevel.EXPERT: 3
        }
        
        self.reverse_difficulty_map = {v: k for k, v in self.difficulty_map.items()}
        
        # DP memoization table for optimal transitions
        self.transition_cache = {}
        
        # Learning efficiency matrix (performance_rate, difficulty_level)
        # Higher values indicate better learning outcomes
        self.efficiency_matrix = np.array([
            # Beginner, Intermediate, Advanced, Expert
            [0.9, 0.7, 0.3, 0.1],  # High performance (>80% correct)
            [0.8, 0.9, 0.6, 0.3],  # Good performance (60-80% correct)
            [0.6, 0.8, 0.8, 0.5],  # Average performance (40-60% correct)
            [0.4, 0.6, 0.7, 0.6],  # Poor performance (<40% correct)
        ])
        
        # Transition costs for difficulty changes
        self.transition_costs = {
            0: 0,   # Stay same difficulty
            1: 0.1, # Move up one level
            -1: 0.05, # Move down one level
            2: 0.3,   # Move up two levels
            -2: 0.2,  # Move down two levels
            3: 0.5,   # Move up three levels
            -3: 0.4   # Move down three levels
        }
    
    def get_optimal_next_difficulty(self, 
                                  current_difficulty: DifficultyLevel,
                                  performance_score: float,
                                  performance_history: List[float] = None) -> DifficultyLevel:
        """
        Use DP to find optimal next difficulty level
        
        Args:
            current_difficulty: Current question difficulty
            performance_score: Recent performance (0.0 to 1.0)
            performance_history: Historical performance data
        
        Returns:
            Optimal next difficulty level
        """
        current_level = self.difficulty_map[current_difficulty]
        
        # Create cache key for memoization
        cache_key = (current_level, round(performance_score, 2))
        
        if cache_key in self.transition_cache:
            return self.reverse_difficulty_map[self.transition_cache[cache_key]]
        
        # Calculate optimal transition using DP
        optimal_level = self._calculate_optimal_transition(
            current_level, performance_score, performance_history
        )
        
        # Cache result for future use
        self.transition_cache[cache_key] = optimal_level
        
        return self.reverse_difficulty_map[optimal_level]
    
    def _calculate_optimal_transition(self, 
                                    current_level: int, 
                                    performance_score: float,
                                    performance_history: List[float] = None) -> int:
        """
        Calculate optimal difficulty transition using dynamic programming
        """
        # Determine performance category
        perf_category = self._get_performance_category(performance_score)
        
        # Calculate value for each possible next difficulty level
        max_value = -float('inf')
        optimal_level = current_level
        
        for next_level in range(4):  # 0-3 for four difficulty levels
            # Calculate transition cost
            level_change = next_level - current_level
            transition_cost = self.transition_costs.get(level_change, 0.5)
            
            # Get learning efficiency for this transition
            efficiency = self.efficiency_matrix[perf_category][next_level]
            
            # Apply trend factor if performance history is available
            trend_factor = self._calculate_trend_factor(performance_history) if performance_history else 1.0
            
            # Calculate total value: efficiency - transition_cost + trend_adjustment
            total_value = efficiency - transition_cost + (trend_factor * 0.1)
            
            if total_value > max_value:
                max_value = total_value
                optimal_level = next_level
        
        return optimal_level
    
    def _get_performance_category(self, performance_score: float) -> int:
        """
        Convert performance score to category index for efficiency matrix
        """
        if performance_score >= 0.8:
            return 0  # High performance
        elif performance_score >= 0.6:
            return 1  # Good performance
        elif performance_score >= 0.4:
            return 2  # Average performance
        else:
            return 3  # Poor performance
    
    def _calculate_trend_factor(self, performance_history: List[float]) -> float:
        """
        Calculate performance trend factor for DP optimization
        Positive trend = improving, Negative trend = declining
        """
        if len(performance_history) < 3:
            return 1.0
        
        # Calculate simple linear trend
        recent_scores = performance_history[-3:]
        if len(recent_scores) < 2:
            return 1.0
        
        # Simple trend calculation: (last - first) / length
        trend = (recent_scores[-1] - recent_scores[0]) / (len(recent_scores) - 1)
        
        # Normalize trend factor between 0.5 and 1.5
        return max(0.5, min(1.5, 1.0 + trend))
    
    def optimize_quiz_difficulty_sequence(self, 
                                        questions_count: int,
                                        starting_difficulty: DifficultyLevel,
                                        target_performance: float = 0.7) -> List[DifficultyLevel]:
        """
        Generate optimal difficulty sequence for a complete quiz
        Uses DP to create a progression that maximizes learning
        """
        sequence = [starting_difficulty]
        current_difficulty = starting_difficulty
        simulated_performance = target_performance
        
        for i in range(1, questions_count):
            # Simulate slight performance variation
            performance_variation = np.random.normal(0, 0.1)
            simulated_performance = max(0.0, min(1.0, simulated_performance + performance_variation))
            
            # Get next optimal difficulty
            next_difficulty = self.get_optimal_next_difficulty(
                current_difficulty, simulated_performance
            )
            
            sequence.append(next_difficulty)
            current_difficulty = next_difficulty
        
        return sequence
    
    def analyze_difficulty_progression(self, 
                                     actual_sequence: List[DifficultyLevel],
                                     performance_scores: List[float]) -> Dict[str, any]:
        """
        Analyze the effectiveness of a difficulty progression
        """
        if len(actual_sequence) != len(performance_scores):
            return {"error": "Sequence and scores length mismatch"}
        
        analysis = {
            'average_performance': np.mean(performance_scores),
            'performance_variance': np.var(performance_scores),
            'difficulty_changes': 0,
            'optimal_efficiency': 0.0,
            'progression_smoothness': 0.0
        }
        
        # Count difficulty changes
        for i in range(1, len(actual_sequence)):
            if actual_sequence[i] != actual_sequence[i-1]:
                analysis['difficulty_changes'] += 1
        
        # Calculate optimal efficiency score
        total_efficiency = 0
        for i, (difficulty, performance) in enumerate(zip(actual_sequence, performance_scores)):
            perf_category = self._get_performance_category(performance)
            difficulty_level = self.difficulty_map[difficulty]
            efficiency = self.efficiency_matrix[perf_category][difficulty_level]
            total_efficiency += efficiency
        
        analysis['optimal_efficiency'] = total_efficiency / len(actual_sequence)
        
        # Calculate progression smoothness (fewer abrupt changes = smoother)
        if len(actual_sequence) > 1:
            difficulty_numbers = [self.difficulty_map[d] for d in actual_sequence]
            changes = [abs(difficulty_numbers[i] - difficulty_numbers[i-1]) 
                      for i in range(1, len(difficulty_numbers))]
            analysis['progression_smoothness'] = 1.0 - (sum(changes) / (len(changes) * 3))
        
        return analysis
    
    def get_difficulty_recommendations(self, 
                                     user_performance_history: List[Tuple[DifficultyLevel, float]]) -> Dict[str, any]:
        """
        Provide recommendations based on user's complete performance history
        """
        if not user_performance_history:
            return {
                'recommended_difficulty': DifficultyLevel.INTERMEDIATE,
                'confidence': 0.5,
                'reasoning': 'No performance history available'
            }
        
        # Analyze recent performance by difficulty
        difficulty_performance = {}
        for difficulty, score in user_performance_history[-10:]:  # Recent 10 questions
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = []
            difficulty_performance[difficulty].append(score)
        
        # Calculate average performance per difficulty
        avg_performance = {}
        for difficulty, scores in difficulty_performance.items():
            avg_performance[difficulty] = np.mean(scores)
        
        # Find best performing difficulty and recommend next level
        if avg_performance:
            best_difficulty = max(avg_performance.keys(), key=lambda d: avg_performance[d])
            best_score = avg_performance[best_difficulty]
            
            recommended_difficulty = self.get_optimal_next_difficulty(
                best_difficulty, best_score
            )
            
            return {
                'recommended_difficulty': recommended_difficulty,
                'confidence': min(0.95, best_score + 0.2),
                'reasoning': f'Based on {best_score:.1%} performance in {best_difficulty.value} questions',
                'performance_by_difficulty': {d.value: f"{score:.1%}" 
                                            for d, score in avg_performance.items()}
            }
        
        return {
            'recommended_difficulty': DifficultyLevel.INTERMEDIATE,
            'confidence': 0.5,
            'reasoning': 'Insufficient performance data for analysis'
        }