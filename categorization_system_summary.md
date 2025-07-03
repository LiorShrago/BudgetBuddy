# Categorization System Summary

## Overview
The current BudgetBuddy application has a comprehensive categorization system with the following components:

## Files Involved

### Backend Files

#### 1. `models.py`
- **Category Model** (lines 179-191)
  - Fields: id, user_id, name, parent_id, color, created_at
  - Self-referential relationship for subcategories
  - Relationships with transactions and budget items

- **CategorizationRule Model** (lines 237-245)
  - Fields: id, user_id, keyword, category_id, priority, is_active, created_at
  - Used for rule-based auto-categorization

- **Transaction Model** (lines 192-205)
  - `category_id` foreign key field (line 198)

#### 2. `routes.py`
**Category Management Routes:**
- `/categories` (line 571) - Display categories
- `/categories/add` (line 578) - Add new category
- `/api/create-category` (line 777) - API for creating categories

**Categorization Routes:**
- `/categorize` (line 672) - Main categorization interface
- `/api/bulk-categorize` (line 712) - Bulk categorize transactions
- `/api/update-category` (line 747) - Update single transaction category
- `/api/ai-suggest-all` (line 818) - AI suggestions for all uncategorized
- `/api/apply-suggestions` (line 856) - Apply AI suggestions
- `/api/ai-suggest-categories` (line 893) - AI suggestions for selected

**Data/Chart Routes:**
- `/api/spending-chart` (line 599) - Category spending data
- `/api/visualization-data` (line 924) - Category breakdown for charts

**Helper Functions:**
- `get_category_breakdown()` (line 979) - Category spending analysis
- `create_default_categories()` (line 1092) - Create default categories for new users

#### 3. `categorization.py` (entire file)
**Rule-based Auto-categorization:**
- `auto_categorize_transaction()` - Main auto-categorization function
- `get_default_category_patterns()` - Pattern matching for common categories
- `create_categorization_rule()` - Create new categorization rules
- `learn_from_user_categorization()` - Learn from manual categorizations

#### 4. `ai_categorizer.py` (entire file)
**AI-powered Categorization:**
- `AITransactionCategorizer` class - Uses Perplexity API
- `auto_categorize_uncategorized_transactions()` - Bulk AI categorization
- `get_categorization_suggestions()` - Get AI suggestions for specific transactions

#### 5. `csv_parsers.py`
- Auto-categorization during CSV import (lines 84-86)

### Frontend Files

#### 6. `templates/categorize.html` (entire file)
**Main Categorization Interface:**
- Transaction table with category dropdowns
- Bulk selection and categorization tools
- AI categorization buttons
- Filtering by category, account, date range
- New category creation modal

#### 7. `templates/categories.html` (entire file)
**Category Management Interface:**
- Display all user categories
- Category cards with color, parent/child relationships
- Add new category modal with parent selection
- Category statistics

#### 8. `static/js/categorize.js` (entire file)
**Frontend JavaScript Functionality:**
- Bulk selection/deselection of transactions
- AJAX calls for categorization operations
- AI suggestion handling
- Filter application
- New category creation
- Transaction categorization interface

## Key Features

### 1. Category Management
- Hierarchical categories (parent/child relationships)
- Custom colors for categories
- Default categories for new users:
  - Food & Dining, Transportation, Shopping, Entertainment
  - Bills & Utilities, Healthcare, Education, Travel
  - Income, Transfer

### 2. Transaction Categorization
- Manual categorization (individual and bulk)
- Rule-based auto-categorization using keywords
- AI-powered categorization using Perplexity API
- Auto-categorization during CSV import

### 3. User Interface
- Dedicated categorization page with filtering
- Category management page
- Bulk operations with select all/none
- AI suggestion modal with accept/reject options

### 4. Analytics & Visualization
- Category-based spending breakdown
- Category filtering in transaction views
- Category-based charts and visualizations
- Spending analysis by category

### 5. Learning System
- Categorization rules that learn from user behavior
- Priority-based rule matching
- Keyword-based pattern matching

## Database Schema Impact

### Tables with categorization data:
- `category` - Main category table
- `categorization_rule` - Auto-categorization rules
- `transaction.category_id` - Foreign key linking transactions to categories
- `budget_item.category_id` - Foreign key for budget categories

## API Endpoints

### Category Management:
- `POST /categories/add` - Add category (form-based)
- `POST /api/create-category` - Add category (JSON API)

### Transaction Categorization:
- `POST /api/bulk-categorize` - Bulk categorize transactions
- `POST /api/update-category` - Update single transaction category
- `POST /api/ai-suggest-all` - Get AI suggestions for all uncategorized
- `POST /api/apply-suggestions` - Apply selected AI suggestions
- `POST /api/ai-suggest-categories` - Get AI suggestions for selected transactions

### Data Access:
- `GET /api/spending-chart` - Category spending data
- `GET /api/visualization-data` - Full category analytics data

## Dependencies
- **AI Categorization:** Perplexity API integration
- **Database:** SQLAlchemy relationships between categories, transactions, and rules
- **Frontend:** Bootstrap modals, jQuery/vanilla JS for interactions

This system provides comprehensive categorization functionality with both manual and automated categorization options.