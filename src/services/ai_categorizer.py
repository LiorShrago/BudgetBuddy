import os
import json
import requests
from typing import List, Dict, Optional
from src.models.models import Transaction, Category, db
from sqlalchemy import func


class AITransactionCategorizer:
    """AI-powered transaction categorization using Perplexity API"""
    
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        self.api_url = 'https://api.perplexity.ai/chat/completions'
        
    def categorize_transactions(self, transactions: List[Transaction], user_categories: List[Category]) -> Dict[int, Optional[int]]:
        """
        Categorize multiple transactions using AI
        Returns dict mapping transaction_id to category_id
        """
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
        if not transactions:
            return {}
        
        # Prepare category list for the AI
        category_list = [{"id": cat.id, "name": cat.name} for cat in user_categories]
        
        # Batch transactions into groups for efficient API calls
        batch_size = 20
        results = {}
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            batch_results = self._categorize_batch(batch, category_list)
            results.update(batch_results)
        
        return results
    
    def _categorize_batch(self, transactions: List[Transaction], categories: List[Dict]) -> Dict[int, Optional[int]]:
        """Categorize a batch of transactions"""
        
        # Prepare transaction data for AI
        transaction_data = []
        for t in transactions:
            transaction_data.append({
                "id": t.id,
                "description": t.description,
                "merchant": t.merchant or "",
                "amount": float(t.amount),
                "type": t.transaction_type
            })
        
        # Create the prompt for AI categorization
        prompt = self._create_categorization_prompt(transaction_data, categories)
        
        try:
            response = self._call_perplexity_api(prompt)
            return self._parse_categorization_response(response, transaction_data)
        except Exception as e:
            print(f"Error in AI categorization: {e}")
            return {}
    
    def _create_categorization_prompt(self, transactions: List[Dict], categories: List[Dict]) -> str:
        """Create the prompt for AI categorization"""
        
        categories_text = "\n".join([f"- {cat['name']} (ID: {cat['id']})" for cat in categories])
        
        transactions_text = ""
        for t in transactions:
            transactions_text += f"ID {t['id']}: {t['description']}"
            if t['merchant']:
                transactions_text += f" | Merchant: {t['merchant']}"
            transactions_text += f" | Amount: ${t['amount']:.2f} | Type: {t['type']}\n"
        
        prompt = f"""You are a financial transaction categorization expert. Please categorize each transaction into the most appropriate category from the provided list.

Available Categories:
{categories_text}

Transactions to categorize:
{transactions_text}

Instructions:
1. Analyze each transaction's description, merchant, and amount
2. Match it to the most appropriate category from the list
3. If no category fits well, return null for that transaction
4. Consider common spending patterns:
   - Grocery stores, supermarkets, convenience stores → Groceries
   - Restaurants, Bars, Fast Food, Food Delivery → Food & Dining
   - Gas stations, car maintenance, car insurance, car payments, parking, Transit → Car/Transportation
   - Amazon, retail stores, malls, winners, any clothing store any tech store like best buy → Shopping
   - Utilities, phone bills, internet bills, cable bills, tel max, gas, hydro, water → Bills & Utilities
   - Movies, games, subscriptions, streaming services → Entertainment
   - Bank transfers received, e-transfers received,salary from AMD,  deposits → Cashflow Income
   - Bank transfers sent, e-transfers sent,salary from AMD,credit card payments, rent, mortgage, insurance, taxes, loans, debt payments → Cashflow Out
   - rent, house purchases - Home
Respond with ONLY a valid JSON object in this exact format:
{{"transaction_id": category_id_or_null, "transaction_id": category_id_or_null}}

Example: {{"123": 1, "124": 3, "125": null}}"""

        return prompt
    
    def _call_perplexity_api(self, prompt: str) -> Dict:
        """Call the Perplexity API"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'llama-3.1-sonar-small-128k-online',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a precise financial categorization assistant. Always respond with valid JSON only.'
                },
                {
                    'role': 'user', 
                    'content': prompt
                }
            ],
            'max_tokens': 1000,
            'temperature': 0.1,
            'stream': False
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def _parse_categorization_response(self, response: Dict, transactions: List[Dict]) -> Dict[int, Optional[int]]:
        """Parse the AI response and return categorization mapping"""
        
        try:
            content = response['choices'][0]['message']['content'].strip()
            
            # Extract JSON from the response (remove any extra text)
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                print(f"No JSON found in response: {content}")
                return {}
            
            json_str = content[start_idx:end_idx]
            categorization_map = json.loads(json_str)
            
            # Convert string keys to integers and validate
            result = {}
            for transaction in transactions:
                t_id = transaction['id']
                t_id_str = str(t_id)
                
                if t_id_str in categorization_map:
                    category_id = categorization_map[t_id_str]
                    result[t_id] = category_id if category_id is not None else None
                else:
                    result[t_id] = None
            
            return result
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response content: {response}")
            return {}


def auto_categorize_uncategorized_transactions(user_id: int) -> Dict[str, int]:
    """
    Auto-categorize all uncategorized transactions for a user
    Returns statistics about the categorization
    """
    
    # Get uncategorized transactions
    from src.models.models import Account
    uncategorized = Transaction.query.join(Account).filter(
        Transaction.category_id.is_(None),
        Account.user_id == user_id
    ).all()
    
    if not uncategorized:
        return {"total": 0, "categorized": 0, "failed": 0}
    
    # Get user categories
    categories = Category.query.filter_by(user_id=user_id).all()
    
    if not categories:
        return {"total": len(uncategorized), "categorized": 0, "failed": len(uncategorized)}
    
    # Initialize AI categorizer
    categorizer = AITransactionCategorizer()
    
    try:
        # Get AI categorization suggestions
        categorization_map = categorizer.categorize_transactions(uncategorized, categories)
        
        # Apply categorizations
        categorized_count = 0
        for transaction_id, category_id in categorization_map.items():
            if category_id is not None:
                transaction = Transaction.query.get(transaction_id)
                if transaction:
                    transaction.category_id = category_id
                    categorized_count += 1
        
        db.session.commit()
        
        return {
            "total": len(uncategorized),
            "categorized": categorized_count,
            "failed": len(uncategorized) - categorized_count
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in auto-categorization: {e}")
        return {"total": len(uncategorized), "categorized": 0, "failed": len(uncategorized)}


def get_categorization_suggestions(transaction_ids: List[int], user_id: int) -> Dict[int, Dict]:
    """
    Get AI categorization suggestions for specific transactions
    Returns dict mapping transaction_id to suggested category info
    """
    
    # Get transactions
    from src.models.models import Account
    transactions = Transaction.query.join(Account).filter(
        Transaction.id.in_(transaction_ids),
        Account.user_id == user_id
    ).all()
    
    if not transactions:
        return {}
    
    # Get user categories
    categories = Category.query.filter_by(user_id=user_id).all()
    
    if not categories:
        return {}
    
    # Initialize AI categorizer
    categorizer = AITransactionCategorizer()
    
    try:
        # Get AI suggestions
        categorization_map = categorizer.categorize_transactions(transactions, categories)
        
        # Build result with category details
        result = {}
        category_lookup = {cat.id: cat for cat in categories}
        
        for transaction_id, category_id in categorization_map.items():
            if category_id is not None and category_id in category_lookup:
                category = category_lookup[category_id]
                result[transaction_id] = {
                    "category_id": category.id,
                    "category_name": category.name,
                    "confidence": "high"  # Could be enhanced with confidence scoring
                }
            else:
                result[transaction_id] = {
                    "category_id": None,
                    "category_name": "No suggestion",
                    "confidence": "low"
                }
        
        return result
        
    except Exception as e:
        print(f"Error getting AI suggestions: {e}")
        return {}