import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# Import the new fraud detection components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from fraud_detection import DuplicateDetector, VendorRiskEngine, BehaviorAnalyzer, FraudScoreCalculator

class FraudDetectionAgent:
    def __init__(self, memory_manager, config):
        self.memory = memory_manager
        self.config = config
        
        # ML-based anomaly detection (your existing code)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.detected_frauds = []
        
        # Rule-based fraud detection (new components)
        self.duplicate_detector = DuplicateDetector()
        self.vendor_risk_engine = VendorRiskEngine()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.fraud_calculator = FraudScoreCalculator()
        
    def extract_features(self, expenses: List[Dict]) -> pd.DataFrame:
        """Extract features for anomaly detection - YOUR EXISTING CODE"""
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
            threshold = self.config.EXPENSE.thresholds.get(category, 1000) if hasattr(self.config, 'EXPENSE') else 1000
            amount_ratio = amount / threshold if threshold > 0 else 0
            
            # Employee behavior features
            employee_id = expense.get('employee_id')
            employee_data = self.memory.get_employee_behavior(employee_id) if hasattr(self.memory, 'get_employee_behavior') else {}
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
        categories = getattr(self.config.EXPENSE, 'categories', ['Travel', 'Meals', 'Entertainment', 'Supplies', 'Software', 'Accommodation', 'Shopping', 'Other'])
        return categories.index(category) if category in categories else len(categories)
    
    def detect_anomalies(self, expenses: List[Dict]) -> pd.DataFrame:
        """Detect anomalous expenses using machine learning - YOUR EXISTING CODE"""
        if len(expenses) < 5:
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
                    'risk_level': 'High' if is_anomaly else 'Low',
                    'detection_method': 'ML_Anomaly'
                })
                
                if is_anomaly:
                    fraud_pattern = {
                        'type': 'ml_anomaly',
                        'employee_id': expense.get('employee_id'),
                        'amount': expense.get('amount'),
                        'category': expense.get('category'),
                        'score': anomaly_score,
                        'timestamp': pd.Timestamp.now()
                    }
                    if hasattr(self.memory, 'add_fraud_pattern'):
                        self.memory.add_fraud_pattern(fraud_pattern)
                    self.detected_frauds.append(fraud_pattern)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"ML Anomaly detection error: {e}")
            return pd.DataFrame([{
                'expense_id': exp.get('id'),
                'employee_id': exp.get('employee_id'),
                'amount': exp.get('amount'),
                'is_anomaly': False,
                'anomaly_score': 0,
                'risk_level': 'Low',
                'detection_method': 'ML_Anomaly'
            } for exp in expenses])
    
    def detect_rule_based_fraud(self, expenses: List[Dict]) -> pd.DataFrame:
        """NEW: Detect fraud using rule-based approaches"""
        if not expenses:
            return pd.DataFrame()
            
        results = []
        historical_expenses = getattr(self.memory, 'get_historical_expenses', lambda: [])()
        
        for expense in expenses:
            # Convert to the format expected by rule-based detectors
            expense_dict = {
                'vendor': expense.get('merchant', ''),
                'amount': expense.get('amount', 0),
                'amount_raw': f"₹{expense.get('amount', 0):.2f}",
                'date': expense.get('date', ''),
                'date_raw': expense.get('date', ''),
                'category': expense.get('category', ''),
                'category_raw': expense.get('category', ''),
                'raw_text': expense.get('description', ''),
                'employee_id': expense.get('employee_id', '')
            }
            
            # Run rule-based fraud detection
            duplicate_result = self.duplicate_detector.detect_duplicates(
                expense_dict, historical_expenses
            )
            
            vendor_risk_result = self.vendor_risk_engine.assess_vendor_risk(
                vendor_name=expense_dict.get('vendor', ''),
                amount=expense_dict.get('amount_raw', ''),
                date_str=expense_dict.get('date_raw', ''),
                category=expense_dict.get('category_raw', ''),
                historical_data=historical_expenses
            )
            
            behavior_risk_result = self.behavior_analyzer.analyze_behavior(
                expense_dict, historical_expenses
            )
            
            # Calculate final fraud score
            fraud_result = self.fraud_calculator.calculate_fraud_score(
                duplicate_result=duplicate_result,
                vendor_risk_result=vendor_risk_result,
                behavior_risk_result=behavior_risk_result
            )
            
            # Combine results
            result = {
                'expense_id': expense.get('id'),
                'employee_id': expense.get('employee_id'),
                'amount': expense.get('amount'),
                'category': expense.get('category'),
                'is_anomaly': fraud_result['final_risk_score'] >= 70,  # Needs review or reject
                'anomaly_score': fraud_result['final_risk_score'] / 100.0,
                'risk_level': 'High' if fraud_result['final_risk_score'] >= 70 else 'Low',
                'detection_method': 'Rule_Based',
                'fraud_score': fraud_result['final_risk_score'],
                'fraud_decision': fraud_result['decision'],
                'fraud_reasons': fraud_result['reasons'],
                'is_duplicate': duplicate_result.get('is_duplicate', False),
                'vendor_risk_score': vendor_risk_result.get('vendor_risk_score', 0),
                'behavior_risk_score': behavior_risk_result.get('behavior_risk_score', 0)
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def detect_behavioral_patterns(self, expenses_df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced behavioral pattern detection"""
        if expenses_df.empty:
            return pd.DataFrame()
            
        patterns = []
        
        # Your existing behavioral patterns
        for employee_id, group in expenses_df.groupby('employee_id'):
            employee_data = getattr(self.memory, 'get_employee_behavior', lambda x: {})(employee_id)
            
            # Check for frequent small expenses
            small_expenses = group[group['amount'] < 25]
            if len(small_expenses) > 8:
                patterns.append({
                    'employee_id': employee_id,
                    'pattern_type': 'frequent_small_expenses',
                    'count': len(small_expenses),
                    'total_amount': small_expenses['amount'].sum(),
                    'risk_level': 'Medium',
                    'detection_method': 'Behavioral_Analysis'
                })
            
            # Check for after-hours expenses
            if 'hour' in group.columns:
                after_hours = group[(group['hour'] >= 18) | (group['hour'] <= 6)]
                if len(after_hours) > 5:
                    patterns.append({
                        'employee_id': employee_id,
                        'pattern_type': 'after_hours_expenses',
                        'count': len(after_hours),
                        'total_amount': after_hours['amount'].sum(),
                        'risk_level': 'Medium',
                        'detection_method': 'Behavioral_Analysis'
                    })
        
        return pd.DataFrame(patterns)
    
    def comprehensive_fraud_detection(self, expenses: List[Dict]) -> Dict:
        """NEW: Combine ML and rule-based approaches for comprehensive fraud detection"""
        print("Running comprehensive fraud detection...")
        
        # Run ML-based anomaly detection
        ml_results = self.detect_anomalies(expenses)
        print(f"ML anomalies detected: {ml_results['is_anomaly'].sum()}")
        
        # Run rule-based fraud detection
        rule_results = self.detect_rule_based_fraud(expenses)
        print(f"Rule-based fraud detected: {rule_results[rule_results['is_anomaly']].shape[0]}")
        
        # Run behavioral patterns
        expenses_df = pd.DataFrame(expenses)
        behavioral_patterns = self.detect_behavioral_patterns(expenses_df)
        print(f"Behavioral patterns found: {len(behavioral_patterns)}")
        
        # Combine results
        combined_results = {
            'ml_anomalies': ml_results,
            'rule_based_fraud': rule_results,
            'behavioral_patterns': behavioral_patterns,
            'summary': {
                'total_expenses': len(expenses),
                'ml_anomalies_count': ml_results['is_anomaly'].sum(),
                'rule_based_fraud_count': rule_results[rule_results['is_anomaly']].shape[0],
                'behavioral_patterns_count': len(behavioral_patterns),
                'combined_risk_count': len(set(ml_results[ml_results['is_anomaly']]['expense_id']).union(
                    set(rule_results[rule_results['is_anomaly']]['expense_id'])
                ))
            }
        }
        
        return combined_results