# BudgetBuddy Debug Checklist

## Authentication Issues

### Login Not Working
- [ ] Check user exists in database
- [ ] Verify password hashing is working correctly
- [ ] Check for account lockout due to failed attempts
- [ ] Inspect Flask session configuration
- [ ] Verify 2FA flow is preserving username/user_id
- [ ] Check that login route is returning correct templates/redirects
- [ ] Test login with a newly created user

### Registration Issues
- [ ] Verify form data is being submitted correctly
- [ ] Check password validation logic
- [ ] Ensure database is accessible and writeable
- [ ] Check for username/email uniqueness enforcement
- [ ] Verify default categories are being created

### Two-Factor Authentication Issues
- [ ] Check TOTP secret generation
- [ ] Verify QR code is displaying correctly
- [ ] Test token verification with known valid token
- [ ] Verify backup codes are being generated and stored properly
- [ ] Check session handling during 2FA flow
- [ ] Verify time synchronization between server and client device
- [ ] Test the wider validation window (±5 intervals)
- [ ] Check input normalization for TOTP and backup codes
- [ ] Verify compatibility with different authenticator apps
- [ ] Test setup with manual key entry vs. QR code scanning

### Microsoft Authenticator Specific Issues
- [ ] Verify app is set up with "Other account" not "Microsoft account"
- [ ] Check if manual key entry was used correctly (using "Enter setup key")
- [ ] Verify time sync on the device (Settings → Time)
- [ ] Test if the wider validation window fixes the issue
- [ ] Check account name format in the app (email address required)

## Database Issues

### Connection Problems
- [ ] Verify database file exists and is accessible
- [ ] Check database URI configuration
- [ ] Ensure database schema is up to date
- [ ] Check for SQLite locking issues
- [ ] Verify connection pool settings

### Data Integrity Issues
- [ ] Check foreign key constraints
- [ ] Verify cascading delete behavior
- [ ] Ensure transaction atomicity for critical operations
- [ ] Check data type handling (especially for decimal amounts)

## Front-End Issues

### UI Not Rendering Correctly
- [ ] Verify all CSS/JS dependencies are loading (check browser console)
- [ ] Check for JavaScript errors
- [ ] Inspect DOM structure for correct nesting
- [ ] Verify Bootstrap components are initialized properly
- [ ] Test responsive behavior at different viewport sizes

### Form Submission Problems
- [ ] Check form action URLs
- [ ] Verify CSRF protection (if enabled)
- [ ] Test form validation (both client and server side)
- [ ] Check for JavaScript event handler issues
- [ ] Verify that form fields match expected backend parameters

## API and Data Processing

### Transaction Import Issues
- [ ] Verify CSV format detection
- [ ] Check file upload permissions and directory
- [ ] Test parser with sample files from each supported institution
- [ ] Verify transaction categorization rules
- [ ] Check duplicate detection logic

### Visualization Issues
- [ ] Verify Chart.js initialization
- [ ] Check data formatting for charts
- [ ] Test API endpoints returning chart data
- [ ] Verify calculations for summary statistics
- [ ] Check date range filtering

## Performance Issues

### Slow Page Loads
- [ ] Check database query optimization
- [ ] Verify index usage for frequent queries
- [ ] Test with larger datasets
- [ ] Check browser resource utilization
- [ ] Verify static asset caching

## Security Issues

### Session Management
- [ ] Verify secret key generation
- [ ] Check session cookie settings
- [ ] Test session expiration
- [ ] Verify secure and httpOnly flags
- [ ] Check for session fixation vulnerabilities

### Password Security
- [ ] Verify password complexity requirements
- [ ] Check password hashing implementation
- [ ] Test account lockout mechanism
- [ ] Verify failed login tracking
- [ ] Check for brute force protections

## Testing Issues

### Automated Tests Failing
- [ ] Check if test database is properly configured
- [ ] Verify test fixtures are working correctly
- [ ] Ensure test environment has all dependencies
- [ ] Check for timing issues in asynchronous tests
- [ ] Verify that tests are isolated properly 