import json

problems = [
    # Arrays
    {
        "problem_id": "arr-001",
        "title": "Two Sum",
        "difficulty": "easy",
        "topic": "arrays",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["arrays", "hash_map"],
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\n**Example:**\n```\nInput: nums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\n```\n\nYou may assume that each input would have exactly one solution.",
        "function_name": "two_sum",
        "starter_code": "def two_sum(nums: list, target: int) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"input": [[3, 2, 4], 6], "expected": [1, 2]},
            {"input": [[3, 3], 6], "expected": [0, 1]}
        ]
    },
    {
        "problem_id": "arr-002",
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "easy",
        "topic": "arrays",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["arrays", "dynamic_programming"],
        "description": "You are given an array `prices` where `prices[i]` is the price of a given stock on the ith day. You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.\n\n**Example:**\n```\nInput: prices = [7, 1, 5, 3, 6, 4]\nOutput: 5\nExplanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6).\n```",
        "function_name": "max_profit",
        "starter_code": "def max_profit(prices: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[7, 1, 5, 3, 6, 4]], "expected": 5},
            {"input": [[7, 6, 4, 3, 1]], "expected": 0},
            {"input": [[1, 2]], "expected": 1}
        ]
    },
    {
        "problem_id": "arr-003",
        "title": "Contains Duplicate",
        "difficulty": "easy",
        "topic": "arrays",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 10,
        "tags": ["arrays", "hash_set"],
        "description": "Given an integer array `nums`, return `true` if any value appears at least twice in the array.\n\n**Example:**\n```\nInput: nums = [1, 2, 3, 1]\nOutput: true\n```",
        "function_name": "contains_duplicate",
        "starter_code": "def contains_duplicate(nums: list) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3, 1]], "expected": True},
            {"input": [[1, 2, 3, 4]], "expected": False},
            {"input": [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], "expected": True}
        ]
    },
    {
        "problem_id": "arr-004",
        "title": "Maximum Subarray",
        "difficulty": "medium",
        "topic": "arrays",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 20,
        "tags": ["arrays", "dynamic_programming", "kadane"],
        "description": "Given an integer array `nums`, find the subarray with the largest sum.\n\n**Example:**\n```\nInput: nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]\nOutput: 6\nExplanation: The subarray [4, -1, 2, 1] has the largest sum.\n```",
        "function_name": "max_subarray",
        "starter_code": "def max_subarray(nums: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
            {"input": [[1]], "expected": 1},
            {"input": [[5, 4, -1, 7, 8]], "expected": 23}
        ]
    },
    {
        "problem_id": "arr-005",
        "title": "Product of Array Except Self",
        "difficulty": "medium",
        "topic": "arrays",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 25,
        "tags": ["arrays", "prefix_sum"],
        "description": "Given an integer array `nums`, return an array where each element is the product of all elements except itself.\n\n**Example:**\n```\nInput: nums = [1, 2, 3, 4]\nOutput: [24, 12, 8, 6]\n```",
        "function_name": "product_except_self",
        "starter_code": "def product_except_self(nums: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3, 4]], "expected": [24, 12, 8, 6]},
            {"input": [[-1, 1, 0, -3, 3]], "expected": [0, 0, 9, 0, 0]}
        ]
    },
    # Strings
    {
        "problem_id": "str-001",
        "title": "Valid Anagram",
        "difficulty": "easy",
        "topic": "strings",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 10,
        "tags": ["strings", "hash_map"],
        "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`.\n\n**Example:**\n```\nInput: s = \"anagram\", t = \"nagaram\"\nOutput: true\n```",
        "function_name": "is_anagram",
        "starter_code": "def is_anagram(s: str, t: str) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": ["anagram", "nagaram"], "expected": True},
            {"input": ["rat", "car"], "expected": False},
            {"input": ["a", "a"], "expected": True}
        ]
    },
    {
        "problem_id": "str-002",
        "title": "Valid Palindrome",
        "difficulty": "easy",
        "topic": "strings",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["strings", "two_pointers"],
        "description": "Check if a phrase is a palindrome after converting to lowercase and removing non-alphanumeric characters.\n\n**Example:**\n```\nInput: s = \"A man, a plan, a canal: Panama\"\nOutput: true\n```",
        "function_name": "is_palindrome",
        "starter_code": "def is_palindrome(s: str) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": ["A man, a plan, a canal: Panama"], "expected": True},
            {"input": ["race a car"], "expected": False},
            {"input": [" "], "expected": True}
        ]
    },
    {
        "problem_id": "str-003",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "medium",
        "topic": "strings",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 25,
        "tags": ["strings", "sliding_window", "hash_set"],
        "description": "Given a string `s`, find the length of the longest substring without repeating characters.\n\n**Example:**\n```\nInput: s = \"abcabcbb\"\nOutput: 3\nExplanation: The answer is \"abc\".\n```",
        "function_name": "length_of_longest_substring",
        "starter_code": "def length_of_longest_substring(s: str) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": ["abcabcbb"], "expected": 3},
            {"input": ["bbbbb"], "expected": 1},
            {"input": ["pwwkew"], "expected": 3}
        ]
    },
    {
        "problem_id": "str-004",
        "title": "Longest Palindromic Substring",
        "difficulty": "medium",
        "topic": "strings",
        "expected_complexity": "O(n^2)",
        "expected_time_minutes": 30,
        "tags": ["strings", "dynamic_programming", "expand_around_center"],
        "description": "Given a string `s`, return the longest palindromic substring.\n\n**Example:**\n```\nInput: s = \"babad\"\nOutput: \"bab\" or \"aba\"\n```",
        "function_name": "longest_palindrome",
        "starter_code": "def longest_palindrome(s: str) -> str:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": ["babad"], "expected": "bab"},
            {"input": ["cbbd"], "expected": "bb"},
            {"input": ["a"], "expected": "a"}
        ]
    },
    # Sliding Window
    {
        "problem_id": "sw-001",
        "title": "Maximum Sum Subarray of Size K",
        "difficulty": "easy",
        "topic": "sliding_window",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["sliding_window", "arrays"],
        "description": "Given an array and a number K, find the maximum sum of any contiguous subarray of size K.\n\n**Example:**\n```\nInput: arr = [2, 1, 5, 1, 3, 2], k = 3\nOutput: 9\nExplanation: Subarray [5, 1, 3] has maximum sum.\n```",
        "function_name": "max_sum_subarray_k",
        "starter_code": "def max_sum_subarray_k(arr: list, k: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[2, 1, 5, 1, 3, 2], 3], "expected": 9},
            {"input": [[2, 3, 4, 1, 5], 2], "expected": 7},
            {"input": [[1, 1, 1, 1, 1], 3], "expected": 3}
        ]
    },
    {
        "problem_id": "sw-002",
        "title": "Minimum Size Subarray Sum",
        "difficulty": "medium",
        "topic": "sliding_window",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 20,
        "tags": ["sliding_window", "two_pointers"],
        "description": "Find the minimal length of a subarray whose sum is >= target.\n\n**Example:**\n```\nInput: target = 7, nums = [2,3,1,2,4,3]\nOutput: 2\nExplanation: [4,3] has the minimal length.\n```",
        "function_name": "min_subarray_len",
        "starter_code": "def min_subarray_len(target: int, nums: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [7, [2, 3, 1, 2, 4, 3]], "expected": 2},
            {"input": [4, [1, 4, 4]], "expected": 1},
            {"input": [11, [1, 1, 1, 1, 1, 1, 1, 1]], "expected": 0}
        ]
    },
    {
        "problem_id": "sw-003",
        "title": "Fruit Into Baskets",
        "difficulty": "medium",
        "topic": "sliding_window",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 25,
        "tags": ["sliding_window", "hash_map"],
        "description": "You have two baskets. Each basket can only hold one type of fruit. Find the maximum number of fruits you can pick.\n\n**Example:**\n```\nInput: fruits = [1, 2, 1]\nOutput: 3\n```",
        "function_name": "total_fruit",
        "starter_code": "def total_fruit(fruits: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 1]], "expected": 3},
            {"input": [[0, 1, 2, 2]], "expected": 3},
            {"input": [[1, 2, 3, 2, 2]], "expected": 4}
        ]
    },
    # Two Pointers
    {
        "problem_id": "tp-001",
        "title": "Two Sum II - Sorted Array",
        "difficulty": "medium",
        "topic": "two_pointers",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["two_pointers", "binary_search"],
        "description": "Given a sorted array, find two numbers that add up to a target. Return their indices (1-indexed).\n\n**Example:**\n```\nInput: numbers = [2,7,11,15], target = 9\nOutput: [1,2]\n```",
        "function_name": "two_sum_sorted",
        "starter_code": "def two_sum_sorted(numbers: list, target: int) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "expected": [1, 2]},
            {"input": [[2, 3, 4], 6], "expected": [1, 3]},
            {"input": [[-1, 0], -1], "expected": [1, 2]}
        ]
    },
    {
        "problem_id": "tp-002",
        "title": "3Sum",
        "difficulty": "medium",
        "topic": "two_pointers",
        "expected_complexity": "O(n^2)",
        "expected_time_minutes": 30,
        "tags": ["two_pointers", "sorting"],
        "description": "Find all unique triplets in the array that sum to zero.\n\n**Example:**\n```\nInput: nums = [-1, 0, 1, 2, -1, -4]\nOutput: [[-1, -1, 2], [-1, 0, 1]]\n```",
        "function_name": "three_sum",
        "starter_code": "def three_sum(nums: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[-1, 0, 1, 2, -1, -4]], "expected": [[-1, -1, 2], [-1, 0, 1]]},
            {"input": [[0, 1, 1]], "expected": []},
            {"input": [[0, 0, 0]], "expected": [[0, 0, 0]]}
        ]
    },
    {
        "problem_id": "tp-003",
        "title": "Container With Most Water",
        "difficulty": "medium",
        "topic": "two_pointers",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 20,
        "tags": ["two_pointers", "greedy"],
        "description": "Given n non-negative integers representing heights, find two lines that form a container with the most water.\n\n**Example:**\n```\nInput: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49\n```",
        "function_name": "max_area",
        "starter_code": "def max_area(height: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 8, 6, 2, 5, 4, 8, 3, 7]], "expected": 49},
            {"input": [[1, 1]], "expected": 1},
            {"input": [[4, 3, 2, 1, 4]], "expected": 16}
        ]
    },
    # Binary Search
    {
        "problem_id": "bs-001",
        "title": "Binary Search",
        "difficulty": "easy",
        "topic": "binary_search",
        "expected_complexity": "O(log n)",
        "expected_time_minutes": 10,
        "tags": ["binary_search"],
        "description": "Given a sorted array and a target value, return the index if found, otherwise -1.\n\n**Example:**\n```\nInput: nums = [-1,0,3,5,9,12], target = 9\nOutput: 4\n```",
        "function_name": "binary_search",
        "starter_code": "def binary_search(nums: list, target: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[-1, 0, 3, 5, 9, 12], 9], "expected": 4},
            {"input": [[-1, 0, 3, 5, 9, 12], 2], "expected": -1},
            {"input": [[5], 5], "expected": 0}
        ]
    },
    {
        "problem_id": "bs-002",
        "title": "Search in Rotated Sorted Array",
        "difficulty": "medium",
        "topic": "binary_search",
        "expected_complexity": "O(log n)",
        "expected_time_minutes": 25,
        "tags": ["binary_search", "arrays"],
        "description": "Search for a target in a rotated sorted array. Return the index or -1.\n\n**Example:**\n```\nInput: nums = [4,5,6,7,0,1,2], target = 0\nOutput: 4\n```",
        "function_name": "search_rotated",
        "starter_code": "def search_rotated(nums: list, target: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[4, 5, 6, 7, 0, 1, 2], 0], "expected": 4},
            {"input": [[4, 5, 6, 7, 0, 1, 2], 3], "expected": -1},
            {"input": [[1], 0], "expected": -1}
        ]
    },
    {
        "problem_id": "bs-003",
        "title": "Find Minimum in Rotated Sorted Array",
        "difficulty": "medium",
        "topic": "binary_search",
        "expected_complexity": "O(log n)",
        "expected_time_minutes": 20,
        "tags": ["binary_search"],
        "description": "Find the minimum element in a rotated sorted array.\n\n**Example:**\n```\nInput: nums = [3,4,5,1,2]\nOutput: 1\n```",
        "function_name": "find_min",
        "starter_code": "def find_min(nums: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[3, 4, 5, 1, 2]], "expected": 1},
            {"input": [[4, 5, 6, 7, 0, 1, 2]], "expected": 0},
            {"input": [[11, 13, 15, 17]], "expected": 11}
        ]
    },
    # Linked Lists
    {
        "problem_id": "ll-001",
        "title": "Reverse Linked List",
        "difficulty": "easy",
        "topic": "linked_lists",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["linked_lists", "recursion"],
        "description": "Reverse a singly linked list. Given as an array, return reversed array.\n\n**Example:**\n```\nInput: head = [1, 2, 3, 4, 5]\nOutput: [5, 4, 3, 2, 1]\n```",
        "function_name": "reverse_list",
        "starter_code": "def reverse_list(head: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5]], "expected": [5, 4, 3, 2, 1]},
            {"input": [[1, 2]], "expected": [2, 1]},
            {"input": [[]], "expected": []}
        ]
    },
    {
        "problem_id": "ll-002",
        "title": "Merge Two Sorted Lists",
        "difficulty": "easy",
        "topic": "linked_lists",
        "expected_complexity": "O(n+m)",
        "expected_time_minutes": 15,
        "tags": ["linked_lists", "recursion"],
        "description": "Merge two sorted linked lists (arrays) into one sorted list.\n\n**Example:**\n```\nInput: list1 = [1,2,4], list2 = [1,3,4]\nOutput: [1,1,2,3,4,4]\n```",
        "function_name": "merge_two_lists",
        "starter_code": "def merge_two_lists(list1: list, list2: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 4], [1, 3, 4]], "expected": [1, 1, 2, 3, 4, 4]},
            {"input": [[], []], "expected": []},
            {"input": [[], [0]], "expected": [0]}
        ]
    },
    {
        "problem_id": "ll-003",
        "title": "Linked List Cycle Detection",
        "difficulty": "easy",
        "topic": "linked_lists",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["linked_lists", "two_pointers", "floyd"],
        "description": "Given an array representing a linked list and a pos indicating where the tail connects (or -1 for no cycle), return True if there is a cycle.\n\n**Example:**\n```\nInput: head = [3,2,0,-4], pos = 1\nOutput: true\n```",
        "function_name": "has_cycle",
        "starter_code": "def has_cycle(head: list, pos: int) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[3, 2, 0, -4], 1], "expected": True},
            {"input": [[1, 2], 0], "expected": True},
            {"input": [[1], -1], "expected": False}
        ]
    },
    # Trees
    {
        "problem_id": "tree-001",
        "title": "Maximum Depth of Binary Tree",
        "difficulty": "easy",
        "topic": "trees",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["trees", "dfs", "recursion"],
        "description": "Given a binary tree as array (level order, None for null nodes), return its maximum depth.\n\n**Example:**\n```\nInput: root = [3, 9, 20, None, None, 15, 7]\nOutput: 3\n```",
        "function_name": "max_depth",
        "starter_code": "def max_depth(root: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[3, 9, 20, None, None, 15, 7]], "expected": 3},
            {"input": [[1, None, 2]], "expected": 2},
            {"input": [[]], "expected": 0}
        ]
    },
    {
        "problem_id": "tree-002",
        "title": "Validate Binary Search Tree",
        "difficulty": "medium",
        "topic": "trees",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 25,
        "tags": ["trees", "dfs", "bst"],
        "description": "Given a binary tree as array, determine if it is a valid BST.\n\n**Example:**\n```\nInput: root = [2, 1, 3]\nOutput: true\n```",
        "function_name": "is_valid_bst",
        "starter_code": "def is_valid_bst(root: list) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[2, 1, 3]], "expected": True},
            {"input": [[5, 1, 4, None, None, 3, 6]], "expected": False},
            {"input": [[1]], "expected": True}
        ]
    },
    {
        "problem_id": "tree-003",
        "title": "Invert Binary Tree",
        "difficulty": "easy",
        "topic": "trees",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 10,
        "tags": ["trees", "recursion"],
        "description": "Invert a binary tree (swap left and right children).\n\n**Example:**\n```\nInput: root = [4, 2, 7, 1, 3, 6, 9]\nOutput: [4, 7, 2, 9, 6, 3, 1]\n```",
        "function_name": "invert_tree",
        "starter_code": "def invert_tree(root: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[4, 2, 7, 1, 3, 6, 9]], "expected": [4, 7, 2, 9, 6, 3, 1]},
            {"input": [[2, 1, 3]], "expected": [2, 3, 1]},
            {"input": [[]], "expected": []}
        ]
    },
    # Dynamic Programming
    {
        "problem_id": "dp-001",
        "title": "Climbing Stairs",
        "difficulty": "easy",
        "topic": "dynamic_programming",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["dynamic_programming", "fibonacci"],
        "description": "You can climb 1 or 2 steps at a time. How many distinct ways can you climb n steps?\n\n**Example:**\n```\nInput: n = 3\nOutput: 3\nExplanation: 1+1+1, 1+2, 2+1\n```",
        "function_name": "climb_stairs",
        "starter_code": "def climb_stairs(n: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [2], "expected": 2},
            {"input": [3], "expected": 3},
            {"input": [5], "expected": 8}
        ]
    },
    {
        "problem_id": "dp-002",
        "title": "House Robber",
        "difficulty": "medium",
        "topic": "dynamic_programming",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 20,
        "tags": ["dynamic_programming"],
        "description": "You cannot rob two adjacent houses. Return the maximum amount you can rob.\n\n**Example:**\n```\nInput: nums = [1, 2, 3, 1]\nOutput: 4\nExplanation: Rob house 1 and 3.\n```",
        "function_name": "rob",
        "starter_code": "def rob(nums: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3, 1]], "expected": 4},
            {"input": [[2, 7, 9, 3, 1]], "expected": 12},
            {"input": [[2, 1, 1, 2]], "expected": 4}
        ]
    },
    {
        "problem_id": "dp-003",
        "title": "Coin Change",
        "difficulty": "medium",
        "topic": "dynamic_programming",
        "expected_complexity": "O(n*amount)",
        "expected_time_minutes": 25,
        "tags": ["dynamic_programming", "bfs"],
        "description": "Find the fewest number of coins to make up the amount. Return -1 if impossible.\n\n**Example:**\n```\nInput: coins = [1, 2, 5], amount = 11\nOutput: 3\nExplanation: 11 = 5 + 5 + 1\n```",
        "function_name": "coin_change",
        "starter_code": "def coin_change(coins: list, amount: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 5], 11], "expected": 3},
            {"input": [[2], 3], "expected": -1},
            {"input": [[1], 0], "expected": 0}
        ]
    },
    {
        "problem_id": "dp-004",
        "title": "Longest Increasing Subsequence",
        "difficulty": "medium",
        "topic": "dynamic_programming",
        "expected_complexity": "O(n log n)",
        "expected_time_minutes": 30,
        "tags": ["dynamic_programming", "binary_search"],
        "description": "Find the length of the longest strictly increasing subsequence.\n\n**Example:**\n```\nInput: nums = [10, 9, 2, 5, 3, 7, 101, 18]\nOutput: 4\nExplanation: [2, 3, 7, 101]\n```",
        "function_name": "length_of_lis",
        "starter_code": "def length_of_lis(nums: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[10, 9, 2, 5, 3, 7, 101, 18]], "expected": 4},
            {"input": [[0, 1, 0, 3, 2, 3]], "expected": 4},
            {"input": [[7, 7, 7, 7, 7]], "expected": 1}
        ]
    },
    {
        "problem_id": "dp-005",
        "title": "Unique Paths",
        "difficulty": "medium",
        "topic": "dynamic_programming",
        "expected_complexity": "O(m*n)",
        "expected_time_minutes": 20,
        "tags": ["dynamic_programming", "math"],
        "description": "A robot is on an m x n grid. It can only move right or down. How many unique paths are there?\n\n**Example:**\n```\nInput: m = 3, n = 7\nOutput: 28\n```",
        "function_name": "unique_paths",
        "starter_code": "def unique_paths(m: int, n: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [3, 7], "expected": 28},
            {"input": [3, 2], "expected": 3},
            {"input": [1, 1], "expected": 1}
        ]
    },
    # Stacks
    {
        "problem_id": "stack-001",
        "title": "Valid Parentheses",
        "difficulty": "easy",
        "topic": "stacks",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 15,
        "tags": ["stacks", "strings"],
        "description": "Given a string with brackets, determine if it's valid.\n\n**Example:**\n```\nInput: s = \"()[]{}\"\nOutput: true\n```",
        "function_name": "is_valid_parentheses",
        "starter_code": "def is_valid_parentheses(s: str) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": ["()[]{}"], "expected": True},
            {"input": ["(]"], "expected": False},
            {"input": ["([])"], "expected": True}
        ]
    },
    {
        "problem_id": "stack-002",
        "title": "Daily Temperatures",
        "difficulty": "medium",
        "topic": "stacks",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 25,
        "tags": ["stacks", "monotonic_stack"],
        "description": "Given temperatures, return the number of days until a warmer temperature.\n\n**Example:**\n```\nInput: temperatures = [73, 74, 75, 71, 69, 72, 76, 73]\nOutput: [1, 1, 4, 2, 1, 1, 0, 0]\n```",
        "function_name": "daily_temperatures",
        "starter_code": "def daily_temperatures(temperatures: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[73, 74, 75, 71, 69, 72, 76, 73]], "expected": [1, 1, 4, 2, 1, 1, 0, 0]},
            {"input": [[30, 40, 50, 60]], "expected": [1, 1, 1, 0]},
            {"input": [[30, 60, 90]], "expected": [1, 1, 0]}
        ]
    },
    # Hashing
    {
        "problem_id": "hash-001",
        "title": "Group Anagrams",
        "difficulty": "medium",
        "topic": "hashing",
        "expected_complexity": "O(n*k log k)",
        "expected_time_minutes": 20,
        "tags": ["hash_map", "strings", "sorting"],
        "description": "Group anagrams together from an array of strings.\n\n**Example:**\n```\nInput: strs = [\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]\nOutput: [[\"bat\"], [\"nat\", \"tan\"], [\"ate\", \"eat\", \"tea\"]]\n```",
        "function_name": "group_anagrams",
        "starter_code": "def group_anagrams(strs: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [["eat", "tea", "tan", "ate", "nat", "bat"]], "expected": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]},
            {"input": [[""]], "expected": [[""]]},
            {"input": [["a"]], "expected": [["a"]]}
        ]
    },
    {
        "problem_id": "hash-002",
        "title": "Top K Frequent Elements",
        "difficulty": "medium",
        "topic": "hashing",
        "expected_complexity": "O(n log k)",
        "expected_time_minutes": 20,
        "tags": ["hash_map", "heap", "bucket_sort"],
        "description": "Given an integer array and k, return the k most frequent elements.\n\n**Example:**\n```\nInput: nums = [1,1,1,2,2,3], k = 2\nOutput: [1, 2]\n```",
        "function_name": "top_k_frequent",
        "starter_code": "def top_k_frequent(nums: list, k: int) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 1, 1, 2, 2, 3], 2], "expected": [1, 2]},
            {"input": [[1], 1], "expected": [1]},
            {"input": [[1, 2], 2], "expected": [1, 2]}
        ]
    },
    # Graphs
    {
        "problem_id": "graph-001",
        "title": "Number of Islands",
        "difficulty": "medium",
        "topic": "graphs",
        "expected_complexity": "O(m*n)",
        "expected_time_minutes": 25,
        "tags": ["graphs", "bfs", "dfs"],
        "description": "Given a 2D grid of '1's (land) and '0's (water), count the number of islands.\n\n**Example:**\n```\nInput: grid = [[1,1,0],[0,1,0],[0,0,1]]\nOutput: 2\n```",
        "function_name": "num_islands",
        "starter_code": "def num_islands(grid: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[[1, 1, 0], [0, 1, 0], [0, 0, 1]]], "expected": 2},
            {"input": [[[1, 1, 1], [1, 1, 1]]], "expected": 1},
            {"input": [[[0, 0], [0, 0]]], "expected": 0}
        ]
    },
    {
        "problem_id": "graph-002",
        "title": "Course Schedule",
        "difficulty": "medium",
        "topic": "graphs",
        "expected_complexity": "O(V+E)",
        "expected_time_minutes": 30,
        "tags": ["graphs", "topological_sort", "dfs"],
        "description": "Given numCourses and prerequisites, determine if you can finish all courses.\n\n**Example:**\n```\nInput: numCourses = 2, prerequisites = [[1,0]]\nOutput: true\n```",
        "function_name": "can_finish",
        "starter_code": "def can_finish(num_courses: int, prerequisites: list) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [2, [[1, 0]]], "expected": True},
            {"input": [2, [[1, 0], [0, 1]]], "expected": False},
            {"input": [3, [[1, 0], [2, 1]]], "expected": True}
        ]
    },
    # Greedy
    {
        "problem_id": "greedy-001",
        "title": "Jump Game",
        "difficulty": "medium",
        "topic": "greedy",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 20,
        "tags": ["greedy", "dynamic_programming"],
        "description": "Given an array where each element represents max jump length, determine if you can reach the last index.\n\n**Example:**\n```\nInput: nums = [2, 3, 1, 1, 4]\nOutput: true\n```",
        "function_name": "can_jump",
        "starter_code": "def can_jump(nums: list) -> bool:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[2, 3, 1, 1, 4]], "expected": True},
            {"input": [[3, 2, 1, 0, 4]], "expected": False},
            {"input": [[0]], "expected": True}
        ]
    },
    {
        "problem_id": "greedy-002",
        "title": "Gas Station",
        "difficulty": "medium",
        "topic": "greedy",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 25,
        "tags": ["greedy"],
        "description": "Find the starting gas station index to complete the circuit, or -1 if impossible.\n\n**Example:**\n```\nInput: gas = [1,2,3,4,5], cost = [3,4,5,1,2]\nOutput: 3\n```",
        "function_name": "can_complete_circuit",
        "starter_code": "def can_complete_circuit(gas: list, cost: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], "expected": 3},
            {"input": [[2, 3, 4], [3, 4, 3]], "expected": -1},
            {"input": [[5, 1, 2, 3, 4], [4, 4, 1, 5, 1]], "expected": 4}
        ]
    },
    # Backtracking
    {
        "problem_id": "bt-001",
        "title": "Subsets",
        "difficulty": "medium",
        "topic": "backtracking",
        "expected_complexity": "O(n * 2^n)",
        "expected_time_minutes": 20,
        "tags": ["backtracking", "bit_manipulation"],
        "description": "Given an integer array of unique elements, return all possible subsets.\n\n**Example:**\n```\nInput: nums = [1, 2, 3]\nOutput: [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]\n```",
        "function_name": "subsets",
        "starter_code": "def subsets(nums: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]},
            {"input": [[0]], "expected": [[], [0]]},
            {"input": [[1, 2]], "expected": [[], [1], [2], [1, 2]]}
        ]
    },
    {
        "problem_id": "bt-002",
        "title": "Permutations",
        "difficulty": "medium",
        "topic": "backtracking",
        "expected_complexity": "O(n!)",
        "expected_time_minutes": 20,
        "tags": ["backtracking"],
        "description": "Given an array of distinct integers, return all possible permutations.\n\n**Example:**\n```\nInput: nums = [1, 2, 3]\nOutput: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]\n```",
        "function_name": "permute",
        "starter_code": "def permute(nums: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]},
            {"input": [[0, 1]], "expected": [[0, 1], [1, 0]]},
            {"input": [[1]], "expected": [[1]]}
        ]
    },
    # Heap
    {
        "problem_id": "heap-001",
        "title": "Kth Largest Element",
        "difficulty": "medium",
        "topic": "heap",
        "expected_complexity": "O(n log k)",
        "expected_time_minutes": 15,
        "tags": ["heap", "quickselect"],
        "description": "Find the kth largest element in an array.\n\n**Example:**\n```\nInput: nums = [3, 2, 1, 5, 6, 4], k = 2\nOutput: 5\n```",
        "function_name": "find_kth_largest",
        "starter_code": "def find_kth_largest(nums: list, k: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[3, 2, 1, 5, 6, 4], 2], "expected": 5},
            {"input": [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], "expected": 4},
            {"input": [[1], 1], "expected": 1}
        ]
    },
    {
        "problem_id": "heap-002",
        "title": "Merge K Sorted Lists",
        "difficulty": "hard",
        "topic": "heap",
        "expected_complexity": "O(n log k)",
        "expected_time_minutes": 30,
        "tags": ["heap", "linked_lists", "divide_and_conquer"],
        "description": "Merge k sorted linked lists (arrays) and return one sorted list.\n\n**Example:**\n```\nInput: lists = [[1, 4, 5], [1, 3, 4], [2, 6]]\nOutput: [1, 1, 2, 3, 4, 4, 5, 6]\n```",
        "function_name": "merge_k_lists",
        "starter_code": "def merge_k_lists(lists: list) -> list:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[[1, 4, 5], [1, 3, 4], [2, 6]]], "expected": [1, 1, 2, 3, 4, 4, 5, 6]},
            {"input": [[]], "expected": []},
            {"input": [[[1]]], "expected": [1]}
        ]
    },
    # Bit Manipulation
    {
        "problem_id": "bit-001",
        "title": "Single Number",
        "difficulty": "easy",
        "topic": "bit_manipulation",
        "expected_complexity": "O(n)",
        "expected_time_minutes": 10,
        "tags": ["bit_manipulation", "xor"],
        "description": "Every element appears twice except for one. Find that single one.\n\n**Example:**\n```\nInput: nums = [4, 1, 2, 1, 2]\nOutput: 4\n```",
        "function_name": "single_number",
        "starter_code": "def single_number(nums: list) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [[2, 2, 1]], "expected": 1},
            {"input": [[4, 1, 2, 1, 2]], "expected": 4},
            {"input": [[1]], "expected": 1}
        ]
    },
    {
        "problem_id": "bit-002",
        "title": "Number of 1 Bits",
        "difficulty": "easy",
        "topic": "bit_manipulation",
        "expected_complexity": "O(1)",
        "expected_time_minutes": 10,
        "tags": ["bit_manipulation"],
        "description": "Count the number of '1' bits in an integer (Hamming weight).\n\n**Example:**\n```\nInput: n = 11\nOutput: 3\nExplanation: 11 in binary is 1011.\n```",
        "function_name": "hamming_weight",
        "starter_code": "def hamming_weight(n: int) -> int:\n    # Write your code here\n    pass",
        "test_cases": [
            {"input": [11], "expected": 3},
            {"input": [128], "expected": 1},
            {"input": [255], "expected": 8}
        ]
    }
]

# Save to file
with open(r'c:\Users\Administrator\Desktop\final-year-project\data\problems.json', 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2, ensure_ascii=False)

print(f"Saved {len(problems)} problems to problems.json")
