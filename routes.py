import os
from datetime import datetime, date
from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func, and_, or_
from app import app, db
from models import User, Account, Category, Transaction, Budget, BudgetItem, CategorizationRule
from csv_processor import process_csv_file
from csv_parsers import get_parser_by_format, detect_csv_format
from categorization import auto_categorize_transaction
from ai_categorizer import auto_categorize_uncategorized_transactions, get_categorization_suggestions


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
    balance_str = request.form.get('balance', '0.00').strip()
    
    # Handle empty or invalid balance
    if not balance_str or balance_str == '':
        balance = Decimal('0.00')
    else:
        try:
            balance = Decimal(balance_str)
        except:
            flash('Invalid balance amount', 'error')
            return redirect(url_for('accounts'))
    
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
        create_new_account = request.form.get('create_new_account')
        csv_format = request.form.get('csv_format', 'auto')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Handle new account creation
        if create_new_account == 'true':
            new_account_name = request.form.get('new_account_name', '').strip()
            new_account_type = request.form.get('new_account_type', '').strip()
            
            if not new_account_name or not new_account_type:
                flash('Please provide account name and type for new account', 'error')
                return redirect(request.url)
            
            # Create new account
            new_account = Account(
                user_id=current_user.id,
                name=new_account_name,
                account_type=new_account_type,
                balance=Decimal('0.00')
            )
            db.session.add(new_account)
            db.session.commit()
            account_id = new_account.id
            flash(f'Created new account: {new_account_name}', 'success')
        
        if not account_id:
            flash('Please select an account or create a new one', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Determine CSV format
                if csv_format == 'auto':
                    detected_format = detect_csv_format(filepath)
                    csv_format = detected_format
                
                # Use appropriate parser
                if csv_format == 'generic':
                    transactions_count = process_csv_file(filepath, int(account_id), current_user.id)
                else:
                    parser = get_parser_by_format(csv_format)
                    if parser:
                        transactions_count = parser.parse(filepath, int(account_id), current_user.id)
                    else:
                        transactions_count = process_csv_file(filepath, int(account_id), current_user.id)
                
                flash(f'Successfully imported {transactions_count} transactions using {csv_format.replace("_", " ").title()} format', 'success')
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
    # Get time period parameter
    period = request.args.get('period', 'month')
    
    # Calculate date range based on period
    from datetime import datetime, timedelta
    
    today = date.today()
    
    if period == 'week':
        # Current week (Monday to Sunday)
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)
    elif period == 'month':
        # Current month
        start_date = today.replace(day=1)
    elif period == 'year':
        # Current year
        start_date = today.replace(month=1, day=1)
    elif period == 'last_30':
        # Last 30 days
        start_date = today - timedelta(days=30)
    elif period == 'last_90':
        # Last 90 days
        start_date = today - timedelta(days=90)
    else:
        # Default to current month
        start_date = today.replace(day=1)
    
    # Build query with date filter
    query = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total'),
        Category.color
    ).join(Transaction).join(Account).filter(
        Account.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.transaction_type == 'expense'
    ).group_by(Category.name, Category.color)
    
    # Handle uncategorized transactions
    uncategorized_query = db.session.query(
        func.sum(Transaction.amount).label('total')
    ).join(Account).filter(
        Account.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.transaction_type == 'expense',
        Transaction.category_id.is_(None)
    ).scalar()
    
    spending_data = query.all()
    
    # Prepare chart data
    labels = [item.name for item in spending_data]
    data = [float(item.total) for item in spending_data]
    colors = [item.color for item in spending_data]
    
    # Add uncategorized transactions if any
    if uncategorized_query and float(uncategorized_query) > 0:
        labels.append('Uncategorized')
        data.append(float(uncategorized_query))
        colors.append('#6c757d')  # Gray color for uncategorized
    
    chart_data = {
        'labels': labels,
        'data': data,
        'colors': colors
    }
    
    return jsonify(chart_data)


@app.route('/categorize')
@login_required
def categorize():
    # Get filter parameters
    category_filter = request.args.get('category', 'uncategorized')
    account_filter = request.args.get('account')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = Transaction.query.join(Account).filter(Account.user_id == current_user.id)
    
    # Apply category filter
    if category_filter == 'uncategorized':
        query = query.filter(Transaction.category_id.is_(None))
    elif category_filter != 'all' and category_filter:
        query = query.filter(Transaction.category_id == category_filter)
    
    # Apply account filter
    if account_filter:
        query = query.filter(Transaction.account_id == account_filter)
    
    # Apply date filters
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Get categories and accounts for dropdowns
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
    
    return render_template('categorize.html', 
                         transactions=transactions,
                         categories=categories,
                         accounts=accounts)


@app.route('/api/bulk-categorize', methods=['POST'])
@login_required
def bulk_categorize():
    try:
        data = request.get_json()
        transaction_ids = data.get('transaction_ids', [])
        category_id = data.get('category_id')
        
        if not transaction_ids:
            return jsonify({'success': False, 'message': 'No transactions selected'})
        
        # Verify transactions belong to user
        transactions = Transaction.query.join(Account).filter(
            Account.user_id == current_user.id,
            Transaction.id.in_(transaction_ids)
        ).all()
        
        if len(transactions) != len(transaction_ids):
            return jsonify({'success': False, 'message': 'Invalid transactions selected'})
        
        # Update categories
        count = 0
        for transaction in transactions:
            transaction.category_id = category_id if category_id else None
            count += 1
        
        db.session.commit()
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/update-category', methods=['POST'])
@login_required
def update_category():
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        category_id = data.get('category_id')
        
        # Verify transaction belongs to user
        transaction = Transaction.query.join(Account).filter(
            Account.user_id == current_user.id,
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            return jsonify({'success': False, 'message': 'Transaction not found'})
        
        # Update category
        transaction.category_id = category_id if category_id else None
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/create-category', methods=['POST'])
@login_required
def create_category_api():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        parent_id = data.get('parent_id')
        color = data.get('color', '#007bff')
        
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'})
        
        # Check if category already exists
        existing = Category.query.filter_by(user_id=current_user.id, name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Category already exists'})
        
        # Create category
        category = Category(
            user_id=current_user.id,
            name=name,
            parent_id=parent_id if parent_id else None,
            color=color
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'color': category.color
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai-categorize-all', methods=['POST'])
@login_required
def ai_categorize_all():
    """Auto-categorize all uncategorized transactions using AI"""
    try:
        stats = auto_categorize_uncategorized_transactions(current_user.id)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f"AI categorized {stats['categorized']} out of {stats['total']} transactions"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai-suggest-categories', methods=['POST'])
@login_required
def ai_suggest_categories():
    """Get AI category suggestions for selected transactions"""
    try:
        data = request.get_json()
        transaction_ids = data.get('transaction_ids', [])
        
        if not transaction_ids:
            return jsonify({'success': False, 'message': 'No transactions selected'})
        
        suggestions = get_categorization_suggestions(transaction_ids, current_user.id)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/visualizations')
@login_required
def visualizations():
    """Expense visualization dashboard"""
    accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
    return render_template('visualizations.html', accounts=accounts)


@app.route('/api/visualization-data')
@login_required
def visualization_data():
    """Get data for expense visualizations"""
    try:
        period = request.args.get('period', 'last_365')
        account_id = request.args.get('account', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build base query
        query = Transaction.query.join(Account).filter(
            Account.user_id == current_user.id,
            Transaction.transaction_type == 'expense'
        )
        
        # Apply date filters
        from datetime import datetime, timedelta
        
        if period == 'custom' and start_date and end_date:
            query = query.filter(
                Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
                Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
            )
        elif period != 'all':
            days_map = {
                'last_30': 30,
                'last_90': 90,
                'last_180': 180,
                'last_365': 365
            }
            if period in days_map:
                cutoff_date = datetime.now().date() - timedelta(days=days_map[period])
                query = query.filter(Transaction.date >= cutoff_date)
        
        # Apply account filter
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        transactions = query.all()
        
        # Process data for different chart types
        data = {
            'categories': get_category_breakdown(transactions),
            'trend': get_spending_trend(transactions),
            'monthly': get_monthly_comparison(transactions),
            'accounts': get_account_distribution(transactions),
            'summary': get_summary_stats(transactions)
        }
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def get_category_breakdown(transactions):
    """Get spending breakdown by category"""
    category_totals = {}
    
    for transaction in transactions:
        category_name = transaction.category.name if transaction.category else 'Uncategorized'
        category_totals[category_name] = category_totals.get(category_name, 0) + float(transaction.amount)
    
    # Sort by amount
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'labels': [item[0] for item in sorted_categories],
        'values': [item[1] for item in sorted_categories]
    }


def get_spending_trend(transactions):
    """Get daily spending trend"""
    from collections import defaultdict
    
    daily_totals = defaultdict(float)
    
    for transaction in transactions:
        date_str = transaction.date.strftime('%Y-%m-%d')
        daily_totals[date_str] += float(transaction.amount)
    
    # Sort by date
    sorted_days = sorted(daily_totals.items())
    
    return {
        'labels': [item[0] for item in sorted_days],
        'values': [item[1] for item in sorted_days]
    }


def get_monthly_comparison(transactions):
    """Get monthly spending comparison"""
    from collections import defaultdict
    
    monthly_totals = defaultdict(float)
    
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        monthly_totals[month_key] += float(transaction.amount)
    
    # Sort by month
    sorted_months = sorted(monthly_totals.items())
    
    # Convert to readable month names
    labels = []
    for month_key, _ in sorted_months:
        month_date = datetime.strptime(month_key, '%Y-%m')
        labels.append(month_date.strftime('%b %Y'))
    
    return {
        'labels': labels,
        'values': [item[1] for item in sorted_months]
    }


def get_account_distribution(transactions):
    """Get spending distribution by account"""
    account_totals = {}
    
    for transaction in transactions:
        account_name = transaction.account.name
        account_totals[account_name] = account_totals.get(account_name, 0) + float(transaction.amount)
    
    # Sort by amount
    sorted_accounts = sorted(account_totals.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'labels': [item[0] for item in sorted_accounts],
        'values': [item[1] for item in sorted_accounts]
    }


def get_summary_stats(transactions):
    """Get summary statistics"""
    if not transactions:
        return {
            'total': 0,
            'avgMonthly': 0,
            'topCategory': None,
            'topCategoryAmount': 0,
            'categoriesCount': 0
        }
    
    total = sum(float(t.amount) for t in transactions)
    
    # Calculate average monthly (assume 30-day months)
    date_range = (max(t.date for t in transactions) - min(t.date for t in transactions)).days
    months = max(1, date_range / 30)
    avg_monthly = total / months
    
    # Top category
    category_breakdown = get_category_breakdown(transactions)
    top_category = category_breakdown['labels'][0] if category_breakdown['labels'] else None
    top_category_amount = category_breakdown['values'][0] if category_breakdown['values'] else 0
    
    # Categories count
    categories_used = set(t.category.name if t.category else 'Uncategorized' for t in transactions)
    
    return {
        'total': total,
        'avgMonthly': avg_monthly,
        'topCategory': top_category,
        'topCategoryAmount': top_category_amount,
        'categoriesCount': len(categories_used)
    }


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
