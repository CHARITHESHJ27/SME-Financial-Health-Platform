"""
Realistic SME Financial Dataset Generator.
Generates statistically grounded synthetic financial data with realistic balance sheet
and income statement relationships across Indian SME industries without data leakage.
"""

import os
import random
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

from ml.features.feature_definitions import (
    ALLOWED_INDUSTRIES,
    RECOMMENDATION_CODES,
    INDUSTRY_BENCHMARKS,
)
from ml.features.feature_pipeline import FinancialFeaturePipeline


def generate_sme_dataset(
    n_samples: int = 6000,
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Generate a dataset of realistic SME financial statements with ground truth risk labels
    and multi-label intervention recommendations.
    """
    np.random.seed(random_seed)
    random.seed(random_seed)

    records = []
    pipeline = FinancialFeaturePipeline()

    industry_profiles = {
        "manufacturing": {
            "rev_mean": 15_000_000, "rev_std": 10_000_000,
            "margin_mean": 0.10, "margin_std": 0.08,
            "asset_intensity": 0.85, "debt_ratio_mean": 0.48,
            "has_inventory": True, "rec_days_mean": 50, "pay_days_mean": 45,
        },
        "retail": {
            "rev_mean": 8_000_000, "rev_std": 6_000_000,
            "margin_mean": 0.07, "margin_std": 0.06,
            "asset_intensity": 0.60, "debt_ratio_mean": 0.45,
            "has_inventory": True, "rec_days_mean": 18, "pay_days_mean": 38,
        },
        "services": {
            "rev_mean": 10_000_000, "rev_std": 8_000_000,
            "margin_mean": 0.16, "margin_std": 0.10,
            "asset_intensity": 0.45, "debt_ratio_mean": 0.32,
            "has_inventory": False, "rec_days_mean": 42, "pay_days_mean": 30,
        },
        "agriculture": {
            "rev_mean": 6_000_000, "rev_std": 4_500_000,
            "margin_mean": 0.09, "margin_std": 0.09,
            "asset_intensity": 0.90, "debt_ratio_mean": 0.55,
            "has_inventory": True, "rec_days_mean": 35, "pay_days_mean": 45,
        },
        "logistics": {
            "rev_mean": 14_000_000, "rev_std": 9_000_000,
            "margin_mean": 0.06, "margin_std": 0.07,
            "asset_intensity": 0.80, "debt_ratio_mean": 0.58,
            "has_inventory": False, "rec_days_mean": 48, "pay_days_mean": 52,
        },
        "e-commerce": {
            "rev_mean": 12_000_000, "rev_std": 11_000_000,
            "margin_mean": 0.05, "margin_std": 0.09,
            "asset_intensity": 0.55, "debt_ratio_mean": 0.40,
            "has_inventory": True, "rec_days_mean": 14, "pay_days_mean": 35,
        },
    }

    for i in range(n_samples):
        industry = random.choice(ALLOWED_INDUSTRIES)
        profile = industry_profiles[industry]

        # 1. Revenue (log-normal distribution for business size diversity)
        revenue = max(500_000.0, float(np.random.normal(profile["rev_mean"], profile["rev_std"])))

        # 2. Profit Margin & Total Expenses
        profit_margin = float(np.random.normal(profile["margin_mean"], profile["margin_std"]))
        profit_margin = np.clip(profit_margin, -0.30, 0.40)
        total_expenses = revenue * (1.0 - profit_margin)

        # 3. Balance Sheet - Assets
        asset_ratio = float(np.random.normal(profile["asset_intensity"], 0.15))
        asset_ratio = np.clip(asset_ratio, 0.30, 1.80)
        total_assets = revenue * asset_ratio

        # Current Assets breakdown
        ca_fraction = float(np.random.uniform(0.40, 0.75))
        current_assets = total_assets * ca_fraction

        # Inventory
        if profile["has_inventory"]:
            inv_days = max(10.0, float(np.random.normal(50, 25)))
            inventory = min(current_assets * 0.60, (total_expenses / 365.0) * inv_days)
        else:
            inventory = 0.0

        # Accounts Receivable
        rec_days = max(5.0, float(np.random.normal(profile["rec_days_mean"], 18)))
        accounts_receivable = min(current_assets - inventory - 10_000, (revenue / 365.0) * rec_days)
        accounts_receivable = max(0.0, accounts_receivable)

        # Cash proxy is remaining current assets
        cash = max(10_000.0, current_assets - inventory - accounts_receivable)
        current_assets = inventory + accounts_receivable + cash  # exact consistency

        # 4. Balance Sheet - Liabilities & Debt
        debt_ratio = float(np.random.normal(profile["debt_ratio_mean"], 0.18))
        debt_ratio = np.clip(debt_ratio, 0.05, 0.95)
        total_debt = total_assets * debt_ratio

        # Current liabilities
        cl_fraction = float(np.random.uniform(0.35, 0.70))
        current_liabilities = total_debt * cl_fraction
        
        # Accounts payable
        pay_days = max(10.0, float(np.random.normal(profile["pay_days_mean"], 15)))
        accounts_payable = min(current_liabilities * 0.85, (total_expenses / 365.0) * pay_days)

        # Growth Rate
        growth_rate = float(np.random.normal(0.08, 0.18))
        growth_rate = np.clip(growth_rate, -0.40, 1.20)

        # 5. Compute Engineered Ratios for Labels
        raw_dict = {
            "revenue": revenue,
            "total_expenses": total_expenses,
            "current_assets": current_assets,
            "current_liabilities": current_liabilities,
            "total_assets": total_assets,
            "total_debt": total_debt,
            "inventory": inventory,
            "accounts_receivable": accounts_receivable,
            "accounts_payable": accounts_payable,
            "revenue_growth_rate": growth_rate,
            "industry": industry,
        }

        ratios = pipeline.transform_single(raw_dict)

        # 6. Formulate Objective Ground Truth Risk Label (0 = Low/Moderate Risk, 1 = High Financial Distress)
        # Financial distress score based on solvency, liquidity, profitability, and cash flow
        distress_points = 0
        if ratios["current_ratio"] < 1.0:
            distress_points += 35
        elif ratios["current_ratio"] < 1.3:
            distress_points += 15

        if ratios["debt_to_assets"] > 0.75:
            distress_points += 35
        elif ratios["debt_to_assets"] > 0.60:
            distress_points += 20

        if ratios["net_margin"] < -0.05:
            distress_points += 30
        elif ratios["net_margin"] < 0.02:
            distress_points += 15

        if ratios["operating_cash_flow_margin"] < -0.02:
            distress_points += 25
        
        if ratios["receivable_days"] > 75:
            distress_points += 15

        if growth_rate < -0.10:
            distress_points += 15

        # Add realistic noise/variance
        distress_score = distress_points + np.random.normal(0, 8)
        risk_label = 1 if distress_score >= 50 else 0

        # 7. Formulate Multi-Label Recommendation Targets
        rec_targets = {}
        # Working Capital: if liquidity is constrained
        rec_targets["target_WORKING_CAPITAL"] = 1 if (ratios["current_ratio"] < 1.3 or ratios["working_capital_to_assets"] < 0.05) else 0
        # Receivables: if DSO is high
        rec_targets["target_RECEIVABLES"] = 1 if (ratios["receivable_days"] > 45.0) else 0
        # Debt Reduction: if leverage is high
        rec_targets["target_DEBT_REDUCTION"] = 1 if (ratios["debt_to_assets"] > 0.55 or ratios["debt_to_equity"] > 1.4) else 0
        # Cost Optimization: if operating expenses are high / margin compressed
        rec_targets["target_COST_OPTIMIZATION"] = 1 if (ratios["operating_margin"] < 0.06 or (total_expenses / revenue) > 0.92) else 0
        # Margin Improvement: if gross margin is below benchmark
        rec_targets["target_MARGIN_IMPROVEMENT"] = 1 if (ratios["gross_margin"] < 0.25) else 0
        # Cash Flow Stabilization: if OCF margin is weak or negative
        rec_targets["target_CASH_FLOW_STABILIZATION"] = 1 if (ratios["operating_cash_flow_margin"] < 0.04) else 0
        # Revenue Growth: if sales are stagnant or declining
        rec_targets["target_REVENUE_GROWTH"] = 1 if (growth_rate < 0.04) else 0
        # Inventory Optimization: if holding goods too long (for inventory industries)
        rec_targets["target_INVENTORY_OPTIMIZATION"] = 1 if (profile["has_inventory"] and ratios["inventory_days"] > 60.0) else 0

        row = {
            **raw_dict,
            **ratios,
            "risk_label": risk_label,
            "distress_score": distress_score,
            **rec_targets,
        }
        records.append(row)

    df = pd.DataFrame(records)
    return df


def save_datasets(data_dir: str = "data") -> Tuple[str, str, str]:
    """
    Generate dataset and save train, validation, and test splits into data/processed.
    """
    processed_dir = os.path.join(data_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)

    df = generate_sme_dataset(n_samples=6000, random_seed=42)

    # 70% Train, 15% Validation, 15% Test
    n = len(df)
    train_end = int(0.70 * n)
    val_end = int(0.85 * n)

    # Shuffle
    df_shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    train_df = df_shuffled.iloc[:train_end]
    val_df = df_shuffled.iloc[train_end:val_end]
    test_df = df_shuffled.iloc[val_end:]

    train_path = os.path.join(processed_dir, "train.csv")
    val_path = os.path.join(processed_dir, "val.csv")
    test_path = os.path.join(processed_dir, "test.csv")

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"Generated {n} total samples:")
    print(f"  - Train: {len(train_df)} samples -> {train_path}")
    print(f"  - Val:   {len(val_df)} samples -> {val_path}")
    print(f"  - Test:  {len(test_df)} samples -> {test_path}")
    print(f"  - Risk label balance: {train_df['risk_label'].mean()*100:.1f}% positive in train")

    return train_path, val_path, test_path


if __name__ == "__main__":
    save_datasets()
