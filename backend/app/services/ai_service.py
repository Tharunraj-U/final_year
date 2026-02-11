"""
AI service for analyzing submissions and recommending problems.
Supports both OpenAI API and local LLMs (Ollama, LM Studio, etc.)
"""

import os
import json
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration - set USE_OPENAI in your .env file
# USE_OPENAI=true  -> Uses OpenAI API
# USE_OPENAI=false -> Uses local Ollama (FREE)

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
OLLAMA_URL = "http://localhost:11434/api/chat"


class AIService:
    """
    Uses either OpenAI GPT or local Ollama to analyze user's coding performance and recommend problems.
    Set USE_OPENAI=true in .env for OpenAI, or USE_OPENAI=false for local Ollama.
    """
    
    def __init__(self):
        self.use_openai = USE_OPENAI
        
        if self.use_openai:
            # Use OpenAI API
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = OPENAI_MODEL
                print(f"🤖 Using OpenAI: {self.model}")
            except ImportError:
                print("⚠️ OpenAI package not installed. Falling back to Ollama.")
                self.use_openai = False
                self.model = OLLAMA_MODEL
                print(f"🤖 Using Ollama: {self.model}")
        else:
            # Use local Ollama (FREE)
            self.model = OLLAMA_MODEL
            print(f"🤖 Using Ollama: {self.model} (FREE - no API key needed)")
    
    def _call_llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        Call the configured LLM (OpenAI or Ollama) and return the response text.
        """
        if self.use_openai:
            return self._call_openai(prompt, temperature, max_tokens)
        else:
            return self._call_ollama(prompt, temperature, max_tokens)
    
    def _call_ollama(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """
        Call Ollama local LLM via HTTP API.
        Make sure Ollama is running: ollama serve
        """
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            response = requests.post(OLLAMA_URL, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to Ollama. Is it running? Start with: ollama serve")
            raise Exception("Ollama not available. Run 'ollama serve' first.")
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            raise
    
    def _call_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    
    def analyze_submission(
        self,
        problem: Dict,
        user_code: str,
        execution_result: Dict,
        submission_history: List[Dict],
        attempt_count: int = 1,
        language: str = "python"
    ) -> Dict:
        """
        Analyze a user's submission with detailed metrics including:
        - Time complexity
        - Space complexity
        - Algorithm type (brute force, sliding window, etc.)
        - Test case analysis
        """
        # Get failed test details
        failed_tests = []
        test_results = execution_result.get('test_results', [])
        for test in test_results:
            if not test.get('passed'):
                failed_tests.append({
                    'test_number': test.get('test_number'),
                    'input': test.get('input'),
                    'expected': test.get('expected'),
                    'actual': test.get('actual'),
                    'error': test.get('error')
                })
        
        prompt = f"""You are an expert AI coding tutor performing deep analysis of a student's code submission.

PROBLEM DETAILS:
- Title: {problem.get('title')}
- Difficulty: {problem.get('difficulty')}
- Topic: {problem.get('topic')}
- Description: {problem.get('description')}
- Expected Optimal Complexity: {problem.get('expected_complexity')}
- Tags: {problem.get('tags', [])}

USER'S CODE ({language}):
```{language}
{user_code}
```

EXECUTION RESULTS:
- All Tests Passed: {execution_result.get('passed', False)}
- Tests Passed: {execution_result.get('passed_count', 0)} / {execution_result.get('total_count', 0)}
- Attempt Number: {attempt_count}
- Error Message: {execution_result.get('error', 'None')}

FAILED TEST CASES:
{json.dumps(failed_tests, indent=2) if failed_tests else 'No failed tests'}

STUDENT'S HISTORY (last 5 submissions):
{json.dumps(submission_history[-5:], indent=2) if submission_history else 'First submission'}

Perform a COMPREHENSIVE analysis and respond in STRICT JSON format:

CRITICAL COMPLEXITY ANALYSIS RULES:
1. Analyze ONLY the code that ACTUALLY EXECUTES, not helper functions that are defined but never called
2. Trace the execution flow from the main function - what code paths are actually run?
3. If a recursive function is defined but never called, it contributes O(0) to complexity
4. A simple loop "for x in collection" is O(n) where n = len(collection)
5. O(1) means CONSTANT time regardless of input size (only single operations, no loops over input)
6. Nested loops are O(n^2), O(n*m), etc.
7. ACTUAL recursion with branching factor b and depth d is O(b^d) - but only if recursion is actually invoked!
8. **HARDCODED / STUB CODE IS O(1) TIME AND O(1) SPACE**: If the code just returns a fixed value, a hardcoded literal, or doesn't process the input at all (e.g., `return [0,1]`, `return new int[]{0,1}`, `return null`, `return 0`), the complexity is O(1) for both time and space. Do NOT report the expected/optimal complexity — report what the code ACTUALLY does.
9. If the code does NOT iterate over, recurse on, or process the input data in any meaningful way, it is O(1).
10. If most test cases FAIL, the code is likely not implementing the correct algorithm — do NOT assume it uses the expected optimal approach.

EXAMPLE: If code defines def dfs() but the return statement uses "for d in digits: result *= mapping[d]", 
the actual complexity is O(n) from the loop, NOT from the unused DFS function.

EXAMPLE: If code is `return new int[]{0,1}` or `return [0, 1]`, the time complexity is O(1) and space complexity is O(1) because no computation happens.

*** CRITICAL is_optimal DETERMINATION RULES ***
The expected complexity for this problem is: {problem.get('expected_complexity')}
Complexity hierarchy (BEST to WORST): O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(n^3) < O(2^n) < O(3^n) < O(4^n) < O(n!)

RULE: is_optimal = TRUE if user's complexity is BETTER THAN OR EQUAL TO expected complexity.
- O(n) vs expected O(4^n) => O(n) is MUCH BETTER => is_optimal = TRUE
- O(n) vs expected O(n) => EQUAL => is_optimal = TRUE  
- O(n^2) vs expected O(n) => WORSE => is_optimal = FALSE

DO NOT mark is_optimal=false just because the user didn't use the "expected algorithm".
If the user found a more efficient approach, that's BETTER and is_optimal should be TRUE!

{{
    "feedback": "Detailed constructive feedback about the solution (3-4 sentences, be specific about what's good and what can improve)",
    "time_complexity": {{
        "estimate": "O(?)",
        "explanation": "Trace execution: what loops/recursions actually run?",
        "is_optimal": true/false (MUST be true if user's O(n) <= expected {problem.get('expected_complexity')})
    }},
    "space_complexity": {{
        "estimate": "O(?)",
        "explanation": "What memory is actually allocated during execution?",
        "is_optimal": true/false (true if user's complexity <= expected complexity)
    }},
    "algorithm_type": {{
        "primary": "The main algorithm/technique used (e.g., 'Brute Force', 'Two Pointers', 'Sliding Window', 'Dynamic Programming', 'Hash Map', 'Binary Search', 'Recursion', 'Greedy', 'BFS/DFS', etc.)",
        "secondary": ["Any additional techniques used"],
        "is_appropriate": true/false,
        "better_approach": "If there's a better approach, describe it briefly, otherwise null"
    }},
    "test_case_analysis": {{
        "total_tests": {execution_result.get('total_count', 0)},
        "passed_tests": {execution_result.get('passed_count', 0)},
        "failed_tests": {len(failed_tests)},
        "failure_patterns": ["List patterns in failures, e.g., 'edge cases', 'empty input', 'large numbers', 'negative values'"],
        "failure_reasons": ["Specific reasons why tests failed"]
    }},
    "code_quality": {{
        "readability": 1-10,
        "variable_naming": 1-10,
        "code_structure": 1-10,
        "comments": "Needs more comments / Adequate / Well commented"
    }},
    "improvement_tips": [
        "Specific actionable tip 1",
        "Specific actionable tip 2",
        "Specific actionable tip 3"
    ],
    "concepts_demonstrated": ["List of CS concepts the student showed understanding of"],
    "concepts_to_learn": ["Concepts the student should focus on learning"],
    "score": 0-100,
    "mastery_level": "Beginner / Developing / Proficient / Expert"
}}

Respond ONLY with valid JSON, no other text."""

        try:
            result = self._call_llm(prompt, temperature=0.3, max_tokens=1000)
            
            # Parse JSON from response
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            
            analysis = json.loads(result)
            
            # Add metadata
            analysis['attempt_number'] = attempt_count
            analysis['language'] = language
            
            return analysis
        except Exception as e:
            print(f"AI analysis error: {e}")
            import traceback
            traceback.print_exc()
            
            # Generate meaningful fallback based on execution results
            passed = execution_result.get('passed', False)
            passed_count = execution_result.get('passed_count', 0)
            total_count = execution_result.get('total_count', 0)
            
            if passed:
                feedback = f"Great job! Your solution passed all {total_count} test cases. Keep practicing to improve your skills!"
                score = 80
                mastery = "Proficient"
            elif passed_count > 0:
                feedback = f"Good effort! You passed {passed_count}/{total_count} tests. Review the failed cases and try again."
                score = int((passed_count / total_count) * 70) if total_count > 0 else 30
                mastery = "Developing"
            else:
                feedback = "Your solution didn't pass the tests. Check your logic and edge cases, then try again!"
                score = 20
                mastery = "Beginner"
            
            return {
                "feedback": feedback,
                "time_complexity": {"estimate": "Analysis unavailable", "explanation": "AI analysis temporarily unavailable", "is_optimal": False},
                "space_complexity": {"estimate": "Analysis unavailable", "explanation": "AI analysis temporarily unavailable", "is_optimal": False},
                "algorithm_type": {"primary": "To be analyzed", "secondary": [], "is_appropriate": passed, "better_approach": None},
                "test_case_analysis": {
                    "total_tests": total_count,
                    "passed_tests": passed_count,
                    "failed_tests": len(failed_tests),
                    "failure_patterns": ["Review edge cases"] if not passed else [],
                    "failure_reasons": ["Check your implementation logic"] if not passed else []
                },
                "code_quality": {"readability": 7, "variable_naming": 7, "code_structure": 7, "comments": "Could use more comments"},
                "improvement_tips": [
                    "Test with edge cases (empty arrays, single elements)",
                    "Consider time and space complexity",
                    "Add comments to explain your logic"
                ] if not passed else ["Great work! Try more challenging problems"],
                "concepts_demonstrated": [problem.get('topic', 'programming')],
                "concepts_to_learn": ["algorithm optimization"] if not passed else [],
                "score": score,
                "mastery_level": mastery,
                "attempt_number": attempt_count,
                "language": language,
                "ai_unavailable": True
            }
    
    def get_recommendations(
        self,
        submission_history: List[Dict],
        available_problems: List[Dict],
        solved_problem_ids: List[str]
    ) -> Dict:
        """
        Get AI-powered problem recommendations based on comprehensive user analysis.
        Uses all available metrics: complexity analysis, algorithm types, test failures, etc.
        """
        # Filter out solved problems
        unsolved = [p for p in available_problems if p['problem_id'] not in solved_problem_ids]
        
        if not unsolved:
            return {
                'recommended_problems': [],
                'learning_path': 'Congratulations! You have solved all available problems.',
                'strengths': [],
                'weaknesses': [],
                'next_steps': []
            }
        
        # Build comprehensive history analysis
        history_analysis = self._analyze_history_deeply(submission_history)
        
        prompt = f"""You are an expert AI coding tutor creating a personalized learning path.

COMPREHENSIVE STUDENT ANALYSIS:
{json.dumps(history_analysis, indent=2)}

AVAILABLE UNSOLVED PROBLEMS:
{json.dumps([{
    'problem_id': p['problem_id'],
    'title': p['title'],
    'difficulty': p['difficulty'],
    'topic': p['topic'],
    'expected_complexity': p['expected_complexity'],
    'tags': p.get('tags', [])
} for p in unsolved[:25]], indent=2)}

Based on the student's COMPLETE performance profile, create a personalized learning plan.

ANALYSIS FACTORS TO CONSIDER:
1. Algorithm types they struggle with (e.g., if they use brute force when optimal solutions exist)
2. Complexity patterns (are their solutions often suboptimal?)
3. Test case failure patterns (edge cases? empty inputs? large inputs?)
4. Number of attempts per problem (struggling = more attempts)
5. Topics with low success rates
6. Time taken vs expected time
7. Progressive skill building

Respond in STRICT JSON format:
{{
    "recommendations": [
        {{
            "problem_id": "exact problem_id from available problems",
            "reason": "Specific reason why this problem is recommended based on their history",
            "expected_learning": "What the student will learn from this problem",
            "difficulty_justification": "Why this difficulty level is appropriate right now"
        }}
    ],
    "learning_path": {{
        "current_level": "Beginner/Intermediate/Advanced based on their performance",
        "focus_areas": ["List of 2-3 specific areas to focus on"],
        "description": "2-3 sentence personalized learning path description"
    }},
    "strengths": {{
        "topics": ["Strong topics"],
        "algorithms": ["Algorithm types they use well"],
        "patterns": ["Good patterns in their code"]
    }},
    "weaknesses": {{
        "topics": ["Weak topics"],
        "algorithms": ["Algorithm types to practice"],
        "patterns": ["Patterns causing failures"]
    }},
    "next_steps": [
        "Specific actionable step 1",
        "Specific actionable step 2",
        "Specific actionable step 3"
    ],
    "estimated_time_to_next_level": "Estimate like '5-10 more problems' or '2-3 weeks of practice'"
}}

Respond ONLY with valid JSON, no other text."""

        try:
            result = self._call_llm(prompt, temperature=0.4, max_tokens=1200)
            
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            
            data = json.loads(result)
            
            # Enrich recommendations with full problem data
            enriched = []
            for rec in data.get('recommendations', []):
                problem = next(
                    (p for p in unsolved if p['problem_id'] == rec['problem_id']),
                    None
                )
                if problem:
                    enriched.append({
                        **problem,
                        'reason': rec['reason']
                    })
            
            return {
                'recommended_problems': enriched,
                'learning_path': data.get('learning_path', {}),
                'strengths': data.get('strengths', {}),
                'weaknesses': data.get('weaknesses', {}),
                'next_steps': data.get('next_steps', []),
                'estimated_time_to_next_level': data.get('estimated_time_to_next_level', '')
            }
        except Exception as e:
            print(f"AI recommendation error: {e}")
            # Fallback to simple recommendations
            return {
                'recommended_problems': unsolved[:3],
                'learning_path': {'description': 'Continue practicing to unlock AI-powered recommendations.'},
                'strengths': {},
                'weaknesses': {},
                'next_steps': ['Keep practicing!'],
                'estimated_time_to_next_level': 'Unknown'
            }
    
    def _analyze_history_deeply(self, history: List[Dict]) -> Dict:
        """Create comprehensive analysis of user's submission history."""
        if not history:
            return {
                "status": "new_user",
                "message": "No submission history yet. This is the student's first session."
            }
        
        total_submissions = len(history)
        solved_problems = set()
        failed_problems = set()
        
        # Metrics
        topic_stats = {}
        difficulty_stats = {'easy': {'attempts': 0, 'solved': 0}, 
                           'medium': {'attempts': 0, 'solved': 0}, 
                           'hard': {'attempts': 0, 'solved': 0}}
        algorithm_usage = {}
        complexity_analysis = {'optimal': 0, 'suboptimal': 0}
        test_failure_patterns = []
        attempt_counts = {}  # problem_id -> attempt count
        time_analysis = {'total_time': 0, 'problems_with_time': 0}
        scores = []
        
        for h in history:
            problem_id = h.get('problem_id', '')
            topic = h.get('topic', 'unknown')
            difficulty = h.get('difficulty', 'easy')
            passed = h.get('passed', False)
            
            # Track attempts per problem
            attempt_counts[problem_id] = attempt_counts.get(problem_id, 0) + 1
            
            # Track solved/failed
            if passed:
                solved_problems.add(problem_id)
            else:
                failed_problems.add(problem_id)
            
            # Topic stats
            if topic not in topic_stats:
                topic_stats[topic] = {'attempts': 0, 'solved': 0, 'total_score': 0, 'algorithms_used': []}
            topic_stats[topic]['attempts'] += 1
            if passed:
                topic_stats[topic]['solved'] += 1
            topic_stats[topic]['total_score'] += h.get('score', 0)
            
            # Difficulty stats
            if difficulty in difficulty_stats:
                difficulty_stats[difficulty]['attempts'] += 1
                if passed:
                    difficulty_stats[difficulty]['solved'] += 1
            
            # Algorithm analysis (from AI analysis if available)
            ai_analysis = h.get('ai_analysis', {})
            if ai_analysis:
                algo_type = ai_analysis.get('algorithm_type', {})
                if isinstance(algo_type, dict):
                    primary = algo_type.get('primary', 'Unknown')
                    algorithm_usage[primary] = algorithm_usage.get(primary, 0) + 1
                    
                    # Track if solution was optimal
                    time_comp = ai_analysis.get('time_complexity', {})
                    if isinstance(time_comp, dict) and time_comp.get('is_optimal'):
                        complexity_analysis['optimal'] += 1
                    else:
                        complexity_analysis['suboptimal'] += 1
                
                # Collect failure patterns
                test_analysis = ai_analysis.get('test_case_analysis', {})
                if isinstance(test_analysis, dict):
                    patterns = test_analysis.get('failure_patterns', [])
                    test_failure_patterns.extend(patterns)
            
            # Time analysis
            time_taken = h.get('time_taken_minutes', 0)
            if time_taken > 0:
                time_analysis['total_time'] += time_taken
                time_analysis['problems_with_time'] += 1
            
            # Scores
            score = h.get('score', 0)
            if score > 0:
                scores.append(score)
        
        # Calculate derived metrics
        avg_score = sum(scores) / len(scores) if scores else 0
        avg_time = time_analysis['total_time'] / time_analysis['problems_with_time'] if time_analysis['problems_with_time'] > 0 else 0
        
        # Problems that took multiple attempts
        struggled_problems = [pid for pid, count in attempt_counts.items() if count > 2]
        
        # Topic success rates
        for topic in topic_stats:
            attempts = topic_stats[topic]['attempts']
            solved = topic_stats[topic]['solved']
            topic_stats[topic]['success_rate'] = (solved / attempts * 100) if attempts > 0 else 0
            topic_stats[topic]['avg_score'] = topic_stats[topic]['total_score'] / attempts if attempts > 0 else 0
        
        # Find weak and strong topics
        weak_topics = [t for t, s in topic_stats.items() if s['success_rate'] < 50]
        strong_topics = [t for t, s in topic_stats.items() if s['success_rate'] >= 70]
        
        # Most common failure patterns
        failure_pattern_counts = {}
        for p in test_failure_patterns:
            failure_pattern_counts[p] = failure_pattern_counts.get(p, 0) + 1
        common_failure_patterns = sorted(failure_pattern_counts.items(), key=lambda x: -x[1])[:5]
        
        return {
            "summary": {
                "total_submissions": total_submissions,
                "unique_problems_attempted": len(attempt_counts),
                "problems_solved": len(solved_problems),
                "success_rate": len(solved_problems) / len(attempt_counts) * 100 if attempt_counts else 0,
                "average_score": round(avg_score, 1),
                "average_time_minutes": round(avg_time, 1)
            },
            "attempts_analysis": {
                "average_attempts_per_problem": round(total_submissions / len(attempt_counts), 1) if attempt_counts else 0,
                "problems_with_multiple_attempts": len(struggled_problems),
                "struggled_problems": struggled_problems[:5]
            },
            "topic_performance": topic_stats,
            "difficulty_performance": difficulty_stats,
            "algorithm_usage": algorithm_usage,
            "complexity_analysis": {
                "optimal_solutions_percentage": round(complexity_analysis['optimal'] / total_submissions * 100, 1) if total_submissions > 0 else 0,
                "needs_optimization": complexity_analysis['suboptimal'] > complexity_analysis['optimal']
            },
            "test_failure_patterns": {
                "common_patterns": [p[0] for p in common_failure_patterns],
                "pattern_counts": dict(common_failure_patterns)
            },
            "skill_assessment": {
                "weak_topics": weak_topics,
                "strong_topics": strong_topics,
                "recommended_focus": weak_topics[:3] if weak_topics else ['Try harder problems']
            }
        }
    
    def _summarize_history(self, history: List[Dict]) -> str:
        """Create a summary of user's submission history."""
        if not history:
            return "No submission history yet. New user."
        
        total = len(history)
        solved = sum(1 for h in history if h.get('passed', False))
        
        topics = {}
        difficulties = {'easy': 0, 'medium': 0, 'hard': 0}
        avg_score = 0
        
        for h in history:
            topic = h.get('topic', 'unknown')
            topics[topic] = topics.get(topic, {'attempts': 0, 'solved': 0})
            topics[topic]['attempts'] += 1
            if h.get('passed'):
                topics[topic]['solved'] += 1
            
            diff = h.get('difficulty', 'easy')
            if diff in difficulties:
                difficulties[diff] += 1
            
            avg_score += h.get('score', 0)
        
        avg_score = avg_score / total if total > 0 else 0
        
        return f"""
Total Submissions: {total}
Problems Solved: {solved} ({(solved/total*100):.0f}% success rate)
Average Score: {avg_score:.0f}/100
Difficulty Distribution: Easy={difficulties['easy']}, Medium={difficulties['medium']}, Hard={difficulties['hard']}
Topic Performance: {json.dumps(topics)}
"""

    # ==================== AI HELP / TUTOR METHODS ====================
    
    def get_problem_explanation(self, problem: Dict) -> Dict:
        """
        Explain the problem in simple terms, what it's asking, and key concepts.
        """
        prompt = f"""You are a friendly coding tutor helping a student understand a problem.

PROBLEM:
Title: {problem.get('title')}
Difficulty: {problem.get('difficulty')}
Topic: {problem.get('topic')}
Description: {problem.get('description')}
Expected Complexity: {problem.get('expected_complexity')}

Please explain this problem in a simple, beginner-friendly way:
1. What is the problem asking? (in simple terms)
2. What are the inputs and expected outputs?
3. Give a simple example with step-by-step walkthrough
4. What key concepts/data structures should the student know?

Be encouraging and supportive. Use simple language. Format with markdown."""

        try:
            result = self._call_llm(prompt, temperature=0.5, max_tokens=800)
            return {
                "success": True,
                "explanation": result,
                "type": "explanation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "explanation": "Sorry, I couldn't generate an explanation right now. Please try again."
            }
    
    def get_hint(self, problem: Dict, hint_level: int = 1, user_code: str = "") -> Dict:
        """
        Give progressive hints (level 1 = gentle, level 3 = almost solution).
        """
        hint_descriptions = {
            1: "Give a very gentle hint - just point them in the right direction without giving away the approach",
            2: "Give a medium hint - suggest the algorithm/approach to use but don't give code",
            3: "Give a strong hint - explain the solution approach step by step, but let them write the code"
        }
        
        hint_instruction = hint_descriptions.get(hint_level, hint_descriptions[1])
        
        code_context = ""
        if user_code and len(user_code.strip()) > 20:
            code_context = f"""
The student has written this code so far:
```
{user_code}
```
Take their current approach into account when giving hints.
"""

        prompt = f"""You are a supportive coding tutor giving hints to a student.

PROBLEM:
Title: {problem.get('title')}
Difficulty: {problem.get('difficulty')}  
Topic: {problem.get('topic')}
Description: {problem.get('description')}
Expected Complexity: {problem.get('expected_complexity')}
{code_context}

HINT LEVEL: {hint_level}/3
{hint_instruction}

Important:
- Do NOT give the complete solution code
- Be encouraging and supportive
- Use simple language
- If they're on the right track, encourage them
- Format with markdown"""

        try:
            result = self._call_llm(prompt, temperature=0.6, max_tokens=500)
            return {
                "success": True,
                "hint": result,
                "level": hint_level,
                "type": "hint"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "hint": "Sorry, I couldn't generate a hint right now. Please try again."
            }
    
    def get_solution_approach(self, problem: Dict) -> Dict:
        """
        Explain the optimal solution approach without giving full code.
        """
        prompt = f"""You are a coding tutor explaining how to solve a problem.

PROBLEM:
Title: {problem.get('title')}
Difficulty: {problem.get('difficulty')}
Topic: {problem.get('topic')}
Description: {problem.get('description')}
Expected Complexity: {problem.get('expected_complexity')}

Explain the OPTIMAL solution approach:
1. 🧠 **Intuition**: What's the key insight to solve this?
2. 📝 **Algorithm**: Step-by-step approach (in plain English)
3. ⚡ **Why it's optimal**: Explain the time/space complexity
4. 🎯 **Key points to remember**: Common mistakes to avoid

Do NOT provide the complete code solution. Let the student implement it themselves.
Use markdown formatting."""

        try:
            result = self._call_llm(prompt, temperature=0.4, max_tokens=700)
            return {
                "success": True,
                "approach": result,
                "type": "approach"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "approach": "Sorry, I couldn't generate the approach right now."
            }
    
    def ask_doubt(self, problem: Dict, question: str, user_code: str = "") -> Dict:
        """
        Answer a specific doubt/question from the student about the problem or their code.
        """
        code_context = ""
        if user_code and len(user_code.strip()) > 10:
            code_context = f"""
Student's current code:
```
{user_code}
```
"""

        prompt = f"""You are a helpful coding tutor. A student is working on a problem and has a question.

PROBLEM:
Title: {problem.get('title')}
Topic: {problem.get('topic')}
Description: {problem.get('description')}
{code_context}

STUDENT'S QUESTION:
{question}

Please answer their question:
- Be helpful and encouraging
- If they're confused about a concept, explain it simply
- If they have a bug, help them find it (don't just give the fix)
- If they're stuck, guide them step by step
- Use simple language and examples
- Format with markdown

IMPORTANT: Guide them to the answer, don't just give them the solution code."""

        try:
            result = self._call_llm(prompt, temperature=0.5, max_tokens=600)
            return {
                "success": True,
                "answer": result,
                "type": "doubt"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "Sorry, I couldn't answer your question right now. Please try again."
            }
    
    def debug_code(self, problem: Dict, user_code: str, error_message: str = "") -> Dict:
        """
        Help debug the student's code.
        """
        error_context = ""
        if error_message:
            error_context = f"Error message: {error_message}"

        prompt = f"""You are a coding tutor helping a student debug their code.

PROBLEM:
Title: {problem.get('title')}
Description: {problem.get('description')}

STUDENT'S CODE:
```
{user_code}
```
{error_context}

Help the student find and fix the bug:
1. 🔍 **Issue Found**: What's wrong with the code?
2. 💡 **Why it happens**: Explain why this causes a problem
3. 🛠️ **How to fix**: Guide them to fix it (don't just give corrected code)
4. ✅ **Prevention tip**: How to avoid this mistake in future

Be supportive - bugs are normal! Use markdown formatting."""

        try:
            result = self._call_llm(prompt, temperature=0.4, max_tokens=600)
            return {
                "success": True,
                "debug_help": result,
                "type": "debug"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "debug_help": "Sorry, I couldn't analyze your code right now."
            }
