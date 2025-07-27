"""
Command-line interface for testing metadata analysis.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

from .database import TestingMetadataDB
from .collector import TestingMetadataAPI

def format_table(data: list, headers: list) -> str:
    """Format data as a table."""
    if not data:
        return "No data available"
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Create header
    header = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-" * len(header)
    
    # Create rows
    rows = []
    for row in data:
        rows.append(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))
    
    return f"{header}\n{separator}\n" + "\n".join(rows)

def show_summary(api: TestingMetadataAPI):
    """Show overall summary."""
    print("=" * 60)
    print("TESTING METADATA SUMMARY")
    print("=" * 60)
    
    # Test summary
    test_summary = api.get_test_summary()
    print(f"\n📊 Test Results (Last 7 days):")
    print(f"   Total Tests: {test_summary['total_tests']}")
    print(f"   Passed: {test_summary['passed']} ✅")
    print(f"   Failed: {test_summary['failed']} ❌")
    print(f"   Skipped: {test_summary['skipped']} ⏭️")
    print(f"   Success Rate: {test_summary['success_rate']:.1f}%")
    print(f"   Avg Execution Time: {test_summary['avg_execution_time']:.2f}s")
    
    # Issue summary
    issue_summary = api.get_issue_summary()
    print(f"\n🐛 Issues:")
    print(f"   Total Issues: {issue_summary['total_issues']}")
    print(f"   Open Issues: {issue_summary['open_issues']} 🔴")
    print(f"   Resolved Issues: {issue_summary['resolved_issues']} ✅")
    print(f"   Critical Issues: {issue_summary.get('critical_issues', 0)} ⚠️")
    
    # Patterns summary
    patterns_summary = api.get_patterns_summary()
    print(f"\n🔄 Patterns:")
    print(f"   Total Patterns: {patterns_summary['total_patterns']}")
    print(f"   High Frequency: {patterns_summary['high_frequency_patterns']}")
    
    # Recommendations
    recommendations = api.get_recommendations()
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            priority_icon = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
            print(f"   {priority_icon} {rec['description']}")
            print(f"      💭 {rec['suggestion']}")
    
    print("=" * 60)

def show_recent_tests(api: TestingMetadataAPI, days: int = 7, limit: int = 20):
    """Show recent test executions."""
    from .metadata_models import TestStatus
    
    start_date = datetime.now() - timedelta(days=days)
    executions = api.db.get_test_executions(start_date=start_date, limit=limit)
    
    if not executions:
        print(f"No test executions found in the last {days} days.")
        return
    
    print(f"\n📋 Recent Test Executions (Last {days} days):")
    
    headers = ["Test", "Type", "Status", "Duration", "File"]
    data = []
    
    for execution in executions:
        status_icon = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌",
            TestStatus.SKIPPED: "⏭️",
            TestStatus.ERROR: "💥"
        }.get(execution.status, "❓")
        
        data.append([
            execution.test_name[:30] + "..." if len(execution.test_name) > 30 else execution.test_name,
            execution.test_type.value,
            f"{status_icon} {execution.status.value}",
            f"{execution.execution_time:.2f}s",
            Path(execution.test_file).name
        ])
    
    print(format_table(data, headers))

def show_issues(api: TestingMetadataAPI, status: str = None, severity: str = None, limit: int = 20):
    """Show issues."""
    from .metadata_models import IssueStatus, IssueSeverity
    
    # Parse filters
    status_filter = IssueStatus(status) if status else None
    severity_filter = IssueSeverity(severity) if severity else None
    
    issues = api.db.get_issues(status=status_filter, severity=severity_filter, limit=limit)
    
    if not issues:
        print("No issues found matching the criteria.")
        return
    
    print(f"\n🐛 Issues:")
    
    headers = ["Title", "Component", "Severity", "Status", "Created"]
    data = []
    
    for issue in issues:
        severity_icon = {
            IssueSeverity.CRITICAL: "🔴",
            IssueSeverity.HIGH: "🟠",
            IssueSeverity.MEDIUM: "🟡",
            IssueSeverity.LOW: "🟢"
        }.get(issue.severity, "❓")
        
        status_icon = {
            IssueStatus.OPEN: "🔴",
            IssueStatus.IN_PROGRESS: "🟡",
            IssueStatus.RESOLVED: "✅",
            IssueStatus.WONT_FIX: "❌"
        }.get(issue.status, "❓")
        
        data.append([
            issue.title[:40] + "..." if len(issue.title) > 40 else issue.title,
            issue.component,
            f"{severity_icon} {issue.severity.value}",
            f"{status_icon} {issue.status.value}",
            issue.created_at.strftime("%Y-%m-%d")
        ])
    
    print(format_table(data, headers))

def show_patterns(api: TestingMetadataAPI, limit: int = 10):
    """Show patterns."""
    patterns = api.db.get_patterns(limit=limit)
    
    if not patterns:
        print("No patterns found.")
        return
    
    print(f"\n🔄 Patterns:")
    
    headers = ["Name", "Type", "Frequency", "Severity", "Last Seen"]
    data = []
    
    for pattern in patterns:
        severity_icon = {
            IssueSeverity.CRITICAL: "🔴",
            IssueSeverity.HIGH: "🟠",
            IssueSeverity.MEDIUM: "🟡",
            IssueSeverity.LOW: "🟢"
        }.get(pattern.severity, "❓")
        
        data.append([
            pattern.name[:40] + "..." if len(pattern.name) > 40 else pattern.name,
            pattern.pattern_type,
            pattern.frequency,
            f"{severity_icon} {pattern.severity.value}",
            pattern.last_seen.strftime("%Y-%m-%d")
        ])
    
    print(format_table(data, headers))

def show_statistics(api: TestingMetadataAPI):
    """Show detailed statistics."""
    stats = api.db.get_statistics()
    
    print("\n📈 Detailed Statistics:")
    print(json.dumps(stats, indent=2, default=str))

def export_data(api: TestingMetadataAPI, output_file: str, format: str = "json"):
    """Export data to file."""
    if format == "json":
        data = {
            "test_summary": api.get_test_summary(),
            "issue_summary": api.get_issue_summary(),
            "patterns_summary": api.get_patterns_summary(),
            "recommendations": api.get_recommendations(),
            "statistics": api.db.get_statistics()
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Data exported to {output_file}")
    else:
        print(f"Unsupported format: {format}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Testing Metadata Analysis CLI")
    parser.add_argument("--db", default="testing_metadata.db", help="Database file path")
    parser.add_argument("--output", help="Output file for export")
    parser.add_argument("--format", choices=["json"], default="json", help="Export format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Summary command
    subparsers.add_parser("summary", help="Show overall summary")
    
    # Recent tests command
    recent_parser = subparsers.add_parser("recent", help="Show recent test executions")
    recent_parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    recent_parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    
    # Issues command
    issues_parser = subparsers.add_parser("issues", help="Show issues")
    issues_parser.add_argument("--status", choices=["open", "in_progress", "resolved", "wont_fix"], help="Filter by status")
    issues_parser.add_argument("--severity", choices=["low", "medium", "high", "critical"], help="Filter by severity")
    issues_parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    
    # Patterns command
    patterns_parser = subparsers.add_parser("patterns", help="Show patterns")
    patterns_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    
    # Statistics command
    subparsers.add_parser("stats", help="Show detailed statistics")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export data")
    export_parser.add_argument("--output", required=True, help="Output file")
    export_parser.add_argument("--format", choices=["json"], default="json", help="Export format")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database and API
    try:
        db = TestingMetadataDB(args.db)
        api = TestingMetadataAPI(db)
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "summary":
            show_summary(api)
        elif args.command == "recent":
            show_recent_tests(api, args.days, args.limit)
        elif args.command == "issues":
            show_issues(api, args.status, args.severity, args.limit)
        elif args.command == "patterns":
            show_patterns(api, args.limit)
        elif args.command == "stats":
            show_statistics(api)
        elif args.command == "export":
            export_data(api, args.output, args.format)
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 