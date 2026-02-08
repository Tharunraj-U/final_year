import json
import os
from pathlib import Path

TARGET_COUNT = 200
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "problems.json"

TOPICS = [
    "arrays", "strings", "sliding_window", "two_pointers", "binary_search",
    "dynamic_programming", "backtracking", "greedy", "stacks", "hashing",
    "heap", "bit_manipulation", "graphs", "trees", "linked_lists"
]

DIFF_SEQ = [
    ("easy", 15),
    ("medium", 30),
    ("hard", 45),
]

# Simple per-topic templates: (description, test_cases, expected_complexity)
# All use function_name = "solution"
TEMPLATES = {
    "arrays": {
        "desc": "Return the sum of elements in the array.",
        "tests": [ {"input": [[1,2,3]], "expected": 6}, {"input": [[-1,5,0,2]], "expected": 6} ],
        "complexity": "O(n)",
        "starter": "def solution(nums: list) -> int:\n    # Return sum of array\n    pass"
    },
    "strings": {
        "desc": "Return the reversed string.",
        "tests": [ {"input": ["abc"], "expected": "cba"}, {"input": ["racecar"], "expected": "racecar"} ],
        "complexity": "O(n)",
        "starter": "def solution(s: str) -> str:\n    # Return reversed string\n    pass"
    },
    "sliding_window": {
        "desc": "Given an array and k, return max sum of a window size k.",
        "tests": [ {"input": [[1,2,3,4,5], 2], "expected": 9}, {"input": [[-1,4,2,10,23,3,1,0,20], 4], "expected": 39} ],
        "complexity": "O(n)",
        "starter": "def solution(nums: list, k: int) -> int:\n    # Max sum of window size k\n    pass"
    },
    "two_pointers": {
        "desc": "Check if the string is a palindrome (alphanumeric, case-insensitive).",
        "tests": [ {"input": ["A man, a plan, a canal: Panama"], "expected": True}, {"input": ["race a car"], "expected": False} ],
        "complexity": "O(n)",
        "starter": "def solution(s: str) -> bool:\n    # Palindrome check with two pointers\n    pass"
    },
    "binary_search": {
        "desc": "Return index of target in sorted array or -1 if not found.",
        "tests": [ {"input": [[-1,0,3,5,9,12], 9], "expected": 4}, {"input": [[-1,0,3,5,9,12], 2], "expected": -1} ],
        "complexity": "O(log n)",
        "starter": "def solution(nums: list, target: int) -> int:\n    # Binary search\n    pass"
    },
    "dynamic_programming": {
        "desc": "Given n, return nth Fibonacci number.",
        "tests": [ {"input": [5], "expected": 5}, {"input": [10], "expected": 55} ],
        "complexity": "O(n)",
        "starter": "def solution(n: int) -> int:\n    # Fibonacci DP\n    pass"
    },
    "backtracking": {
        "desc": "Given digits, return count of possible letter combinations like phone keypad.",
        "tests": [ {"input": ["23"], "expected": 9}, {"input": [""], "expected": 0} ],
        "complexity": "O(4^n)",
        "starter": "def solution(digits: str) -> int:\n    # Return number of combinations\n    pass"
    },
    "greedy": {
        "desc": "Given coins and amount, return min number of coins (classic coin change greedy where canonical).",
        "tests": [ {"input": [[1,2,5], 11], "expected": 3}, {"input": [[2], 3], "expected": -1} ],
        "complexity": "O(n log n)",
        "starter": "def solution(coins: list, amount: int) -> int:\n    # Greedy coin change (works for canonical systems)\n    pass"
    },
    "stacks": {
        "desc": "Validate parentheses string consisting of '()[]{}'.",
        "tests": [ {"input": ["()[]{}"], "expected": True}, {"input": ["(]"], "expected": False} ],
        "complexity": "O(n)",
        "starter": "def solution(s: str) -> bool:\n    # Valid parentheses using stack\n    pass"
    },
    "hashing": {
        "desc": "Return True if the array contains any duplicate value.",
        "tests": [ {"input": [[1,2,3,1]], "expected": True}, {"input": [[1,2,3,4]], "expected": False} ],
        "complexity": "O(n)",
        "starter": "def solution(nums: list) -> bool:\n    # Contains duplicate using set\n    pass"
    },
    "heap": {
        "desc": "Return k largest elements from the array (any order).",
        "tests": [ {"input": [[3,2,1,5,6,4], 2], "expected": [6,5]}, {"input": [[1], 1], "expected": [1]} ],
        "complexity": "O(n log k)",
        "starter": "def solution(nums: list, k: int) -> list:\n    # k largest using heap\n    pass"
    },
    "bit_manipulation": {
        "desc": "Given a list where every element appears twice except one, return the single number.",
        "tests": [ {"input": [[2,2,1]], "expected": 1}, {"input": [[4,1,2,1,2]], "expected": 4} ],
        "complexity": "O(n)",
        "starter": "def solution(nums: list) -> int:\n    # Single number using XOR\n    pass"
    },
    "graphs": {
        "desc": "Given adjacency list (dict of node->list), return number of connected components.",
        "tests": [ {"input": [{"0":["1"],"1":["0"],"2":[]}], "expected": 2}, {"input": [{"0":["1","2"],"1":["0"],"2":["0"]}], "expected": 1} ],
        "complexity": "O(V+E)",
        "starter": "def solution(graph: dict) -> int:\n    # Count connected components\n    pass"
    },
    "trees": {
        "desc": "Given array representation of level-order tree values (None for missing), return count of non-null nodes.",
        "tests": [ {"input": [[1,2,3,None,4]], "expected": 4}, {"input": [[None]], "expected": 0} ],
        "complexity": "O(n)",
        "starter": "def solution(levels: list) -> int:\n    # Count non-null nodes in level-order array\n    pass"
    },
    "linked_lists": {
        "desc": "Given list of values, return True if it contains a cycle flag as second param (mocked input).",
        "tests": [ {"input": [[1,2,3], False], "expected": False}, {"input": [[1,2], True], "expected": True} ],
        "complexity": "O(n)",
        "starter": "def solution(values: list, has_cycle: bool) -> bool:\n    # Mocked linked list cycle detection input\n    pass"
    },
}


def main():
    if not DATA_PATH.exists():
        raise SystemExit(f"Problems file not found: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        problems = json.load(f)

    existing_ids = {p["problem_id"] for p in problems}
    current = len(problems)
    if current >= TARGET_COUNT:
        print(f"Already have {current} problems (>= {TARGET_COUNT}). Nothing to do.")
        return

    next_index = 1
    # Find next available numeric suffix for generated problems
    while f"gen-{next_index:03d}" in existing_ids:
        next_index += 1

    added = 0
    t_idx = 0
    d_idx = 0

    while len(problems) < TARGET_COUNT:
        topic = TOPICS[t_idx % len(TOPICS)]
        difficulty, exp_minutes = DIFF_SEQ[d_idx % len(DIFF_SEQ)]
        tid = f"gen-{next_index:03d}"
        tmpl = TEMPLATES[topic]

        problem = {
            "problem_id": tid,
            "title": f"{topic.replace('_', ' ').title()} Practice {next_index}",
            "difficulty": difficulty,
            "topic": topic,
            "expected_complexity": tmpl["complexity"],
            "expected_time_minutes": exp_minutes,
            "tags": [topic],
            "description": tmpl["desc"],
            "function_name": "solution",
            "starter_code": tmpl["starter"],
            "test_cases": tmpl["tests"],
        }

        problems.append(problem)
        existing_ids.add(tid)
        next_index += 1
        t_idx += 1
        d_idx += 1
        added += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(problems, f, indent=2)

    print(f"Added {added} problems. Total is now {len(problems)}.")


if __name__ == "__main__":
    main()
