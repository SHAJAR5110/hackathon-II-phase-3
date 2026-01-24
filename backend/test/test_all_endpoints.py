#!/usr/bin/env python3
"""
Comprehensive test of all backend API endpoints
"""
import httpx
import json
import time

BASE_URL = "http://localhost:8000"
EMAIL = f"testuser_{int(time.time())}@example.com"
PASSWORD = "TestPassword123!"
NAME = "Test User"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}\n")

def test_request(method, endpoint, data=None, headers=None):
    """Make HTTP request and print results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"{method} {endpoint}")

    try:
        if method == "GET":
            response = httpx.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = httpx.post(url, json=data, headers=headers, timeout=10)
        elif method == "PATCH":
            response = httpx.patch(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = httpx.delete(url, headers=headers, timeout=10)

        print(f"Status: {response.status_code}")

        try:
            result = response.json()
            print(f"Response:\n{json.dumps(result, indent=2)}")
            return result, response.status_code
        except:
            print(f"Response: {response.text}")
            return response.text, response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# Test 1: Health Check
print_section("TEST 1: Health Check")
test_request("GET", "/health")

# Test 2: Signup
print_section("TEST 2: User Signup")
signup_data = {
    "email": EMAIL,
    "password": PASSWORD,
    "name": NAME
}
result, status = test_request("POST", "/api/auth/signup", data=signup_data)

# Test 3: Signin
print_section("TEST 3: User Signin")
signin_data = {
    "email": EMAIL,
    "password": PASSWORD
}
result, status = test_request("POST", "/api/auth/signin", data=signin_data)

# Extract token for subsequent requests
token = None
if result and isinstance(result, dict) and "access_token" in result:
    token = result["access_token"]
    print(f"\nExtracted token: {token[:20]}...")
else:
    print("\nFailed to extract token!")

# Test 4: Get Current User
print_section("TEST 4: Get Current User")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    test_request("GET", "/api/users/me", headers=headers)
else:
    print("Skipped (no token)")

# Test 5: Create Task
print_section("TEST 5: Create Task (POST /api/tasks)")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    create_task_data = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }
    result, status = test_request("POST", "/api/tasks", data=create_task_data, headers=headers)
    task_id = None
    if result and isinstance(result, dict) and "id" in result:
        task_id = result["id"]
        print(f"\nCreated task ID: {task_id}")
else:
    print("Skipped (no token)")

# Test 6: List Tasks
print_section("TEST 6: List Tasks (GET /api/tasks)")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    result, status = test_request("GET", "/api/tasks", headers=headers)
else:
    print("Skipped (no token)")

# Test 7: Get Specific Task
print_section("TEST 7: Get Specific Task (GET /api/tasks/1)")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    test_request("GET", "/api/tasks/1", headers=headers)
else:
    print("Skipped (no token)")

# Test 8: Update Task
print_section("TEST 8: Update Task (PATCH /api/tasks/1)")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "title": "Buy groceries and fruits",
        "completed": True
    }
    test_request("PATCH", "/api/tasks/1", data=update_data, headers=headers)
else:
    print("Skipped (no token)")

# Test 9: Delete Task
print_section("TEST 9: Delete Task (DELETE /api/tasks/1)")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    test_request("DELETE", "/api/tasks/1", headers=headers)
else:
    print("Skipped (no token)")

# Test 10: List Tasks After Delete
print_section("TEST 10: List Tasks After Delete")
if token:
    headers = {"Authorization": f"Bearer {token}"}
    test_request("GET", "/api/tasks", headers=headers)
else:
    print("Skipped (no token)")

print("\n" + "="*70)
print(f"{'TEST SUMMARY':^70}")
print("="*70)
print("All endpoint tests completed!")
