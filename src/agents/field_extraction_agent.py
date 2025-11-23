import re
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict

class FieldExtractionAgent:
    def __init__(self):
        print("Field Extraction Agent initialized!")
    
    def extract_vendor(self, raw_text):
        """Extract vendor name from raw text"""
        patterns = [
            r'(Uber|Lyft|Taxi|Cab|OLA|McDonald|KFC|Amazon|Flipkart|Starbucks|Zomato|Swiggy|RECHARGE|GIFT)',
            r'([A-Z][a-z]+ Restaurant|[A-Z][a-z]+ Cafe|Burger King|Pizza Hut)',
            r'(Hotel [A-Z][a-z]+|Motel [A-Z][a-z]+|Marriott|Hilton|Hyatt)',
            r'([A-Z]{2,} Store|[A-Z]{2,} Market|Walmart|Target)',
            r'([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)'  # Three-word company names
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Fallback: extract first capitalized word sequence
        fallback = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', raw_text)
        return fallback.group(0) if fallback else "Unknown Vendor"
    
    def extract_amount(self, raw_text):
        """Extract amount from raw text"""
        patterns = [
            r'₹\s*(\d+[.,]\d+)',
            r'Rs\.?\s*(\d+[.,]\d+)',
            r'(\d+[.,]\d+)\s*(?:₹|Rs|INR|USD|\$)',
            r'Total[:\s]+[₹$\s]*(\d+[.,]\d+)',
            r'Amount[:\s]+[₹$\s]*(\d+[.,]\d+)',
            r'[\$₹]\s*(\d+[.,]\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_text)
            if match:
                amount_str = match.group(0).strip()
                # Convert to float for processing - IMPROVED CLEANING
                amount_clean = re.sub(r'[₹Rs$, ]', '', amount_str)
                # Handle cases where we might have multiple dots
                if amount_clean.count('.') > 1:
                    # Keep only the last dot as decimal
                    parts = amount_clean.split('.')
                    amount_clean = ''.join(parts[:-1]) + '.' + parts[-1]
                
                try:
                    return float(amount_clean)
                except ValueError:
                    continue
        
        return 0.0
    
    def extract_date(self, raw_text):
        """Extract date from raw text"""
        patterns = [
            r'\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}-\d{1,2}-\d{4}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_text)
            if match:
                return match.group(0)
        
        return datetime.now().strftime("%d %b %Y")
    
    def extract_category(self, raw_text):
        """Extract category from raw text"""
        categories = {
            'Travel': ['uber', 'lyft', 'taxi', 'cab', 'flight', 'train', 'ola', 'airline', 'transport'],
            'Meals': ['restaurant', 'cafe', 'food', 'dinner', 'lunch', 'breakfast', 'mcdonald', 'kfc', 'starbucks', 'pizza', 'burger', 'zomato', 'swiggy'],
            'Entertainment': ['movie', 'concert', 'entertainment', 'casino', 'theater', 'game'],
            'Supplies': ['stationery', 'print', 'copy', 'office supplies', 'store', 'market'],
            'Software': ['software', 'subscription', 'license', 'app', 'digital'],
            'Accommodation': ['hotel', 'motel', 'lodging', 'marriott', 'hilton', 'hyatt', 'inn'],
            'Shopping': ['amazon', 'flipkart', 'walmart', 'target', 'retail'],
            'Personal': ['recharge', 'gift', 'personal', 'mobile', 'prepaid']
        }
        
        text_lower = raw_text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "Other"
    
    def extract_employee_id(self, raw_text):
        """Simple employee ID extraction - can be enhanced with company directory"""
        # Look for employee patterns in text
        emp_pattern = r'[Ee](?:mployee)?[\s:]*([A-Z0-9]{3,6})'
        match = re.search(emp_pattern, raw_text)
        if match:
            return match.group(1)
        
        # Default employee IDs for demo
        employees = [f'E{str(i).zfill(3)}' for i in range(1, 21)]
        return np.random.choice(employees)
    
    def process_raw_receipts(self, raw_receipts):
        """Convert raw receipts to structured expense data"""
        structured_expenses = []
        
        for i, receipt in enumerate(raw_receipts):
            # Extract all fields
            vendor = self.extract_vendor(receipt)
            amount = self.extract_amount(receipt)
            date_str = self.extract_date(receipt)
            category = self.extract_category(receipt)
            employee_id = self.extract_employee_id(receipt)
            
            extracted_data = {
                "vendor": vendor,
                "amount_raw": amount,
                "date_raw": date_str,
                "category_raw": category,
                "raw_text": receipt[:100] + "..." if len(receipt) > 100 else receipt
            }
            
            # Convert to expense format for the main system
            expense = {
                'id': f'EXP{len(structured_expenses):06d}',
                'employee_id': employee_id,
                'amount': amount,
                'category': category,
                'date': date_str,
                'merchant': vendor,
                'location': self._extract_location(receipt),
                'description': f'Expense at {vendor} for {category}',
                'hour': np.random.randint(6, 23)  # Random hour for demo
            }
            
            structured_expenses.append(expense)
            
            # Print extraction results for verification
            print(f"  Receipt {i+1}: {vendor} - ₹{amount:.2f} - {category}")
        
        return structured_expenses
    
    def _extract_location(self, raw_text):
        """Extract location from text"""
        locations = ['New York', 'London', 'Tokyo', 'Mumbai', 'Bangalore', 'Delhi', 'Remote', 'Office']
        text_lower = raw_text.lower()
        
        for location in locations:
            if location.lower() in text_lower:
                return location
        
        return np.random.choice(locations)