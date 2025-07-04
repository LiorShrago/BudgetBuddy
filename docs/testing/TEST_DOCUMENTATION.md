# BudgetBuddy Testing Documentation

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Manual Testing](#manual-testing)
- [Enhanced AI Testing](#enhanced-ai-testing)
- [Unified Finances Testing](#unified-finances-testing)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)
- [Adding New Tests](#adding-new-tests)

## Overview

The testing system provides comprehensive validation of BudgetBuddy's functionality with emphasis on:

- **Authentication**: Registration, login, password policies
- **Two-Factor Authentication (2FA)**: Setup, verification, backup codes
- **Security Features**: Account lockout, login tracking, session management
- **Password Management**: Strength validation, hashing, change functionality
- **User Management**: Account creation, profile updates, permissions
- **AI Categorization**: Enhanced transaction categorization with online research
- **Unified Finances**: Comprehensive account and transaction management

These tests help ensure the system remains secure, functional, and resistant to common security vulnerabilities.

## Test Structure

```
tests/
├── README.md                               # Main documentation file
├── README_QUICK_START.md                   # Quick start guide
├── conftest.py                             # Test configuration and fixtures
├── conftest_selenium.py                    # Selenium test configuration
├── run_tests.py                            # Main test runner script
├── run_enhanced_ai_tests.py                # Enhanced AI test runner
├── run_finances_tests.py                   # Unified finances test runner
├── test_auth.py                            # Authentication tests
├── test_security.py                        # Security feature tests
├── test_api.py                             # API endpoint tests
├── test_dashboard.py                       # Dashboard functionality tests
├── test_enhanced_ai_categorizer.py         # AI categorizer unit tests
├── test_enhanced_ai_api_endpoints.py       # AI API endpoint tests
├── test_enhanced_ai_live_integration.py    # AI live integration tests
├── test_finances_js.py                     # Finances JavaScript unit tests
├── test_finances_integration.py            # Finances integration tests
├── test_finances_e2e.py                    # Finances end-to-end tests
├── test_finances_responsive_accessibility.py # Finances responsive & accessibility tests
└── manual_tests.md                         # Manual testing checklist
```

## Running Tests

### Prerequisites

- Python 3.11 or higher
- All BudgetBuddy dependencies installed
- Test dependencies installed: `pip install -r tests/requirements-test.txt`

### Quick Start

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --auth      # Authentication tests only
python tests/run_tests.py --security  # Security tests only
python tests/run_tests.py --api       # API tests only

# Generate test coverage report
python tests/run_tests.py --coverage

# Generate HTML coverage report
python tests/run_tests.py --coverage --html

# Run unified finances tests
python tests/run_finances_tests.py
```

### Execute All Tests with Pytest Directly

```bash
python -m pytest
```

### Execute Specific Test Files

```bash
python -m pytest tests/test_auth.py
python -m pytest tests/test_security.py
python -m pytest tests/test_finances_js.py
```

### Run With Coverage Report

```bash
python -m pytest --cov=. tests/
```

## Test Categories

### Authentication Tests (`test_auth.py`)

Tests user authentication flows including:
- User registration with validation
- Login process with various credentials
- Password strength enforcement
- Two-factor authentication setup and verification
- Backup code generation and usage

### Security Tests (`test_security.py`)

Validates security mechanisms including:
- Account lockout after failed attempts
- Password hashing and verification
- Session management and security
- Login attempt logging and monitoring
- IP tracking and suspicious activity detection

### API Tests (`test_api.py`)

Tests API endpoints for:
- CSRF protection
- Input validation
- Authorization checks
- Response format and security headers

### Dashboard Tests (`test_dashboard.py`)

Tests dashboard functionality including:
- Financial metrics calculation
- UI component rendering
- Data aggregation and display
- Interactive features

### Enhanced AI Tests

The enhanced AI categorization system has its own comprehensive test suite:

- **Unit Tests** (`test_enhanced_ai_categorizer.py`): Tests core AI categorization functions
- **API Tests** (`test_enhanced_ai_api_endpoints.py`): Tests AI API endpoints
- **Integration Tests** (`test_enhanced_ai_live_integration.py`): Tests live integration with Perplexity API

To run just the enhanced AI tests:

```bash
python tests/run_enhanced_ai_tests.py
```

## Manual Testing

Some features require manual testing. Use the manual testing checklist:

```bash
# Open manual testing checklist
open tests/manual_tests.md  # On macOS
notepad tests/manual_tests.md  # On Windows
```

The manual testing checklist covers:
- UI functionality that's difficult to test automatically
- User experience flows
- Visual rendering and layout
- Interactive features
- Cross-browser compatibility

## Enhanced AI Testing

The enhanced AI categorization system requires special testing considerations:

1. **Environment Setup**:
   - Set `PERPLEXITY_API_KEY` environment variable for live tests
   - Use mock responses for unit tests to avoid API costs

2. **Test Categories**:
   - Unit tests for core functionality
   - API endpoint tests for integration
   - Live tests with real API calls (optional, requires API key)

3. **Running AI Tests**:
   ```bash
   # Run all AI tests
   python tests/run_enhanced_ai_tests.py
   
   # Run without live API tests
   python tests/run_enhanced_ai_tests.py --skip-live
   
   # Run with coverage
   python tests/run_enhanced_ai_tests.py --coverage
   ```

## Unified Finances Testing

The unified finances feature has a comprehensive testing suite covering:

- JavaScript unit tests
- Integration tests for backend/API
- End-to-end workflow tests
- Responsive design tests
- Accessibility tests
- Cross-browser compatibility tests
- Performance tests

For detailed information, see [FINANCES_TEST_DOCUMENTATION.md](FINANCES_TEST_DOCUMENTATION.md).

To run unified finances tests:

```bash
# Run all finances tests
python tests/run_finances_tests.py

# Run specific test categories
python tests/run_finances_tests.py --unit           # JavaScript unit tests
python tests/run_finances_tests.py --integration    # Integration tests
python tests/run_finances_tests.py --e2e            # End-to-end tests
python tests/run_finances_tests.py --responsive     # Responsive design tests
python tests/run_finances_tests.py --accessibility  # Accessibility tests
python tests/run_finances_tests.py --cross-browser  # Cross-browser tests
python tests/run_finances_tests.py --performance    # Performance tests
```

## Test Coverage

Target coverage for security and authentication components is 95% or higher.
Current coverage metrics:

- Authentication modules: 92%
- Security features: 94%
- API endpoints: 85%
- Enhanced AI categorization: 90%
- Unified finances interface: 88%
- Overall application: 89%

To generate an HTML coverage report:

```bash
python tests/run_tests.py --coverage --html
```

## Troubleshooting

### Common Test Failures

- **Database Errors**: Ensure test DB can be created in-memory
- **Time-sensitive tests**: TOTP tests may fail if system time is off
- **Environment variables**: Some tests require specific env variables
- **API limitations**: Enhanced AI tests may fail due to API rate limits
- **Selenium issues**: WebDriver version may need to match browser version

### Debug Mode

For more verbose output:

```bash
python -m pytest -v tests/
```

For step-by-step debugging:

```bash
python -m pytest --pdb tests/
```

### Known Issues

- TOTP validation tests may occasionally fail due to timing issues
- Live API tests require valid API credentials
- Some tests may be sensitive to database state
- Selenium tests may be flaky due to timing or element visibility issues

## Adding New Tests

When adding new tests:

1. Use appropriate test class
2. Leverage existing fixtures when possible
3. Keep tests isolated and independent
4. Focus on one feature per test case
5. Use descriptive test names

For AI categorization tests:
1. Use mocks for API calls in unit tests
2. Keep live API calls in separate test files
3. Add appropriate test fixtures in conftest.py 