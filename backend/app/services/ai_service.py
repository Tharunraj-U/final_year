"""
OpenAI GPT-powered AI service for analyzing submissions and recommending problems.
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIService:
    """
    Uses OpenAI GPT to analyze user's coding performance and recommend problems.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
    
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
{{
    "feedback": "Detailed constructive feedback about the solution (3-4 sentences, be specific about what's good and what can improve)",
    "time_complexity": {{
        "estimate": "O(?) - the time complexity of their solution",
        "explanation": "Brief explanation of why this is the time complexity",
        "is_optimal": true/false
    }},
    "space_complexity": {{
        "estimate": "O(?) - the space complexity of their solution",
        "explanation": "Brief explanation of space usage",
        "is_optimal": true/false
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1200
            )
            
            result = response.choices[0].message.content.strip()
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
