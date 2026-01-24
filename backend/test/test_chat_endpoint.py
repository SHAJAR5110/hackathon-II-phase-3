#!/usr/bin/env python
"""
Test script for Chat Endpoint
Tests the POST /api/{user_id}/chat endpoint with various scenarios
"""

import requests
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

# Test user auth header
AUTH_HEADER = {"Authorization": f"Bearer {USER_ID}"}

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check Endpoint")
    print("="*70)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Root Endpoint")
    print("="*70)

    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat_without_auth():
    """Test chat endpoint without authentication"""
    print("\n" + "="*70)
    print("TEST 3: Chat Without Authentication (Should Fail)")
    print("="*70)

    payload = {
        "message": "Add a task to buy groceries"
    }

    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401

def test_chat_with_auth_new_conversation():
    """Test chat endpoint with authentication (new conversation)"""
    print("\n" + "="*70)
    print("TEST 4: Chat With Auth - New Conversation")
    print("="*70)

    payload = {
        "message": "Add a task to buy groceries with milk and eggs"
    }

    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload,
        headers=AUTH_HEADER
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data, response.status_code
    else:
        print(f"Error: {response.text}")
        return None, response.status_code

def test_chat_list_tasks(conversation_id: Optional[int] = None):
    """Test listing tasks"""
    print("\n" + "="*70)
    print("TEST 5: Chat - List Tasks")
    print("="*70)

    payload = {
        "message": "Show me all my tasks"
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id

    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload,
        headers=AUTH_HEADER
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data, response.status_code
    else:
        print(f"Error: {response.text}")
        return None, response.status_code

def test_invalid_message():
    """Test with invalid message"""
    print("\n" + "="*70)
    print("TEST 6: Invalid Message (Empty)")
    print("="*70)

    payload = {
        "message": ""
    }

    response = requests.post(
        f"{BASE_URL}/api/{USER_ID}/chat",
        json=payload,
        headers=AUTH_HEADER
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 422  # Validation error

def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "="*70)
    print("=" + " "*68 + "=")
    print("=" + "  CHATBOT API TEST SUITE".center(68) + "=")
    print("=" + " "*68 + "=")
    print("="*70)

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    time.sleep(1)

    # Test 2: Root endpoint
    results.append(("Root Endpoint", test_root_endpoint()))
    time.sleep(1)

    # Test 3: Chat without auth (should fail)
    results.append(("Chat Without Auth", test_chat_without_auth()))
    time.sleep(1)

    # Test 4: Chat with auth - new conversation
    response_4, status_4 = test_chat_with_auth_new_conversation()
    results.append(("Chat With Auth (New Conv)", status_4 == 200))

    if response_4 and "conversation_id" in response_4:
        conversation_id = response_4["conversation_id"]
        time.sleep(1)

        # Test 5: List tasks in same conversation
        response_5, status_5 = test_chat_list_tasks(conversation_id)
        results.append(("List Tasks in Conversation", status_5 == 200))
    else:
        results.append(("List Tasks in Conversation", False))

    time.sleep(1)

    # Test 6: Invalid message
    results.append(("Invalid Message Validation", test_invalid_message()))

    # Print summary
    print("\n" + "="*70)
    print("=" + " "*68 + "=")
    print("=" + "  TEST SUMMARY".center(68) + "=")
    print("=" + " "*68 + "=")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} | {test_name}")

    print("\n" + "-"*70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("-"*70 + "\n")

    return passed == total

if __name__ == "__main__":
    try:
        print("Waiting for server to be ready...")
        time.sleep(2)

        success = run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
