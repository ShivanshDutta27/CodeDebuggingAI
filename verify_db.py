"""Database verification and setup script for Fixie AI Debugger.

Usage:
    python verify_db.py            # Test connection & inspect database status
    python verify_db.py --init     # Initialize database and tables
    python verify_db.py --test-all # Full test: verify connection, init, and test CRUD
"""

import sys
import argparse
from database.config import get_db_config
from database.service import DatabaseService
from database.connection import test_connection


def mask_password(pwd: str) -> str:
    if not pwd:
        return "<empty>"
    return "*" * len(pwd)


def main():
    parser = argparse.ArgumentParser(description="Fixie MySQL Database Verification Tool")
    parser.add_argument("--init", action="store_true", help="Initialize database schema and tables")
    parser.add_argument("--test-all", action="store_true", help="Run full diagnostic and CRUD roundtrip test")
    args = parser.parse_args()

    cfg = get_db_config()

    print("=" * 60)
    print("Fixie AI Debugger - Database Verification")
    print("=" * 60)
    print("Current Configuration (from environment / .env):")
    print(f"  DB_HOST:            {cfg.host}")
    print(f"  DB_PORT:            {cfg.port}")
    print(f"  DB_USER:            {cfg.user}")
    print(f"  DB_PASSWORD:        {mask_password(cfg.password)}")
    print(f"  DB_NAME:            {cfg.database}")
    print(f"  DB_CONNECT_TIMEOUT: {cfg.connect_timeout}s")
    print("-" * 60)

    service = DatabaseService(config=cfg)

    # Step 1: Health Check
    print("1. Testing MySQL Server Connectivity...")
    is_ok, msg = service.check_connection()
    if not is_ok:
        print(f"❌ Connection Failed: {msg}")
        print("\nTroubleshooting tips:")
        print("  1. Ensure MySQL server is running (e.g. net start MySQL80)")
        print("  2. Verify DB_HOST, DB_PORT, DB_USER, and DB_PASSWORD in your .env file")
        print("  3. Refer to .env.example for configuration details")
        sys.exit(1)

    print(f"✅ Connection Successful: {msg}")

    # Step 2: Initialize schema if requested or --test-all
    if args.init or args.test_all:
        print("\n2. Initializing Database Schema & Tables...")
        try:
            service.init_db()
            print(f"✅ Schema initialized: Database '{cfg.database}' and table 'debugging_sessions' are ready.")
        except Exception as e:
            print(f"❌ Schema Initialization Failed: {e}")
            sys.exit(1)

    # Step 3: Test CRUD operations if requested
    if args.test_all:
        print("\n3. Testing Session CRUD Roundtrip...")
        test_code = 'def divide(a, b):\n    return a / b\nprint(divide(10, 0))'
        test_error = "ZeroDivisionError: division by zero at line 3"
        try:
            created = service.create_session(
                original_code=test_code,
                language="python",
                error_description=test_error
            )
            print(f"✅ Created session with ID: {created.id} at {created.created_at}")

            fetched = service.get_session(created.id)
            if fetched and fetched.original_code == test_code:
                print(f"✅ Successfully retrieved session {fetched.id} from MySQL.")
            else:
                print(f"❌ Verification failed: Fetched data does not match.")
                sys.exit(1)

            sessions = service.list_sessions(limit=5)
            print(f"✅ Total recent sessions listed: {len(sessions)}")
        except Exception as e:
            print(f"❌ CRUD Test Failed: {e}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Database check completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
