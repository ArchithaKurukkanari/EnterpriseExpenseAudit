import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, memory_size=1000):
        self.memory_size = memory_size
        self.expense_memory = []
        self.fraud_patterns = []
        self.employee_behavior = {}
        
        # Simple embedding simulation (replace with actual model if needed)
        self.use_embeddings = False
        
    def add_expense(self, expense_data):
        """Add expense to memory"""
        expense_record = {
            'data': expense_data,
            'timestamp': datetime.now(),
            'processed': False
        }
        self.expense_memory.append(expense_record)
        
        # Update employee behavior
        employee_id = expense_data.get('employee_id')
        if employee_id:
            if employee_id not in self.employee_behavior:
                self.employee_behavior[employee_id] = {
                    'total_expenses': 0,
                    'total_amount': 0,
                    'categories': {},
                    'last_expense_date': None
                }
            
            self.employee_behavior[employee_id]['total_expenses'] += 1
            self.employee_behavior[employee_id]['total_amount'] += expense_data.get('amount', 0)
            
            category = expense_data.get('category', 'Other')
            if category not in self.employee_behavior[employee_id]['categories']:
                self.employee_behavior[employee_id]['categories'][category] = 0
            self.employee_behavior[employee_id]['categories'][category] += 1
        
        # Maintain memory size
        if len(self.expense_memory) > self.memory_size:
            self.expense_memory.pop(0)
    
    def find_similar_expenses(self, expense_data, threshold=0.8):
        """Find similar historical expenses using simple matching"""
        if not self.expense_memory:
            return []
            
        similar_expenses = []
        for record in self.expense_memory[-100:]:  # Check recent 100 records
            similarity_score = self._calculate_similarity(expense_data, record['data'])
            if similarity_score > threshold:
                similar_expenses.append((record['data'], similarity_score))
        
        return similar_expenses
    
    def _calculate_similarity(self, expense1, expense2):
        """Calculate similarity between two expenses"""
        score = 0
        matches = 0
        
        # Compare key fields
        if expense1.get('employee_id') == expense2.get('employee_id'):
            score += 0.3
            matches += 1
        
        if expense1.get('category') == expense2.get('category'):
            score += 0.2
            matches += 1
            
        if expense1.get('merchant') == expense2.get('merchant'):
            score += 0.3
            matches += 1
            
        # Amount similarity (within 10%)
        amount1 = expense1.get('amount', 0)
        amount2 = expense2.get('amount', 0)
        if amount1 > 0 and amount2 > 0:
            amount_ratio = min(amount1, amount2) / max(amount1, amount2)
            score += amount_ratio * 0.2
            matches += 1
        
        return score if matches > 0 else 0
    
    def add_fraud_pattern(self, pattern):
        """Add detected fraud pattern to memory"""
        self.fraud_patterns.append({
            'pattern': pattern,
            'timestamp': datetime.now(),
            'count': 1
        })
    
    def get_fraud_patterns(self):
        """Get all known fraud patterns"""
        return self.fraud_patterns
    
    def get_employee_behavior(self, employee_id):
        """Get behavior profile for an employee"""
        return self.employee_behavior.get(employee_id, {})
    
    def save_memory(self, filepath='memory_data.json'):
        """Save memory to file"""
        memory_data = {
            'expense_memory': self.expense_memory,
            'fraud_patterns': self.fraud_patterns,
            'employee_behavior': self.employee_behavior
        }
        
        with open(filepath, 'w') as f:
            json.dump(memory_data, f, default=str, indent=2)
    
    def load_memory(self, filepath='memory_data.json'):
        """Load memory from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                memory_data = json.load(f)
                self.expense_memory = memory_data.get('expense_memory', [])
                self.fraud_patterns = memory_data.get('fraud_patterns', [])
                self.employee_behavior = memory_data.get('employee_behavior', {})