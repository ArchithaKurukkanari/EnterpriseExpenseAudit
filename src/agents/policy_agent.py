import pandas as pd
from typing import Dict, List, Tuple
import json
from datetime import datetime

class PolicyAgent:
    def __init__(self, memory_manager, config):
        self.memory = memory_manager
        self.config = config
        self.policy_violations = []
        
    def validate_expense(self, expense: Dict) -> Tuple[bool, List[str]]:
        """Validate expense against company policies"""
        violations = []
        
        # Amount threshold checks
        category = expense.get('category', 'Other')
        amount = expense.get('amount', 0)
        
        if category in self.config.EXPENSE.thresholds:
            if amount > self.config.EXPENSE.thresholds[category]:
                violations.append(f"Amount ${amount} exceeds ${self.config.EXPENSE.thresholds[category]} limit for {category}")
        
        # Merchant checks
        merchant = expense.get('merchant', '').lower()
        for risky_merchant in self.config.EXPENSE.high_risk_merchants:
            if risky_merchant.lower() in merchant:
                violations.append(f"Merchant '{merchant}' is high-risk")
        
        # Location checks
        location = expense.get('location', '').lower()
        for risky_location in self.config.EXPENSE.risky_locations:
            if risky_location.lower() in location:
                violations.append(f"Location '{location}' is flagged as high-risk")
        
        # Date validation
        expense_date = expense.get('date')
        if isinstance(expense_date, str):
            try:
                expense_date = pd.to_datetime(expense_date)
            except:
                expense_date = datetime.now()
        
        if expense_date and expense_date > datetime.now():
            violations.append("Future-dated expense")
        
        # Weekend expenses check
        if expense_date and expense_date.weekday() >= 5:  # Saturday=5, Sunday=6
            violations.append("Weekend expense - requires additional justification")
        
        # Duplicate expense check
        similar_expenses = self.memory.find_similar_expenses(expense, threshold=0.9)
        if len(similar_expenses) > 2:  # More than 2 very similar expenses
            violations.append("Potential duplicate expense pattern detected")
        
        # Missing information checks
        if not expense.get('description') or len(expense.get('description', '').strip()) < 5:
            violations.append("Insufficient description")
            
        if not expense.get('merchant'):
            violations.append("Missing merchant information")
        
        is_valid = len(violations) == 0
        if not is_valid:
            self.policy_violations.append({
                'expense_id': expense.get('id'),
                'violations': violations,
                'timestamp': datetime.now()
            })
            
        return is_valid, violations
    
    def batch_validate(self, expenses: List[Dict]) -> pd.DataFrame:
        """Validate multiple expenses"""
        results = []
        for expense in expenses:
            # Add to memory first
            self.memory.add_expense(expense)
            
            # Then validate
            is_valid, violations = self.validate_expense(expense)
            results.append({
                'expense_id': expense.get('id'),
                'employee_id': expense.get('employee_id'),
                'amount': expense.get('amount'),
                'category': expense.get('category'),
                'merchant': expense.get('merchant'),
                'date': expense.get('date'),
                'is_valid': is_valid,
                'violations': violations,
                'violation_count': len(violations),
                'requires_review': len(violations) > 0
            })
        
        return pd.DataFrame(results)
    
    def get_violation_summary(self):
        """Get summary of policy violations"""
        summary = {}
        for violation in self.policy_violations:
            for v in violation['violations']:
                if v not in summary:
                    summary[v] = 0
                summary[v] += 1
        return summary