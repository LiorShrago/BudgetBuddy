# BudgetBuddy Documentation

Welcome to the BudgetBuddy documentation! This directory contains comprehensive documentation for the BudgetBuddy project.

## Documentation Structure

- **[CHANGELOG.md](CHANGELOG.md)**: Complete project changelog
- **[UNIFIED_FINANCES_USER_GUIDE.md](UNIFIED_FINANCES_USER_GUIDE.md)**: User guide for the unified finances interface
- **[Development](development/)**: Developer documentation
  - **[DEVELOPMENT_NOTES.md](development/DEVELOPMENT_NOTES.md)**: Technical notes for developers
  - **[DEBUG_CHECKLIST.md](development/DEBUG_CHECKLIST.md)**: Debugging procedures and checklists
  - **[UNIFIED_FINANCES.md](development/UNIFIED_FINANCES.md)**: Documentation for the unified finances interface
- **[Testing](testing/)**: Testing documentation
  - **[TEST_DOCUMENTATION.md](testing/TEST_DOCUMENTATION.md)**: Comprehensive testing guide
  - **[FINANCES_TEST_DOCUMENTATION.md](testing/FINANCES_TEST_DOCUMENTATION.md)**: Unified finances testing guide

## Features

BudgetBuddy is a personal finance management application with the following key features:

1. **Account Management**: Track multiple financial accounts in one place
2. **Transaction Categorization**: Organize transactions with AI-powered categorization
3. **Dashboard**: Visual representation of financial data
4. **Budgeting**: Set and track spending goals
5. **Enhanced AI Categorization**: Online research for accurate transaction categorization
6. **Secure Authentication**: Two-factor authentication and secure session management
7. **Unified Financial Overview**: Comprehensive financial management in a single interface

## Getting Started

1. **Installation**: See [Installation Guide](installation.md) (TODO)
2. **Configuration**: Configuration options and environment variables
3. **Development**: Development setup and guidelines
4. **Testing**: Comprehensive testing procedures

## Contributing

1. Review the [DEVELOPMENT_NOTES.md](development/DEVELOPMENT_NOTES.md)
2. Set up your development environment
3. Make changes following our coding standards
4. Run tests using the procedures in [TEST_DOCUMENTATION.md](testing/TEST_DOCUMENTATION.md)
5. Submit a pull request

## Project Structure

```
BudgetBuddy/
├── app.py                # Main application entry point
├── src/                  # Source code directory
│   ├── models/           # Database models
│   ├── routs/            # Route handlers
│   └── services/         # Business logic services
├── templates/            # Jinja2 templates
├── static/               # Static assets (CSS, JS, images)
├── tests/                # Test suite
│   ├── conftest.py       # Test configuration and fixtures
│   ├── conftest_selenium.py # Selenium test configuration
│   ├── run_tests.py      # Main test runner script
│   ├── run_finances_tests.py # Unified finances test runner
│   └── test_*.py         # Test files
└── docs/                 # Documentation (you are here)
```

## Maintenance and Support

For issues or support:
1. Check the [DEBUG_CHECKLIST.md](development/DEBUG_CHECKLIST.md)
2. Review common issues in the development notes
3. Run relevant tests to identify the problem

## Changelog

For a complete history of changes, see [CHANGELOG.md](CHANGELOG.md) 