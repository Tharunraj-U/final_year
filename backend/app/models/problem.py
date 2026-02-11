"""
Problem data model for the AI Learning Assistant.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class Problem:
    """Represents a coding problem."""
    
    problem_id: str
    title: str
    difficulty: str  # easy, medium, hard
    topic: str
    expected_complexity: str  # e.g., "O(n)", "O(n log n)"
    expected_space_complexity: str = "O(n)"  # e.g., "O(1)", "O(n)"
    expected_time_minutes: int = 30
    tags: List[str] = field(default_factory=list)
    description: str = ""
    function_name: str = "solution"
    starter_code: str = ""
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "problem_id": self.problem_id,
            "title": self.title,
            "difficulty": self.difficulty,
            "topic": self.topic,
            "expected_complexity": self.expected_complexity,
            "expected_space_complexity": self.expected_space_complexity,
            "expected_time_minutes": self.expected_time_minutes,
            "tags": self.tags,
            "description": self.description,
            "function_name": self.function_name,
            "starter_code": self.starter_code,
            "test_cases": self.test_cases
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Problem":
        """Create Problem from dictionary."""
        return cls(
            problem_id=data["problem_id"],
            title=data["title"],
            difficulty=data["difficulty"],
            topic=data["topic"],
            expected_complexity=data["expected_complexity"],
            expected_space_complexity=data.get("expected_space_complexity", "O(n)"),
            expected_time_minutes=data.get("expected_time_minutes", 30),
            tags=data.get("tags", []),
            description=data.get("description", ""),
            function_name=data.get("function_name", "solution"),
            starter_code=data.get("starter_code", ""),
            test_cases=data.get("test_cases", [])
        )


class ProblemBank:
    """Collection of problems with filtering capabilities."""
    
    def __init__(self):
        self.problems: Dict[str, Problem] = {}
    
    def add_problem(self, problem: Problem):
        """Add a problem to the bank."""
        self.problems[problem.problem_id] = problem
    
    def get_problem(self, problem_id: str) -> Optional[Problem]:
        """Get a problem by ID."""
        return self.problems.get(problem_id)
    
    def get_by_topic(self, topic: str) -> List[Problem]:
        """Get all problems for a specific topic."""
        return [p for p in self.problems.values() if p.topic == topic]
    
    def get_by_difficulty(self, difficulty: str) -> List[Problem]:
        """Get all problems for a specific difficulty."""
        return [p for p in self.problems.values() if p.difficulty == difficulty]
    
    def get_by_topic_and_difficulty(self, topic: str, difficulty: str) -> List[Problem]:
        """Get problems matching both topic and difficulty."""
        return [
            p for p in self.problems.values() 
            if p.topic == topic and p.difficulty == difficulty
        ]
    
    def get_unsolved(self, solved_ids: List[str]) -> List[Problem]:
        """Get problems not yet solved by user."""
        return [
            p for p in self.problems.values() 
            if p.problem_id not in solved_ids
        ]
    
    def get_unsolved_by_topic(self, topic: str, solved_ids: List[str]) -> List[Problem]:
        """Get unsolved problems for a specific topic."""
        return [
            p for p in self.problems.values() 
            if p.topic == topic and p.problem_id not in solved_ids
        ]
    
    def load_from_list(self, problems_data: List[Dict]):
        """Load problems from a list of dictionaries."""
        for data in problems_data:
            problem = Problem.from_dict(data)
            self.add_problem(problem)
    
    def to_list(self) -> List[Dict]:
        """Export all problems as a list of dictionaries."""
        return [p.to_dict() for p in self.problems.values()]
    
    def get_all_topics(self) -> List[str]:
        """Get list of all unique topics."""
        return list(set(p.topic for p in self.problems.values()))
    
    def __len__(self) -> int:
        return len(self.problems)
