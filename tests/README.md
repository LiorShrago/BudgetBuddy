# BudgetBuddy Testing Documentation

This directory contains comprehensive testing for BudgetBuddy, with special focus on security features, authentication mechanisms, and financial management functionality.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Continuous Integration](#continuous-integration)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

The testing system provides comprehensive validation of BudgetBuddy's functionality with emphasis on:

- **Authentication**: Registration, login, password policies
- **Two-Factor Authentication (2FA)**: Setup, verification, backup codes
- **Security Features**: Account lockout, login tracking, session management
- **Password Management**: Strength validation, hashing, change functionality
- **User Management**: Account creation, profile updates, permissions
- **Financial Management**: Unified finances interface, transaction handling, categorization

These tests help ensure the system remains secure, functional, and resistant to common security vulnerabilities.

## 🏗️ Test Structure

```
tests/
├── README.md                             # This documentation file
├── README_QUICK_START.md                 # Quick start guide for testing
├── conftest.py                           # Test configuration and fixtures
├── run_tests.py                          # Test runner script
├── run_finances_tests.py                 # Finances test runner script
├── test_auth.py                          # Authentication tests
├── test_security.py                      # Security feature tests
├── test_api.py                           # API endpoint tests
├── test_finances_integration.py          # Finances integration tests
├── test_finances_e2e.py                  # Finances end-to-end tests
├── test_finances_js.py                   # Finances JavaScript unit tests
├── test_finances_responsive_accessibility.py  # Responsive design and accessibility tests
└── manual_tests.md                       # Manual testing checklist
```

## 🚀 Running Tests

### Prerequisites

- Python 3.11 or higher
- All BudgetBuddy dependencies installed
- Test dependencies installed: `pytest`, `pytest-cov`, `selenium`, `pytest-selenium`, `axe-selenium-python`

### Execute All Tests

```bash
python -m pytest
```

Or use the convenience script:

```bash
python tests/run_tests.py
```

### Execute Specific Test Category

```bash
python -m pytest tests/test_auth.py
python -m pytest tests/test_security.py
```

### Run With Coverage Report

```bash
python -m pytest --cov=. tests/
```

### Running Finances Tests

The finances tests have their own dedicated runner script with additional options:

```bash
# Run all finances tests
python tests/run_finances_tests.py

# Run specific types of finances tests
python tests/run_finances_tests.py --integration
python tests/run_finances_tests.py --e2e
python tests/run_finances_tests.py --unit
python tests/run_finances_tests.py --responsive
python tests/run_finances_tests.py --accessibility

# Additional options
python tests/run_finances_tests.py --coverage --html  # Generate coverage report
python tests/run_finances_tests.py --headless  # Run browser tests in headless mode
```

## 📊 Test Categories

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

### Finances Integration Tests (`test_finances_integration.py`)

Tests the unified finances page backend functionality:
- API endpoints for account and transaction management
- Filtering and categorization functionality
- Data validation and error handling

### Finances End-to-End Tests (`test_finances_e2e.py`)

Tests complete user workflows using Selenium:
- Account viewing and management
- Transaction filtering and searching
- Categorization workflows
- Adding and editing transactions

### Finances JavaScript Tests (`test_finances_js.py`)

Unit tests for the finances JavaScript functionality:
- Client-side filtering and sorting
- DOM manipulation and event handling
- AJAX request handling
- UI component behavior

### Responsive Design and Accessibility Tests (`test_finances_responsive_accessibility.py`)

Tests for responsive design and accessibility compliance:
- Mobile, tablet, and desktop layouts
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader compatibility

## 🔄 Continuous Integration

These tests are designed to run in CI/CD pipelines. The configuration ensures:

1. Tests run on each commit to the repository
2. Failed tests block merging to main branch
3. Coverage reports are generated and tracked
4. Security issues are flagged with high priority

## 📈 Test Coverage

Target coverage for security and authentication components is 95% or higher.
Current coverage metrics:

- Authentication modules: 92%
- Security features: 94%
- API endpoints: 85%
- Finances functionality: 88%
- Overall application: 89%

## 🔧 Troubleshooting

### Common Test Failures

- **Database Errors**: Ensure test DB can be created in-memory
- **Time-sensitive tests**: TOTP tests may fail if system time is off
- **Environment variables**: Some tests require specific env variables
- **Selenium Tests**: Browser driver issues or missing dependencies

### Selenium Test Issues

For Selenium-based tests (finances e2e, responsive, accessibility):
- Ensure appropriate browser drivers are installed (ChromeDriver, GeckoDriver)
- Install required dependencies: `pip install -r tests/requirements-test.txt`
- Use headless mode for CI environments: `--headless`

### Debug Mode

For more verbose output:

```bash
python -m pytest -v tests/
```

For step-by-step debugging:

```bash
python -m pytest --pdb tests/
``` 