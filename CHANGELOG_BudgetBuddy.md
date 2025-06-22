## BudgetBuddy Changelog

### 2025-01-20 06:12:58
- **File(s):** CHANGELOG_BudgetBuddy.md
- **Change:** Created changelog file to track BudgetBuddy dashboard modifications
- **Timestamp:** 2025-01-20 06:12:58

### 2025-01-20 06:12:58
- **File(s):** templates/dashboard.html
- **Change:** Replaced three legacy statistic tiles with five Mint-style cards (Net Worth, Credit Cards, Cash, Loans, Investments) with interactive dropdowns
- **Timestamp:** 2025-01-20 06:12:58

### 2025-01-20 06:20:30
- **File(s):** routes.py, templates/dashboard.html
- **Change:** Added calculation functions for net worth, credit cards, cash, loans, and investments totals based on user accounts with proper positive/negative styling
- **Timestamp:** 2025-01-20 06:20:30
## 2025-01-20 07:02:00 UTC

- **routes.py**: Added real account data queries for dashboard dropdown menus, replacing hardcoded sample data with actual user account information
- **templates/dashboard.html**: Updated all five statistic card dropdown menus to display real account data instead of placeholder values, added proper conditional rendering for empty states
- **templates/dashboard.html**: Fixed viewAccount function to properly route to accounts page with highlighting

### 2025-01-20 07:10:00
- **File(s):** templates/dashboard.html
- **Change:** Fixed dropdown menu z-index issues by increasing z-index to 9999 and adding dropdown-active class management to ensure dropdowns appear above all other page elements
- **Timestamp:** 2025-01-20 07:10:00

