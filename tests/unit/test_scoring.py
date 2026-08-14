"""
Unit tests for Risk Scoring and Model Inference.
"""

import pytest
from ml.inference.predictor import SMEPredictor
from ml.inference.model_manager import ModelManager


@pytest.fixture
def predictor():
    return SMEPredictor()


@pytest.fixture
def healthy_financial_data():
    return {
        "revenue": 20_000_000.0,
        "total_expenses": 16_000_000.0,
        "current_assets": 10_000_000.0,
        "current_liabilities": 4_000_000.0,
        "total_assets": 18_000_000.0,
        "total_debt": 3_000_000.0,
        "inventory": 2_000_000.0,
        "accounts_receivable": 2_000_000.0,
        "accounts_payable": 1_500_000.0,
        "revenue_growth_rate": 0.15,
        "industry": "services",
    }


@pytest.fixture
def distressed_financial_data():
    return {
        "revenue": 5_000_000.0,
        "total_expenses": 5_800_000.0,  # Operating at a loss
        "current_assets": 1_200_000.0,
        "current_liabilities": 2_400_000.0,  # Current ratio < 0.5
        "total_assets": 3_000_000.0,
        "total_debt": 2_700_000.0,  # Debt to assets 90%
        "inventory": 400_000.0,
        "accounts_receivable": 700_000.0,
        "accounts_payable": 1_800_000.0,
        "revenue_growth_rate": -0.15,
        "industry": "manufacturing",
    }


def test_predict_risk_returns_valid_structure(predictor, healthy_financial_data):
    result = predictor.predict_risk(healthy_financial_data)
    assert "score" in result
    assert "probability" in result
    assert "category" in result
    assert "model_version" in result
    assert "features" in result

    assert 0 <= result["score"] <= 100
    assert 0.0 <= result["probability"] <= 1.0
    assert result["category"] in ["MINIMAL", "LOW", "MEDIUM", "HIGH"]


def test_distressed_profile_scores_higher_risk(predictor, healthy_financial_data, distressed_financial_data):
    healthy_risk = predictor.predict_risk(healthy_financial_data)
    distressed_risk = predictor.predict_risk(distressed_financial_data)

    assert distressed_risk["probability"] > healthy_risk["probability"]
    assert distressed_risk["score"] > healthy_risk["score"]
    assert distressed_risk["category"] in ["HIGH", "MEDIUM"]
    assert healthy_risk["category"] in ["LOW", "MINIMAL"]


def test_model_manager_readiness():
    manager = ModelManager()
    status = manager.is_healthy()
    assert status["status"] in ["ready", "degraded"]
    assert "risk_model" in status
    assert "recommendation_model" in status
