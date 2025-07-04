# BudgetBuddy Development Notes

## Authentication System

### Login Flow
- Standard login: username + password → dashboard
- 2FA login: username + password → 2FA code entry → dashboard
- Session variables used:
  - `pending_user_id`: Stores User.id during 2FA flow
  - `pending_username`: Stores username during 2FA flow

### Critical Components
- `login()` route in routes.py handles all authentication logic
- `User` model in models.py contains all user auth methods
- Templates:
  - login.html: Handles both initial login and 2FA verification
  - register.html: User registration form

### Two-Factor Authentication (2FA)
- Implementation uses pyotp library for TOTP generation and verification
- QR code generation via qrcode library and base64 encoding
- TOTP verification:
  - Normalizes input (removes spaces, non-numeric characters)
  - First tries exact match, then falls back to wider window (±5 intervals = ±2.5 minutes)
  - Handles exceptions from TOTP library
  - Provides detailed error feedback to users
- Backup codes for recovery:
  - 10 random hex codes generated when 2FA is enabled
  - Stored as JSON in the database
  - Single-use only (removed when used)

### Debugging Authentication Issues
1. Check database for user existence
2. Verify password hash matches stored hash
3. Inspect session variables during 2FA flow
4. Ensure 2FA tokens are being generated/validated correctly
5. Check for account lockout due to failed attempts

### Flask Session Configuration
- Session type: filesystem
- Session location: flask_session/ directory
- Session lifetime: 30 minutes
- Session permanence: False (cookie expires when browser closes)

## Database Schema

### Core Models
- User: Authentication and profile
- Account: Financial accounts (checking, savings, credit)
- Transaction: Financial movements
- Category: Transaction categorization
- Budget: Spending limits
- BudgetItem: Individual budget allocations

### Security-related Models
- LoginAttempt: Track login success/failure

## Front-End Architecture

### Key Templates
- base.html: Main layout, navigation, JavaScript dependencies
- login.html: Authentication forms
- register.html: Registration form
- dashboard.html: Main user interface
- setup_2fa.html: Two-factor authentication setup interface
- 2fa_backup_codes.html: Displays backup codes after 2FA setup

### JavaScript Dependencies
- Bootstrap 5.3.0: UI framework
- jQuery 3.6.0: DOM manipulation
- Chart.js: Visualization
- Feather Icons: UI icons

### CSS Organization
- Bootstrap core styles
- Custom styles in static/css/custom.css

## Testing Framework

### Test Structure
- `conftest.py`: Fixtures for test database, users, sessions
- `test_auth.py`: Authentication tests (registration, login, 2FA)
- `test_security.py`: Security tests (sessions, access control)
- `test_api.py`: API endpoint tests (data validation, error handling)
- `manual_tests.md`: Checklist for manual testing

### Running Tests
- Use `run_tests.py` to execute test suite
- Options for specific test categories and coverage reports

### Test Database
- In-memory SQLite database for fast tests
- Separate test session directory

## Security Considerations

### Password Management
- Passwords stored as hashes using werkzeug.security
- Password requirements enforced in registration/change flows
- Account lockout after 5 failed attempts (30-minute duration)

### Two-Factor Authentication
- TOTP implementation using pyotp library
- QR code generation with qrcode library
- Backup codes for account recovery
- Compatibility issues:
  - Microsoft Authenticator may have time synchronization issues
  - Specific setup instructions provided for Microsoft Authenticator
  - Input normalization ensures consistent format handling

### Session Security
- Secret key generated randomly if not provided in environment
- Session data stored server-side in filesystem
- Session cookies HTTP-only and secure

## Common Issues and Fixes

### Login Problems
- Issue: User cannot log in despite correct credentials
  - Possible causes: 
    - Account locked due to failed attempts
    - Session variables not being preserved
    - Password hash mismatch
    - 2FA token validation failure
  - Fix approaches:
    - Reset failed login attempts in database
    - Ensure session configuration is correct
    - Verify password hashing algorithm
    - Check TOTP secret generation and verification

### 2FA Problems
- Issue: "Invalid code" errors during 2FA setup or login
  - Possible causes:
    - Time synchronization issues between server and device
    - User entering expired codes
    - Incorrectly entered secret key
    - App compatibility issues
  - Fix approaches:
    - Increase the validation window (now ±5 intervals)
    - Normalize input to handle format variations
    - Add detailed troubleshooting instructions
    - Add app-specific setup instructions

### Database Issues
- Issue: Database errors during user operations
  - Possible causes:
    - Schema changes without migration
    - SQLite locking issues
    - Connection pool exhaustion
  - Fix approaches:
    - Recreate database with current schema
    - Use db.create_all() within app context
    - Configure connection pooling appropriately

### Front-End Issues
- Issue: UI components not working properly
  - Possible causes:
    - JavaScript errors
    - Missing dependencies
    - CSS conflicts
  - Fix approaches:
    - Check browser console for errors
    - Verify all JS/CSS dependencies are loaded
    - Inspect DOM elements for correct structure 