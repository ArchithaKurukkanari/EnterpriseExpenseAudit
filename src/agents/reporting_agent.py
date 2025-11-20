import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class ReportingAgent:
    def __init__(self, memory_manager, config):
        self.memory = memory_manager
        self.config = config
        
    def generate_compliance_report(self, policy_results, fraud_results):
        """Generate compliance summary report"""
        
        compliance_data = {
            'total_expenses': len(policy_results),
            'compliant_expenses': len(policy_results[policy_results['is_valid'] == True]),
            'non_compliant_expenses': len(policy_results[policy_results['is_valid'] == False]),
            'total_amount': policy_results['amount'].sum(),
            'average_amount': policy_results['amount'].mean(),
            'max_amount': policy_results['amount'].max()
        }
        
        # Category-wise compliance
        category_compliance = {}
        for category in self.config.EXPENSE.categories:
            category_data = policy_results[policy_results['category'] == category]
            if len(category_data) > 0:
                compliance_rate = (len(category_data[category_data['is_valid'] == True]) / len(category_data)) * 100
                category_compliance[category] = {
                    'count': len(category_data),
                    'compliance_rate': compliance_rate,
                    'total_amount': category_data['amount'].sum()
                }
        
        report = {
            'report_date': datetime.now(),
            'compliance_summary': compliance_data,
            'category_breakdown': category_compliance,
            'top_violators': self._get_top_violators(policy_results),
            'risk_assessment': self._assess_risk_level(policy_results, fraud_results)
        }
        
        return report
    
    def _get_top_violators(self, policy_results):
        """Identify employees with most violations"""
        violators = policy_results[policy_results['violation_count'] > 0]
        if violators.empty:
            return []
            
        violator_summary = violators.groupby('employee_id').agg({
            'violation_count': 'sum',
            'amount': 'sum',
            'expense_id': 'count'
        }).reset_index()
        
        violator_summary.columns = ['employee_id', 'total_violations', 'total_amount', 'expense_count']
        violator_summary['avg_violations_per_expense'] = violator_summary['total_violations'] / violator_summary['expense_count']
        
        return violator_summary.nlargest(5, 'total_violations').to_dict('records')
    
    def _assess_risk_level(self, policy_results, fraud_results):
        """Assess overall risk level"""
        total_expenses = len(policy_results)
        if total_expenses == 0:
            return 'Low'
            
        violation_rate = len(policy_results[policy_results['violation_count'] > 0]) / total_expenses
        anomaly_rate = len(fraud_results[fraud_results['is_anomaly'] == True]) / total_expenses if not fraud_results.empty else 0
        
        overall_risk = (violation_rate * 0.6) + (anomaly_rate * 0.4)
        
        if overall_risk > 0.3:
            return 'High'
        elif overall_risk > 0.1:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_visualizations(self, policy_results, fraud_results, output_dir='reports'):
        """Generate visual charts and graphs"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Compliance by Category
        category_data = []
        for category in self.config.EXPENSE.categories:
            cat_expenses = policy_results[policy_results['category'] == category]
            if len(cat_expenses) > 0:
                compliant = len(cat_expenses[cat_expenses['is_valid'] == True])
                non_compliant = len(cat_expenses[cat_expenses['is_valid'] == False])
                category_data.append({'Category': category, 'Compliant': compliant, 'Non-Compliant': non_compliant})
        
        if category_data:
            cat_df = pd.DataFrame(category_data)
            cat_df.set_index('Category')[['Compliant', 'Non-Compliant']].plot(
                kind='bar', ax=axes[0,0], title='Compliance by Category'
            )
        
        # 2. Violation Types
        all_violations = []
        for violations in policy_results['violations']:
            all_violations.extend(violations)
        
        if all_violations:
            violation_counts = pd.Series(all_violations).value_counts().head(8)
            violation_counts.plot(kind='pie', ax=axes[0,1], title='Top Violation Types')
        
        # 3. Amount Distribution
        policy_results['amount'].plot(kind='hist', ax=axes[1,0], title='Expense Amount Distribution', bins=20)
        
        # 4. Risk Levels
        if not fraud_results.empty:
            risk_counts = fraud_results['risk_level'].value_counts()
            risk_counts.plot(kind='bar', ax=axes[1,1], title='Risk Level Distribution', color=['green', 'orange', 'red'])
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/audit_visualizations.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_dir}/audit_visualizations.png")