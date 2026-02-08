"""
Flask API application for AI Learning Assistant.
LeetCode-style problem solving with GPT-powered recommendations.
"""

import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from .models.problem import ProblemBank, Problem
from .services.ai_service import AIService
from .services.data_store import DataStore
from .services.code_executor import CodeExecutor
from .services.google_oauth import google_oauth_service
from .services.email_service import email_service

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}}, supports_credentials=True)

# Initialize services
problem_bank = ProblemBank()
data_store = DataStore()
code_executor = CodeExecutor()
ai_service = AIService()


def load_problem_bank(filepath: str = "data/problems.json"):
    """Load problems from JSON file."""
    try:
        with open(filepath, "r") as f:
            problems_data = json.load(f)
            problem_bank.load_from_list(problems_data)
            print(f"Loaded {len(problem_bank)} problems")
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. Using empty problem bank.")
    except json.JSONDecodeError as e:
        print(f"Error loading problems: {e}")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "AI Learning Assistant",
        "problems_loaded": len(problem_bank)
    })


# Handle CORS preflight for all routes
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# ==================== AUTHENTICATION ====================

@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    """Login endpoint."""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        user = data_store.authenticate_user(username, password)
        
        if user:
            return jsonify({
                "success": True,
                "user": user,
                "message": "Login successful"
            })
        else:
            return jsonify({"error": "Invalid username or password"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    """Register endpoint."""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json()
        
        username = data.get("username", "").strip().lower().replace(" ", "_")
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        if not username or not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400
        
        if len(password) < 3:
            return jsonify({"error": "Password must be at least 3 characters"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        user = data_store.register_user(username, name, email, password)
        
        return jsonify({
            "success": True,
            "user": user,
            "message": "Registration successful"
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/user/<user_id>", methods=["GET"])
def get_auth_user(user_id):
    """Get user profile."""
    user = data_store.get_user(user_id)
    if user:
        user_copy = user.copy()
        user_copy.pop('password', None)
        return jsonify(user_copy)
    return jsonify({"error": "User not found"}), 404


@app.route("/api/auth/google", methods=["POST", "OPTIONS"])
def google_auth():
    """Google OAuth authentication endpoint."""
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json()
        token = data.get("token") or data.get("credential") or data.get("access_token")
        
        if not token:
            return jsonify({"error": "Token is required"}), 400
        
        # Try to verify as ID token first, then as access token
        user_info = google_oauth_service.verify_token(token)
        if not user_info:
            user_info = google_oauth_service.verify_access_token(token)
        
        if not user_info:
            return jsonify({"error": "Invalid Google token"}), 401
        
        # Check if user exists by email or Google ID
        email = user_info.get('email')
        google_id = user_info.get('google_id')
        
        existing_user = data_store.get_user_by_email(email)
        
        if existing_user:
            # Update Google ID if not set
            if not existing_user.get('google_id'):
                data_store.update_user(existing_user['user_id'], {'google_id': google_id})
            
            user = existing_user.copy()
            user.pop('password', None)
            return jsonify({
                "success": True,
                "user": user,
                "message": "Login successful"
            })
        else:
            # Create new user
            username = email.split('@')[0].lower().replace('.', '_')
            name = user_info.get('name', username)
            
            # Make username unique
            base_username = username
            counter = 1
            while data_store.get_user(username):
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = data_store.register_google_user(
                username=username,
                name=name,
                email=email,
                google_id=google_id,
                picture=user_info.get('picture')
            )
            
            return jsonify({
                "success": True,
                "user": user,
                "message": "Account created successfully"
            }), 201
            
    except Exception as e:
        print(f"Google auth error: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== WEEKLY REPORTS ====================

@app.route("/api/reports/send-weekly", methods=["POST"])
def send_weekly_report():
    """Send weekly report to a specific user."""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        user = data_store.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        stats = data_store.get_user_stats(user_id)
        submissions = data_store.get_submission_history(user_id, 100)
        
        success = email_service.send_weekly_report(user, stats, submissions)
        
        if success:
            return jsonify({"success": True, "message": "Weekly report sent successfully"})
        else:
            return jsonify({"error": "Failed to send email"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/send-all-weekly", methods=["POST"])
def send_all_weekly_reports():
    """Send weekly reports to all users with emails."""
    try:
        users = data_store.get_all_users()
        sent_count = 0
        failed_count = 0
        
        for user in users:
            if user.get('email'):
                user_id = user.get('user_id')
                stats = data_store.get_user_stats(user_id)
                submissions = data_store.get_submission_history(user_id, 100)
                
                if email_service.send_weekly_report(user, stats, submissions):
                    sent_count += 1
                else:
                    failed_count += 1
        
        return jsonify({
            "success": True,
            "sent": sent_count,
            "failed": failed_count,
            "message": f"Sent {sent_count} reports, {failed_count} failed"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/preview/<user_id>", methods=["GET"])
def preview_weekly_report(user_id):
    """Preview the weekly report HTML for a user."""
    try:
        user = data_store.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        stats = data_store.get_user_stats(user_id)
        submissions = data_store.get_submission_history(user_id, 100)
        
        html = email_service.generate_weekly_report_html(user, stats, submissions)
        
        return html, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== PROBLEMS ====================

@app.route("/api/problems", methods=["GET"])
def list_problems():
    """List all available problems."""
    topic = request.args.get("topic")
    difficulty = request.args.get("difficulty")
    user_id = request.args.get("user_id")
    
    if topic and difficulty:
        problems = problem_bank.get_by_topic_and_difficulty(topic, difficulty)
    elif topic:
        problems = problem_bank.get_by_topic(topic)
    elif difficulty:
        problems = problem_bank.get_by_difficulty(difficulty)
    else:
        problems = list(problem_bank.problems.values())
    
    # Add solved status if user_id provided
    solved_ids = []
    if user_id:
        solved_ids = data_store.get_solved_problem_ids(user_id)
    
    problems_list = []
    for p in problems:
        problem_dict = p.to_dict()
        problem_dict['solved'] = p.problem_id in solved_ids
        problems_list.append(problem_dict)
    
    return jsonify({
        "count": len(problems_list),
        "problems": problems_list
    })


@app.route("/api/problems/<problem_id>", methods=["GET"])
def get_problem(problem_id):
    """Get a specific problem with details."""
    problem = problem_bank.get_problem(problem_id)
    
    if not problem:
        return jsonify({"error": "Problem not found"}), 404
    
    user_id = request.args.get("user_id")
    solved = False
    if user_id:
        solved_ids = data_store.get_solved_problem_ids(user_id)
        solved = problem_id in solved_ids
    
    problem_dict = problem.to_dict()
    problem_dict['solved'] = solved
    
    return jsonify(problem_dict)


# ==================== CODE EXECUTION ====================

@app.route("/api/run", methods=["POST"])
def run_code():
    """Run code without submitting (for testing)."""
    try:
        data = request.get_json()
        
        problem_id = data.get("problem_id")
        user_code = data.get("code", "")
        language = data.get("language", "python")
        
        problem = problem_bank.get_problem(problem_id)
        if not problem:
            return jsonify({"error": "Problem not found"}), 404
        
        # Validate code first
        validation = code_executor.validate_code(user_code, language)
        if not validation['valid']:
            return jsonify({
                "passed": False,
                "error": validation['error'],
                "test_results": []
            })
        
        # Get test cases for the problem
        test_cases = problem.to_dict().get('test_cases', [])
        if not test_cases:
            test_cases = [{"input": [], "expected": None}]
        
        # Execute code
        result = code_executor.execute_code(
            user_code,
            test_cases[:3],
            problem.to_dict().get('function_name', 'solution'),
            language
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/submit", methods=["POST"])
def submit_code():
    """Submit code for evaluation and get comprehensive AI feedback."""
    try:
        data = request.get_json()
        
        user_id = data.get("user_id", "anonymous")
        problem_id = data.get("problem_id")
        user_code = data.get("code", "")
        time_taken = data.get("time_taken_minutes", 0)
        language = data.get("language", "python")
        
        problem = problem_bank.get_problem(problem_id)
        if not problem:
            return jsonify({"error": "Problem not found"}), 404
        
        problem_dict = problem.to_dict()
        
        # Execute code against all test cases
        test_cases = problem_dict.get('test_cases', [])
        result = code_executor.execute_code(
            user_code,
            test_cases,
            problem_dict.get('function_name', 'solution'),
            language
        )
        
        # Get submission history for AI analysis
        history = data_store.get_user_submissions(user_id)
        
        # Count attempts for this specific problem
        attempt_count = sum(1 for h in history if h.get('problem_id') == problem_id) + 1
        
        # Get AI analysis with all parameters
        ai_analysis = ai_service.analyze_submission(
            problem_dict,
            user_code,
            result,
            history,
            attempt_count=attempt_count,
            language=language
        )
        
        # Build comprehensive submission record
        submission = {
            'problem_id': problem_id,
            'problem_title': problem_dict['title'],
            'topic': problem_dict['topic'],
            'difficulty': problem_dict['difficulty'],
            'code': user_code,
            'language': language,
            'passed': result['passed'],
            'passed_count': result.get('passed_count', 0),
            'total_count': result.get('total_count', 0),
            'failed_count': result.get('total_count', 0) - result.get('passed_count', 0),
            'time_taken_minutes': time_taken,
            'expected_time_minutes': problem_dict.get('expected_time_minutes', 30),
            'attempt_number': attempt_count,
            'score': ai_analysis.get('score', 0),
            # Complexity analysis
            'time_complexity': ai_analysis.get('time_complexity', {}),
            'space_complexity': ai_analysis.get('space_complexity', {}),
            # Algorithm analysis
            'algorithm_type': ai_analysis.get('algorithm_type', {}),
            # Test case analysis
            'test_case_analysis': ai_analysis.get('test_case_analysis', {}),
            # Code quality
            'code_quality': ai_analysis.get('code_quality', {}),
            'mastery_level': ai_analysis.get('mastery_level', 'Unknown'),
            # Store full AI analysis for history
            'ai_analysis': ai_analysis
        }
        
        saved_submission = data_store.add_submission(user_id, submission)
        
        return jsonify({
            'submission': saved_submission,
            'execution_result': result,
            'ai_analysis': ai_analysis
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== AI RECOMMENDATIONS ====================

@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """Get AI-powered problem recommendations."""
    user_id = request.args.get("user_id", "anonymous")
    
    try:
        history = data_store.get_user_submissions(user_id)
        solved_ids = data_store.get_solved_problem_ids(user_id)
        all_problems = [p.to_dict() for p in problem_bank.problems.values()]
        
        recommendations = ai_service.get_recommendations(
            history,
            all_problems,
            solved_ids
        )
        
        return jsonify(recommendations)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== USER DATA ====================

@app.route("/api/user/<user_id>/stats", methods=["GET"])
def get_user_stats(user_id):
    """Get user statistics."""
    stats = data_store.get_user_stats(user_id)
    return jsonify(stats)


@app.route("/api/user/<user_id>/detailed-stats", methods=["GET"])
def get_user_detailed_stats(user_id):
    """Get detailed user statistics for dashboard."""
    basic_stats = data_store.get_user_stats(user_id)
    submissions = data_store.get_submission_history(user_id, 100)
    
    # Calculate detailed stats
    easy_solved = 0
    medium_solved = 0
    hard_solved = 0
    total_score = 0
    perfect_scores = 0
    
    solved_problems = set()
    for sub in submissions:
        if sub.get('score', 0) > 0:
            solved_problems.add(sub.get('problem_id'))
            total_score += sub.get('score', 0)
            if sub.get('score', 0) >= 95:
                perfect_scores += 1
            
            difficulty = sub.get('difficulty', 'medium').lower()
            if difficulty == 'easy':
                easy_solved += 1
            elif difficulty == 'medium':
                medium_solved += 1
            elif difficulty == 'hard':
                hard_solved += 1
    
    accuracy = 0
    if len(submissions) > 0:
        successful = len([s for s in submissions if s.get('score', 0) >= 60])
        accuracy = round((successful / len(submissions)) * 100)
    
    return jsonify({
        "problems_solved": len(solved_problems),
        "total_submissions": len(submissions),
        "accuracy": accuracy,
        "avg_score": basic_stats.get('avg_score', 0),
        "easy_solved": easy_solved,
        "medium_solved": medium_solved,
        "hard_solved": hard_solved,
        "streak": basic_stats.get('streak', 0),
        "total_score": total_score,
        "perfect_scores": perfect_scores
    })


@app.route("/api/user/<user_id>/streak", methods=["GET"])
def get_user_streak(user_id):
    """Get user's practice streak."""
    stats = data_store.get_user_stats(user_id)
    return jsonify({
        "streak": stats.get('streak', 0),
        "last_practice": stats.get('last_submission_date')
    })


@app.route("/api/user/<user_id>/achievements", methods=["GET"])
def get_user_achievements(user_id):
    """Get user achievement stats for determining unlocked achievements."""
    basic_stats = data_store.get_user_stats(user_id)
    submissions = data_store.get_submission_history(user_id, 200)
    
    # Gather achievement-related stats
    problems_solved = basic_stats.get('problems_solved', 0)
    streak = basic_stats.get('streak', 0)
    
    # Check for perfect scores
    has_perfect_score = any(s.get('score', 0) >= 100 for s in submissions)
    
    # Get fastest solve time
    fastest_solve = 999
    for sub in submissions:
        time_taken = sub.get('time_taken_minutes', 999)
        if time_taken > 0 and time_taken < fastest_solve:
            fastest_solve = time_taken
    
    # Count unique topics
    topics = set()
    for sub in submissions:
        topic = sub.get('topic')
        if topic:
            topics.add(topic)
    
    # Count hard problems solved
    hard_solved = len([s for s in submissions if s.get('difficulty', '').lower() == 'hard' and s.get('score', 0) > 0])
    
    return jsonify({
        "problems_solved": problems_solved,
        "streak": streak,
        "has_perfect_score": has_perfect_score,
        "fastest_solve": fastest_solve,
        "topics_count": len(topics),
        "hard_solved": hard_solved
    })


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get leaderboard of top users."""
    timeframe = request.args.get("timeframe", "all")
    
    # Get all users and their stats
    users = data_store.get_all_users()
    leaderboard = []
    
    avatars = ['🦁', '🐯', '🐻', '🦊', '🐼', '🐨', '🐸', '🦉', '🦋', '🐙']
    
    for i, user in enumerate(users):
        user_id = user.get('user_id')
        if not user_id:
            continue
            
        stats = data_store.get_user_stats(user_id)
        leaderboard.append({
            "username": user_id,
            "name": user.get('name', user_id),
            "problems_solved": stats.get('problems_solved', 0),
            "total_score": stats.get('total_score', 0),
            "avatar": avatars[i % len(avatars)]
        })
    
    # Sort by total score, then by problems solved
    leaderboard.sort(key=lambda x: (-x['total_score'], -x['problems_solved']))
    
    # Add rank
    for i, entry in enumerate(leaderboard):
        entry['rank'] = i + 1
    
    return jsonify(leaderboard[:20])  # Return top 20


@app.route("/api/user/<user_id>/history", methods=["GET"])
def get_user_history(user_id):
    """Get user submission history."""
    limit = request.args.get("limit", 50, type=int)
    history = data_store.get_submission_history(user_id, limit)
    return jsonify({
        "count": len(history),
        "submissions": history
    })


@app.route("/api/user/<user_id>", methods=["DELETE"])
def clear_user_data(user_id):
    """Clear all user data."""
    data_store.clear_user_data(user_id)
    return jsonify({"message": f"Data cleared for user {user_id}"})


@app.route("/api/topics", methods=["GET"])
def list_topics():
    """Get list of all available topics."""
    topics = problem_bank.get_all_topics()
    return jsonify({
        "count": len(topics),
        "topics": topics
    })


# ==================== CUSTOM PROBLEMS ====================

@app.route("/api/problems/custom", methods=["POST"])
def add_custom_problem():
    """Add a custom problem uploaded by user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'difficulty', 'topic', 'description', 'function_name', 'test_cases']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate a unique problem ID
        import uuid
        problem_id = f"custom-{uuid.uuid4().hex[:8]}"
        
        # Create problem data
        problem_data = {
            "problem_id": problem_id,
            "title": data['title'],
            "difficulty": data['difficulty'].lower(),
            "topic": data['topic'].lower().replace(' ', '_'),
            "expected_complexity": data.get('expected_complexity', 'O(n)'),
            "expected_time_minutes": data.get('expected_time_minutes', 30),
            "tags": data.get('tags', [data['topic']]),
            "description": data['description'],
            "function_name": data['function_name'],
            "starter_code": data.get('starter_code', f"def {data['function_name']}():\n    # Write your code here\n    pass"),
            "test_cases": data['test_cases'],
            "is_custom": True,
            "created_by": data.get('user_id', 'anonymous')
        }
        
        # Create and add problem
        problem = Problem.from_dict(problem_data)
        problem_bank.add_problem(problem)
        
        # Save to custom problems file
        save_custom_problem(problem_data)
        
        return jsonify({
            "message": "Problem created successfully",
            "problem": problem.to_dict()
        }), 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def save_custom_problem(problem_data: dict):
    """Save custom problem to a separate JSON file."""
    custom_file = "data/custom_problems.json"
    try:
        with open(custom_file, "r") as f:
            custom_problems = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        custom_problems = []
    
    custom_problems.append(problem_data)
    
    with open(custom_file, "w") as f:
        json.dump(custom_problems, f, indent=2)


def load_custom_problems():
    """Load custom problems from file."""
    custom_file = "data/custom_problems.json"
    try:
        with open(custom_file, "r") as f:
            custom_problems = json.load(f)
            for data in custom_problems:
                problem = Problem.from_dict(data)
                problem_bank.add_problem(problem)
            print(f"Loaded {len(custom_problems)} custom problems")
    except (FileNotFoundError, json.JSONDecodeError):
        pass


def create_app():
    """Application factory."""
    load_problem_bank()
    load_custom_problems()
    return app


if __name__ == "__main__":
    load_problem_bank()
    load_custom_problems()
    print("Starting server on http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000, threaded=True)
