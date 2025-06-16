import os
from datetime import datetime, date
from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func, and_, or_
from app import app, db
from models import User, Account, Category, Transaction, Budget, BudgetItem, CategorizationRule
from csv_processor import process_csv_file
from categorization import auto_categorize_transaction


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create default categories
        create_default_categories(user.id)
        
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary data
    total_balance = db.session.query(func.sum(Account.balance)).filter_by(user_id=current_user.id).scalar() or 0
    total_accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).count()
    
    # Get recent transactions
    recent_transactions = Transaction.query.join(Account).filter(
        Account.user_id == current_user.id
    ).order_by(Transaction.date.desc()).limit(10).all()
    
    # Get spending by category for current month
    current_month = date.today().replace(day=1)
    spending_by_category = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).join(Account).filter(
        Account.user_id == current_user.id,
        Transaction.date >= current_month,
        Transaction.transaction_type == 'expense'
    ).group_by(Category.name).all()
    
    return render_template('dashboard.html', 
                         total_balance=total_balance,
                         total_accounts=total_accounts,
                         recent_transactions=recent_transactions,
                         spending_by_category=spending_by_category)


@app.route('/accounts')
@login_required
def accounts():
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', accounts=user_accounts)


@app.route('/accounts/add', methods=['POST'])
@login_required
def add_account():
    name = request.form['name']
    account_type = request.form['account_type']
    balance = Decimal(request.form.get('balance', '0.00'))
    
    account = Account(
        user_id=current_user.id,
        name=name,
        account_type=account_type,
        balance=balance
    )
    
    db.session.add(account)
    db.session.commit()
    
    flash('Account added successfully', 'success')
    return redirect(url_for('accounts'))


@app.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category')
    account_filter = request.args.get('account')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = Transaction.query.join(Account).filter(Account.user_id == current_user.id)
    
    if category_filter:
        query = query.filter(Transaction.category_id == category_filter)
    
    if account_filter:
        query = query.filter(Transaction.account_id == account_filter)
    
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    transactions_data = query.order_by(Transaction.date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # Get filter options
    categories = Category.query.filter_by(user_id=current_user.id).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    return render_template('transactions.html',
                         transactions=transactions_data,
                         categories=categories,
                         accounts=accounts)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        account_id = request.form.get('account_id')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not account_id:
            flash('Please select an account', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process CSV file
                transactions_count = process_csv_file(filepath, account_id, current_user.id)
                flash(f'Successfully imported {transactions_count} transactions', 'success')
                os.remove(filepath)  # Clean up uploaded file
                return redirect(url_for('transactions'))
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash('Please upload a CSV file', 'error')
    
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('upload.html', accounts=accounts)


@app.route('/budgets')
@login_required
def budgets():
    user_budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template('budgets.html', budgets=user_budgets)


@app.route('/budgets/add', methods=['POST'])
@login_required
def add_budget():
    name = request.form['name']
    period_type = request.form['period_type']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    total_budget = Decimal(request.form['total_budget'])
    
    budget = Budget(
        user_id=current_user.id,
        name=name,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        total_budget=total_budget
    )
    
    db.session.add(budget)
    db.session.commit()
    
    flash('Budget created successfully', 'success')
    return redirect(url_for('budgets'))


@app.route('/categories')
@login_required
def categories():
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=user_categories)


@app.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name = request.form['name']
    parent_id = request.form.get('parent_id') or None
    color = request.form.get('color', '#007bff')
    
    category = Category(
        user_id=current_user.id,
        name=name,
        parent_id=parent_id,
        color=color
    )
    
    db.session.add(category)
    db.session.commit()
    
    flash('Category added successfully', 'success')
    return redirect(url_for('categories'))


@app.route('/api/spending-chart')
@login_required
def spending_chart():
    # Get spending data for chart
    current_month = date.today().replace(day=1)
    spending_data = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total'),
        Category.color
    ).join(Transaction).join(Account).filter(
        Account.user_id == current_user.id,
        Transaction.date >= current_month,
        Transaction.transaction_type == 'expense'
    ).group_by(Category.name, Category.color).all()
    
    chart_data = {
        'labels': [item.name for item in spending_data],
        'data': [float(item.total) for item in spending_data],
        'colors': [item.color for item in spending_data]
    }
    
    return jsonify(chart_data)


def create_default_categories(user_id):
    """Create default categories for new users"""
    default_categories = [
        {'name': 'Food & Dining', 'color': '#28a745'},
        {'name': 'Transportation', 'color': '#17a2b8'},
        {'name': 'Shopping', 'color': '#ffc107'},
        {'name': 'Entertainment', 'color': '#e83e8c'},
        {'name': 'Bills & Utilities', 'color': '#dc3545'},
        {'name': 'Healthcare', 'color': '#6f42c1'},
        {'name': 'Education', 'color': '#fd7e14'},
        {'name': 'Travel', 'color': '#20c997'},
        {'name': 'Income', 'color': '#198754'},
        {'name': 'Transfer', 'color': '#6c757d'},
    ]
    
    for cat_data in default_categories:
        category = Category(
            user_id=user_id,
            name=cat_data['name'],
            color=cat_data['color']
        )
        db.session.add(category)
    
    db.session.commit()
