#!/usr/bin/env python3
"""
Main entry point for the Network UI application.

This script provides command-line interface for running the application,
API server, and various utilities.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_ui.api import create_app


def run_api_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask API server."""
    app = create_app()
    print(f"🚀 Starting Network UI API server on {host}:{port}")
    print(f"📊 API Documentation: http://{host}:{port}/health")
    app.run(host=host, port=port, debug=debug)


def run_tests():
    """Run the test suite."""
    print("🧪 Running Network UI test suite...")
    os.system("python scripts/development/run_tests.py")


def run_demo():
    """Run the demo script."""
    print("🎯 Running Network UI demo...")
    os.system("python tests/functional/demo.py")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Network UI - Network visualization and analysis platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py server                    # Start API server
  python main.py server --port 8080       # Start server on port 8080
  python main.py server --debug           # Start server in debug mode
  python main.py test                     # Run test suite
  python main.py demo                     # Run demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start API server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    server_parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    server_parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run test suite')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo')
    
    args = parser.parse_args()
    
    if args.command == 'server':
        run_api_server(host=args.host, port=args.port, debug=args.debug)
    elif args.command == 'test':
        run_tests()
    elif args.command == 'demo':
        run_demo()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main() 