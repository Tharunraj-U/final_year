"""
Data storage service for persisting user submissions and history.
"""

import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime


class DataStore:
    """
    Simple JSON-based data storage for user submissions and history.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.submissions_file = os.path.join(data_dir, "submissions.json")
        self._ensure_files()
        self._ensure_default_users()
    
    def _ensure_files(self):
        """Ensure data files exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.users_file):
            self._write_json(self.users_file, {})
        
        if not os.path.exists(self.submissions_file):
            self._write_json(self.submissions_file, {})
    
    def _ensure_default_users(self):
        """Ensure default demo users exist with passwords."""
        users = self._read_json(self.users_file)
        
        default_users = {
            'student_tharun': {'name': 'Tharun', 'email': 'tharun@example.com', 'password': self._hash_password('123')},
            'student_vijay': {'name': 'Vijay', 'email': 'vijay@example.com', 'password': self._hash_password('123')},
            'student_irfan': {'name': 'Irfan', 'email': 'irfan@example.com', 'password': self._hash_password('123')},
            'student_jai': {'name': 'Jai', 'email': 'jai@example.com', 'password': self._hash_password('123')},
        }
        
        updated = False
        for user_id, user_data in default_users.items():
            if user_id not in users:
                users[user_id] = {
                    'user_id': user_id,
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'created_at': datetime.now().isoformat(),
                    'total_submissions': 0,
                    'problems_solved': []
                }
                updated = True
            elif 'password' not in users[user_id]:
                users[user_id]['password'] = user_data['password']
                users[user_id]['name'] = user_data['name']
                users[user_id]['email'] = user_data['email']
                updated = True
        
        if updated:
            self._write_json(self.users_file, users)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password."""
        user = self.get_user(user_id)
        if not user or 'password' not in user:
            return False
        return user['password'] == self._hash_password(password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user by username/user_id and password."""
        users = self._read_json(self.users_file)
        
        # Check by user_id
        if username in users:
            if users[username].get('password') == self._hash_password(password):
                user = users[username].copy()
                user.pop('password', None)
                return user
        
        # Check by email
        for user_id, user in users.items():
            if user.get('email') == username:
                if user.get('password') == self._hash_password(password):
                    result = user.copy()
                    result.pop('password', None)
                    return result
        
        return None
    
    def register_user(self, user_id: str, name: str, email: str, password: str) -> Dict:
        """Register a new user."""
        users = self._read_json(self.users_file)
        
        if user_id in users:
            raise ValueError("Username already exists")
        
        # Check if email already exists
        for uid, user in users.items():
            if user.get('email') == email:
                raise ValueError("Email already registered")
        
        users[user_id] = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'password': self._hash_password(password),
            'created_at': datetime.now().isoformat(),
            'total_submissions': 0,
            'problems_solved': []
        }
        
        self._write_json(self.users_file, users)
        
        result = users[user_id].copy()
        result.pop('password', None)
        return result
    
    def _read_json(self, filepath: str) -> Dict:
        """Read JSON file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_json(self, filepath: str, data: Dict):
        """Write JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # User methods
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data."""
        users = self._read_json(self.users_file)
        return users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address."""
        users = self._read_json(self.users_file)
        for user_id, user in users.items():
            if user.get('email', '').lower() == email.lower():
                return user
        return None
    
    def get_user_by_google_id(self, google_id: str) -> Optional[Dict]:
        """Get user by Google ID."""
        users = self._read_json(self.users_file)
        for user_id, user in users.items():
            if user.get('google_id') == google_id:
                return user
        return None
    
    def update_user(self, user_id: str, data: Dict) -> Optional[Dict]:
        """Update user data."""
        users = self._read_json(self.users_file)
        if user_id not in users:
            return None
        users[user_id].update(data)
        self._write_json(self.users_file, users)
        return users[user_id]
    
    def register_google_user(self, username: str, name: str, email: str, google_id: str, picture: str = None) -> Dict:
        """Register a new user via Google OAuth."""
        users = self._read_json(self.users_file)
        
        if username in users:
            raise ValueError("Username already exists")
        
        users[username] = {
            'user_id': username,
            'name': name,
            'email': email,
            'google_id': google_id,
            'picture': picture,
            'auth_provider': 'google',
            'created_at': datetime.now().isoformat(),
            'total_submissions': 0,
            'problems_solved': []
        }
        
        self._write_json(self.users_file, users)
        return users[username]
    
    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        users = self._read_json(self.users_file)
        user_list = []
        for user_id, user in users.items():
            user_copy = user.copy()
            user_copy.pop('password', None)
            user_list.append(user_copy)
        return user_list
    
    def create_or_update_user(self, user_id: str, data: Dict) -> Dict:
        """Create or update user."""
        users = self._read_json(self.users_file)
        
        if user_id not in users:
            users[user_id] = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'total_submissions': 0,
                'problems_solved': [],
                **data
            }
        else:
            users[user_id].update(data)
        
        self._write_json(self.users_file, users)
        return users[user_id]
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics."""
        user = self.get_user(user_id)
        submissions = self.get_user_submissions(user_id)
        
        if not user:
            return {
                'total_submissions': 0,
                'problems_solved': 0,
                'success_rate': 0,
                'avg_score': 0,
                'streak': 0,
                'total_score': 0
            }
        
        solved = len(set(s['problem_id'] for s in submissions if s.get('passed')))
        total = len(submissions)
        passed = sum(1 for s in submissions if s.get('passed'))
        total_score = sum(s.get('score', 0) for s in submissions)
        avg_score = total_score / total if total > 0 else 0
        
        # Calculate streak (simplified - based on consecutive days)
        streak = self._calculate_streak(submissions)
        
        return {
            'total_submissions': total,
            'problems_solved': solved,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'avg_score': round(avg_score, 1),
            'streak': streak,
            'total_score': round(total_score, 1)
        }
    
    def _calculate_streak(self, submissions: List[Dict]) -> int:
        """Calculate practice streak from submissions."""
        if not submissions:
            return 0
        
        from datetime import datetime, timedelta
        
        # Get unique dates
        dates = set()
        for sub in submissions:
            submitted_at = sub.get('submitted_at', '')
            if submitted_at:
                try:
                    dt = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    dates.add(dt.date())
                except:
                    pass
        
        if not dates:
            return 0
        
        # Sort dates in descending order
        sorted_dates = sorted(dates, reverse=True)
        today = datetime.now().date()
        
        # Check if most recent submission is today or yesterday
        if sorted_dates[0] < today - timedelta(days=1):
            return 0  # Streak broken
        
        # Count consecutive days
        streak = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i-1] - sorted_dates[i] == timedelta(days=1):
                streak += 1
            else:
                break
        
        return streak
    
    # Submission methods
    def add_submission(self, user_id: str, submission: Dict) -> Dict:
        """Add a new submission."""
        submissions = self._read_json(self.submissions_file)
        
        if user_id not in submissions:
            submissions[user_id] = []
        
        # Add metadata
        submission['submission_id'] = f"{user_id}_{len(submissions[user_id]) + 1}"
        submission['submitted_at'] = datetime.now().isoformat()
        
        submissions[user_id].append(submission)
        self._write_json(self.submissions_file, submissions)
        
        # Update user stats
        user = self.get_user(user_id) or {}
        user['total_submissions'] = len(submissions[user_id])
        if submission.get('passed') and submission.get('problem_id'):
            solved = set(user.get('problems_solved', []))
            solved.add(submission['problem_id'])
            user['problems_solved'] = list(solved)
        self.create_or_update_user(user_id, user)
        
        return submission
    
    def get_user_submissions(self, user_id: str) -> List[Dict]:
        """Get all submissions for a user."""
        submissions = self._read_json(self.submissions_file)
        return submissions.get(user_id, [])
    
    def get_solved_problem_ids(self, user_id: str) -> List[str]:
        """Get list of problem IDs solved by user."""
        submissions = self.get_user_submissions(user_id)
        return list(set(s['problem_id'] for s in submissions if s.get('passed')))
    
    def get_problem_submissions(self, user_id: str, problem_id: str) -> List[Dict]:
        """Get all submissions for a specific problem by a user."""
        submissions = self.get_user_submissions(user_id)
        problem_subs = [s for s in submissions if s.get('problem_id') == problem_id]
        return sorted(
            problem_subs,
            key=lambda x: x.get('submitted_at', ''),
            reverse=True
        )
    
    def get_submission_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent submission history."""
        submissions = self.get_user_submissions(user_id)
        return sorted(
            submissions,
            key=lambda x: x.get('submitted_at', ''),
            reverse=True
        )[:limit]
    
    def clear_user_data(self, user_id: str):
        """Clear all data for a user."""
        users = self._read_json(self.users_file)
        submissions = self._read_json(self.submissions_file)
        
        if user_id in users:
            del users[user_id]
            self._write_json(self.users_file, users)
        
        if user_id in submissions:
            del submissions[user_id]
            self._write_json(self.submissions_file, submissions)

    def get_all_users(self) -> List[Dict]:
        """Get all users (without passwords)."""
        users = self._read_json(self.users_file)
        result = []
        for user_id, user_data in users.items():
            user_copy = user_data.copy()
            user_copy.pop('password', None)
            result.append(user_copy)
        return result
