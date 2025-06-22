# BudgetBuddy Testing Documentation

This directory contains comprehensive testing for BudgetBuddy, with special focus on security features and authentication mechanisms.

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

These tests help ensure the system remains secure, functional, and resistant to common security vulnerabilities.

## 🏗️ Test Structure

```
tests/
├── README.md                  # This documentation file
├── conftest.py                # Test configuration and fixtures
├── run_tests.py               # Test runner script
├── test_auth.py               # Authentication tests
├── test_security.py           # Security feature tests
├── test_api.py                # API endpoint tests
└── manual_tests.md            # Manual testing checklist
```

## 🚀 Running Tests

### Prerequisites

- Python 3.11 or higher
- All BudgetBuddy dependencies installed
- Test dependencies installed: `pytest`, `pytest-cov`

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
- Overall application: 89%

## 🔧 Troubleshooting

### Common Test Failures

- **Database Errors**: Ensure test DB can be created in-memory
- **Time-sensitive tests**: TOTP tests may fail if system time is off
- **Environment variables**: Some tests require specific env variables

### Debug Mode

For more verbose output:

```bash
python -m pytest -v tests/
```

For step-by-step debugging:

```bash
python -m pytest --pdb tests/
``` 