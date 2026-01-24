#!/usr/bin/env python3
"""
Comprehensive test for delete_task and session persistence issues
Tests:
1. Signup and login
2. Create task
3. Delete task via chat endpoint
4. List tasks (verify deletion)
5. Session persistence after "page refresh"
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test_delete@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test Delete User"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def log_info(text):
    print(f"{Colors.CYAN}[INFO]{Colors.END} {text}")

def log_success(text):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {text}")

def log_error(text):
    print(f"{Colors.RED}[ERROR]{Colors.END} {text}")

def log_warning(text):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {text}")

def test_signup():
    """Test user signup"""
    log_header("Step 1: User Signup")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": TEST_NAME,
            },
            timeout=10
        )

        log_info(f"POST /api/auth/signup")
        log_info(f"Status: {response.status_code}")

        if response.status_code == 201:
            log_success("User signup successful")
            return True
        else:
            # User might already exist from previous test
            if response.status_code == 400 and "already registered" in response.text.lower():
                log_warning("User already exists (from previous test)")
                return True
            log_error(f"Signup failed: {response.json()}")
            return False

    except Exception as e:
        log_error(f"Signup failed: {str(e)}")
        return False

def test_signin():
    """Test user signin and get token"""
    log_header("Step 2: User Signin")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signin",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
            timeout=10
        )

        log_info(f"POST /api/auth/signin")
        log_info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")

            log_success(f"User signin successful")
            log_info(f"User ID: {user_id}")
            log_info(f"Token received: {bool(token)}")

            return token, user_id
        else:
            log_error(f"Signin failed: {response.json()}")
            return None, None

    except Exception as e:
        log_error(f"Signin failed: {str(e)}")
        return None, None

def test_create_task(token, user_id):
    """Create a test task"""
    log_header("Step 3: Create Task via REST API")

    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            json={
                "title": "Meeting with Shajar",
                "description": "Discuss project status",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        log_info(f"POST /api/tasks")
        log_info(f"Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.json()
            task_id = data.get("id")
            task_title = data.get("title")

            log_success(f"Task created successfully")
            log_info(f"Task ID: {task_id}")
            log_info(f"Task Title: {task_title}")

            return task_id, task_title
        else:
            log_error(f"Task creation failed: {response.json()}")
            return None, None

    except Exception as e:
        log_error(f"Task creation failed: {str(e)}")
        return None, None

def test_chat_delete(token, user_id):
    """Test delete via chat endpoint"""
    log_header("Step 4: Delete Task via Chat Endpoint")

    try:
        # First chat to delete the task
        response = requests.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={
                "message": "Delete the Meeting with Shajar task",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )

        log_info(f"POST /api/{user_id}/chat")
        log_info(f"Message: 'Delete the Meeting with Shajar task'")
        log_info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            chat_response = data.get("response", "")
            tool_calls = data.get("tool_calls", [])
            conversation_id = data.get("conversation_id")

            log_success(f"Chat completed successfully")
            log_info(f"Conversation ID: {conversation_id}")
            log_info(f"Assistant Response: {chat_response[:100]}...")
            log_info(f"Tools Called: {len(tool_calls)}")

            for tool in tool_calls:
                log_info(f"  - {tool.get('tool')}: {tool.get('params')}")

            # Check if delete_task was called
            delete_called = any(t.get("tool") == "delete_task" for t in tool_calls)
            if delete_called:
                log_success("delete_task tool was invoked")
            else:
                log_warning("delete_task tool was NOT invoked")

            return conversation_id, chat_response, delete_called
        else:
            log_error(f"Chat failed: {response.json()}")
            return None, None, False

    except Exception as e:
        log_error(f"Chat failed: {str(e)}")
        return None, None, False

def test_list_tasks(token, user_id):
    """List tasks to verify deletion"""
    log_header("Step 5: List Tasks (Verify Deletion)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        log_info(f"GET /api/tasks")
        log_info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            tasks = data.get("tasks", [])

            log_success(f"Retrieved {len(tasks)} tasks")

            # Check if "Meeting" task still exists
            meeting_task = None
            for task in tasks:
                if "meeting" in task.get("title", "").lower():
                    meeting_task = task
                    break

            if meeting_task:
                log_error(f"PROBLEM: 'Meeting' task still exists after deletion!")
                log_info(f"  Task ID: {meeting_task.get('id')}")
                log_info(f"  Task Title: {meeting_task.get('title')}")
                log_info(f"  Completed: {meeting_task.get('completed')}")
                return False
            else:
                log_success("'Meeting' task was successfully deleted")
                return True
        else:
            log_error(f"Task list failed: {response.json()}")
            return False

    except Exception as e:
        log_error(f"Task list failed: {str(e)}")
        return False

def test_session_persistence(token, user_id):
    """Test if session persists (simulating page refresh)"""
    log_header("Step 6: Test Session Persistence (Simulate Page Refresh)")

    try:
        # This simulates what the frontend auth-context does on page load
        response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        log_info(f"GET /api/users/me (Simulating page refresh)")
        log_info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            log_success("Session validation successful")
            log_info(f"User ID: {data.get('id')}")
            log_info(f"Email: {data.get('email')}")
            log_info(f"Name: {data.get('name')}")
            return True
        elif response.status_code == 401:
            log_error("Session validation failed (401 Unauthorized)")
            log_error("This is why users are redirected to login on page refresh!")
            return False
        else:
            log_error(f"Session validation failed: {response.status_code}")
            log_error(f"Response: {response.json()}")
            return False

    except Exception as e:
        log_error(f"Session validation failed: {str(e)}")
        return False

def test_chat_list_tasks(token, user_id):
    """Test listing tasks via chat to check if agent sees the deletion"""
    log_header("Step 7: List Tasks via Chat (Agent's View)")

    try:
        response = requests.post(
            f"{BASE_URL}/api/{user_id}/chat",
            json={
                "message": "Show me all my tasks",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )

        log_info(f"POST /api/{user_id}/chat")
        log_info(f"Message: 'Show me all my tasks'")
        log_info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            chat_response = data.get("response", "")

            log_success(f"Chat completed successfully")
            log_info(f"Assistant Response:\n{chat_response}")

            # Check if the deleted task is mentioned
            if "meeting" in chat_response.lower():
                log_error("PROBLEM: Agent still sees the 'Meeting' task after deletion!")
                return False
            else:
                log_success("Agent correctly does not show the deleted task")
                return True
        else:
            log_error(f"Chat failed: {response.json()}")
            return False

    except Exception as e:
        log_error(f"Chat failed: {str(e)}")
        return False

def main():
    log_header("Testing Delete Task and Session Persistence")
    log_info(f"Timestamp: {datetime.now().isoformat()}")
    log_info(f"Test User: {TEST_EMAIL}")
    log_info(f"Base URL: {BASE_URL}")

    # Test 1: Signup
    if not test_signup():
        log_error("Signup failed, cannot continue")
        return

    # Test 2: Signin
    token, user_id = test_signin()
    if not token or not user_id:
        log_error("Signin failed, cannot continue")
        return

    # Test 3: Create task
    task_id, task_title = test_create_task(token, user_id)
    if not task_id:
        log_error("Task creation failed, cannot continue")
        return

    # Small delay to ensure DB is updated
    time.sleep(1)

    # Test 4: Delete via chat
    conv_id, assistant_msg, delete_called = test_chat_delete(token, user_id)
    if not delete_called:
        log_error("Delete was not called by the agent, cannot continue with meaningful test")

    # Small delay to ensure DB is updated
    time.sleep(1)

    # Test 5: List tasks to verify deletion
    deletion_verified = test_list_tasks(token, user_id)

    # Test 6: Session persistence
    session_ok = test_session_persistence(token, user_id)

    # Test 7: Chat list tasks
    agent_sees_deletion = test_chat_list_tasks(token, user_id)

    # Summary
    log_header("Test Summary")
    print(f"{Colors.BOLD}Delete Verification:{Colors.END} {'PASS' if deletion_verified else 'FAIL'}")
    print(f"{Colors.BOLD}Session Persistence:{Colors.END} {'PASS' if session_ok else 'FAIL'}")
    print(f"{Colors.BOLD}Agent Sees Deletion:{Colors.END} {'PASS' if agent_sees_deletion else 'FAIL'}")

    if deletion_verified and session_ok and agent_sees_deletion:
        log_success("\nAll tests PASSED!")
    else:
        log_error("\nSome tests FAILED. See details above.")

if __name__ == "__main__":
    main()
