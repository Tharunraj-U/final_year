"""Simple script to test the API."""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    print("Testing health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_problems():
    print("\nTesting problems endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/problems")
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Problems count: {len(data)}")
        if data:
            print(f"First problem: {data[0]['id']}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_run_python():
    print("\n" + "="*50)
    print("Testing Python code execution...")
    try:
        code = """def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []"""
        
        payload = {
            "problem_id": "arr-001",
            "code": code,
            "language": "python"
        }
        
        r = requests.post(f"{BASE_URL}/run", json=payload)
        print(f"Status: {r.status_code}")
        result = r.json()
        print(f"Passed: {result.get('passed')}, Count: {result.get('passed_count')}/{result.get('total_count')}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        return r.status_code == 200 and result.get('passed')
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_run_javascript():
    print("\n" + "="*50)
    print("Testing JavaScript code execution...")
    try:
        code = """function two_sum(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) {
                return [i, j];
            }
        }
    }
    return [];
}"""
        
        payload = {
            "problem_id": "arr-001",
            "code": code,
            "language": "javascript"
        }
        
        r = requests.post(f"{BASE_URL}/run", json=payload)
        print(f"Status: {r.status_code}")
        result = r.json()
        print(f"Passed: {result.get('passed')}, Count: {result.get('passed_count')}/{result.get('total_count')}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_run_java():
    print("\n" + "="*50)
    print("Testing Java code compilation...")
    try:
        code = """class Solution {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }
}"""
        
        payload = {
            "problem_id": "arr-001",
            "code": code,
            "language": "java"
        }
        
        r = requests.post(f"{BASE_URL}/run", json=payload)
        print(f"Status: {r.status_code}")
        result = r.json()
        print(f"Output: {result.get('output', '')[:100]}")
        if result.get('error'):
            print(f"Error: {result['error'][:200]}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stub_code():
    print("\n" + "="*50)
    print("Testing stub code detection (Python)...")
    try:
        code = """def two_sum(nums, target):
    pass"""
        
        payload = {
            "problem_id": "arr-001",
            "code": code,
            "language": "python"
        }
        
        r = requests.post(f"{BASE_URL}/run", json=payload)
        print(f"Status: {r.status_code}")
        result = r.json()
        print(f"Passed: {result.get('passed')}")
        if result.get('error'):
            print(f"Error (expected): {result['error']}")
        return r.status_code == 200 and not result.get('passed')
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stub_code_js():
    print("\n" + "="*50)
    print("Testing stub code detection (JavaScript)...")
    try:
        code = """function two_sum(nums, target) {
    // Write your code here
    
}"""
        
        payload = {
            "problem_id": "arr-001",
            "code": code,
            "language": "javascript"
        }
        
        r = requests.post(f"{BASE_URL}/run", json=payload)
        print(f"Status: {r.status_code}")
        result = r.json()
        print(f"Passed: {result.get('passed')}")
        if result.get('error'):
            print(f"Error (expected): {result['error']}")
        return r.status_code == 200 and not result.get('passed')
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("API TEST SCRIPT")
    print("=" * 50)
    
    results = []
    results.append(("Health", test_health()))
    results.append(("Problems", test_problems()))
    results.append(("Python Execution", test_run_python()))
    results.append(("JavaScript Execution", test_run_javascript()))
    results.append(("Java Compilation", test_run_java()))
    results.append(("Python Stub Detection", test_stub_code()))
    results.append(("JS Stub Detection", test_stub_code_js()))
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
