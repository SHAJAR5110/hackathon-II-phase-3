"""Quick test to diagnose 500 error on signup"""
import asyncio
import sys
import os
sys.path.insert(0, '.')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

async def test():
    from src.db import engine, async_session_maker, init_db
    from sqlmodel import text
    
    # Test 1: DB connection
    print("=== Test 1: Database connection ===")
    try:
        async with async_session_maker() as session:
            result = await session.execute(text('SELECT 1'))
            print(f"DB query result: {result.scalar()}")
    except Exception as e:
        print(f"DB connection error: {type(e).__name__}: {e}")
        return
    
    # Test 2: init_db (create tables)
    print("\n=== Test 2: Init DB (create tables) ===")
    try:
        await init_db()
        print("init_db succeeded")
    except Exception as e:
        print(f"init_db error: {type(e).__name__}: {e}")
    
    # Test 3: Signup
    print("\n=== Test 3: Signup ===")
    try:
        from src.models import SignupRequest
        from src.services.auth_service import AuthService
        
        signup_data = SignupRequest(
            email="quicktest@example.com",
            password="TestPass123",
            name="Quick Test"
        )
        
        async with async_session_maker() as session:
            result = await AuthService.signup(session, signup_data)
            print(f"Signup result: {result}")
    except Exception as e:
        import traceback
        print(f"Signup error: {type(e).__name__}: {e}")
        traceback.print_exc()

asyncio.run(test())
