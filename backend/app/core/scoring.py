import numpy as np
from typing import Dict, Any, List

class CreditScorer:
    def __init__(self):
        # Scoring weights for different financial aspects
        self.weights = {
            'liquidity': 0.25,
            'profitability': 0.30,
            'leverage': 0.25,
            'efficiency': 0.10,
            'growth': 0.10
        }
        
        # Industry-specific adjustments
        self.industry_adjustments = {
            'manufacturing': {'leverage': 0.05, 'efficiency': 0.05},
            'retail': {'liquidity': 0.05, 'efficiency': 0.05},
            'services': {'profitability': 0.05, 'growth': 0.05},
            'agriculture': {'growth': -0.05, 'leverage': 0.05},
            'logistics': {'efficiency': 0.10, 'leverage': -0.05},
            'e-commerce': {'growth': 0.10, 'liquidity': -0.05}
        }
    
    def calculate_credit_score(self, financial_data: Dict[str, float], ratios: Dict[str, float]) -> float:
        """Calculate comprehensive credit score (0-100)"""
        
        # Individual component scores
        liquidity_score = self._score_liquidity(ratios)
        profitability_score = self._score_profitability(ratios)
        leverage_score = self._score_leverage(ratios)
        efficiency_score = self._score_efficiency(ratios)
        growth_score = self._score_growth(ratios)
        
        # Apply industry adjustments
        industry = financial_data.get('industry', 'services').lower()
        adjusted_weights = self._adjust_weights_for_industry(industry)
        
        # Calculate weighted score
        credit_score = (
            liquidity_score * adjusted_weights['liquidity'] +
            profitability_score * adjusted_weights['profitability'] +
            leverage_score * adjusted_weights['leverage'] +
            efficiency_score * adjusted_weights['efficiency'] +
            growth_score * adjusted_weights['growth']
        )
        
        # Apply business size adjustment
        size_adjustment = self._get_size_adjustment(financial_data['revenue'])
        credit_score += size_adjustment
        
        # Ensure score is within bounds
        return max(0, min(100, credit_score))
    
    def _score_liquidity(self, ratios: Dict[str, float]) -> float:
        """Score liquidity metrics (0-100)"""
        current_ratio = ratios.get('current_ratio', 0)
        quick_ratio = ratios.get('quick_ratio', 0)
        
        # Current ratio scoring
        if current_ratio >= 2.0:
            current_score = 100
        elif current_ratio >= 1.5:
            current_score = 80
        elif current_ratio >= 1.0:
            current_score = 60
        elif current_ratio >= 0.8:
            current_score = 40
        else:
            current_score = 20
        
        # Quick ratio scoring
        if quick_ratio >= 1.5:
            quick_score = 100
        elif quick_ratio >= 1.0:
            quick_score = 80
        elif quick_ratio >= 0.8:
            quick_score = 60
        elif quick_ratio >= 0.5:
            quick_score = 40
        else:
            quick_score = 20
        
        return (current_score * 0.6 + quick_score * 0.4)
    
    def _score_profitability(self, ratios: Dict[str, float]) -> float:
        """Score profitability metrics (0-100)"""
        profit_margin = ratios.get('profit_margin', 0)
        roa = ratios.get('roa', 0)
        
        # Profit margin scoring
        if profit_margin >= 0.20:
            margin_score = 100
        elif profit_margin >= 0.15:
            margin_score = 85
        elif profit_margin >= 0.10:
            margin_score = 70
        elif profit_margin >= 0.05:
            margin_score = 55
        elif profit_margin >= 0:
            margin_score = 40
        else:
            margin_score = 10
        
        # ROA scoring
        if roa >= 0.15:
            roa_score = 100
        elif roa >= 0.10:
            roa_score = 80
        elif roa >= 0.05:
            roa_score = 60
        elif roa >= 0:
            roa_score = 40
        else:
            roa_score = 10
        
        return (margin_score * 0.7 + roa_score * 0.3)
    
    def _score_leverage(self, ratios: Dict[str, float]) -> float:
        """Score leverage metrics (0-100) - lower debt is better"""
        debt_to_asset = ratios.get('debt_to_asset_ratio', 0)
        equity_ratio = ratios.get('equity_ratio', 1)
        
        # Debt to asset scoring (inverted - lower is better)
        if debt_to_asset <= 0.20:
            debt_score = 100
        elif debt_to_asset <= 0.40:
            debt_score = 80
        elif debt_to_asset <= 0.60:
            debt_score = 60
        elif debt_to_asset <= 0.80:
            debt_score = 40
        else:
            debt_score = 20
        
        # Equity ratio scoring
        if equity_ratio >= 0.80:
            equity_score = 100
        elif equity_ratio >= 0.60:
            equity_score = 80
        elif equity_ratio >= 0.40:
            equity_score = 60
        elif equity_ratio >= 0.20:
            equity_score = 40
        else:
            equity_score = 20
        
        return (debt_score * 0.6 + equity_score * 0.4)
    
    def _score_efficiency(self, ratios: Dict[str, float]) -> float:
        """Score efficiency metrics (0-100)"""
        receivables_turnover = ratios.get('receivables_turnover', 0)
        days_sales_outstanding = ratios.get('days_sales_outstanding', 365)
        
        # Receivables turnover scoring
        if receivables_turnover >= 12:  # Monthly collection
            turnover_score = 100
        elif receivables_turnover >= 8:
            turnover_score = 80
        elif receivables_turnover >= 6:
            turnover_score = 60
        elif receivables_turnover >= 4:
            turnover_score = 40
        else:
            turnover_score = 20
        
        # Days sales outstanding scoring (inverted - lower is better)
        if days_sales_outstanding <= 30:
            dso_score = 100
        elif days_sales_outstanding <= 45:
            dso_score = 80
        elif days_sales_outstanding <= 60:
            dso_score = 60
        elif days_sales_outstanding <= 90:
            dso_score = 40
        else:
            dso_score = 20
        
        return (turnover_score * 0.5 + dso_score * 0.5)
    
    def _score_growth(self, ratios: Dict[str, float]) -> float:
        """Score growth metrics (0-100)"""
        revenue_growth = ratios.get('revenue_growth_rate', 0)
        
        if revenue_growth >= 0.30:
            return 100
        elif revenue_growth >= 0.20:
            return 85
        elif revenue_growth >= 0.15:
            return 70
        elif revenue_growth >= 0.10:
            return 60
        elif revenue_growth >= 0.05:
            return 50
        elif revenue_growth >= 0:
            return 40
        elif revenue_growth >= -0.05:
            return 30
        elif revenue_growth >= -0.10:
            return 20
        else:
            return 10
    
    def _adjust_weights_for_industry(self, industry: str) -> Dict[str, float]:
        """Adjust scoring weights based on industry"""
        adjusted_weights = self.weights.copy()
        
        if industry in self.industry_adjustments:
            adjustments = self.industry_adjustments[industry]
            for metric, adjustment in adjustments.items():
                adjusted_weights[metric] += adjustment
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        for key in adjusted_weights:
            adjusted_weights[key] /= total_weight
        
        return adjusted_weights
    
    def _get_size_adjustment(self, revenue: float) -> float:
        """Apply size-based adjustment to credit score"""
        # Larger businesses typically have more stability
        if revenue >= 10000000:  # 1 crore+
            return 5
        elif revenue >= 5000000:  # 50 lakh+
            return 3
        elif revenue >= 1000000:  # 10 lakh+
            return 1
        else:
            return 0
    
    def get_credit_rating(self, credit_score: float) -> str:
        """Convert credit score to rating"""
        if credit_score >= 90:
            return "AAA"
        elif credit_score >= 80:
            return "AA"
        elif credit_score >= 70:
            return "A"
        elif credit_score >= 60:
            return "BBB"
        elif credit_score >= 50:
            return "BB"
        elif credit_score >= 40:
            return "B"
        elif credit_score >= 30:
            return "CCC"
        else:
            return "D"
    
    def get_recommended_products(self, credit_score: float, industry: str) -> List[Dict[str, Any]]:
        """Recommend financial products based on credit score"""
        products = []
        
        if credit_score >= 70:
            products.extend([
                {
                    "product": "Term Loan",
                    "interest_rate": "8.5-10.5%",
                    "max_amount": "Up to 5 Crores",
                    "tenure": "1-7 years"
                },
                {
                    "product": "Working Capital Loan",
                    "interest_rate": "9.0-11.0%",
                    "max_amount": "Up to 2 Crores",
                    "tenure": "12 months"
                }
            ])
        elif credit_score >= 50:
            products.extend([
                {
                    "product": "MSME Loan",
                    "interest_rate": "10.0-12.0%",
                    "max_amount": "Up to 1 Crore",
                    "tenure": "1-5 years"
                },
                {
                    "product": "Invoice Financing",
                    "interest_rate": "12.0-15.0%",
                    "max_amount": "Up to 50 Lakhs",
                    "tenure": "30-90 days"
                }
            ])
        else:
            products.extend([
                {
                    "product": "Secured Business Loan",
                    "interest_rate": "12.0-16.0%",
                    "max_amount": "Up to 25 Lakhs",
                    "tenure": "1-3 years"
                },
                {
                    "product": "Merchant Cash Advance",
                    "interest_rate": "15.0-20.0%",
                    "max_amount": "Up to 10 Lakhs",
                    "tenure": "3-12 months"
                }
            ])
        
        return products