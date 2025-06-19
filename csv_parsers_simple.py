import csv
import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from app import db
from models import Transaction, Account
from categorization import auto_categorize_transaction


class CSVParser:
    """Base class for CSV parsers"""
    
    def __init__(self, bank_name: str):
        self.bank_name = bank_name
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        """Parse CSV file and return number of transactions created"""
        raise NotImplementedError
    
    def clean_amount(self, amount_str: str) -> Decimal:
        """Clean and convert amount string to decimal"""
        if not amount_str:
            return Decimal('0.00')
        
        # Remove currency symbols, spaces, and commas
        cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
        
        # Handle empty string after cleaning
        if not cleaned:
            return Decimal('0.00')
        
        try:
            return Decimal(cleaned)
        except:
            return Decimal('0.00')
    
    def parse_date(self, date_str: str, formats: List[str]):
        """Parse date string using provided formats"""
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def create_transaction(self, account_id: int, user_id: int, date, description: str, 
                          amount: Decimal, transaction_type: str) -> Optional[Transaction]:
        """Create a transaction if it doesn't already exist"""
        # Check if transaction already exists
        existing = Transaction.query.filter_by(
            account_id=account_id,
            date=date,
            description=description,
            amount=amount
        ).first()
        
        if existing:
            return None
        
        # Extract merchant name
        merchant = self.extract_merchant(description)
        
        # Create new transaction
        transaction = Transaction(
            account_id=account_id,
            date=date,
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            merchant=merchant
        )
        
        # Auto-categorize
        category_id = auto_categorize_transaction(description, merchant, user_id)
        if category_id:
            transaction.category_id = category_id
        
        db.session.add(transaction)
        return transaction
    
    def extract_merchant(self, description: str) -> Optional[str]:
        """Extract merchant name from description"""
        # Remove common prefixes and suffixes
        merchant = description.strip()
        
        # Common patterns to clean
        patterns = [
            r'^(DEBIT|CREDIT|PURCHASE|PAYMENT)\s+',
            r'\s+\d+$',  # trailing numbers
            r'\s+[A-Z]{2,3}$',  # trailing country codes
            r'\*+',  # asterisks
        ]
        
        for pattern in patterns:
            merchant = re.sub(pattern, '', merchant, flags=re.IGNORECASE)
        
        return merchant.strip()[:200] if merchant.strip() else None


class AmexParser(CSVParser):
    """Parser for American Express CSV files"""
    
    def __init__(self):
        super().__init__("American Express")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        transactions_created = 0
        
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Amex format: Date, Description, Amount
                    date = self.parse_date(row['Date'], ['%m/%d/%Y', '%Y-%m-%d'])
                    description = row['Description'].strip()
                    amount = abs(self.clean_amount(row['Amount']))
                    
                    # Determine transaction type (Amex typically shows charges as positive)
                    transaction_type = 'expense'
                    
                    transaction = self.create_transaction(
                        account_id, user_id, date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        transactions_created += 1
                        
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
        
        db.session.commit()
        return transactions_created


class CibcParser(CSVParser):
    """Parser for CIBC CSV files"""
    
    def __init__(self):
        super().__init__("CIBC")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        transactions_created = 0
        
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    date = self.parse_date(row['Date'], ['%m/%d/%Y', '%Y-%m-%d'])
                    description = row['Description'].strip()
                    amount = abs(self.clean_amount(row['Amount']))
                    
                    transaction_type = 'expense'
                    
                    transaction = self.create_transaction(
                        account_id, user_id, date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        transactions_created += 1
                        
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
        
        db.session.commit()
        return transactions_created


class EqBankParser(CSVParser):
    """Parser for EQ Bank CSV files"""
    
    def __init__(self):
        super().__init__("EQ Bank")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        transactions_created = 0
        
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    date = self.parse_date(row['Date'], ['%Y-%m-%d', '%m/%d/%Y'])
                    description = row['Description'].strip()
                    
                    # EQ Bank might have separate debit/credit columns
                    debit = self.clean_amount(row.get('Debit', '0'))
                    credit = self.clean_amount(row.get('Credit', '0'))
                    
                    if debit > 0:
                        amount = debit
                        transaction_type = 'expense'
                    elif credit > 0:
                        amount = credit
                        transaction_type = 'income'
                    else:
                        continue
                    
                    transaction = self.create_transaction(
                        account_id, user_id, date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        transactions_created += 1
                        
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
        
        db.session.commit()
        return transactions_created


class SimpliiParser(CSVParser):
    """Parser for Simplii Financial CSV files"""
    
    def __init__(self):
        super().__init__("Simplii Financial")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        transactions_created = 0
        
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    date = self.parse_date(row['Date'], ['%m/%d/%Y', '%Y-%m-%d'])
                    description = row['Description'].strip()
                    amount = abs(self.clean_amount(row['Amount']))
                    
                    # Determine type based on amount sign or description
                    transaction_type = 'expense'
                    if 'deposit' in description.lower() or 'credit' in description.lower():
                        transaction_type = 'income'
                    
                    transaction = self.create_transaction(
                        account_id, user_id, date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        transactions_created += 1
                        
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
        
        db.session.commit()
        return transactions_created


class TdParser(CSVParser):
    """Parser for TD Bank CSV files"""
    
    def __init__(self):
        super().__init__("TD Bank")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        transactions_created = 0
        
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    date = self.parse_date(row['Date'], ['%m/%d/%Y', '%Y-%m-%d'])
                    description = row['Description'].strip()
                    amount = abs(self.clean_amount(row['Amount']))
                    
                    transaction_type = 'expense'
                    
                    transaction = self.create_transaction(
                        account_id, user_id, date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        transactions_created += 1
                        
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
        
        db.session.commit()
        return transactions_created


def get_parser_by_format(format_type: str) -> CSVParser:
    """Factory function to get the appropriate parser"""
    parsers = {
        'amex': AmexParser(),
        'cibc': CibcParser(),
        'eq_bank': EqBankParser(),
        'simplii': SimpliiParser(),
        'td': TdParser(),
    }
    
    return parsers.get(format_type.lower())


def detect_csv_format(filepath: str) -> str:
    """Automatically detect CSV format based on file content"""
    with open(filepath, 'r', encoding='utf-8') as file:
        # Read first few lines to detect format
        lines = [file.readline().strip() for _ in range(3)]
        header = lines[0].lower()
        
        # Simple detection based on header patterns
        if 'american express' in header or 'amex' in header:
            return 'amex'
        elif 'cibc' in header:
            return 'cibc'
        elif 'eq bank' in header or 'equitable' in header:
            return 'eq_bank'
        elif 'simplii' in header:
            return 'simplii'
        elif 'td' in header or 'toronto dominion' in header:
            return 'td'
        
        # Default fallback
        return 'amex'