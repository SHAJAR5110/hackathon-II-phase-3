#!/usr/bin/env python
"""
Simple Chat Endpoint Test
Tests the POST /api/{user_id}/chat endpoint
"""

import requests
import json
import time
from datetime import datetime, timedelta
from jose import jwt

BASE_URL = "http://localhost:8000"
SECRET_KEY = "test-secret-key-for-testing-only"  # From .env
ALGORITHM = "HS256"
USER_ID = "test_user_123"

def create_jwt_token(user_id: str) -> str:
    """Create a valid JWT token for testing"""
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_health():
    """Test health check"""
    print("\n[TEST 1] Health Check")
    print("-" * 50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return True
    return False

def test_chat_without_auth():
    """Test chat without auth (should return 401)"""
    print("\n[TEST 2] Chat Without Auth (expect 401)")
    print("-" * 50)

    payload = {"message": "hello"}
    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 401:
        print("[PASS] Correctly returned 401 Unauthorized")
        return True
    else:
        print(f"[FAIL] Expected 401, got {response.status_code}")
        return False

def test_chat_with_valid_auth():
    """Test chat with valid JWT token"""
    print("\n[TEST 3] Chat With Valid JWT Auth")
    print("-" * 50)

    token = create_jwt_token(USER_ID)
    print(f"Generated JWT token: {token[:50]}...")

    auth_header = {"Authorization": f"Bearer {token}"}
    payload = {"message": "Add a task to buy groceries"}

    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload,
        headers=auth_header
    )
    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        if response.status_code == 200:
            print("[PASS] Chat endpoint returned 200 OK")
            if "conversation_id" in data and "response" in data:
                print(f"[INFO] Conversation ID: {data['conversation_id']}")
                print(f"[INFO] Assistant response: {data['response'][:100]}...")
                return True, data.get("conversation_id")
        return False, None
    except Exception as e:
        print(f"[FAIL] Error parsing response: {e}")
        print(f"Raw response: {response.text}")
        return False, None

def test_chat_with_invalid_auth():
    """Test chat with invalid token (should return 401)"""
    print("\n[TEST 4] Chat With Invalid JWT Auth (expect 401)")
    print("-" * 50)

    auth_header = {"Authorization": "Bearer invalid_token_here"}
    payload = {"message": "hello"}

    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload,
        headers=auth_header
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 401:
        print("[PASS] Correctly returned 401 Unauthorized")
        return True
    else:
        print(f"[FAIL] Expected 401, got {response.status_code}")
        return False

def main():
    print("\n" + "="*50)
    print("Chat Endpoint Test Suite")
    print("="*50)

    try:
        # Wait for server
        print("\nWaiting for server...")
        time.sleep(2)

        results = []

        # Test 1: Health check
        results.append(("Health Check", test_health()))
        time.sleep(1)

        # Test 2: No auth (should fail)
        results.append(("Chat Without Auth", test_chat_without_auth()))
        time.sleep(1)

        # Test 3: Invalid auth (should fail)
        results.append(("Chat With Invalid Auth", test_chat_with_invalid_auth()))
        time.sleep(1)

        # Test 4: Valid auth
        success, conversation_id = test_chat_with_valid_auth()
        results.append(("Chat With Valid Auth", success))

        # Print summary
        print("\n" + "="*50)
        print("Test Summary")
        print("="*50)

        for test_name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {test_name}")

        passed = sum(1 for _, r in results if r)
        print(f"\nTotal: {passed}/{len(results)} tests passed")

        return all(r for _, r in results)

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
