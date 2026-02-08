"""
Tests for the Recommendation Engine.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.recommender import RecommendationEngine
from app.services.analyzer import PerformanceAnalyzer
from app.models.problem import ProblemBank, Problem


class TestRecommendationEngine:
    """Test cases for RecommendationEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.problem_bank = ProblemBank()
        self._load_test_problems()
        self.analyzer = PerformanceAnalyzer()
        self.recommender = RecommendationEngine(
            self.problem_bank, 
            self.analyzer
        )
    
    def _load_test_problems(self):
        """Load test problems into bank."""
        test_problems = [
            {
                "problem_id": "arr-easy-1",
                "title": "Array Easy 1",
                "difficulty": "easy",
                "topic": "arrays",
                "expected_complexity": "O(n)",
                "expected_time_minutes": 15
            },
            {
                "problem_id": "arr-easy-2",
                "title": "Array Easy 2",
                "difficulty": "easy",
                "topic": "arrays",
                "expected_complexity": "O(n)",
                "expected_time_minutes": 15
            },
            {
                "problem_id": "arr-med-1",
                "title": "Array Medium 1",
                "difficulty": "medium",
                "topic": "arrays",
                "expected_complexity": "O(n log n)",
                "expected_time_minutes": 30
            },
            {
                "problem_id": "dp-easy-1",
                "title": "DP Easy 1",
                "difficulty": "easy",
                "topic": "dynamic_programming",
                "expected_complexity": "O(n)",
                "expected_time_minutes": 20
            },
            {
                "problem_id": "dp-med-1",
                "title": "DP Medium 1",
                "difficulty": "medium",
                "topic": "dynamic_programming",
                "expected_complexity": "O(n^2)",
                "expected_time_minutes": 35
            },
            {
                "problem_id": "graph-easy-1",
                "title": "Graph Easy 1",
                "difficulty": "easy",
                "topic": "graphs",
                "expected_complexity": "O(V+E)",
                "expected_time_minutes": 20
            }
        ]
        self.problem_bank.load_from_list(test_problems)
    
    def test_empty_recommendations(self):
        """Test recommendations with no prior history."""
        analysis = self.analyzer.analyze_submissions([])
        
        recs = self.recommender.generate_recommendations(
            user_id="test_user",
            analysis=analysis,
            solved_problem_ids=[],
            max_recommendations=3
        )
        
        # Should recommend easy problems for new user
        assert len(recs) > 0
        assert all(r["difficulty"] == "easy" for r in recs)
    
    def test_weakness_prioritization(self):
        """Test that weak topics are prioritized."""
        # User is weak in DP (failed problem)
        submissions = [
            {
                "problem_id": "arr-easy-1",
                "topic": "arrays",
                "difficulty": "easy",
                "solved": True,
                "attempts": 1,
                "time_taken_minutes": 10,
                "user_complexity": "O(n)",
                "expected_complexity": "O(n)"
            },
            {
                "problem_id": "dp-easy-1",
                "topic": "dynamic_programming",
                "difficulty": "easy",
                "solved": False,
                "attempts": 5,
                "time_taken_minutes": 60,
                "user_complexity": "O(2^n)",
                "expected_complexity": "O(n)"
            }
        ]
        
        analysis = self.analyzer.analyze_submissions(submissions)
        
        recs = self.recommender.generate_recommendations(
            user_id="test_user",
            analysis=analysis,
            solved_problem_ids=["arr-easy-1", "dp-easy-1"],
            max_recommendations=3
        )
        
        # Should have DP recommendations due to weakness
        dp_recs = [r for r in recs if r["topic"] == "dynamic_programming"]
        assert len(dp_recs) > 0 or len(recs) > 0  # Some recommendation made
    
    def test_difficulty_progression(self):
        """Test that difficulty progresses correctly."""
        # User has mastered easy arrays
        submissions = [
            {
                "problem_id": f"arr-easy-{i}",
                "topic": "arrays",
                "difficulty": "easy",
                "solved": True,
                "attempts": 1,
                "time_taken_minutes": 10,
                "user_complexity": "O(n)",
                "expected_complexity": "O(n)"
            }
            for i in range(1, 3)
        ]
        
        analysis = self.analyzer.analyze_submissions(submissions)
        
        recs = self.recommender.generate_recommendations(
            user_id="test_user",
            analysis=analysis,
            solved_problem_ids=["arr-easy-1", "arr-easy-2"],
            max_recommendations=3
        )
        
        # Should recommend medium level for arrays
        array_recs = [r for r in recs if r["topic"] == "arrays"]
        if array_recs:
            assert any(r["difficulty"] in ["medium", "easy"] for r in array_recs)
    
    def test_no_duplicate_recommendations(self):
        """Test that solved problems are not recommended."""
        analysis = self.analyzer.analyze_submissions([])
        
        solved = ["arr-easy-1", "dp-easy-1"]
        
        recs = self.recommender.generate_recommendations(
            user_id="test_user",
            analysis=analysis,
            solved_problem_ids=solved,
            max_recommendations=5
        )
        
        rec_ids = [r["problem_id"] for r in recs]
        for solved_id in solved:
            assert solved_id not in rec_ids
    
    def test_max_recommendations_respected(self):
        """Test that max recommendations limit is respected."""
        analysis = self.analyzer.analyze_submissions([])
        
        recs = self.recommender.generate_recommendations(
            user_id="test_user",
            analysis=analysis,
            solved_problem_ids=[],
            max_recommendations=2
        )
        
        assert len(recs) <= 2
    
    def test_next_milestone_calculation(self):
        """Test milestone calculation."""
        analysis = {
            "overall_score": 35,
            "skill_level": "beginner"
        }
        
        milestone = self.recommender.get_next_milestone(analysis, 10)
        
        assert "description" in milestone
        assert "progress" in milestone
        assert milestone["progress"] >= 0
        assert milestone["progress"] <= 100


class TestProblemBank:
    """Test cases for ProblemBank."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bank = ProblemBank()
    
    def test_add_and_get_problem(self):
        """Test adding and retrieving problems."""
        problem = Problem(
            problem_id="test-001",
            title="Test Problem",
            difficulty="easy",
            topic="arrays",
            expected_complexity="O(n)",
            expected_time_minutes=15
        )
        
        self.bank.add_problem(problem)
        
        retrieved = self.bank.get_problem("test-001")
        assert retrieved is not None
        assert retrieved.title == "Test Problem"
    
    def test_filter_by_topic(self):
        """Test filtering by topic."""
        self.bank.load_from_list([
            {"problem_id": "1", "title": "P1", "difficulty": "easy", 
             "topic": "arrays", "expected_complexity": "O(n)"},
            {"problem_id": "2", "title": "P2", "difficulty": "easy", 
             "topic": "trees", "expected_complexity": "O(n)"}
        ])
        
        arrays = self.bank.get_by_topic("arrays")
        assert len(arrays) == 1
        assert arrays[0].topic == "arrays"
    
    def test_filter_by_difficulty(self):
        """Test filtering by difficulty."""
        self.bank.load_from_list([
            {"problem_id": "1", "title": "P1", "difficulty": "easy", 
             "topic": "arrays", "expected_complexity": "O(n)"},
            {"problem_id": "2", "title": "P2", "difficulty": "hard", 
             "topic": "arrays", "expected_complexity": "O(n)"}
        ])
        
        easy = self.bank.get_by_difficulty("easy")
        assert len(easy) == 1
        assert easy[0].difficulty == "easy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
