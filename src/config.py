import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AgentConfig:
    name: str
    role: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1

@dataclass
class ExpenseConfig:
    categories: List[str] = None
    thresholds: Dict[str, float] = None
    high_risk_merchants: List[str] = None
    risky_locations: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = ["Travel", "Meals", "Entertainment", "Supplies", "Software", "Other"]
        if self.thresholds is None:
            self.thresholds = {
                "Travel": 1000, 
                "Meals": 100, 
                "Entertainment": 200,
                "Supplies": 500,
                "Software": 1000,
                "Other": 300
            }
        if self.high_risk_merchants is None:
            self.high_risk_merchants = [
                "Casino", "Gambling", "Adult Entertainment", 
                "Liquor Store", "Night Club", "Massage Parlor"
            ]
        if self.risky_locations is None:
            self.risky_locations = [
                "Las Vegas", "Macau", "Monte Carlo", "Atlantic City"
            ]

class Config:
    AGENTS = {
        "policy_agent": AgentConfig("Policy Agent", "Validate expenses against company policies"),
        "fraud_agent": AgentConfig("Fraud Detection Agent", "Detect suspicious patterns and anomalies"),
        "audit_agent": AgentConfig("Audit Agent", "Conduct detailed expense audits"),
        "reporting_agent": AgentConfig("Reporting Agent", "Generate compliance reports")
    }
    
    EXPENSE = ExpenseConfig()
    MEMORY_SIZE = 1000
    SIMILARITY_THRESHOLD = 0.8
    
    # Database configuration
    DATABASE_CONFIG = {
        'host': 'localhost',
        'database': 'expense_audit',
        'user': 'username',
        'password': 'password'
    }