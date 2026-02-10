# AI Recommendation System Documentation

## Overview

The CodeMaster AI platform uses a sophisticated multi-layer recommendation system that combines **rule-based algorithms** with **Large Language Model (LLM) intelligence** to provide personalized problem recommendations for each user.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI RECOMMENDATION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│  │    User      │    │  Submission  │    │      Problem Bank            │  │
│  │   Profile    │───▶│   History    │───▶│   (Available Problems)       │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────────┘  │
│         │                   │                         │                     │
│         ▼                   ▼                         ▼                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     PERFORMANCE ANALYZER                              │  │
│  │  • Topic breakdown    • Strength/weakness detection                   │  │
│  │  • Skill level        • Algorithm usage patterns                      │  │
│  │  • Efficiency rating  • Test failure patterns                         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│                                ▼                                            │
│         ┌─────────────────────────────────────────────────┐                │
│         │                DUAL RECOMMENDATION              │                │
│         │                    ENGINES                      │                │
│         └─────────────────────────────────────────────────┘                │
│                    │                        │                              │
│                    ▼                        ▼                              │
│  ┌──────────────────────────┐  ┌─────────────────────────────────────┐    │
│  │    RULE-BASED ENGINE     │  │        AI/LLM ENGINE                │    │
│  │    (RecommendationEngine)│  │        (AIService)                  │    │
│  │                          │  │                                     │    │
│  │  • Weakness priority 60% │  │  ┌───────────┐  ┌───────────────┐  │    │
│  │  • Progression 40%       │  │  │  Ollama   │  │   OpenAI      │  │    │
│  │  • New topic exploration │  │  │  (Local)  │  │   (GPT-4)     │  │    │
│  │  • Mastery thresholds    │  │  │   FREE    │  │   API-based   │  │    │
│  │                          │  │  └───────────┘  └───────────────┘  │    │
│  └──────────────────────────┘  └─────────────────────────────────────┘    │
│                    │                        │                              │
│                    └────────────┬───────────┘                              │
│                                 ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    PERSONALIZED RECOMMENDATIONS                       │  │
│  │  • Recommended problems with reasons                                  │  │
│  │  • Learning path description                                          │  │
│  │  • Strengths & weaknesses analysis                                    │  │
│  │  • Next steps & estimated progress                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. Performance Analyzer (`analyzer.py`)

The analyzer processes user submissions to create a comprehensive performance profile.

#### Key Metrics Calculated:

| Metric | Description | Weight |
|--------|-------------|--------|
| **Overall Score** | Weighted average of all submission scores | - |
| **Skill Level** | beginner/intermediate/advanced based on score | - |
| **Topic Breakdown** | Per-topic accuracy, score, and difficulty distribution | - |
| **Efficiency Rating** | How optimal are the solutions | - |
| **Brute Force Count** | Number of non-optimal solutions | - |

#### Topic Performance Analysis:
```
For each topic:
├── problems_attempted
├── problems_solved
├── accuracy (solved/attempted)
├── average_score
├── avg_complexity_score
└── difficulty_distribution {easy, medium, hard}
```

### 2. Scorer (`scorer.py`)

Calculates individual submission and overall performance scores.

#### Score Formula:
```
Performance Score = w₁(Correctness) + w₂(Efficiency) + w₃(Speed) + w₄(Attempts)

Where:
  w₁ = 0.35 (Correctness weight)
  w₂ = 0.30 (Efficiency weight)
  w₃ = 0.20 (Speed weight)
  w₄ = 0.15 (Attempts weight)
```

#### Component Calculations:

**1. Correctness Score:**
```python
correctness = 1.0 if solved else 0.0
```

**2. Efficiency Score (Complexity Comparison):**
```
Complexity Hierarchy (Best → Worst):
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(n² log n) < O(n³) < O(2ⁿ) < O(n!)

Scoring:
  - Exact match or better: 1.0
  - 1 level worse: 0.8
  - 2 levels worse: 0.5
  - 3 levels worse: 0.3
  - 4+ levels worse: 0.1
```

**3. Speed Score:**
```python
Expected time limits:
  - Easy: 15 minutes
  - Medium: 30 minutes
  - Hard: 45 minutes

Score calculation:
  - ≤ 50% of expected: 1.0 (excellent)
  - ≤ 100% of expected: 0.8-1.0
  - ≤ 200% of expected: 0.5-0.8
  - > 200% of expected: 0.1-0.5
```

**4. Attempts Score:**
```python
  - 1 attempt: 1.0
  - 2 attempts: 0.9
  - 3 attempts: 0.7
  - 4 attempts: 0.5
  - 5+ attempts: 0.3
```

### 3. Rule-Based Recommendation Engine (`recommender.py`)

Uses algorithmic rules to select problems based on performance analysis.

#### Strategy Distribution:
```
┌────────────────────────────────────────────────────┐
│           RECOMMENDATION STRATEGY                   │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌─────────────────────┐  Priority: 60%           │
│  │  WEAKNESS-BASED     │                          │
│  │  • Target weak topics                          │
│  │  • Match appropriate difficulty                │
│  │  • Max 2 problems per weak topic               │
│  └─────────────────────┘                          │
│                                                    │
│  ┌─────────────────────┐  Priority: 40%           │
│  │  PROGRESSION-BASED  │                          │
│  │  • Advance in strong topics                    │
│  │  • Move to next difficulty level               │
│  │  • Requires 70% accuracy & score               │
│  └─────────────────────┘                          │
│                                                    │
│  ┌─────────────────────┐  Fallback                │
│  │  EXPLORATION        │                          │
│  │  • Try new topics                              │
│  │  • Start with easy problems                    │
│  │  • Balance coverage                            │
│  └─────────────────────┘                          │
│                                                    │
└────────────────────────────────────────────────────┘
```

#### Difficulty Progression Rules:
```python
# To progress from one difficulty to the next:

MASTERY_THRESHOLDS = {
    "easy": {
        "min_solved": 5,      # Solve at least 5 easy problems
        "min_accuracy": 0.80, # With 80% accuracy
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
```

### 4. AI/LLM Service (`ai_service.py`)

Provides intelligent recommendations using Large Language Models.

---

## LLM Integration Architecture

### Dual-Mode AI Support

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM CONFIGURATION                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Environment Variable: USE_OPENAI                                  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  USE_OPENAI=false (Default)                                 │  │
│   │  ─────────────────────────────                              │  │
│   │                                                             │  │
│   │  ┌─────────────────────┐                                    │  │
│   │  │     OLLAMA          │  • Runs locally on your machine    │  │
│   │  │   (Local LLM)       │  • No API costs - 100% FREE        │  │
│   │  │                     │  • Default model: qwen2.5-coder:3b │  │
│   │  │  localhost:11434    │  • Privacy: data stays local       │  │
│   │  └─────────────────────┘  • Latency: 5-30 seconds           │  │
│   │                                                             │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  USE_OPENAI=true                                            │  │
│   │  ────────────────────                                       │  │
│   │                                                             │  │
│   │  ┌─────────────────────┐                                    │  │
│   │  │     OpenAI          │  • Cloud-based API                 │  │
│   │  │   (GPT-4 / GPT-4o)  │  • Requires API key                │  │
│   │  │                     │  • Default: gpt-4o-mini            │  │
│   │  │  api.openai.com     │  • Higher accuracy                 │  │
│   │  └─────────────────────┘  • Latency: 1-5 seconds            │  │
│   │                                                             │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Setting Up Ollama (FREE Local LLM)

```bash
# 1. Install Ollama
# Windows: Download from https://ollama.ai/download
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull the coding model
ollama pull qwen2.5-coder:3b

# 3. Start the Ollama server
ollama serve

# 4. The API is now available at http://localhost:11434
```

### API Request Flow:

```
┌────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Frontend  │─────▶│   Backend    │─────▶│   LLM Service   │
│   React    │      │   Flask      │      │ Ollama/OpenAI   │
└────────────┘      └──────────────┘      └─────────────────┘
       │                   │                      │
       │  POST /api/ai/    │  _call_llm()         │
       │  recommend        │                      │
       │──────────────────▶│                      │
       │                   │  Construct prompt    │
       │                   │  with user history   │
       │                   │─────────────────────▶│
       │                   │                      │
       │                   │    LLM Response      │
       │                   │◀─────────────────────│
       │                   │                      │
       │                   │  Parse JSON          │
       │   JSON Response   │  Enrich with data    │
       │◀──────────────────│                      │
       │                   │                      │
```

---

## AI-Powered Analysis

### Submission Analysis

When a user submits code, the AI performs deep analysis:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI SUBMISSION ANALYSIS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT TO AI:                                                       │
│  ├── Problem details (title, description, topic, difficulty)       │
│  ├── User's code                                                    │
│  ├── Execution results (passed/failed tests)                       │
│  ├── Failed test case details                                       │
│  └── Last 5 submissions (context)                                   │
│                                                                     │
│  AI ANALYSIS OUTPUT:                                                │
│  ├── Time Complexity                                                │
│  │   ├── estimate: "O(n)"                                          │
│  │   ├── explanation: "Single loop over array"                     │
│  │   └── is_optimal: true/false                                    │
│  │                                                                  │
│  ├── Space Complexity                                               │
│  │   ├── estimate: "O(1)"                                          │
│  │   ├── explanation: "Only uses constant variables"               │
│  │   └── is_optimal: true/false                                    │
│  │                                                                  │
│  ├── Algorithm Type                                                 │
│  │   ├── primary: "Two Pointers"                                   │
│  │   ├── secondary: ["Hash Map"]                                   │
│  │   ├── is_appropriate: true/false                                │
│  │   └── better_approach: null or "Use sliding window"             │
│  │                                                                  │
│  ├── Test Case Analysis                                             │
│  │   ├── total_tests: 10                                           │
│  │   ├── passed_tests: 8                                           │
│  │   ├── failure_patterns: ["edge cases", "empty input"]           │
│  │   └── failure_reasons: ["Off-by-one error"]                     │
│  │                                                                  │
│  ├── Code Quality                                                   │
│  │   ├── readability: 8/10                                         │
│  │   ├── variable_naming: 7/10                                     │
│  │   ├── code_structure: 8/10                                      │
│  │   └── comments: "Needs more comments"                           │
│  │                                                                  │
│  ├── Improvement Tips                                               │
│  │   └── ["Use meaningful variable names", "Add edge case checks"] │
│  │                                                                  │
│  ├── Concepts Demonstrated                                          │
│  │   └── ["Array manipulation", "Loop iteration"]                  │
│  │                                                                  │
│  ├── Concepts to Learn                                              │
│  │   └── ["Two-pointer technique", "Space optimization"]           │
│  │                                                                  │
│  ├── Score: 0-100                                                   │
│  │                                                                  │
│  └── Mastery Level: "Beginner" / "Developing" / "Proficient"       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### AI Recommendation Generation

The AI analyzes the user's complete history to generate personalized recommendations:

```python
# Deep History Analysis performed by AI:

history_analysis = {
    "summary": {
        "total_submissions": 45,
        "unique_problems_attempted": 20,
        "problems_solved": 15,
        "success_rate": 75.0,
        "average_score": 72.5,
        "average_time_minutes": 22.3
    },
    "attempts_analysis": {
        "average_attempts_per_problem": 2.25,
        "problems_with_multiple_attempts": 8,
        "struggled_problems": ["prob_001", "prob_015"]
    },
    "topic_performance": {
        "arrays": {"attempts": 10, "solved": 8, "success_rate": 80},
        "dynamic_programming": {"attempts": 5, "solved": 2, "success_rate": 40},
        # ...
    },
    "algorithm_usage": {
        "Brute Force": 15,
        "Two Pointers": 8,
        "Hash Map": 12,
        "Dynamic Programming": 3
    },
    "complexity_analysis": {
        "optimal_solutions_percentage": 65.0,
        "needs_optimization": True
    },
    "test_failure_patterns": {
        "common_patterns": ["edge cases", "large inputs"],
        "pattern_counts": {"edge cases": 8, "large inputs": 5}
    },
    "skill_assessment": {
        "weak_topics": ["dynamic_programming", "graphs"],
        "strong_topics": ["arrays", "strings"],
        "recommended_focus": ["dynamic_programming", "graphs"]
    }
}
```

### AI Tutor Features

The AI provides 5 interactive help modes:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AI TUTOR CAPABILITIES                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. EXPLAIN PROBLEM                                                 │
│     ├── Simplifies problem statement                                │
│     ├── Explains inputs/outputs                                     │
│     ├── Provides step-by-step examples                              │
│     └── Lists key concepts to know                                  │
│                                                                     │
│  2. GET HINTS (3 Levels)                                            │
│     ├── Level 1: Gentle nudge (direction only)                      │
│     ├── Level 2: Medium hint (suggest approach)                     │
│     └── Level 3: Strong hint (detailed steps)                       │
│                                                                     │
│  3. SOLUTION APPROACH                                               │
│     ├── Key insight/intuition                                       │
│     ├── Algorithm steps (no code)                                   │
│     ├── Why it's optimal                                            │
│     └── Common mistakes to avoid                                    │
│                                                                     │
│  4. ASK DOUBT                                                       │
│     ├── Answers specific questions                                  │
│     ├── Considers user's current code                               │
│     └── Guides without giving solution                              │
│                                                                     │
│  5. DEBUG CODE                                                      │
│     ├── Identifies the bug                                          │
│     ├── Explains why it occurs                                      │
│     ├── Guides to fix (not direct fix)                              │
│     └── Prevention tips                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Recommendation Algorithm Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│              COMPLETE RECOMMENDATION FLOW                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  START: User requests recommendations                               │
│    │                                                                │
│    ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  1. GATHER DATA                                              │   │
│  │     • Fetch user's submission history                        │   │
│  │     • Get all available problems                             │   │
│  │     • Identify solved problem IDs                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│    │                                                                │
│    ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  2. ANALYZE PERFORMANCE                                      │   │
│  │     • Calculate topic breakdown                              │   │
│  │     • Identify strengths/weaknesses                          │   │
│  │     • Determine skill level                                  │   │
│  │     • Analyze algorithm patterns                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│    │                                                                │
│    ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  3. GENERATE RECOMMENDATIONS (Rule-Based)                    │   │
│  │     │                                                        │   │
│  │     ├── 3a. Weakness Recommendations (60%)                   │   │
│  │     │   • Find weak topics (accuracy < 50% or score < 40)    │   │
│  │     │   • Match appropriate difficulty                       │   │
│  │     │   • Select unsolved problems                           │   │
│  │     │                                                        │   │
│  │     ├── 3b. Progression Recommendations (40%)                │   │
│  │     │   • Find topics with score ≥ 70 and accuracy ≥ 70%     │   │
│  │     │   • Advance to next difficulty level                   │   │
│  │     │                                                        │   │
│  │     └── 3c. Exploration (Fallback)                           │   │
│  │         • Find untried topics                                │   │
│  │         • Start with easy problems                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│    │                                                                │
│    ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  4. AI ENHANCEMENT (LLM-Based)                               │   │
│  │     • Deep history analysis                                  │   │
│  │     • Pattern recognition                                    │   │
│  │     • Personalized reasoning                                 │   │
│  │     • Learning path generation                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│    │                                                                │
│    ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  5. OUTPUT                                                   │   │
│  │     • List of recommended problems with reasons              │   │
│  │     • Learning path description                              │   │
│  │     • Strengths summary                                      │   │
│  │     • Weaknesses summary                                     │   │
│  │     • Next steps                                             │   │
│  │     • Estimated time to next level                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  END: Recommendations displayed to user                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Configuration Reference

### Environment Variables

```bash
# .env file configuration

# LLM Selection
USE_OPENAI=false              # Set to "true" for OpenAI, "false" for Ollama

# Ollama Configuration (Local - FREE)
OLLAMA_MODEL=qwen2.5-coder:3b # Model to use with Ollama

# OpenAI Configuration (Paid)
OPENAI_API_KEY=sk-...         # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini      # OpenAI model to use
```

### Scoring Weights (`constants.py`)

```python
SCORING_WEIGHTS = {
    "correctness": 0.35,  # 35% weight for solving correctly
    "efficiency": 0.30,   # 30% weight for optimal complexity
    "speed": 0.20,        # 20% weight for time taken
    "attempts": 0.15      # 15% weight for number of attempts
}
```

### Recommendation Config (`constants.py`)

```python
RECOMMENDATION_CONFIG = {
    "max_recommendations": 5,           # Number of problems to recommend
    "weakness_priority_weight": 0.6,    # 60% focus on weak areas
    "progression_weight": 0.4,          # 40% focus on advancement
    "min_topic_exposure": 3             # Min problems before moving topics
}
```

### Skill Level Thresholds

```python
SKILL_LEVEL_THRESHOLDS = {
    "beginner": (0, 40),       # Score 0-40
    "intermediate": (40, 70),  # Score 40-70
    "advanced": (70, 100)      # Score 70-100
}
```

---

## API Endpoints

### Get AI Recommendations

```
POST /api/ai/recommendations

Request Body:
{
    "user_id": "string"
}

Response:
{
    "recommended_problems": [
        {
            "problem_id": "two_sum",
            "title": "Two Sum",
            "difficulty": "easy",
            "topic": "arrays",
            "reason": "Practice needed in arrays - strengthen fundamentals"
        }
    ],
    "learning_path": {
        "current_level": "Intermediate",
        "focus_areas": ["dynamic_programming", "graphs"],
        "description": "Focus on building DP intuition..."
    },
    "strengths": {
        "topics": ["arrays", "strings"],
        "algorithms": ["Two Pointers", "Hash Map"]
    },
    "weaknesses": {
        "topics": ["dynamic_programming"],
        "algorithms": ["Recursion with memoization"]
    },
    "next_steps": [
        "Practice 3 more DP problems",
        "Focus on identifying subproblems",
        "Try medium difficulty graphs"
    ]
}
```

### Get AI Submission Analysis

```
POST /api/submit

Request Body:
{
    "user_id": "string",
    "problem_id": "string",
    "code": "string",
    "language": "python"
}

Response includes:
{
    "ai_analysis": {
        "feedback": "Great solution! You used...",
        "time_complexity": {
            "estimate": "O(n)",
            "is_optimal": true
        },
        "space_complexity": {
            "estimate": "O(1)",
            "is_optimal": true
        },
        "algorithm_type": {
            "primary": "Two Pointers"
        },
        "score": 85,
        "mastery_level": "Proficient",
        "improvement_tips": [...]
    }
}
```

### AI Tutor Endpoints

```
# Explain Problem
POST /api/ai/help/explain
Body: { "problem_id": "string" }

# Get Hint
POST /api/ai/help/hint
Body: { "problem_id": "string", "level": 1|2|3, "code": "optional" }

# Get Solution Approach
POST /api/ai/help/approach
Body: { "problem_id": "string" }

# Ask Doubt
POST /api/ai/help/doubt
Body: { "problem_id": "string", "question": "string", "code": "optional" }

# Debug Code
POST /api/ai/help/debug
Body: { "problem_id": "string", "code": "string", "error": "optional" }
```

---

## Diagrams Summary

### Data Flow Diagram

```
User Action → Frontend → API → Backend Services → LLM → Response → UI Update
     │                                                                    │
     └────────────────── Feedback Loop ──────────────────────────────────┘
```

### Component Dependency

```
                    ┌─────────────┐
                    │   main.py   │
                    │ (Flask API) │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌───────────────┐
│  AIService    │  │  Analyzer    │  │  Recommender  │
│ (ai_service)  │  │ (analyzer)   │  │ (recommender) │
└───────┬───────┘  └──────┬───────┘  └───────┬───────┘
        │                 │                   │
        │                 ▼                   │
        │          ┌──────────────┐           │
        │          │   Scorer     │           │
        │          │  (scorer)    │           │
        │          └──────┬───────┘           │
        │                 │                   │
        │                 ▼                   │
        │          ┌──────────────┐           │
        └─────────▶│  constants   │◀──────────┘
                   │ complexity   │
                   └──────────────┘
```

---

## Conclusion

The CodeMaster AI recommendation system combines:

1. **Rule-based logic** for consistent, deterministic recommendations
2. **LLM intelligence** for personalized insights and natural language feedback
3. **Multi-factor scoring** considering correctness, efficiency, speed, and attempts
4. **Adaptive difficulty** that progresses users through mastery thresholds
5. **Weakness targeting** to ensure balanced skill development

This hybrid approach ensures users receive relevant, challenging problems that match their current skill level while pushing them to improve in weak areas.
