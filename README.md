# 🏢 Enterprise Expense Audit System

A comprehensive multi-agent system for expense auditing and fraud detection.

## 🎯 Project Overview

### Member 1B - Field Extraction Agent
- Extracts structured data from raw receipts
- Uses regex and pattern matching
- Converts free text → organized JSON

### P2-C - Advanced Fraud Detection
- **Duplicate Receipt Detection**: vendor + amount + date matching
- **Vendor Risk Engine**: Identifies high-risk vendors
- **Behavior Analyzer**: Detects suspicious patterns
- **Fraud Score Calculator**: Combines multiple risk factors

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/ArchithaKurukkanari/EnterpriseExpenseAudit.git

# Install dependencies
pip install -r requirements.txt

# Run the system
python main.py

# Run tests
python test_integration.py
python test_fraud_patterns.py
