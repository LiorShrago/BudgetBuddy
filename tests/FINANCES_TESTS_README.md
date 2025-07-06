# Finances Tests

This document provides instructions on how to run the tests for the unified finances feature.

## Prerequisites

The finances tests require several dependencies that need to be installed before running the tests:

```bash
pip install -r tests/requirements-test.txt
```

Key dependencies include:
- pytest
- selenium
- pytest-selenium
- axe-selenium-python

## Running the Tests

### Using the Test Runner

The simplest way to run the finances tests is to use the provided test runner script:

```bash
python tests/run_finances_tests.py
```

This will install the required dependencies and run all tests.

### Running Specific Test Types

You can run specific types of tests using the following options:

```bash
# Run only integration tests
python tests/run_finances_tests.py --integration

# Run only unit tests
python tests/run_finances_tests.py --unit

# Run only end-to-end tests
python tests/run_finances_tests.py --e2e

# Run only responsive design tests
python tests/run_finances_tests.py --responsive

# Run only accessibility tests
python tests/run_finances_tests.py --accessibility
```

### Additional Options

The test runner supports several additional options:

```bash
# Skip dependency installation
python tests/run_finances_tests.py --skip-deps

# Generate test coverage report
python tests/run_finances_tests.py --coverage

# Generate HTML coverage report
python tests/run_finances_tests.py --coverage --html

# Run browser tests in headless mode
python tests/run_finances_tests.py --headless

# Run cross-browser tests on specific browsers
python tests/run_finances_tests.py --cross-browser --browsers chrome,firefox
```

## Running Tests Directly with pytest

You can also run the tests directly using pytest:

```bash
# Run integration tests
pytest tests/test_finances_integration.py -m integration

# Run unit tests
pytest tests/test_finances_js.py -m unit

# Run end-to-end tests
pytest tests/test_finances_e2e.py -m e2e
```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing modules like `selenium`, make sure to install the required dependencies:

```bash
pip install -r tests/requirements-test.txt
```

### Browser Driver Issues

For Selenium tests, you need to have the appropriate browser drivers installed and in your PATH:

- Chrome: Download ChromeDriver from https://chromedriver.chromium.org/
- Firefox: Download GeckoDriver from https://github.com/mozilla/geckodriver/releases

### Test Failures

If tests fail, check the following:

1. Make sure the application server is running
2. Verify that the test user exists in the database
3. Check that the test database has appropriate test data

## Test Results

Test results are saved in the `test_results/finances_tests/` directory, organized by timestamp. Each run creates a new directory with:

- Test output logs
- Summary JSON file
- Coverage reports (if requested) 