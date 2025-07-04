"""
Integration tests for the unified finances page.
"""
import pytest
import json
from flask import url_for


@pytest.mark.integration
class TestFinancesIntegration:
    """Integration tests for the finances page."""
    
    def test_finances_page_loads(self, app_client_with_user):
        """Test that finances page loads successfully."""
        response = app_client_with_user.get('/finances')
        assert response.status_code == 200
        assert b'<title>Unified Finances - BudgetBuddy</title>' in response.data
        assert b'id="financial-summary"' in response.data
        
    def test_account_summary_data_loaded(self, app_client_with_user):
        """Test that account summary data is loaded correctly."""
        response = app_client_with_user.get('/finances')
        assert b'id="net-worth-card"' in response.data
        assert b'id="cash-accounts-card"' in response.data
        assert b'id="credit-card-accounts-card"' in response.data
        assert b'id="investment-accounts-card"' in response.data
        assert b'id="loan-accounts-card"' in response.data
        
    def test_account_sections_rendered(self, app_client_with_user, sample_accounts):
        """Test that account sections are rendered."""
        response = app_client_with_user.get('/finances')
        for account in sample_accounts:
            assert bytes(f'data-account-id="{account.id}"', 'utf-8') in response.data
            assert bytes(account.name, 'utf-8') in response.data
            
    def test_filter_form_rendered(self, app_client_with_user):
        """Test that filter form is rendered."""
        response = app_client_with_user.get('/finances')
        assert b'id="filter-date-from"' in response.data
        assert b'id="filter-date-to"' in response.data
        assert b'id="filter-account"' in response.data
        assert b'id="filter-category"' in response.data
        assert b'id="filter-type"' in response.data
        assert b'id="search-transactions"' in response.data
        
    def test_quick_filter_buttons_rendered(self, app_client_with_user):
        """Test that quick filter buttons are rendered."""
        response = app_client_with_user.get('/finances')
        assert b'id="quick-filter-all"' in response.data
        assert b'id="quick-filter-uncategorized"' in response.data
        assert b'id="quick-filter-recent"' in response.data
        assert b'id="quick-filter-large"' in response.data
        assert b'id="quick-filter-income"' in response.data
        
    def test_account_transactions_api(self, app_client_with_user, sample_accounts, sample_transactions):
        """Test the account transactions API endpoint."""
        # Get first account ID
        account_id = sample_accounts[0].id
        
        # Call API for transactions
        response = app_client_with_user.get(f'/api/account-transactions?account_id={account_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)
        
        # Verify transactions belong to the account
        for transaction in data['transactions']:
            assert transaction['account_id'] == account_id
            
    def test_filtered_transactions_api(self, app_client_with_user):
        """Test filtering transactions through API."""
        # Test date filter
        response = app_client_with_user.get('/api/account-transactions?from_date=2025-01-01&to_date=2025-01-31')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for transaction in data['transactions']:
            transaction_date = transaction['date']
            assert transaction_date >= '2025-01-01'
            assert transaction_date <= '2025-01-31'
            
    def test_category_filter_api(self, app_client_with_user, sample_categories):
        """Test filtering transactions by category."""
        # Get first category ID
        category_id = sample_categories[0].id
        
        response = app_client_with_user.get(f'/api/account-transactions?category_id={category_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for transaction in data['transactions']:
            assert transaction['category_id'] == category_id
            
    def test_transaction_type_filter_api(self, app_client_with_user):
        """Test filtering transactions by type (income/expense)."""
        # Test expense filter
        response = app_client_with_user.get('/api/account-transactions?transaction_type=expense')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for transaction in data['transactions']:
            assert transaction['transaction_type'] == 'expense'
            
        # Test income filter
        response = app_client_with_user.get('/api/account-transactions?transaction_type=income')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for transaction in data['transactions']:
            assert transaction['transaction_type'] == 'income'
            
    def test_search_filter_api(self, app_client_with_user):
        """Test searching transactions."""
        search_term = "grocery"
        response = app_client_with_user.get(f'/api/account-transactions?search={search_term}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for transaction in data['transactions']:
            # Check if search term appears in description or merchant
            found = False
            if search_term.lower() in transaction['description'].lower():
                found = True
            elif transaction.get('merchant') and search_term.lower() in transaction['merchant'].lower():
                found = True
            assert found
            
    def test_add_transaction_api(self, app_client_with_user, sample_accounts, sample_categories):
        """Test adding a transaction through API."""
        # Get first account and category
        account_id = sample_accounts[0].id
        category_id = sample_categories[0].id
        
        # Create transaction data
        transaction_data = {
            'account_id': account_id,
            'category_id': category_id,
            'date': '2025-01-15',
            'description': 'Test transaction',
            'amount': 50.00,
            'transaction_type': 'expense',
            'merchant': 'Test Merchant'
        }
        
        # Post to API
        response = app_client_with_user.post(
            '/api/add-transaction',
            data=json.dumps(transaction_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Verify transaction was added
        data = json.loads(response.data)
        assert 'id' in data
        assert data['success'] is True
        
        # Get the transaction to verify
        transaction_id = data['id']
        response = app_client_with_user.get(f'/api/account-transactions?transaction_id={transaction_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['transactions']) == 1
        transaction = data['transactions'][0]
        assert transaction['description'] == 'Test transaction'
        assert float(transaction['amount']) == 50.00
        assert transaction['account_id'] == account_id
        assert transaction['category_id'] == category_id
        
    def test_update_transaction_api(self, app_client_with_user, sample_transactions, sample_categories):
        """Test updating a transaction through API."""
        # Get first transaction and a different category
        transaction = sample_transactions[0]
        new_category_id = sample_categories[1].id if sample_categories[1].id != transaction.category_id else sample_categories[0].id
        
        # Create update data
        update_data = {
            'id': transaction.id,
            'description': 'Updated transaction',
            'category_id': new_category_id
        }
        
        # Post to API
        response = app_client_with_user.post(
            '/api/update-transaction',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify transaction was updated
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Get the transaction to verify
        response = app_client_with_user.get(f'/api/account-transactions?transaction_id={transaction.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        transaction = data['transactions'][0]
        assert transaction['description'] == 'Updated transaction'
        assert transaction['category_id'] == new_category_id
        
    def test_delete_transaction_api(self, app_client_with_user, sample_transactions):
        """Test deleting a transaction through API."""
        # Get first transaction
        transaction_id = sample_transactions[0].id
        
        # Delete transaction
        response = app_client_with_user.post(
            '/api/delete-transaction',
            data=json.dumps({'id': transaction_id}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify transaction was deleted
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Try to get the transaction
        response = app_client_with_user.get(f'/api/account-transactions?transaction_id={transaction_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['transactions']) == 0
        
    def test_bulk_categorize_api(self, app_client_with_user, sample_transactions, sample_categories):
        """Test bulk categorizing transactions through API."""
        # Get two transactions and a category
        transaction_ids = [sample_transactions[0].id, sample_transactions[1].id]
        category_id = sample_categories[0].id
        
        # Create bulk categorize data
        bulk_data = {
            'transaction_ids': transaction_ids,
            'category_id': category_id
        }
        
        # Post to API
        response = app_client_with_user.post(
            '/api/bulk-categorize',
            data=json.dumps(bulk_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify transactions were categorized
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 2
        
        # Get the transactions to verify
        for transaction_id in transaction_ids:
            response = app_client_with_user.get(f'/api/account-transactions?transaction_id={transaction_id}')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            transaction = data['transactions'][0]
            assert transaction['category_id'] == category_id 