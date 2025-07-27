"""
Testing Metadata Database Manager
Handles storage, retrieval, and querying of testing and debugging metadata.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pickle
import hashlib

from .metadata_models import (
    TestExecution, TestSuite, Issue, Fix, Pattern, Environment,
    PerformanceMetrics, CodeCoverage, DebugSession,
    TestStatus, IssueSeverity, IssueStatus, TestType
)

class TestingMetadataDB:
    """Database manager for testing and debugging metadata."""
    
    def __init__(self, db_path: str = "testing_metadata.db"):
        """Initialize the database manager."""
        self.db_path = Path(db_path)
        self.logger = self._setup_logging()
        self._init_database()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the database manager."""
        logger = logging.getLogger('TestingMetadataDB')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS test_executions (
                    id TEXT PRIMARY KEY,
                    test_name TEXT NOT NULL,
                    test_file TEXT NOT NULL,
                    test_class TEXT,
                    test_method TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    execution_time REAL DEFAULT 0.0,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    error_message TEXT,
                    error_traceback TEXT,
                    test_parameters TEXT,
                    environment_info TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS test_suites (
                    id TEXT PRIMARY KEY,
                    suite_name TEXT NOT NULL,
                    total_tests INTEGER DEFAULT 0,
                    passed_tests INTEGER DEFAULT 0,
                    failed_tests INTEGER DEFAULT 0,
                    skipped_tests INTEGER DEFAULT 0,
                    error_tests INTEGER DEFAULT 0,
                    total_execution_time REAL DEFAULT 0.0,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    environment_info TEXT,
                    test_executions TEXT,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    issue_type TEXT,
                    component TEXT,
                    file_path TEXT,
                    line_number INTEGER,
                    error_message TEXT,
                    error_traceback TEXT,
                    reproduction_steps TEXT,
                    expected_behavior TEXT,
                    actual_behavior TEXT,
                    test_execution_ids TEXT,
                    tags TEXT,
                    assignee TEXT,
                    reporter TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    resolved_at TEXT
                );
                
                CREATE TABLE IF NOT EXISTS fixes (
                    id TEXT PRIMARY KEY,
                    issue_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    fix_type TEXT,
                    files_changed TEXT,
                    lines_changed TEXT,
                    code_changes TEXT,
                    before_state TEXT,
                    after_state TEXT,
                    applied_by TEXT NOT NULL,
                    applied_at TEXT NOT NULL,
                    verification_tests TEXT,
                    success_rate REAL DEFAULT 0.0,
                    regression_tests TEXT
                );
                
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    pattern_type TEXT,
                    signature TEXT UNIQUE,
                    frequency INTEGER DEFAULT 0,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    affected_components TEXT,
                    related_issues TEXT,
                    related_tests TEXT,
                    severity TEXT,
                    suggested_fixes TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    tags TEXT
                );
                
                CREATE TABLE IF NOT EXISTS environments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    os_name TEXT,
                    os_version TEXT,
                    python_version TEXT,
                    dependencies TEXT,
                    system_info TEXT,
                    configuration TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    test_execution_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    threshold REAL,
                    threshold_exceeded BOOLEAN DEFAULT FALSE,
                    component TEXT,
                    timestamp TEXT NOT NULL,
                    context TEXT
                );
                
                CREATE TABLE IF NOT EXISTS code_coverage (
                    id TEXT PRIMARY KEY,
                    test_execution_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    total_lines INTEGER DEFAULT 0,
                    covered_lines INTEGER DEFAULT 0,
                    coverage_percentage REAL DEFAULT 0.0,
                    uncovered_lines TEXT,
                    branch_coverage REAL,
                    function_coverage REAL,
                    timestamp TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS debug_sessions (
                    id TEXT PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    issue_id TEXT,
                    test_execution_id TEXT,
                    debugger_type TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL DEFAULT 0.0,
                    breakpoints TEXT,
                    variables_inspected TEXT,
                    code_executed TEXT,
                    findings TEXT,
                    resolution TEXT,
                    debugger_output TEXT,
                    created_at TEXT NOT NULL
                );
            """)
            
            # Create indexes for better query performance
            cursor.executescript("""
                CREATE INDEX IF NOT EXISTS idx_test_executions_status ON test_executions(status);
                CREATE INDEX IF NOT EXISTS idx_test_executions_test_type ON test_executions(test_type);
                CREATE INDEX IF NOT EXISTS idx_test_executions_created_at ON test_executions(created_at);
                CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
                CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity);
                CREATE INDEX IF NOT EXISTS idx_issues_component ON issues(component);
                CREATE INDEX IF NOT EXISTS idx_patterns_signature ON patterns(signature);
                CREATE INDEX IF NOT EXISTS idx_performance_metrics_test_id ON performance_metrics(test_execution_id);
            """)
            
            conn.commit()
    
    def _serialize_dict(self, data: Dict[str, Any]) -> str:
        """Serialize dictionary to JSON string."""
        return json.dumps(data, default=str)
    
    def _deserialize_dict(self, data: str) -> Dict[str, Any]:
        """Deserialize JSON string to dictionary."""
        if not data:
            return {}
        return json.loads(data)
    
    def _serialize_list(self, data: List[Any]) -> str:
        """Serialize list to JSON string."""
        return json.dumps(data, default=str)
    
    def _deserialize_list(self, data: str) -> List[Any]:
        """Deserialize JSON string to list."""
        if not data:
            return []
        return json.loads(data)
    
    def store_test_execution(self, execution: TestExecution) -> bool:
        """Store a test execution record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO test_executions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.id,
                    execution.test_name,
                    execution.test_file,
                    execution.test_class,
                    execution.test_method,
                    execution.test_type.value,
                    execution.status.value,
                    execution.execution_time,
                    execution.start_time.isoformat(),
                    execution.end_time.isoformat() if execution.end_time else None,
                    execution.error_message,
                    execution.error_traceback,
                    self._serialize_dict(execution.test_parameters),
                    self._serialize_dict(execution.environment_info),
                    self._serialize_list(execution.tags),
                    execution.created_at.isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to store test execution: {e}")
            return False
    
    def store_test_suite(self, suite: TestSuite) -> bool:
        """Store a test suite record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO test_suites VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    suite.id,
                    suite.suite_name,
                    suite.total_tests,
                    suite.passed_tests,
                    suite.failed_tests,
                    suite.skipped_tests,
                    suite.error_tests,
                    suite.total_execution_time,
                    suite.start_time.isoformat(),
                    suite.end_time.isoformat() if suite.end_time else None,
                    self._serialize_dict(suite.environment_info),
                    self._serialize_list(suite.test_executions),
                    suite.created_at.isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to store test suite: {e}")
            return False
    
    def store_issue(self, issue: Issue) -> bool:
        """Store an issue record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO issues VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    issue.id,
                    issue.title,
                    issue.description,
                    issue.severity.value,
                    issue.status.value,
                    issue.issue_type,
                    issue.component,
                    issue.file_path,
                    issue.line_number,
                    issue.error_message,
                    issue.error_traceback,
                    self._serialize_list(issue.reproduction_steps),
                    issue.expected_behavior,
                    issue.actual_behavior,
                    self._serialize_list(issue.test_execution_ids),
                    self._serialize_list(issue.tags),
                    issue.assignee,
                    issue.reporter,
                    issue.created_at.isoformat(),
                    issue.updated_at.isoformat(),
                    issue.resolved_at.isoformat() if issue.resolved_at else None
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to store issue: {e}")
            return False
    
    def store_fix(self, fix: Fix) -> bool:
        """Store a fix record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO fixes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fix.id,
                    fix.issue_id,
                    fix.title,
                    fix.description,
                    fix.fix_type,
                    self._serialize_list(fix.files_changed),
                    self._serialize_dict(fix.lines_changed),
                    self._serialize_dict(fix.code_changes),
                    self._serialize_dict(fix.before_state),
                    self._serialize_dict(fix.after_state),
                    fix.applied_by,
                    fix.applied_at.isoformat(),
                    self._serialize_list(fix.verification_tests),
                    fix.success_rate,
                    self._serialize_list(fix.regression_tests)
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to store fix: {e}")
            return False
    
    def store_pattern(self, pattern: Pattern) -> bool:
        """Store a pattern record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.id,
                    pattern.name,
                    pattern.description,
                    pattern.pattern_type,
                    pattern.signature,
                    pattern.frequency,
                    pattern.first_seen.isoformat(),
                    pattern.last_seen.isoformat(),
                    self._serialize_list(pattern.affected_components),
                    self._serialize_list(pattern.related_issues),
                    self._serialize_list(pattern.related_tests),
                    pattern.severity.value,
                    self._serialize_list(pattern.suggested_fixes),
                    pattern.confidence_score,
                    self._serialize_list(pattern.tags)
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {e}")
            return False
    
    def get_test_executions(self, 
                          status: Optional[TestStatus] = None,
                          test_type: Optional[TestType] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          limit: int = 100) -> List[TestExecution]:
        """Retrieve test executions with filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM test_executions WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                if test_type:
                    query += " AND test_type = ?"
                    params.append(test_type.value)
                
                if start_date:
                    query += " AND created_at >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND created_at <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                executions = []
                for row in rows:
                    execution = TestExecution(
                        id=row[0],
                        test_name=row[1],
                        test_file=row[2],
                        test_class=row[3],
                        test_method=row[4],
                        test_type=TestType(row[5]),
                        status=TestStatus(row[6]),
                        execution_time=row[7],
                        start_time=datetime.fromisoformat(row[8]),
                        end_time=datetime.fromisoformat(row[9]) if row[9] else None,
                        error_message=row[10],
                        error_traceback=row[11],
                        test_parameters=self._deserialize_dict(row[12]),
                        environment_info=self._deserialize_dict(row[13]),
                        tags=self._deserialize_list(row[14]),
                        created_at=datetime.fromisoformat(row[15])
                    )
                    executions.append(execution)
                
                return executions
        except Exception as e:
            self.logger.error(f"Failed to retrieve test executions: {e}")
            return []
    
    def get_issues(self,
                  status: Optional[IssueStatus] = None,
                  severity: Optional[IssueSeverity] = None,
                  component: Optional[str] = None,
                  limit: int = 100) -> List[Issue]:
        """Retrieve issues with filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM issues WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity.value)
                
                if component:
                    query += " AND component = ?"
                    params.append(component)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                issues = []
                for row in rows:
                    issue = Issue(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        severity=IssueSeverity(row[3]),
                        status=IssueStatus(row[4]),
                        issue_type=row[5],
                        component=row[6],
                        file_path=row[7],
                        line_number=row[8],
                        error_message=row[9],
                        error_traceback=row[10],
                        reproduction_steps=self._deserialize_list(row[11]),
                        expected_behavior=row[12],
                        actual_behavior=row[13],
                        test_execution_ids=self._deserialize_list(row[14]),
                        tags=self._deserialize_list(row[15]),
                        assignee=row[16],
                        reporter=row[17],
                        created_at=datetime.fromisoformat(row[18]),
                        updated_at=datetime.fromisoformat(row[19]),
                        resolved_at=datetime.fromisoformat(row[20]) if row[20] else None
                    )
                    issues.append(issue)
                
                return issues
        except Exception as e:
            self.logger.error(f"Failed to retrieve issues: {e}")
            return []
    
    def get_patterns(self, pattern_type: Optional[str] = None, limit: int = 100) -> List[Pattern]:
        """Retrieve patterns with filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM patterns WHERE 1=1"
                params = []
                
                if pattern_type:
                    query += " AND pattern_type = ?"
                    params.append(pattern_type)
                
                query += " ORDER BY frequency DESC, last_seen DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                patterns = []
                for row in rows:
                    pattern = Pattern(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        pattern_type=row[3],
                        signature=row[4],
                        frequency=row[5],
                        first_seen=datetime.fromisoformat(row[6]),
                        last_seen=datetime.fromisoformat(row[7]),
                        affected_components=self._deserialize_list(row[8]),
                        related_issues=self._deserialize_list(row[9]),
                        related_tests=self._deserialize_list(row[10]),
                        severity=IssueSeverity(row[11]),
                        suggested_fixes=self._deserialize_list(row[12]),
                        confidence_score=row[13],
                        tags=self._deserialize_list(row[14])
                    )
                    patterns.append(pattern)
                
                return patterns
        except Exception as e:
            self.logger.error(f"Failed to retrieve patterns: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall testing statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Test execution statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_tests,
                        SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed_tests,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tests,
                        SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped_tests,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_tests,
                        AVG(execution_time) as avg_execution_time
                    FROM test_executions
                """)
                test_stats = cursor.fetchone()
                
                # Issue statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_issues,
                        SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_issues,
                        SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_issues,
                        SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_issues
                    FROM issues
                """)
                issue_stats = cursor.fetchone()
                
                # Pattern statistics
                cursor.execute("SELECT COUNT(*) FROM patterns")
                pattern_count = cursor.fetchone()[0]
                
                return {
                    "test_executions": {
                        "total": test_stats[0],
                        "passed": test_stats[1],
                        "failed": test_stats[2],
                        "skipped": test_stats[3],
                        "error": test_stats[4],
                        "avg_execution_time": test_stats[5] or 0.0,
                        "success_rate": (test_stats[1] / test_stats[0] * 100) if test_stats[0] > 0 else 0.0
                    },
                    "issues": {
                        "total": issue_stats[0],
                        "open": issue_stats[1],
                        "resolved": issue_stats[2],
                        "critical": issue_stats[3]
                    },
                    "patterns": {
                        "total": pattern_count
                    }
                }
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old test executions
                cursor.execute("DELETE FROM test_executions WHERE created_at < ?", 
                             (cutoff_date.isoformat(),))
                
                # Clean up old test suites
                cursor.execute("DELETE FROM test_suites WHERE created_at < ?", 
                             (cutoff_date.isoformat(),))
                
                # Clean up old performance metrics
                cursor.execute("DELETE FROM performance_metrics WHERE timestamp < ?", 
                             (cutoff_date.isoformat(),))
                
                # Clean up old code coverage data
                cursor.execute("DELETE FROM code_coverage WHERE timestamp < ?", 
                             (cutoff_date.isoformat(),))
                
                conn.commit()
                self.logger.info(f"Cleaned up data older than {days} days")
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}") 