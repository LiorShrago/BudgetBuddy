######## TEMPLATE ########
## {{date}}
### Added
### Changed
### Fixed
#########################


# BudgetBuddy Project Changelog


## Table of Contents
- [Overview](#overview)
- [Change Log](#change-log)
  - [Authentication System](#authentication-system)
  - [User Interface](#user-interface)
  - [Backend](#backend)
  - [Performance](#performance)
  - [Security](#security)
- [Known Issues](#known-issues)
- [Future Improvements](#future-improvements)

## Overview
This changelog tracks all modifications, fixes, and improvements made to the BudgetBuddy project. Each entry includes detailed notes about the changes, reasoning, and impacts on the system.

## Change Log

### Backend
- **[2025-06-22]** Restructured project directory:
  - Reorganized codebase into a more modular structure
  - Moved models to src/models/
  - Moved routes to src/routs/
  - Moved services to src/services/
  - Renamed project_changelog.md to CHANGELOG.md for better standardization
  - Updated import paths across the project
  - Issue: Project structure was flat and difficult to maintain
  - Root cause: Initial development focused on functionality over structure

### Authentication System
- **[2025-06-20]** Fixed Two-Factor Authentication (2FA) with Microsoft Authenticator:
  - Enhanced TOTP validation with more robust error handling and a wider validation window
  - Added input normalization for TOTP codes and backup codes
  - Improved verification with better exception handling
  - Added specific instructions for Microsoft Authenticator in the setup UI
  - Issue: "Invalid code" errors when using Microsoft Authenticator for 2FA
  - Root cause: Time synchronization issues and limited validation window

- **[2025-06-20]** Fixed login form two-factor authentication flow:
  - Modified hidden inputs in the 2FA form to correctly store username using `{{ username }}` template variable instead of session values
  - Added `autocomplete="off"` to sensitive inputs for better security
  - Issue: Login form was storing user ID instead of username during 2FA flow, breaking the authentication process
  - Root cause: The template was using `session.get('pending_user_id')` as the username value

- **[2025-06-20]** Updated routes.py login handler:
  - Added support for storing and passing username between requests using both session variables and template rendering
  - Modified password verification to accept 'verified' as a valid password during 2FA flow
  - Added `session['pending_username']` to preserve username during multi-step authentication
  - Issue: Username was lost between the initial login and 2FA verification steps

- **[2025-06-20]** Improved session management:
  - Configured Flask session with secure settings
  - Added filesystem-based session storage in dedicated 'flask_session' directory
  - Set session lifetime to 30 minutes
  - Generated secure random secret key if environment variable not set
  - Issue: Sessions were not properly configured for secure persistence

### User Interface
- **[2025-06-20]** Enhanced 2FA setup user experience:
  - Added detailed troubleshooting guidance for common TOTP issues
  - Included specific setup instructions for Microsoft Authenticator
  - Improved error messaging with more specific feedback
  - Issue: Users were confused when encountering 2FA setup problems

- **[2025-06-20]** Updated front-end dependencies:
  - Replaced custom Bootstrap CSS with standard Bootstrap 5.3.0
  - Added jQuery 3.6.0 for better JavaScript component support
  - Issue: UI components might not have been functioning correctly due to missing or incompatible dependencies

### Testing
- **[2025-06-20]** Added comprehensive test suite:
  - Created authentication tests covering registration, login, and 2FA
  - Added security tests for session management and access control
  - Implemented API endpoint tests with error handling verification
  - Created manual testing checklist for features requiring human verification
  - Issue: Lack of automated testing made regression detection difficult

### Known Issues
- None documented yet

### Future Improvements
- Implement remember-me functionality for login
- Add email verification during registration
- Improve password recovery workflow
- Add more robust CSRF protection
- Enhance session security with IP binding
- Implement progressive session timeout

## [2025-01-20]

### Added
- Enhanced dashboard with Mint-style financial metrics
- Added net worth calculation and display
- Added account-specific metrics (credit cards, cash, loans, investments)
- Added interactive dropdowns for account details
- Added comprehensive test suite for dashboard functionality
- Added proper z-index handling for dropdown menus
- Added vim and openssh to development environment
- Added auth fixture to conftest.py for authentication testing
- Added sample transaction data files for testing
- Added comprehensive .gitignore rules

### Changed
- Restructured project to use src/ directory structure
- Updated import paths to use src prefix
- Improved code organization and maintainability
- Replaced legacy statistic tiles with modern financial metric cards
- Updated template comments to use Jinja2 style
- Updated .replit configuration to include additional development tools
- Updated test configuration in conftest.py

### Fixed
- Resolved merge conflicts in routes.py and dashboard.html
- Fixed account balance calculations
- Improved error handling in financial calculations
- Fixed dropdown menu z-index issues
- Fixed viewAccount function to properly route to accounts page
- Fixed git tracking of generated files (database, session files, etc.) 