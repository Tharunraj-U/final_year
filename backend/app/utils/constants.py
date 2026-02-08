"""
Constants and configuration for the AI Learning Assistant.
"""

# Scoring weights for performance calculation
SCORING_WEIGHTS = {
    "correctness": 0.35,
    "efficiency": 0.30,
    "speed": 0.20,
    "attempts": 0.15
}

# Complexity hierarchy (lower index = better complexity)
COMPLEXITY_ORDER = [
    "O(1)",
    "O(log n)",
    "O(n)",
    "O(n log n)",
    "O(n^2)",
    "O(n^2 log n)",
    "O(n^3)",
    "O(2^n)",
    "O(n!)"
]

# Complexity scoring matrix
# Score based on how close user's complexity is to expected
COMPLEXITY_SCORES = {
    0: 1.0,   # Exact match
    1: 0.8,   # One level worse
    2: 0.5,   # Two levels worse
    3: 0.3,   # Three levels worse
    4: 0.1,   # Four+ levels worse (brute force)
}

# Difficulty levels
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

# Mastery thresholds for each difficulty
MASTERY_THRESHOLDS = {
    "easy": {
        "min_solved": 5,
        "min_accuracy": 0.80,
        "max_avg_attempts": 2.0
    },
    "medium": {
        "min_solved": 10,
        "min_accuracy": 0.70,
        "max_avg_attempts": 3.0
    },
    "hard": {
        "min_solved": 5,
        "min_accuracy": 0.60,
        "max_avg_attempts": 4.0
    }
}

# Topics/categories for problems
PROBLEM_TOPICS = [
    "arrays",
    "strings",
    "linked_lists",
    "stacks_queues",
    "trees",
    "graphs",
    "dynamic_programming",
    "greedy",
    "binary_search",
    "sorting",
    "hashing",
    "recursion",
    "backtracking",
    "bit_manipulation",
    "math"
]

# Expected time limits per difficulty (in minutes)
EXPECTED_TIME_LIMITS = {
    "easy": 15,
    "medium": 30,
    "hard": 45
}

# Skill level thresholds based on overall score
SKILL_LEVEL_THRESHOLDS = {
    "beginner": (0, 40),
    "intermediate": (40, 70),
    "advanced": (70, 100)
}

# Efficiency ratings
EFFICIENCY_RATINGS = {
    "optimal": (0.8, 1.0),
    "suboptimal": (0.5, 0.8),
    "brute_force": (0.0, 0.5)
}

# Recommendation settings
RECOMMENDATION_CONFIG = {
    "max_recommendations": 5,
    "weakness_priority_weight": 0.6,
    "progression_weight": 0.4,
    "min_topic_exposure": 3  # Min problems before moving to next topic
}
