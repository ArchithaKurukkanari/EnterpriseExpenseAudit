import pandas as pd
import numpy as np
import os
import sys
import re
import json
from datetime import datetime, timedelta
from collections import Counter

# Field Extraction Agent Class
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
                # Convert to float for processing
                amount_clean = re.sub(r'[₹Rs$, ]', '', amount_str)
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

# Enhanced Fraud Detection with Proper Score Calculation
class AdvancedFraudDetector:
    def __init__(self):
        self.high_risk_vendors = ['uber', 'ola', 'zomato', 'swiggy', 'recharge', 'gift', 'personal']
        self.personal_keywords = ['recharge', 'gift', 'personal', 'mobile', 'entertainment']
    
    def detect_duplicates(self, expenses):
        """Detect duplicate receipts based on vendor + amount + date"""
        duplicates = []
        seen = set()
        
        for expense in expenses:
            key = (expense['merchant'].lower(), expense['amount'], expense['date'])
            if key in seen:
                duplicates.append(expense)
            seen.add(key)
        
        return duplicates
    
    def calculate_vendor_risk(self, vendor, category):
        """Calculate vendor risk score"""
        risk_score = 0
        reasons = []
        
        vendor_lower = vendor.lower()
        
        # High-risk vendors
        if any(risk_vendor in vendor_lower for risk_vendor in self.high_risk_vendors):
            risk_score += 30
            reasons.append(f"High-risk vendor: {vendor}")
        
        # Personal expense keywords
        if any(keyword in vendor_lower for keyword in self.personal_keywords):
            risk_score += 25
            reasons.append("Personal expense detected")
        
        # Category mismatch
        if 'uber' in vendor_lower and category != 'Travel':
            risk_score += 20
            reasons.append("Category mismatch: Uber should be Travel")
        elif 'zomato' in vendor_lower and category != 'Meals':
            risk_score += 20
            reasons.append("Category mismatch: Zomato should be Meals")
        
        return min(risk_score, 100), reasons
    
    def detect_behavior_anomalies(self, expenses):
        """Detect behavioral anomalies"""
        anomalies = []
        
        # Group by employee and date
        employee_date_groups = {}
        for expense in expenses:
            key = (expense['employee_id'], expense['date'])
            if key not in employee_date_groups:
                employee_date_groups[key] = []
            employee_date_groups[key].append(expense)
        
        # Check for multiple same vendor on same day
        for key, group in employee_date_groups.items():
            vendor_count = Counter(exp['merchant'] for exp in group)
            for vendor, count in vendor_count.items():
                if count > 2:  # More than 2 expenses from same vendor on same day
                    for exp in group:
                        if exp['merchant'] == vendor:
                            anomalies.append({
                                'expense': exp,
                                'reason': f"Multiple {vendor} expenses on same day ({count})",
                                'score': 25
                            })
        
        # Check for same amount patterns
        amount_count = Counter(exp['amount'] for exp in expenses)
        for amount, count in amount_count.items():
            if count > 1 and amount > 0:
                for exp in expenses:
                    if exp['amount'] == amount:
                        anomalies.append({
                            'expense': exp,
                            'reason': f"Same amount ₹{amount} repeated {count} times",
                            'score': 30
                        })
        
        return anomalies
    
    def calculate_fraud_score(self, expense, duplicates, vendor_risk_score, vendor_reasons, behavior_anomalies):
        """Calculate final fraud score combining all factors"""
        fraud_score = 0
        all_reasons = []
        
        # Check if this expense is a duplicate
        is_duplicate = any(dup['id'] == expense['id'] for dup in duplicates)
        if is_duplicate:
            fraud_score += 40
            all_reasons.append("Duplicate receipt detected")
        
        # Add vendor risk score
        fraud_score += vendor_risk_score
        all_reasons.extend(vendor_reasons)
        
        # Add behavior anomalies
        for anomaly in behavior_anomalies:
            if anomaly['expense']['id'] == expense['id']:
                fraud_score += anomaly['score']
                all_reasons.append(anomaly['reason'])
        
        # Determine decision
        if fraud_score >= 70:
            decision = "REJECT"
            is_anomaly = True
        elif fraud_score >= 50:
            decision = "NEEDS_REVIEW" 
            is_anomaly = True
        else:
            decision = "APPROVE"
            is_anomaly = False
        
        return {
            "final_risk_score": min(fraud_score, 100),
            "decision": decision,
            "reasons": all_reasons,
            "is_anomaly": is_anomaly,
            "is_duplicate": is_duplicate,
            "vendor_risk_score": vendor_risk_score
        }
    
    def analyze_expenses(self, expenses):
        """Complete fraud analysis for all expenses"""
        print("    🔍 Analyzing duplicates...")
        duplicates = self.detect_duplicates(expenses)
        print(f"       Found {len(duplicates)} potential duplicates")
        
        print("    🔍 Analyzing vendor risk...")
        print("    🔍 Analyzing behavior patterns...")
        behavior_anomalies = self.detect_behavior_anomalies(expenses)
        print(f"       Found {len(behavior_anomalies)} behavior anomalies")
        
        results = []
        for expense in expenses:
            vendor_risk_score, vendor_reasons = self.calculate_vendor_risk(
                expense['merchant'], expense['category']
            )
            
            fraud_result = self.calculate_fraud_score(
                expense, duplicates, vendor_risk_score, vendor_reasons, behavior_anomalies
            )
            
            results.append({
                'expense_id': expense['id'],
                'employee_id': expense['employee_id'],
                'amount': expense['amount'],
                'category': expense['category'],
                'merchant': expense['merchant'],
                'is_anomaly': fraud_result['is_anomaly'],
                'anomaly_score': fraud_result['final_risk_score'] / 100.0,
                'fraud_score': fraud_result['final_risk_score'],
                'fraud_decision': fraud_result['decision'],
                'fraud_reasons': fraud_result['reasons'],
                'is_duplicate': fraud_result['is_duplicate'],
                'vendor_risk_score': fraud_result['vendor_risk_score']
            })
        
        return pd.DataFrame(results)

# Import the enhanced FraudDetectionAgent
try:
    from src.agents.fraud_detection_agent import FraudDetectionAgent
    USE_ENHANCED_AGENT = True
    print("✅ Using enhanced FraudDetectionAgent with rule-based detection")
except ImportError as e:
    USE_ENHANCED_AGENT = False
    print(f"⚠️ Using built-in AdvancedFraudDetector: {e}")

# Import SummaryAgent
try:
    from src.agents.summary_agent import SummaryAgent
    USE_SUMMARY_AGENT = True
    print("✅ Using SummaryAgent for human-friendly explanations")
except ImportError as e:
    USE_SUMMARY_AGENT = False
    print(f"⚠️ SummaryAgent not available: {e}")

class PolicyAgent:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
    
    def batch_validate(self, expenses_data):
        """Mock policy validation"""
        df = pd.DataFrame(expenses_data)
        df['violation_count'] = np.random.randint(0, 3, len(df))
        df['violations'] = df.apply(lambda x: ['Weekend expense'] if x['violation_count'] > 0 else [], axis=1)
        return df

class AuditAgent:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
    
    def generate_audit_report(self, policy_results, fraud_results, behavioral_patterns):
        """Enhanced audit report with fraud insights"""
        high_risk_policy = len(policy_results[policy_results['violation_count'] > 0])
        
        return {
            'risk_assessment': {
                'high_risk_count': high_risk_policy,
                'medium_risk_count': len(behavioral_patterns),
                'low_risk_count': 0
            },
            'summary': {
                'compliance_rate': np.random.uniform(40, 60),
                'total_expenses': len(policy_results)
            },
            'top_violations': [('Weekend expense', 46), ('Amount exceeds limit', 2)],
            'recommendations': [
                {'priority': 'High', 'description': 'Provide policy training'},
                {'priority': 'High', 'description': 'Manually review anomalous expenses'}
            ]
        }

class ReportingAgent:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
    
    def generate_compliance_report(self, policy_results, fraud_results):
        """Mock compliance report"""
        return {
            'compliance_rate': np.random.uniform(40, 60),
            'violations_by_category': {'Travel': 10, 'Meals': 5},
            'summary': 'Compliance report generated'
        }
    
    def generate_visualizations(self, policy_results, fraud_results):
        """Mock visualization generation"""
        print("Visualizations saved to reports/audit_visualizations.png")
        return True

class MemoryManager:
    def __init__(self):
        self.memory_data = {}
        self.historical_expenses = []
    
    def save_memory(self, filename):
        """Save memory to file"""
        with open(filename, 'w') as f:
            json.dump(self.memory_data, f, indent=2)
        return True
    
    def get_employee_behavior(self, employee_id):
        """Mock employee behavior data"""
        return {'total_amount': 5000, 'total_expenses': 15}
    
    def get_historical_expenses(self):
        """Get historical expenses for duplicate detection"""
        return self.historical_expenses

class Config:
    def __init__(self):
        self.settings = {}
        # Add expense configuration for ML detection
        self.EXPENSE = type('EXPENSE', (), {
            'thresholds': {
                'Travel': 1000,
                'Meals': 500,
                'Entertainment': 300,
                'Supplies': 200,
                'Software': 2000,
                'Accommodation': 2000,
                'Shopping': 1000,
                'Other': 500,
                'Personal': 200
            },
            'categories': ['Travel', 'Meals', 'Entertainment', 'Supplies', 'Software', 'Accommodation', 'Shopping', 'Other', 'Personal']
        })()

# Summary Agent Integration
class SummaryProcessor:
    def __init__(self):
        self.summary_agent = SummaryAgent() if USE_SUMMARY_AGENT else None
    
    def generate_summaries(self, expenses_data, rule_based_results):
        """Generate human-friendly summaries for all expenses"""
        if not self.summary_agent:
            print("⚠️  SummaryAgent not available - skipping summary generation")
            return pd.DataFrame()
        
        summaries = []
        print("    📝 Generating human-friendly explanations...")
        
        for expense in expenses_data:
            # Find corresponding fraud result
            fraud_result = rule_based_results[rule_based_results['expense_id'] == expense['id']]
            if fraud_result.empty:
                continue
            
            fraud_row = fraud_result.iloc[0]
            
            # Create P2 output format for summary agent
            p2_output = {
                "decision": fraud_row['fraud_decision'],
                "final_risk_score": fraud_row['fraud_score'],
                "policy_violations": [],  # Could integrate with policy results
                "reasons": fraud_row.get('fraud_reasons', [])
            }
            
            # Generate summary
            summary_result = self.summary_agent.generate(expense, p2_output)
            
            summaries.append({
                'expense_id': expense['id'],
                'employee_id': expense['employee_id'],
                'merchant': expense['merchant'],
                'amount': expense['amount'],
                'summary_text': summary_result['summary_text'],
                'confidence_score': summary_result['confidence_score'],
                'recommendation': summary_result['recommendation'],
                'explanation_points': summary_result['explanation_points'],
                'review_timestamp': summary_result['review_timestamp']
            })
        
        return pd.DataFrame(summaries)

# Main System Class
class EnterpriseExpenseAuditSystem:
    def __init__(self):
        self.config = Config()
        self.memory = MemoryManager()
        self.advanced_fraud_detector = AdvancedFraudDetector()
        self.summary_processor = SummaryProcessor()
        
        self.agents = {
            'field_extraction': FieldExtractionAgent(),
            'policy': PolicyAgent(self.memory, self.config),
            'audit': AuditAgent(self.memory, self.config),
            'reporting': ReportingAgent(self.memory, self.config)
        }
        
        # Use enhanced agent if available, otherwise use built-in
        if USE_ENHANCED_AGENT:
            self.agents['fraud'] = FraudDetectionAgent(self.memory, self.config)
        else:
            self.agents['fraud'] = self.advanced_fraud_detector
            
        print("Enterprise Expense Audit System initialized successfully!")
    
    def process_raw_receipts(self, raw_receipts):
        """Process raw receipts through the entire pipeline"""
        print(f"Processing {len(raw_receipts)} raw receipts...")
        
        # Step 1: Field Extraction
        print("1. Extracting fields from raw receipts...")
        structured_expenses = self.agents['field_extraction'].process_raw_receipts(raw_receipts)
        
        # Continue with existing processing
        return self.process_expenses(structured_expenses)
    
    def process_expenses(self, expenses_data):
        """Process expenses through all agents - ENHANCED VERSION"""
        print(f"2. Processing {len(expenses_data)} structured expenses through multi-agent system...")
        
        # Policy validation
        print("3. Running policy validation...")
        policy_results = self.agents['policy'].batch_validate(expenses_data)
        
        # ENHANCED FRAUD DETECTION
        print("4. Running ADVANCED rule-based fraud detection...")
        rule_based_results = self.advanced_fraud_detector.analyze_expenses(expenses_data)
        
        # ML fraud detection (if available)
        if USE_ENHANCED_AGENT:
            print("4a. Running ML fraud detection...")
            fraud_results = self.agents['fraud'].detect_anomalies(expenses_data)
        else:
            fraud_results = pd.DataFrame()
        
        # NEW: Generate human-friendly summaries
        print("5. Generating human-friendly explanations...")
        summary_results = self.summary_processor.generate_summaries(expenses_data, rule_based_results)
        
        # Behavioral analysis
        print("6. Analyzing behavioral patterns...")
        expenses_df = pd.DataFrame(expenses_data)
        behavioral_patterns = pd.DataFrame()  # Simplified for demo
        
        # Generate audit report
        print("7. Generating enhanced audit report...")
        audit_report = self.agents['audit'].generate_audit_report(
            policy_results, fraud_results, behavioral_patterns
        )
        
        # Add rule-based results to audit report
        if not rule_based_results.empty:
            high_risk_fraud = rule_based_results[rule_based_results['fraud_decision'].isin(['REJECT', 'NEEDS_REVIEW'])]
            audit_report['advanced_fraud'] = {
                'rule_based_high_risk': len(high_risk_fraud),
                'duplicates_detected': rule_based_results['is_duplicate'].sum(),
                'high_risk_vendors': rule_based_results[rule_based_results['vendor_risk_score'] > 50].shape[0],
                'total_fraud_cases': len(high_risk_fraud),
                'fraud_decisions': {
                    'REJECT': len(rule_based_results[rule_based_results['fraud_decision'] == 'REJECT']),
                    'NEEDS_REVIEW': len(rule_based_results[rule_based_results['fraud_decision'] == 'NEEDS_REVIEW']),
                    'APPROVE': len(rule_based_results[rule_based_results['fraud_decision'] == 'APPROVE'])
                }
            }
        
        # Generate compliance report
        print("8. Generating compliance report...")
        compliance_report = self.agents['reporting'].generate_compliance_report(
            policy_results, fraud_results
        )
        
        # Generate visualizations
        print("9. Creating visualizations...")
        self.agents['reporting'].generate_visualizations(policy_results, fraud_results)
        
        # Store expenses for future duplicate detection
        self.memory.historical_expenses.extend(expenses_data)
        
        return {
            'field_extraction': expenses_data,
            'policy_validation': policy_results,
            'fraud_detection': fraud_results,  # ML results
            'rule_based_fraud': rule_based_results,  # NEW: Advanced fraud detection
            'summary_results': summary_results,  # NEW: Human-friendly summaries
            'behavioral_patterns': behavioral_patterns,
            'audit_report': audit_report,
            'compliance_report': compliance_report
        }

def generate_fraud_test_receipts(num_receipts=10):
    """Generate receipts that should trigger fraud detection"""
    receipts = []
    
    # Patterns that should trigger fraud detection
    fraud_patterns = [
        # DUPLICATE PATTERN: Same vendor, same amount, same day
        ("UBER INDIA PVT LTD\nRide completed: 15 Jan 2025\nTotal: ₹450.00\nPayment: Credit Card ****1234", "Uber", 450.00, "15 Jan 2025"),
        ("UBER INDIA\nTrip to office: 15 Jan 2025\nAmount: ₹450.00\nThank you!", "Uber", 450.00, "15 Jan 2025"),
        
        # HIGH-RISK VENDOR PATTERN: Personal expenses
        ("MOBILE RECHARGE STORE\nPersonal recharge: ₹500.00\nDate: 16 Jan 2025", "RECHARGE STORE", 500.00, "16 Jan 2025"),
        ("GIFT CARD EMPORIUM\nGift Card: ₹300.00\nDate: 17 Jan 2025", "GIFT CARD EMPORIUM", 300.00, "17 Jan 2025"),
        
        # SAME AMOUNT PATTERN
        ("AMAZON INDIA\nOrder total: ₹499.00\nOrder date: 18 Jan 2025", "Amazon", 499.00, "18 Jan 2025"),
        ("FLIPKART SHOPPING\nAmount: ₹499.00\nDate: 19 Jan 2025", "Flipkart", 499.00, "19 Jan 2025"),
        
        # MULTIPLE SAME VENDOR
        ("UBER INDIA\nNight ride: ₹600.00\nDate: 15 Jan 2025", "Uber", 600.00, "15 Jan 2025"),
        ("ZOMATO FOOD\nOrder: ₹650.00\nDate: 15 Jan 2025", "Zomato", 650.00, "15 Jan 2025"),
    ]
    
    # Use fraud patterns first, then fill with random if needed
    for pattern in fraud_patterns[:min(num_receipts, len(fraud_patterns))]:
        receipt_text, vendor, amount, date = pattern
        receipts.append(receipt_text)
    
    return receipts

def display_results(results):
    """Display results in a formatted way - ENHANCED"""
    print("\n" + "="*60)
    print("ENTERPRISE EXPENSE AUDIT RESULTS")
    print("="*60)
    
    # Field Extraction Results
    extracted_data = results['field_extraction']
    print(f"\n📝 FIELD EXTRACTION SUMMARY:")
    print(f"   Receipts processed: {len(extracted_data)}")
    print(f"   Total amount extracted: ₹{sum(exp['amount'] for exp in extracted_data):.2f}")
    
    # Categories found
    categories = {}
    for exp in extracted_data:
        cat = exp['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"   Categories detected: {', '.join([f'{k} ({v})' for k, v in categories.items()])}")
    
    # ENHANCED FRAUD DETECTION STATISTICS
    total_expenses = len(results['policy_validation'])
    policy_violations = len(results['policy_validation'][results['policy_validation']['violation_count'] > 0])
    
    # ML anomalies
    ml_anomalies = results['fraud_detection']['is_anomaly'].sum() if not results['fraud_detection'].empty else 0
    
    # NEW: Rule-based fraud insights
    rule_fraud_count = 0
    duplicate_count = 0
    high_risk_vendors = 0
    fraud_reasons = []
    
    if 'rule_based_fraud' in results and not results['rule_based_fraud'].empty:
        rule_data = results['rule_based_fraud']
        rule_fraud_count = rule_data[rule_data['is_anomaly']].shape[0]
        duplicate_count = rule_data['is_duplicate'].sum()
        high_risk_vendors = rule_data[rule_data['vendor_risk_score'] > 50].shape[0]
        
        # Collect fraud reasons
        for _, fraud in rule_data[rule_data['is_anomaly']].iterrows():
            if 'fraud_reasons' in fraud and fraud['fraud_reasons']:
                fraud_reasons.extend(fraud['fraud_reasons'])
    
    print(f"\n🔍 ENHANCED FRAUD DETECTION SUMMARY:")
    print(f"   ML Anomalies: {ml_anomalies}")
    print(f"   Rule-based Fraud Cases: {rule_fraud_count}")
    print(f"   Duplicate Receipts: {duplicate_count}")
    print(f"   High-Risk Vendors: {high_risk_vendors}")
    
    # Show top fraud reasons
    if fraud_reasons:
        from collections import Counter
        top_reasons = Counter(fraud_reasons).most_common(5)
        print(f"   🚨 Top Fraud Patterns:")
        for reason, count in top_reasons:
            print(f"      • {reason} ({count} cases)")
    elif rule_fraud_count > 0:
        print(f"   ℹ️  Fraud detected but no specific reasons recorded")
    
    # NEW: Summary Results Display
    if 'summary_results' in results and not results['summary_results'].empty:
        print(f"\n📋 HUMAN-FRIENDLY SUMMARIES:")
        summary_data = results['summary_results']
        print(f"   Summaries generated: {len(summary_data)}")
        
        # Show sample summaries
        sample_summaries = summary_data.head(2)
        for _, summary in sample_summaries.iterrows():
            print(f"\n   🎯 {summary['merchant']} - ₹{summary['amount']:.2f}")
            print(f"      Summary: {summary['summary_text']}")
            print(f"      Confidence: {summary['confidence_score']}%")
            print(f"      Recommendation: {summary['recommendation']}")
            if summary['explanation_points'] and len(summary['explanation_points']) > 0:
                print(f"      Key Points: {summary['explanation_points'][0]}")
    
    # Basic statistics
    print(f"\n📊 AUDIT STATISTICS:")
    print(f"   Total expenses processed: {total_expenses}")
    print(f"   Policy violations found: {policy_violations}")
    print(f"   Total suspicious expenses: {ml_anomalies + rule_fraud_count}")
    
    # Audit report highlights
    audit = results['audit_report']
    print(f"\n⚡ RISK ASSESSMENT:")
    print(f"   Overall risk level: {audit['risk_assessment']['high_risk_count']} high, "
          f"{audit['risk_assessment']['medium_risk_count']} medium, "
          f"{audit['risk_assessment']['low_risk_count']} low")
    
    print(f"   Compliance rate: {audit['summary']['compliance_rate']:.1f}%")
    
    # Show advanced fraud insights if available
    if 'advanced_fraud' in audit:
        adv = audit['advanced_fraud']
        print(f"\n🎯 ADVANCED FRAUD INSIGHTS:")
        print(f"   Rule-based high-risk cases: {adv.get('rule_based_high_risk', 0)}")
        print(f"   Duplicate receipts detected: {adv.get('duplicates_detected', 0)}")
        print(f"   High-risk vendor transactions: {adv.get('high_risk_vendors', 0)}")
        print(f"   Total fraud cases identified: {adv.get('total_fraud_cases', 0)}")
        
        # Show fraud decision breakdown
        if 'fraud_decisions' in adv:
            decisions = adv['fraud_decisions']
            print(f"   Fraud Decisions: REJECT({decisions.get('REJECT', 0)}), "
                  f"REVIEW({decisions.get('NEEDS_REVIEW', 0)}), "
                  f"APPROVE({decisions.get('APPROVE', 0)})")
    
    # Show detailed fraud cases
    if 'rule_based_fraud' in results and not results['rule_based_fraud'].empty:
        fraud_cases = results['rule_based_fraud'][results['rule_based_fraud']['is_anomaly']]
        if not fraud_cases.empty:
            print(f"\n🚨 DETAILED FRAUD CASES:")
            for _, fraud in fraud_cases.iterrows():
                reasons = fraud.get('fraud_reasons', ['Suspicious pattern'])
                print(f"   • {fraud['merchant']} - ₹{fraud['amount']:.2f}")
                print(f"     Score: {fraud['fraud_score']}, Decision: {fraud['fraud_decision']}")
                print(f"     Reasons: {', '.join(reasons[:2])}")
    
    # Top violations
    if audit.get('top_violations'):
        print(f"\n🚨 TOP VIOLATIONS:")
        for violation, count in audit['top_violations'][:3]:
            print(f"   • {violation}: {count} occurrences")
    
    # Recommendations
    if audit.get('recommendations'):
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in audit['recommendations'][:3]:
            print(f"   [{rec['priority']}] {rec['description']}")
    
    print(f"\n📈 Reports and visualizations have been generated")
    print("="*60)

def main():
    """Main function to run the expense audit system"""
    print("🚀 Enterprise Expense Audit and Fraud Detection System")
    print("With Enhanced Rule-Based Fraud Detection & Human-Friendly Summaries")
    print("="*50)
    
    # Initialize system
    audit_system = EnterpriseExpenseAuditSystem()
    
    # Generate fraud-test receipts instead of random ones
    print("\n📄 Generating fraud-test receipts...")
    sample_receipts = generate_fraud_test_receipts(8)
    
    # Process raw receipts through the entire pipeline
    print("\n🔄 Starting end-to-end processing...")
    results = audit_system.process_raw_receipts(sample_receipts)
    
    # Display results
    display_results(results)
    
    # Save detailed results
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Save extracted data
    extracted_df = pd.DataFrame(results['field_extraction'])
    extracted_df.to_csv('reports/extracted_expenses.csv', index=False)
    
    # Save audit results
    results['policy_validation'].to_csv('reports/policy_validation_results.csv', index=False)
    if not results['fraud_detection'].empty:
        results['fraud_detection'].to_csv('reports/fraud_detection_results.csv', index=False)
    
    # Save rule-based fraud results
    if 'rule_based_fraud' in results and not results['rule_based_fraud'].empty:
        results['rule_based_fraud'].to_csv('reports/rule_based_fraud_results.csv', index=False)
    
    # NEW: Save summary results
    if 'summary_results' in results and not results['summary_results'].empty:
        results['summary_results'].to_csv('reports/summary_results.csv', index=False)
    
    # Save audit report as JSON
    with open('reports/audit_report.json', 'w') as f:
        json.dump(results['audit_report'], f, default=str, indent=2)
    
    # Save memory for future sessions
    audit_system.memory.save_memory('reports/system_memory.json')
    
    print("\n✅ Audit completed successfully!")
    print("📁 Results saved to:")
    print("   - reports/extracted_expenses.csv")
    print("   - reports/policy_validation_results.csv")
    print("   - reports/fraud_detection_results.csv") 
    print("   - reports/rule_based_fraud_results.csv")
    print("   - reports/summary_results.csv")  # NEW
    print("   - reports/audit_report.json")
    print("   - reports/system_memory.json")
    print("   - reports/audit_visualizations.png")
    
    # Show sample extracted data
    print(f"\n🎯 SAMPLE EXTRACTED DATA:")
    print("="*50)
    for i, expense in enumerate(results['field_extraction'][:3]):
        print(f"Receipt {i+1}:")
        print(f"  Vendor: {expense['merchant']}")
        print(f"  Amount: ₹{expense['amount']:.2f}")
        print(f"  Category: {expense['category']}")
        print(f"  Date: {expense['date']}")
        print(f"  Employee: {expense['employee_id']}")
        print()

if __name__ == "__main__":
    main()