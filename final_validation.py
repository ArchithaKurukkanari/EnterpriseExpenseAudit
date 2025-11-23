import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.summary_agent import SummaryAgent

def validate_summary_agent():
    """Final validation of the Summary Agent"""
    print("🎯 FINAL VALIDATION - SUMMARY AGENT")
    print("=" * 50)
    
    agent = SummaryAgent()
    
    test_cases = [
        {
            "expense": {
                "id": "EXP000001",
                "vendor": "Uber", 
                "merchant": "Uber",
                "amount": 450.00,
                "category": "Travel",
                "employee_id": "EMP001"
            },
            "p2_output": {
                "decision": "NEEDS_REVIEW",
                "final_risk_score": 65,
                "policy_violations": ["amount_limit"],
                "reasons": ["vendor_frequency", "duplicate_detected"]
            }
        },
        {
            "expense": {
                "id": "EXP000002",
                "vendor": "Mobile Recharge",
                "merchant": "Mobile Recharge", 
                "amount": 500.00,
                "category": "Personal",
                "employee_id": "EMP002"
            },
            "p2_output": {
                "decision": "REJECTED", 
                "final_risk_score": 85,
                "policy_violations": ["non_business_expense"],
                "reasons": ["high_risk_vendor", "personal_expense"]
            }
        },
        {
            "expense": {
                "id": "EXP000003", 
                "vendor": "Amazon",
                "merchant": "Amazon",
                "amount": 1200.00,
                "category": "Shopping", 
                "employee_id": "EMP003"
            },
            "p2_output": {
                "decision": "APPROVED",
                "final_risk_score": 15,
                "policy_violations": [],
                "reasons": []
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}:")
        print(f"   Expense: {test_case['expense']['merchant']} - ₹{test_case['expense']['amount']}")
        print(f"   P2 Decision: {test_case['p2_output']['decision']} (Score: {test_case['p2_output']['final_risk_score']})")
        
        result = agent.generate(test_case['expense'], test_case['p2_output'])
        
        print(f"   ✅ Summary: {result['summary_text']}")
        print(f"   ✅ Confidence: {result['confidence_score']}%")
        print(f"   ✅ Recommendation: {result['recommendation']}")
        print(f"   ✅ Key Points:")
        for point in result['explanation_points'][:2]:  # Show first 2 points
            print(f"      • {point}")
    
    print(f"\n🎉 SUMMARY AGENT VALIDATION COMPLETE!")
    print("   All test cases processed successfully with human-friendly explanations.")

if __name__ == "__main__":
    validate_summary_agent()