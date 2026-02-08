"""
Performance analyzer service for evaluating user performance.
"""

from typing import Dict, List, Tuple
from collections import defaultdict

from ..models.user import TopicProgress
from ..models.submission import Submission, SubmissionAnalysis
from ..utils.constants import (
    PROBLEM_TOPICS,
    MASTERY_THRESHOLDS,
    DIFFICULTY_LEVELS
)
from ..utils.complexity import compare_complexity
from .scorer import Scorer


class PerformanceAnalyzer:
    """
    Analyzes user's coding performance across topics and difficulties.
    
    Responsibilities:
    - Calculate topic-wise performance
    - Identify strengths and weaknesses
    - Track mastery progress
    - Generate comprehensive analysis reports
    """
    
    def __init__(self, scorer: Scorer = None):
        """
        Initialize analyzer with optional custom scorer.
        
        Args:
            scorer: Custom Scorer instance (defaults to new Scorer)
        """
        self.scorer = scorer or Scorer()
    
    def analyze_submissions(
        self, 
        submissions: List[Dict]
    ) -> Dict:
        """
        Analyze a list of user submissions.
        
        Args:
            submissions: List of submission dictionaries
        
        Returns:
            Complete analysis dictionary
        """
        if not submissions:
            return self._empty_analysis()
        
        # Convert to Submission objects
        submission_objects = [
            Submission.from_dict(s) for s in submissions
        ]
        
        # Analyze each submission
        analyses = [
            self.scorer.calculate_submission_score(s) 
            for s in submission_objects
        ]
        
        # Calculate topic breakdown
        topic_breakdown = self._calculate_topic_breakdown(analyses)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(topic_breakdown)
        
        # Calculate overall metrics
        overall_score = self.scorer.calculate_overall_score(analyses)
        skill_level = self.scorer.get_skill_level(overall_score)
        
        # Calculate efficiency rating
        avg_efficiency = sum(a.efficiency_score for a in analyses) / len(analyses)
        efficiency_rating = self.scorer.get_efficiency_rating(avg_efficiency)
        
        # Check for brute force patterns
        brute_force_count = sum(1 for a in analyses if a.is_brute_force)
        
        return {
            "overall_score": round(overall_score, 2),
            "skill_level": skill_level,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "efficiency_rating": efficiency_rating,
            "topic_breakdown": topic_breakdown,
            "statistics": {
                "total_problems_attempted": len(submission_objects),
                "total_problems_solved": sum(1 for s in submission_objects if s.solved),
                "brute_force_solutions": brute_force_count,
                "average_attempts": round(
                    sum(s.attempts for s in submission_objects) / len(submission_objects), 2
                ),
                "average_efficiency_score": round(avg_efficiency, 2)
            }
        }
    
    def _calculate_topic_breakdown(
        self, 
        analyses: List[SubmissionAnalysis]
    ) -> List[Dict]:
        """Calculate performance breakdown by topic."""
        topic_data = defaultdict(lambda: {
            "attempts": 0,
            "solved": 0,
            "total_efficiency": 0.0,
            "total_score": 0.0,
            "difficulties": defaultdict(int)
        })
        
        for analysis in analyses:
            topic = analysis.submission.topic
            data = topic_data[topic]
            
            data["attempts"] += 1
            if analysis.submission.solved:
                data["solved"] += 1
            data["total_efficiency"] += analysis.efficiency_score
            data["total_score"] += analysis.overall_score
            data["difficulties"][analysis.submission.difficulty] += 1
        
        breakdown = []
        for topic, data in topic_data.items():
            count = data["attempts"]
            breakdown.append({
                "topic": topic,
                "score": round((data["total_score"] / count) * 100, 2),
                "problems_solved": data["solved"],
                "problems_attempted": count,
                "accuracy": round(data["solved"] / count, 2) if count > 0 else 0,
                "avg_complexity_score": round(data["total_efficiency"] / count, 2),
                "difficulty_distribution": dict(data["difficulties"])
            })
        
        # Sort by score descending
        breakdown.sort(key=lambda x: x["score"], reverse=True)
        
        return breakdown
    
    def _identify_strengths_weaknesses(
        self, 
        topic_breakdown: List[Dict]
    ) -> Tuple[List[str], List[str]]:
        """
        Identify user's strengths and weaknesses from topic breakdown.
        
        Returns:
            Tuple of (strengths list, weaknesses list)
        """
        if not topic_breakdown:
            return [], []
        
        strengths = []
        weaknesses = []
        
        for topic_data in topic_breakdown:
            topic = topic_data["topic"]
            score = topic_data["score"]
            accuracy = topic_data["accuracy"]
            efficiency = topic_data["avg_complexity_score"]
            
            # Strength criteria: high score, good accuracy, good efficiency
            if score >= 70 and accuracy >= 0.7 and efficiency >= 0.7:
                strengths.append(topic)
            # Weakness criteria: low score or poor efficiency
            elif score < 50 or efficiency < 0.5 or accuracy < 0.5:
                weaknesses.append(topic)
        
        # Limit to top 3 each
        return strengths[:3], weaknesses[:3]
    
    def check_topic_mastery(
        self, 
        topic_data: Dict, 
        difficulty: str
    ) -> bool:
        """
        Check if user has mastered a topic at a given difficulty.
        
        Args:
            topic_data: Topic performance data
            difficulty: Difficulty level to check
        
        Returns:
            True if mastery criteria met
        """
        thresholds = MASTERY_THRESHOLDS.get(difficulty, MASTERY_THRESHOLDS["medium"])
        
        solved = topic_data.get("problems_solved", 0)
        accuracy = topic_data.get("accuracy", 0)
        
        return (
            solved >= thresholds["min_solved"] and
            accuracy >= thresholds["min_accuracy"]
        )
    
    def get_next_difficulty(
        self, 
        topic_breakdown: List[Dict], 
        topic: str
    ) -> str:
        """
        Determine next appropriate difficulty for a topic.
        
        Args:
            topic_breakdown: Topic performance breakdown
            topic: Topic to check
        
        Returns:
            Recommended difficulty level
        """
        topic_data = next(
            (t for t in topic_breakdown if t["topic"] == topic), 
            None
        )
        
        if not topic_data:
            return "easy"
        
        # Check mastery at each level
        for i, difficulty in enumerate(DIFFICULTY_LEVELS):
            if not self.check_topic_mastery(topic_data, difficulty):
                return difficulty
        
        return "hard"
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure."""
        return {
            "overall_score": 0.0,
            "skill_level": "beginner",
            "strengths": [],
            "weaknesses": [],
            "efficiency_rating": "suboptimal",
            "topic_breakdown": [],
            "statistics": {
                "total_problems_attempted": 0,
                "total_problems_solved": 0,
                "brute_force_solutions": 0,
                "average_attempts": 0,
                "average_efficiency_score": 0
            }
        }
