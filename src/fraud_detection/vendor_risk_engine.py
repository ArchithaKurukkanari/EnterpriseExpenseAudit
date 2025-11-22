import re
from collections import Counter

class VendorRiskEngine:
    def __init__(self):
        self.high_risk_vendors = {
            'uber': {'base_risk': 30, 'odd_hours_risk': 40},
            'ola': {'base_risk': 30, 'odd_hours_risk': 40},
            'zomato': {'base_risk': 20},
            'swiggy': {'base_risk': 20},
            'amazon': {'base_risk': 10},
            'flipkart': {'base_risk': 10}
        }
        
        self.personal_vendor_keywords = [
            'recharge', 'mobile', 'prepaid', 'gift', 'personal', 'family',
            'entertainment', 'movie', 'party', 'drinks', 'alcohol',
            'shopping', 'fashion', 'jewelry', 'liquor', 'bar'
        ]
        
        self.suspicious_patterns = [
            r'.*recharge.*',
            r'.*gift.*card.*',
            r'.*personal.*',
            r'.*entertainment.*',
            r'.*liquor.*',
            r'.*alcohol.*',
            r'.*bar.*',
            r'.*casino.*'
        ]
    
    def assess_vendor_risk(self, vendor_name, amount, date_str, category, historical_data=None):
        """Assess risk level for a vendor"""
        risk_score = 0
        reasons = []
        
        vendor_lower = vendor_name.lower() if vendor_name else ""
        amount_value = self._extract_numeric_amount(amount)
        
        # Check if vendor is in high-risk list
        for risk_vendor, risk_config in self.high_risk_vendors.items():
            if risk_vendor in vendor_lower:
                risk_score += risk_config['base_risk']
                reasons.append(f"High-risk vendor: {risk_vendor}")
                break
        
        # Check for personal vendor keywords
        for keyword in self.personal_vendor_keywords:
            if keyword in vendor_lower:
                risk_score += 25
                reasons.append(f"Personal expense keyword: {keyword}")
                break
        
        # Check suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.match(pattern, vendor_lower, re.IGNORECASE):
                risk_score += 20
                reasons.append("Suspicious vendor pattern detected")
                break
        
        # Check for missing GST (small local vendors)
        if self._is_small_local_vendor(vendor_name):
            risk_score += 15
            reasons.append("Small local vendor without GST")
        
        # Check vendor frequency in historical data
        if historical_data:
            freq_risk = self._check_vendor_frequency(vendor_name, historical_data)
            risk_score += freq_risk['score']
            reasons.extend(freq_risk['reasons'])
        
        # Check category mismatch
        category_mismatch = self._check_category_mismatch(vendor_name, category)
        if category_mismatch['score'] > 0:
            risk_score += category_mismatch['score']
            reasons.append(category_mismatch['reason'])
        
        return {
            "vendor_risk_score": min(risk_score, 100),
            "reasons": reasons
        }
    
    def _extract_numeric_amount(self, amount_str):
        """Extract numeric value from amount string"""
        if not amount_str:
            return 0.0
        try:
            cleaned = re.sub(r'[^\d.]', '', str(amount_str))
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def _is_small_local_vendor(self, vendor_name):
        """Identify small local vendors (heuristic)"""
        if not vendor_name:
            return False
            
        small_vendor_indicators = [
            'store', 'shop', 'local', 'corner', 'kirana',
            'vendor', 'merchant', 'trader'
        ]
        
        vendor_lower = vendor_name.lower()
        return any(indicator in vendor_lower for indicator in small_vendor_indicators)
    
    def _check_vendor_frequency(self, vendor_name, historical_data):
        """Check if vendor appears too frequently"""
        if not vendor_name or not historical_data:
            return {"score": 0, "reasons": []}
            
        vendor_count = 0
        for expense in historical_data:
            hist_vendor = expense.get('vendor', '')
            if hist_vendor and hist_vendor.lower() == vendor_name.lower():
                vendor_count += 1
        
        risk_score = 0
        reasons = []
        
        if vendor_count >= 5:
            risk_score = 30
            reasons.append(f"Vendor used {vendor_count} times recently")
        elif vendor_count >= 3:
            risk_score = 15
            reasons.append(f"Vendor used {vendor_count} times recently")
        
        return {"score": risk_score, "reasons": reasons}
    
    def _check_category_mismatch(self, vendor_name, category):
        """Check if vendor doesn't match category"""
        if not vendor_name or not category:
            return {"score": 0, "reason": ""}
            
        vendor_lower = vendor_name.lower()
        category_lower = category.lower()
        
        # Vendor to expected category mapping
        expected_categories = {
            'uber': 'travel', 'ola': 'travel', 'taxi': 'travel', 'cab': 'travel',
            'zomato': 'food', 'swiggy': 'food', 'restaurant': 'food', 'cafe': 'food',
            'hotel': 'travel', 'flight': 'travel', 'train': 'travel', 'airline': 'travel'
        }
        
        for vendor_key, expected_cat in expected_categories.items():
            if vendor_key in vendor_lower:
                if expected_cat not in category_lower:
                    return {
                        "score": 25,
                        "reason": f"Category mismatch: vendor suggests '{expected_cat}' but got '{category}'"
                    }
                break
        
        return {"score": 0, "reason": ""}