import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

class GSTMockService:
    """Mock GST service for demonstration purposes"""
    
    def __init__(self):
        self.mock_data = {
            "27AABCU9603R1ZX": {
                "business_name": "Tech Solutions Pvt Ltd",
                "registration_date": "2020-04-01",
                "status": "Active",
                "returns_filed": 36,
                "compliance_score": 85
            },
            "29AABCU9603R1ZY": {
                "business_name": "Retail Mart Enterprises",
                "registration_date": "2019-07-15",
                "status": "Active",
                "returns_filed": 42,
                "compliance_score": 92
            }
        }
    
    def get_gst_compliance_data(self, gst_number: str) -> Dict[str, Any]:
        """Get GST compliance data for a business"""
        
        if gst_number in self.mock_data:
            base_data = self.mock_data[gst_number]
        else:
            # Generate mock data for unknown GST numbers
            base_data = {
                "business_name": f"Business {gst_number[-4:]}",
                "registration_date": "2021-01-01",
                "status": "Active",
                "returns_filed": random.randint(12, 48),
                "compliance_score": random.randint(70, 95)
            }
        
        # Generate recent returns data
        returns_data = self._generate_returns_data(base_data["returns_filed"])
        
        return {
            "gst_number": gst_number,
            "business_details": base_data,
            "compliance_summary": {
                "overall_score": base_data["compliance_score"],
                "returns_filed_on_time": returns_data["on_time_filings"],
                "total_returns_due": returns_data["total_due"],
                "pending_returns": returns_data["pending"],
                "last_filing_date": returns_data["last_filing"]
            },
            "tax_summary": self._generate_tax_summary(),
            "compliance_issues": self._generate_compliance_issues(base_data["compliance_score"]),
            "recommendations": self._generate_tax_recommendations(base_data["compliance_score"])
        }
    
    def get_gst_returns_summary(self, gst_number: str, period_months: int = 12) -> Dict[str, Any]:
        """Get GST returns summary for specified period"""
        
        monthly_data = []
        total_sales = 0
        total_tax_paid = 0
        
        for i in range(period_months):
            month_date = datetime.now() - timedelta(days=30 * i)
            monthly_sales = random.uniform(500000, 2000000)  # Random sales between 5L to 20L
            tax_rate = 0.18  # 18% GST
            monthly_tax = monthly_sales * tax_rate
            
            total_sales += monthly_sales
            total_tax_paid += monthly_tax
            
            monthly_data.append({
                "month": month_date.strftime("%Y-%m"),
                "sales_value": round(monthly_sales, 2),
                "tax_liability": round(monthly_tax, 2),
                "input_tax_credit": round(monthly_tax * 0.7, 2),  # 70% ITC
                "net_tax_paid": round(monthly_tax * 0.3, 2),
                "filing_status": "Filed" if random.random() > 0.1 else "Pending"
            })
        
        return {
            "gst_number": gst_number,
            "period": f"Last {period_months} months",
            "summary": {
                "total_sales": round(total_sales, 2),
                "total_tax_liability": round(total_tax_paid, 2),
                "total_itc_claimed": round(total_tax_paid * 0.7, 2),
                "net_tax_paid": round(total_tax_paid * 0.3, 2),
                "average_monthly_sales": round(total_sales / period_months, 2)
            },
            "monthly_data": monthly_data[::-1],  # Reverse to show chronological order
            "compliance_metrics": {
                "on_time_filing_rate": random.randint(85, 98),
                "itc_utilization_rate": random.randint(65, 85),
                "tax_payment_punctuality": random.randint(80, 95)
            }
        }
    
    def validate_gst_number(self, gst_number: str) -> Dict[str, Any]:
        """Validate GST number format and status"""
        
        # Basic GST number format validation
        if not gst_number or len(gst_number) != 15:
            return {
                "valid": False,
                "error": "GST number must be 15 characters long"
            }
        
        # Check if it follows GST format (simplified)
        if not gst_number[:2].isdigit() or not gst_number[2:12].isalnum():
            return {
                "valid": False,
                "error": "Invalid GST number format"
            }
        
        # Mock validation - assume all properly formatted numbers are valid
        return {
            "valid": True,
            "status": "Active",
            "registration_date": "2020-01-01",
            "business_name": f"Business {gst_number[-4:]}",
            "business_type": random.choice(["Private Limited", "Partnership", "Proprietorship", "LLP"])
        }
    
    def get_tax_optimization_suggestions(self, gst_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tax optimization suggestions based on GST data"""
        
        suggestions = []
        
        compliance_score = gst_data.get("compliance_summary", {}).get("overall_score", 80)
        
        if compliance_score < 90:
            suggestions.append({
                "category": "Compliance Improvement",
                "suggestion": "Set up automated GST return filing to improve compliance score",
                "potential_benefit": "Avoid penalties and improve credit rating",
                "priority": "High"
            })
        
        suggestions.extend([
            {
                "category": "Input Tax Credit",
                "suggestion": "Review and claim all eligible ITC to reduce tax liability",
                "potential_benefit": "5-10% reduction in effective tax rate",
                "priority": "Medium"
            },
            {
                "category": "Invoice Management",
                "suggestion": "Implement digital invoice management system for better tracking",
                "potential_benefit": "Improved accuracy and faster processing",
                "priority": "Medium"
            },
            {
                "category": "Tax Planning",
                "suggestion": "Plan purchases and sales timing for optimal tax benefits",
                "potential_benefit": "Better cash flow management",
                "priority": "Low"
            }
        ])
        
        return suggestions
    
    def _generate_returns_data(self, total_filed: int) -> Dict[str, Any]:
        """Generate mock returns filing data"""
        total_due = total_filed + random.randint(0, 3)
        on_time = max(0, total_filed - random.randint(0, 5))
        
        return {
            "total_due": total_due,
            "on_time_filings": on_time,
            "pending": total_due - total_filed,
            "last_filing": (datetime.now() - timedelta(days=random.randint(1, 45))).strftime("%Y-%m-%d")
        }
    
    def _generate_tax_summary(self) -> Dict[str, float]:
        """Generate mock tax summary"""
        annual_turnover = random.uniform(5000000, 50000000)  # 50L to 5Cr
        
        return {
            "annual_turnover": round(annual_turnover, 2),
            "total_tax_liability": round(annual_turnover * 0.18, 2),
            "input_tax_credit": round(annual_turnover * 0.18 * 0.7, 2),
            "net_tax_paid": round(annual_turnover * 0.18 * 0.3, 2),
            "effective_tax_rate": round(5.4, 2)  # 18% * 30%
        }
    
    def _generate_compliance_issues(self, compliance_score: int) -> List[str]:
        """Generate compliance issues based on score"""
        issues = []
        
        if compliance_score < 95:
            potential_issues = [
                "Late filing of GSTR-1 for 2 months",
                "Mismatch in GSTR-2A and GSTR-3B",
                "Pending payment of interest on delayed filing",
                "Incomplete input tax credit reconciliation",
                "Missing e-way bills for interstate transactions"
            ]
            
            num_issues = max(0, (95 - compliance_score) // 10)
            issues = random.sample(potential_issues, min(num_issues, len(potential_issues)))
        
        return issues
    
    def _generate_tax_recommendations(self, compliance_score: int) -> List[str]:
        """Generate tax recommendations based on compliance"""
        recommendations = [
            "Set up automated GST return filing system",
            "Regular reconciliation of books with GST returns",
            "Maintain proper documentation for all transactions"
        ]
        
        if compliance_score < 85:
            recommendations.extend([
                "Engage a tax consultant for compliance review",
                "Implement GST-compliant accounting software",
                "Regular training for accounts team on GST updates"
            ])
        
        return recommendations