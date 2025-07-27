"""
Testing and Debugging Metadata Models
Comprehensive database models for tracking testing details, issues, patterns, and fixes.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"

class IssueSeverity(Enum):
    """Issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueStatus(Enum):
    """Issue resolution status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"

class TestType(Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    API = "api"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI = "ui"

@dataclass
class TestExecution:
    """Record of a test execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_name: str = ""
    test_file: str = ""
    test_class: Optional[str] = None
    test_method: str = ""
    test_type: TestType = TestType.UNIT
    status: TestStatus = TestStatus.PASSED
    execution_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    test_parameters: Dict[str, Any] = field(default_factory=dict)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TestSuite:
    """Record of a test suite execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suite_name: str = ""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    total_execution_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    environment_info: Dict[str, Any] = field(default_factory=dict)
    test_executions: List[str] = field(default_factory=list)  # List of TestExecution IDs
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Issue:
    """Record of an issue found during testing or development."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: IssueSeverity = IssueSeverity.MEDIUM
    status: IssueStatus = IssueStatus.OPEN
    issue_type: str = ""  # e.g., "bug", "feature_request", "performance", "security"
    component: str = ""  # e.g., "api", "ui", "database", "core"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    reproduction_steps: List[str] = field(default_factory=list)
    expected_behavior: str = ""
    actual_behavior: str = ""
    test_execution_ids: List[str] = field(default_factory=list)  # Related test executions
    tags: List[str] = field(default_factory=list)
    assignee: Optional[str] = None
    reporter: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

@dataclass
class Fix:
    """Record of a fix applied to resolve an issue."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    issue_id: str = ""
    title: str = ""
    description: str = ""
    fix_type: str = ""  # e.g., "code_change", "configuration", "dependency_update"
    files_changed: List[str] = field(default_factory=list)
    lines_changed: Dict[str, List[int]] = field(default_factory=dict)  # file_path -> [line_numbers]
    code_changes: Dict[str, str] = field(default_factory=dict)  # file_path -> diff
    before_state: Dict[str, Any] = field(default_factory=dict)
    after_state: Dict[str, Any] = field(default_factory=dict)
    applied_by: str = ""
    applied_at: datetime = field(default_factory=datetime.now)
    verification_tests: List[str] = field(default_factory=list)  # TestExecution IDs
    success_rate: float = 0.0  # Percentage of tests that pass after fix
    regression_tests: List[str] = field(default_factory=list)  # Tests to ensure no regression

@dataclass
class Pattern:
    """Record of recurring patterns in issues or test failures."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    pattern_type: str = ""  # e.g., "test_failure", "performance_degradation", "error_pattern"
    signature: str = ""  # Unique signature to identify the pattern
    frequency: int = 0  # How many times this pattern has occurred
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    affected_components: List[str] = field(default_factory=list)
    related_issues: List[str] = field(default_factory=list)  # Issue IDs
    related_tests: List[str] = field(default_factory=list)  # TestExecution IDs
    severity: IssueSeverity = IssueSeverity.MEDIUM
    suggested_fixes: List[str] = field(default_factory=list)  # Fix IDs
    confidence_score: float = 0.0  # Confidence in pattern identification
    tags: List[str] = field(default_factory=list)

@dataclass
class Environment:
    """Record of environment information for test executions."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    os_name: str = ""
    os_version: str = ""
    python_version: str = ""
    dependencies: Dict[str, str] = field(default_factory=dict)  # package -> version
    system_info: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceMetrics:
    """Record of performance metrics during testing."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_execution_id: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
    threshold: Optional[float] = None
    threshold_exceeded: bool = False
    component: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CodeCoverage:
    """Record of code coverage information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_execution_id: str = ""
    file_path: str = ""
    total_lines: int = 0
    covered_lines: int = 0
    coverage_percentage: float = 0.0
    uncovered_lines: List[int] = field(default_factory=list)
    branch_coverage: Optional[float] = None
    function_coverage: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DebugSession:
    """Record of debugging sessions."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_name: str = ""
    issue_id: Optional[str] = None
    test_execution_id: Optional[str] = None
    debugger_type: str = ""  # e.g., "pdb", "ipdb", "pycharm", "vscode"
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    breakpoints: List[Dict[str, Any]] = field(default_factory=list)
    variables_inspected: List[str] = field(default_factory=list)
    code_executed: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    resolution: Optional[str] = None
    debugger_output: str = ""
    created_at: datetime = field(default_factory=datetime.now) 