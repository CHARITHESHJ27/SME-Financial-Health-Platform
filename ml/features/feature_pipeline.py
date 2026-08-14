"""
Financial Feature Engineering Pipeline.
Calculates 22 robust financial ratios across Profitability, Liquidity, Leverage,
Efficiency, Growth, and Cash Flow with strict zero-division protection and outlier handling.
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union
from ml.features.feature_definitions import (
    FEATURE_VERSION,
    ENGINEERED_FEATURE_NAMES,
    ALLOWED_INDUSTRIES,
)
from ml.features.validation import sanitize_financial_inputs

EPSILON = 1e-6


class FinancialFeaturePipeline:
    """
    Feature transformation pipeline for SME financial data.
    Computes all 22 core financial ratios deterministically.
    """

    def __init__(self, version: str = FEATURE_VERSION):
        self.version = version
        self.feature_names = ENGINEERED_FEATURE_NAMES
        self.industry_list = ALLOWED_INDUSTRIES

    def transform_single(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from a single company's financial inputs.
        Returns a dictionary mapping feature names to computed float values.
        """
        clean = sanitize_financial_inputs(data)

        revenue = clean["revenue"]
        expenses = clean["total_expenses"]
        current_assets = clean["current_assets"]
        current_liabilities = clean["current_liabilities"]
        total_assets = clean["total_assets"]
        total_debt = clean["total_debt"]
        inventory = clean["inventory"]
        receivables = clean["accounts_receivable"]
        payables = clean["accounts_payable"]
        growth_rate = clean["revenue_growth_rate"]

        net_profit = revenue - expenses
        equity = max(total_assets - total_debt, EPSILON)

        # ── 1. Profitability Ratios ──────────────────────────────────────────
        # Gross Margin (proxy based on direct costs if inventory exists)
        cogs_proxy = expenses * 0.65 if inventory > 0 else expenses * 0.40
        gross_profit = revenue - min(cogs_proxy, expenses)
        gross_margin = (gross_profit / revenue) if revenue > 0 else 0.0

        # Operating Margin & Net Margin
        operating_profit = revenue - expenses
        operating_margin = (operating_profit / revenue) if revenue > 0 else 0.0
        net_margin = (net_profit / revenue) if revenue > 0 else 0.0

        # EBITDA Margin (approximate by adding back 5% estimated depreciation & interest)
        ebitda_proxy = operating_profit + (0.05 * total_assets)
        ebitda_margin = (ebitda_proxy / revenue) if revenue > 0 else 0.0

        # ROA & ROE
        roa = (net_profit / total_assets) if total_assets > 0 else 0.0
        roe = (net_profit / equity) if equity > 0 else (net_profit / total_assets if total_assets > 0 else 0.0)

        # ── 2. Liquidity Ratios ──────────────────────────────────────────────
        current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else (current_assets / 1.0 if current_assets > 0 else 1.0)
        
        quick_assets = max(0.0, current_assets - inventory)
        quick_ratio = (quick_assets / current_liabilities) if current_liabilities > 0 else (quick_assets / 1.0 if quick_assets > 0 else 1.0)

        cash_proxy = max(0.0, quick_assets - receivables)
        cash_ratio = (cash_proxy / current_liabilities) if current_liabilities > 0 else (cash_proxy / 1.0 if cash_proxy > 0 else 0.5)

        working_capital = current_assets - current_liabilities
        working_capital_to_assets = (working_capital / total_assets) if total_assets > 0 else 0.0

        # ── 3. Leverage & Solvency Ratios ───────────────────────────────────
        debt_to_equity = (total_debt / equity) if equity > 0 else (total_debt / total_assets if total_assets > 0 else 0.0)
        debt_to_assets = (total_debt / total_assets) if total_assets > 0 else 0.0
        
        estimated_interest = max(total_debt * 0.09, EPSILON)
        interest_coverage = (operating_profit / estimated_interest) if estimated_interest > 0 else 1.0
        
        equity_ratio = (equity / total_assets) if total_assets > 0 else 0.5

        # ── 4. Efficiency Ratios ─────────────────────────────────────────────
        if revenue > 0 and receivables > 0:
            receivable_turnover = revenue / receivables
            receivable_days = min(365.0, 365.0 / max(receivable_turnover, EPSILON))
        else:
            receivable_days = 30.0  # default neutral

        if expenses > 0 and payables > 0:
            payable_turnover = expenses / payables
            payable_days = min(365.0, 365.0 / max(payable_turnover, EPSILON))
        else:
            payable_days = 30.0

        if expenses > 0 and inventory > 0:
            inventory_turnover = expenses / inventory
            inventory_days = min(365.0, 365.0 / max(inventory_turnover, EPSILON))
        else:
            inventory_days = 0.0

        cash_conversion_cycle = receivable_days + inventory_days - payable_days
        asset_turnover = (revenue / total_assets) if total_assets > 0 else 1.0

        # ── 5. Growth Indicators ─────────────────────────────────────────────
        revenue_growth_rate = float(growth_rate)
        # Expense growth elasticity
        expense_growth_rate = (revenue_growth_rate * 0.9) if revenue_growth_rate > 0 else (revenue_growth_rate * 1.1)

        # ── 6. Cash Flow Metrics ─────────────────────────────────────────────
        # Operating cash flow proxy: Net Profit + Depreciation proxy - Working Capital delta proxy
        ocf_proxy = net_profit + (0.04 * total_assets) - (0.1 * abs(working_capital))
        operating_cash_flow_margin = (ocf_proxy / revenue) if revenue > 0 else 0.0
        cash_flow_to_debt = (ocf_proxy / total_debt) if total_debt > 0 else (1.0 if ocf_proxy > 0 else 0.0)

        # Build feature dictionary
        features = {
            "gross_margin": float(np.clip(gross_margin, -1.0, 1.0)),
            "operating_margin": float(np.clip(operating_margin, -2.0, 1.0)),
            "net_margin": float(np.clip(net_margin, -2.0, 1.0)),
            "ebitda_margin": float(np.clip(ebitda_margin, -2.0, 1.5)),
            "roa": float(np.clip(roa, -1.0, 1.0)),
            "roe": float(np.clip(roe, -2.0, 3.0)),
            "current_ratio": float(np.clip(current_ratio, 0.0, 20.0)),
            "quick_ratio": float(np.clip(quick_ratio, 0.0, 20.0)),
            "cash_ratio": float(np.clip(cash_ratio, 0.0, 10.0)),
            "working_capital_to_assets": float(np.clip(working_capital_to_assets, -1.0, 1.0)),
            "debt_to_equity": float(np.clip(debt_to_equity, 0.0, 15.0)),
            "debt_to_assets": float(np.clip(debt_to_assets, 0.0, 1.0)),
            "interest_coverage": float(np.clip(interest_coverage, -10.0, 50.0)),
            "equity_ratio": float(np.clip(equity_ratio, -0.5, 1.0)),
            "receivable_days": float(np.clip(receivable_days, 0.0, 365.0)),
            "payable_days": float(np.clip(payable_days, 0.0, 365.0)),
            "inventory_days": float(np.clip(inventory_days, 0.0, 365.0)),
            "cash_conversion_cycle": float(np.clip(cash_conversion_cycle, -180.0, 365.0)),
            "asset_turnover": float(np.clip(asset_turnover, 0.0, 20.0)),
            "revenue_growth_rate": float(np.clip(revenue_growth_rate, -1.0, 5.0)),
            "expense_growth_rate": float(np.clip(expense_growth_rate, -1.0, 5.0)),
            "operating_cash_flow_margin": float(np.clip(operating_cash_flow_margin, -2.0, 1.0)),
            "cash_flow_to_debt": float(np.clip(cash_flow_to_debt, -5.0, 10.0)),
        }

        return features

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Vectorized feature extraction over a DataFrame of financial records.
        """
        rows = [self.transform_single(row.to_dict()) for _, row in df.iterrows()]
        feature_df = pd.DataFrame(rows, columns=self.feature_names)
        
        # Add industry encoding if present
        if "industry" in df.columns:
            for ind in self.industry_list:
                feature_df[f"industry_{ind}"] = (df["industry"].str.lower() == ind).astype(float)

        return feature_df

    def to_feature_vector(self, data: Dict[str, Any], include_industry: bool = True) -> np.ndarray:
        """
        Convert raw input dict into an ordered numeric array ready for scikit-learn/XGBoost models.
        """
        feat_dict = self.transform_single(data)
        vector = [feat_dict[name] for name in self.feature_names]

        if include_industry:
            ind_val = str(data.get("industry", "services")).lower()
            for ind in self.industry_list:
                vector.append(1.0 if ind_val == ind else 0.0)

        return np.array(vector, dtype=np.float32)

    def get_full_feature_names(self, include_industry: bool = True) -> List[str]:
        """
        Returns full ordered list of feature column names including industry one-hot indicators.
        """
        names = list(self.feature_names)
        if include_industry:
            for ind in self.industry_list:
                names.append(f"industry_{ind}")
        return names
