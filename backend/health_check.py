#!/usr/bin/env python3
"""
Health check script for SME Financial Health Platform
"""

import sys
import os
import requests
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def check_database():
    """Check if database connection works"""
    try:
        from database import engine
        with engine.connect() as conn:
            print("✅ Database connection: OK")
            return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Environment variables missing: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Environment variables: OK")
        return True

def check_api_server(port=8000, timeout=5):
    """Check if API server is responding"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        if response.status_code == 200:
            print("✅ API server: OK")
            return True
        else:
            print(f"❌ API server: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API server: Not responding - {e}")
        return False

def main():
    """Run all health checks"""
    print("🏥 SME Financial Health Platform - Health Check")
    print("=" * 50)
    
    checks = [
        ("Database", check_database),
        ("Environment", check_environment),
    ]
    
    # Check if we should test the API server
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        checks.append(("API Server", check_api_server))
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if check_func():
            passed += 1
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"Health Check Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All checks passed! System is healthy.")
        sys.exit(0)
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()