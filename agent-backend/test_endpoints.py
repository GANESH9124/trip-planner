"""
Test script for agent-backend API endpoints
Run this after starting the Flask server: python app.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_index():
    """Test index endpoint"""
    print("\n=== Testing Index Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_plan():
    """Test /api/plan endpoint"""
    print("\n=== Testing Plan Endpoint ===")
    data = {
        "task": "Plan a 5-day trip to Paris for a couple"
    }
    response = requests.post(f"{BASE_URL}/api/plan", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Thread ID: {result.get('thread_id')}")
    print(f"Plan (first 200 chars): {result.get('plan', '')[:200]}...")
    return response.status_code == 200, result.get('thread_id')

def test_research(plan, thread_id):
    """Test /api/research endpoint"""
    print("\n=== Testing Research Endpoint ===")
    data = {
        "plan": plan,
        "thread_id": thread_id
    }
    response = requests.post(f"{BASE_URL}/api/research", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Queries: {result.get('queries', [])}")
    print(f"Answers count: {len(result.get('answers', []))}")
    return response.status_code == 200, result

def test_generate(task, plan, thread_id):
    """Test /api/generate endpoint"""
    print("\n=== Testing Generate Endpoint ===")
    data = {
        "task": task,
        "plan": plan,
        "thread_id": thread_id
    }
    response = requests.post(f"{BASE_URL}/api/generate", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Draft (first 200 chars): {result.get('draft', '')[:200]}...")
    print(f"Revision number: {result.get('revision_number')}")
    return response.status_code == 200, result.get('draft', '')

def test_critique(draft, thread_id):
    """Test /api/critique endpoint"""
    print("\n=== Testing Critique Endpoint ===")
    data = {
        "draft": draft,
        "thread_id": thread_id
    }
    response = requests.post(f"{BASE_URL}/api/critique", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Critique (first 200 chars): {result.get('critique', '')[:200]}...")
    return response.status_code == 200

def test_get_state(thread_id):
    """Test /api/get-state endpoint"""
    print("\n=== Testing Get State Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/get-state", params={"thread_id": thread_id})
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"State keys: {list(result.get('values', {}).keys())}")
    return response.status_code == 200

def test_get_state_history(thread_id):
    """Test /api/get-state-history endpoint"""
    print("\n=== Testing Get State History Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/get-state-history", params={"thread_id": thread_id})
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"History entries: {len(result.get('history', []))}")
    return response.status_code == 200

def test_error_cases():
    """Test error handling"""
    print("\n=== Testing Error Cases ===")
    
    # Test plan without task
    print("\n1. Testing plan endpoint without task...")
    response = requests.post(f"{BASE_URL}/api/plan", json={})
    print(f"   Status: {response.status_code} (expected 400)")
    print(f"   Error: {response.json().get('error')}")
    
    # Test research without plan
    print("\n2. Testing research endpoint without plan...")
    response = requests.post(f"{BASE_URL}/api/research", json={"thread_id": "0"})
    print(f"   Status: {response.status_code} (expected 400)")
    print(f"   Error: {response.json().get('error')}")
    
    # Test generate without required fields
    print("\n3. Testing generate endpoint without required fields...")
    response = requests.post(f"{BASE_URL}/api/generate", json={"thread_id": "0"})
    print(f"   Status: {response.status_code} (expected 400)")
    print(f"   Error: {response.json().get('error')}")
    
    # Test critique without draft
    print("\n4. Testing critique endpoint without draft...")
    response = requests.post(f"{BASE_URL}/api/critique", json={"thread_id": "0"})
    print(f"   Status: {response.status_code} (expected 400)")
    print(f"   Error: {response.json().get('error')}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Agent Backend API Test Suite")
    print("=" * 60)
    
    # Basic health checks
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        return
    
    test_index()
    
    # Full workflow test
    print("\n" + "=" * 60)
    print("Testing Full Workflow")
    print("=" * 60)
    
    success, thread_id = test_plan()
    if not success:
        print("\n❌ Plan test failed. Cannot continue.")
        return
    
    # Get the plan for next steps
    plan_response = requests.post(f"{BASE_URL}/api/plan", json={
        "task": "Plan a 5-day trip to Paris for a couple"
    })
    plan = plan_response.json().get('plan', '')
    
    success, research_result = test_research(plan, thread_id)
    if not success:
        print("\n⚠️  Research test failed, but continuing...")
    
    task = "Plan a 5-day trip to Paris for a couple"
    success, draft = test_generate(task, plan, thread_id)
    if not success:
        print("\n⚠️  Generate test failed, but continuing...")
    
    if draft:
        test_critique(draft, thread_id)
    
    # State tests
    test_get_state(thread_id)
    test_get_state_history(thread_id)
    
    # Error handling tests
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    test_error_cases()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Make sure the Flask server is running on http://localhost:5000")
        print("   Start it with: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
