# BudgetBuddy Project Changelog

## Table of Contents

- [Overview](#overview)
- [Change Log](#change-log)
  - [2025-07-12 Finances Tests Dependency Fix](#2025-07-4)
  - [2025-07-11 Test Fixtures and Integration Tests Fix](#2025-07-4)
  - [2025-07-10 Unified Financial Overview](#2025-07-4)
  - [2025-07-04 Documentation Reorganization](#2025-07-04)
  - [2025-07-01 Enhanced AI Categorization](#2025-07-01)
  - [2025-06-22 Project Restructuring](#2025-06-22)
  - [2025-06-20 Authentication System Improvements](#2025-06-20)
  - [2025-01-20 Dashboard Enhancements](#2025-01-20)
  - [2023-07-03 Development Standards](#2023-07-03)
- [Known Issues](#known-issues)
- [Future Improvements](#future-improvements)

## Overview

This changelog tracks all modifications, fixes, and improvements made to the BudgetBuddy project. Each entry includes detailed notes about the changes, reasoning, and impacts on the system.

## Change Log

### 2025-07-12

#### Finances Tests Performance and Reliability Improvements

**Changes:**
- Enhanced the dependency installation process in run_finances_tests.py
- Added fallback direct installation for critical packages like selenium
- Added verification step to ensure selenium is properly installed
- Improved error handling and user feedback during dependency installation
- Added more detailed troubleshooting instructions for manual dependency installation
- Fixed performance tests to properly authenticate and handle API endpoints
- Added dynamic port selection for Flask test server to avoid port conflicts
- Implemented robust account ID detection for API tests
- Fixed HTML report generation issues with better error handling
- Made performance tests more resilient to API failures
- Added automatic test account creation for performance tests
- Improved error handling in test execution
- Updated documentation with detailed performance testing information

**Reasoning:**
- Tests were failing with "ModuleNotFoundError: No module named 'selenium'" despite requirements-test.txt
- Performance tests were failing due to authentication issues and fixed port usage
- The original dependency installation process didn't handle edge cases or verify successful installation
- Users needed clearer guidance when automatic installation fails
- Port conflicts were causing Flask server startup failures

**Impact:**
- More reliable test execution with proper dependency handling
- Performance tests now run successfully with proper authentication
- Dynamic port selection prevents conflicts with other running services
- Better user experience with clearer error messages and troubleshooting guidance
- Reduced friction when running tests in different environments

### 2025-07-11

#### Test Fixtures and Integration Tests Fix

**Changes:**
- Fixed test fixtures in conftest.py to properly handle SQLAlchemy session management
- Updated finances integration tests to match actual API implementation
- Fixed API endpoint parameter naming in tests to align with backend routes
- Added proper error handling for API tests with conditional assertions
- Fixed transaction update test to include all required fields
- Added automatic dependency installation to run_finances_tests.py
- Created pytest.ini file to register custom test markers
- Added comprehensive documentation for running finances tests

**Reasoning:**
- Integration tests were failing due to mismatches between test expectations and actual API implementation
- Test fixtures needed updates to prevent DetachedInstanceError from SQLAlchemy
- API parameter names in tests didn't match the actual backend implementation
- Selenium and other test dependencies were missing, causing test failures
- Custom test markers were not registered, causing pytest warnings

**Impact:**
- All finances integration tests now pass successfully
- Improved test reliability and maintainability
- Better alignment between tests and actual implementation
- Simplified test setup with automatic dependency installation
- Added clear documentation for running and troubleshooting tests

### 2025-07-10

#### Unified Financial Overview

**Changes:**
- Created new unified finances page combining accounts and transactions
- Implemented client-side filtering and sorting of transactions
- Added account management directly from the finances page
- Developed transaction quick-add functionality within account view
- Created responsive design for all screen sizes
- Added comprehensive test suite for the new functionality

**Reasoning:**
- Users requested a more streamlined interface for managing finances
- Previous separate pages for accounts and transactions created friction
- Unified view allows for better financial decision making

**Impact:**
- Improved user experience with consolidated financial management
- Reduced navigation steps for common financial tasks
- Enhanced visual presentation of financial data

### 2025-07-04

#### Documentation Reorganization

##### Added

- Added new documentation structure with centralized docs/ directory
- Created organized subdirectories for different documentation types:
  - docs/development/ for development-related documentation
  - docs/testing/ for testing documentation
- Added docs/CONTEXT7_COMPATIBILITY.md to document compatibility features
- Added docs/DOCUMENTATION_CLEANUP.md to track documentation efforts

##### Changed

- Moved CHANGELOG.md to docs/CHANGELOG.md with improved structure and formatting
- Reorganized content with better chronological ordering and section anchors
- Moved debug_checklist.md to docs/development/DEBUG_CHECKLIST.md
- Moved development_notes.md to docs/development/DEVELOPMENT_NOTES.md
- Updated Table of Contents with links to all major changelog entries

##### Fixed

- Resolved duplicate entries for 2025-01-20 release
- Fixed broken links and formatting issues in documentation
- Improved consistency in changelog entry format
- Added missing anchor links for better navigation

### 2025-07-01

#### Enhanced AI Categorization

- **Added enhanced AI categorization system:**
  - Created `enhanced_ai_categorizer.py` with online research capabilities using Perplexity API
  - Implemented `research_and_categorize_transaction()` function that searches online for transaction descriptions
  - Added `enhanced_auto_categorize_uncategorized_transactions()` for improved batch processing
  - Created new API endpoints: `/api/ai-research-categorize` and `/api/ai-auto-categorize-enhanced`
  - Updated `categorize.html` template with new "AI Research & Categorize" and "Enhanced Auto-Categorize" buttons
  - Added JavaScript functions for enhanced AI features in `categorize.js`
  - Created comprehensive test suite and documentation
  - **Issue:** Original AI categorization relied only on pattern matching without understanding what purchases were for
  - **Root cause:** Need for better context about merchants and transaction purposes to improve accuracy
  - **Files affected:**
    - `src/services/enhanced_ai_categorizer.py` (new)
    - `src/routs/routes.py`
    - `templates/categorize.html`
    - `static/js/categorize.js`
    - Test files in `tests/` directory
    - Documentation in `docs/` directory

### 2025-06-22

#### Project Restructuring

- **Restructured project directory:**
  - Reorganized codebase into a more modular structure
  - Moved models to `src/models/`
  - Moved routes to `src/routs/`
  - Moved services to `src/services/`
  - Renamed `project_changelog.md` to `CHANGELOG.md` for better standardization
  - Updated import paths across the project
  - **Issue:** Project structure was flat and difficult to maintain
  - **Root cause:** Initial development focused on functionality over structure

### 2025-06-20

#### Authentication System Improvements

- **Fixed Two-Factor Authentication (2FA) with Microsoft Authenticator:**

  - Enhanced TOTP validation with more robust error handling and a wider validation window
  - Added input normalization for TOTP codes and backup codes
  - Improved verification with better exception handling
  - Added specific instructions for Microsoft Authenticator in the setup UI
  - **Issue:** "Invalid code" errors when using Microsoft Authenticator for 2FA
  - **Root cause:** Time synchronization issues and limited validation window

- **Fixed login form two-factor authentication flow:**

  - Modified hidden inputs in the 2FA form to correctly store username using `{{ username }}` template variable instead of session values
  - Added `autocomplete="off"` to sensitive inputs for better security
  - **Issue:** Login form was storing user ID instead of username during 2FA flow, breaking the authentication process
  - **Root cause:** The template was using `session.get('pending_user_id')` as the username value

- **Updated routes.py login handler:**

  - Added support for storing and passing username between requests using both session variables and template rendering
  - Modified password verification to accept 'verified' as a valid password during 2FA flow
  - Added `session['pending_username']` to preserve username during multi-step authentication
  - **Issue:** Username was lost between the initial login and 2FA verification steps

- **Improved session management:**
  - Configured Flask session with secure settings
  - Added filesystem-based session storage in dedicated 'flask_session' directory
  - Set session lifetime to 30 minutes
  - Generated secure random secret key if environment variable not set
  - **Issue:** Sessions were not properly configured for secure persistence

#### User Interface Improvements

- **Enhanced 2FA setup user experience:**

  - Added detailed troubleshooting guidance for common TOTP issues
  - Included specific setup instructions for Microsoft Authenticator
  - Improved error messaging with more specific feedback
  - **Issue:** Users were confused when encountering 2FA setup problems

- **Updated front-end dependencies:**
  - Replaced custom Bootstrap CSS with standard Bootstrap 5.3.0
  - Added jQuery 3.6.0 for better JavaScript component support
  - **Issue:** UI components might not have been functioning correctly due to missing or incompatible dependencies

#### Testing Improvements

- **Added comprehensive test suite:**
  - Created authentication tests covering registration, login, and 2FA
  - Added security tests for session management and access control
  - Implemented API endpoint tests with error handling verification
  - Created manual testing checklist for features requiring human verification
  - **Issue:** Lack of automated testing made regression detection difficult

### 2025-01-20

#### Dashboard Enhancements

##### Initial Dashboard Improvements (06:12:58 UTC)

- **Created initial dashboard changes:**
  - Replaced three legacy statistic tiles with five Mint-style cards (Net Worth, Credit Cards, Cash, Loans, Investments) with interactive dropdowns
  - **Files affected:**
    - `templates/dashboard.html`

##### Calculation Functions (06:20:30 UTC)

- **Added financial calculation functions:**
  - Implemented calculation functions for net worth, credit cards, cash, loans, and investments totals based on user accounts
  - Added proper positive/negative styling for financial data
  - **Files affected:**
    - `routes.py`
    - `templates/dashboard.html`

##### Real Account Data Integration (07:02:00 UTC)

- **Enhanced data display:**
  - Added real account data queries for dashboard dropdown menus, replacing hardcoded sample data with actual user account information
  - Updated all five statistic card dropdown menus to display real account data instead of placeholder values
  - Added proper conditional rendering for empty states
  - Fixed viewAccount function to properly route to accounts page with highlighting
  - **Files affected:**
    - `routes.py`
    - `templates/dashboard.html`

##### UI Fixes (07:10:00 UTC)

- **Fixed dropdown menu z-index issues:**

  - Increased z-index to 9999
  - Added dropdown-active class management to ensure dropdowns appear above all other page elements
  - **Files affected:**
    - `templates/dashboard.html`

- **Added new features:**

  - Net worth calculation and display
  - Account-specific metrics (credit cards, cash, loans, investments)
  - Interactive dropdowns for account details
  - Comprehensive test suite for dashboard functionality
  - Proper z-index handling for dropdown menus
  - Development environment improvements (vim and openssh)
  - Authentication testing fixtures in conftest.py
  - Sample transaction data files for testing
  - Comprehensive .gitignore rules and environment configuration
  - Secure secret key generation script
  - `.env.example` template

- **Changed infrastructure:**

  - Restructured project to use src/ directory structure
  - Updated import paths to use src prefix
  - Improved code organization and maintainability
  - Replaced legacy statistic tiles with modern financial metric cards
  - Updated template comments to use Jinja2 style
  - Updated .replit configuration for development tools
  - Enhanced test configuration in conftest.py
  - Improved security with environment-based configuration

- **Fixed issues:**

  - Resolved merge conflicts in routes.py and dashboard.html
  - Fixed account balance calculations
  - Improved error handling in financial calculations
  - Fixed dropdown menu z-index issues
  - Fixed git tracking of generated files (database, session files, etc.)
  - Fixed security issues with hardcoded configuration

- **Security enhancements:**
  - Moved sensitive configuration to environment variables
  - Added secure secret key generation
  - Enhanced session security settings
  - Added rate limiting configuration
  - Improved database connection security

### 2023-07-03

#### Development Standards

##### Added

- Added comprehensive rule structure in .cursor/rules/ directory
- Added specific rule files for core development, Python coding standards, Flask patterns, templates, frontend, database, testing, and security
- Added clear guidance on error handling for different types of errors
- Added security headers and CSP configuration recommendations
- Added JavaScript module organization and bundling recommendations

##### Changed

- Consolidated redundant rules into a cohesive structure
- Clarified base.html modification policy to allow adding new blocks while preserving existing structure
- Made SQL usage guidelines consistent across rule files
- Updated frontend standards with modern tooling recommendations
- Reorganized rule structure with clear categories and subcategories
- Improved documentation requirements with consolidated guidance

##### Fixed

- Resolved contradiction between base.html being read-only and needed for template inheritance
- Fixed inconsistent SQL usage restrictions across different rule files
- Addressed missing guidance for error handling specific error types
- Added previously missing environment variable handling guidance

## Known Issues

- None documented yet

## Future Improvements

- Implement remember-me functionality for login
- Add email verification during registration
- Improve password recovery workflow
- Add more robust CSRF protection
- Enhance session security with IP binding
- Implement progressive session timeout

---

## Changelog Template

When adding new entries, please use the following template:

```
### YYYY-MM-DD

#### Feature or Component Name
- **Added/Changed/Fixed/Removed description:**
  - Detail 1
  - Detail 2
  - **Issue:** Description of the issue that prompted this change
  - **Root cause:** What caused the issue
  - **Files affected:**
    - File path 1
    - File path 2
```
