"""
Unit tests for SHAP Feature Attribution and Business Explanations.
"""

import pytest
from ml.inference.predictor import SMEPredictor
from backend.app.services.explanation_service import ExplanationService
from ml.features.feature_definitions import ENGINEERED_FEATURE_NAMES


@pytest.fixture
def predictor():
    return SMEPredictor()


@pytest.fixture
def explanation_service(predictor):
    return ExplanationService(predictor)


@pytest.fixture
def sample_company_data():
    return {
        "revenue": 8_000_000.0,
        "total_expenses": 7_500_000.0,
        "current_assets": 2_500_000.0,
        "current_liabilities": 2_800_000.0,  # CR < 1.0 (Liquidity risk driver)
        "total_assets": 6_000_000.0,
        "total_debt": 4_000_000.0,          # DTA > 66% (Leverage risk driver)
        "inventory": 800_000.0,
        "accounts_receivable": 1_200_000.0,
        "accounts_payable": 1_000_000.0,
        "revenue_growth_rate": 0.05,
        "industry": "retail",
    }


def test_shap_explanations_are_traceable(predictor, sample_company_data):
    explanations = predictor.explain_risk(sample_company_data, top_n=5)
    assert len(explanations) > 0
    assert len(explanations) <= 5

    for item in explanations:
        assert item["feature"] in ENGINEERED_FEATURE_NAMES
        assert item["direction"] in ["increases_risk", "decreases_risk"]
        assert item["impact"] in ["HIGH", "MEDIUM", "LOW"]
        assert isinstance(item["value"], (int, float))
        assert isinstance(item["contribution"], float)
        assert len(item["explanation"]) > 0


def test_executive_summary_construction(explanation_service, sample_company_data):
    features = explanation_service.predictor.pipeline.transform_single(sample_company_data)
    risk_res = explanation_service.predictor.predict_risk(sample_company_data)
    explanations = explanation_service.generate_explanations(sample_company_data, features, risk_res, top_n=5)
    
    summary = explanation_service.build_executive_summary(
        company_name="Apex Retail Pvt Ltd",
        industry="retail",
        risk_result=risk_res,
        recommendations=[{"title": "Improve Working Capital", "confidence": 0.92, "rationale": "Current ratio below benchmark"}],
        explanations=explanations
    )

    assert "headline" in summary
    assert "narrative" in summary
    assert "Apex Retail" in summary["narrative"]
    assert "top_risk_drivers" in summary
    assert "top_protective_factors" in summary
