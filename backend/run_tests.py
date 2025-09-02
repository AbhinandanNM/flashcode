#!/usr/bin/env python3
"""
Comprehensive test runner for CodeCrafts MVP backend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed!")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main test runner"""
    print("CodeCrafts MVP - Comprehensive Test Suite")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Test commands to run
    test_commands = [
        {
            "command": "python -m pytest test_auth.py -v --tb=short",
            "description": "Authentication Tests"
        },
        {
            "command": "python -m pytest test_lessons.py -v --tb=short",
            "description": "Lesson Service Tests"
        },
        {
            "command": "python -m pytest test_questions.py -v --tb=short",
            "description": "Question Service Tests"
        },
        {
            "command": "python -m pytest test_code_execution.py -v --tb=short",
            "description": "Code Execution Tests"
        },
        {
            "command": "python -m pytest test_duels.py -v --tb=short",
            "description": "Duel System Tests"
        },
        {
            "command": "python -m pytest test_api_endpoints.py -v --tb=short",
            "description": "API Endpoint Tests"
        },
        {
            "command": "python -m pytest test_database_integration.py -v --tb=short",
            "description": "Database Integration Tests"
        },
        {
            "command": "python -m pytest test_integration.py -v --tb=short",
            "description": "Full Integration Tests"
        },
        {
            "command": "python -m pytest test_models.py -v --tb=short",
            "description": "Database Model Tests"
        }
    ]
    
    # Run individual test suites
    passed_tests = 0
    failed_tests = 0
    
    for test in test_commands:
        if run_command(test["command"], test["description"]):
            passed_tests += 1
        else:
            failed_tests += 1
    
    # Run comprehensive test suite with coverage
    print(f"\n{'='*60}")
    print("Running comprehensive test suite with coverage...")
    print(f"{'='*60}")
    
    coverage_command = (
        "python -m pytest "
        "--cov=. "
        "--cov-report=html "
        "--cov-report=term-missing "
        "--cov-report=xml "
        "-v "
        "--tb=short "
        "test_*.py"
    )
    
    if run_command(coverage_command, "Full Test Suite with Coverage"):
        print("\n✅ Coverage report generated in htmlcov/index.html")
    
    # Performance tests
    print(f"\n{'='*60}")
    print("Running performance tests...")
    print(f"{'='*60}")
    
    perf_command = "python -m pytest test_database_integration.py::TestDatabasePerformance -v"
    run_command(perf_command, "Performance Tests")
    
    # Security tests (if any)
    print(f"\n{'='*60}")
    print("Running security tests...")
    print(f"{'='*60}")
    
    security_command = "python -m pytest test_api_endpoints.py::TestErrorHandling -v"
    run_command(security_command, "Security & Error Handling Tests")
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed test suites: {passed_tests}")
    print(f"❌ Failed test suites: {failed_tests}")
    print(f"📊 Total test suites: {passed_tests + failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! The application is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())