import hashlib
import re
from difflib import SequenceMatcher
from datetime import datetime

class DuplicateDetector:
    def __init__(self, similarity_threshold=0.85):
        self.similarity_threshold = similarity_threshold
    
    def calculate_text_hash(self, text):
        """Calculate MD5 hash of normalized text"""
        if not text:
            return ""
        normalized_text = re.sub(r'\s+', ' ', text.strip().lower())
        return hashlib.md5(normalized_text.encode()).hexdigest()
    
    def text_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def fuzzy_amount_match(self, amount1, amount2, threshold=0.01):
        """Check if amounts are approximately equal"""
        try:
            amt1 = self._extract_numeric_amount(amount1)
            amt2 = self._extract_numeric_amount(amount2)
            return abs(amt1 - amt2) <= threshold
        except:
            return amount1 == amount2
    
    def detect_duplicates(self, current_expense, historical_expenses):
        """
        Detect duplicate receipts based on multiple criteria
        """
        duplicates = []
        reasons = []
        
        current_vendor = current_expense.get('vendor', '').lower()
        current_amount = current_expense.get('amount', '') or current_expense.get('amount_raw', '')
        current_date = current_expense.get('date', '') or current_expense.get('date_raw', '')
        current_text = current_expense.get('raw_text', '')
        
        # Calculate current text hash
        current_hash = self.calculate_text_hash(current_text)
        
        for expense in historical_expenses:
            hist_vendor = expense.get('vendor', '').lower()
            hist_amount = expense.get('amount', '') or expense.get('amount_raw', '')
            hist_date = expense.get('date', '') or expense.get('date_raw', '')
            hist_text = expense.get('raw_text', '')
            hist_hash = self.calculate_text_hash(hist_text)
            
            # Skip if comparing with itself
            if current_hash == hist_hash and current_hash != "":
                continue
            
            # Check exact text hash match
            if current_hash == hist_hash and current_hash != "":
                duplicates.append(expense)
                reasons.append("Exact duplicate receipt detected")
                continue
            
            # Check text similarity
            similarity = self.text_similarity(current_text, hist_text)
            if similarity > self.similarity_threshold:
                duplicates.append(expense)
                reasons.append(f"High text similarity ({similarity:.2f})")
                continue
            
            # Check vendor + amount + date combination
            if (current_vendor and current_vendor == hist_vendor and 
                self.fuzzy_amount_match(current_amount, hist_amount) and
                self._dates_within_range(current_date, hist_date, 1)):
                duplicates.append(expense)
                reasons.append("Same vendor, amount, and date combination")
        
        return {
            "is_duplicate": len(duplicates) > 0,
            "duplicate_count": len(duplicates),
            "matching_expenses": duplicates[:3],  # Limit to top 3
            "reasons": list(set(reasons))
        }
    
    def _extract_numeric_amount(self, amount_str):
        """Extract numeric value from amount string"""
        if not amount_str:
            return 0.0
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            formats = ['%d %b %Y', '%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %B %Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            return None
        except:
            return None
    
    def _dates_within_range(self, date1_str, date2_str, days=1):
        """Check if two dates are within specified days range"""
        date1 = self._parse_date(date1_str)
        date2 = self._parse_date(date2_str)
        
        if not date1 or not date2:
            return False
        
        return abs((date1 - date2).days) <= days