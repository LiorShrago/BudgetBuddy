# BudgetBuddy Test Framework Quick Start Guide

## Setup

1. Install test dependencies:
   ```bash
   pip install -r tests/requirements-test.txt
   ```

2. Make sure your application is properly set up with a database.

## Running Tests

### Run all tests:
```bash
python tests/run_tests.py
```

### Run specific test categories:
```bash
# Authentication tests only
python tests/run_tests.py --auth

# Security tests only
python tests/run_tests.py --security

# API tests only
python tests/run_tests.py --api
```

### Generate test coverage report:
```bash
python tests/run_tests.py --coverage

# Generate HTML coverage report
python tests/run_tests.py --coverage --html
```

## Test Categories

1. **Authentication Tests** (`test_auth.py`):
   - User registration
   - Password validation
   - Login functionality
   - Two-factor authentication
   - Password management

2. **Security Tests** (`test_security.py`):
   - Session management
   - Account lockout
   - Access control
   - Login security
   - Protection mechanisms

3. **API Tests** (`test_api.py`):
   - API endpoints
   - Error handling
   - Authorization checks
   - Data validation

## Manual Testing

Some features require manual testing. Use the manual testing checklist:
```bash
# Open manual testing checklist
open tests/manual_tests.md  # On macOS
notepad tests/manual_tests.md  # On Windows
```

## Test Structure

- **Fixtures**: Reusable components in `conftest.py`
- **Test Files**: Organized by functionality
- **Test Classes**: Group related test cases
- **Manual Tests**: Checklist for features that need human verification

## Troubleshooting

If tests fail, check:

1. **Database setup**: Make sure you're using a test database
2. **Environment**: Ensure FLASK_ENV=testing is set
3. **Dependencies**: Verify all test dependencies are installed
4. **Permissions**: Ensure write access to the test directory

## Adding New Tests

When adding new tests:

1. Use appropriate test class
2. Leverage existing fixtures when possible
3. Keep tests isolated and independent
4. Focus on one feature per test case
5. Use descriptive test names

## Code Coverage

Aim for at least 80% code coverage, with critical security features at 90%+.
Coverage reports are generated in `tests/coverage/` when using `--coverage --html`. 