from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import io
import base64
import time


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Two-Factor Authentication fields
    totp_secret = db.Column(db.String(32), nullable=True)
    is_two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_backup_codes = db.Column(db.Text, nullable=True)  # JSON string of backup codes
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_token = db.Column(db.String(128), nullable=True)  # For secure session management
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_account_locked(self):
        """Check if account is currently locked due to failed login attempts"""
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock account if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts and unlock account"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def generate_totp_secret(self):
        """Generate a new TOTP secret for 2FA setup"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self, app_name="BudgetBuddy"):
        """Get TOTP URI for QR code generation"""
        if not self.totp_secret:
            return None
        totp = pyotp.totp.TOTP(self.totp_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name=app_name
        )
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.totp_secret:
            return False
        
        # Normalize the token (remove spaces and non-numeric characters)
        token = ''.join(c for c in token if c.isdigit())
        
        if len(token) != 6:
            return False
            
        try:
            # Create TOTP object
            totp = pyotp.TOTP(self.totp_secret)
            
            # Try exact match first
            if totp.verify(token):
                return True
                
            # If that fails, try with a larger window (±5 windows = ±2.5 minutes)
            return totp.verify(token, valid_window=5)
        except Exception:
            # Catch any unexpected errors in the TOTP library
            return False
    
    def generate_backup_codes(self):
        """Generate backup codes for 2FA recovery"""
        import secrets
        import json
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.two_factor_backup_codes = json.dumps(codes)
        return codes
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if not self.two_factor_backup_codes:
            return False
        
        # Normalize the code (remove spaces, convert to uppercase)
        code = ''.join(c for c in code if c.isalnum()).upper()
        
        import json
        try:
            codes = json.loads(self.two_factor_backup_codes)
            if code in codes:
                codes.remove(code)
                self.two_factor_backup_codes = json.dumps(codes)
                db.session.commit()
                return True
        except (json.JSONDecodeError, ValueError):
            pass
        return False
    
    def enable_two_factor(self):
        """Enable two-factor authentication"""
        if self.totp_secret:
            self.is_two_factor_enabled = True
            db.session.commit()
            return True
        return False
    
    def disable_two_factor(self):
        """Disable two-factor authentication"""
        self.is_two_factor_enabled = False
        self.totp_secret = None
        self.two_factor_backup_codes = None
        db.session.commit()
    
    def generate_qr_code(self, app_name="BudgetBuddy"):
        """Generate QR code for TOTP setup"""
        if not self.totp_secret:
            return None
        
        uri = self.get_totp_uri(app_name)
        if not uri:
            return None
        
        qr = qrcode.main.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # checking, savings, credit_card, investment
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade='all, delete-orphan')





class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense
    merchant = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_split = db.Column(db.Boolean, default=False)
    parent_transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=True)
    
    # Self-referential relationship for split transactions
    split_transactions = db.relationship('Transaction', backref=db.backref('parent_transaction', remote_side=[id]), lazy=True)


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    period_type = db.Column(db.String(20), nullable=False)  # weekly, monthly, yearly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_budget = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    budget_items = db.relationship('BudgetItem', backref='budget', lazy=True, cascade='all, delete-orphan')


class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    allocated_amount = db.Column(db.Numeric(10, 2), nullable=False)





class LoginAttempt(db.Model):
    """Track login attempts for security monitoring"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for failed username attempts
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    attempted_username = db.Column(db.String(64))
    success = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    two_factor_used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='login_attempts')
