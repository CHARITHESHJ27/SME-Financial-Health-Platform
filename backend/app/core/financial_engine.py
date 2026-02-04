import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class FinancialAnalyzer:
    def __init__(self):
        self.risk_thresholds = {
            'current_ratio': {'low': 1.0, 'medium': 1.5, 'high': 2.0},
            'debt_to_asset_ratio': {'low': 0.3, 'medium': 0.6, 'high': 0.8},
            'profit_margin': {'low': 0.05, 'medium': 0.10, 'high': 0.15},
            'revenue_growth': {'low': 0.05, 'medium': 0.15, 'high': 0.25}
        }
    
    def calculate_ratios(self, data: Dict[str, float]) -> Dict[str, float]:
        """Calculate comprehensive financial ratios"""
        ratios = {}
        
        # Ensure all values are not None
        for key in data:
            if data[key] is None:
                data[key] = 0.0
        
        # Liquidity Ratios
        if data['current_liabilities'] > 0:
            ratios['current_ratio'] = data['current_assets'] / data['current_liabilities']
        else:
            ratios['current_ratio'] = float('inf')
        
        # Quick Ratio (assuming inventory is provided)
        inventory = data.get('inventory', 0) or 0
        quick_assets = data['current_assets'] - inventory
        if data['current_liabilities'] > 0:
            ratios['quick_ratio'] = quick_assets / data['current_liabilities']
        else:
            ratios['quick_ratio'] = float('inf')
        
        # Profitability Ratios
        if data['revenue'] > 0:
            ratios['profit_margin'] = (data['revenue'] - data['total_expenses']) / data['revenue']
            ratios['expense_ratio'] = data['total_expenses'] / data['revenue']
        else:
            ratios['profit_margin'] = 0
            ratios['expense_ratio'] = 0
        
        if data['total_assets'] > 0:
            ratios['roa'] = (data['revenue'] - data['total_expenses']) / data['total_assets']
        else:
            ratios['roa'] = 0
        
        # Leverage Ratios
        if data['total_assets'] > 0:
            ratios['debt_to_asset_ratio'] = data['total_debt'] / data['total_assets']
            ratios['equity_ratio'] = (data['total_assets'] - data['total_debt']) / data['total_assets']
        else:
            ratios['debt_to_asset_ratio'] = 0
            ratios['equity_ratio'] = 0
        
        # Efficiency Ratios
        accounts_receivable = data.get('accounts_receivable', 0) or 0
        if accounts_receivable > 0 and data['revenue'] > 0:
            ratios['receivables_turnover'] = data['revenue'] / accounts_receivable
            ratios['days_sales_outstanding'] = 365 / ratios['receivables_turnover']
        else:
            ratios['receivables_turnover'] = 0
            ratios['days_sales_outstanding'] = 0
        
        # Growth Ratios
        ratios['revenue_growth_rate'] = data.get('revenue_growth_rate', 0) or 0
        
        return ratios
    
    def assess_risks(self, data: Dict[str, float], ratios: Dict[str, float]) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        risks = []
        risk_score = 0
        
        # Liquidity Risk
        if ratios['current_ratio'] < self.risk_thresholds['current_ratio']['low']:
            risks.append("Low liquidity - Current ratio below 1.0")
            risk_score += 25
        elif ratios['current_ratio'] < self.risk_thresholds['current_ratio']['medium']:
            risks.append("Moderate liquidity concern")
            risk_score += 15
        
        # Leverage Risk
        if ratios['debt_to_asset_ratio'] > self.risk_thresholds['debt_to_asset_ratio']['high']:
            risks.append("High leverage - Debt to asset ratio above 80%")
            risk_score += 30
        elif ratios['debt_to_asset_ratio'] > self.risk_thresholds['debt_to_asset_ratio']['medium']:
            risks.append("Moderate leverage concern")
            risk_score += 20
        
        # Profitability Risk
        if ratios['profit_margin'] < 0:
            risks.append("Operating at a loss")
            risk_score += 35
        elif ratios['profit_margin'] < self.risk_thresholds['profit_margin']['low']:
            risks.append("Low profit margins")
            risk_score += 20
        
        # Growth Risk
        if ratios['revenue_growth_rate'] < 0:
            risks.append("Declining revenue")
            risk_score += 25
        elif ratios['revenue_growth_rate'] < self.risk_thresholds['revenue_growth']['low']:
            risks.append("Slow revenue growth")
            risk_score += 10
        
        # Cash Flow Risk
        if data.get('accounts_receivable', 0) > data['revenue'] * 0.25:
            risks.append("High accounts receivable - potential cash flow issues")
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        elif risk_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'identified_risks': risks,
            'risk_factors': {
                'liquidity_risk': ratios['current_ratio'] < 1.5,
                'leverage_risk': ratios['debt_to_asset_ratio'] > 0.6,
                'profitability_risk': ratios['profit_margin'] < 0.05,
                'growth_risk': ratios['revenue_growth_rate'] < 0.05
            }
        }
    
    def generate_recommendations(self, data: Dict[str, float], ratios: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Liquidity recommendations
        if ratios['current_ratio'] < 1.5:
            recommendations.append("Improve working capital management - consider invoice factoring or short-term credit facilities")
            recommendations.append("Accelerate accounts receivable collection")
        
        # Profitability recommendations
        if ratios['profit_margin'] < 0.10:
            recommendations.append("Review pricing strategy and cost structure")
            recommendations.append("Identify and eliminate non-essential expenses")
        
        # Leverage recommendations
        if ratios['debt_to_asset_ratio'] > 0.6:
            recommendations.append("Consider debt restructuring or equity financing")
            recommendations.append("Focus on debt reduction through improved cash flow")
        
        # Growth recommendations
        if ratios['revenue_growth_rate'] < 0.10:
            recommendations.append("Develop new revenue streams or market expansion strategies")
            recommendations.append("Invest in marketing and customer acquisition")
        
        # Efficiency recommendations
        if ratios.get('days_sales_outstanding', 0) > 45:
            recommendations.append("Implement stricter credit policies and collection procedures")
        
        return recommendations
    
    def identify_cost_savings(self, data: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify potential cost optimization opportunities"""
        cost_savings = []
        
        expense_ratio = data['total_expenses'] / data['revenue'] if data['revenue'] > 0 else 0
        
        if expense_ratio > 0.85:
            cost_savings.append({
                'category': 'Overall Cost Structure',
                'potential_savings': f"{(expense_ratio - 0.80) * data['revenue']:.0f}",
                'recommendation': 'Comprehensive cost audit and reduction program',
                'priority': 'HIGH'
            })
        
        # Industry-specific cost optimization
        cost_savings.append({
            'category': 'Technology & Automation',
            'potential_savings': f"{data['total_expenses'] * 0.05:.0f}",
            'recommendation': 'Implement automation tools to reduce manual processes',
            'priority': 'MEDIUM'
        })
        
        cost_savings.append({
            'category': 'Vendor Management',
            'potential_savings': f"{data['total_expenses'] * 0.03:.0f}",
            'recommendation': 'Renegotiate supplier contracts and consolidate vendors',
            'priority': 'MEDIUM'
        })
        
        return cost_savings
    
    def extract_financial_data(self, df: pd.DataFrame) -> Dict[str, float]:
        """Enhanced data extraction from uploaded files"""
        # Common column mappings
        column_mappings = {
            'revenue': ['Revenue', 'Sales', 'Income', 'Turnover'],
            'total_expenses': ['Expenses', 'Costs', 'Expenditure', 'Total Expenses'],
            'current_assets': ['Current Assets', 'Current_Assets'],
            'current_liabilities': ['Current Liabilities', 'Current_Liabilities'],
            'total_assets': ['Total Assets', 'Total_Assets'],
            'total_debt': ['Total Debt', 'Total_Debt', 'Liabilities']
        }
        
        extracted_data = {}
        
        for key, possible_columns in column_mappings.items():
            for col in possible_columns:
                if col in df.columns:
                    if key in ['revenue', 'total_expenses']:
                        extracted_data[key] = float(df[col].sum())
                    else:
                        extracted_data[key] = float(df[col].iloc[-1]) if len(df) > 0 else 0.0
                    break
            else:
                extracted_data[key] = 0.0
        
        # Set defaults for optional fields
        extracted_data['revenue_growth_rate'] = 0.0
        extracted_data['inventory'] = 0.0
        extracted_data['accounts_receivable'] = 0.0
        extracted_data['accounts_payable'] = 0.0
        
        return extracted_data
    
    def assess_data_quality(self, df: pd.DataFrame) -> float:
        """Assess the quality of uploaded financial data"""
        quality_score = 100
        
        # Check for missing values
        missing_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns))
        quality_score -= missing_percentage * 30
        
        # Check for data consistency
        if len(df) < 3:
            quality_score -= 20
        
        # Check for required columns
        required_columns = ['Revenue', 'Expenses']
        missing_required = sum(1 for col in required_columns if col not in df.columns)
        quality_score -= missing_required * 25
        
        return max(0, quality_score)
    
    def generate_forecast(self, historical_assessments: List, months: int) -> Dict[str, Any]:
        """Generate financial forecasting based on historical data"""
        if len(historical_assessments) < 3:
            return {"error": "Insufficient data for forecasting"}
        
        # Extract historical trends
        scores = [assessment.overall_health_score for assessment in historical_assessments]
        dates = [assessment.assessment_date for assessment in historical_assessments]
        
        # Simple trend analysis
        if len(scores) >= 2:
            trend = (scores[0] - scores[-1]) / len(scores)
        else:
            trend = 0
        
        # Generate forecast
        forecast_data = []
        current_score = scores[0]
        
        for i in range(months):
            future_date = datetime.now() + timedelta(days=30 * (i + 1))
            projected_score = max(0, min(100, current_score + (trend * (i + 1))))
            
            forecast_data.append({
                'month': future_date.strftime('%Y-%m'),
                'projected_health_score': round(projected_score, 1),
                'confidence_level': max(0.5, 0.9 - (i * 0.05))  # Decreasing confidence over time
            })
        
        return {
            'forecast_period': f"{months} months",
            'trend_direction': "improving" if trend > 0 else "declining" if trend < 0 else "stable",
            'forecast_data': forecast_data,
            'methodology': "Trend-based projection with historical performance analysis"
        }
    
    def extract_from_pdf_text(self, text: str) -> Dict[str, float]:
        """Extract financial data from PDF text"""
        import re
        
        # Simple regex patterns for common financial terms
        patterns = {
            'revenue': r'(?:revenue|sales|income)\s*:?\s*([\d,]+)',
            'expenses': r'(?:expenses|costs)\s*:?\s*([\d,]+)',
            'assets': r'(?:total\s*assets)\s*:?\s*([\d,]+)',
            'liabilities': r'(?:liabilities)\s*:?\s*([\d,]+)'
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).replace(',', '')
                extracted[key] = float(value) if value.isdigit() else 0
            else:
                extracted[key] = 0
        
        return {
            'revenue': extracted.get('revenue', 0),
            'total_expenses': extracted.get('expenses', 0),
            'total_assets': extracted.get('assets', 0),
            'total_debt': extracted.get('liabilities', 0),
            'current_assets': extracted.get('assets', 0) * 0.4,
            'current_liabilities': extracted.get('liabilities', 0) * 0.6
        }