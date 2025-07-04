# BudgetBuddy

BudgetBuddy is a comprehensive personal finance management application built with Flask. Track accounts, categorize transactions, set budgets, and gain insights into your financial health.

## Features

- **Account Management**: Track multiple financial accounts in one place
- **Transaction Categorization**: Organize transactions with AI-powered categorization
- **Dashboard**: Visual representation of financial data
- **Budgeting**: Set and track spending goals
- **Enhanced AI Categorization**: Online research for accurate transaction categorization
- **Secure Authentication**: Two-factor authentication and secure session management

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see Configuration section)
4. Run the application: `python app.py`
5. Visit http://localhost:5000 in your browser

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- [Project Changelog](docs/CHANGELOG.md)
- [Development Notes](docs/development/DEVELOPMENT_NOTES.md)
- [Debug Checklist](docs/development/DEBUG_CHECKLIST.md)
- [Testing Guide](docs/testing/TEST_DOCUMENTATION.md)

## Configuration

BudgetBuddy requires the following environment variables:

- `FLASK_SECRET_KEY`: Secret key for Flask session
- `PERPLEXITY_API_KEY`: API key for Perplexity service (for Enhanced AI Categorization)

## Development

See the [Development Notes](docs/development/DEVELOPMENT_NOTES.md) for detailed information on the codebase, architecture, and development practices.

## Testing

Run tests with:

```bash
python tests/run_tests.py
```

For more information, see the [Testing Guide](docs/testing/TEST_DOCUMENTATION.md).

## Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## License

This project is licensed under the MIT License. 