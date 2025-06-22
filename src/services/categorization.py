import re
from src.models.models import Category, CategorizationRule
from app import db


def auto_categorize_transaction(description, merchant, user_id):
    """Automatically categorize a transaction based on description and merchant"""
    
    # First, check existing categorization rules
    rules = CategorizationRule.query.filter_by(
        user_id=user_id, 
        is_active=True
    ).order_by(CategorizationRule.priority.desc()).all()
    
    search_text = f"{description} {merchant or ''}".lower()
    
    for rule in rules:
        if rule.keyword.lower() in search_text:
            return rule.category_id
    
    # Fallback to built-in categorization patterns
    category_patterns = get_default_category_patterns(user_id)
    
    for pattern, category_id in category_patterns:
        if re.search(pattern, search_text, re.IGNORECASE):
            return category_id
    
    return None


def get_default_category_patterns(user_id):
    """Get default categorization patterns mapped to user's categories"""
    patterns = []
    
    # Get user's categories
    categories = Category.query.filter_by(user_id=user_id).all()
    category_map = {cat.name.lower(): cat.id for cat in categories}
    
    # Define patterns for common categories
    pattern_definitions = {
        'food & dining': [
            r'restaurant|cafe|coffee|pizza|burger|mcdonalds|subway|starbucks',
            r'grocery|supermarket|walmart|target|kroger|safeway|whole foods',
            r'dining|food|meal|lunch|dinner|breakfast'
        ],
        'transportation': [
            r'gas|fuel|shell|exxon|chevron|bp|mobil',
            r'uber|lyft|taxi|cab',
            r'parking|toll|metro|bus|train|subway'
        ],
        'shopping': [
            r'amazon|ebay|walmart|target|bestbuy|costco',
            r'clothing|apparel|shoe|fashion',
            r'store|shop|retail|mall'
        ],
        'entertainment': [
            r'movie|cinema|theater|netflix|spotify|hulu',
            r'game|gaming|xbox|playstation|steam',
            r'concert|show|event|ticket'
        ],
        'bills & utilities': [
            r'electric|electricity|power|utility',
            r'water|sewer|trash|garbage',
            r'internet|cable|phone|wireless|verizon|att|comcast',
            r'insurance|premium'
        ],
        'healthcare': [
            r'medical|doctor|hospital|pharmacy|cvs|walgreens',
            r'dental|dentist|vision|eye',
            r'health|clinic|urgent care'
        ],
        'education': [
            r'school|university|college|tuition',
            r'book|textbook|supplies',
            r'course|class|training'
        ],
        'travel': [
            r'hotel|motel|airbnb|booking',
            r'flight|airline|airport',
            r'travel|vacation|trip'
        ],
        'income': [
            r'salary|payroll|wages|deposit|income',
            r'refund|rebate|cashback'
        ],
        'transfer': [
            r'transfer|payment|check|atm withdrawal'
        ]
    }
    
    # Map patterns to category IDs
    for category_name, pattern_list in pattern_definitions.items():
        if category_name in category_map:
            category_id = category_map[category_name]
            for pattern in pattern_list:
                patterns.append((pattern, category_id))
    
    return patterns


def create_categorization_rule(user_id, keyword, category_id, priority=1):
    """Create a new categorization rule"""
    rule = CategorizationRule(
        user_id=user_id,
        keyword=keyword,
        category_id=category_id,
        priority=priority
    )
    
    db.session.add(rule)
    db.session.commit()
    
    return rule


def learn_from_user_categorization(transaction, user_id):
    """Learn from user's manual categorization to improve auto-categorization"""
    if not transaction.category_id or not transaction.merchant:
        return
    
    # Check if we already have a rule for this merchant
    existing_rule = CategorizationRule.query.filter_by(
        user_id=user_id,
        keyword=transaction.merchant.lower(),
        category_id=transaction.category_id
    ).first()
    
    if not existing_rule:
        # Create new rule based on merchant name
        create_categorization_rule(
            user_id=user_id,
            keyword=transaction.merchant.lower(),
            category_id=transaction.category_id,
            priority=5  # Higher priority for learned rules
        )
