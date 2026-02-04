from typing import Dict, List, Any
from datetime import datetime, timedelta
import random

class BankingAPIMock:
    """Mock banking API service for demonstration"""
    
    def __init__(self):
        self.mock_accounts = {
            "ACC001": {
                "account_number": "ACC001",
                "bank_name": "HDFC Bank",
                "account_type": "Current",
                "balance": 2500000,
                "currency": "INR"
            },
            "ACC002": {
                "account_number": "ACC002", 
                "bank_name": "ICICI Bank",
                "account_type": "Savings",
                "balance": 850000,
                "currency": "INR"
            }
        }
    
    def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """Get current account balance"""
        if account_id in self.mock_accounts:
            account = self.mock_accounts[account_id]
            return {
                "account_id": account_id,
                "balance": account["balance"],
                "currency": account["currency"],
                "last_updated": datetime.now().isoformat()
            }
        return {"error": "Account not found"}
    
    def get_transaction_history(self, account_id: str, days: int = 30) -> Dict[str, Any]:
        """Get transaction history for specified period"""
        if account_id not in self.mock_accounts:
            return {"error": "Account not found"}
        
        transactions = []
        for i in range(random.randint(10, 50)):
            transaction_date = datetime.now() - timedelta(days=random.randint(0, days))
            amount = random.uniform(-50000, 100000)
            
            transactions.append({
                "transaction_id": f"TXN{i+1:04d}",
                "date": transaction_date.isoformat(),
                "amount": round(amount, 2),
                "type": "credit" if amount > 0 else "debit",
                "description": random.choice([
                    "Customer Payment", "Supplier Payment", "Salary Payment",
                    "Utility Bill", "Loan EMI", "Tax Payment", "Sales Receipt"
                ]),
                "balance_after": self.mock_accounts[account_id]["balance"] + amount
            })
        
        return {
            "account_id": account_id,
            "period_days": days,
            "transaction_count": len(transactions),
            "transactions": sorted(transactions, key=lambda x: x["date"], reverse=True)
        }
    
    def get_cash_flow_analysis(self, account_id: str, months: int = 6) -> Dict[str, Any]:
        """Analyze cash flow patterns"""
        if account_id not in self.mock_accounts:
            return {"error": "Account not found"}
        
        monthly_data = []
        for i in range(months):
            month_date = datetime.now() - timedelta(days=30 * i)
            inflow = random.uniform(500000, 1500000)
            outflow = random.uniform(400000, 1200000)
            
            monthly_data.append({
                "month": month_date.strftime("%Y-%m"),
                "total_inflow": round(inflow, 2),
                "total_outflow": round(outflow, 2),
                "net_flow": round(inflow - outflow, 2),
                "transaction_count": random.randint(50, 150)
            })
        
        # Calculate averages
        avg_inflow = sum(m["total_inflow"] for m in monthly_data) / len(monthly_data)
        avg_outflow = sum(m["total_outflow"] for m in monthly_data) / len(monthly_data)
        
        return {
            "account_id": account_id,
            "analysis_period": f"{months} months",
            "monthly_data": monthly_data[::-1],  # Chronological order
            "summary": {
                "average_monthly_inflow": round(avg_inflow, 2),
                "average_monthly_outflow": round(avg_outflow, 2),
                "average_net_flow": round(avg_inflow - avg_outflow, 2),
                "cash_flow_volatility": random.uniform(0.1, 0.4)
            }
        }

class PaymentAPIMock:
    """Mock payment gateway API for transaction analysis"""
    
    def get_payment_analytics(self, merchant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get payment analytics for merchant"""
        
        # Generate mock payment data
        total_transactions = random.randint(100, 500)
        total_amount = random.uniform(1000000, 5000000)
        success_rate = random.uniform(0.85, 0.98)
        
        payment_methods = {
            "UPI": random.uniform(0.4, 0.6),
            "Cards": random.uniform(0.2, 0.4),
            "Net Banking": random.uniform(0.1, 0.2),
            "Wallets": random.uniform(0.05, 0.15)
        }
        
        return {
            "merchant_id": merchant_id,
            "period_days": days,
            "summary": {
                "total_transactions": total_transactions,
                "total_amount": round(total_amount, 2),
                "success_rate": round(success_rate, 3),
                "average_transaction_value": round(total_amount / total_transactions, 2),
                "failed_transactions": int(total_transactions * (1 - success_rate))
            },
            "payment_methods": payment_methods,
            "trends": {
                "growth_rate": random.uniform(-0.1, 0.3),
                "seasonal_factor": random.uniform(0.8, 1.2)
            }
        }