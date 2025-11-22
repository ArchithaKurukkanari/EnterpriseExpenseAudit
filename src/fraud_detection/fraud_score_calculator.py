class FraudScoreCalculator:
    def __init__(self):
        self.weights = {
            'duplicate': 0.30,
            'vendor_risk': 0.25,
            'behavior_risk': 0.25,
            'rule_risk': 0.20  # From P2-A policy agent
        }
        
        self.thresholds = {
            'APPROVE': 30,
            'NEEDS_REVIEW': 70,
            'REJECT': 85
        }
    
    def calculate_fraud_score(self, duplicate_result, vendor_risk_result, 
                            behavior_risk_result, rule_risk_score=0):
        """Calculate final fraud score and decision"""
        
        # Calculate component scores
        duplicate_score = 100 if duplicate_result.get('is_duplicate', False) else 0
        vendor_score = vendor_risk_result.get('vendor_risk_score', 0)
        behavior_score = behavior_risk_result.get('behavior_risk_score', 0)
        
        # Calculate weighted score
        weighted_score = (
            duplicate_score * self.weights['duplicate'] +
            vendor_score * self.weights['vendor_risk'] +
            behavior_score * self.weights['behavior_risk'] +
            rule_risk_score * self.weights['rule_risk']
        )
        
        # Make decision
        decision = self._make_decision(weighted_score)
        
        # Collect all reasons
        all_reasons = []
        
        if duplicate_result.get('is_duplicate', False):
            all_reasons.extend(duplicate_result.get('reasons', []))
        
        all_reasons.extend(vendor_risk_result.get('reasons', []))
        all_reasons.extend(behavior_risk_result.get('reasons', []))
        
        # Remove duplicates and limit reasons
        unique_reasons = list(set(all_reasons))[:5]
        
        return {
            "final_risk_score": min(round(weighted_score), 100),
            "decision": decision,
            "reasons": unique_reasons,
            "component_scores": {
                "duplicate_score": duplicate_score,
                "vendor_risk_score": vendor_score,
                "behavior_risk_score": behavior_score,
                "rule_risk_score": rule_risk_score
            }
        }
    
    def _make_decision(self, score):
        """Make decision based on score threshold"""
        if score >= self.thresholds['REJECT']:
            return "REJECT"
        elif score >= self.thresholds['NEEDS_REVIEW']:
            return "NEEDS_REVIEW"
        else:
            return "APPROVE"