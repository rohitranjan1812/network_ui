#!/usr/bin/env python3
"""
Comprehensive Test Runner for Network UI Platform
Executes all test categories including advanced edge cases, stress tests, and performance benchmarks.
"""

import subprocess
import sys
import time
import os
from datetime import datetime


def run_command(command, description, timeout=300):
    """Run a command and return results."""
    print(f"\n{'='*80}")
    print(f"🔄 {description}")
    print(f"Command: {command}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📤 Exit Code: {result.returncode}")
        
        if result.stdout:
            print(f"📤 STDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"⚠️  STDERR:\n{result.stderr}")
        
        return {
            'command': command,
            'description': description,
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: Command exceeded {timeout} seconds")
        return {
            'command': command,
            'description': description,
            'duration': timeout,
            'returncode': -1,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'success': False
        }
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            'command': command,
            'description': description,
            'duration': 0,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def check_dependencies():
    """Check that all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        'pytest', 'pytest-cov', 'pytest-mock', 'pytest-xdist',
        'pandas', 'numpy', 'flask', 'flask-cors', 'psutil'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Installing missing dependencies...")
        install_cmd = f"pip install {' '.join(missing)}"
        result = run_command(install_cmd, "Installing dependencies")
        if not result['success']:
            print("❌ Failed to install dependencies!")
            return False
    
    return True


def main():
    """Run comprehensive test suite."""
    print("🧪 Network UI - Comprehensive Advanced Test Suite")
    print("="*80)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Ensure we're in a virtual environment (Windows)
    if not os.path.exists('venv/Scripts/python.exe'):
        print("⚠️  Virtual environment not found. Please run from project root with venv activated.")
        sys.exit(1)
    
    # Test categories with their configurations
    test_categories = [
        {
            'name': 'Unit Tests (Original)',
            'command': 'python -m pytest tests/unit/ -v --tb=short',
            'timeout': 300,
            'critical': True
        },
        {
            'name': 'Advanced Data Importer Tests',
            'command': 'python -m pytest tests/unit/test_importer_advanced.py -v --tb=short',
            'timeout': 600,
            'critical': False
        },
        {
            'name': 'Advanced Validator Tests',
            'command': 'python -m pytest tests/unit/test_validators_advanced.py -v --tb=short',
            'timeout': 300,
            'critical': False
        },
        {
            'name': 'Advanced Transformer Tests',
            'command': 'python -m pytest tests/unit/test_transformers_advanced.py -v --tb=short',
            'timeout': 600,
            'critical': False
        },
        {
            'name': 'Parametrized Format Tests',
            'command': 'python -m pytest tests/unit/test_parametrized_formats.py -v --tb=short',
            'timeout': 900,
            'critical': False
        },
        {
            'name': 'API Security Tests',
            'command': 'python -m pytest tests/api/test_api_security.py -v --tb=short',
            'timeout': 600,
            'critical': False
        },
        {
            'name': 'Performance Benchmarks',
            'command': 'python -m pytest tests/performance/test_performance_benchmarks.py -v --tb=short -m "not slow"',
            'timeout': 1200,
            'critical': False
        },
        {
            'name': 'Integration Tests',
            'command': 'python -m pytest tests/integration/ -v --tb=short',
            'timeout': 300,
            'critical': True
        },
        {
            'name': 'API Tests',
            'command': 'python -m pytest tests/api/test_app.py -v --tb=short',
            'timeout': 300,
            'critical': True
        },
        {
            'name': 'Functional Tests',
            'command': 'python -m pytest tests/functional/ -v --tb=short',
            'timeout': 300,
            'critical': True
        },
        {
            'name': 'Code Coverage Report',
            'command': 'python -m pytest tests/ --cov=src/network_ui --cov-report=html --cov-report=xml --cov-report=term-missing',
            'timeout': 600,
            'critical': False
        },
        {
            'name': 'Type Checking',
            'command': 'python -m mypy src/network_ui/ --ignore-missing-imports',
            'timeout': 120,
            'critical': False
        },
        {
            'name': 'Code Linting',
            'command': 'python -m flake8 src/network_ui/ tests/ --max-line-length=120 --ignore=E501,W503 --exclude=tests/performance/',
            'timeout': 120,
            'critical': False
        }
    ]
    
    # Execute test categories
    results = []
    total_start_time = time.time()
    
    for category in test_categories:
        result = run_command(
            category['command'],
            category['name'],
            category['timeout']
        )
        
        result['critical'] = category['critical']
        results.append(result)
        
        # Stop on critical test failures
        if category['critical'] and not result['success']:
            print(f"\n❌ Critical test category '{category['name']}' failed. Stopping execution.")
            break
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST REPORT")
    print(f"{'='*80}")
    print(f"🕐 Total Duration: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    critical_passed = sum(1 for r in results if r['critical'] and r['success'])
    critical_total = sum(1 for r in results if r['critical'])
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"   Total Test Categories: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"   🔑 Critical Tests: {critical_passed}/{critical_total} passed")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        critical = " (CRITICAL)" if result['critical'] else ""
        print(f"   {i:2d}. {status}{critical} - {result['description']}")
        print(f"       Duration: {result['duration']:.2f}s, Exit Code: {result['returncode']}")
        
        if not result['success']:
            # Show brief error info
            error_preview = result['stderr'][:200] + "..." if len(result['stderr']) > 200 else result['stderr']
            print(f"       Error: {error_preview}")
    
    # Performance insights
    print(f"\n⚡ PERFORMANCE INSIGHTS:")
    slowest_tests = sorted(results, key=lambda x: x['duration'], reverse=True)[:5]
    for i, test in enumerate(slowest_tests, 1):
        print(f"   {i}. {test['description']}: {test['duration']:.2f}s")
    
    # Categories analysis
    advanced_tests = [r for r in results if 'Advanced' in r['description'] or 'Performance' in r['description']]
    if advanced_tests:
        advanced_passed = sum(1 for r in advanced_tests if r['success'])
        print(f"\n🚀 ADVANCED TESTING RESULTS:")
        print(f"   Advanced/Performance Tests: {advanced_passed}/{len(advanced_tests)} passed")
        print(f"   Advanced Success Rate: {(advanced_passed/len(advanced_tests)*100):.1f}%")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if failed_tests == 0:
        print("   🎉 All tests passed! Your codebase is in excellent shape.")
        print("   🔍 Consider adding more edge cases or performance tests.")
    elif critical_passed == critical_total:
        print("   ✅ All critical tests passed - core functionality is stable.")
        print("   🔧 Focus on fixing non-critical test failures for better coverage.")
    else:
        print("   🚨 Critical test failures detected - immediate attention required!")
        print("   🔧 Fix critical issues before proceeding with advanced testing.")
    
    if any(r['duration'] > 300 for r in results):
        print("   ⏰ Some tests are taking a long time - consider optimizing performance.")
    
    # Coverage reminder
    coverage_test = next((r for r in results if 'Coverage' in r['description']), None)
    if coverage_test and coverage_test['success']:
        print("   📊 Check the generated coverage report in htmlcov/index.html")
    
    print(f"\n{'='*80}")
    
    # Exit with appropriate code
    if critical_passed < critical_total:
        print("❌ Critical tests failed!")
        sys.exit(1)
    elif failed_tests > 0:
        print("⚠️  Some tests failed, but all critical tests passed.")
        sys.exit(2)
    else:
        print("🎉 All tests passed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main() 