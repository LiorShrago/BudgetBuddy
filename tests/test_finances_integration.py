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
        assert b'<title>My Finances - BudgetBuddy</title>' in response.data
        assert b'My Finances' in response.data
        
    def test_account_summary_data_loaded(self, app_client_with_user):
        """Test that account summary data is loaded correctly."""
        response = app_client_with_user.get('/finances')
        assert b'Net Worth' in response.data
        assert b'Cash & Checking' in response.data
        assert b'Credit Cards' in response.data
        assert b'Savings & Investments' in response.data
        
    def test_account_sections_rendered(self, app_client_with_user, sample_accounts):
        """Test that account sections are rendered."""
        response = app_client_with_user.get('/finances')
        accounts = sample_accounts()  # Call the fixture function to get accounts
        for account in accounts:
            assert bytes(f'data-account-id="{account.id}"', 'utf-8') in response.data
            assert bytes(account.name, 'utf-8') in response.data
            
    def test_filter_form_rendered(self, app_client_with_user):
        """Test that filter form is rendered."""
        response = app_client_with_user.get('/finances')
        assert b'id="account-type-filter"' in response.data
        assert b'id="transaction-category-filter"' in response.data
        assert b'id="date-range-filter"' in response.data
        assert b'id="transaction-type-filter"' in response.data
        assert b'id="apply-filters"' in response.data
        
    def test_quick_filter_buttons_rendered(self, app_client_with_user):
        """Test that quick filter buttons are rendered."""
        response = app_client_with_user.get('/finances')
        assert b'class="btn btn-sm btn-outline-secondary quick-filter"' in response.data
        assert b'data-filter="recent"' in response.data
        assert b'data-filter="uncategorized"' in response.data
        assert b'data-filter="high-value"' in response.data
        assert b'data-filter="reset"' in response.data
        
    def test_account_transactions_api(self, app_client_with_user, sample_accounts, sample_transactions):
        """Test the account transactions API endpoint."""
        # Get first account ID
        accounts = sample_accounts()  # Call the fixture function
        account_id = accounts[0].id
        
        # Call API for transactions
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)
        
        # Since account_id is not returned in the response, we can't verify it directly
        # But we know the API only returns transactions for the specified account
        if data['transactions']:
            assert 'id' in data['transactions'][0]
            assert 'date' in data['transactions'][0]
            assert 'description' in data['transactions'][0]
            
    def test_filtered_transactions_api(self, app_client_with_user, sample_accounts):
        """Test filtering transactions through API."""
        # Need an account ID for the API
        accounts = sample_accounts()  # Call the fixture function
        account_id = accounts[0].id
        
        # Test date filter
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}&date_from=2025-01-01&date_to=2025-01-31')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Skip assertion if no transactions in date range
        if data['transactions']:
            for transaction in data['transactions']:
                transaction_date = transaction['date']
                assert transaction_date >= '2025-01-01'
                assert transaction_date <= '2025-01-31'
            
    def test_category_filter_api(self, app_client_with_user, sample_accounts, sample_categories):
        """Test filtering transactions by category."""
        # Get first account ID and category ID
        accounts = sample_accounts()  # Call the fixture function
        categories = sample_categories()  # Call the fixture function
        account_id = accounts[0].id
        category_id = categories[0].id
        
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}&category={category_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Skip assertion if no transactions with this category
        if data['transactions']:
            for transaction in data['transactions']:
                assert transaction['category_id'] == category_id
            
    def test_transaction_type_filter_api(self, app_client_with_user, sample_accounts):
        """Test filtering transactions by type (income/expense)."""
        # Need an account ID for the API
        accounts = sample_accounts()  # Call the fixture function
        account_id = accounts[0].id
        
        # Test expense filter
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}&type=expense')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Skip assertion if no expense transactions
        if data['transactions']:
            for transaction in data['transactions']:
                assert transaction['transaction_type'] == 'expense'
            
        # Test income filter
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}&type=income')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Skip assertion if no income transactions
        if data['transactions']:
            for transaction in data['transactions']:
                assert transaction['transaction_type'] == 'income'
            
    def test_search_filter_api(self, app_client_with_user, sample_accounts):
        """Test searching transactions."""
        # Need an account ID for the API
        accounts = sample_accounts()  # Call the fixture function
        account_id = accounts[0].id
        
        search_term = "grocery"
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}&description={search_term}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Skip assertion if no matching transactions
        if data['transactions']:
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
        accounts = sample_accounts()  # Call the fixture function
        categories = sample_categories()  # Call the fixture function
        account_id = accounts[0].id
        category_id = categories[0].id
        
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
        assert response.status_code == 200
        
        # Verify transaction was added
        data = json.loads(response.data)
        assert 'transaction_id' in data
        assert data['success'] is True
        
        # Get the transaction to verify
        transaction_id = data['transaction_id']
        response = app_client_with_user.get(f'/api/account-transactions?account={account_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        transaction_found = False
        for transaction in data['transactions']:
            if transaction['id'] == transaction_id:
                transaction_found = True
                assert transaction['description'] == 'Test transaction'
                assert float(transaction['amount']) == 50.00
                assert transaction['category_id'] == category_id
                break
                
        assert transaction_found, "Added transaction not found in response"
        
    def test_update_transaction_api(self, app_client_with_user, sample_transactions, sample_categories):
        """Test updating a transaction through API."""
        # Get first transaction and a different category
        transactions = sample_transactions()  # Call the fixture function
        categories = sample_categories()  # Call the fixture function
        transaction = transactions[0]
        new_category_id = categories[1].id if categories[1].id != transaction.category_id else categories[0].id
        
        # Create update data - need all required fields for an update
        update_data = {
            'transaction_id': transaction.id,
            'account_id': transaction.account_id,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'description': 'Updated transaction',
            'amount': float(transaction.amount),
            'transaction_type': transaction.transaction_type,
            'category_id': new_category_id
        }
        
        # Post to API
        response = app_client_with_user.post(
            '/api/add-transaction',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify transaction was updated
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Get the transaction to verify
        response = app_client_with_user.get(f'/api/account-transactions?account={transaction.account_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        transaction_found = False
        for t in data['transactions']:
            if t['id'] == transaction.id:
                transaction_found = True
                assert t['description'] == 'Updated transaction'
                assert t['category_id'] == new_category_id
                break
                
        assert transaction_found, "Updated transaction not found in response"
        
    def test_delete_transaction_api(self, app_client_with_user, sample_transactions):
        """Test deleting a transaction through API."""
        # Get first transaction
        transactions = sample_transactions()  # Call the fixture function
        transaction = transactions[0]
        
        # Delete transaction
        response = app_client_with_user.post(
            '/api/delete-transaction',
            data=json.dumps({'transaction_id': transaction.id}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify transaction was deleted
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Try to get the transaction
        response = app_client_with_user.get(f'/api/account-transactions?account={transaction.account_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        for t in data['transactions']:
            assert t['id'] != transaction.id
            
    def test_bulk_categorize_api(self, app_client_with_user, sample_transactions, sample_categories):
        """Test bulk categorizing transactions through API."""
        # Get two transactions and a category
        transactions = sample_transactions()  # Call the fixture function
        categories = sample_categories()  # Call the fixture function
        transaction_ids = [transactions[0].id, transactions[1].id]
        category_id = categories[0].id
        
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
        for transaction in transactions[:2]:
            response = app_client_with_user.get(f'/api/account-transactions?account={transaction.account_id}')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            transaction_found = False
            for t in data['transactions']:
                if t['id'] == transaction.id:
                    transaction_found = True
                    assert t['category_id'] == category_id
                    break
                    
            assert transaction_found, f"Transaction {transaction.id} not found in response" 