#!/usr/bin/env python3
"""
Advanced UI Test Runner
Comprehensive testing suite for the ultra-advanced Network UI features.
Connected to testing metadata database for detailed tracking and analysis.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def setup_test_environment():
    """Setup the test environment for advanced UI testing."""
    print("🔧 Setting up advanced UI test environment...")
    
    # Ensure we're in the project directory
    os.chdir(Path(__file__).parent)
    
    # Add src to Python path
    src_path = Path("src").absolute()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variables for testing
    os.environ['TESTING_METADATA_DB'] = 'advanced_ui_test_metadata.db'
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['ADVANCED_UI_TESTING'] = 'true'
    
    print("✅ Test environment configured")


def run_advanced_ui_tests(test_categories: List[str] = None, verbose: bool = True, 
                         coverage: bool = True, parallel: bool = False) -> Dict:
    """Run advanced UI tests with comprehensive metadata collection."""
    
    # Default test categories if none specified
    if not test_categories:
        test_categories = [
            'ui_core',
            'data_import', 
            'analytics',
            'visualization',
            'interactions',
            'performance',
            'integration'
        ]
    
    print(f"🚀 Running Advanced UI Tests: {', '.join(test_categories)}")
    print("=" * 80)
    
    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/ui/test_advanced_ui.py",
        "-v" if verbose else "-q",
        "--tb=short",
        "--disable-warnings"
    ]
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=src/network_ui",
            "--cov-report=html:htmlcov_advanced_ui",
            "--cov-report=term-missing"
        ])
    
    # Add parallel execution if requested
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add test markers for specific categories
    test_markers = []
    for category in test_categories:
        if category == 'ui_core':
            test_markers.append("TestAdvancedUICore")
        elif category == 'data_import':
            test_markers.append("TestAdvancedDataImport")
        elif category == 'analytics':
            test_markers.append("TestAdvancedAnalytics")
        elif category == 'visualization':
            test_markers.append("TestAdvancedVisualization")
        elif category == 'interactions':
            test_markers.append("TestAdvancedInteractions")
        elif category == 'performance':
            test_markers.append("TestPerformanceMonitoring")
        elif category == 'integration':
            test_markers.append("TestAdvancedUIIntegration")
    
    if test_markers:
        # Run specific test classes
        for marker in test_markers:
            class_cmd = cmd + [f"-k", marker]
            print(f"🧪 Running {marker} tests...")
            
            start_time = time.time()
            result = subprocess.run(class_cmd, capture_output=True, text=True)
            end_time = time.time()
            
            print(f"⏱️  {marker} completed in {end_time - start_time:.2f}s")
            print(f"Exit code: {result.returncode}")
            
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            
            if result.stderr and result.returncode != 0:
                print("STDERR:")
                print(result.stderr)
            
            print("-" * 60)
    else:
        # Run all tests
        print("🧪 Running all advanced UI tests...")
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        print(f"⏱️  All tests completed in {end_time - start_time:.2f}s")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print("STDERR:")
            print(result.stderr)
    
    return {
        'success': result.returncode == 0,
        'exit_code': result.returncode,
        'duration': end_time - start_time,
        'stdout': result.stdout,
        'stderr': result.stderr
    }


def run_api_endpoint_tests() -> Dict:
    """Run tests specifically for the new advanced API endpoints."""
    print("🔌 Testing Advanced API Endpoints...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/api/",
        "-v",
        "--tb=short",
        "-k", "advanced or config or visualization"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  API tests completed in {end_time - start_time:.2f}s")
    print(f"Exit code: {result.returncode}")
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr and result.returncode != 0:
        print("STDERR:")
        print(result.stderr)
    
    return {
        'success': result.returncode == 0,
        'exit_code': result.returncode,
        'duration': end_time - start_time,
        'stdout': result.stdout,
        'stderr': result.stderr
    }


def run_integration_tests() -> Dict:
    """Run integration tests between advanced UI and backend systems."""
    print("🔗 Running Advanced UI Integration Tests...")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "-m", "integration"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  Integration tests completed in {end_time - start_time:.2f}s")
    print(f"Exit code: {result.returncode}")
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr and result.returncode != 0:
        print("STDERR:")
        print(result.stderr)
    
    return {
        'success': result.returncode == 0,
        'exit_code': result.returncode,
        'duration': end_time - start_time,
        'stdout': result.stdout,
        'stderr': result.stderr
    }


def generate_advanced_ui_report():
    """Generate a comprehensive report of advanced UI test results."""
    print("📊 Generating Advanced UI Test Report...")
    
    try:
        # Import the testing metadata API
        from network_ui.testing import TestingMetadataAPI, TestingMetadataDB
        
        # Connect to the test metadata database
        db_path = os.environ.get('TESTING_METADATA_DB', 'advanced_ui_test_metadata.db')
        db = TestingMetadataDB(db_path)
        api = TestingMetadataAPI(db)
        
        # Generate comprehensive report
        print("\n" + "=" * 80)
        print("ADVANCED UI TESTING REPORT")
        print("=" * 80)
        
        # Test summary
        test_summary = api.get_test_summary()
        print(f"📈 Test Execution Summary:")
        print(f"  Total Tests: {test_summary.get('total_tests', 0)}")
        print(f"  Passed: {test_summary.get('passed', 0)}")
        print(f"  Failed: {test_summary.get('failed', 0)}")
        print(f"  Success Rate: {test_summary.get('success_rate', 0):.1f}%")
        print(f"  Average Execution Time: {test_summary.get('avg_execution_time', 0):.2f}s")
        
        # Issues summary
        issue_summary = api.get_issue_summary()
        print(f"\n🐛 Issues Summary:")
        print(f"  Total Issues: {issue_summary.get('total_issues', 0)}")
        print(f"  Open Issues: {issue_summary.get('open_issues', 0)}")
        print(f"  Critical Issues: {issue_summary.get('critical_issues', 0)}")
        print(f"  High Priority Issues: {issue_summary.get('high_issues', 0)}")
        
        # Pattern analysis
        patterns_summary = api.get_patterns_summary()
        print(f"\n🔍 Pattern Analysis:")
        print(f"  Total Patterns: {patterns_summary.get('total_patterns', 0)}")
        print(f"  High Frequency Patterns: {patterns_summary.get('high_frequency_patterns', 0)}")
        
        # Recommendations
        recommendations = api.get_recommendations()
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"  {i}. [{rec.get('priority', 'MEDIUM').upper()}] {rec.get('description', 'N/A')}")
                print(f"     Suggestion: {rec.get('suggestion', 'N/A')}")
        
        # Advanced UI specific metrics
        print(f"\n🎨 Advanced UI Metrics:")
        ui_tests = db.get_tests_by_suite("TestAdvancedUICore")
        if ui_tests:
            print(f"  Core UI Tests: {len(ui_tests)}")
            ui_success_rate = len([t for t in ui_tests if t.status.value == 'passed']) / len(ui_tests) * 100
            print(f"  Core UI Success Rate: {ui_success_rate:.1f}%")
        
        # Performance metrics
        perf_tests = db.get_tests_by_suite("TestPerformanceMonitoring")
        if perf_tests:
            print(f"  Performance Tests: {len(perf_tests)}")
            perf_success_rate = len([t for t in perf_tests if t.status.value == 'passed']) / len(perf_tests) * 100
            print(f"  Performance Success Rate: {perf_success_rate:.1f}%")
        
        print("=" * 80)
        
        # Generate detailed JSON report
        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'test_summary': test_summary,
            'issue_summary': issue_summary,
            'patterns_summary': patterns_summary,
            'recommendations': recommendations,
            'test_categories': {
                'ui_core': len(db.get_tests_by_suite("TestAdvancedUICore")),
                'data_import': len(db.get_tests_by_suite("TestAdvancedDataImport")),
                'analytics': len(db.get_tests_by_suite("TestAdvancedAnalytics")),
                'visualization': len(db.get_tests_by_suite("TestAdvancedVisualization")),
                'interactions': len(db.get_tests_by_suite("TestAdvancedInteractions")),
                'performance': len(db.get_tests_by_suite("TestPerformanceMonitoring")),
                'integration': len(db.get_tests_by_suite("TestAdvancedUIIntegration"))
            }
        }
        
        # Save detailed report
        report_file = f"advanced_ui_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(detailed_report, f, indent=2)
        
        print(f"📋 Detailed report saved to: {report_file}")
        
    except ImportError as e:
        print(f"⚠️  Could not generate metadata report: {e}")
        print("Make sure the testing metadata system is properly installed.")
    except Exception as e:
        print(f"❌ Error generating report: {e}")


def run_selenium_browser_tests() -> Dict:
    """Run browser-based Selenium tests for the advanced UI."""
    print("🌐 Running Browser-based UI Tests...")
    
    # Check if Selenium dependencies are available
    try:
        import selenium
        from selenium import webdriver
    except ImportError:
        print("⚠️  Selenium not installed. Skipping browser tests.")
        print("Install with: pip install selenium")
        return {'success': False, 'reason': 'selenium_not_installed'}
    
    # Check for Chrome/ChromeDriver
    try:
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        
    except Exception as e:
        print(f"⚠️  Chrome/ChromeDriver not available: {e}")
        print("Browser tests will be skipped in test execution.")
        return {'success': False, 'reason': 'chrome_not_available'}
    
    # Run UI tests that require browser
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/ui/test_advanced_ui.py",
        "-v",
        "--tb=short",
        "-k", "browser or selenium or canvas"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️  Browser tests completed in {end_time - start_time:.2f}s")
    print(f"Exit code: {result.returncode}")
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr and result.returncode != 0:
        print("STDERR:")
        print(result.stderr)
    
    return {
        'success': result.returncode == 0,
        'exit_code': result.returncode,
        'duration': end_time - start_time,
        'stdout': result.stdout,
        'stderr': result.stderr
    }


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Advanced UI Test Runner")
    parser.add_argument('--categories', nargs='+', 
                       choices=['ui_core', 'data_import', 'analytics', 'visualization', 
                               'interactions', 'performance', 'integration'],
                       help="Test categories to run")
    parser.add_argument('--no-coverage', action='store_true', help="Skip coverage analysis")
    parser.add_argument('--parallel', action='store_true', help="Run tests in parallel")
    parser.add_argument('--browser-tests', action='store_true', help="Include browser-based tests")
    parser.add_argument('--api-tests', action='store_true', help="Include API endpoint tests")
    parser.add_argument('--integration-tests', action='store_true', help="Include integration tests")
    parser.add_argument('--quick', action='store_true', help="Run quick test suite only")
    parser.add_argument('--report-only', action='store_true', help="Generate report only, skip tests")
    
    args = parser.parse_args()
    
    # Setup test environment
    setup_test_environment()
    
    # Track overall results
    all_results = {}
    overall_success = True
    
    if args.report_only:
        generate_advanced_ui_report()
        return
    
    # Run main advanced UI tests
    if not args.quick:
        print("🎯 Running Advanced UI Test Suite")
        ui_results = run_advanced_ui_tests(
            test_categories=args.categories,
            coverage=not args.no_coverage,
            parallel=args.parallel
        )
        all_results['ui_tests'] = ui_results
        overall_success &= ui_results['success']
    
    # Run API tests if requested
    if args.api_tests or not args.quick:
        api_results = run_api_endpoint_tests()
        all_results['api_tests'] = api_results
        overall_success &= api_results['success']
    
    # Run integration tests if requested
    if args.integration_tests or not args.quick:
        integration_results = run_integration_tests()
        all_results['integration_tests'] = integration_results
        overall_success &= integration_results['success']
    
    # Run browser tests if requested
    if args.browser_tests:
        browser_results = run_selenium_browser_tests()
        all_results['browser_tests'] = browser_results
        if browser_results.get('reason') != 'selenium_not_installed':
            overall_success &= browser_results['success']
    
    # Generate comprehensive report
    print("\n" + "🔄" * 20)
    generate_advanced_ui_report()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    
    for test_type, results in all_results.items():
        status = "✅ PASSED" if results['success'] else "❌ FAILED"
        duration = results.get('duration', 0)
        print(f"{test_type.upper()}: {status} ({duration:.2f}s)")
    
    if overall_success:
        print("\n🎉 ALL ADVANCED UI TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main() 