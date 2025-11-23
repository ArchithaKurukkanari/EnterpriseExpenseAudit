import json
from datetime import datetime
from typing import Dict, List, Any

class SummaryAgent:
    """
    LLM Summary & Explanation Agent
    Converts policy + fraud results into human-friendly explanations
    """
    
    def __init__(self):
        self.confidence_rules = {
            "APPROVED": 90,
            "NEEDS_REVIEW": 50,
            "REJECTED": 20
        }
        
        # Mapping for common policy violations to human-readable text
        self.policy_explanations = {
            "amount_limit": "Expense exceeds category spending limit",
            "category_violation": "Expense category violates company policy",
            "vendor_blacklist": "Vendor is restricted or blacklisted",
            "date_out_of_policy": "Expense date is outside policy period",
            "missing_receipt": "Missing or invalid receipt documentation",
            "non_business_expense": "Expense appears to be personal in nature",
            "late_submission": "Expense submitted after deadline"
        }
        
        # Mapping for fraud patterns to human-readable text
        self.fraud_explanations = {
            "duplicate": "Potential duplicate receipt detected",
            "vendor_frequency": "Unusual vendor usage pattern detected",
            "repeating_amounts": "Suspicious repeating amount pattern",
            "category_mismatch": "Vendor-category mismatch detected",
            "high_risk_vendor": "Transaction with high-risk vendor",
            "suspicious_behavior": "Unusual employee spending behavior",
            "odd_hours": "Expense occurred during non-business hours",
            "high-risk vendor": "Vendor flagged as high-risk",
            "personal expense": "Personal expense detected",
            "same amount": "Repeated amount pattern detected"
        }
    
    def generate(self, expense: Dict, p2_output: Dict) -> Dict[str, Any]:
        """
        Generate human-readable explanation for expense review
        
        Args:
            expense: Normalized expense data from field extraction
            p2_output: Combined policy + fraud detection results
        
        Returns:
            Dictionary with summary text, explanation points, and confidence score
        """
        try:
            # Extract key information with safe defaults
            decision = p2_output.get("decision", "NEEDS_REVIEW")
            risk_score = p2_output.get("final_risk_score", 0)
            policy_flags = p2_output.get("policy_violations", [])
            fraud_reasons = p2_output.get("reasons", [])
            
            # Generate explanation components
            summary_text = self._generate_summary_text(expense, decision, risk_score)
            explanation_points = self._generate_explanation_points(policy_flags, fraud_reasons)
            confidence_score = self._calculate_confidence(decision, risk_score, policy_flags, fraud_reasons)
            recommendation = self._generate_recommendation(decision, risk_score)
            
            return {
                "summary_text": summary_text,
                "explanation_points": explanation_points,
                "confidence_score": confidence_score,
                "recommendation": recommendation,
                "review_timestamp": datetime.now().isoformat(),
                "expense_id": expense.get("id", "unknown"),
                "employee_id": expense.get("employee_id", "unknown")
            }
            
        except Exception as e:
            return self._generate_error_response(str(e))
    
    def _generate_summary_text(self, expense: Dict, decision: str, risk_score: int) -> str:
        """Generate main summary text"""
        
        vendor = expense.get("merchant", expense.get("vendor", "Unknown vendor"))
        amount = expense.get("amount", "Unknown amount")
        category = expense.get("category", "Unknown category")
        
        base_summary = f"Expense of ₹{amount} from {vendor} categorized as {category}"
        
        decision_texts = {
            "APPROVED": f"{base_summary} has been automatically approved with low risk indicators.",
            "NEEDS_REVIEW": f"{base_summary} requires manager review due to moderate risk factors (Score: {risk_score}/100).",
            "REJECTED": f"{base_summary} has been flagged for rejection due to high-risk violations (Score: {risk_score}/100)."
        }
        
        return decision_texts.get(decision, f"{base_summary} is pending review.")
    
    def _generate_explanation_points(self, policy_flags: List, fraud_reasons: List) -> List[str]:
        """Generate bullet-point explanations"""
        points = []
        
        # Process policy violations
        for violation in policy_flags:
            if isinstance(violation, dict):
                violation_type = violation.get("type", "")
                explanation = self.policy_explanations.get(violation_type, f"Policy violation: {violation_type}")
                points.append(explanation)
            else:
                # Handle string violations
                violation_lower = str(violation).lower()
                found_match = False
                for key, explanation in self.policy_explanations.items():
                    if key in violation_lower:
                        points.append(explanation)
                        found_match = True
                        break
                if not found_match:
                    points.append(f"Policy issue: {violation}")
        
        # Process fraud detection reasons
        for reason in fraud_reasons:
            if isinstance(reason, dict):
                reason_type = reason.get("type", "")
                explanation = self.fraud_explanations.get(reason_type, f"Risk indicator: {reason_type}")
                points.append(explanation)
            else:
                reason_lower = str(reason).lower()
                found_match = False
                for key, explanation in self.fraud_explanations.items():
                    if key in reason_lower:
                        points.append(explanation)
                        found_match = True
                        break
                if not found_match:
                    # Try partial matching for common patterns
                    if "duplicate" in reason_lower:
                        points.append("Potential duplicate receipt detected")
                    elif "vendor" in reason_lower and "risk" in reason_lower:
                        points.append("High-risk vendor identified")
                    elif "personal" in reason_lower:
                        points.append("Personal expense detected")
                    elif "amount" in reason_lower and "repeat" in reason_lower:
                        points.append("Suspicious repeating amount pattern")
                    else:
                        points.append(f"Anomaly detected: {reason}")
        
        # Add positive feedback if no issues
        if not points:
            points.extend([
                "✓ No policy violations detected",
                "✓ No suspicious patterns identified",
                "✓ Vendor appears legitimate",
                "✓ Amount within reasonable range"
            ])
        
        return points
    
    def _calculate_confidence(self, decision: str, risk_score: int, 
                            policy_flags: List, fraud_reasons: List) -> int:
        """Calculate confidence score based on rules and patterns"""
        
        base_confidence = self.confidence_rules.get(decision, 50)
        
        # Adjust based on risk score
        if risk_score < 25:
            base_confidence += 20
        elif risk_score < 50:
            base_confidence += 10
        elif risk_score > 75:
            base_confidence -= 25
        elif risk_score > 50:
            base_confidence -= 10
        
        # Adjust based on number and severity of violations
        violation_count = len(policy_flags) + len(fraud_reasons)
        if violation_count == 0:
            base_confidence += 15
        elif violation_count >= 3:
            base_confidence -= 20
        
        # Ensure confidence stays within bounds
        return max(0, min(100, base_confidence))
    
    def _generate_recommendation(self, decision: str, risk_score: int) -> str:
        """Generate specific recommendation text"""
        
        recommendations = {
            "APPROVED": "Automatically approve this expense. No further action required.",
            "NEEDS_REVIEW": f"Manually review this expense. Verify business purpose and receipt details. Risk level: {'Medium' if risk_score < 70 else 'High'}.",
            "REJECTED": "Reject this expense. Contact employee for clarification if policy allows."
        }
        
        return recommendations.get(decision, "Investigate this expense further.")
    
    def _generate_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate response when processing fails"""
        return {
            "summary_text": f"Error generating summary: {error_msg}",
            "explanation_points": ["System error occurred during analysis"],
            "confidence_score": 0,
            "recommendation": "Manual review required due to system error",
            "review_timestamp": datetime.now().isoformat(),
            "error": error_msg
        }
    
    def batch_process(self, expenses_with_p2: List[tuple]) -> List[Dict]:
        """Process multiple expenses in batch"""
        results = []
        for expense, p2_output in expenses_with_p2:
            result = self.generate(expense, p2_output)
            results.append(result)
        return results