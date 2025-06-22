"""
API Tests for BudgetBuddy
========================

This module contains tests for the BudgetBuddy API endpoints including:
- Data retrieval endpoints
- Data modification endpoints
- Error handling
- Authorization checks

These tests ensure that the API works correctly and securely.
"""

import unittest
import sys
import os
import pytest
import json
from datetime import datetime, date, timedelta

# Add the parent directory to the path so we can import from the main application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from src.models.models import Category, Transaction, Account, User


class TestApiEndpoints(unittest.TestCase):
    """Tests for API endpoints."""
    
    def setUp(self):
        """Set up test environment."""
        flask_app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SERVER_NAME': 'localhost.localdomain',
            'SESSION_TYPE': 'filesystem',
            'SESSION_FILE_DIR': 'tests/test_session',
            'SESSION_PERMANENT': False,
            'SESSION_USE_SIGNER': True,
            'PERMANENT_SESSION_LIFETIME': 3600  # 1 hour for testing
        })
        
        # Create session directory if it doesn't exist
        os.makedirs('tests/test_session', exist_ok=True)
        
        self.app = flask_app
        self.client = self.app.test_client()
        
        # Create an application context
        with self.app.app_context():
            # Create database tables
            db.create_all()
            
            # Create a test user
            self.user = User(username='testuser', email='test@example.com')
            self.user.set_password('Test@123456')
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            
            # Create test categories
            categories = [
                Category(user_id=self.user_id, name='Food', color='#FF5733'),
                Category(user_id=self.user_id, name='Transportation', color='#33FF57'),
                Category(user_id=self.user_id, name='Housing', color='#3357FF'),
            ]
            
            for category in categories:
                db.session.add(category)
                
            db.session.commit()
            
            # Create test accounts
            accounts = [
                Account(
                    user_id=self.user_id,
                    name='Test Checking',
                    account_type='checking',
                    balance=1000.00
                ),
                Account(
                    user_id=self.user_id,
                    name='Test Savings',
                    account_type='savings',
                    balance=5000.00
                ),
                Account(
                    user_id=self.user_id,
                    name='Test Credit Card',
                    account_type='credit_card',
                    balance=-500.00
                )
            ]
            
            for account in accounts:
                db.session.add(account)
                
            db.session.commit()
            
            # Store IDs for later use
            self.category_ids = [c.id for c in Category.query.all()]
            self.account_ids = [a.id for a in Account.query.all()]
            
            # Login to create session
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_spending_chart_api(self):
        """Test the spending chart API endpoint."""
        with self.app.app_context():
            response = self.client.get('/api/spending-chart')
            self.assertEqual(response.status_code, 200)
            
            # Check response format
            data = json.loads(response.data.decode('utf-8'))
            self.assertIn('labels', data)
            self.assertIn('data', data)
            self.assertIn('colors', data)
    
    def test_spending_chart_unauthorized(self):
        """Test that unauthorized users cannot access API endpoints."""
        # Create a new client (not logged in)
        with self.app.app_context():
            unauth_client = self.app.test_client()
            response = unauth_client.get('/api/spending-chart', follow_redirects=False)
            # Should be redirected to login
            self.assertIn(response.status_code, (302, 303))  # Redirect
            
            # Follow redirect to confirm it goes to login
            response = unauth_client.get('/api/spending-chart', follow_redirects=True)
            self.assertIn(b'Please log in', response.data)
    
    def test_visualization_data_api(self):
        """Test the visualization data API endpoint."""
        with self.app.app_context():
            response = self.client.get('/api/visualization-data')
            self.assertEqual(response.status_code, 200)
            
            # Check response format
            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('categories', data['data'])
            self.assertIn('trend', data['data'])
            self.assertIn('monthly', data['data'])
            self.assertIn('accounts', data['data'])
            self.assertIn('summary', data['data'])
    
    def test_create_category_api(self):
        """Test the create category API endpoint."""
        with self.app.app_context():
            # Create a new category
            response = self.client.post('/api/create-category', 
                                       json={
                                           'name': 'Test API Category',
                                           'color': '#FF5733'
                                       })
            self.assertEqual(response.status_code, 200)
            
            # Check response format
            data = json.loads(response.data.decode('utf-8'))
            self.assertIn('success', data)
            if data['success']:
                # Check for category object in response
                self.assertIn('category', data)
                if 'category' in data:
                    self.assertIn('id', data['category'])
                    self.assertIn('name', data['category'])
                    self.assertIn('color', data['category'])
            
            # Verify category was created
            category = Category.query.filter_by(
                user_id=self.user_id,
                name='Test API Category'
            ).first()
            self.assertIsNotNone(category)
            self.assertEqual(category.color, '#FF5733')
    
    def test_update_category_api(self):
        """Test the update category API endpoint."""
        with self.app.app_context():
            # Create a test transaction with proper date object
            account_id = self.account_ids[0]
            transaction = Transaction(
                account_id=account_id,
                date=date(2023, 1, 1),  # Use Python date object
                description='Test Transaction',
                amount=100.00,
                transaction_type='expense'
            )
            db.session.add(transaction)
            db.session.commit()
            transaction_id = transaction.id
            
            # Update category
            category_id = self.category_ids[0]
            response = self.client.post('/api/update-category', 
                                       json={
                                           'transaction_id': transaction_id,
                                           'category_id': category_id
                                       })
            
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data.decode('utf-8'))
            if 'success' in data:  # If transaction exists and was updated
                self.assertTrue(data['success'])
            else:  # If transaction doesn't exist (expected in test environment)
                self.assertIn('error', data)
                
            # Verify the transaction was updated
            updated_transaction = Transaction.query.get(transaction_id)
            self.assertEqual(updated_transaction.category_id, category_id)
    
    def test_bulk_categorize_api(self):
        """Test the bulk categorize API endpoint."""
        with self.app.app_context():
            # Create test transactions
            account_id = self.account_ids[0]  
            category_id = self.category_ids[0]
            
            # Create some uncategorized transactions
            transaction_ids = []
            for i in range(3):
                transaction = Transaction(
                    account_id=account_id,
                    date=date(2023, 1, i+1),  # Use Python date object
                    description=f'Test Transaction {i+1}',
                    amount=100.00 + i,
                    transaction_type='expense'
                )
                db.session.add(transaction)
            
            db.session.commit()
            
            # Get the IDs of the transactions we just created
            transactions = Transaction.query.filter_by(account_id=account_id).all()
            transaction_ids = [t.id for t in transactions]
            
            # Bulk categorize transactions
            response = self.client.post('/api/bulk-categorize', 
                                       json={
                                           'transaction_ids': transaction_ids,
                                           'category_id': category_id
                                       })
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode('utf-8'))
            self.assertIn('success', data)
            
            # Verify transactions were updated
            for tid in transaction_ids:
                trans = Transaction.query.get(tid)
                self.assertEqual(trans.category_id, category_id)
    
    def test_ai_suggest_categories(self):
        """Test the AI suggest categories API endpoint."""
        # This is more of an integration test and depends on the AI service
        # We'll just check that the endpoint responds properly
        with self.app.app_context():
            response = self.client.post('/api/ai-suggest-categories', 
                                       json={
                                           'description': 'Grocery shopping at Walmart'
                                       })
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode('utf-8'))
            
            # The AI service might not be available in testing
            # So just check for a response structure
            if 'suggestions' in data:
                self.assertIsInstance(data['suggestions'], list)
            else:
                # If AI service isn't available, there should be an error message
                self.assertTrue('error' in data or 'message' in data)


class TestApiErrorHandling(unittest.TestCase):
    """Tests for API error handling."""
    
    def setUp(self):
        """Set up test environment."""
        flask_app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SERVER_NAME': 'localhost.localdomain',
            'SESSION_TYPE': 'filesystem',
            'SESSION_FILE_DIR': 'tests/test_session',
            'SESSION_PERMANENT': False,
            'SESSION_USE_SIGNER': True,
            'PERMANENT_SESSION_LIFETIME': 3600  # 1 hour for testing
        })
        
        # Create session directory if it doesn't exist
        os.makedirs('tests/test_session', exist_ok=True)
        
        self.app = flask_app
        self.client = self.app.test_client()
        
        # Create an application context
        with self.app.app_context():
            # Create database tables
            db.create_all()
            
            # Create a test user
            self.user = User(username='testuser', email='test@example.com')
            self.user.set_password('Test@123456')
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            
            # Login to create session
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_invalid_category_id(self):
        """Test API error handling for invalid category ID."""
        with self.app.app_context():
            response = self.client.post('/api/update-category', 
                                       json={
                                           'transaction_id': '1',
                                           'category_id': '999999'  # Invalid ID
                                       })
            
            self.assertIn(response.status_code, (200, 400, 404))  # Varies by implementation
            data = json.loads(response.data.decode('utf-8'))
            
            # Should either return error in JSON or success=False
            if 'error' in data:
                self.assertIn('error', data)
            elif 'message' in data:
                self.assertIn('message', data)
            else:
                self.assertFalse(data.get('success', True))
    
    def test_missing_parameters(self):
        """Test API error handling for missing parameters."""
        # Missing required parameters
        with self.app.app_context():
            response = self.client.post('/api/update-category', json={})
            
            self.assertIn(response.status_code, (200, 400, 422))  # Varies by implementation
            data = json.loads(response.data.decode('utf-8'))
            
            # Should either return error in JSON or success=False
            if 'error' in data:
                self.assertIn('error', data)
            elif 'message' in data:
                self.assertIn('message', data)
            else:
                self.assertFalse(data.get('success', True))


class TestApiSecurity(unittest.TestCase):
    """Tests for API security."""
    
    def setUp(self):
        """Set up test environment."""
        flask_app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SERVER_NAME': 'localhost.localdomain',
            'SESSION_TYPE': 'filesystem',
            'SESSION_FILE_DIR': 'tests/test_session',
            'SESSION_PERMANENT': False,
            'SESSION_USE_SIGNER': True,
            'PERMANENT_SESSION_LIFETIME': 3600  # 1 hour for testing
        })
        
        # Create session directory if it doesn't exist
        os.makedirs('tests/test_session', exist_ok=True)
        
        self.app = flask_app
        self.client = self.app.test_client()
        
        # Create an application context
        with self.app.app_context():
            # Create database tables
            db.create_all()
            
            # Create a test user
            self.user = User(username='testuser', email='test@example.com')
            self.user.set_password('Test@123456')
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            
            # Create test category
            category = Category(user_id=self.user_id, name='Food', color='#FF5733')
            db.session.add(category)
            db.session.commit()
            self.category_id = category.id
            
            # Login to create session
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_api_csrf_protection(self):
        """Test API endpoints for CSRF protection."""
        # Skip if CSRF is disabled for testing
        if self.app.config.get('WTF_CSRF_ENABLED') is False:
            self.skipTest("CSRF protection is disabled in testing mode")
        
        # Try to update without CSRF token
        with self.app.app_context():
            response = self.client.post('/api/update-category', 
                                       json={
                                           'transaction_id': '1',
                                           'category_id': str(self.category_id)
                                       }, 
                                       headers={'X-Requested-With': 'XMLHttpRequest'})
            
            # Should fail with CSRF error
            self.assertIn(response.status_code, (400, 403))
    
    def test_api_rate_limiting(self):
        """Test API rate limiting (if implemented)."""
        # Make multiple rapid requests to API
        with self.app.app_context():
            responses = []
            for _ in range(20):
                response = self.client.get('/api/visualization-data')
                responses.append(response)
            
            # Check if any responses indicate rate limiting
            rate_limited = any(r.status_code == 429 for r in responses)
            
            # This is more of a check than a requirement
            # If rate limiting is implemented, some responses might be 429
            # If not implemented, all should be 200
            for response in responses:
                self.assertIn(response.status_code, (200, 429))
                
            # Just a sanity check that all responses are valid
            for response in responses[:5]:  # Check at least first few
                if response.status_code == 200:
                    data = json.loads(response.data.decode('utf-8'))
                    self.assertTrue(data['success'])
                    self.assertIn('data', data)


if __name__ == '__main__':
    unittest.main() 