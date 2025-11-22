import sys
import os
sys.path.append('src')

from agents.field_extraction_agent import FieldExtractionAgent
from agents.fraud_detection_agent import FraudDetectionAgent

class MockMemoryManager:
    def get_employee_behavior(self, employee_id):
        return {'total_amount': 5000, 'total_expenses': 15}
    
    def get_historical_expenses(self):
        return []
    
    def add_fraud_pattern(self, pattern):
        print(f"   💾 Fraud pattern saved: {pattern['type']}")

class MockConfig:
    class EXPENSE:
        thresholds = {
            'Travel': 1000, 'Meals': 500, 'Entertainment': 300, 'Supplies': 200,
            'Software': 2000, 'Accommodation': 2000, 'Shopping': 1000, 'Other': 500
        }
        categories = ['Travel', 'Meals', 'Entertainment', 'Supplies', 'Software', 'Accommodation', 'Shopping', 'Other']

def test_fraud_patterns():
    """Test with data that should trigger fraud detection"""
    print("🧪 Testing with Fraud-Prone Data Patterns")
    print("=" * 60)
    
    field_agent = FieldExtractionAgent()
    fraud_agent = FraudDetectionAgent(MockMemoryManager(), MockConfig())
    
    # Create receipts that should trigger fraud detection
    fraud_receipts = [
        # DUPLICATE PATTERN: Same vendor, same amount, same day
        "Uber India Trip to office ₹450.00 15 Jan 2025 Travel",
        "Uber India Trip to client ₹450.00 15 Jan 2025 Travel",  # Should be duplicate
        
        # HIGH-RISK VENDOR PATTERN: Personal expenses
        "Mobile Recharge Store ₹500.00 16 Jan 2025 Personal Recharge",
        "Gift Card Shop ₹300.00 17 Jan 2025 Entertainment Gift",
        
        # SUSPICIOUS AMOUNT PATTERN: Same amount repeated
        "Amazon India Order ₹499.00 18 Jan 2025 Shopping",
        "Flipkart Shopping ₹499.00 19 Jan 2025 Shopping",  # Same amount
        
        # BEHAVIORAL PATTERN: Multiple same vendor in short time
        "Uber India Night Ride ₹600.00 15 Jan 2025 Travel",  # 3rd Uber same day
        "Zomato Food Order ₹650.00 15 Jan 2025 Meals",  # Multiple same day
    ]
    
    print("1. Processing fraud-prone receipts...")
    expenses = field_agent.process_raw_receipts(fraud_receipts)
    
    print("2. Running rule-based fraud detection...")
    rule_results = fraud_agent.detect_rule_based_fraud(expenses)
    
    # Analyze results
    fraud_cases = rule_results[rule_results['is_anomaly']]
    duplicate_count = rule_results['is_duplicate'].sum()
    high_risk_vendors = rule_results[rule_results['vendor_risk_score'] > 50].shape[0]
    
    print(f"\n📊 FRAUD DETECTION RESULTS:")
    print(f"   Total expenses: {len(expenses)}")
    print(f"   Fraud cases detected: {len(fraud_cases)}")
    print(f"   Duplicates found: {duplicate_count}")
    print(f"   High-risk vendors: {high_risk_vendors}")
    
    if not fraud_cases.empty:
        print(f"\n🚨 FRAUD CASES IDENTIFIED:")
        for _, fraud in fraud_cases.iterrows():
            reasons = fraud.get('fraud_reasons', ['Unknown pattern'])
            print(f"   - {fraud['expense_id']}: {fraud['merchant']} - ₹{fraud['amount']}")
            print(f"     Score: {fraud['fraud_score']}, Decision: {fraud['fraud_decision']}")
            print(f"     Reasons: {', '.join(reasons[:2])}")
    else:
        print(f"\n❌ NO FRAUD CASES DETECTED - This indicates an issue")
        print("   Checking individual components...")
        
        # Test duplicate detection specifically
        print(f"\n🔍 DEBUGGING DUPLICATE DETECTION:")
        for i, exp1 in enumerate(expenses):
            for j, exp2 in enumerate(expenses):
                if i != j and exp1['merchant'] == exp2['merchant'] and exp1['amount'] == exp2['amount']:
                    print(f"   Potential duplicate: {exp1['merchant']} - ₹{exp1['amount']}")
        
        # Test vendor risk specifically
        print(f"\n🔍 DEBUGGING VENDOR RISK:")
        for exp in expenses:
            vendor = exp['merchant']
            if any(keyword in vendor.lower() for keyword in ['recharge', 'gift', 'personal']):
                print(f"   High-risk vendor: {vendor}")

if __name__ == "__main__":
    test_fraud_patterns()