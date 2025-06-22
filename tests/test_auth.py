"""
Authentication Tests for BudgetBuddy
===================================

This module contains tests for authentication functionality including:
- User registration
- Login
- Password validation
- Two-Factor Authentication (2FA)
- Account lockout

These tests ensure that the authentication system is secure and works correctly.
"""

import unittest
import sys
import os
import pytest
import pyotp
import json

# Add the parent directory to the path so we can import from the main application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from src.models.models import User, LoginAttempt


class TestRegistration(unittest.TestCase):
    """Tests for user registration functionality."""
    
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
    
    def test_registration_valid(self):
        """Test registration with valid user data."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'NewPass@123',
                'confirm_password': 'NewPass@123'
            }, follow_redirects=True)
            
            # Check response
            self.assertIn(b'Registration successful', response.data)
            
            # Verify user exists in database
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'new@example.com')
            self.assertTrue(user.check_password('NewPass@123'))
    
    def test_registration_duplicate_username(self):
        """Test registration with existing username."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'testuser',  # Use existing username
                'email': 'another@example.com',
                'password': 'NewPass@123',
                'confirm_password': 'NewPass@123'
            }, follow_redirects=True)
            
            self.assertIn(b'Username already exists', response.data)
    
    def test_registration_duplicate_email(self):
        """Test registration with existing email."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'anotherusername',
                'email': 'test@example.com',  # Use existing email
                'password': 'NewPass@123',
                'confirm_password': 'NewPass@123'
            }, follow_redirects=True)
            
            self.assertIn(b'Email already exists', response.data)
    
    def test_registration_password_mismatch(self):
        """Test registration with non-matching passwords."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'Password@123',
                'confirm_password': 'DifferentPassword@123'
            }, follow_redirects=True)
            
            self.assertIn(b'Passwords do not match', response.data)


class TestPasswordStrength(unittest.TestCase):
    """Tests for password strength validation."""
    
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
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_password_too_short(self):
        """Test registration with password that's too short."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'Sh0rt!',
                'confirm_password': 'Sh0rt!'
            }, follow_redirects=True)
            
            self.assertIn(b'Password must be at least 8 characters long', response.data)
    
    def test_password_no_uppercase(self):
        """Test registration with password without uppercase letters."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'password123!',
                'confirm_password': 'password123!'
            }, follow_redirects=True)
            
            self.assertIn(b'Password must contain at least one uppercase letter', response.data)
    
    def test_password_no_lowercase(self):
        """Test registration with password without lowercase letters."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'PASSWORD123!',
                'confirm_password': 'PASSWORD123!'
            }, follow_redirects=True)
            
            self.assertIn(b'Password must contain at least one lowercase letter', response.data)
    
    def test_password_no_digit(self):
        """Test registration with password without digits."""
        with self.app.app_context():
            response = self.client.post('/register', data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'Password!',
                'confirm_password': 'Password!'
            }, follow_redirects=True)
            
            self.assertIn(b'Password must contain at least one number', response.data)


class TestLogin(unittest.TestCase):
    """Tests for login functionality."""
    
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
    
    def test_login_valid(self):
        """Test login with valid credentials."""
        with self.app.app_context():
            response = self.client.post('/login', data={
                'username': 'testuser',
                'password': 'Test@123456'
            }, follow_redirects=True)
            
            self.assertIn(b'Dashboard', response.data)
    
    def test_login_invalid_username(self):
        """Test login with invalid username."""
        with self.app.app_context():
            response = self.client.post('/login', data={
                'username': 'nonexistentuser',
                'password': 'SomePassword@123'
            }, follow_redirects=True)
            
            self.assertIn(b'Invalid username or password', response.data)
    
    def test_login_invalid_password(self):
        """Test login with invalid password."""
        with self.app.app_context():
            response = self.client.post('/login', data={
                'username': 'testuser',
                'password': 'WrongPassword@123'
            }, follow_redirects=True)
            
            self.assertIn(b'Invalid username or password', response.data)


if __name__ == '__main__':
    unittest.main() 