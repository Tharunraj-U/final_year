"""
Tests for the Performance Analyzer service.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.analyzer import PerformanceAnalyzer
from app.services.scorer import Scorer


class TestPerformanceAnalyzer:
    """Test cases for PerformanceAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = PerformanceAnalyzer()
    
    def test_empty_submissions(self):
        """Test analysis with no submissions."""
        result = self.analyzer.analyze_submissions([])
        
        assert result["overall_score"] == 0.0
        assert result["skill_level"] == "beginner"
        assert result["strengths"] == []
        assert result["weaknesses"] == []
    
    def test_single_optimal_submission(self):
        """Test analysis with a single optimal submission."""
        submissions = [{
            "problem_id": "test-001",
            "problem_title": "Test Problem",
            "topic": "arrays",
            "difficulty": "easy",
            "solved": True,
            "attempts": 1,
            "time_taken_minutes": 10,
            "user_complexity": "O(n)",
            "expected_complexity": "O(n)"
        }]
        
        result = self.analyzer.analyze_submissions(submissions)
        
        assert result["overall_score"] > 80
        assert result["efficiency_rating"] == "optimal"
        assert result["statistics"]["total_problems_solved"] == 1
        assert result["statistics"]["brute_force_solutions"] == 0
    
    def test_brute_force_detection(self):
        """Test that brute force solutions are detected."""
        submissions = [{
            "problem_id": "test-001",
            "problem_title": "Test Problem",
            "topic": "arrays",
            "difficulty": "easy",
            "solved": True,
            "attempts": 1,
            "time_taken_minutes": 10,
            "user_complexity": "O(n^2)",
            "expected_complexity": "O(n)"
        }]
        
        result = self.analyzer.analyze_submissions(submissions)
        
        assert result["statistics"]["brute_force_solutions"] == 1
        assert result["efficiency_rating"] != "optimal"
    
    def test_multiple_topics_analysis(self):
        """Test analysis across multiple topics."""
        submissions = [
            {
                "problem_id": "arr-001",
                "problem_title": "Array Problem",
                "topic": "arrays",
                "difficulty": "easy",
                "solved": True,
                "attempts": 1,
                "time_taken_minutes": 10,
                "user_complexity": "O(n)",
                "expected_complexity": "O(n)"
            },
            {
                "problem_id": "dp-001",
                "problem_title": "DP Problem",
                "topic": "dynamic_programming",
                "difficulty": "medium",
                "solved": False,
                "attempts": 5,
                "time_taken_minutes": 60,
                "user_complexity": "O(2^n)",
                "expected_complexity": "O(n)"
            }
        ]
        
        result = self.analyzer.analyze_submissions(submissions)
        
        assert len(result["topic_breakdown"]) == 2
        
        # Arrays should be a strength
        array_topic = next(
            t for t in result["topic_breakdown"] 
            if t["topic"] == "arrays"
        )
        assert array_topic["accuracy"] == 1.0
        
        # DP should be a weakness
        dp_topic = next(
            t for t in result["topic_breakdown"] 
            if t["topic"] == "dynamic_programming"
        )
        assert dp_topic["accuracy"] == 0.0
    
    def test_strength_weakness_identification(self):
        """Test correct identification of strengths and weaknesses."""
        # Create submissions with clear strength and weakness
        submissions = [
            # Strong in arrays (3 solved optimally)
            {
                "problem_id": "arr-001",
                "topic": "arrays",
                "difficulty": "easy",
                "solved": True,
                "attempts": 1,
                "time_taken_minutes": 10,
                "user_complexity": "O(n)",
                "expected_complexity": "O(n)"
            },
            {
                "problem_id": "arr-002",
                "topic": "arrays",
                "difficulty": "easy",
                "solved": True,
                "attempts": 1,
                "time_taken_minutes": 12,
                "user_complexity": "O(n)",
                "expected_complexity": "O(n)"
            },
            # Weak in graphs (failed with brute force)
            {
                "problem_id": "graph-001",
                "topic": "graphs",
                "difficulty": "medium",
                "solved": False,
                "attempts": 5,
                "time_taken_minutes": 60,
                "user_complexity": "O(n^3)",
                "expected_complexity": "O(n)"
            }
        ]
        
        result = self.analyzer.analyze_submissions(submissions)
        
        assert "arrays" in result["strengths"]
        assert "graphs" in result["weaknesses"]


class TestScorer:
    """Test cases for Scorer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = Scorer()
    
    def test_correctness_score(self):
        """Test correctness scoring."""
        assert self.scorer.calculate_correctness_score(True) == 1.0
        assert self.scorer.calculate_correctness_score(False) == 0.0
    
    def test_efficiency_score_optimal(self):
        """Test efficiency scoring for optimal solution."""
        score = self.scorer.calculate_efficiency_score("O(n)", "O(n)")
        assert score == 1.0
    
    def test_efficiency_score_better_than_expected(self):
        """Test efficiency scoring when user does better."""
        score = self.scorer.calculate_efficiency_score("O(log n)", "O(n)")
        assert score == 1.0
    
    def test_efficiency_score_suboptimal(self):
        """Test efficiency scoring for suboptimal solution."""
        score = self.scorer.calculate_efficiency_score("O(n^2)", "O(n)")
        assert score < 1.0
        assert score > 0.0
    
    def test_speed_score_fast(self):
        """Test speed scoring for fast solution."""
        # Easy problem, expected 15 min, solved in 7 min
        score = self.scorer.calculate_speed_score(7, "easy")
        assert score >= 0.9
    
    def test_speed_score_slow(self):
        """Test speed scoring for slow solution."""
        # Easy problem, expected 15 min, solved in 45 min
        score = self.scorer.calculate_speed_score(45, "easy")
        assert score < 0.5
    
    def test_attempts_score(self):
        """Test attempts scoring."""
        assert self.scorer.calculate_attempts_score(1) == 1.0
        assert self.scorer.calculate_attempts_score(2) == 0.8
        assert self.scorer.calculate_attempts_score(5) == 0.4
        assert self.scorer.calculate_attempts_score(10) < 0.2
    
    def test_skill_level_determination(self):
        """Test skill level determination."""
        assert self.scorer.get_skill_level(30) == "beginner"
        assert self.scorer.get_skill_level(55) == "intermediate"
        assert self.scorer.get_skill_level(85) == "advanced"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
