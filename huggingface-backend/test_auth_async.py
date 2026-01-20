"""
Async Test Script for Authentication Endpoints
Tests POST /auth/signup and POST /auth/signin using httpx async client.
"""

import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"


async def test_signup_valid():
    """Test signup with valid data"""
    print("\n" + "=" * 60)
    print("TEST 1: POST /auth/signup with valid data")
    print("=" * 60)

    payload = {
        "email": "asynctest@example.com",
        "password": "SecurePass123",
        "name": "Async Test User"
    }

    print(f"\nRequest payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/signup", json=payload)

    print(f"\nResponse status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    if response.status_code == 201:
        print("\n[PASS] SUCCESS: User created successfully")
        data = response.json()
        print(f"  - User ID: {data['user']['id']}")
        print(f"  - Email: {data['user']['email']}")
        print(f"  - Name: {data['user']['name']}")
        print(f"  - Token length: {len(data['token'])}")
        print(f"  - Expires in: {data['expires_in']} seconds")
        return True
    else:
        print(f"\n[FAIL] FAILED: Expected 201, got {response.status_code}")
        return False


async def test_signup_existing_email():
    """Test signup with existing email"""
    print("\n" + "=" * 60)
    print("TEST 2: POST /auth/signup with existing email (should return 409)")
    print("=" * 60)

    payload = {
        "email": "asynctest@example.com",
        "password": "SecurePass123",
        "name": "Async Test User"
    }

    print(f"\nRequest payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/signup", json=payload)

    print(f"\nResponse status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    if response.status_code == 409:
        print("\n[PASS] SUCCESS: Correctly rejected duplicate email")
        return True
    else:
        print(f"\n[FAIL] FAILED: Expected 409, got {response.status_code}")
        return False


async def test_signup_weak_password():
    """Test signup with weak password"""
    print("\n" + "=" * 60)
    print("TEST 3: POST /auth/signup with weak password (should return 400)")
    print("=" * 60)

    payload = {
        "email": "newasyncuser@example.com",
        "password": "weak",
        "name": "New Async User"
    }

    print(f"\nRequest payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/signup", json=payload)

    print(f"\nResponse status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    if response.status_code == 400:
        print("\n[PASS] SUCCESS: Correctly rejected weak password")
        return True
    else:
        print(f"\n[FAIL] FAILED: Expected 400, got {response.status_code}")
        return False


async def test_signin_valid():
    """Test signin with valid credentials"""
    print("\n" + "=" * 60)
    print("TEST 4: POST /auth/signin with valid credentials")
    print("=" * 60)

    payload = {
        "email": "asynctest@example.com",
        "password": "SecurePass123"
    }

    print(f"\nRequest payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/signin", json=payload)

    print(f"\nResponse status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    if response.status_code == 200:
        print("\n[PASS] SUCCESS: User authenticated successfully")
        data = response.json()
        print(f"  - User ID: {data['user']['id']}")
        print(f"  - Email: {data['user']['email']}")
        print(f"  - Name: {data['user']['name']}")
        print(f"  - Token length: {len(data['token'])}")
        print(f"  - Expires in: {data['expires_in']} seconds")
        return True
    else:
        print(f"\n[FAIL] FAILED: Expected 200, got {response.status_code}")
        return False


async def test_signin_wrong_password():
    """Test signin with wrong password"""
    print("\n" + "=" * 60)
    print("TEST 5: POST /auth/signin with wrong password (should return 401)")
    print("=" * 60)

    payload = {
        "email": "asynctest@example.com",
        "password": "WrongPassword123"
    }

    print(f"\nRequest payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/signin", json=payload)

    print(f"\nResponse status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    if response.status_code == 401:
        print("\n[PASS] SUCCESS: Correctly rejected wrong password")
        return True
    else:
        print(f"\n[FAIL] FAILED: Expected 401, got {response.status_code}")
        return False


async def test_signin_nonexistent_user():
    """Test signin with non-existent user"""
    print("\n" + "=" * 60)
    print("TEST 6: POST /auth/signin with non-existent email (should return 401)")
    print("=" * 60)

    payload = {
        "email": "nonexistent@example.com",
        "password": "SecurePass123"
    }

    print(f"\nRequest payload: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/signin", json=payload)

    print(f"\nResponse status code: {response.status_code}")
    print(f"Response body: {response.json()}")

    if response.status_code == 401:
        print("\n[PASS] SUCCESS: Correctly rejected non-existent user")
        return True
    else:
        print(f"\n[FAIL] FAILED: Expected 401, got {response.status_code}")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print(" " * 10 + "AUTHENTICATION ENDPOINTS TEST SUITE")
    print("=" * 60)
    print("\nMake sure the FastAPI server is running on http://localhost:8000")
    print("Run: uvicorn main:app --reload")

    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=2.0)
            if response.status_code != 200:
                print("\n[ERROR] Server is not responding correctly")
                print("Please start the server first: uvicorn main:app --reload")
                return 1
    except Exception as e:
        print(f"\n[ERROR] Cannot connect to server: {e}")
        print("Please start the server first: uvicorn main:app --reload")
        return 1

    print("\n[OK] Server is running\n")

    results = []

    # Run tests
    results.append(("Signup with valid data", await test_signup_valid()))
    results.append(("Signup with existing email", await test_signup_existing_email()))
    results.append(("Signup with weak password", await test_signup_weak_password()))
    results.append(("Signin with valid credentials", await test_signin_valid()))
    results.append(("Signin with wrong password", await test_signin_wrong_password()))
    results.append(("Signin with non-existent user", await test_signin_nonexistent_user()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "[+]" if result else "[-]"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed successfully!")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
