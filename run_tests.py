#!/usr/bin/env python3
"""
Test runner script for Kubli encryption/decryption application.

This script provides an easy way to run all tests with proper coverage reporting.
It can run all tests, only unit tests, only integration tests, or specific test files.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --file test_name   # Run specific test file
    python run_tests.py --help             # Show help
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a shell command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {command[0]}")
        print("Make sure pytest is installed: pip install -r requirements.txt")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pytest
        import cryptography
        import colorama
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Test runner for Kubli encryption/decryption application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests (encryption and decryption modules)"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file (e.g., 'test_encryption')"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Kubli Test Runner")
    print(f"Project root: {project_root}")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add coverage options if not disabled
    if not args.no_coverage:
        pytest_cmd.extend([
            "--cov=utils",
            "--cov=kubli",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_html"
        ])
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")
    else:
        pytest_cmd.append("-v")  # Always use verbose for better output
    
    # Determine which tests to run
    if args.file:
        # Run specific test file
        test_file = f"tests/test_{args.file}.py" if not args.file.startswith("test_") else f"tests/{args.file}.py"
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return 1
        pytest_cmd.append(test_file)
        description = f"specific test file: {test_file}"
    elif args.unit:
        # Run only unit tests
        pytest_cmd.extend(["tests/test_encryption.py", "tests/test_decryption.py"])
        description = "unit tests"
    elif args.integration:
        # Run only integration tests
        pytest_cmd.append("tests/test_integration.py")
        description = "integration tests"
    else:
        # Run all tests
        pytest_cmd.append("tests/")
        description = "all tests"
    
    # Run the tests
    success = run_command(pytest_cmd, f"Running {description}")
    
    if success and not args.no_coverage:
        print(f"\n📊 Coverage report generated in: {project_root}/coverage_html/index.html")
        print("You can open this file in a web browser to view detailed coverage information.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
