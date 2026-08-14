"""
Unit tests for Multi-Label Recommendation Model and Ranking.
"""

import pytest
from ml.inference.predictor import SMEPredictor
from backend.app.services.recommendation_service import RecommendationService
from ml.features.feature_definitions import RECOMMENDATION_CODES


@pytest.fixture
def predictor():
    return SMEPredictor()


@pytest.fixture
def recommendation_service(predictor):
    return RecommendationService(predictor)


@pytest.fixture
def high_receivables_data():
    return {
        "revenue": 10_000_000.0,
        "total_expenses": 8_000_000.0,
        "current_assets": 5_000_000.0,
        "current_liabilities": 2_500_000.0,
        "total_assets": 9_000_000.0,
        "total_debt": 3_000_000.0,
        "inventory": 500_000.0,
        "accounts_receivable": 3_000_000.0,  # ~110 days receivable
        "accounts_payable": 800_000.0,
        "revenue_growth_rate": 0.08,
        "industry": "manufacturing",
    }


def test_predict_recommendation_candidates(predictor, high_receivables_data):
    candidates = predictor.predict_recommendation_candidates(high_receivables_data)
    assert len(candidates) > 0
    for cand in candidates:
        assert cand["code"] in RECOMMENDATION_CODES
        assert 0.0 <= cand["confidence"] <= 1.0


def test_ranked_recommendations_generates_valid_output(recommendation_service, high_receivables_data):
    features = recommendation_service.predictor.pipeline.transform_single(high_receivables_data)
    recs = recommendation_service.generate_ranked_recommendations(
        raw_data=high_receivables_data,
        features=features,
        risk_probability=0.50,
        limit=5
    )

    assert len(recs) > 0
    assert len(recs) <= 5
    for rank, rec in enumerate(recs, start=1):
        assert rec["priority"] == rank
        assert rec["severity"] in ["HIGH", "MEDIUM", "LOW"]
        assert rec["impact"] in ["HIGH", "MEDIUM", "LOW"]
        assert 0.0 <= rec["confidence"] <= 1.0
        assert len(rec["rationale"]) > 0

    # Receivables recommendation should be present and high priority given 110 days DSO
    rec_codes = [r["code"] for r in recs]
    assert "RECEIVABLES" in rec_codes
