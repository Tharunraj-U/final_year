"""
Scoring service for calculating performance scores.
"""

from typing import Dict, List
from ..utils.constants import (
    SCORING_WEIGHTS,
    EXPECTED_TIME_LIMITS,
    SKILL_LEVEL_THRESHOLDS,
    EFFICIENCY_RATINGS
)
from ..utils.complexity import compare_complexity, is_brute_force
from ..models.submission import Submission, SubmissionAnalysis


class Scorer:
    """
    Calculates performance scores for user submissions.
    
    Score Formula:
    Performance = w1*Correctness + w2*Efficiency + w3*Speed + w4*Attempts
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize scorer with optional custom weights.
        
        Args:
            weights: Custom scoring weights (defaults to SCORING_WEIGHTS)
        """
        self.weights = weights or SCORING_WEIGHTS
    
    def calculate_correctness_score(self, solved: bool) -> float:
        """
        Calculate correctness score.
        
        Args:
            solved: Whether the problem was solved
        
        Returns:
            1.0 if solved, 0.0 otherwise
        """
        return 1.0 if solved else 0.0
    
    def calculate_efficiency_score(
        self, 
        user_complexity: str, 
        expected_complexity: str
    ) -> float:
        """
        Calculate efficiency score based on complexity comparison.
        
        Args:
            user_complexity: User's solution complexity
            expected_complexity: Expected optimal complexity
        
        Returns:
            Score between 0.0 and 1.0
        """
        return compare_complexity(user_complexity, expected_complexity)
    
    def calculate_speed_score(
        self, 
        time_taken: int, 
        difficulty: str
    ) -> float:
        """
        Calculate speed score based on time taken.
        
        Args:
            time_taken: Time taken in minutes
            difficulty: Problem difficulty level
        
        Returns:
            Score between 0.0 and 1.0
        """
        expected_time = EXPECTED_TIME_LIMITS.get(difficulty, 30)
        
        if time_taken <= 0:
            return 0.0
        
        # Score based on ratio of expected to actual time
        ratio = expected_time / time_taken
        
        if ratio >= 2.0:
            # Finished in half the expected time or less
            return 1.0
        elif ratio >= 1.0:
            # Finished within expected time
            return 0.8 + (ratio - 1.0) * 0.2
        elif ratio >= 0.5:
            # Took up to 2x expected time
            return 0.5 + (ratio - 0.5) * 0.6
        else:
            # Took more than 2x expected time
            return max(0.1, ratio)
    
    def calculate_attempts_score(self, attempts: int) -> float:
        """
        Calculate score based on number of attempts.
        
        Args:
            attempts: Number of submission attempts
        
        Returns:
            Score between 0.0 and 1.0
        """
        if attempts <= 0:
            return 0.0
        elif attempts == 1:
            return 1.0
        elif attempts == 2:
            return 0.8
        elif attempts == 3:
            return 0.6
        elif attempts <= 5:
            return 0.4
        else:
            return max(0.1, 1.0 - (attempts * 0.1))
    
    def calculate_submission_score(self, submission: Submission) -> SubmissionAnalysis:
        """
        Calculate complete analysis for a submission.
        
        Args:
            submission: The submission to analyze
        
        Returns:
            SubmissionAnalysis with all scores
        """
        correctness = self.calculate_correctness_score(submission.solved)
        efficiency = self.calculate_efficiency_score(
            submission.user_complexity,
            submission.expected_complexity
        )
        speed = self.calculate_speed_score(
            submission.time_taken_minutes,
            submission.difficulty
        )
        attempts = self.calculate_attempts_score(submission.attempts)
        
        # Calculate weighted overall score
        overall = (
            self.weights["correctness"] * correctness +
            self.weights["efficiency"] * efficiency +
            self.weights["speed"] * speed +
            self.weights["attempts"] * attempts
        )
        
        # Check for brute force
        brute_force = is_brute_force(
            submission.user_complexity,
            submission.expected_complexity
        )
        
        # Generate feedback
        feedback = self._generate_feedback(
            correctness, efficiency, speed, attempts, brute_force
        )
        
        return SubmissionAnalysis(
            submission=submission,
            correctness_score=correctness,
            efficiency_score=efficiency,
            speed_score=speed,
            attempts_score=attempts,
            overall_score=overall,
            is_brute_force=brute_force,
            feedback=feedback
        )
    
    def _generate_feedback(
        self,
        correctness: float,
        efficiency: float,
        speed: float,
        attempts: float,
        brute_force: bool
    ) -> str:
        """Generate human-readable feedback based on scores."""
        feedback_parts = []
        
        if correctness == 0:
            feedback_parts.append("Problem not solved.")
        
        if brute_force:
            feedback_parts.append(
                "Brute force approach detected. Consider optimizing your algorithm."
            )
        elif efficiency < 0.8:
            feedback_parts.append(
                "Solution efficiency can be improved."
            )
        
        if speed < 0.5:
            feedback_parts.append(
                "Try to improve your solving speed with more practice."
            )
        
        if attempts < 0.6:
            feedback_parts.append(
                "High number of attempts. Review your approach before submitting."
            )
        
        if not feedback_parts:
            feedback_parts.append("Great job! Optimal solution achieved.")
        
        return " ".join(feedback_parts)
    
    def calculate_overall_score(
        self, 
        analyses: List[SubmissionAnalysis]
    ) -> float:
        """
        Calculate overall score from multiple submission analyses.
        
        Args:
            analyses: List of submission analyses
        
        Returns:
            Overall score as percentage (0-100)
        """
        if not analyses:
            return 0.0
        
        total = sum(a.overall_score for a in analyses)
        return (total / len(analyses)) * 100
    
    def get_skill_level(self, overall_score: float) -> str:
        """
        Determine skill level based on overall score.
        
        Args:
            overall_score: Score from 0-100
        
        Returns:
            Skill level string
        """
        for level, (min_score, max_score) in SKILL_LEVEL_THRESHOLDS.items():
            if min_score <= overall_score < max_score:
                return level
        return "advanced"
    
    def get_efficiency_rating(self, avg_efficiency_score: float) -> str:
        """
        Get efficiency rating label.
        
        Args:
            avg_efficiency_score: Average efficiency score (0-1)
        
        Returns:
            Efficiency rating string
        """
        for rating, (min_val, max_val) in EFFICIENCY_RATINGS.items():
            if min_val <= avg_efficiency_score < max_val:
                return rating
        return "optimal" if avg_efficiency_score >= 0.8 else "suboptimal"
