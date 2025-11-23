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

def demo_summary_agent():
    """Demo the summary explanation capabilities"""
    try:
        from src.agents.summary_agent import SummaryAgent
        
        agent = SummaryAgent()
        
        # Sample integrated P2 output (policy + fraud)
        sample_p2_output = {
            "decision": "NEEDS_REVIEW",
            "final_risk_score": 65,
            "policy_violations": ["amount_limit", "late_submission"],
            "reasons": ["vendor_frequency", "category_mismatch"]
        }
        
        sample_expense = {
            "vendor": "Premium Taxi Service",
            "amount": "₹1200.00",
            "date": "2025-01-18",
            "category": "Local Travel",
            "employee_id": "EMP123"
        }
        
        result = agent.generate(sample_expense, sample_p2_output)
        
        print("\n🎯 EXPENSE REVIEW SUMMARY")
        print("=" * 50)
        print(f"📝 {result['summary_text']}")
        print(f"✅ Confidence: {result['confidence_score']}%")
        print(f"💡 Recommendation: {result['recommendation']}")
        print("\n🔍 Detailed Analysis:")
        for point in result['explanation_points']:
            print(f"   • {point}")
            
    except ImportError as e:
        print(f"❌ SummaryAgent not available: {e}")
    except Exception as e:
        print(f"❌ Error in summary demo: {e}")

if __name__ == "__main__":
    quick_demo()
    demo_summary_agent()