#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
Run this before deployment to catch import errors early
"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    errors = []
    
    print("=" * 60)
    print("Testing RestoBot App Imports")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {sys.path[0]}")
    print()
    
    # Test 1: Core imports
    tests = [
        ("app.core.config", "from app.core.config import settings"),
        ("app.core.database", "from app.core.database import Base, engine, SessionLocal"),
        ("app.core.security", "from app.core.security import get_password_hash, verify_password"),
        ("app.api", "from app.api import router as api_router"),
        ("app.api.v1", "from app.api.v1 import api_router as api_v1_router"),
        ("app.api.v1.auth", "from app.api.v1.auth import router as auth_router"),
        ("app.api.v1.users", "from app.api.v1.users import router as users_router"),
        ("app.api.v1.menu", "from app.api.v1.menu import router as menu_router"),
        ("app.api.v1.orders", "from app.api.v1.orders import router as orders_router"),
        ("app.api.v1.tables", "from app.api.v1.tables import router as tables_router"),
        ("app.core.database", "from app.core.database import Base"),
        ("app.schemas", "from app.schemas import UserCreate"),
        ("app.main", "from app.main import app"),
    ]
    
    for test_name, import_statement in tests:
        try:
            print(f"Testing {test_name}...", end=" ")
            exec(import_statement)
            print("✓ OK")
        except Exception as e:
            error_msg = str(e)
            print(f"✗ FAILED")
            errors.append({
                'test': test_name,
                'statement': import_statement,
                'error': error_msg
            })
            traceback.print_exc()
    
    print()
    print("=" * 60)
    
    if errors:
        print(f"FAILED: {len(errors)} import(s) failed")
        print()
        for error in errors:
            print(f"❌ {error['test']}")
            print(f"   Statement: {error['statement']}")
            print(f"   Error: {error['error']}")
            print()
        return False
    else:
        print("SUCCESS: All imports passed!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
