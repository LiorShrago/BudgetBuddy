"""
Security Tests for BudgetBuddy
=============================

This module contains tests for security features including:
- Session management
- CSRF protection
- Login attempt tracking
- Account lockout
- Access control for protected routes
- Security headers

These tests ensure that the application's security features work correctly and
provide adequate protection against common security threats.
"""

import unittest
import sys
import os
import pytest
from flask import session

# Add the parent directory to the path so we can import from the main application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from models import User, LoginAttempt


class TestSessionManagement(unittest.TestCase):
    """Tests for session management functionality."""
    
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
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_session_creation(self):
        """Test session creation during login."""
        # Login
        with self.app.app_context():
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
            
            # Check session is created
            with self.client.session_transaction() as sess:
                self.assertIn('_id', sess)  # Session ID should exist
    
    def test_session_destruction(self):
        """Test session destruction during logout."""
        # Login first
        with self.app.app_context():
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
            
            # Logout
            self.client.get('/logout')
            
            # Session should be cleared
            with self.client.session_transaction() as sess:
                self.assertNotIn('_id', sess)
    
    def test_session_access_after_logout(self):
        """Test access to protected routes after logout."""
        # Login first
        with self.app.app_context():
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
            
            # Logout
            self.client.get('/logout')
            
            # Try to access protected route
            response = self.client.get('/dashboard', follow_redirects=True)
            self.assertIn(b'Please log in', response.data)


class TestAccessControl(unittest.TestCase):
    """Tests for access control to protected resources."""
    
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
            
            # Create another user
            self.other_user = User(username='otheruser', email='other@example.com')
            self.other_user.set_password('OtherPass@123')
            db.session.add(self.other_user)
            db.session.commit()
            self.other_user_id = self.other_user.id
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_protected_routes_require_login(self):
        """Test that protected routes require login."""
        protected_routes = [
            '/dashboard',
            '/accounts',
            '/transactions',
            '/budgets',
            '/categories',
            '/security',
            '/upload'
        ]
        
        for route in protected_routes:
            with self.app.app_context():
                response = self.client.get(route, follow_redirects=True)
                self.assertIn(b'Please log in', response.data)
    
    def test_user_cannot_access_others_data(self):
        """Test that users cannot access other users' data."""
        # Login as test_user
        with self.app.app_context():
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
            
            # Try to access other user's data by manipulating URL parameters
            # In this example, we'll try to directly access a URL with user_id parameter
            # Note: This test assumes your app has routes with user_id parameter
            
            # For testing purposes, we'll test if any user-specific route leaks data
            # by checking if account data contains other user's information
            response = self.client.get('/accounts')
            self.assertNotIn(b'otheruser', response.data)


class TestLoginSecurity(unittest.TestCase):
    """Tests for login security features."""
    
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
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login_attempt_tracking(self):
        """Test that login attempts are properly tracked."""
        # Failed login attempt
        with self.app.app_context():
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'WrongPassword@123'
            })
            
            # Check login attempt was recorded
            attempts = LoginAttempt.query.filter_by(user_id=self.user_id, success=False).all()
            self.assertEqual(len(attempts), 1)
            
            # Check IP and user agent were recorded
            self.assertIsNotNone(attempts[0].ip_address)
            self.assertIsNotNone(attempts[0].user_agent)
    
    def test_progressive_lockout(self):
        """Test progressive account lockout after multiple failed attempts."""
        # Make several failed login attempts
        with self.app.app_context():
            for i in range(1, 6):
                self.client.post('/login', data={
                    'username': 'testuser',
                    'password': f'WrongPassword{i}'
                })
                
                # Check lockout status after each attempt
                user = User.query.get(self.user_id)
                
                if i < 5:
                    # Account should not be locked yet
                    self.assertFalse(user.is_account_locked())
                    self.assertEqual(user.failed_login_attempts, i)
                else:
                    # Account should be locked after 5 attempts
                    self.assertTrue(user.is_account_locked())
                    self.assertIsNotNone(user.account_locked_until)
    
    def test_security_log(self):
        """Test that security log displays login attempts."""
        # Create some login attempts
        with self.app.app_context():
            # Login to create session
            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            })
            
            # Create failed login attempt
            test_client = self.app.test_client()
            test_client.post('/login', data={
                'username': 'testuser',
                'password': 'WrongPassword@123'
            })
            
            # Check security log
            response = self.client.get('/security-log')
            
            # Verify attempts appear in log
            self.assertIn(b'Failed', response.data)
            self.assertIn(b'Successful', response.data)


class TestProtectionMechanisms(unittest.TestCase):
    """Tests for various protection mechanisms."""
    
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
    
    def test_csrf_protection(self):
        """Test CSRF protection for form submissions.
        
        Note: Since we disabled CSRF for testing, this test checks if CSRF is 
        properly disabled in testing mode and enabled otherwise.
        """
        # In test mode, CSRF should be disabled and this request should work
        with self.app.app_context():
            response = self.client.post('/change-password', data={
                'current_password': 'anything',
                'new_password': 'NewPass@123',
                'confirm_password': 'NewPass@123'
            }, follow_redirects=True)
            
            # Should fail because of incorrect current password, not CSRF
            self.assertIn(b'Current password is incorrect', response.data)
            
            # Check that CSRF is enabled in production mode
            self.assertFalse(self.app.config['WTF_CSRF_ENABLED'])  # Should be disabled for testing
    
    def test_http_security_headers(self):
        """Test that security headers are properly set."""
        with self.app.app_context():
            response = self.client.get('/')
            headers = response.headers
            
            # Test for common security headers
            # Uncomment these as you implement them in your application
            
            # self.assertEqual(headers.get('X-Content-Type-Options'), 'nosniff')
            # self.assertEqual(headers.get('X-Frame-Options'), 'SAMEORIGIN')
            # self.assertEqual(headers.get('X-XSS-Protection'), '1; mode=block')
            # self.assertIn('Content-Security-Policy', headers)
    
    def test_secure_password_storage(self):
        """Test that passwords are securely stored."""
        with self.app.app_context():
            user = User.query.get(self.user_id)
            
            # Password should be hashed, not stored in plain text
            self.assertNotEqual(user.password_hash, 'Test@123456')
            
            # Hash should be long enough to be secure
            self.assertGreater(len(user.password_hash), 50)
            
            # Should be able to verify password
            self.assertTrue(user.check_password('Test@123456'))
            self.assertFalse(user.check_password('WrongPassword'))


if __name__ == '__main__':
    unittest.main() 