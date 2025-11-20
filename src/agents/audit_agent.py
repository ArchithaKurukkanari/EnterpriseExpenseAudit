import pandas as pd
from typing import Dict, List
from datetime import datetime

class AuditAgent:
    def __init__(self, memory_manager, config):
        self.memory = memory_manager
        self.config = config
        self.audit_trails = []
    
    def generate_audit_report(self, policy_results, fraud_results, behavioral_patterns):
        """Generate comprehensive audit report"""
        
        # Calculate key metrics
        total_expenses = len(policy_results)
        policy_violations = len(policy_results[policy_results['violation_count'] > 0])
        anomalies_detected = len(fraud_results[fraud_results['is_anomaly'] == True]) if not fraud_results.empty else 0
        behavioral_issues = len(behavioral_patterns)
        
        # Risk assessment
        high_risk_expenses = policy_results[
            (policy_results['violation_count'] > 0) | 
            (policy_results['requires_review'] == True)
        ]
        
        # Generate report
        audit_report = {
            'report_date': datetime.now(),
            'summary': {
                'total_expenses_audited': total_expenses,
                'policy_violations': int(policy_violations),
                'anomalies_detected': int(anomalies_detected),
                'behavioral_patterns_found': int(behavioral_issues),
                'compliance_rate': ((total_expenses - policy_violations) / total_expenses * 100) if total_expenses > 0 else 100
            },
            'risk_assessment': {
                'high_risk_count': len(high_risk_expenses),
                'medium_risk_count': len(behavioral_patterns[behavioral_patterns['risk_level'] == 'Medium']),
                'low_risk_count': len(behavioral_patterns[behavioral_patterns['risk_level'] == 'Low'])
            },
            'top_violations': self._get_top_violations(policy_results),
            'recommendations': self._generate_recommendations(policy_results, fraud_results, behavioral_patterns)
        }
        
        # Store audit trail
        self.audit_trails.append(audit_report)
        
        return audit_report
    
    def _get_top_violations(self, policy_results):
        """Extract top policy violations"""
        all_violations = []
        for violations in policy_results['violations']:
            all_violations.extend(violations)
        
        violation_counts = {}
        for violation in all_violations:
            if violation in violation_counts:
                violation_counts[violation] += 1
            else:
                violation_counts[violation] = 1
        
        return sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _generate_recommendations(self, policy_results, fraud_results, behavioral_patterns):
        """Generate recommendations based on audit findings"""
        recommendations = []
        
        # Policy violation recommendations
        policy_violation_count = len(policy_results[policy_results['violation_count'] > 0])
        if policy_violation_count > 0:
            recommendations.append({
                'type': 'policy_training',
                'priority': 'High',
                'description': f'Provide policy training for employees with {policy_violation_count} violations'
            })
        
        # Anomaly detection recommendations
        if not fraud_results.empty:
            anomaly_count = fraud_results['is_anomaly'].sum()
            if anomaly_count > 0:
                recommendations.append({
                    'type': 'manual_review',
                    'priority': 'High',
                    'description': f'Manually review {anomaly_count} anomalous expenses'
                })
        
        # Behavioral pattern recommendations
        if not behavioral_patterns.empty:
            high_risk_patterns = behavioral_patterns[behavioral_patterns['risk_level'] == 'High']
            if len(high_risk_patterns) > 0:
                recommendations.append({
                    'type': 'behavior_monitoring',
                    'priority': 'Medium',
                    'description': 'Implement enhanced monitoring for employees with suspicious behavioral patterns'
                })
        
        return recommendations