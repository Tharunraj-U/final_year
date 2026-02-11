"""
Complexity comparison utilities.
"""

from .constants import COMPLEXITY_ORDER, COMPLEXITY_SCORES


def normalize_complexity(complexity: str) -> str:
    """
    Normalize complexity string to standard format.
    
    Args:
        complexity: Raw complexity string (e.g., "O(n)", "o(n)", "O(N)")
    
    Returns:
        Normalized complexity string
    """
    if not complexity:
        return "O(n)"
    
    # Convert to lowercase and standardize
    c = complexity.lower().strip()
    
    # Map common variations
    mappings = {
        "o(1)": "O(1)",
        "o(log n)": "O(log n)",
        "o(logn)": "O(log n)",
        "o(log(n))": "O(log n)",
        "o(n)": "O(n)",
        "o(n log k)": "O(n log k)",
        "o(n+m)": "O(n+m)",
        "o(n + m)": "O(n+m)",
        "o(n log n)": "O(n log n)",
        "o(nlogn)": "O(n log n)",
        "o(n*logn)": "O(n log n)",
        "o(n*log n)": "O(n log n)",
        "o(n*log(n))": "O(n log n)",
        "o(n*k log k)": "O(n*k log k)",
        "o(v+e)": "O(V+E)",
        "o(v + e)": "O(V+E)",
        "o(n^2)": "O(n^2)",
        "o(n*n)": "O(n^2)",
        "o(n²)": "O(n^2)",
        "o(n*amount)": "O(n*amount)",
        "o(m*n)": "O(m*n)",
        "o(m * n)": "O(m*n)",
        "o(mn)": "O(m*n)",
        "o(n^2 log n)": "O(n^2 log n)",
        "o(n^3)": "O(n^3)",
        "o(n³)": "O(n^3)",
        "o(2^n)": "O(2^n)",
        "o(n * 2^n)": "O(n * 2^n)",
        "o(n*2^n)": "O(n * 2^n)",
        "o(3^n)": "O(3^n)",
        "o(4^n)": "O(4^n)",
        "o(n!)": "O(n!)"
    }
    
    return mappings.get(c, "O(n)")


def get_complexity_index(complexity: str) -> int:
    """
    Get the index of a complexity in the hierarchy.
    
    Args:
        complexity: Normalized complexity string
    
    Returns:
        Index in COMPLEXITY_ORDER (0 = best, higher = worse)
    """
    normalized = normalize_complexity(complexity)
    try:
        return COMPLEXITY_ORDER.index(normalized)
    except ValueError:
        return len(COMPLEXITY_ORDER) - 1  # Assume worst if unknown


def compare_complexity(user_complexity: str, expected_complexity: str) -> float:
    """
    Compare user's complexity against expected optimal complexity.
    
    Args:
        user_complexity: User's solution complexity
        expected_complexity: Expected optimal complexity
    
    Returns:
        Score between 0.0 and 1.0 (1.0 = optimal match)
    """
    user_idx = get_complexity_index(user_complexity)
    expected_idx = get_complexity_index(expected_complexity)
    
    # Calculate the difference (negative means user did better!)
    diff = user_idx - expected_idx
    
    if diff <= 0:
        # User met or exceeded expectations
        return 1.0
    
    # User's solution is worse than expected
    if diff >= len(COMPLEXITY_SCORES):
        diff = max(COMPLEXITY_SCORES.keys())
    
    return COMPLEXITY_SCORES.get(diff, 0.1)


def get_efficiency_label(complexity_score: float) -> str:
    """
    Get human-readable efficiency label.
    
    Args:
        complexity_score: Score from compare_complexity
    
    Returns:
        Efficiency label string
    """
    if complexity_score >= 0.8:
        return "optimal"
    elif complexity_score >= 0.5:
        return "suboptimal"
    else:
        return "brute_force"


def is_brute_force(user_complexity: str, expected_complexity: str) -> bool:
    """
    Check if user's solution is considered brute force.
    
    Args:
        user_complexity: User's solution complexity
        expected_complexity: Expected optimal complexity
    
    Returns:
        True if brute force approach detected
    """
    score = compare_complexity(user_complexity, expected_complexity)
    return score <= 0.5  # Changed from < 0.5 to <= 0.5
