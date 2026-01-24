#!/usr/bin/env python3
"""
Database migration script to create all tables in Neon PostgreSQL
Run this once to initialize the database schema
"""

import os
import sys
from pathlib import Path

# Handle Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from sqlalchemy import text
from sqlmodel import SQLModel, create_engine
from src.models import User, Task, Conversation, Message

def migrate():
    """Create all tables in the database"""

    database_url = os.getenv("NEON_DATABASE_URL")

    if not database_url:
        print("[ERROR] NEON_DATABASE_URL not found in .env file")
        exit(1)

    print(f"[CONNECTING] Connecting to database...")
    print(f"   Database: {database_url.split('/')[-1]}")

    try:
        # Create engine
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
        )

        # Create all tables
        print("[CREATING] Creating tables...")
        SQLModel.metadata.create_all(engine)

        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()

            print("\n[SUCCESS] Migration successful! Created tables:")
            for row in tables:
                table_name = row[0]
                print(f"   [OK] {table_name}")

        print("\n[READY] Database is ready!")
        print("   You can now run: python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    migrate()
