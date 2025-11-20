import pandas as pd
import numpy as np
import os
import sys
import re
import json
from datetime import datetime, timedelta

# Field Extraction Agent Class
class FieldExtractionAgent:
    def __init__(self):
        print("Field Extraction Agent initialized!")
    
    def extract_vendor(self, raw_text):
        """Extract vendor name from raw text"""
        patterns = [
            r'(Uber|Lyft|Taxi|Cab|OLA|McDonald|KFC|Amazon|Flipkart|Starbucks)',
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
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def extract_category(self, raw_text):
        """Extract category from raw text"""
        categories = {
            'Travel': ['uber', 'lyft', 'taxi', 'cab', 'flight', 'train', 'ola', 'airline', 'transport'],
            'Meals': ['restaurant', 'cafe', 'food', 'dinner', 'lunch', 'breakfast', 'mcdonald', 'kfc', 'starbucks', 'pizza', 'burger'],
            'Entertainment': ['movie', 'concert', 'entertainment', 'casino', 'theater', 'game'],
            'Supplies': ['stationery', 'print', 'copy', 'office supplies', 'store', 'market'],
            'Software': ['software', 'subscription', 'license', 'app', 'digital'],
            'Accommodation': ['hotel', 'motel', 'lodging', 'marriott', 'hilton', 'hyatt', 'inn'],
            'Shopping': ['amazon', 'flipkart', 'walmart', 'target', 'retail']
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
            print(f"  Receipt {i+1}: {vendor} - ₹{amount} - {category}")
        
        return structured_expenses
    
    def _extract_location(self, raw_text):
        """Extract location from text"""
        locations = ['New York', 'London', 'Tokyo', 'Mumbai', 'Bangalore', 'Delhi', 'Remote', 'Office']
        text_lower = raw_text.lower()
        
        for location in locations:
            if location.lower() in text_lower:
                return location
        
        return np.random.choice(locations)

# Mock other agent classes for demonstration
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

class FraudDetectionAgent:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
    
    def detect_anomalies(self, expenses_data):
        """Mock fraud detection"""
        df = pd.DataFrame(expenses_data)
        df['is_anomaly'] = np.random.choice([True, False], len(df), p=[0.1, 0.9])
        df['anomaly_score'] = np.random.uniform(0, 1, len(df))
        return df
    
    def detect_behavioral_patterns(self, expenses_df):
        """Mock behavioral analysis"""
        return pd.DataFrame([{'pattern': 'test', 'count': 1}])

class AuditAgent:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
    
    def generate_audit_report(self, policy_results, fraud_results, behavioral_patterns):
        """Mock audit report"""
        return {
            'risk_assessment': {
                'high_risk_count': len(policy_results[policy_results['violation_count'] > 0]),
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
    
    def save_memory(self, filename):
        """Save memory to file"""
        with open(filename, 'w') as f:
            json.dump(self.memory_data, f, indent=2)
        return True

class Config:
    def __init__(self):
        self.settings = {}

# Main System Class
class EnterpriseExpenseAuditSystem:
    def __init__(self):
        self.config = Config()
        self.memory = MemoryManager()
        self.agents = {
            'field_extraction': FieldExtractionAgent(),
            'policy': PolicyAgent(self.memory, self.config),
            'fraud': FraudDetectionAgent(self.memory, self.config),
            'audit': AuditAgent(self.memory, self.config),
            'reporting': ReportingAgent(self.memory, self.config)
        }
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
        """Process expenses through all agents"""
        print(f"2. Processing {len(expenses_data)} structured expenses through multi-agent system...")
        
        # Policy validation
        print("3. Running policy validation...")
        policy_results = self.agents['policy'].batch_validate(expenses_data)
        
        # Fraud detection
        print("4. Running fraud detection...")
        fraud_results = self.agents['fraud'].detect_anomalies(expenses_data)
        
        # Behavioral analysis
        print("5. Analyzing behavioral patterns...")
        expenses_df = pd.DataFrame(expenses_data)
        behavioral_patterns = self.agents['fraud'].detect_behavioral_patterns(expenses_df)
        
        # Generate audit report
        print("6. Generating audit report...")
        audit_report = self.agents['audit'].generate_audit_report(
            policy_results, fraud_results, behavioral_patterns
        )
        
        # Generate compliance report
        print("7. Generating compliance report...")
        compliance_report = self.agents['reporting'].generate_compliance_report(
            policy_results, fraud_results
        )
        
        # Generate visualizations
        print("8. Creating visualizations...")
        self.agents['reporting'].generate_visualizations(policy_results, fraud_results)
        
        return {
            'field_extraction': expenses_data,
            'policy_validation': policy_results,
            'fraud_detection': fraud_results,
            'behavioral_patterns': behavioral_patterns,
            'audit_report': audit_report,
            'compliance_report': compliance_report
        }

def generate_sample_receipts(num_receipts=10):
    """Generate sample raw receipt data for demonstration"""
    receipts = []
    
    templates = [
        """
        UBER INDIA PVT LTD
        Ride completed: {date}
        Total: ₹{amount:.2f}
        Payment: Credit Card ****1234
        Thank you for riding!
        """,
        
        """
        McDonald's Restaurant
        Order #12345
        Date: {date}
        Amount: Rs. {amount:.2f}
        Thank you for your visit!
        Employee: {employee}
        """,
        
        """
        Amazon India
        Order total: ₹{amount:.2f}
        Order date: {date}
        Delivery by: {delivery_date}
        """,
        
        """
        STARBUCKS COFFEE
        {date} {time}
        Total: ${usd_amount:.2f}
        Card: ****5678
        Thank You!
        """,
        
        """
        Hotel Marriott
        Check-out: {date}
        Room Charges: ₹{amount:.2f}
        Thank you for staying with us!
        """
    ]
    
    for i in range(num_receipts):
        template = np.random.choice(templates)
        date = (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime("%d %b %Y")
        amount = np.random.uniform(100, 2000)
        employee = np.random.choice([f'E{str(i).zfill(3)}' for i in range(1, 21)])
        delivery_date = (datetime.now() - timedelta(days=np.random.randint(0, 10))).strftime("%d %b %Y")
        time = f"{np.random.randint(8, 22):02d}:{np.random.randint(0, 60):02d}"
        usd_amount = amount / 75  # Rough USD conversion
        
        receipt = template.format(
            date=date,
            amount=amount,
            employee=employee,
            delivery_date=delivery_date,
            time=time,
            usd_amount=usd_amount
        )
        
        receipts.append(receipt)
    
    return receipts

def display_results(results):
    """Display results in a formatted way"""
    print("\n" + "="*60)
    print("ENTERPRISE EXPENSE AUDIT RESULTS")
    print("="*60)
    
    # Field Extraction Results
    extracted_data = results['field_extraction']
    print(f"\n📝 FIELD EXTRACTION SUMMARY:")
    print(f"   Receipts processed: {len(extracted_data)}")
    print(f"   Total amount extracted: ₹{sum(exp["amount"] for exp in extracted_data):.2f}")
    
    # Categories found
    categories = {}
    for exp in extracted_data:
        cat = exp['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"   Categories detected: {', '.join([f'{k} ({v})' for k, v in categories.items()])}")
    
    # Basic statistics
    total_expenses = len(results['policy_validation'])
    policy_violations = len(results['policy_validation'][results['policy_validation']['violation_count'] > 0])
    anomalies = results['fraud_detection']['is_anomaly'].sum() if not results['fraud_detection'].empty else 0
    
    print(f"\n📊 AUDIT STATISTICS:")
    print(f"   Total expenses processed: {total_expenses}")
    print(f"   Policy violations found: {policy_violations}")
    print(f"   Anomalies detected: {anomalies}")
    
    # Audit report highlights
    audit = results['audit_report']
    print(f"\n⚡ RISK ASSESSMENT:")
    print(f"   Overall risk level: {audit['risk_assessment']['high_risk_count']} high, "
          f"{audit['risk_assessment']['medium_risk_count']} medium, "
          f"{audit['risk_assessment']['low_risk_count']} low")
    
    print(f"   Compliance rate: {audit['summary']['compliance_rate']:.1f}%")
    
    # Top violations
    if audit['top_violations']:
        print(f"\n🚨 TOP VIOLATIONS:")
        for violation, count in audit['top_violations'][:3]:
            print(f"   • {violation}: {count} occurrences")
    
    # Recommendations
    if audit['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in audit['recommendations'][:3]:
            print(f"   [{rec['priority']}] {rec['description']}")
    
    print(f"\n📈 Reports and visualizations have been generated")
    print("="*60)

def main():
    """Main function to run the expense audit system"""
    print("🚀 Enterprise Expense Audit and Fraud Detection System")
    print("With Field Extraction Agent")
    print("="*50)
    
    # Initialize system
    audit_system = EnterpriseExpenseAuditSystem()
    
    # Generate sample raw receipts
    print("\n📄 Generating sample raw receipts...")
    sample_receipts = generate_sample_receipts(8)
    
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