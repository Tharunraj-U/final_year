"""Full test of AI Service with Ollama."""
from app.services.ai_service import AIService
import json

print("Testing AI Service with Ollama (qwen2.5-coder:3b)...")
print("=" * 50)

ai = AIService()

# Test problem
test_problem = {
    "title": "Two Sum",
    "difficulty": "easy",
    "topic": "arrays",
    "description": "Find two numbers that add up to target",
    "expected_complexity": "O(n)",
    "tags": ["arrays", "hash-map"]
}

test_code = """def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []"""

test_result = {"passed": True, "passed_count": 3, "total_count": 3, "test_results": []}

print("Calling AI for code analysis...")
print("(This may take 30-60 seconds with local LLM)")
print()

result = ai.analyze_submission(test_problem, test_code, test_result, [], 1, "python")

print("AI Analysis Result:")
print("-" * 30)
print(f"Feedback: {result.get('feedback', 'N/A')[:300]}")
print()
print(f"Time Complexity: {result.get('time_complexity', {})}")
print(f"Space Complexity: {result.get('space_complexity', {})}")
print(f"Algorithm Type: {result.get('algorithm_type', {}).get('primary', 'N/A')}")
print(f"Score: {result.get('score', 'N/A')}")
print(f"Mastery Level: {result.get('mastery_level', 'N/A')}")
print()

if result.get("ai_unavailable"):
    print("⚠️ AI analysis unavailable - using fallback")
else:
    print("✅ AI analysis successful!")
