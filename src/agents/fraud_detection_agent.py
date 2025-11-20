import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

class FraudDetectionAgent:
    def __init__(self, memory_manager, config):
        self.memory = memory_manager
        self.config = config
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.detected_frauds = []
        
    def extract_features(self, expenses: List[Dict]) -> pd.DataFrame:
        """Extract features for anomaly detection"""
        features = []
        
        for expense in expenses:
            # Basic features
            amount = expense.get('amount', 0)
            description = expense.get('description', '')
            
            # Date features
            expense_date = expense.get('date')
            if isinstance(expense_date, str):
                try:
                    expense_date = pd.to_datetime(expense_date)
                except:
                    expense_date = pd.Timestamp.now()
            
            hour = expense_date.hour if hasattr(expense_date, 'hour') else 12
            weekday = expense_date.weekday() if hasattr(expense_date, 'weekday') else 0
            is_weekend = 1 if weekday >= 5 else 0
            
            # Category encoding
            category_enc = self._get_category_encoding(expense.get('category'))
            
            # Amount ratio to threshold
            category = expense.get('category', 'Other')
            threshold = self.config.EXPENSE.thresholds.get(category, 1000)
            amount_ratio = amount / threshold if threshold > 0 else 0
            
            # Employee behavior features
            employee_id = expense.get('employee_id')
            employee_data = self.memory.get_employee_behavior(employee_id)
            avg_amount = employee_data.get('total_amount', 0) / max(employee_data.get('total_expenses', 1), 1)
            amount_deviation = (amount - avg_amount) / max(avg_amount, 1) if avg_amount > 0 else 0
            
            feature_vector = [
                amount,
                len(description),
                hour,
                weekday,
                is_weekend,
                category_enc,
                amount_ratio,
                amount_deviation
            ]
            features.append(feature_vector)
        
        return pd.DataFrame(features, columns=[
            'amount', 'description_length', 'hour', 'weekday', 
            'is_weekend', 'category_enc', 'amount_ratio', 'amount_deviation'
        ])
    
    def _get_category_encoding(self, category: str) -> int:
        """Encode category as integer"""
        categories = self.config.EXPENSE.categories
        return categories.index(category) if category in categories else len(categories)
    
    def detect_anomalies(self, expenses: List[Dict]) -> pd.DataFrame:
        """Detect anomalous expenses using machine learning"""
        if len(expenses) < 5:
            # Return empty DataFrame with proper structure
            return pd.DataFrame(columns=['expense_id', 'employee_id', 'amount', 'is_anomaly', 'anomaly_score'])
            
        try:
            features_df = self.extract_features(expenses)
            
            if not self.is_fitted:
                features_scaled = self.scaler.fit_transform(features_df)
                anomalies = self.anomaly_detector.fit_predict(features_scaled)
                self.is_fitted = True
            else:
                features_scaled = self.scaler.transform(features_df)
                anomalies = self.anomaly_detector.predict(features_scaled)
            
            results = []
            for i, expense in enumerate(expenses):
                is_anomaly = anomalies[i] == -1
                anomaly_score = self.anomaly_detector.decision_function([features_scaled[i]])[0] if hasattr(self.anomaly_detector, 'decision_function') else -1
                
                results.append({
                    'expense_id': expense.get('id'),
                    'employee_id': expense.get('employee_id'),
                    'amount': expense.get('amount'),
                    'category': expense.get('category'),
                    'is_anomaly': is_anomaly,
                    'anomaly_score': anomaly_score,
                    'risk_level': 'High' if is_anomaly else 'Low'
                })
                
                # Add to fraud patterns if anomalous
                if is_anomaly:
                    fraud_pattern = {
                        'type': 'ml_anomaly',
                        'employee_id': expense.get('employee_id'),
                        'amount': expense.get('amount'),
                        'category': expense.get('category'),
                        'score': anomaly_score,
                        'timestamp': pd.Timestamp.now()
                    }
                    self.memory.add_fraud_pattern(fraud_pattern)
                    self.detected_frauds.append(fraud_pattern)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            # Return default results
            return pd.DataFrame([{
                'expense_id': exp.get('id'),
                'employee_id': exp.get('employee_id'),
                'amount': exp.get('amount'),
                'is_anomaly': False,
                'anomaly_score': 0,
                'risk_level': 'Low'
            } for exp in expenses])
    
    def detect_behavioral_patterns(self, expenses_df: pd.DataFrame) -> pd.DataFrame:
        """Detect behavioral fraud patterns"""
        if expenses_df.empty:
            return pd.DataFrame()
            
        patterns = []
        
        # Group by employee
        for employee_id, group in expenses_df.groupby('employee_id'):
            employee_data = self.memory.get_employee_behavior(employee_id)
            
            # Check for frequent small expenses (potential micro-fraud)
            small_expenses = group[group['amount'] < 25]
            if len(small_expenses) > 8:  # More than 8 small expenses
                patterns.append({
                    'employee_id': employee_id,
                    'pattern_type': 'frequent_small_expenses',
                    'count': len(small_expenses),
                    'total_amount': small_expenses['amount'].sum(),
                    'risk_level': 'Medium'
                })
            
            # Check for after-hours expenses (6 PM - 6 AM)
            if 'hour' in group.columns:
                after_hours = group[(group['hour'] >= 18) | (group['hour'] <= 6)]
                if len(after_hours) > 5:
                    patterns.append({
                        'employee_id': employee_id,
                        'pattern_type': 'after_hours_expenses',
                        'count': len(after_hours),
                        'total_amount': after_hours['amount'].sum(),
                        'risk_level': 'Medium'
                    })
            
            # Check for category concentration
            category_counts = group['category'].value_counts()
            if len(category_counts) > 0:
                most_common_category = category_counts.index[0]
                most_common_count = category_counts.iloc[0]
                total_count = len(group)
                
                if most_common_count / total_count > 0.7:  # 70% in one category
                    patterns.append({
                        'employee_id': employee_id,
                        'pattern_type': 'category_concentration',
                        'category': most_common_category,
                        'concentration_ratio': most_common_count / total_count,
                        'risk_level': 'Low'
                    })
        
        return pd.DataFrame(patterns)