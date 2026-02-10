"""Test the get_problem_submissions function."""
from app.services.data_store import DataStore

ds = DataStore()

# Get some test user submissions
user_id = 'guest_user'
all_subs = ds.get_user_submissions(user_id)
print(f'Total submissions for {user_id}: {len(all_subs)}')

if all_subs:
    # Get a problem_id from first submission
    problem_id = all_subs[0].get('problem_id')
    print(f'Testing get_problem_submissions for problem: {problem_id}')
    
    problem_subs = ds.get_problem_submissions(user_id, problem_id)
    print(f'Submissions for this problem: {len(problem_subs)}')
    
    if problem_subs:
        sub = problem_subs[0]
        submitted_at = sub.get('submitted_at', 'N/A')
        passed = sub.get('passed', False)
        score = sub.get('score', 0)
        language = sub.get('language', 'N/A')
        has_code = 'code' in sub and len(sub.get('code', '')) > 0
        
        print(f'  - Date: {submitted_at}')
        print(f'  - Passed: {passed}')
        print(f'  - Score: {score}')
        print(f'  - Language: {language}')
        print(f'  - Has code: {has_code}')
else:
    print('No submissions found. Try submitting a solution first.')
