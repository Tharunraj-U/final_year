"""
MongoDB data storage service for persisting user submissions and coding history.
"""

import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()


class MongoDBStore:
    """
    MongoDB-based data storage for user submissions, coding history, and drafts.
    """
    
    def __init__(self):
        # Connect to MongoDB (cloud or local)
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        
        # Use ServerApi for MongoDB Atlas connections
        if "mongodb+srv" in mongo_uri:
            self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        else:
            self.client = MongoClient(mongo_uri)
        
        # Test connection
        try:
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
        
        self.db = self.client.codemaster_ai
        
        # Collections
        self.users = self.db.users
        self.submissions = self.db.submissions
        self.code_drafts = self.db.code_drafts  # Auto-save drafts
        self.coding_history = self.db.coding_history  # Detailed coding history
        
        # Create indexes
        self._create_indexes()
        self._ensure_default_users()
    
    def _create_indexes(self):
        """Create database indexes for faster queries."""
        # Users indexes
        self.users.create_index("user_id", unique=True)
        self.users.create_index("email")
        self.users.create_index("google_id", sparse=True)
        
        # Submissions indexes
        self.submissions.create_index([("user_id", 1), ("submitted_at", -1)])
        self.submissions.create_index([("user_id", 1), ("problem_id", 1)])
        
        # Code drafts indexes
        self.code_drafts.create_index([("user_id", 1), ("problem_id", 1)], unique=True)
        self.code_drafts.create_index("updated_at")
        
        # Coding history indexes
        self.coding_history.create_index([("user_id", 1), ("timestamp", -1)])
        self.coding_history.create_index([("user_id", 1), ("problem_id", 1)])
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _ensure_default_users(self):
        """Ensure default demo users exist."""
        default_users = [
            {'user_id': 'student_tharun', 'name': 'Tharun', 'email': 'tharun@example.com', 'password': '123'},
            {'user_id': 'student_vijay', 'name': 'Vijay', 'email': 'vijay@example.com', 'password': '123'},
            {'user_id': 'student_irfan', 'name': 'Irfan', 'email': 'irfan@example.com', 'password': '123'},
            {'user_id': 'student_jai', 'name': 'Jai', 'email': 'jai@example.com', 'password': '123'},
        ]
        
        for user in default_users:
            if not self.users.find_one({"user_id": user['user_id']}):
                self.users.insert_one({
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'email': user['email'],
                    'password': self._hash_password(user['password']),
                    'created_at': datetime.now(),
                    'total_submissions': 0,
                    'problems_solved': [],
                    'streak': 0,
                    'last_practice_date': None
                })
    
    # ==================== USER METHODS ====================
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user by username/email and password."""
        hashed = self._hash_password(password)
        
        user = self.users.find_one({
            "$or": [
                {"user_id": username, "password": hashed},
                {"email": username, "password": hashed}
            ]
        })
        
        if user:
            user['_id'] = str(user['_id'])
            user.pop('password', None)
            return user
        return None
    
    def register_user(self, user_id: str, name: str, email: str, password: str) -> Dict:
        """Register a new user."""
        if self.users.find_one({"user_id": user_id}):
            raise ValueError("Username already exists")
        
        if self.users.find_one({"email": email}):
            raise ValueError("Email already registered")
        
        user = {
            'user_id': user_id,
            'name': name,
            'email': email,
            'password': self._hash_password(password),
            'created_at': datetime.now(),
            'total_submissions': 0,
            'problems_solved': [],
            'streak': 0,
            'last_practice_date': None
        }
        
        self.users.insert_one(user)
        user['_id'] = str(user['_id'])
        user.pop('password', None)
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        user = self.users.find_one({"user_id": user_id})
        if user:
            user['_id'] = str(user['_id'])
            return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        user = self.users.find_one({"email": email.lower()})
        if user:
            user['_id'] = str(user['_id'])
            return user
        return None
    
    def get_user_by_google_id(self, google_id: str) -> Optional[Dict]:
        """Get user by Google ID."""
        user = self.users.find_one({"google_id": google_id})
        if user:
            user['_id'] = str(user['_id'])
            return user
        return None
    
    def update_user(self, user_id: str, data: Dict) -> Optional[Dict]:
        """Update user data."""
        data.pop('_id', None)
        data.pop('password', None)
        
        result = self.users.find_one_and_update(
            {"user_id": user_id},
            {"$set": data},
            return_document=True
        )
        if result:
            result['_id'] = str(result['_id'])
            return result
        return None
    
    def register_google_user(self, username: str, name: str, email: str, google_id: str, picture: str = None) -> Dict:
        """Register a new user via Google OAuth."""
        if self.users.find_one({"user_id": username}):
            raise ValueError("Username already exists")
        
        user = {
            'user_id': username,
            'name': name,
            'email': email,
            'google_id': google_id,
            'picture': picture,
            'auth_provider': 'google',
            'created_at': datetime.now(),
            'total_submissions': 0,
            'problems_solved': [],
            'streak': 0,
            'last_practice_date': None
        }
        
        self.users.insert_one(user)
        user['_id'] = str(user['_id'])
        return user
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (without passwords)."""
        users = list(self.users.find({}, {"password": 0}))
        for user in users:
            user['_id'] = str(user['_id'])
        return users
    
    def create_or_update_user(self, user_id: str, data: Dict) -> Dict:
        """Create or update user."""
        data.pop('_id', None)
        
        result = self.users.find_one_and_update(
            {"user_id": user_id},
            {"$set": data, "$setOnInsert": {"created_at": datetime.now()}},
            upsert=True,
            return_document=True
        )
        result['_id'] = str(result['_id'])
        return result
    
    # ==================== SUBMISSION METHODS ====================
    
    def add_submission(self, user_id: str, submission: Dict) -> Dict:
        """Add a new submission and update coding history."""
        submission['user_id'] = user_id
        submission['submitted_at'] = datetime.now()
        submission['_id'] = ObjectId()
        submission['submission_id'] = str(submission['_id'])
        
        # Insert submission
        self.submissions.insert_one(submission)
        
        # Update user stats
        self.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"total_submissions": 1},
                "$addToSet": {"problems_solved": submission.get('problem_id')} if submission.get('passed') else {},
                "$set": {"last_practice_date": datetime.now().date().isoformat()}
            },
            upsert=True
        )
        
        # Update streak
        self._update_streak(user_id)
        
        # Add to coding history
        self._add_coding_history(user_id, submission)
        
        submission['_id'] = str(submission['_id'])
        return submission
    
    def _add_coding_history(self, user_id: str, submission: Dict):
        """Add detailed coding history entry."""
        history_entry = {
            'user_id': user_id,
            'problem_id': submission.get('problem_id'),
            'problem_title': submission.get('problem_title'),
            'topic': submission.get('topic'),
            'difficulty': submission.get('difficulty'),
            'code': submission.get('code'),
            'language': submission.get('language', 'python'),
            'passed': submission.get('passed', False),
            'score': submission.get('score', 0),
            'time_complexity': submission.get('time_complexity'),
            'space_complexity': submission.get('space_complexity'),
            'algorithm_type': submission.get('algorithm_type'),
            'ai_analysis': submission.get('ai_analysis'),
            'timestamp': datetime.now()
        }
        self.coding_history.insert_one(history_entry)
    
    def get_user_submissions(self, user_id: str) -> List[Dict]:
        """Get all submissions for a user."""
        submissions = list(self.submissions.find(
            {"user_id": user_id}
        ).sort("submitted_at", DESCENDING))
        
        for sub in submissions:
            sub['_id'] = str(sub['_id'])
            if 'submitted_at' in sub and isinstance(sub['submitted_at'], datetime):
                sub['submitted_at'] = sub['submitted_at'].isoformat()
        return submissions
    
    def get_solved_problem_ids(self, user_id: str) -> List[str]:
        """Get list of problem IDs solved by user."""
        solved = self.submissions.distinct(
            "problem_id",
            {"user_id": user_id, "passed": True}
        )
        return solved
    
    def get_submission_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent submission history."""
        submissions = list(self.submissions.find(
            {"user_id": user_id}
        ).sort("submitted_at", DESCENDING).limit(limit))
        
        for sub in submissions:
            sub['_id'] = str(sub['_id'])
            if 'submitted_at' in sub and isinstance(sub['submitted_at'], datetime):
                sub['submitted_at'] = sub['submitted_at'].isoformat()
        return submissions
    
    # ==================== CODE DRAFT METHODS (Auto-save) ====================
    
    def save_code_draft(self, user_id: str, problem_id: str, code: str, language: str = 'python') -> Dict:
        """Save code draft for auto-save functionality."""
        draft = {
            'user_id': user_id,
            'problem_id': problem_id,
            'code': code,
            'language': language,
            'updated_at': datetime.now()
        }
        
        self.code_drafts.update_one(
            {"user_id": user_id, "problem_id": problem_id},
            {"$set": draft},
            upsert=True
        )
        
        return draft
    
    def get_code_draft(self, user_id: str, problem_id: str) -> Optional[Dict]:
        """Get saved code draft for a problem."""
        draft = self.code_drafts.find_one({
            "user_id": user_id,
            "problem_id": problem_id
        })
        
        if draft:
            draft['_id'] = str(draft['_id'])
            if 'updated_at' in draft and isinstance(draft['updated_at'], datetime):
                draft['updated_at'] = draft['updated_at'].isoformat()
        return draft
    
    def delete_code_draft(self, user_id: str, problem_id: str):
        """Delete code draft after successful submission."""
        self.code_drafts.delete_one({
            "user_id": user_id,
            "problem_id": problem_id
        })
    
    def get_all_drafts(self, user_id: str) -> List[Dict]:
        """Get all code drafts for a user."""
        drafts = list(self.code_drafts.find({"user_id": user_id}))
        for draft in drafts:
            draft['_id'] = str(draft['_id'])
            if 'updated_at' in draft and isinstance(draft['updated_at'], datetime):
                draft['updated_at'] = draft['updated_at'].isoformat()
        return drafts
    
    # ==================== CODING HISTORY METHODS ====================
    
    def get_coding_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get detailed coding history with full code."""
        history = list(self.coding_history.find(
            {"user_id": user_id}
        ).sort("timestamp", DESCENDING).limit(limit))
        
        for entry in history:
            entry['_id'] = str(entry['_id'])
            if 'timestamp' in entry and isinstance(entry['timestamp'], datetime):
                entry['timestamp'] = entry['timestamp'].isoformat()
        return history
    
    def get_problem_history(self, user_id: str, problem_id: str) -> List[Dict]:
        """Get all attempts for a specific problem."""
        history = list(self.coding_history.find({
            "user_id": user_id,
            "problem_id": problem_id
        }).sort("timestamp", DESCENDING))
        
        for entry in history:
            entry['_id'] = str(entry['_id'])
            if 'timestamp' in entry and isinstance(entry['timestamp'], datetime):
                entry['timestamp'] = entry['timestamp'].isoformat()
        return history
    
    # ==================== STREAK METHODS ====================
    
    def _update_streak(self, user_id: str):
        """Update user's practice streak."""
        user = self.get_user(user_id)
        if not user:
            return
        
        today = datetime.now().date()
        last_practice = user.get('last_practice_date')
        current_streak = user.get('streak', 0)
        
        if last_practice:
            if isinstance(last_practice, str):
                try:
                    last_date = datetime.fromisoformat(last_practice).date()
                except:
                    last_date = None
            else:
                last_date = last_practice
            
            if last_date:
                diff = (today - last_date).days
                
                if diff == 0:
                    # Same day, streak unchanged
                    pass
                elif diff == 1:
                    # Consecutive day, increment streak
                    current_streak += 1
                else:
                    # Streak broken, reset
                    current_streak = 1
            else:
                current_streak = 1
        else:
            current_streak = 1
        
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "streak": current_streak,
                "last_practice_date": today.isoformat()
            }}
        )
    
    def get_user_streak(self, user_id: str) -> Dict:
        """Get user's streak information."""
        user = self.get_user(user_id)
        if not user:
            return {"streak": 0, "last_practice_date": None}
        
        # Get practice dates for calendar
        submissions = list(self.submissions.find(
            {"user_id": user_id},
            {"submitted_at": 1}
        ).sort("submitted_at", DESCENDING).limit(365))
        
        practice_dates = set()
        for sub in submissions:
            if 'submitted_at' in sub:
                dt = sub['submitted_at']
                if isinstance(dt, datetime):
                    practice_dates.add(dt.strftime('%Y-%m-%d'))
        
        return {
            "streak": user.get('streak', 0),
            "last_practice_date": user.get('last_practice_date'),
            "practice_dates": list(practice_dates)
        }
    
    # ==================== STATS METHODS ====================
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics."""
        user = self.get_user(user_id)
        
        if not user:
            return {
                'total_submissions': 0,
                'problems_solved': 0,
                'success_rate': 0,
                'avg_score': 0,
                'streak': 0,
                'total_score': 0
            }
        
        # Get submission stats
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "passed": {"$sum": {"$cond": ["$passed", 1, 0]}},
                "total_score": {"$sum": {"$ifNull": ["$score", 0]}}
            }}
        ]
        
        result = list(self.submissions.aggregate(pipeline))
        stats = result[0] if result else {"total": 0, "passed": 0, "total_score": 0}
        
        solved_count = len(self.get_solved_problem_ids(user_id))
        
        return {
            'total_submissions': stats.get('total', 0),
            'problems_solved': solved_count,
            'success_rate': round((stats.get('passed', 0) / stats.get('total', 1)) * 100, 1) if stats.get('total', 0) > 0 else 0,
            'avg_score': round(stats.get('total_score', 0) / stats.get('total', 1), 1) if stats.get('total', 0) > 0 else 0,
            'streak': user.get('streak', 0),
            'total_score': round(stats.get('total_score', 0), 1)
        }
    
    def clear_user_data(self, user_id: str):
        """Clear all data for a user."""
        self.users.delete_one({"user_id": user_id})
        self.submissions.delete_many({"user_id": user_id})
        self.code_drafts.delete_many({"user_id": user_id})
        self.coding_history.delete_many({"user_id": user_id})
