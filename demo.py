
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def quick_demo():
    print("🚀 ENTERPRISE EXPENSE AUDIT - QUICK DEMO")
    print("=" * 50)
    
    from src.agents.field_extraction_agent import FieldExtractionAgent
    
    # Test with sample receipts
    extractor = FieldExtractionAgent()
    
    sample_receipts = [
        """
        UBER INDIA PVT LTD
        Ride completed: 15 Jan 2024
        Total: ₹980.50
        Payment: Credit Card ****1234
        Thank you for riding!
        """,
        
        """
        MCDONALD'S RESTAURANT
        Order Date: 14/01/2024
        Amount: Rs. 450.00
        Thank you for your visit!
        Employee: E012
        """,
        
        """
        AMAZON INDIA
        Order total: ₹2,499.00
        Order date: 2024-01-10
        Delivery by: 12 Jan 2024
        """
    ]
    
    print("📄 Processing sample receipts...")
    expenses = extractor.process_raw_receipts(sample_receipts)
    
    print("\n🎯 EXTRACTED DATA:")
    for i, expense in enumerate(expenses, 1):
        print(f"{i}. {expense['merchant']}")
        print(f"   Amount: ₹{expense['amount']:.2f}")
        print(f"   Category: {expense['category']}")
        print(f"   Date: {expense['date']}")
        print(f"   Employee: {expense['employee_id']}")
        print()
    
    print("✅ Demo completed! Run 'python main.py' for the full multi-agent system.")

if __name__ == "__main__":
    quick_demo()