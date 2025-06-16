import pandas as pd
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
        if pd.isna(amount_str) or amount_str == '':
            return Decimal('0.00')
        
        # Convert to string and clean
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols, spaces, and commas
        amount_str = re.sub(r'[^\d\.\-\+\(\)]', '', amount_str)
        
        # Handle parentheses as negative
        if '(' in amount_str and ')' in amount_str:
            amount_str = '-' + amount_str.replace('(', '').replace(')', '')
        
        try:
            return Decimal(amount_str)
        except:
            return Decimal('0.00')
    
    def parse_date(self, date_str: str, formats: List[str]):
        """Parse date string using provided formats"""
        if pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def create_transaction(self, account_id: int, user_id: int, date, description: str, 
                          amount: Decimal, transaction_type: str) -> Optional[Transaction]:
        """Create a transaction if it doesn't already exist"""
        # Check for duplicates
        existing = Transaction.query.join(Account).filter(
            Account.user_id == user_id,
            Transaction.account_id == account_id,
            Transaction.date == date,
            Transaction.description == description,
            Transaction.amount == abs(amount)
        ).first()
        
        if existing:
            return None
        
        # Extract merchant name
        merchant = self.extract_merchant(description)
        
        # Create transaction
        transaction = Transaction(
            account_id=account_id,
            date=date,
            description=description,
            amount=abs(amount),
            transaction_type=transaction_type,
            merchant=merchant
        )
        
        # Auto-categorize
        category_id = auto_categorize_transaction(description, merchant, user_id)
        if category_id:
            transaction.category_id = category_id
        
        return transaction
    
    def extract_merchant(self, description: str) -> Optional[str]:
        """Extract merchant name from description"""
        if not description:
            return None
        
        # Remove common prefixes and clean up
        description = re.sub(r'^(POS MERCHANDISE|INTERNET BILL PAYMENT|PAYROLL DEPOSIT|EFT CREDIT|INTERAC E-TRANSFER|ABM WITHDRAWAL)', '', description)
        description = description.strip()
        
        # Take first part before common separators
        separators = [' - ', ' / ', ' #', ' *', '  ', ',']
        for sep in separators:
            if sep in description:
                description = description.split(sep)[0]
                break
        
        return description.strip()[:200] if description.strip() else None


class AmexParser(CSVParser):
    """Parser for American Express CSV files"""
    
    def __init__(self):
        super().__init__("American Express")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        try:
            # Read CSV without headers since Amex format doesn't have them
            df = pd.read_csv(filepath, header=None)
            
            # Amex format: Date, Description, Empty, Amount
            df.columns = ['date', 'description', 'empty', 'amount']
            
            transactions_created = 0
            date_formats = ['%d %b. %Y', '%d %b %Y', '%d %B %Y', '%d %B. %Y']
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    transaction_date = self.parse_date(row['date'], date_formats)
                    if not transaction_date:
                        continue
                    
                    # Clean description
                    description = str(row['description']).strip()
                    if not description or description == 'nan':
                        continue
                    
                    # Parse amount
                    amount = self.clean_amount(row['amount'])
                    if amount == 0:
                        continue
                    
                    # Determine transaction type (Amex shows expenses as positive, payments as negative)
                    transaction_type = 'expense' if amount > 0 else 'income'
                    
                    # Create transaction
                    transaction = self.create_transaction(
                        account_id, user_id, transaction_date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        db.session.add(transaction)
                        transactions_created += 1
                
                except Exception as e:
                    print(f"Error processing Amex row: {e}")
                    continue
            
            db.session.commit()
            return transactions_created
            
        except Exception as e:
            db.session.rollback()
            raise e


class CibcParser(CSVParser):
    """Parser for CIBC CSV files"""
    
    def __init__(self):
        super().__init__("CIBC")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        try:
            df = pd.read_csv(filepath)
            
            transactions_created = 0
            date_formats = ['%Y-%m-%d']
            
            for _, row in df.iterrows():
                try:
                    # Parse date (first column)
                    transaction_date = self.parse_date(str(row.iloc[0]), date_formats)
                    if not transaction_date:
                        continue
                    
                    # Description (second column)
                    description = str(row.iloc[1]).strip()
                    if not description or description == 'nan':
                        continue
                    
                    # CIBC has debit and credit columns (columns 2 and 3)
                    debit = self.clean_amount(str(row.iloc[2]) if len(row) > 2 else '')
                    credit = self.clean_amount(str(row.iloc[3]) if len(row) > 3 else '')
                    
                    # Determine amount and type
                    if debit > 0:
                        amount = debit
                        transaction_type = 'expense'
                    elif credit > 0:
                        amount = credit
                        transaction_type = 'income'
                    else:
                        continue
                    
                    # Create transaction
                    transaction = self.create_transaction(
                        account_id, user_id, transaction_date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        db.session.add(transaction)
                        transactions_created += 1
                
                except Exception as e:
                    print(f"Error processing CIBC row: {e}")
                    continue
            
            db.session.commit()
            return transactions_created
            
        except Exception as e:
            db.session.rollback()
            raise e


class EqBankParser(CSVParser):
    """Parser for EQ Bank CSV files"""
    
    def __init__(self):
        super().__init__("EQ Bank")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        try:
            df = pd.read_csv(filepath, header=None)
            
            # EQ Bank format: Date, Description, Amount, Balance
            df.columns = ['date', 'description', 'amount', 'balance']
            
            transactions_created = 0
            date_formats = ['%d-%b-%y', '%d-%B-%y', '%d-%b-%Y', '%d-%B-%Y']
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    transaction_date = self.parse_date(row['date'], date_formats)
                    if not transaction_date:
                        continue
                    
                    # Description
                    description = str(row['description']).strip()
                    if not description or description == 'nan':
                        continue
                    
                    # Parse amount - EQ Bank uses ($xxx) for debits
                    amount_str = str(row['amount']).strip()
                    amount = self.clean_amount(amount_str)
                    
                    if amount == 0:
                        continue
                    
                    # Determine transaction type
                    transaction_type = 'expense' if amount < 0 else 'income'
                    
                    # Create transaction
                    transaction = self.create_transaction(
                        account_id, user_id, transaction_date, description, abs(amount), transaction_type
                    )
                    
                    if transaction:
                        db.session.add(transaction)
                        transactions_created += 1
                
                except Exception as e:
                    print(f"Error processing EQ Bank row: {e}")
                    continue
            
            db.session.commit()
            return transactions_created
            
        except Exception as e:
            db.session.rollback()
            raise e


class SimpliiParser(CSVParser):
    """Parser for Simplii Financial CSV files"""
    
    def __init__(self):
        super().__init__("Simplii Financial")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        try:
            df = pd.read_csv(filepath)
            
            transactions_created = 0
            date_formats = ['%m/%d/%Y', '%d/%m/%Y']
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    transaction_date = self.parse_date(str(row['Date']).strip(), date_formats)
                    if not transaction_date:
                        continue
                    
                    # Description
                    description = str(row['Transaction Details']).strip()
                    if not description or description == 'nan' or description == 'Transaction Details':
                        continue
                    
                    # Simplii has separate Funds Out and Funds In columns
                    funds_out = self.clean_amount(str(row['Funds Out']) if 'Funds Out' in row else '')
                    funds_in = self.clean_amount(str(row['Funds In']) if 'Funds In' in row else '')
                    
                    # Determine amount and type
                    if funds_out > 0:
                        amount = funds_out
                        transaction_type = 'expense'
                    elif funds_in > 0:
                        amount = funds_in
                        transaction_type = 'income'
                    else:
                        continue
                    
                    # Create transaction
                    transaction = self.create_transaction(
                        account_id, user_id, transaction_date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        db.session.add(transaction)
                        transactions_created += 1
                
                except Exception as e:
                    print(f"Error processing Simplii row: {e}")
                    continue
            
            db.session.commit()
            return transactions_created
            
        except Exception as e:
            db.session.rollback()
            raise e


class TdParser(CSVParser):
    """Parser for TD Bank CSV files"""
    
    def __init__(self):
        super().__init__("TD Bank")
    
    def parse(self, filepath: str, account_id: int, user_id: int) -> int:
        try:
            df = pd.read_csv(filepath)
            
            transactions_created = 0
            date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y']
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    transaction_date = self.parse_date(str(row['date']), date_formats)
                    if not transaction_date:
                        continue
                    
                    # Description
                    description = str(row['description']).strip()
                    if not description or description == 'nan':
                        continue
                    
                    # Parse amount (TD shows as debit)
                    amount = self.clean_amount(str(row['debit']))
                    if amount == 0:
                        continue
                    
                    # TD format typically shows expenses as positive debits
                    transaction_type = 'expense'
                    
                    # Create transaction
                    transaction = self.create_transaction(
                        account_id, user_id, transaction_date, description, amount, transaction_type
                    )
                    
                    if transaction:
                        db.session.add(transaction)
                        transactions_created += 1
                
                except Exception as e:
                    print(f"Error processing TD row: {e}")
                    continue
            
            db.session.commit()
            return transactions_created
            
        except Exception as e:
            db.session.rollback()
            raise e


def get_parser_by_format(format_type: str) -> CSVParser:
    """Factory function to get the appropriate parser"""
    parsers = {
        'amex': AmexParser(),
        'cibc': CibcParser(),
        'eq_bank': EqBankParser(),
        'simplii': SimpliiParser(),
        'td': TdParser(),
        'generic': None  # Will use the original generic parser
    }
    
    return parsers.get(format_type)


def detect_csv_format(filepath: str) -> str:
    """Automatically detect CSV format based on file content"""
    try:
        # Read first few lines to detect format
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()
        
        # Amex format detection (no header, starts with date)
        if not first_line.lower().startswith(('date', 'transaction')) and re.match(r'\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', first_line):
            return 'amex'
        
        # CIBC format detection (has header, specific format)
        if 'cibc' in first_line.lower() or ('mastercard' in first_line.lower() and 'payment thank you' in second_line.lower()):
            return 'cibc'
        
        # EQ Bank format detection
        if re.match(r'\d+-\w+-\d+', first_line) and ('deposit' in first_line.lower() or 'transfer' in first_line.lower()):
            return 'eq_bank'
        
        # Simplii format detection
        if 'transaction details' in first_line.lower() and 'funds out' in first_line.lower():
            return 'simplii'
        
        # TD format detection
        if 'date,description,debit' in first_line.lower():
            return 'td'
        
        return 'generic'
        
    except Exception:
        return 'generic'