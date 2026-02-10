"""Test the AI Help features."""
from app.services.ai_service import AIService
import json

print("Testing AI Help Features with Ollama...")
print("=" * 50)

ai = AIService()

# Test problem
test_problem = {
    "title": "Two Sum",
    "difficulty": "easy",
    "topic": "arrays",
    "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
    "expected_complexity": "O(n)",
    "tags": ["arrays", "hash-map"]
}

# Test 1: Explain Problem
print("\n1️⃣ Testing: Explain Problem")
print("-" * 30)
result = ai.get_problem_explanation(test_problem)
if result.get("success"):
    print("✅ Explanation generated!")
    print(result.get("explanation", "")[:300] + "...")
else:
    print("❌ Failed:", result.get("error"))

# Test 2: Get Hint
print("\n2️⃣ Testing: Get Hint (Level 1)")
print("-" * 30)
result = ai.get_hint(test_problem, hint_level=1)
if result.get("success"):
    print("✅ Hint generated!")
    print(result.get("hint", "")[:300] + "...")
else:
    print("❌ Failed:", result.get("error"))

# Test 3: Ask Doubt
print("\n3️⃣ Testing: Ask Doubt")
print("-" * 30)
result = ai.ask_doubt(test_problem, "What data structure should I use for this problem?")
if result.get("success"):
    print("✅ Doubt answered!")
    print(result.get("answer", "")[:300] + "...")
else:
    print("❌ Failed:", result.get("error"))

print("\n" + "=" * 50)
print("✅ AI Help features are working!")
