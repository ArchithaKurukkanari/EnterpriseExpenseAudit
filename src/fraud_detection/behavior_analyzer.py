from collections import defaultdict, Counter
from datetime import datetime

class BehaviorAnalyzer:
    def __init__(self):
        self.suspicious_patterns = {
            'same_amount_repeats': 40,
            'multiple_receipts_same_day': 30,
            'weekend_expenses': 15,
            'after_hours_expenses': 20
        }
    
    def analyze_behavior(self, current_expense, historical_expenses):
        """Analyze spending behavior patterns"""
        risk_score = 0
        reasons = []
        
        if not historical_expenses:
            return {
                "behavior_risk_score": 0,
                "reasons": ["No historical data for behavior analysis"]
            }
        
        current_amount = current_expense.get('amount', '') or current_expense.get('amount_raw', '')
        current_date = current_expense.get('date', '') or current_expense.get('date_raw', '')
        
        # Check for same amount repeats
        amount_repeats = self._check_same_amount_repeats(current_amount, historical_expenses)
        if amount_repeats['count'] >= 3:
            risk_score += self.suspicious_patterns['same_amount_repeats']
            reasons.append(amount_repeats['reason'])
        
        # Check multiple receipts on same day
        same_day_count = self._count_same_day_expenses(current_date, historical_expenses)
        if same_day_count >= 3:
            risk_score += self.suspicious_patterns['multiple_receipts_same_day']
            reasons.append(f"{same_day_count} receipts on same day")
        
        # Check weekend expenses
        if self._is_weekend(current_date):
            risk_score += self.suspicious_patterns['weekend_expenses']
            reasons.append("Expense on weekend")
        
        return {
            "behavior_risk_score": min(risk_score, 100),
            "reasons": reasons
        }
    
    def _check_same_amount_repeats(self, current_amount, historical_expenses):
        """Check if same amount appears multiple times"""
        amount_counts = Counter()
        
        # Count all amounts in historical data
        for expense in historical_expenses:
            amount = expense.get('amount', '') or expense.get('amount_raw', '')
            if amount:
                amount_counts[amount] += 1
        
        # Check current amount frequency
        current_count = amount_counts.get(current_amount, 0) + 1
        
        if current_count >= 3:
            return {
                "count": current_count,
                "reason": f"Same amount {current_amount} repeated {current_count} times"
            }
        
        return {"count": current_count, "reason": ""}
    
    def _count_same_day_expenses(self, current_date, historical_expenses):
        """Count expenses on the same day"""
        if not current_date:
            return 0
            
        count = 0
        for expense in historical_expenses:
            exp_date = expense.get('date', '') or expense.get('date_raw', '')
            if exp_date == current_date:
                count += 1
        return count
    
    def _is_weekend(self, date_str):
        """Check if date is weekend"""
        if not date_str:
            return False
            
        try:
            date_obj = datetime.strptime(date_str, '%d %b %Y')
            return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday
        except:
            # Try other formats
            formats = ['%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d']
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.weekday() >= 5
                except:
                    continue
            return False