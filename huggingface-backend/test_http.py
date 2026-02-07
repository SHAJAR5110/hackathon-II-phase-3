"""Test HTTP endpoints"""
import urllib.request
import json
import time
import uuid

BASE = "http://localhost:8000"

# Use unique email to avoid conflicts
unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

def test_signup():
    data = json.dumps({
        "email": unique_email,
        "password": "TestPass123",
        "name": "HTTP Test"
    }).encode()
    
    req = urllib.request.Request(
        f"{BASE}/api/auth/signup",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            print(f"STATUS: {resp.status}")
            result = json.loads(body)
            print(f"USER: {result['user']['email']}")
            print(f"TOKEN: {result['token'][:50]}...")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP ERROR: {e.code}")
        print(f"BODY: {body}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_create_task(token):
    data = json.dumps({
        "title": "Test Task from Script",
        "description": "Auto-created task"
    }).encode()
    
    req = urllib.request.Request(
        f"{BASE}/api/tasks",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            print(f"STATUS: {resp.status}")
            result = json.loads(body)
            print(f"TASK: id={result['id']}, title={result['title']}")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP ERROR: {e.code}")
        print(f"BODY: {body}")
        return None

def test_list_tasks(token):
    req = urllib.request.Request(
        f"{BASE}/api/tasks",
        headers={"Authorization": f"Bearer {token}"},
        method="GET"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            print(f"STATUS: {resp.status}")
            result = json.loads(body)
            print(f"TASKS COUNT: {len(result['tasks'])}")
            for t in result['tasks']:
                print(f"  - [{t['id']}] {t['title']} (completed={t['completed']})")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP ERROR: {e.code}")
        print(f"BODY: {body}")

if __name__ == "__main__":
    print(f"Testing with email: {unique_email}")
    
    print("\n=== Test 1: Signup ===")
    result = test_signup()
    
    if not result or "token" not in result:
        print("Signup failed, cannot continue")
        exit(1)
    
    token = result["token"]
    
    print(f"\n=== Test 2: Create Task ===")
    test_create_task(token)
    
    print(f"\n=== Test 3: List Tasks ===")
    test_list_tasks(token)
    
    print("\n=== ALL TESTS PASSED ===")

