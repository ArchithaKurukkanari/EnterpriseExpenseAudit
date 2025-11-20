import re
import json
import pandas as pd
from datetime import datetime

class FieldExtractionAgent:
    def __init__(self):
        print("Field Extraction Agent initialized!")
    
    def extract_vendor(self, raw_text):
        """Extract vendor name from raw text"""
        patterns = [
            r'(Uber|Lyft|Taxi|Cab|OLA|McDonald|KFC|Amazon|Flipkart)',
            r'([A-Z][a-z]+ Restaurant|[A-Z][a-z]+ Cafe)',
            r'(Hotel [A-Z][a-z]+|Motel [A-Z][a-z]+)',
            r'([A-Z]{2,} Store|[A-Z]{2,} Market)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Unknown"
    
    def extract_amount(self, raw_text):
        """Extract amount from raw text"""
        patterns = [
            r'₹\s*(\d+[.,]\d+)',
            r'Rs\.?\s*(\d+[.,]\d+)',
            r'(\d+[.,]\d+)\s*(?:₹|Rs|INR)',
            r'Total[:\s]+₹?\s*(\d+[.,]\d+)',
            r'Amount[:\s]+₹?\s*(\d+[.,]\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_text)
            if match:
                amount_str = match.group(0).strip()
                # Convert to float for processing
                amount_clean = re.sub(r'[₹Rs, ]', '', amount_str)
                return float(amount_clean)
        
        return 0.0
    
    def extract_date(self, raw_text):
        """Extract date from raw text"""
        patterns = [
            r'\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_text)
            if match:
                return match.group(0)
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def extract_category(self, raw_text):
        """Extract category from raw text"""
        categories = {
            'Travel': ['uber', 'lyft', 'taxi', 'cab', 'flight', 'train', 'ola'],
            'Meals': ['restaurant', 'cafe', 'food', 'dinner', 'lunch', 'breakfast', 'mcdonald', 'kfc'],
            'Entertainment': ['movie', 'concert', 'entertainment', 'casino'],
            'Supplies': ['stationery', 'print', 'copy', 'office supplies'],
            'Software': ['software', 'subscription', 'license'],
            'Shopping': ['amazon', 'flipkart', 'store', 'market']
        }
        
        text_lower = raw_text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "Other"
    
    def process_raw_receipts(self, raw_receipts):
        """Convert raw receipts to structured expense data"""
        structured_expenses = []
        
        for receipt in raw_receipts:
            extracted_data = {
                "vendor": self.extract_vendor(receipt),
                "amount_raw": self.extract_amount(receipt),
                "date_raw": self.extract_date(receipt),
                "category_raw": self.extract_category(receipt),
                "raw_text": receipt[:100] + "..." if len(receipt) > 100 else receipt
            }
            
            # Convert to expense format for the main system
            expense = {
                'id': f'EXP{len(structured_expenses):06d}',
                'employee_id': 'E001',  # Default, can be enhanced
                'amount': extracted_data["amount_raw"],
                'category': extracted_data["category_raw"],
                'date': extracted_data["date_raw"],
                'merchant': extracted_data["vendor"],
                'location': 'Unknown',  # Can be enhanced
                'description': extracted_data["raw_text"],
                'hour': datetime.now().hour  # Default hour
            }
            
            structured_expenses.append(expense)
        
        return structured_expenses