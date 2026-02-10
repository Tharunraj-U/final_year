"""
Script to upload all problems from problems.json to MongoDB Atlas.
Run this script once to migrate your problems to the cloud database.
"""

import json
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Atlas connection string
MONGODB_URI = "mongodb+srv://root:root@todo.mk9rmqh.mongodb.net/?appName=TODO"

def upload_problems():
    """Upload all problems from problems.json to MongoDB."""
    
    # Connect to MongoDB Atlas
    print("🔌 Connecting to MongoDB Atlas...")
    try:
        client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return
    
    # Get database and collection
    db = client.codemaster_ai
    problems_collection = db.problems
    
    # Load problems from JSON file
    problems_file = os.path.join(os.path.dirname(__file__), "data", "problems.json")
    
    print(f"📂 Loading problems from {problems_file}...")
    try:
        with open(problems_file, "r", encoding="utf-8") as f:
            problems = json.load(f)
        print(f"✅ Loaded {len(problems)} problems from JSON file")
    except FileNotFoundError:
        print(f"❌ File not found: {problems_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return
    
    # Clear existing problems (optional - comment out to append instead)
    print("🗑️  Clearing existing problems in MongoDB...")
    problems_collection.delete_many({})
    
    # Insert problems
    print("📤 Uploading problems to MongoDB...")
    
    # Add problem_id as _id for easy lookup
    for problem in problems:
        problem['_id'] = problem.get('problem_id', problem.get('id'))
    
    try:
        result = problems_collection.insert_many(problems)
        print(f"✅ Successfully uploaded {len(result.inserted_ids)} problems to MongoDB!")
    except Exception as e:
        print(f"❌ Error uploading problems: {e}")
        return
    
    # Create indexes for faster queries
    print("🔧 Creating indexes...")
    problems_collection.create_index("problem_id")
    problems_collection.create_index("topic")
    problems_collection.create_index("difficulty")
    problems_collection.create_index([("topic", 1), ("difficulty", 1)])
    
    # Verify upload
    count = problems_collection.count_documents({})
    print(f"\n✅ Verification: {count} problems now in MongoDB Atlas!")
    
    # Print sample
    print("\n📋 Sample problems:")
    for p in problems_collection.find().limit(5):
        print(f"  - {p.get('problem_id')}: {p.get('title')} ({p.get('difficulty')})")
    
    client.close()
    print("\n🎉 Migration complete!")


if __name__ == "__main__":
    upload_problems()
