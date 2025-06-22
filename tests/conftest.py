"""
BudgetBuddy Test Configuration
=============================

This module contains pytest fixtures and configuration for BudgetBuddy tests.
Fixtures provide reusable test components like database connections, test clients,
and test users that can be shared across multiple test functions.
"""

import os
import pytest
import sys
import pyotp
import json
from datetime import datetime, timedelta
from flask import appcontext_pushed, g

# Add the parent directory to the path so we can import from the main application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db
from src.models.models import User, Account, Category, Transaction, LoginAttempt


@pytest.fixture
def app():
    """
    Create and configure a Flask application instance for testing.
    
    This fixture configures the application with test-specific settings,
    creates an in-memory database, and sets up the application context.
    
    Returns:
        flask.Flask: A configured Flask application for testing
    """
    # Configure app for testing
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
    
    # Create application context and push it
    with flask_app.app_context():
        # Create database tables
        db.create_all()
        
        yield flask_app
        
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Create a Flask test client for the application.
    
    Args:
        app: The Flask application fixture
        
    Returns:
        flask.testing.FlaskClient: A test client for the Flask application
    """
    return app.test_client()


@pytest.fixture
def test_user(app):
    """
    Create a test user in the database.
    
    This creates a user with username 'testuser' and password 'Test@123456'.
    
    Args:
        app: The Flask application fixture
        
    Returns:
        tuple: (user_id, username, password)
    """
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('Test@123456')
        db.session.add(user)
        db.session.commit()
        
        return user.id, 'testuser', 'Test@123456'


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Create an authenticated client session.
    
    This logs in the test user and returns a client with an active session.
    
    Args:
        client: The Flask test client fixture
        test_user: The test user fixture
        
    Returns:
        flask.testing.FlaskClient: An authenticated test client
    """
    user_id, username, password = test_user
    
    # Login
    client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)
    
    return client


@pytest.fixture
def user_with_2fa(app, test_user):
    """
    Create a test user with 2FA enabled.
    
    Args:
        app: The Flask application fixture
        test_user: The test user fixture
        
    Returns:
        tuple: (user_id, username, password, totp_secret)
    """
    user_id, username, password = test_user
    
    with app.app_context():
        user = User.query.get(user_id)
        
        # Configure 2FA
        totp_secret = user.generate_totp_secret()
        user.enable_two_factor()
        user.generate_backup_codes()
        db.session.commit()
        
        return user_id, username, password, totp_secret


@pytest.fixture
def valid_totp_code(user_with_2fa):
    """
    Generate a valid TOTP code for the test user with 2FA.
    
    Args:
        user_with_2fa: The user with 2FA fixture
        
    Returns:
        str: A valid 6-digit TOTP code
    """
    _, _, _, totp_secret = user_with_2fa
    totp = pyotp.TOTP(totp_secret)
    return totp.now()


@pytest.fixture
def backup_codes(app, user_with_2fa):
    """
    Get the backup codes for a user with 2FA.
    
    Args:
        app: The Flask application fixture
        user_with_2fa: The user with 2FA fixture
        
    Returns:
        list: List of backup codes
    """
    user_id, _, _, _ = user_with_2fa
    
    with app.app_context():
        user = User.query.get(user_id)
        return json.loads(user.two_factor_backup_codes)


@pytest.fixture
def test_accounts(app, test_user):
    """
    Create test accounts for the test user.
    
    Args:
        app: The Flask application fixture
        test_user: The test user fixture
        
    Returns:
        list: List of account IDs
    """
    user_id, _, _ = test_user
    account_ids = []
    
    with app.app_context():
        # Create checking account
        checking = Account(
            user_id=user_id,
            name='Test Checking',
            account_type='checking',
            balance=1000.00
        )
        db.session.add(checking)
        
        # Create savings account
        savings = Account(
            user_id=user_id,
            name='Test Savings',
            account_type='savings',
            balance=5000.00
        )
        db.session.add(savings)
        
        # Create credit card account
        credit = Account(
            user_id=user_id,
            name='Test Credit Card',
            account_type='credit_card',
            balance=-500.00
        )
        db.session.add(credit)
        
        db.session.commit()
        
        account_ids.extend([checking.id, savings.id, credit.id])
        
    return account_ids


@pytest.fixture
def test_categories(app, test_user):
    """
    Create test categories for the test user.
    
    Args:
        app: The Flask application fixture
        test_user: The test user fixture
        
    Returns:
        list: List of category IDs
    """
    user_id, _, _ = test_user
    category_ids = []
    
    with app.app_context():
        # Create parent categories
        categories = [
            Category(user_id=user_id, name='Food', color='#FF5733'),
            Category(user_id=user_id, name='Transportation', color='#33FF57'),
            Category(user_id=user_id, name='Housing', color='#3357FF'),
        ]
        
        for category in categories:
            db.session.add(category)
            
        db.session.commit()
        
        for category in categories:
            category_ids.append(category.id)
    
    return category_ids


@pytest.fixture
def auth(client):
    """
    Authentication fixture for tests.
    
    This fixture provides helper functions for authentication operations
    like login, logout, and registration.
    
    Args:
        client: The Flask test client fixture
        
    Returns:
        AuthActions: An object with authentication helper methods
    """
    class AuthActions:
        def __init__(self, client):
            self._client = client
        
        def login(self, username='testuser', password='Test@123456'):
            return self._client.post(
                '/login',
                data={'username': username, 'password': password},
                follow_redirects=True
            )
        
        def logout(self):
            return self._client.get('/logout', follow_redirects=True)
        
        def register(self, username='newuser', email='new@example.com', password='Test@123456'):
            return self._client.post(
                '/register',
                data={
                    'username': username,
                    'email': email,
                    'password': password,
                    'confirm_password': password
                },
                follow_redirects=True
            )
    
    return AuthActions(client) 