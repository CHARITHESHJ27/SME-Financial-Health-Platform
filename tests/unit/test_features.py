"""
Unit tests for Financial Feature Engineering Pipeline.
"""

import pytest
import numpy as np
import pandas as pd

from ml.features.feature_definitions import (
    FEATURE_VERSION,
    ENGINEERED_FEATURE_NAMES,
    ALLOWED_INDUSTRIES,
)
from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.features.validation import (
    validate_raw_financial_data,
    sanitize_financial_inputs,
    FinancialValidationError,
)


@pytest.fixture
def feature_pipeline():
    return FinancialFeaturePipeline()


@pytest.fixture
def sample_financial_data():
    return {
        "revenue": 10_000_000.0,
        "total_expenses": 8_500_000.0,
        "current_assets": 4_000_000.0,
        "current_liabilities": 2_500_000.0,
        "total_assets": 8_000_000.0,
        "total_debt": 3_000_000.0,
        "inventory": 1_000_000.0,
        "accounts_receivable": 1_200_000.0,
        "accounts_payable": 800_000.0,
        "revenue_growth_rate": 0.12,
        "industry": "manufacturing",
    }


def test_feature_pipeline_computes_all_22_features(feature_pipeline, sample_financial_data):
    features = feature_pipeline.transform_single(sample_financial_data)
    assert len(features) == len(ENGINEERED_FEATURE_NAMES)
    for name in ENGINEERED_FEATURE_NAMES:
        assert name in features
        assert isinstance(features[name], float)
        assert not np.isnan(features[name])
        assert not np.isinf(features[name])


def test_division_by_zero_protection(feature_pipeline):
    """Test with zeros across all denominators."""
    zero_data = {
        "revenue": 0.0,
        "total_expenses": 0.0,
        "current_assets": 0.0,
        "current_liabilities": 0.0,
        "total_assets": 0.0,
        "total_debt": 0.0,
        "inventory": 0.0,
        "accounts_receivable": 0.0,
        "accounts_payable": 0.0,
        "revenue_growth_rate": 0.0,
        "industry": "services",
    }
    features = feature_pipeline.transform_single(zero_data)
    for k, v in features.items():
        assert not np.isnan(v), f"Feature {k} is NaN on zero denominators"
        assert not np.isinf(v), f"Feature {k} is Inf on zero denominators"


def test_liquidity_ratios_calculation(feature_pipeline, sample_financial_data):
    features = feature_pipeline.transform_single(sample_financial_data)
    # Current Ratio: 4M / 2.5M = 1.6
    assert pytest.approx(features["current_ratio"], 0.01) == 1.6
    # Quick Ratio: (4M - 1M) / 2.5M = 1.2
    assert pytest.approx(features["quick_ratio"], 0.01) == 1.2


def test_profitability_ratios_calculation(feature_pipeline, sample_financial_data):
    features = feature_pipeline.transform_single(sample_financial_data)
    # Net Margin: (10M - 8.5M) / 10M = 0.15 (15%)
    assert pytest.approx(features["net_margin"], 0.01) == 0.15
    # ROA: 1.5M / 8M = 0.1875
    assert pytest.approx(features["roa"], 0.01) == 0.1875


def test_efficiency_days_calculation(feature_pipeline, sample_financial_data):
    features = feature_pipeline.transform_single(sample_financial_data)
    # Receivables Days: (1.2M / 10M) * 365 = 43.8 days
    assert pytest.approx(features["receivable_days"], 0.1) == 43.8
    # Payables Days: (0.8M / 8.5M) * 365 = 34.35 days
    assert pytest.approx(features["payable_days"], 0.1) == 34.35


def test_feature_vector_includes_industry_encoding(feature_pipeline, sample_financial_data):
    vector = feature_pipeline.to_feature_vector(sample_financial_data, include_industry=True)
    assert len(vector) == len(ENGINEERED_FEATURE_NAMES) + len(ALLOWED_INDUSTRIES)
    assert vector.dtype == np.float32


def test_validation_rejects_negative_values():
    bad_data = {
        "revenue": -500000.0,
        "total_expenses": 300000.0,
        "current_assets": 200000.0,
        "current_liabilities": 100000.0,
        "total_assets": 500000.0,
        "total_debt": 100000.0,
    }
    is_valid, errors = validate_raw_financial_data(bad_data)
    assert not is_valid
    assert any("must be non-negative" in e or "greater than zero" in e for e in errors)


def test_validation_rejects_current_assets_exceeding_total_assets():
    inconsistent_data = {
        "revenue": 1000000.0,
        "total_expenses": 800000.0,
        "current_assets": 900000.0,
        "current_liabilities": 300000.0,
        "total_assets": 500000.0,  # less than current assets
        "total_debt": 200000.0,
    }
    is_valid, errors = validate_raw_financial_data(inconsistent_data)
    assert not is_valid
    assert any("Current assets" in e and "cannot exceed total assets" in e for e in errors)
