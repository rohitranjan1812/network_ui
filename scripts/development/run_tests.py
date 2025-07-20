#!/usr/bin/env python3
"""
Comprehensive test runner for the Data Model Import module.
This script runs all tests and provides detailed reporting.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Duration: {duration:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  STDERR:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, "", str(e)


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pandas',
        'numpy',
        'flask',
        'flask-cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    return True


def check_test_files():
    """Check if required test files exist."""
    print("\n🔍 Checking test files...")
    
    required_files = [
        'test_data.csv',
        'test_edges.csv',
        'test_data_json.json',
        'test_data_xml.xml',
        'test_data_invalid.csv',
        'test_data_empty.csv',
        'test_data_duplicates.csv'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing test files: {', '.join(missing_files)}")
        return False
    
    return True


def run_unit_tests():
    """Run unit tests."""
    return run_command(
        "python -m pytest tests/ -v --tb=short --cov=data_model_import --cov-report=term-missing",
        "Running Unit Tests"
    )


def run_integration_tests():
    """Run integration tests."""
    return run_command(
        "python -m pytest tests/ -v -m integration --tb=short",
        "Running Integration Tests"
    )


def run_specific_test_file(test_file):
    """Run tests from a specific file."""
    return run_command(
        f"python -m pytest {test_file} -v --tb=short",
        f"Running Tests from {test_file}"
    )


def run_coverage_report():
    """Generate detailed coverage report."""
    return run_command(
        "python -m pytest tests/ --cov=data_model_import --cov-report=html --cov-report=xml --cov-report=term-missing",
        "Generating Coverage Report"
    )


def run_functional_tests():
    """Run functional tests using the demo script."""
    return run_command(
        "python demo.py",
        "Running Functional Tests (Demo)"
    )


def run_api_tests():
    """Run API tests."""
    # Start the Flask server in background
    print("\n🚀 Starting Flask server for API tests...")
    server_process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Run API tests
        success, stdout, stderr = run_command(
            "python -m pytest tests/test_api.py -v --tb=short",
            "Running API Tests"
        )
        
        return success, stdout, stderr
        
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()


def run_performance_tests():
    """Run performance tests."""
    return run_command(
        "python -m pytest tests/ -v -m slow --tb=short",
        "Running Performance Tests"
    )


def run_linting():
    """Run code linting."""
    return run_command(
        "python -m flake8 data_model_import/ tests/ --max-line-length=120 --ignore=E501,W503",
        "Running Code Linting"
    )


def run_type_checking():
    """Run type checking."""
    return run_command(
        "python -m mypy data_model_import/ --ignore-missing-imports",
        "Running Type Checking"
    )


def generate_test_report(results):
    """Generate a test report."""
    print("\n" + "="*80)
    print("📊 TEST REPORT")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for success, _, _ in results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Categories: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ Failed Tests:")
        for i, (success, stdout, stderr) in enumerate(results):
            if not success:
                print(f"  {i+1}. Test category failed")
                if stderr:
                    print(f"     Error: {stderr[:200]}...")
    
    print("\n" + "="*80)


def main():
    """Main test runner function."""
    print("🧪 Data Model Import - Comprehensive Test Suite")
    print("="*80)
    
    # Check prerequisites
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        sys.exit(1)
    
    if not check_test_files():
        print("\n❌ Test files check failed. Please ensure all test files exist.")
        sys.exit(1)
    
    # Run different types of tests
    test_results = []
    
    # Unit tests
    success, stdout, stderr = run_unit_tests()
    test_results.append((success, stdout, stderr))
    
    # Integration tests
    success, stdout, stderr = run_integration_tests()
    test_results.append((success, stdout, stderr))
    
    # Functional tests
    success, stdout, stderr = run_functional_tests()
    test_results.append((success, stdout, stderr))
    
    # Coverage report
    success, stdout, stderr = run_coverage_report()
    test_results.append((success, stdout, stderr))
    
    # Code quality checks
    success, stdout, stderr = run_linting()
    test_results.append((success, stdout, stderr))
    
    success, stdout, stderr = run_type_checking()
    test_results.append((success, stdout, stderr))
    
    # Generate report
    generate_test_report(test_results)
    
    # Determine overall success
    overall_success = all(success for success, _, _ in test_results)
    
    if overall_success:
        print("\n🎉 All tests passed! The module is ready for production.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    # Check if specific test file is provided
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if os.path.exists(test_file):
            print(f"🧪 Running specific test file: {test_file}")
            success, stdout, stderr = run_specific_test_file(test_file)
            if success:
                print("\n✅ Test file passed!")
                sys.exit(0)
            else:
                print("\n❌ Test file failed!")
                sys.exit(1)
        else:
            print(f"❌ Test file not found: {test_file}")
            sys.exit(1)
    else:
        main() 