"""
Pytest configuration with testing metadata collection.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the testing metadata collector
from network_ui.testing import TestingMetadataCollector

# Global collector instance
metadata_collector = None

def pytest_configure(config):
    """Configure pytest with metadata collection."""
    global metadata_collector
    
    # Initialize the metadata collector
    db_path = os.environ.get('TESTING_METADATA_DB', 'testing_metadata.db')
    metadata_collector = TestingMetadataCollector(db_path)
    
    # Register the collector as a plugin
    config.pluginmanager.register(metadata_collector, "metadata_collector")

def pytest_unconfigure(config):
    """Clean up after pytest."""
    global metadata_collector
    
    if metadata_collector:
        # Analyze patterns after test completion
        from network_ui.testing import TestingMetadataAPI
        api = TestingMetadataAPI(metadata_collector.db)
        api.analyze_and_update_patterns()
        
        # Print summary
        print("\n" + "="*60)
        print("TESTING METADATA SUMMARY")
        print("="*60)
        
        test_summary = api.get_test_summary()
        print(f"Test Results (Last 7 days):")
        print(f"  Total Tests: {test_summary['total_tests']}")
        print(f"  Passed: {test_summary['passed']}")
        print(f"  Failed: {test_summary['failed']}")
        print(f"  Success Rate: {test_summary['success_rate']:.1f}%")
        print(f"  Avg Execution Time: {test_summary['avg_execution_time']:.2f}s")
        
        issue_summary = api.get_issue_summary()
        print(f"\nIssues:")
        print(f"  Total Issues: {issue_summary['total_issues']}")
        print(f"  Open Issues: {issue_summary['open_issues']}")
        print(f"  Critical Issues: {issue_summary['critical_issues']}")
        
        patterns_summary = api.get_patterns_summary()
        print(f"\nPatterns:")
        print(f"  Total Patterns: {patterns_summary['total_patterns']}")
        print(f"  High Frequency: {patterns_summary['high_frequency_patterns']}")
        
        recommendations = api.get_recommendations()
        if recommendations:
            print(f"\nRecommendations:")
            for rec in recommendations:
                print(f"  [{rec['priority'].upper()}] {rec['description']}")
                print(f"    Suggestion: {rec['suggestion']}")
        
        print("="*60)

# Pytest fixtures for testing metadata
@pytest.fixture
def metadata_db():
    """Provide access to the testing metadata database."""
    global metadata_collector
    if metadata_collector:
        return metadata_collector.db
    return None

@pytest.fixture
def metadata_api():
    """Provide access to the testing metadata API."""
    global metadata_collector
    if metadata_collector:
        from network_ui.testing import TestingMetadataAPI
        return TestingMetadataAPI(metadata_collector.db)
    return None 