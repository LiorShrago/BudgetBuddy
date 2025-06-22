import pytest
from decimal import Decimal
from datetime import datetime, date

def test_dashboard_metrics(client, auth, app, test_user):
    """Test all financial metrics on dashboard"""
    # Get test user ID
    user_id, _, _ = test_user
    
    # Create test user and log in
    auth.login()
    
    # Create test accounts with various types
    with app.app_context():
        from src.models.models import Account, db
        
        # Add test accounts
        accounts = [
            Account(user_id=user_id, name='Test Checking', account_type='checking', balance=1000.00, is_active=True),
            Account(user_id=user_id, name='Test Savings', account_type='savings', balance=5000.00, is_active=True),
            Account(user_id=user_id, name='Test Credit Card', account_type='credit_card', balance=500.00, is_active=True),
            Account(user_id=user_id, name='Test Investment', account_type='investment', balance=10000.00, is_active=True),
            Account(user_id=user_id, name='Test Loan', account_type='loan', balance=20000.00, is_active=True),
        ]
        for account in accounts:
            db.session.add(account)
        db.session.commit()
    
    # Test dashboard page loads with all metrics
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Test presence of all financial metrics
    html = response.data.decode()
    assert 'Net Worth' in html
    assert 'Credit Cards' in html
    assert 'Cash' in html
    assert 'Loans' in html
    assert 'Investments' in html
    
    # Test metric calculations
    assert '$-4,500.00' in html  # Net Worth (assets - liabilities)
    assert '$500.00' in html     # Credit Cards
    assert '$1,000.00' in html   # Cash
    assert '$20,000.00' in html  # Loans
    assert '$10,000.00' in html  # Investments

def test_dashboard_account_dropdowns(client, auth, app, test_user):
    """Test account dropdowns in dashboard cards"""
    # Get test user ID
    user_id, _, _ = test_user
    
    # Login and create test accounts
    auth.login()
    with app.app_context():
        from src.models.models import Account, db
        
        # Add test accounts
        accounts = [
            Account(user_id=user_id, name='Test Credit Card', account_type='credit_card', balance=500.00, is_active=True),
            Account(user_id=user_id, name='Test Checking', account_type='checking', balance=1000.00, is_active=True),
            Account(user_id=user_id, name='Test Loan', account_type='loan', balance=20000.00, is_active=True),
            Account(user_id=user_id, name='Test Investment', account_type='investment', balance=10000.00, is_active=True),
        ]
        for account in accounts:
            db.session.add(account)
        db.session.commit()
    
    response = client.get('/dashboard')
    html = response.data.decode()
    
    # Test presence of account dropdowns
    assert 'dropdown-credit-cards' in html
    assert 'dropdown-cash' in html
    assert 'dropdown-loans' in html
    assert 'dropdown-investments' in html

def test_dashboard_empty_state(client, auth, test_user):
    """Test dashboard display with no accounts"""
    # Get test user ID and login
    user_id, _, _ = test_user
    auth.login()
    
    response = client.get('/dashboard')
    html = response.data.decode()
    
    # Test empty state messages
    assert 'No credit card accounts found' in html
    assert 'No cash accounts found' in html
    assert 'No loan accounts found' in html
    assert 'No investment accounts found' in html 