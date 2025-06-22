# BudgetBuddy Manual Testing Checklist

This document contains manual testing procedures for features that are difficult to automate or require human verification. Use this checklist to ensure that all critical functionality works correctly.

## 📱 Authentication and Security

### Registration Flow
- [ ] **New user registration**
  - [ ] Enter valid registration details
  - [ ] Verify confirmation message appears
  - [ ] Verify able to log in with new credentials
  - [ ] Verify default categories are created

- [ ] **Password strength enforcement**
  - [ ] Try password without uppercase letters
  - [ ] Try password without lowercase letters
  - [ ] Try password without numbers
  - [ ] Try password without special characters
  - [ ] Try password shorter than 8 characters
  - [ ] Try common passwords (password123, admin123)
  - [ ] Verify appropriate error messages for each case

### Login Flow
- [ ] **Standard login**
  - [ ] Enter valid credentials
  - [ ] Verify redirect to dashboard
  - [ ] Check "Remember me" functionality (if implemented)

- [ ] **Failed login attempts**
  - [ ] Enter incorrect password multiple times
  - [ ] Verify account locks after 5 attempts
  - [ ] Verify lockout duration (30 minutes)
  - [ ] Verify login works after lockout expires

### Two-Factor Authentication
- [ ] **2FA setup**
  - [ ] Verify QR code displays correctly
  - [ ] Scan with Google Authenticator
  - [ ] Scan with Microsoft Authenticator
  - [ ] Enter valid code to complete setup
  - [ ] Verify backup codes are displayed and can be copied

- [ ] **2FA login flow**
  - [ ] Log in with username/password
  - [ ] Enter valid 2FA code
  - [ ] Verify successful login

- [ ] **2FA edge cases**
  - [ ] Test with incorrect 2FA code
  - [ ] Test with valid code but entered too late
  - [ ] Test with valid backup code
  - [ ] Verify backup code is consumed after use
  - [ ] Test with device time slightly off

- [ ] **2FA management**
  - [ ] Disable 2FA with correct password
  - [ ] Generate new backup codes
  - [ ] Verify old backup codes no longer work

### Session Management
- [ ] **Session behavior**
  - [ ] Verify session persists across page loads
  - [ ] Verify session expires after inactivity period
  - [ ] Verify session is destroyed on logout
  - [ ] Test multiple concurrent sessions

## 💰 Financial Features

### Account Management
- [ ] **Account creation**
  - [ ] Create each type of account (checking, savings, credit)
  - [ ] Verify initial balance is correctly stored
  - [ ] Verify account appears in accounts list

- [ ] **Account editing**
  - [ ] Change account name
  - [ ] Change account type
  - [ ] Update balance
  - [ ] Toggle active status

- [ ] **Account deletion**
  - [ ] Delete account with no transactions
  - [ ] Attempt to delete account with transactions
  - [ ] Verify confirmation dialog works

### Transaction Management
- [ ] **Manual transaction entry**
  - [ ] Create income transaction
  - [ ] Create expense transaction
  - [ ] Verify balance updates correctly
  - [ ] Verify transaction appears in list

- [ ] **Transaction categorization**
  - [ ] Assign category to transaction
  - [ ] Change transaction category
  - [ ] Use bulk categorization
  - [ ] Verify category changes are saved

- [ ] **Transaction filtering**
  - [ ] Filter by date range
  - [ ] Filter by account
  - [ ] Filter by category
  - [ ] Filter by transaction type
  - [ ] Verify correct transactions shown for each filter

### CSV Import
- [ ] **File upload**
  - [ ] Upload CSV from each supported bank
  - [ ] Verify file size validation
  - [ ] Test with invalid file format

- [ ] **CSV parsing**
  - [ ] Verify correct format detection
  - [ ] Check date parsing for different formats
  - [ ] Verify amount parsing (positive/negative values)
  - [ ] Check description and merchant extraction

- [ ] **Duplicate detection**
  - [ ] Import same file twice
  - [ ] Verify duplicates are identified
  - [ ] Test duplicate handling options

## 📊 Reporting and Visualization

### Dashboard
- [ ] **Summary statistics**
  - [ ] Verify total balance calculation
  - [ ] Check account count
  - [ ] Verify recent transactions list
  - [ ] Check spending by category

- [ ] **Charts and graphs**
  - [ ] Verify spending trend chart loads
  - [ ] Test interactive chart features
  - [ ] Check responsiveness on different screen sizes

### Visualizations Page
- [ ] **Data filtering**
  - [ ] Change time period (month, quarter, year)
  - [ ] Filter by specific accounts
  - [ ] Filter by transaction types
  - [ ] Verify charts update correctly

- [ ] **Chart interactions**
  - [ ] Hover over chart elements for tooltips
  - [ ] Click legend items to toggle visibility
  - [ ] Check drill-down functionality (if implemented)

## 🧠 AI Features

### AI Categorization
- [ ] **Suggestion accuracy**
  - [ ] Test with common merchant names
  - [ ] Test with ambiguous descriptions
  - [ ] Verify suggestions match expected categories

- [ ] **Bulk AI categorization**
  - [ ] Run AI categorization on uncategorized transactions
  - [ ] Review and apply suggestions
  - [ ] Verify categories are correctly applied

- [ ] **Learning capability**
  - [ ] Categorize transactions manually
  - [ ] Check if AI suggestions improve over time
  - [ ] Test with similar transactions later

## 📱 User Experience

### Responsive Design
- [ ] **Mobile view**
  - [ ] Test navigation menu on small screens
  - [ ] Verify forms resize appropriately
  - [ ] Check charts and tables are readable

- [ ] **Tablet view**
  - [ ] Verify layout adjusts correctly
  - [ ] Test form interactions
  - [ ] Check touch interactions for charts

- [ ] **Desktop view**
  - [ ] Verify optimal use of screen space
  - [ ] Check advanced features are accessible

### Accessibility
- [ ] **Keyboard navigation**
  - [ ] Navigate entire site using only keyboard
  - [ ] Verify tab order is logical
  - [ ] Check focus indicators are visible

- [ ] **Screen reader compatibility**
  - [ ] Test with screen reader software
  - [ ] Verify form labels are announced
  - [ ] Check chart data is accessible

- [ ] **Color contrast**
  - [ ] Verify text meets contrast requirements
  - [ ] Check chart colors are distinguishable

## 🛠 Error Handling

### Form Validation
- [ ] **Input validation**
  - [ ] Test with invalid data formats
  - [ ] Submit empty required fields
  - [ ] Test with extreme values (very large numbers)
  - [ ] Verify helpful error messages

- [ ] **Error recovery**
  - [ ] Verify form data is preserved after error
  - [ ] Check focused field after error
  - [ ] Test error message dismissal

### System Errors
- [ ] **Database connection**
  - [ ] Test behavior when database is unavailable
  - [ ] Verify appropriate error message

- [ ] **API failures**
  - [ ] Test behavior when API endpoint fails
  - [ ] Verify graceful degradation

## Notes

* Record all test failures with:
  * Steps to reproduce
  * Expected behavior
  * Actual behavior
  * Screenshots if relevant
  * Environment details (browser, OS, screen size)

* For security findings, escalate immediately to the security team.

* For usability issues, include suggestions for improvement. 