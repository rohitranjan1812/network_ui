"""
Testing Metadata Collector
Pytest plugin for automatically collecting testing and debugging metadata.
"""

import os
import sys
import time
import traceback
import platform
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pytest
import json

from .metadata_models import (
    TestExecution, TestSuite, Issue, Pattern, Environment,
    TestStatus, TestType, IssueSeverity, IssueStatus
)
from .database import TestingMetadataDB

class TestingMetadataCollector:
    """Collects testing metadata during test execution."""
    
    def __init__(self, db_path: str = "testing_metadata.db"):
        """Initialize the collector."""
        self.db = TestingMetadataDB(db_path)
        self.current_suite: Optional[TestSuite] = None
        self.test_executions: Dict[str, TestExecution] = {}
        self.environment = self._capture_environment()
        self.start_time = datetime.now()
    
    def _capture_environment(self) -> Environment:
        """Capture current environment information."""
        try:
            import pkg_resources
            dependencies = {}
            for dist in pkg_resources.working_set:
                dependencies[dist.project_name] = dist.version
        except ImportError:
            dependencies = {}
        
        return Environment(
            name=f"{platform.system()}-{platform.release()}",
            os_name=platform.system(),
            os_version=platform.release(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            dependencies=dependencies,
            system_info={
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "memory_total": psutil.virtual_memory().total if hasattr(psutil, 'virtual_memory') else None,
                "cpu_count": psutil.cpu_count() if hasattr(psutil, 'cpu_count') else None
            },
            configuration={
                "pytest_version": pytest.__version__,
                "python_path": sys.executable,
                "working_directory": os.getcwd()
            }
        )
    
    def _determine_test_type(self, node) -> TestType:
        """Determine the type of test based on file path and markers."""
        file_path = str(node.fspath)
        
        if "unit" in file_path.lower():
            return TestType.UNIT
        elif "integration" in file_path.lower():
            return TestType.INTEGRATION
        elif "functional" in file_path.lower():
            return TestType.FUNCTIONAL
        elif "api" in file_path.lower():
            return TestType.API
        elif "performance" in file_path.lower():
            return TestType.PERFORMANCE
        elif "security" in file_path.lower():
            return TestType.SECURITY
        elif "ui" in file_path.lower():
            return TestType.UI
        else:
            return TestType.UNIT
    
    def _extract_test_parameters(self, node) -> Dict[str, Any]:
        """Extract test parameters from the test node."""
        params = {}
        
        # Extract pytest markers
        if hasattr(node, 'own_markers'):
            params['markers'] = [marker.name for marker in node.own_markers]
        
        # Extract test function parameters
        if hasattr(node, 'funcargs'):
            params['funcargs'] = list(node.funcargs.keys())
        
        # Extract test class if applicable
        if hasattr(node, 'cls') and node.cls:
            params['test_class'] = node.cls.__name__
        
        return params
    
    def pytest_runtest_setup(self, item):
        """Called before each test setup."""
        test_id = f"{item.nodeid}_{datetime.now().timestamp()}"
        
        execution = TestExecution(
            id=test_id,
            test_name=item.name,
            test_file=str(item.fspath),
            test_class=item.cls.__name__ if hasattr(item, 'cls') and item.cls else None,
            test_method=item.name,
            test_type=self._determine_test_type(item),
            status=TestStatus.PASSED,
            start_time=datetime.now(),
            test_parameters=self._extract_test_parameters(item),
            environment_info={
                "os": self.environment.os_name,
                "python_version": self.environment.python_version,
                "pytest_version": pytest.__version__
            },
            tags=[]
        )
        
        self.test_executions[test_id] = execution
    
    def pytest_runtest_teardown(self, item, nextitem):
        """Called after each test teardown."""
        # Find the test execution for this item
        test_id = None
        for tid, execution in self.test_executions.items():
            if execution.test_name == item.name and execution.test_file == str(item.fspath):
                test_id = tid
                break
        
        if test_id:
            execution = self.test_executions[test_id]
            execution.end_time = datetime.now()
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            
            # Store the test execution
            self.db.store_test_execution(execution)
    
    def pytest_runtest_logreport(self, report):
        """Called for each test report."""
        # Find the test execution for this report
        test_id = None
        for tid, execution in self.test_executions.items():
            if execution.test_name == report.nodeid.split("::")[-1]:
                test_id = tid
                break
        
        if test_id and report.when == 'call':
            execution = self.test_executions[test_id]
            
            # Update status based on report
            if report.passed:
                execution.status = TestStatus.PASSED
            elif report.failed:
                execution.status = TestStatus.FAILED
                execution.error_message = str(report.longrepr) if hasattr(report, 'longrepr') else None
                execution.error_traceback = str(report.longrepr) if hasattr(report, 'longrepr') else None
            elif report.skipped:
                execution.status = TestStatus.SKIPPED
                execution.error_message = str(report.longrepr) if hasattr(report, 'longrepr') else None
    
    def pytest_sessionstart(self, session):
        """Called at the start of the test session."""
        self.current_suite = TestSuite(
            suite_name=session.config.getoption("--tb", default="auto"),
            start_time=datetime.now(),
            environment_info={
                "os": self.environment.os_name,
                "python_version": self.environment.python_version,
                "pytest_version": pytest.__version__,
                "test_paths": session.config.args if hasattr(session.config, 'args') else []
            }
        )
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called at the end of the test session."""
        if self.current_suite:
            self.current_suite.end_time = datetime.now()
            self.current_suite.total_execution_time = (
                self.current_suite.end_time - self.current_suite.start_time
            ).total_seconds()
            
            # Count test results
            passed = failed = skipped = error = 0
            for execution in self.test_executions.values():
                if execution.status == TestStatus.PASSED:
                    passed += 1
                elif execution.status == TestStatus.FAILED:
                    failed += 1
                elif execution.status == TestStatus.SKIPPED:
                    skipped += 1
                elif execution.status == TestStatus.ERROR:
                    error += 1
            
            self.current_suite.passed_tests = passed
            self.current_suite.failed_tests = failed
            self.current_suite.skipped_tests = skipped
            self.current_suite.error_tests = error
            self.current_suite.total_tests = passed + failed + skipped + error
            self.current_suite.test_executions = list(self.test_executions.keys())
            
            # Store the test suite
            self.db.store_test_suite(self.current_suite)
    
    def pytest_exception_interact(self, call, report):
        """Called when an exception occurs during test execution."""
        if report.failed:
            # Create an issue for the failure
            issue = Issue(
                title=f"Test failure: {report.nodeid}",
                description=f"Test {report.nodeid} failed during execution",
                severity=IssueSeverity.MEDIUM,
                status=IssueStatus.OPEN,
                issue_type="test_failure",
                component=self._extract_component_from_path(str(report.fspath)),
                file_path=str(report.fspath),
                line_number=getattr(report, 'lineno', None),
                error_message=str(report.longrepr) if hasattr(report, 'longrepr') else None,
                error_traceback=str(report.longrepr) if hasattr(report, 'longrepr') else None,
                expected_behavior="Test should pass",
                actual_behavior="Test failed with exception",
                reporter="pytest_metadata_collector"
            )
            
            # Try to find related test execution
            for execution in self.test_executions.values():
                if execution.test_name in report.nodeid:
                    issue.test_execution_ids.append(execution.id)
                    break
            
            self.db.store_issue(issue)
    
    def _extract_component_from_path(self, file_path: str) -> str:
        """Extract component name from file path."""
        path_parts = file_path.split(os.sep)
        if "api" in path_parts:
            return "api"
        elif "core" in path_parts:
            return "core"
        elif "analytics" in path_parts:
            return "analytics"
        elif "visualization" in path_parts:
            return "visualization"
        else:
            return "unknown"

class IssueTracker:
    """Tracks and analyzes issues for patterns."""
    
    def __init__(self, db: TestingMetadataDB):
        """Initialize the issue tracker."""
        self.db = db
    
    def analyze_patterns(self):
        """Analyze issues to find recurring patterns."""
        issues = self.db.get_issues()
        
        # Group issues by error signature
        error_groups = {}
        for issue in issues:
            if issue.error_message:
                # Create a signature based on error message
                signature = self._create_error_signature(issue.error_message)
                if signature not in error_groups:
                    error_groups[signature] = []
                error_groups[signature].append(issue)
        
        # Create patterns for recurring errors
        for signature, issue_group in error_groups.items():
            if len(issue_group) > 1:  # Only create patterns for recurring issues
                pattern = Pattern(
                    name=f"Recurring error: {signature[:50]}...",
                    description=f"Error pattern occurring {len(issue_group)} times",
                    pattern_type="test_failure",
                    signature=signature,
                    frequency=len(issue_group),
                    first_seen=min(issue.created_at for issue in issue_group),
                    last_seen=max(issue.created_at for issue in issue_group),
                    affected_components=list(set(issue.component for issue in issue_group)),
                    related_issues=[issue.id for issue in issue_group],
                    related_tests=[tid for issue in issue_group for tid in issue.test_execution_ids],
                    severity=IssueSeverity.HIGH if len(issue_group) > 5 else IssueSeverity.MEDIUM,
                    confidence_score=min(len(issue_group) / 10.0, 1.0)
                )
                
                self.db.store_pattern(pattern)
    
    def _create_error_signature(self, error_message: str) -> str:
        """Create a signature for an error message."""
        import hashlib
        
        # Clean the error message (remove line numbers, file paths, etc.)
        cleaned = error_message
        # Remove common variable parts
        import re
        cleaned = re.sub(r'line \d+', 'line N', cleaned)
        cleaned = re.sub(r'File ".*?"', 'File "..."', cleaned)
        cleaned = re.sub(r'at 0x[0-9a-fA-F]+', 'at 0x...', cleaned)
        
        # Create hash
        return hashlib.md5(cleaned.encode()).hexdigest()[:16]

class TestingMetadataAPI:
    """API for querying testing metadata."""
    
    def __init__(self, db: TestingMetadataDB):
        """Initialize the API."""
        self.db = db
        self.issue_tracker = IssueTracker(db)
    
    def get_test_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get a summary of test results for the specified period."""
        start_date = datetime.now() - timedelta(days=days)
        
        executions = self.db.get_test_executions(start_date=start_date)
        
        summary = {
            "period_days": days,
            "total_tests": len(executions),
            "passed": len([e for e in executions if e.status == TestStatus.PASSED]),
            "failed": len([e for e in executions if e.status == TestStatus.FAILED]),
            "skipped": len([e for e in executions if e.status == TestStatus.SKIPPED]),
            "error": len([e for e in executions if e.status == TestStatus.ERROR]),
            "avg_execution_time": sum(e.execution_time for e in executions) / len(executions) if executions else 0,
            "success_rate": len([e for e in executions if e.status == TestStatus.PASSED]) / len(executions) * 100 if executions else 0
        }
        
        return summary
    
    def get_issue_summary(self) -> Dict[str, Any]:
        """Get a summary of issues."""
        issues = self.db.get_issues()
        
        summary = {
            "total_issues": len(issues),
            "open_issues": len([i for i in issues if i.status == IssueStatus.OPEN]),
            "resolved_issues": len([i for i in issues if i.status == IssueStatus.RESOLVED]),
            "critical_issues": len([i for i in issues if i.severity == IssueSeverity.CRITICAL]),
            "by_component": {},
            "by_severity": {}
        }
        
        # Group by component
        for issue in issues:
            if issue.component not in summary["by_component"]:
                summary["by_component"][issue.component] = 0
            summary["by_component"][issue.component] += 1
        
        # Group by severity
        for issue in issues:
            severity = issue.severity.value
            if severity not in summary["by_severity"]:
                summary["by_severity"][severity] = 0
            summary["by_severity"][severity] += 1
        
        return summary
    
    def get_patterns_summary(self) -> Dict[str, Any]:
        """Get a summary of patterns."""
        patterns = self.db.get_patterns()
        
        summary = {
            "total_patterns": len(patterns),
            "high_frequency_patterns": len([p for p in patterns if p.frequency > 5]),
            "by_type": {},
            "most_frequent": []
        }
        
        # Group by type
        for pattern in patterns:
            if pattern.pattern_type not in summary["by_type"]:
                summary["by_type"][pattern.pattern_type] = 0
            summary["by_type"][pattern.pattern_type] += 1
        
        # Get most frequent patterns
        summary["most_frequent"] = [
            {
                "name": p.name,
                "frequency": p.frequency,
                "type": p.pattern_type,
                "severity": p.severity.value
            }
            for p in sorted(patterns, key=lambda x: x.frequency, reverse=True)[:5]
        ]
        
        return summary
    
    def analyze_and_update_patterns(self):
        """Analyze issues and update patterns."""
        self.issue_tracker.analyze_patterns()
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations based on analysis."""
        recommendations = []
        
        # Get statistics
        stats = self.db.get_statistics()
        
        # Check for high failure rates
        if stats.get("test_executions", {}).get("success_rate", 100) < 90:
            recommendations.append({
                "type": "high_failure_rate",
                "priority": "high",
                "description": f"Test success rate is {stats['test_executions']['success_rate']:.1f}%, below 90% threshold",
                "suggestion": "Review failing tests and investigate root causes"
            })
        
        # Check for critical issues
        critical_issues = stats.get("issues", {}).get("critical", 0) or 0
        if critical_issues > 0:
            recommendations.append({
                "type": "critical_issues",
                "priority": "critical",
                "description": f"{stats['issues']['critical']} critical issues found",
                "suggestion": "Address critical issues immediately"
            })
        
        # Check for recurring patterns
        patterns = self.db.get_patterns()
        high_freq_patterns = [p for p in patterns if p.frequency > 3]
        if high_freq_patterns:
            recommendations.append({
                "type": "recurring_patterns",
                "priority": "medium",
                "description": f"{len(high_freq_patterns)} recurring patterns detected",
                "suggestion": "Investigate and fix root causes of recurring issues"
            })
        
        return recommendations 