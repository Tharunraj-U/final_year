"""Test script to verify Ollama integration works."""
import requests
import json

print("Testing simple Ollama call...")
print("=" * 50)

payload = {
    "model": "qwen2.5-coder:3b",
    "messages": [{"role": "user", "content": "Respond with only this JSON: {\"status\": \"ok\", \"message\": \"hello\"}"}],
    "stream": False,
    "options": {"temperature": 0.3, "num_predict": 50}
}

try:
    print("Sending request to Ollama...")
    resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        print(f"Response: {content}")
        print("\n✅ Ollama is working!")
    else:
        print(f"Error: {resp.text}")
except requests.exceptions.Timeout:
    print("❌ Request timed out. Model might be loading or too slow.")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Ollama. Make sure 'ollama serve' is running.")
except Exception as e:
    print(f"❌ Error: {e}")
