"""
Submission data model for the AI Learning Assistant.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class Submission:
    """Represents a user's submission for a problem."""
    
    submission_id: str
    user_id: str
    problem_id: str
    problem_title: str
    topic: str
    difficulty: str
    solved: bool
    attempts: int
    time_taken_minutes: int
    user_complexity: str  # User's solution complexity
    expected_complexity: str  # Expected optimal complexity
    submitted_at: datetime = field(default_factory=datetime.now)
    code: str = ""  # Optional: submitted code
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "submission_id": self.submission_id,
            "user_id": self.user_id,
            "problem_id": self.problem_id,
            "problem_title": self.problem_title,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "solved": self.solved,
            "attempts": self.attempts,
            "time_taken_minutes": self.time_taken_minutes,
            "user_complexity": self.user_complexity,
            "expected_complexity": self.expected_complexity,
            "submitted_at": self.submitted_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Submission":
        """Create Submission from dictionary."""
        return cls(
            submission_id=data.get("submission_id", ""),
            user_id=data.get("user_id", ""),
            problem_id=data["problem_id"],
            problem_title=data.get("problem_title", ""),
            topic=data["topic"],
            difficulty=data["difficulty"],
            solved=data["solved"],
            attempts=data.get("attempts", 1),
            time_taken_minutes=data.get("time_taken_minutes", 0),
            user_complexity=data.get("user_complexity", "O(n)"),
            expected_complexity=data.get("expected_complexity", "O(n)"),
            submitted_at=datetime.fromisoformat(
                data.get("submitted_at", datetime.now().isoformat())
            ),
            code=data.get("code", "")
        )


@dataclass
class SubmissionAnalysis:
    """Analysis results for a single submission."""
    
    submission: Submission
    correctness_score: float = 0.0
    efficiency_score: float = 0.0
    speed_score: float = 0.0
    attempts_score: float = 0.0
    overall_score: float = 0.0
    is_brute_force: bool = False
    feedback: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "submission": self.submission.to_dict(),
            "scores": {
                "correctness": round(self.correctness_score, 2),
                "efficiency": round(self.efficiency_score, 2),
                "speed": round(self.speed_score, 2),
                "attempts": round(self.attempts_score, 2),
                "overall": round(self.overall_score, 2)
            },
            "is_brute_force": self.is_brute_force,
            "feedback": self.feedback
        }
