# BudgetBuddy - Personal Finance Management System

## Overview

BudgetBuddy is a comprehensive personal finance management application built with Flask. It provides users with tools to track multiple financial accounts, categorize transactions with AI assistance, set budgets, and gain insights into their financial health through visual dashboards and analytics.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite for development (configurable for PostgreSQL in production via DATABASE_URL)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login with comprehensive security features
- **Session Management**: Flask sessions with filesystem storage

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **UI Framework**: Bootstrap with dark theme support
- **Icons**: Feather Icons
- **Charts**: Chart.js for financial visualizations
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Security Architecture
- **Authentication**: Username/password with optional two-factor authentication (TOTP)
- **Session Security**: Secure session tokens, configurable timeouts
- **Password Security**: Strong password requirements, secure hashing
- **Account Protection**: Failed login attempt tracking with automatic lockouts
- **2FA Implementation**: TOTP with QR codes, backup codes for recovery

## Key Components

### Models (src/models/models.py)
- **User**: Authentication, security settings, 2FA configuration
- **Account**: Financial accounts (checking, savings, credit cards, investments, loans)
- **Transaction**: Financial movements with categorization
- **Category**: Transaction categorization system
- **Budget**: Budget management and tracking
- **LoginAttempt**: Security audit trail for login attempts

### Core Features
1. **Account Management**: Multi-account tracking with balance monitoring
2. **Transaction Processing**: CSV import with intelligent parsing and duplicate detection
3. **AI-Powered Categorization**: Enhanced categorization using Perplexity API for merchant research
4. **Unified Finances Interface**: Comprehensive financial overview with filtering and transaction management
5. **Budget Management**: Goal setting and spending tracking
6. **Dashboard Analytics**: Visual representation of financial data
7. **Security Features**: 2FA, account lockout, session management

### Routing Structure
- **Authentication Routes**: Login, registration, 2FA setup/verification
- **Core Application Routes**: Dashboard, accounts, transactions, categories, budgets
- **Unified Interface**: `/finances` route providing comprehensive financial management
- **API Endpoints**: RESTful endpoints for dynamic content and AJAX operations
- **Security Routes**: Security settings, 2FA management, login history

## Data Flow

### Transaction Processing Flow
1. **CSV Upload**: Users upload bank transaction files
2. **Intelligent Parsing**: Bank-specific parsers extract transaction data
3. **Duplicate Detection**: System identifies and prevents duplicate imports
4. **AI Categorization**: Enhanced categorization using online merchant research
5. **User Review**: Users can review and adjust categorizations
6. **Storage**: Validated transactions stored in database

### Authentication Flow
1. **Standard Login**: Username/password validation
2. **2FA Challenge**: TOTP code verification (if enabled)
3. **Session Creation**: Secure session establishment
4. **Access Control**: Route-based authorization checks
5. **Security Monitoring**: Failed attempt tracking and lockout management

### Financial Data Flow
1. **Account Aggregation**: Real-time balance calculations across all accounts
2. **Transaction Filtering**: Dynamic filtering by date, category, account, type
3. **Analytics Generation**: Spending pattern analysis and budget progress
4. **Visualization**: Chart generation for dashboard and reports

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **Werkzeug**: WSGI utilities and security helpers
- **Flask-Login**: User session management
- **Pandas**: CSV processing and data manipulation

### Security Dependencies
- **PyOTP**: Two-factor authentication (TOTP implementation)
- **QRCode**: QR code generation for 2FA setup
- **Pillow**: Image processing for QR codes

### AI Integration
- **Requests**: HTTP client for external API calls
- **Perplexity API**: Enhanced merchant categorization (requires API key)

### Frontend Dependencies
- **Bootstrap**: UI framework with dark theme
- **Chart.js**: Financial data visualization
- **Feather Icons**: Icon system

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with debug mode
- **Database**: SQLite for quick setup and testing
- **Session Storage**: Filesystem-based sessions
- **Configuration**: Environment variables for sensitive data

### Production Considerations
- **Database**: PostgreSQL recommended for production (via DATABASE_URL)
- **Session Storage**: Consider Redis or database-backed sessions for scalability
- **Security**: SSL/TLS termination, secure headers, environment-based secrets
- **Performance**: Gunicorn WSGI server, connection pooling, caching strategies

### Environment Configuration
Required environment variables:
- `SESSION_SECRET` or `FLASK_SECRET_KEY`: Session encryption key
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `PERPLEXITY_API_KEY`: API key for enhanced AI categorization (optional)

### File Upload Handling
- **Upload Directory**: Configurable upload folder for CSV files
- **File Size Limits**: 16MB maximum file size
- **Security**: File type validation and secure filename handling

## Changelog

- July 06, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.