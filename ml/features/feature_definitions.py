"""
Feature definitions, schemas, and ratio specifications for SME Financial Health Platform.
Version: 1.0.0
"""

from typing import List, Dict, Any

FEATURE_VERSION = "1.0.0"

# List of all 22 engineered quantitative financial features
ENGINEERED_FEATURE_NAMES: List[str] = [
    # Profitability (6)
    "gross_margin",
    "operating_margin",
    "net_margin",
    "ebitda_margin",
    "roa",
    "roe",
    # Liquidity (4)
    "current_ratio",
    "quick_ratio",
    "cash_ratio",
    "working_capital_to_assets",
    # Leverage (4)
    "debt_to_equity",
    "debt_to_assets",
    "interest_coverage",
    "equity_ratio",
    # Efficiency (5)
    "receivable_days",
    "payable_days",
    "inventory_days",
    "cash_conversion_cycle",
    "asset_turnover",
    # Growth (2)
    "revenue_growth_rate",
    "expense_growth_rate",
    # Cash Flow (2)
    "operating_cash_flow_margin",
    "cash_flow_to_debt",
]

# Raw financial inputs required for feature computation
RAW_FINANCIAL_FIELDS: List[str] = [
    "revenue",
    "total_expenses",
    "current_assets",
    "current_liabilities",
    "total_assets",
    "total_debt",
    "inventory",
    "accounts_receivable",
    "accounts_payable",
    "revenue_growth_rate",
    "industry",
]

# Supported industries
ALLOWED_INDUSTRIES: List[str] = [
    "manufacturing",
    "retail",
    "services",
    "agriculture",
    "logistics",
    "e-commerce",
]

# Multi-label Recommendation Codes
RECOMMENDATION_CODES: List[str] = [
    "WORKING_CAPITAL",
    "RECEIVABLES",
    "DEBT_REDUCTION",
    "COST_OPTIMIZATION",
    "MARGIN_IMPROVEMENT",
    "CASH_FLOW_STABILIZATION",
    "REVENUE_GROWTH",
    "INVENTORY_OPTIMIZATION",
]

# Mapping recommendation codes to human-readable titles and business action descriptions
RECOMMENDATION_METADATA: Dict[str, Dict[str, Any]] = {
    "WORKING_CAPITAL": {
        "title": "Improve Working Capital Management",
        "description": "Optimize short-term liquidity, restructure short-term obligations, or establish a revolving working capital line.",
        "primary_metric": "current_ratio",
        "benchmark_direction": "below_benchmark",
        "default_impact": "HIGH",
    },
    "RECEIVABLES": {
        "title": "Accelerate Accounts Receivable Collection",
        "description": "Tighten customer credit terms, implement automated invoicing reminders, or utilize invoice factoring to reduce collection days.",
        "primary_metric": "receivable_days",
        "benchmark_direction": "above_benchmark",
        "default_impact": "HIGH",
    },
    "DEBT_REDUCTION": {
        "title": "Reduce Leverage & Debt Burden",
        "description": "Prioritize paying down high-cost short-term debt, negotiate debt refinancing, or strengthen equity buffers to lower solvency risk.",
        "primary_metric": "debt_to_assets",
        "benchmark_direction": "above_benchmark",
        "default_impact": "HIGH",
    },
    "COST_OPTIMIZATION": {
        "title": "Execute Cost Optimization & Vendor Rationalization",
        "description": "Conduct a line-by-line expense audit, renegotiate supplier contracts, and reduce overhead to realign operating expense ratio.",
        "primary_metric": "operating_margin",
        "benchmark_direction": "below_benchmark",
        "default_impact": "MEDIUM",
    },
    "MARGIN_IMPROVEMENT": {
        "title": "Enhance Pricing Strategy & Gross Margins",
        "description": "Review pricing tiers, eliminate negative-margin product/service lines, and focus sales on high-contribution margin channels.",
        "primary_metric": "gross_margin",
        "benchmark_direction": "below_benchmark",
        "default_impact": "HIGH",
    },
    "CASH_FLOW_STABILIZATION": {
        "title": "Stabilize Operating Cash Flow",
        "description": "Align payment schedules with inflows, build a minimum 60-day cash operating buffer, and smooth seasonal cash flow dips.",
        "primary_metric": "operating_cash_flow_margin",
        "benchmark_direction": "below_benchmark",
        "default_impact": "HIGH",
    },
    "REVENUE_GROWTH": {
        "title": "Diversify Revenue & Expand Channels",
        "description": "Explore cross-selling, enter adjacent geographic or digital markets, and launch proactive customer retention campaigns.",
        "primary_metric": "revenue_growth_rate",
        "benchmark_direction": "below_benchmark",
        "default_impact": "MEDIUM",
    },
    "INVENTORY_OPTIMIZATION": {
        "title": "Implement Just-In-Time Inventory Management",
        "description": "Liquidate slow-moving SKU inventory, minimize holding costs, and establish dynamic replenishment triggers.",
        "primary_metric": "inventory_days",
        "benchmark_direction": "above_benchmark",
        "default_impact": "MEDIUM",
    },
}

# Standard industry benchmarks for financial ratio comparison
INDUSTRY_BENCHMARKS: Dict[str, Dict[str, Dict[str, float]]] = {
    "manufacturing": {
        "current_ratio": {"min": 1.2, "target": 1.8, "max": 2.5},
        "quick_ratio": {"min": 0.8, "target": 1.2, "max": 1.8},
        "net_margin": {"min": 0.05, "target": 0.12, "max": 0.20},
        "gross_margin": {"min": 0.20, "target": 0.35, "max": 0.50},
        "debt_to_assets": {"min": 0.20, "target": 0.45, "max": 0.65},
        "debt_to_equity": {"min": 0.30, "target": 0.80, "max": 1.50},
        "receivable_days": {"min": 30.0, "target": 45.0, "max": 75.0},
        "inventory_days": {"min": 30.0, "target": 60.0, "max": 90.0},
        "payable_days": {"min": 30.0, "target": 45.0, "max": 60.0},
        "roa": {"min": 0.04, "target": 0.09, "max": 0.16},
        "operating_cash_flow_margin": {"min": 0.05, "target": 0.12, "max": 0.22},
    },
    "retail": {
        "current_ratio": {"min": 1.1, "target": 1.5, "max": 2.2},
        "quick_ratio": {"min": 0.5, "target": 0.8, "max": 1.4},
        "net_margin": {"min": 0.03, "target": 0.08, "max": 0.14},
        "gross_margin": {"min": 0.18, "target": 0.28, "max": 0.40},
        "debt_to_assets": {"min": 0.25, "target": 0.50, "max": 0.70},
        "debt_to_equity": {"min": 0.40, "target": 1.00, "max": 1.80},
        "receivable_days": {"min": 7.0, "target": 15.0, "max": 30.0},
        "inventory_days": {"min": 25.0, "target": 45.0, "max": 75.0},
        "payable_days": {"min": 25.0, "target": 40.0, "max": 60.0},
        "roa": {"min": 0.03, "target": 0.07, "max": 0.14},
        "operating_cash_flow_margin": {"min": 0.04, "target": 0.09, "max": 0.16},
    },
    "services": {
        "current_ratio": {"min": 1.3, "target": 2.0, "max": 3.0},
        "quick_ratio": {"min": 1.2, "target": 1.8, "max": 2.8},
        "net_margin": {"min": 0.08, "target": 0.16, "max": 0.25},
        "gross_margin": {"min": 0.35, "target": 0.50, "max": 0.70},
        "debt_to_assets": {"min": 0.15, "target": 0.35, "max": 0.55},
        "debt_to_equity": {"min": 0.20, "target": 0.60, "max": 1.20},
        "receivable_days": {"min": 25.0, "target": 40.0, "max": 65.0},
        "inventory_days": {"min": 0.0, "target": 0.0, "max": 10.0},
        "payable_days": {"min": 20.0, "target": 35.0, "max": 50.0},
        "roa": {"min": 0.06, "target": 0.14, "max": 0.22},
        "operating_cash_flow_margin": {"min": 0.08, "target": 0.18, "max": 0.28},
    },
    "agriculture": {
        "current_ratio": {"min": 1.1, "target": 1.6, "max": 2.4},
        "quick_ratio": {"min": 0.6, "target": 1.0, "max": 1.6},
        "net_margin": {"min": 0.04, "target": 0.10, "max": 0.18},
        "gross_margin": {"min": 0.18, "target": 0.30, "max": 0.45},
        "debt_to_assets": {"min": 0.30, "target": 0.55, "max": 0.75},
        "debt_to_equity": {"min": 0.50, "target": 1.20, "max": 2.00},
        "receivable_days": {"min": 20.0, "target": 35.0, "max": 60.0},
        "inventory_days": {"min": 35.0, "target": 70.0, "max": 110.0},
        "payable_days": {"min": 25.0, "target": 45.0, "max": 65.0},
        "roa": {"min": 0.03, "target": 0.08, "max": 0.15},
        "operating_cash_flow_margin": {"min": 0.04, "target": 0.10, "max": 0.20},
    },
    "logistics": {
        "current_ratio": {"min": 1.1, "target": 1.4, "max": 2.0},
        "quick_ratio": {"min": 0.9, "target": 1.2, "max": 1.8},
        "net_margin": {"min": 0.03, "target": 0.07, "max": 0.12},
        "gross_margin": {"min": 0.18, "target": 0.25, "max": 0.38},
        "debt_to_assets": {"min": 0.35, "target": 0.60, "max": 0.80},
        "debt_to_equity": {"min": 0.60, "target": 1.50, "max": 2.50},
        "receivable_days": {"min": 30.0, "target": 45.0, "max": 70.0},
        "inventory_days": {"min": 5.0, "target": 15.0, "max": 30.0},
        "payable_days": {"min": 30.0, "target": 50.0, "max": 75.0},
        "roa": {"min": 0.03, "target": 0.06, "max": 0.12},
        "operating_cash_flow_margin": {"min": 0.05, "target": 0.10, "max": 0.18},
    },
    "e-commerce": {
        "current_ratio": {"min": 1.0, "target": 1.4, "max": 2.0},
        "quick_ratio": {"min": 0.7, "target": 1.1, "max": 1.6},
        "net_margin": {"min": 0.02, "target": 0.06, "max": 0.14},
        "gross_margin": {"min": 0.25, "target": 0.40, "max": 0.55},
        "debt_to_assets": {"min": 0.20, "target": 0.42, "max": 0.65},
        "debt_to_equity": {"min": 0.35, "target": 0.90, "max": 1.60},
        "receivable_days": {"min": 5.0, "target": 15.0, "max": 25.0},
        "inventory_days": {"min": 20.0, "target": 35.0, "max": 60.0},
        "payable_days": {"min": 20.0, "target": 35.0, "max": 55.0},
        "roa": {"min": 0.02, "target": 0.07, "max": 0.15},
        "operating_cash_flow_margin": {"min": 0.03, "target": 0.08, "max": 0.16},
    },
}
