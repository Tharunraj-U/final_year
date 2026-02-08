"""
Recommendation engine for suggesting next problems.
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import random

from ..models.problem import Problem, ProblemBank
from ..utils.constants import (
    DIFFICULTY_LEVELS,
    PROBLEM_TOPICS,
    MASTERY_THRESHOLDS,
    RECOMMENDATION_CONFIG
)
from .analyzer import PerformanceAnalyzer


class RecommendationEngine:
    """
    Generates personalized problem recommendations based on user performance.
    
    Strategy:
    1. Prioritize weak topics
    2. Progress gradually (Easy → Medium → Hard)
    3. Ensure concept mastery before advancing
    4. Balance between reinforcement and new challenges
    """
    
    def __init__(
        self, 
        problem_bank: ProblemBank,
        analyzer: PerformanceAnalyzer = None
    ):
        """
        Initialize recommendation engine.
        
        Args:
            problem_bank: Bank of available problems
            analyzer: Performance analyzer instance
        """
        self.problem_bank = problem_bank
        self.analyzer = analyzer or PerformanceAnalyzer()
        self.config = RECOMMENDATION_CONFIG
    
    def generate_recommendations(
        self,
        user_id: str,
        analysis: Dict,
        solved_problem_ids: List[str],
        max_recommendations: int = None
    ) -> List[Dict]:
        """
        Generate problem recommendations for a user.
        
        Args:
            user_id: User identifier
            analysis: User performance analysis
            solved_problem_ids: List of already solved problem IDs
            max_recommendations: Maximum number of recommendations
        
        Returns:
            List of recommended problems with reasons
        """
        max_recs = max_recommendations or self.config["max_recommendations"]
        solved_set = set(solved_problem_ids)
        
        recommendations = []
        
        # Strategy 1: Address weaknesses (60% priority)
        weakness_recs = self._recommend_for_weaknesses(
            analysis.get("weaknesses", []),
            analysis.get("topic_breakdown", []),
            solved_set,
            int(max_recs * self.config["weakness_priority_weight"])
        )
        recommendations.extend(weakness_recs)
        
        # Strategy 2: Progressive challenges (40% priority)
        remaining = max_recs - len(recommendations)
        if remaining > 0:
            progression_recs = self._recommend_for_progression(
                analysis.get("topic_breakdown", []),
                analysis.get("skill_level", "beginner"),
                solved_set,
                remaining
            )
            recommendations.extend(progression_recs)
        
        # Strategy 3: Explore new topics if needed
        if len(recommendations) < max_recs:
            remaining = max_recs - len(recommendations)
            explored_topics = {r["topic"] for r in recommendations}
            new_topic_recs = self._recommend_new_topics(
                analysis.get("topic_breakdown", []),
                solved_set,
                explored_topics,
                remaining
            )
            recommendations.extend(new_topic_recs)
        
        # Deduplicate and limit
        seen_ids = set()
        unique_recs = []
        for rec in recommendations:
            if rec["problem_id"] not in seen_ids:
                seen_ids.add(rec["problem_id"])
                unique_recs.append(rec)
                if len(unique_recs) >= max_recs:
                    break
        
        return unique_recs
    
    def _recommend_for_weaknesses(
        self,
        weaknesses: List[str],
        topic_breakdown: List[Dict],
        solved_ids: Set[str],
        count: int
    ) -> List[Dict]:
        """Recommend problems to address weak topics."""
        recommendations = []
        
        for topic in weaknesses:
            if len(recommendations) >= count:
                break
            
            # Find appropriate difficulty for this topic
            topic_data = next(
                (t for t in topic_breakdown if t["topic"] == topic),
                None
            )
            
            difficulty = self._get_appropriate_difficulty(topic_data)
            
            # Get unsolved problems for this topic and difficulty
            candidates = self.problem_bank.get_by_topic_and_difficulty(
                topic, difficulty
            )
            unsolved = [p for p in candidates if p.problem_id not in solved_ids]
            
            for problem in unsolved[:2]:  # Max 2 per weak topic
                if len(recommendations) >= count:
                    break
                recommendations.append(self._format_recommendation(
                    problem,
                    f"Practice needed in {topic} - strengthen your fundamentals"
                ))
        
        return recommendations
    
    def _recommend_for_progression(
        self,
        topic_breakdown: List[Dict],
        skill_level: str,
        solved_ids: Set[str],
        count: int
    ) -> List[Dict]:
        """Recommend problems for skill progression."""
        recommendations = []
        
        # Find topics with good performance to advance
        for topic_data in topic_breakdown:
            if len(recommendations) >= count:
                break
            
            topic = topic_data["topic"]
            score = topic_data.get("score", 0)
            accuracy = topic_data.get("accuracy", 0)
            
            # If performing well, try next difficulty
            if score >= 70 and accuracy >= 0.7:
                current_diff = self._get_current_difficulty(topic_data)
                next_diff = self._get_next_difficulty(current_diff)
                
                if next_diff:
                    candidates = self.problem_bank.get_by_topic_and_difficulty(
                        topic, next_diff
                    )
                    unsolved = [p for p in candidates if p.problem_id not in solved_ids]
                    
                    if unsolved:
                        problem = unsolved[0]
                        recommendations.append(self._format_recommendation(
                            problem,
                            f"Ready for {next_diff} level in {topic} - great progress!"
                        ))
        
        return recommendations
    
    def _recommend_new_topics(
        self,
        topic_breakdown: List[Dict],
        solved_ids: Set[str],
        explored_topics: Set[str],
        count: int
    ) -> List[Dict]:
        """Recommend problems from unexplored topics."""
        recommendations = []
        
        attempted_topics = {t["topic"] for t in topic_breakdown}
        new_topics = [
            t for t in PROBLEM_TOPICS 
            if t not in attempted_topics and t not in explored_topics
        ]
        
        for topic in new_topics:
            if len(recommendations) >= count:
                break
            
            # Start with easy problems for new topics
            candidates = self.problem_bank.get_by_topic_and_difficulty(topic, "easy")
            unsolved = [p for p in candidates if p.problem_id not in solved_ids]
            
            if unsolved:
                problem = unsolved[0]
                recommendations.append(self._format_recommendation(
                    problem,
                    f"Explore new topic: {topic}"
                ))
        
        return recommendations
    
    def _get_appropriate_difficulty(self, topic_data: Optional[Dict]) -> str:
        """Determine appropriate difficulty based on topic performance."""
        if not topic_data:
            return "easy"
        
        accuracy = topic_data.get("accuracy", 0)
        score = topic_data.get("score", 0)
        
        if accuracy < 0.5 or score < 40:
            return "easy"
        elif accuracy < 0.7 or score < 70:
            return "medium"
        else:
            return "hard"
    
    def _get_current_difficulty(self, topic_data: Dict) -> str:
        """Get the current difficulty level user is working on."""
        dist = topic_data.get("difficulty_distribution", {})
        
        if dist.get("hard", 0) > 0:
            return "hard"
        elif dist.get("medium", 0) > 0:
            return "medium"
        return "easy"
    
    def _get_next_difficulty(self, current: str) -> Optional[str]:
        """Get the next difficulty level."""
        try:
            idx = DIFFICULTY_LEVELS.index(current)
            if idx < len(DIFFICULTY_LEVELS) - 1:
                return DIFFICULTY_LEVELS[idx + 1]
        except ValueError:
            pass
        return None
    
    def _format_recommendation(self, problem: Problem, reason: str) -> Dict:
        """Format a problem recommendation."""
        return {
            "problem_id": problem.problem_id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "topic": problem.topic,
            "expected_complexity": problem.expected_complexity,
            "reason": reason
        }
    
    def get_next_milestone(
        self,
        analysis: Dict,
        solved_count: int
    ) -> Dict:
        """
        Calculate the next milestone for the user.
        
        Args:
            analysis: User performance analysis
            solved_count: Total problems solved
        
        Returns:
            Milestone information
        """
        skill_level = analysis.get("skill_level", "beginner")
        overall_score = analysis.get("overall_score", 0)
        
        milestones = {
            "beginner": {
                "next": "intermediate",
                "score_target": 40,
                "problems_target": 20
            },
            "intermediate": {
                "next": "advanced",
                "score_target": 70,
                "problems_target": 50
            },
            "advanced": {
                "next": "expert",
                "score_target": 90,
                "problems_target": 100
            }
        }
        
        current = milestones.get(skill_level, milestones["beginner"])
        
        score_progress = min(100, (overall_score / current["score_target"]) * 100)
        problems_progress = min(100, (solved_count / current["problems_target"]) * 100)
        
        progress = (score_progress + problems_progress) / 2
        
        return {
            "description": f"Reach {current['next']} level",
            "progress": round(progress, 2),
            "requirements": {
                "score_target": current["score_target"],
                "problems_target": current["problems_target"],
                "current_score": round(overall_score, 2),
                "current_problems": solved_count
            }
        }
