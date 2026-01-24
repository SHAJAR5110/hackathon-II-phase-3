#!/usr/bin/env python
"""
Comprehensive Chat Endpoint Tests
Tests the complete chat flow with authentication, database, and MCP tools
"""

import json
from datetime import datetime, timedelta
from jose import jwt
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.db import SessionLocal
from backend.src.models import User, Task, Conversation

# Test configuration
SECRET_KEY = "test-secret-key-for-testing-only"  # From .env
ALGORITHM = "HS256"
USER_ID = "test_user_comprehensive"
EMAIL = f"{USER_ID}@test.com"

client = TestClient(app)


def create_jwt_token(user_id: str) -> str:
    """Create a valid JWT token for testing"""
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def setup_test_user():
    """Create a test user in the database"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.user_id == USER_ID).first()
        if existing_user:
            db.delete(existing_user)
            db.commit()

        # Create new user
        user = User(
            user_id=USER_ID,
            email=EMAIL,
            name="Test User",
            hashed_password="hashed_password_here"
        )
        db.add(user)
        db.commit()
        print(f"[INFO] Created test user: {USER_ID}")
        return user
    except Exception as e:
        print(f"[ERROR] Failed to create test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_test_user():
    """Clean up test user and related data"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == USER_ID).first()
        if user:
            # Delete all related data
            db.query(Task).filter(Task.user_id == USER_ID).delete()
            db.query(Conversation).filter(Conversation.user_id == USER_ID).delete()
            db.delete(user)
            db.commit()
            print(f"[INFO] Cleaned up test user: {USER_ID}")
    except Exception as e:
        print(f"[ERROR] Failed to cleanup test user: {e}")
        db.rollback()
    finally:
        db.close()


def test_health_check():
    """Test health endpoint"""
    print("\n[TEST 1] Health Check Endpoint")
    print("-" * 60)

    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    print("[PASS] Server is healthy")
    return True


def test_root_endpoint():
    """Test root endpoint"""
    print("\n[TEST 2] Root Endpoint")
    print("-" * 60)

    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    print(f"[PASS] API endpoints: {list(data['endpoints'].keys())}")
    return True


def test_chat_without_auth():
    """Test chat without authentication"""
    print("\n[TEST 3] Chat Without Authentication (expect 401)")
    print("-" * 60)

    payload = {"message": "Add a task"}
    response = client.post(f"/api/{USER_ID}/chat", json=payload)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    data = response.json()
    assert "detail" in data or "error" in data
    print("[PASS] Correctly returned 401 Unauthorized")
    return True


def test_chat_with_invalid_token():
    """Test chat with invalid token"""
    print("\n[TEST 4] Chat With Invalid Token (expect 401)")
    print("-" * 60)

    headers = {"Authorization": "Bearer invalid_token_here"}
    payload = {"message": "hello"}
    response = client.post(
        f"/api/{USER_ID}/chat",
        json=payload,
        headers=headers
    )

    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("[PASS] Correctly returned 401 for invalid token")
    return True


def test_chat_with_valid_token():
    """Test chat with valid JWT token"""
    print("\n[TEST 5] Chat With Valid JWT Token")
    print("-" * 60)

    token = create_jwt_token(USER_ID)
    print(f"[INFO] Generated token for user: {USER_ID}")

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": "Add a task to buy groceries with eggs and milk"}

    response = client.post(
        f"/api/{USER_ID}/chat",
        json=payload,
        headers=headers
    )

    print(f"[INFO] Response status: {response.status_code}")

    if response.status_code != 200:
        print(f"[ERROR] Expected 200, got {response.status_code}")
        print(f"[ERROR] Response: {response.text[:500]}")
        return False

    data = response.json()
    print(f"[INFO] Response: {json.dumps(data, indent=2)[:200]}...")

    assert "conversation_id" in data, "Missing conversation_id"
    assert "response" in data, "Missing response"
    assert isinstance(data["conversation_id"], int)
    assert isinstance(data["response"], str)

    print(f"[PASS] Chat endpoint working")
    print(f"[INFO] Conversation ID: {data['conversation_id']}")
    print(f"[INFO] Assistant response: {data['response'][:80]}...")

    return True, data.get("conversation_id")


def test_list_tasks_in_conversation(conversation_id: int):
    """Test listing tasks in the same conversation"""
    print("\n[TEST 6] List Tasks in Same Conversation")
    print("-" * 60)

    token = create_jwt_token(USER_ID)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "conversation_id": conversation_id,
        "message": "Show me all my tasks"
    }

    response = client.post(
        f"/api/{USER_ID}/chat",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        print(f"[ERROR] Expected 200, got {response.status_code}")
        print(f"[ERROR] Response: {response.text[:500]}")
        return False

    data = response.json()
    assert data["conversation_id"] == conversation_id, "Conversation ID mismatch"
    print(f"[PASS] Listed tasks in conversation {conversation_id}")
    print(f"[INFO] Response: {data['response'][:80]}...")

    return True


def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "="*60)
    print("Chat Endpoint Comprehensive Test Suite")
    print("="*60)

    results = []

    try:
        # Setup test user
        setup_test_user()

        # Test 1: Health check
        try:
            results.append(("Health Check", test_health_check()))
        except Exception as e:
            print(f"[FAIL] {e}")
            results.append(("Health Check", False))

        # Test 2: Root endpoint
        try:
            results.append(("Root Endpoint", test_root_endpoint()))
        except Exception as e:
            print(f"[FAIL] {e}")
            results.append(("Root Endpoint", False))

        # Test 3: No auth
        try:
            results.append(("Chat Without Auth", test_chat_without_auth()))
        except Exception as e:
            print(f"[FAIL] {e}")
            results.append(("Chat Without Auth", False))

        # Test 4: Invalid token
        try:
            results.append(("Chat With Invalid Token", test_chat_with_invalid_token()))
        except Exception as e:
            print(f"[FAIL] {e}")
            results.append(("Chat With Invalid Token", False))

        # Test 5: Valid token
        try:
            result = test_chat_with_valid_token()
            if isinstance(result, tuple):
                success, conversation_id = result
                results.append(("Chat With Valid Token", success))

                # Test 6: List tasks (only if test 5 passed)
                if success and conversation_id:
                    try:
                        results.append(("List Tasks", test_list_tasks_in_conversation(conversation_id)))
                    except Exception as e:
                        print(f"[FAIL] {e}")
                        results.append(("List Tasks", False))
            else:
                results.append(("Chat With Valid Token", result))
        except Exception as e:
            print(f"[FAIL] {e}")
            results.append(("Chat With Valid Token", False))

    finally:
        # Cleanup
        cleanup_test_user()

    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed\n")

    return all(r for _, r in results)


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
