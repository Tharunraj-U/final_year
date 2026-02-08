"""
User data model for the AI Learning Assistant.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class UserProfile:
    """Represents a user's profile and overall statistics."""
    
    user_id: str
    username: str
    created_at: datetime = field(default_factory=datetime.now)
    total_problems_attempted: int = 0
    total_problems_solved: int = 0
    skill_level: str = "beginner"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "total_problems_attempted": self.total_problems_attempted,
            "total_problems_solved": self.total_problems_solved,
            "skill_level": self.skill_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """Create UserProfile from dictionary."""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            total_problems_attempted=data.get("total_problems_attempted", 0),
            total_problems_solved=data.get("total_problems_solved", 0),
            skill_level=data.get("skill_level", "beginner")
        )


@dataclass
class TopicProgress:
    """Tracks user's progress in a specific topic."""
    
    topic: str
    problems_attempted: int = 0
    problems_solved: int = 0
    total_attempts: int = 0
    total_time_minutes: int = 0
    avg_complexity_score: float = 0.0
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy rate."""
        if self.problems_attempted == 0:
            return 0.0
        return self.problems_solved / self.problems_attempted
    
    @property
    def avg_attempts_per_problem(self) -> float:
        """Calculate average attempts per problem."""
        if self.problems_attempted == 0:
            return 0.0
        return self.total_attempts / self.problems_attempted
    
    @property
    def avg_time_per_problem(self) -> float:
        """Calculate average time per problem in minutes."""
        if self.problems_attempted == 0:
            return 0.0
        return self.total_time_minutes / self.problems_attempted
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "topic": self.topic,
            "problems_attempted": self.problems_attempted,
            "problems_solved": self.problems_solved,
            "accuracy": round(self.accuracy, 2),
            "avg_attempts": round(self.avg_attempts_per_problem, 2),
            "avg_time_minutes": round(self.avg_time_per_problem, 2),
            "avg_complexity_score": round(self.avg_complexity_score, 2)
        }


@dataclass
class UserPerformanceData:
    """Complete user performance data for analysis."""
    
    user_id: str
    submissions: List[Dict] = field(default_factory=list)
    topic_progress: Dict[str, TopicProgress] = field(default_factory=dict)
    
    def add_submission(self, submission: Dict):
        """Add a submission and update topic progress."""
        self.submissions.append(submission)
        
        topic = submission.get("topic", "unknown")
        if topic not in self.topic_progress:
            self.topic_progress[topic] = TopicProgress(topic=topic)
        
        progress = self.topic_progress[topic]
        progress.problems_attempted += 1
        progress.total_attempts += submission.get("attempts", 1)
        progress.total_time_minutes += submission.get("time_taken_minutes", 0)
        
        if submission.get("solved", False):
            progress.problems_solved += 1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "submissions": self.submissions,
            "topic_progress": {
                topic: prog.to_dict() 
                for topic, prog in self.topic_progress.items()
            }
        }
