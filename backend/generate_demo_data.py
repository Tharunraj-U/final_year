"""
Generate sample submission data for demo users to show personalized recommendations.
Each user has different performance patterns:
- Tharun: Expert in Arrays/Strings, struggles with DP
- Irfan: Good at DP, struggles with Graphs
- Jai: Beginner, mostly Easy problems, uses brute force
- Vijay: Advanced, solves Hard problems optimally
"""

import json
from datetime import datetime, timedelta

def generate_sample_data():
    submissions = {}
    users = {}
    
    # THARUN - Expert in Arrays/Strings, struggles with Dynamic Programming
    tharun_subs = [
        # Arrays - Expert (all solved optimally)
        {
            "problem_id": "arr-001",
            "problem_title": "Two Sum",
            "topic": "arrays",
            "difficulty": "easy",
            "code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 8,
            "expected_time_minutes": 15,
            "attempt_number": 1,
            "score": 95,
            "time_complexity": {"estimate": "O(n)", "is_optimal": True},
            "space_complexity": {"estimate": "O(n)", "is_optimal": True},
            "algorithm_type": {"primary": "Hash Map", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "Hash Map"}, "time_complexity": {"is_optimal": True}}
        },
        {
            "problem_id": "arr-002",
            "problem_title": "Maximum Subarray",
            "topic": "arrays",
            "difficulty": "medium",
            "code": "def max_subarray(nums):\n    max_sum = curr_sum = nums[0]\n    for num in nums[1:]:\n        curr_sum = max(num, curr_sum + num)\n        max_sum = max(max_sum, curr_sum)\n    return max_sum",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 12,
            "score": 98,
            "time_complexity": {"estimate": "O(n)", "is_optimal": True},
            "algorithm_type": {"primary": "Kadane's Algorithm", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "Kadane's Algorithm"}, "time_complexity": {"is_optimal": True}}
        },
        {
            "problem_id": "str-001",
            "problem_title": "Valid Anagram",
            "topic": "strings",
            "difficulty": "easy",
            "code": "def is_anagram(s, t):\n    return sorted(s) == sorted(t)",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 5,
            "score": 90,
            "time_complexity": {"estimate": "O(n log n)", "is_optimal": False},
            "algorithm_type": {"primary": "Sorting", "is_appropriate": True},
            "mastery_level": "Proficient",
            "ai_analysis": {"algorithm_type": {"primary": "Sorting"}, "time_complexity": {"is_optimal": False}}
        },
        # DP - Struggles (low scores, multiple attempts)
        {
            "problem_id": "dp-001",
            "problem_title": "Climbing Stairs",
            "topic": "dynamic_programming",
            "difficulty": "easy",
            "code": "def climb_stairs(n):\n    if n <= 2:\n        return n\n    return climb_stairs(n-1) + climb_stairs(n-2)",
            "language": "python",
            "passed": False,
            "passed_count": 2,
            "total_count": 5,
            "time_taken_minutes": 25,
            "score": 40,
            "time_complexity": {"estimate": "O(2^n)", "is_optimal": False},
            "algorithm_type": {"primary": "Brute Force Recursion", "is_appropriate": False, "better_approach": "Use DP with memoization"},
            "mastery_level": "Beginner",
            "ai_analysis": {"algorithm_type": {"primary": "Brute Force Recursion"}, "time_complexity": {"is_optimal": False}, "test_case_analysis": {"failure_patterns": ["timeout", "large inputs"]}}
        },
        {
            "problem_id": "dp-002",
            "problem_title": "House Robber",
            "topic": "dynamic_programming",
            "difficulty": "medium",
            "code": "# Couldn't solve",
            "language": "python",
            "passed": False,
            "passed_count": 1,
            "total_count": 5,
            "time_taken_minutes": 40,
            "score": 20,
            "time_complexity": {"estimate": "Unknown", "is_optimal": False},
            "algorithm_type": {"primary": "Unknown", "is_appropriate": False},
            "mastery_level": "Beginner",
            "ai_analysis": {"algorithm_type": {"primary": "Unknown"}, "test_case_analysis": {"failure_patterns": ["logic error", "edge cases"]}}
        }
    ]
    
    # IRFAN - Good at DP, struggles with Graphs
    irfan_subs = [
        # DP - Expert
        {
            "problem_id": "dp-001",
            "problem_title": "Climbing Stairs",
            "topic": "dynamic_programming",
            "difficulty": "easy",
            "code": "def climb_stairs(n):\n    if n <= 2:\n        return n\n    dp = [0] * (n + 1)\n    dp[1], dp[2] = 1, 2\n    for i in range(3, n + 1):\n        dp[i] = dp[i-1] + dp[i-2]\n    return dp[n]",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 10,
            "score": 95,
            "time_complexity": {"estimate": "O(n)", "is_optimal": True},
            "algorithm_type": {"primary": "Dynamic Programming", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "Dynamic Programming"}, "time_complexity": {"is_optimal": True}}
        },
        {
            "problem_id": "dp-002",
            "problem_title": "House Robber",
            "topic": "dynamic_programming",
            "difficulty": "medium",
            "code": "def rob(nums):\n    if len(nums) <= 2:\n        return max(nums) if nums else 0\n    dp = [0] * len(nums)\n    dp[0] = nums[0]\n    dp[1] = max(nums[0], nums[1])\n    for i in range(2, len(nums)):\n        dp[i] = max(dp[i-1], dp[i-2] + nums[i])\n    return dp[-1]",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 15,
            "score": 92,
            "time_complexity": {"estimate": "O(n)", "is_optimal": True},
            "algorithm_type": {"primary": "Dynamic Programming", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "Dynamic Programming"}, "time_complexity": {"is_optimal": True}}
        },
        # Graphs - Struggles
        {
            "problem_id": "graph-001",
            "problem_title": "Number of Islands",
            "topic": "graphs",
            "difficulty": "medium",
            "code": "# Couldn't implement DFS correctly",
            "language": "python",
            "passed": False,
            "passed_count": 2,
            "total_count": 5,
            "time_taken_minutes": 45,
            "score": 30,
            "time_complexity": {"estimate": "Unknown", "is_optimal": False},
            "algorithm_type": {"primary": "Attempted DFS", "is_appropriate": True, "better_approach": "Need to learn DFS/BFS properly"},
            "mastery_level": "Beginner",
            "ai_analysis": {"algorithm_type": {"primary": "Attempted DFS"}, "test_case_analysis": {"failure_patterns": ["edge cases", "visited tracking"]}}
        },
        {
            "problem_id": "graph-002",
            "problem_title": "Clone Graph",
            "topic": "graphs",
            "difficulty": "medium",
            "code": "# Confused with graph traversal",
            "language": "python",
            "passed": False,
            "passed_count": 0,
            "total_count": 5,
            "time_taken_minutes": 50,
            "score": 15,
            "algorithm_type": {"primary": "Unknown", "is_appropriate": False},
            "mastery_level": "Beginner",
            "ai_analysis": {"algorithm_type": {"primary": "Unknown"}, "test_case_analysis": {"failure_patterns": ["graph traversal", "node cloning"]}}
        }
    ]
    
    # JAI - Beginner, uses brute force, mostly easy problems
    jai_subs = [
        {
            "problem_id": "arr-001",
            "problem_title": "Two Sum",
            "topic": "arrays",
            "difficulty": "easy",
            "code": "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 20,
            "score": 65,
            "time_complexity": {"estimate": "O(n²)", "is_optimal": False},
            "algorithm_type": {"primary": "Brute Force", "is_appropriate": False, "better_approach": "Use Hash Map for O(n)"},
            "mastery_level": "Developing",
            "ai_analysis": {"algorithm_type": {"primary": "Brute Force"}, "time_complexity": {"is_optimal": False}}
        },
        {
            "problem_id": "arr-003",
            "problem_title": "Contains Duplicate",
            "topic": "arrays",
            "difficulty": "easy",
            "code": "def contains_duplicate(nums):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] == nums[j]:\n                return True\n    return False",
            "language": "python",
            "passed": True,
            "passed_count": 3,
            "total_count": 5,
            "time_taken_minutes": 15,
            "score": 55,
            "time_complexity": {"estimate": "O(n²)", "is_optimal": False},
            "algorithm_type": {"primary": "Brute Force", "is_appropriate": False, "better_approach": "Use Set for O(n)"},
            "mastery_level": "Developing",
            "ai_analysis": {"algorithm_type": {"primary": "Brute Force"}, "time_complexity": {"is_optimal": False}, "test_case_analysis": {"failure_patterns": ["timeout", "large inputs"]}}
        },
        {
            "problem_id": "str-001",
            "problem_title": "Valid Anagram",
            "topic": "strings",
            "difficulty": "easy",
            "code": "def is_anagram(s, t):\n    if len(s) != len(t):\n        return False\n    return sorted(s) == sorted(t)",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 10,
            "score": 70,
            "time_complexity": {"estimate": "O(n log n)", "is_optimal": False},
            "algorithm_type": {"primary": "Sorting", "is_appropriate": True},
            "mastery_level": "Developing",
            "ai_analysis": {"algorithm_type": {"primary": "Sorting"}, "time_complexity": {"is_optimal": False}}
        }
    ]
    
    # VIJAY - Advanced, solves hard problems optimally
    vijay_subs = [
        {
            "problem_id": "arr-001",
            "problem_title": "Two Sum",
            "topic": "arrays",
            "difficulty": "easy",
            "code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 5,
            "score": 100,
            "time_complexity": {"estimate": "O(n)", "is_optimal": True},
            "algorithm_type": {"primary": "Hash Map", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "Hash Map"}, "time_complexity": {"is_optimal": True}}
        },
        {
            "problem_id": "dp-003",
            "problem_title": "Longest Increasing Subsequence",
            "topic": "dynamic_programming",
            "difficulty": "hard",
            "code": "def length_of_lis(nums):\n    from bisect import bisect_left\n    tails = []\n    for num in nums:\n        pos = bisect_left(tails, num)\n        if pos == len(tails):\n            tails.append(num)\n        else:\n            tails[pos] = num\n    return len(tails)",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 20,
            "score": 98,
            "time_complexity": {"estimate": "O(n log n)", "is_optimal": True},
            "algorithm_type": {"primary": "Binary Search + DP", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "Binary Search + DP"}, "time_complexity": {"is_optimal": True}}
        },
        {
            "problem_id": "graph-001",
            "problem_title": "Number of Islands",
            "topic": "graphs",
            "difficulty": "medium",
            "code": "def num_islands(grid):\n    def dfs(i, j):\n        if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]) or grid[i][j] != '1':\n            return\n        grid[i][j] = '0'\n        dfs(i+1, j)\n        dfs(i-1, j)\n        dfs(i, j+1)\n        dfs(i, j-1)\n    \n    count = 0\n    for i in range(len(grid)):\n        for j in range(len(grid[0])):\n            if grid[i][j] == '1':\n                dfs(i, j)\n                count += 1\n    return count",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 15,
            "score": 95,
            "time_complexity": {"estimate": "O(m*n)", "is_optimal": True},
            "algorithm_type": {"primary": "DFS", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "DFS"}, "time_complexity": {"is_optimal": True}}
        },
        {
            "problem_id": "tree-002",
            "problem_title": "Binary Tree Level Order Traversal",
            "topic": "trees",
            "difficulty": "medium",
            "code": "from collections import deque\ndef level_order(root):\n    if not root:\n        return []\n    result = []\n    queue = deque([root])\n    while queue:\n        level = []\n        for _ in range(len(queue)):\n            node = queue.popleft()\n            level.append(node.val)\n            if node.left:\n                queue.append(node.left)\n            if node.right:\n                queue.append(node.right)\n        result.append(level)\n    return result",
            "language": "python",
            "passed": True,
            "passed_count": 5,
            "total_count": 5,
            "time_taken_minutes": 12,
            "score": 96,
            "time_complexity": {"estimate": "O(n)", "is_optimal": True},
            "algorithm_type": {"primary": "BFS", "is_appropriate": True},
            "mastery_level": "Expert",
            "ai_analysis": {"algorithm_type": {"primary": "BFS"}, "time_complexity": {"is_optimal": True}}
        }
    ]
    
    # Add timestamps
    base_time = datetime.now() - timedelta(days=7)
    
    def add_metadata(subs, user_id):
        for i, sub in enumerate(subs):
            sub["submission_id"] = f"{user_id}_{i+1}"
            sub["submitted_at"] = (base_time + timedelta(hours=i*5)).isoformat()
        return subs
    
    submissions["student_tharun"] = add_metadata(tharun_subs, "student_tharun")
    submissions["student_irfan"] = add_metadata(irfan_subs, "student_irfan")
    submissions["student_jai"] = add_metadata(jai_subs, "student_jai")
    submissions["student_vijay"] = add_metadata(vijay_subs, "student_vijay")
    
    # Create users data
    users = {
        "student_tharun": {
            "user_id": "student_tharun",
            "created_at": (base_time - timedelta(days=30)).isoformat(),
            "total_submissions": len(tharun_subs),
            "problems_solved": ["arr-001", "arr-002", "str-001"]
        },
        "student_irfan": {
            "user_id": "student_irfan",
            "created_at": (base_time - timedelta(days=25)).isoformat(),
            "total_submissions": len(irfan_subs),
            "problems_solved": ["dp-001", "dp-002"]
        },
        "student_jai": {
            "user_id": "student_jai",
            "created_at": (base_time - timedelta(days=10)).isoformat(),
            "total_submissions": len(jai_subs),
            "problems_solved": ["arr-001", "arr-003", "str-001"]
        },
        "student_vijay": {
            "user_id": "student_vijay",
            "created_at": (base_time - timedelta(days=60)).isoformat(),
            "total_submissions": len(vijay_subs),
            "problems_solved": ["arr-001", "dp-003", "graph-001", "tree-002"]
        }
    }
    
    return submissions, users

if __name__ == "__main__":
    submissions, users = generate_sample_data()
    
    # Read existing data
    try:
        with open("data/submissions.json", "r") as f:
            existing_subs = json.load(f)
    except:
        existing_subs = {}
    
    try:
        with open("data/users.json", "r") as f:
            existing_users = json.load(f)
    except:
        existing_users = {}
    
    # Merge new demo data
    existing_subs.update(submissions)
    existing_users.update(users)
    
    # Save
    with open("data/submissions.json", "w") as f:
        json.dump(existing_subs, f, indent=2)
    
    with open("data/users.json", "w") as f:
        json.dump(existing_users, f, indent=2)
    
    print("✅ Sample data created!")
    print(f"   - Tharun: {len(submissions['student_tharun'])} submissions (Expert in Arrays, struggles with DP)")
    print(f"   - Irfan: {len(submissions['student_irfan'])} submissions (Expert in DP, struggles with Graphs)")
    print(f"   - Jai: {len(submissions['student_jai'])} submissions (Beginner, uses Brute Force)")
    print(f"   - Vijay: {len(submissions['student_vijay'])} submissions (Advanced, solves Hard problems)")
