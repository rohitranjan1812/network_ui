#!/usr/bin/env python3
"""
Run tests with metadata collection enabled.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_tests_with_metadata(test_path: str = "tests/", db_path: str = "testing_metadata.db", 
                           additional_args: list = None):
    """Run tests with metadata collection."""
    
    # Set environment variable for database path
    os.environ['TESTING_METADATA_DB'] = db_path
    
    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    # Add additional arguments
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"Running tests with metadata collection...")
    print(f"Database: {db_path}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        # Run pytest
        result = subprocess.run(cmd, check=False)
        
        print("-" * 60)
        print(f"Tests completed with exit code: {result.returncode}")
        
        # Show metadata summary if database exists
        if Path(db_path).exists():
            print("\nGenerating metadata summary...")
            try:
                summary_cmd = [
                    sys.executable, "-m", "network_ui.testing.cli",
                    "--db", db_path, "summary"
                ]
                subprocess.run(summary_cmd, check=False)
            except Exception as e:
                print(f"Could not generate summary: {e}")
        
        return result.returncode
    
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests with metadata collection")
    parser.add_argument("test_path", nargs="?", default="tests/", 
                       help="Path to test directory or file")
    parser.add_argument("--db", default="testing_metadata.db",
                       help="Database file path for metadata")
    parser.add_argument("--coverage", action="store_true",
                       help="Run with coverage reporting")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--markers", nargs="+",
                       help="Run only tests with specific markers")
    parser.add_argument("--exclude", nargs="+",
                       help="Exclude tests with specific markers")
    
    args, unknown = parser.parse_known_args()
    
    # Build additional arguments
    additional_args = []
    
    if args.coverage:
        additional_args.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    if args.parallel:
        additional_args.extend(["-n", "auto"])
    
    if args.markers:
        for marker in args.markers:
            additional_args.extend(["-m", marker])
    
    if args.exclude:
        for marker in args.exclude:
            additional_args.extend(["-m", f"not {marker}"])
    
    # Add any unknown arguments
    additional_args.extend(unknown)
    
    # Run tests
    exit_code = run_tests_with_metadata(
        test_path=args.test_path,
        db_path=args.db,
        additional_args=additional_args
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 