import json
import pandas as pd
from typing import Dict, Any, List

class IndustryBenchmarks:
    def __init__(self):
        # Industry benchmark data (normally loaded from database/file)
        self.benchmarks = {
            'manufacturing': {
                'current_ratio': {'median': 1.8, 'q1': 1.2, 'q3': 2.5},
                'profit_margin': {'median': 0.12, 'q1': 0.08, 'q3': 0.18},
                'debt_to_asset_ratio': {'median': 0.45, 'q1': 0.30, 'q3': 0.60},
                'revenue_growth_rate': {'median': 0.08, 'q1': 0.03, 'q3': 0.15},
                'days_sales_outstanding': {'median': 45, 'q1': 30, 'q3': 60}
            },
            'retail': {
                'current_ratio': {'median': 1.5, 'q1': 1.0, 'q3': 2.2},
                'profit_margin': {'median': 0.08, 'q1': 0.04, 'q3': 0.12},
                'debt_to_asset_ratio': {'median': 0.50, 'q1': 0.35, 'q3': 0.65},
                'revenue_growth_rate': {'median': 0.06, 'q1': 0.02, 'q3': 0.12},
                'days_sales_outstanding': {'median': 15, 'q1': 10, 'q3': 25}
            },
            'services': {
                'current_ratio': {'median': 2.0, 'q1': 1.3, 'q3': 3.0},
                'profit_margin': {'median': 0.15, 'q1': 0.10, 'q3': 0.22},
                'debt_to_asset_ratio': {'median': 0.35, 'q1': 0.20, 'q3': 0.50},
                'revenue_growth_rate': {'median': 0.12, 'q1': 0.05, 'q3': 0.20},
                'days_sales_outstanding': {'median': 35, 'q1': 25, 'q3': 50}
            },
            'agriculture': {
                'current_ratio': {'median': 1.6, 'q1': 1.1, 'q3': 2.3},
                'profit_margin': {'median': 0.10, 'q1': 0.05, 'q3': 0.16},
                'debt_to_asset_ratio': {'median': 0.55, 'q1': 0.40, 'q3': 0.70},
                'revenue_growth_rate': {'median': 0.04, 'q1': -0.02, 'q3': 0.10},
                'days_sales_outstanding': {'median': 30, 'q1': 20, 'q3': 45}
            },
            'logistics': {
                'current_ratio': {'median': 1.4, 'q1': 1.0, 'q3': 1.9},
                'profit_margin': {'median': 0.06, 'q1': 0.03, 'q3': 0.10},
                'debt_to_asset_ratio': {'median': 0.60, 'q1': 0.45, 'q3': 0.75},
                'revenue_growth_rate': {'median': 0.10, 'q1': 0.04, 'q3': 0.18},
                'days_sales_outstanding': {'median': 40, 'q1': 30, 'q3': 55}
            },
            'e-commerce': {
                'current_ratio': {'median': 1.3, 'q1': 0.9, 'q3': 1.8},
                'profit_margin': {'median': 0.05, 'q1': 0.01, 'q3': 0.12},
                'debt_to_asset_ratio': {'median': 0.40, 'q1': 0.25, 'q3': 0.55},
                'revenue_growth_rate': {'median': 0.25, 'q1': 0.10, 'q3': 0.45},
                'days_sales_outstanding': {'median': 20, 'q1': 15, 'q3': 30}
            }
        }
        
        # Industry-specific KPIs
        self.industry_kpis = {
            'manufacturing': ['inventory_turnover', 'asset_turnover', 'capacity_utilization'],
            'retail': ['inventory_turnover', 'sales_per_sqft', 'customer_acquisition_cost'],
            'services': ['utilization_rate', 'customer_retention', 'revenue_per_employee'],
            'agriculture': ['yield_per_acre', 'seasonal_variance', 'weather_dependency'],
            'logistics': ['fleet_utilization', 'delivery_efficiency', 'fuel_cost_ratio'],
            'e-commerce': ['conversion_rate', 'customer_lifetime_value', 'cart_abandonment_rate']
        }
    
    def compare_with_industry(self, industry: str, company_ratios: Dict[str, float]) -> Dict[str, Any]:
        """Compare company metrics with industry benchmarks"""
        industry_lower = industry.lower()
        
        if industry_lower not in self.benchmarks:
            industry_lower = 'services'  # Default fallback
        
        industry_data = self.benchmarks[industry_lower]
        comparison_results = {}
        
        for metric, company_value in company_ratios.items():
            if metric in industry_data:
                benchmark = industry_data[metric]
                percentile = self._calculate_percentile(company_value, benchmark)
                
                comparison_results[metric] = {
                    'company_value': company_value,
                    'industry_median': benchmark['median'],
                    'industry_q1': benchmark['q1'],
                    'industry_q3': benchmark['q3'],
                    'percentile': percentile,
                    'performance': self._get_performance_rating(percentile),
                    'comparison_text': self._generate_comparison_text(metric, percentile, company_value, benchmark)
                }
        
        # Overall industry comparison summary
        avg_percentile = sum(result['percentile'] for result in comparison_results.values()) / len(comparison_results)
        
        return {
            'industry': industry,
            'overall_percentile': avg_percentile,
            'overall_performance': self._get_performance_rating(avg_percentile),
            'metric_comparisons': comparison_results,
            'industry_insights': self._generate_industry_insights(industry_lower, avg_percentile),
            'recommended_focus_areas': self._get_focus_areas(comparison_results)
        }
    
    def _calculate_percentile(self, value: float, benchmark: Dict[str, float]) -> float:
        """Calculate percentile ranking against industry benchmark"""
        q1, median, q3 = benchmark['q1'], benchmark['median'], benchmark['q3']
        
        if value <= q1:
            return 25 * (value / q1) if q1 > 0 else 0
        elif value <= median:
            return 25 + 25 * ((value - q1) / (median - q1)) if median > q1 else 25
        elif value <= q3:
            return 50 + 25 * ((value - median) / (q3 - median)) if q3 > median else 50
        else:
            return min(100, 75 + 25 * ((value - q3) / q3)) if q3 > 0 else 75
    
    def _get_performance_rating(self, percentile: float) -> str:
        """Convert percentile to performance rating"""
        if percentile >= 75:
            return "Excellent"
        elif percentile >= 50:
            return "Above Average"
        elif percentile >= 25:
            return "Below Average"
        else:
            return "Poor"
    
    def _generate_comparison_text(self, metric: str, percentile: float, company_value: float, benchmark: Dict[str, float]) -> str:
        """Generate human-readable comparison text"""
        performance = self._get_performance_rating(percentile)
        median = benchmark['median']
        
        metric_names = {
            'current_ratio': 'Current Ratio',
            'profit_margin': 'Profit Margin',
            'debt_to_asset_ratio': 'Debt-to-Asset Ratio',
            'revenue_growth_rate': 'Revenue Growth Rate',
            'days_sales_outstanding': 'Days Sales Outstanding'
        }
        
        metric_name = metric_names.get(metric, metric.replace('_', ' ').title())
        
        if percentile >= 75:
            return f"Your {metric_name} of {company_value:.2f} is excellent, ranking in the top 25% of {metric_name.lower()} performers in your industry."
        elif percentile >= 50:
            return f"Your {metric_name} of {company_value:.2f} is above the industry median of {median:.2f}."
        elif percentile >= 25:
            return f"Your {metric_name} of {company_value:.2f} is below the industry median of {median:.2f} and needs improvement."
        else:
            return f"Your {metric_name} of {company_value:.2f} is significantly below industry standards and requires immediate attention."
    
    def _generate_industry_insights(self, industry: str, avg_percentile: float) -> List[str]:
        """Generate industry-specific insights"""
        insights = []
        
        industry_characteristics = {
            'manufacturing': [
                "Manufacturing businesses typically require higher working capital",
                "Focus on inventory management and production efficiency",
                "Asset utilization is crucial for profitability"
            ],
            'retail': [
                "Retail businesses have seasonal variations in performance",
                "Inventory turnover is a key success metric",
                "Location and customer experience drive revenue"
            ],
            'services': [
                "Service businesses typically have higher profit margins",
                "Human capital is the primary asset",
                "Scalability depends on process optimization"
            ],
            'agriculture': [
                "Agricultural businesses face weather and commodity price risks",
                "Seasonal cash flow patterns are normal",
                "Government policies significantly impact profitability"
            ],
            'logistics': [
                "Logistics businesses are capital intensive",
                "Fuel costs and route optimization are critical",
                "Technology adoption drives efficiency gains"
            ],
            'e-commerce': [
                "E-commerce businesses prioritize growth over immediate profitability",
                "Customer acquisition costs are typically high initially",
                "Technology and marketing investments are essential"
            ]
        }
        
        base_insights = industry_characteristics.get(industry, [])
        insights.extend(base_insights)
        
        if avg_percentile >= 75:
            insights.append("Your business is performing exceptionally well compared to industry peers.")
        elif avg_percentile >= 50:
            insights.append("Your business performance is solid with room for optimization.")
        else:
            insights.append("Consider industry best practices to improve your competitive position.")
        
        return insights
    
    def _get_focus_areas(self, comparison_results: Dict[str, Any]) -> List[str]:
        """Identify areas that need focus based on industry comparison"""
        focus_areas = []
        
        for metric, result in comparison_results.items():
            if result['percentile'] < 25:
                metric_focus = {
                    'current_ratio': 'Improve working capital management',
                    'profit_margin': 'Optimize cost structure and pricing',
                    'debt_to_asset_ratio': 'Reduce debt levels or increase assets',
                    'revenue_growth_rate': 'Develop growth strategies',
                    'days_sales_outstanding': 'Improve collections and credit policies'
                }
                
                if metric in metric_focus:
                    focus_areas.append(metric_focus[metric])
        
        return focus_areas
    
    def get_industry_benchmarks(self, industry: str) -> Dict[str, Any]:
        """Get complete benchmark data for an industry"""
        industry_lower = industry.lower()
        
        if industry_lower not in self.benchmarks:
            return {"error": f"Benchmarks not available for industry: {industry}"}
        
        return {
            'industry': industry,
            'benchmarks': self.benchmarks[industry_lower],
            'key_performance_indicators': self.industry_kpis.get(industry_lower, []),
            'industry_characteristics': self._get_industry_characteristics(industry_lower)
        }
    
    def _get_industry_characteristics(self, industry: str) -> Dict[str, Any]:
        """Get industry-specific characteristics and trends"""
        characteristics = {
            'manufacturing': {
                'typical_margins': '8-18%',
                'capital_intensity': 'High',
                'seasonality': 'Moderate',
                'key_challenges': ['Raw material costs', 'Labor availability', 'Regulatory compliance']
            },
            'retail': {
                'typical_margins': '4-12%',
                'capital_intensity': 'Medium',
                'seasonality': 'High',
                'key_challenges': ['Inventory management', 'Customer retention', 'Online competition']
            },
            'services': {
                'typical_margins': '10-22%',
                'capital_intensity': 'Low',
                'seasonality': 'Low',
                'key_challenges': ['Talent retention', 'Service quality', 'Scalability']
            },
            'agriculture': {
                'typical_margins': '5-16%',
                'capital_intensity': 'High',
                'seasonality': 'Very High',
                'key_challenges': ['Weather dependency', 'Price volatility', 'Input costs']
            },
            'logistics': {
                'typical_margins': '3-10%',
                'capital_intensity': 'High',
                'seasonality': 'Moderate',
                'key_challenges': ['Fuel costs', 'Route optimization', 'Regulatory changes']
            },
            'e-commerce': {
                'typical_margins': '1-12%',
                'capital_intensity': 'Medium',
                'seasonality': 'High',
                'key_challenges': ['Customer acquisition', 'Logistics costs', 'Technology investments']
            }
        }
        
        return characteristics.get(industry, {})