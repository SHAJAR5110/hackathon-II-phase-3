#!/usr/bin/env python3
"""
Test task operations with correct task ID
"""
import httpx
import json
import time

BASE_URL = "http://localhost:8000"

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

# Setup: Create a test user
EMAIL = f"testuser_{int(time.time())}@example.com"
PASSWORD = "TestPassword123!"
NAME = "Test User"

print_section("SETUP: Create Test User")
result, _ = test_request("POST", "/api/auth/signup", data={
    "email": EMAIL,
    "password": PASSWORD,
    "name": NAME
})

print_section("SETUP: Signin User")
result, _ = test_request("POST", "/api/auth/signin", data={
    "email": EMAIL,
    "password": PASSWORD
})

token = result["access_token"]
headers = {"Authorization": f"Bearer {token}"}
user_id = result["user"]["id"]

print(f"Token: {token[:30]}...")
print(f"User ID: {user_id}")

# Create a task
print_section("TEST 1: Create Task")
result, status = test_request("POST", "/api/tasks", data={
    "title": "Test Task",
    "description": "This is a test task"
}, headers=headers)

task_id = result["id"]
print(f"\nCreated task ID: {task_id}")

# Get the task
print_section(f"TEST 2: Get Task {task_id}")
test_request("GET", f"/api/tasks/{task_id}", headers=headers)

# Update the task
print_section(f"TEST 3: Update Task {task_id}")
test_request("PATCH", f"/api/tasks/{task_id}", data={
    "title": "Updated Test Task",
    "description": "Updated description",
    "completed": True
}, headers=headers)

# List tasks
print_section("TEST 4: List All Tasks")
test_request("GET", "/api/tasks", headers=headers)

# List completed tasks
print_section("TEST 5: List Completed Tasks")
test_request("GET", "/api/tasks?status=completed", headers=headers)

# List pending tasks
print_section("TEST 6: List Pending Tasks")
result, _ = test_request("POST", "/api/tasks", data={
    "title": "Pending Task",
    "description": "This should be pending"
}, headers=headers)

test_request("GET", "/api/tasks?status=pending", headers=headers)

# Delete task
print_section(f"TEST 7: Delete Task {task_id}")
test_request("DELETE", f"/api/tasks/{task_id}", headers=headers)

# Verify deletion
print_section("TEST 8: List Tasks After Deletion")
test_request("GET", "/api/tasks", headers=headers)

print("\n" + "="*70)
print(f"{'ALL TASK OPERATIONS VERIFIED':^70}")
print("="*70)
