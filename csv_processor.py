import pandas as pd
import re
from datetime import datetime
from decimal import Decimal
from app import db
from models import Transaction, Account
from categorization import auto_categorize_transaction


def process_csv_file(filepath, account_id, user_id):
    """Process uploaded CSV file and create transactions"""
    try:
        # Read CSV file
        df = pd.read_csv(filepath)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Try to detect common column mappings
        column_mapping = detect_column_mapping(df.columns)
        
        if not column_mapping:
            raise ValueError("Could not detect required columns (date, description, amount)")
        
        transactions_created = 0
        
        for _, row in df.iterrows():
            try:
                # Extract transaction data
                transaction_date = parse_date(row[column_mapping['date']])
                description = clean_description(str(row[column_mapping['description']]))
                amount = parse_amount(row[column_mapping['amount']])
                
                # Skip if essential data is missing
                if not transaction_date or not description or amount is None:
                    continue
                
                # Determine transaction type
                transaction_type = 'expense' if amount < 0 else 'income'
                amount = abs(amount)  # Store as positive value
                
                # Extract merchant name
                merchant = extract_merchant_name(description)
                
                # Check for duplicates
                existing_transaction = Transaction.query.join(Account).filter(
                    Account.user_id == user_id,
                    Transaction.account_id == account_id,
                    Transaction.date == transaction_date,
                    Transaction.description == description,
                    Transaction.amount == amount
                ).first()
                
                if existing_transaction:
                    continue  # Skip duplicate
                
                # Create transaction
                transaction = Transaction(
                    account_id=account_id,
                    date=transaction_date,
                    description=description,
                    amount=amount,
                    transaction_type=transaction_type,
                    merchant=merchant
                )
                
                # Auto-categorize transaction
                category_id = auto_categorize_transaction(description, merchant, user_id)
                if category_id:
                    transaction.category_id = category_id
                
                db.session.add(transaction)
                transactions_created += 1
                
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        db.session.commit()
        return transactions_created
        
    except Exception as e:
        db.session.rollback()
        raise e


def detect_column_mapping(columns):
    """Detect column mappings based on common patterns"""
    mapping = {}
    
    # Date column patterns
    date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
    for pattern in date_patterns:
        for col in columns:
            if pattern in col:
                mapping['date'] = col
                break
        if 'date' in mapping:
            break
    
    # Description column patterns
    desc_patterns = ['description', 'desc', 'memo', 'transaction', 'details']
    for pattern in desc_patterns:
        for col in columns:
            if pattern in col:
                mapping['description'] = col
                break
        if 'description' in mapping:
            break
    
    # Amount column patterns
    amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
    for pattern in amount_patterns:
        for col in columns:
            if pattern in col:
                mapping['amount'] = col
                break
        if 'amount' in mapping:
            break
    
    # Check if we have all required mappings
    if all(key in mapping for key in ['date', 'description', 'amount']):
        return mapping
    
    return None


def parse_date(date_str):
    """Parse date string into date object"""
    if pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    
    # Common date formats
    date_formats = [
        '%m/%d/%Y',
        '%m-%d-%Y',
        '%Y-%m-%d',
        '%m/%d/%y',
        '%m-%d-%y',
        '%d/%m/%Y',
        '%d-%m-%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def parse_amount(amount_str):
    """Parse amount string into decimal"""
    if pd.isna(amount_str):
        return None
    
    amount_str = str(amount_str).strip()
    
    # Remove currency symbols and spaces
    amount_str = re.sub(r'[^\d\.\-\+]', '', amount_str)
    
    try:
        return Decimal(amount_str)
    except:
        return None


def clean_description(description):
    """Clean and normalize transaction description"""
    if pd.isna(description):
        return ""
    
    description = str(description).strip()
    
    # Remove common patterns that don't add value
    patterns_to_remove = [
        r'\*+\d+\*+',  # Card numbers like *1234*
        r'#\d+',       # Reference numbers
        r'\d{4}-\d{4}',  # Date patterns
    ]
    
    for pattern in patterns_to_remove:
        description = re.sub(pattern, '', description)
    
    return description.strip()


def extract_merchant_name(description):
    """Extract merchant name from transaction description"""
    if not description:
        return None
    
    # Simple merchant extraction - take first part before common separators
    separators = [' - ', ' / ', ' #', ' *', '  ']
    
    merchant = description
    for sep in separators:
        if sep in merchant:
            merchant = merchant.split(sep)[0]
            break
    
    return merchant.strip()[:200]  # Limit length
