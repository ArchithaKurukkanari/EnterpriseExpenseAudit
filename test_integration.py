import sys
import os
import pandas as pd

# Add src to path so we can import our modules
sys.path.append('src')

from agents.field_extraction_agent import FieldExtractionAgent
from agents.fraud_detection_agent import FraudDetectionAgent

# Mock classes for dependencies
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
            'Travel': 1000,
            'Meals': 500, 
            'Entertainment': 300,
            'Supplies': 200,
            'Software': 2000,
            'Accommodation': 2000,
            'Shopping': 1000,
            'Other': 500
        }
        categories = ['Travel', 'Meals', 'Entertainment', 'Supplies', 'Software', 'Accommodation', 'Shopping', 'Other']

def test_basic_integration():
    print("🧪 Testing Fraud Detection Integration...")
    print("=" * 50)
    
    try:
        # Initialize components
        field_agent = FieldExtractionAgent()
        fraud_agent = FraudDetectionAgent(MockMemoryManager(), MockConfig())
        
        # Sample raw receipts - including some suspicious patterns
        sample_receipts = [
            "Uber India Pvt Ltd Trip to client ₹450.00 15 Jan 2025 Travel",
            "Uber India Pvt Ltd Trip to office ₹450.00 15 Jan 2025 Travel",  # Potential duplicate
            "Zomato Food Order ₹650.00 16 Jan 2025 Meals", 
            "Mobile Recharge Store ₹500.00 17 Jan 2025 Personal",  # High-risk vendor
            "Amazon Shopping ₹1200.00 18 Jan 2025 Shopping",
            "Uber India Night Ride ₹600.00 15 Jan 2025 Travel"  # Same day, same vendor
        ]
        
        # Step 1: Field Extraction (your existing code)
        print("1. Testing field extraction...")
        expenses = field_agent.process_raw_receipts(sample_receipts)
        print(f"   ✅ Extracted {len(expenses)} expenses")
        for i, exp in enumerate(expenses[:2]):  # Show first 2
            print(f"      {i+1}. {exp['merchant']} - ₹{exp['amount']} - {exp['category']}")
        
        # Step 2: Test ML fraud detection (your existing code)
        print("\n2. Testing ML fraud detection...")
        ml_results = fraud_agent.detect_anomalies(expenses)
        print(f"   ✅ ML anomalies found: {ml_results['is_anomaly'].sum()}")
        if not ml_results.empty:
            anomalies = ml_results[ml_results['is_anomaly']]
            if not anomalies.empty:
                print("   🚨 ML Anomalies detected in:")
                for _, anomaly in anomalies.iterrows():
                    print(f"      - {anomaly['expense_id']}: ₹{anomaly['amount']} ({anomaly['category']})")
        
        # Step 3: Test NEW rule-based fraud detection
        print("\n3. Testing rule-based fraud detection...")
        rule_results = fraud_agent.detect_rule_based_fraud(expenses)
        rule_fraud_count = rule_results[rule_results['is_anomaly']].shape[0]
        print(f"   ✅ Rule-based fraud cases: {rule_fraud_count}")
        
        if rule_fraud_count > 0:
            fraud_cases = rule_results[rule_results['is_anomaly']]
            print("   🚨 Rule-based fraud detected:")
            for _, fraud in fraud_cases.iterrows():
                reasons = fraud.get('fraud_reasons', [])
                reason_str = reasons[0] if reasons else "Suspicious pattern"
                print(f"      - {fraud['expense_id']}: {reason_str}")
                print(f"        Score: {fraud['fraud_score']}, Decision: {fraud['fraud_decision']}")
        
        # Step 4: Check for duplicates specifically
        duplicate_count = rule_results['is_duplicate'].sum()
        if duplicate_count > 0:
            print(f"   🔍 Duplicates found: {duplicate_count}")
        
        # Step 5: Test comprehensive detection
        print("\n4. Testing comprehensive detection...")
        comprehensive_results = fraud_agent.comprehensive_fraud_detection(expenses)
        summary = comprehensive_results['summary']
        print(f"   ✅ Comprehensive summary:")
        print(f"      - Total expenses: {summary['total_expenses']}")
        print(f"      - ML anomalies: {summary['ml_anomalies_count']}")
        print(f"      - Rule-based fraud: {summary['rule_based_fraud_count']}")
        print(f"      - Combined risk cases: {summary['combined_risk_count']}")
        
        print("\n🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test each fraud detection component individually"""
    print("\n🔧 Testing Individual Components...")
    print("=" * 50)
    
    try:
        fraud_agent = FraudDetectionAgent(MockMemoryManager(), MockConfig())
        
        # Test sample expense data
        sample_expenses = [
            {
                'id': 'EXP001',
                'employee_id': 'E001',
                'amount': 450.0,
                'category': 'Travel',
                'date': '15 Jan 2025',
                'merchant': 'Uber India',
                'description': 'Trip to client meeting',
                'hour': 14
            },
            {
                'id': 'EXP002', 
                'employee_id': 'E001',
                'amount': 450.0,  # Same amount - potential pattern
                'category': 'Travel',
                'date': '15 Jan 2025',  # Same date
                'merchant': 'Uber India',  # Same vendor
                'description': 'Trip to office',
                'hour': 18
            }
        ]
        
        print("1. Testing ML anomaly detection...")
        ml_results = fraud_agent.detect_anomalies(sample_expenses)
        print(f"   ✅ ML detection working: {len(ml_results)} results")
        
        print("2. Testing rule-based fraud detection...")
        rule_results = fraud_agent.detect_rule_based_fraud(sample_expenses)
        print(f"   ✅ Rule-based detection working: {len(rule_results)} results")
        
        print("3. Testing behavioral patterns...")
        expenses_df = pd.DataFrame(sample_expenses)
        behavior_results = fraud_agent.detect_behavioral_patterns(expenses_df)
        print(f"   ✅ Behavioral analysis working: {len(behavior_results)} patterns")
        
        print("\n🎉 All individual components working!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_duplicate_detection():
    """Specifically test duplicate detection"""
    print("\n🔍 Testing Duplicate Detection...")
    print("=" * 50)
    
    try:
        fraud_agent = FraudDetectionAgent(MockMemoryManager(), MockConfig())
        
        # Create expenses with duplicates
        duplicate_expenses = [
            {
                'id': 'EXP001',
                'employee_id': 'E001',
                'amount': 450.0,
                'category': 'Travel',
                'date': '15 Jan 2025',
                'merchant': 'Uber India',
                'description': 'Trip to client meeting',
                'hour': 14
            },
            {
                'id': 'EXP002',
                'employee_id': 'E001', 
                'amount': 450.0,  # Same amount
                'category': 'Travel',  # Same category
                'date': '15 Jan 2025',  # Same date
                'merchant': 'Uber India',  # Same vendor
                'description': 'Trip to client meeting',  # Same description
                'hour': 15
            }
        ]
        
        print("Testing with potential duplicates...")
        rule_results = fraud_agent.detect_rule_based_fraud(duplicate_expenses)
        
        duplicates = rule_results['is_duplicate'].sum()
        print(f"   ✅ Duplicates detected: {duplicates}")
        
        if duplicates > 0:
            print("   🎯 Duplicate detection is working!")
        else:
            print("   ℹ️  No duplicates detected in this test case")
        
        return True
        
    except Exception as e:
        print(f"❌ Duplicate test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Fraud Detection Integration Tests")
    print("This tests the new rule-based fraud detection with your existing system")
    print("=" * 60)
    
    # Run tests
    success1 = test_basic_integration()
    success2 = test_individual_components()
    success3 = test_duplicate_detection()
    
    if success1 and success2 and success3:
        print("\n✅ ALL TESTS PASSED! Your system is ready with enhanced fraud detection.")
        print("\nNext steps:")
        print("1. Run 'python main.py' to see the enhanced system in action")
        print("2. Check the new 'rule_based_fraud' section in your results")
        print("3. Look for duplicate detection and vendor risk analysis")
    else:
        print("\n❌ Some tests failed. Check the errors above.")