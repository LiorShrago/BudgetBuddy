#!/usr/bin/env python3
"""
BudgetBuddy Test Runner
======================

This script runs all tests for the BudgetBuddy application.
"""

import os
import sys
import argparse
import importlib.util
import unittest
import traceback

def run_tests_with_pytest(args):
    """Run tests using pytest if available."""
    try:
        import pytest
        print("=== Running BudgetBuddy Tests with pytest ===")

        # Determine test files to run
        test_files = ['test_auth.py', 'test_security.py', 'test_api.py']
        test_files_str = ', '.join(test_files)
        print(f"Test files: {test_files_str}")

        # Construct pytest arguments
        pytest_args = []
        if args.verbose:
            pytest_args.append('-v')
        if args.coverage:
            pytest_args.extend(['--cov=.', '--cov-report=term-missing'])
        if args.test_file:
            pytest_args.append(args.test_file)
        else:
            for test_file in test_files:
                file_path = os.path.join(os.path.dirname(__file__), test_file)
                if os.path.exists(file_path):
                    pytest_args.append(file_path)
                else:
                    print(f"Warning: Test file {file_path} not found")

        # Run pytest
        return pytest.main(pytest_args)
    except ImportError:
        print("\nPytest not available, falling back to unittest...")
        return run_tests_with_unittest(args)
    except Exception as e:
        print(f"\nError running pytest: {str(e)}")
        traceback.print_exc()
        return run_tests_with_unittest(args)

def run_tests_with_unittest(args):
    """Run tests using unittest as a fallback."""
    print("\n=== Running BudgetBuddy Tests with unittest ===")
    
    # Define test directory
    test_dir = os.path.dirname(__file__)
    
    # Add parent directory to path
    sys.path.insert(0, os.path.abspath(os.path.join(test_dir, '..')))
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add specific test file or discover all tests
    if args.test_file:
        if os.path.exists(args.test_file):
            if args.test_file.endswith('.py'):
                # Load tests from the specified file
                module_name = os.path.basename(args.test_file)[:-3]
                spec = importlib.util.spec_from_file_location(module_name, args.test_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                suite.addTest(loader.loadTestsFromModule(module))
            else:
                print(f"Error: {args.test_file} is not a Python file")
                return 1
        else:
            print(f"Error: Test file {args.test_file} not found")
            return 1
    else:
        # Discover all tests in the test directory
        test_files = ['test_auth.py', 'test_security.py', 'test_api.py']
        for test_file in test_files:
            file_path = os.path.join(test_dir, test_file)
            if os.path.exists(file_path):
                module_name = test_file[:-3]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        suite.addTest(loader.loadTestsFromModule(module))
                    except Exception as e:
                        print(f"Error loading {file_path}: {str(e)}")
                        traceback.print_exc()
    
    # Run tests
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run BudgetBuddy tests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Run tests in verbose mode')
    parser.add_argument('-c', '--coverage', action='store_true', help='Run tests with coverage report')
    parser.add_argument('-f', '--test-file', help='Specify a single test file to run')
    parser.add_argument('-u', '--use-unittest', action='store_true', help='Force using unittest instead of pytest')
    args = parser.parse_args()
    
    # Run tests with appropriate framework
    if args.use_unittest:
        return run_tests_with_unittest(args)
    else:
        return run_tests_with_pytest(args)

if __name__ == '__main__':
    sys.exit(main()) 