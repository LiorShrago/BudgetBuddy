#!/usr/bin/env python3
"""
Comprehensive test runner for the unified finances feature.

This script runs all test suites related to the unified finances feature,
including unit tests, integration tests, end-to-end tests, responsive design
tests, accessibility tests, and cross-browser tests.

Usage:
    python run_finances_tests.py [options]

Options:
    --unit           Run only unit tests
    --integration    Run only integration tests
    --e2e            Run only end-to-end tests
    --responsive     Run only responsive design tests
    --accessibility  Run only accessibility tests
    --cross-browser  Run cross-browser tests (Chrome, Firefox, Edge)
    --performance    Run performance tests
    --coverage       Generate test coverage report
    --html           Generate HTML report (with --coverage)
    --all            Run all tests (default)
    --headless       Run browser tests in headless mode
    --browsers       Comma-separated list of browsers to test (chrome,firefox,edge,safari)
"""

import os
import sys
import argparse
import subprocess
import time
import json
import datetime
import shutil


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run unified finances tests')
    
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests only')
    parser.add_argument('--responsive', action='store_true', help='Run responsive design tests only')
    parser.add_argument('--accessibility', action='store_true', help='Run accessibility tests only')
    parser.add_argument('--cross-browser', action='store_true', help='Run cross-browser tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--coverage', action='store_true', help='Generate test coverage report')
    parser.add_argument('--html', action='store_true', help='Generate HTML report (with --coverage)')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    parser.add_argument('--headless', action='store_true', help='Run browser tests in headless mode')
    parser.add_argument('--browsers', type=str, default='chrome', 
                       help='Comma-separated list of browsers to test (chrome,firefox,edge,safari)')
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run all tests
    if not (args.unit or args.integration or args.e2e or 
            args.responsive or args.accessibility or 
            args.cross_browser or args.performance):
        args.all = True
    
    # Create results directory
    results_dir = os.path.join('test_results', 'finances_tests', 
                             datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(results_dir, exist_ok=True)
    
    # Dictionary to store test results
    results = {
        'summary': {'passed': 0, 'failed': 0, 'skipped': 0, 'total': 0},
        'tests': {}
    }
    
    # Run unit tests
    if args.unit or args.all:
        print("\n=== Running JavaScript unit tests ===\n")
        results['tests']['unit'] = run_test_suite(
            'test_finances_js.py',
            'unit',
            args.coverage,
            args.html,
            results_dir
        )
        update_summary(results['summary'], results['tests']['unit'])
    
    # Run integration tests
    if args.integration or args.all:
        print("\n=== Running integration tests ===\n")
        results['tests']['integration'] = run_test_suite(
            'test_finances_integration.py',
            'integration',
            args.coverage,
            args.html,
            results_dir
        )
        update_summary(results['summary'], results['tests']['integration'])
    
    # Run end-to-end tests
    if args.e2e or args.all:
        print("\n=== Running end-to-end tests ===\n")
        results['tests']['e2e'] = run_test_suite(
            'test_finances_e2e.py',
            'e2e',
            args.coverage,
            args.html,
            results_dir,
            headless=args.headless
        )
        update_summary(results['summary'], results['tests']['e2e'])
    
    # Run responsive design tests
    if args.responsive or args.all:
        print("\n=== Running responsive design tests ===\n")
        results['tests']['responsive'] = run_test_suite(
            'test_finances_responsive_accessibility.py',
            'responsive',
            args.coverage,
            args.html,
            results_dir,
            headless=args.headless
        )
        update_summary(results['summary'], results['tests']['responsive'])
    
    # Run accessibility tests
    if args.accessibility or args.all:
        print("\n=== Running accessibility tests ===\n")
        results['tests']['accessibility'] = run_test_suite(
            'test_finances_responsive_accessibility.py',
            'accessibility',
            args.coverage,
            args.html,
            results_dir,
            headless=args.headless
        )
        update_summary(results['summary'], results['tests']['accessibility'])
    
    # Run cross-browser tests
    if args.cross_browser or args.all:
        browsers = args.browsers.split(',')
        print(f"\n=== Running cross-browser tests on {', '.join(browsers)} ===\n")
        
        results['tests']['cross_browser'] = {}
        for browser in browsers:
            print(f"\n--- Testing on {browser} ---\n")
            browser_result = run_cross_browser_test(
                browser,
                args.coverage,
                args.html,
                results_dir,
                headless=args.headless
            )
            results['tests']['cross_browser'][browser] = browser_result
            update_summary(results['summary'], browser_result)
    
    # Run performance tests
    if args.performance or args.all:
        print("\n=== Running performance tests ===\n")
        results['tests']['performance'] = run_performance_tests(results_dir)
        update_summary(results['summary'], results['tests']['performance'])
    
    # Save test results summary
    with open(os.path.join(results_dir, 'summary.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== Test Summary ===\n")
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Skipped: {results['summary']['skipped']}")
    
    if args.coverage and args.html:
        print(f"\nCoverage report: {os.path.join(results_dir, 'htmlcov/index.html')}")
    
    # Generate summary report
    generate_summary_report(results, results_dir)
    
    return 0 if results['summary']['failed'] == 0 else 1


def run_test_suite(test_file, marker=None, coverage=False, html=False, results_dir=None, headless=False):
    """Run a specific test suite."""
    cmd = ['python', '-m', 'pytest', test_file, '-v']
    
    if marker:
        cmd.extend(['-m', marker])
    
    if coverage:
        cmd.extend(['--cov=.', '--cov-report=term'])
        if html:
            cmd.append('--cov-report=html')
    
    if headless:
        cmd.extend(['--headless'])
    
    # Save output to file
    if results_dir:
        test_name = os.path.splitext(os.path.basename(test_file))[0]
        if marker:
            test_name = f"{test_name}_{marker}"
        output_file = os.path.join(results_dir, f"{test_name}_output.txt")
        
        with open(output_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
        
        # Read results for summary
        with open(output_file, 'r') as f:
            output = f.read()
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
    
    # Copy coverage report if generated
    if coverage and html and results_dir:
        if os.path.exists('htmlcov'):
            coverage_dir = os.path.join(results_dir, 'htmlcov')
            if os.path.exists(coverage_dir):
                shutil.rmtree(coverage_dir)
            shutil.copytree('htmlcov', coverage_dir)
    
    # Parse results
    tests_total = 0
    tests_passed = 0
    tests_failed = 0
    tests_skipped = 0
    
    # Extract summary line (looks like "5 passed, 2 failed, 1 skipped")
    summary_line = None
    for line in output.split('\n'):
        if "passed" in line and ("failed" in line or "skipped" in line) and "==" in line:
            summary_line = line.strip()
            break
    
    if summary_line:
        parts = summary_line.split()
        for i, part in enumerate(parts):
            if part.isdigit():
                tests_total += int(part)
                if i+1 < len(parts) and "passed" in parts[i+1]:
                    tests_passed += int(part)
                elif i+1 < len(parts) and "failed" in parts[i+1]:
                    tests_failed += int(part)
                elif i+1 < len(parts) and "skipped" in parts[i+1]:
                    tests_skipped += int(part)
    
    return {
        'total': tests_total,
        'passed': tests_passed,
        'failed': tests_failed,
        'skipped': tests_skipped,
        'exit_code': result.returncode
    }


def run_cross_browser_test(browser, coverage=False, html=False, results_dir=None, headless=False):
    """Run tests on a specific browser."""
    cmd = ['python', '-m', 'pytest', 'test_finances_e2e.py', '-v', '--browser', browser]
    
    if coverage:
        cmd.extend(['--cov=.', '--cov-report=term'])
        if html:
            cmd.append('--cov-report=html')
    
    if headless:
        cmd.extend(['--headless'])
    
    # Save output to file
    if results_dir:
        output_file = os.path.join(results_dir, f"cross_browser_{browser}_output.txt")
        
        with open(output_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
        
        # Read results for summary
        with open(output_file, 'r') as f:
            output = f.read()
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
    
    # Parse results
    tests_total = 0
    tests_passed = 0
    tests_failed = 0
    tests_skipped = 0
    
    # Extract summary line
    summary_line = None
    for line in output.split('\n'):
        if "passed" in line and ("failed" in line or "skipped" in line) and "==" in line:
            summary_line = line.strip()
            break
    
    if summary_line:
        parts = summary_line.split()
        for i, part in enumerate(parts):
            if part.isdigit():
                tests_total += int(part)
                if i+1 < len(parts) and "passed" in parts[i+1]:
                    tests_passed += int(part)
                elif i+1 < len(parts) and "failed" in parts[i+1]:
                    tests_failed += int(part)
                elif i+1 < len(parts) and "skipped" in parts[i+1]:
                    tests_skipped += int(part)
    
    return {
        'total': tests_total,
        'passed': tests_passed,
        'failed': tests_failed,
        'skipped': tests_skipped,
        'exit_code': result.returncode
    }


def run_performance_tests(results_dir=None):
    """Run performance tests."""
    # Simple performance tests using timeit
    import timeit
    
    # Define performance tests
    performance_tests = [
        {
            'name': 'page_load',
            'setup': '''
import requests
from requests.cookies import cookiejar_from_dict

# Setup session with auth cookies
session = requests.Session()
session.cookies = cookiejar_from_dict({'session': 'test_session_cookie'})
            ''',
            'stmt': '''
response = session.get('http://127.0.0.1:5000/finances')
            ''',
            'number': 10
        },
        {
            'name': 'api_transactions',
            'setup': '''
import requests
from requests.cookies import cookiejar_from_dict

# Setup session with auth cookies
session = requests.Session()
session.cookies = cookiejar_from_dict({'session': 'test_session_cookie'})
            ''',
            'stmt': '''
response = session.get('http://127.0.0.1:5000/api/account-transactions')
            ''',
            'number': 20
        }
    ]
    
    # Run the tests
    results = {}
    for test in performance_tests:
        try:
            execution_time = timeit.timeit(
                stmt=test['stmt'],
                setup=test['setup'],
                number=test['number']
            ) / test['number']  # Average time per execution
            
            results[test['name']] = {
                'time': execution_time,
                'passed': True
            }
            
            print(f"Performance test '{test['name']}': {execution_time:.4f} seconds")
        except Exception as e:
            results[test['name']] = {
                'time': 0,
                'passed': False,
                'error': str(e)
            }
            print(f"Performance test '{test['name']}' failed: {str(e)}")
    
    # Save results
    if results_dir:
        with open(os.path.join(results_dir, 'performance_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
    
    # Calculate success rate
    total = len(performance_tests)
    passed = sum(1 for test in results.values() if test['passed'])
    failed = total - passed
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': 0,
        'exit_code': 0 if failed == 0 else 1
    }


def update_summary(summary, results):
    """Update the summary with results from a test run."""
    summary['total'] += results['total']
    summary['passed'] += results['passed']
    summary['failed'] += results['failed']
    summary['skipped'] += results['skipped']


def generate_summary_report(results, results_dir):
    """Generate a summary HTML report."""
    report_path = os.path.join(results_dir, 'summary_report.html')
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unified Finances Tests Summary</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .passed { color: green; }
            .failed { color: red; }
            .skipped { color: orange; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>Unified Finances Tests Summary</h1>
        
        <div class="summary">
            <h2>Overall Summary</h2>
            <p>
                <strong>Total Tests:</strong> {total}<br>
                <strong class="passed">Passed:</strong> {passed}<br>
                <strong class="failed">Failed:</strong> {failed}<br>
                <strong class="skipped">Skipped:</strong> {skipped}
            </p>
        </div>
        
        <h2>Test Suite Results</h2>
        <table>
            <tr>
                <th>Suite</th>
                <th>Total</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Skipped</th>
                <th>Status</th>
            </tr>
    """.format(
        total=results['summary']['total'],
        passed=results['summary']['passed'],
        failed=results['summary']['failed'],
        skipped=results['summary']['skipped']
    )
    
    # Add rows for each test suite
    for suite_name, suite_results in results['tests'].items():
        if suite_name == 'cross_browser':
            # Add a row for each browser
            for browser, browser_results in suite_results.items():
                status = "PASSED" if browser_results['failed'] == 0 else "FAILED"
                status_class = "passed" if browser_results['failed'] == 0 else "failed"
                
                html += f"""
                <tr>
                    <td>{suite_name} ({browser})</td>
                    <td>{browser_results['total']}</td>
                    <td class="passed">{browser_results['passed']}</td>
                    <td class="failed">{browser_results['failed']}</td>
                    <td class="skipped">{browser_results['skipped']}</td>
                    <td class="{status_class}">{status}</td>
                </tr>
                """
        else:
            status = "PASSED" if suite_results['failed'] == 0 else "FAILED"
            status_class = "passed" if suite_results['failed'] == 0 else "failed"
            
            html += f"""
            <tr>
                <td>{suite_name}</td>
                <td>{suite_results['total']}</td>
                <td class="passed">{suite_results['passed']}</td>
                <td class="failed">{suite_results['failed']}</td>
                <td class="skipped">{suite_results['skipped']}</td>
                <td class="{status_class}">{status}</td>
            </tr>
            """
    
    # Complete the HTML
    html += """
        </table>
        
        <h2>Test Output Files</h2>
        <ul>
    """
    
    # Add links to output files
    for filename in os.listdir(results_dir):
        if filename.endswith('_output.txt'):
            html += f'<li><a href="{filename}">{filename}</a></li>\n'
    
    # Add link to coverage report if exists
    if os.path.exists(os.path.join(results_dir, 'htmlcov')):
        html += f'<li><a href="htmlcov/index.html">Coverage Report</a></li>\n'
    
    html += """
        </ul>
    </body>
    </html>
    """
    
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"\nSummary report: {report_path}")


if __name__ == '__main__':
    sys.exit(main()) 