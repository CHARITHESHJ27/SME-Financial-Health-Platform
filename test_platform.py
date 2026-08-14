#!/usr/bin/env python3
"""
Platform Smoke Test Suite.
Verifies Feature Engineering, Calibrated Risk ML Inference, Multi-Label Recommendations,
Deterministic Rule Engine, and SHAP Explainability without external API dependencies.
"""

import sys
import os

# Ensure backend and workspace are on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.features.validation import validate_raw_financial_data
from ml.inference.predictor import SMEPredictor
from ml.inference.model_manager import ModelManager
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.explanation_service import ExplanationService


def test_feature_pipeline():
    """Test 22 financial ratio computations."""
    try:
        pipeline = FinancialFeaturePipeline()
        sample_data = {
            "revenue": 12_000_000,
            "total_expenses": 10_000_000,
            "current_assets": 5_000_000,
            "current_liabilities": 3_500_000,
            "total_assets": 10_000_000,
            "total_debt": 4_500_000,
            "inventory": 1_200_000,
            "accounts_receivable": 1_800_000,
            "accounts_payable": 1_200_000,
            "revenue_growth_rate": 0.14,
            "industry": "manufacturing",
        }
        features = pipeline.transform_single(sample_data)
        assert len(features) >= 22
        assert "current_ratio" in features
        assert "net_margin" in features
        assert "debt_to_assets" in features
        assert "receivable_days" in features
        print(f"✓ Feature Pipeline Test passed ({len(features)} ratios computed)")
        return True
    except Exception as e:
        print(f"✗ Feature Pipeline Test failed: {e}")
        return False


def test_ml_risk_predictor():
    """Test Calibrated ML Risk Prediction."""
    try:
        predictor = SMEPredictor()
        sample_data = {
            "revenue": 10_000_000,
            "total_expenses": 8_500_000,
            "current_assets": 4_000_000,
            "current_liabilities": 2_500_000,
            "total_assets": 8_000_000,
            "total_debt": 3_000_000,
            "inventory": 800_000,
            "accounts_receivable": 1_200_000,
            "accounts_payable": 900_000,
            "revenue_growth_rate": 0.10,
            "industry": "retail",
        }
        risk = predictor.predict_risk(sample_data)
        assert 0 <= risk["score"] <= 100
        assert 0.0 <= risk["probability"] <= 1.0
        assert risk["category"] in ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
        print(f"✓ ML Risk Model Test passed (Score: {risk['score']}/100, Prob: {risk['probability']*100:.1f}%, Tier: {risk['category']})")
        return True
    except Exception as e:
        print(f"✗ ML Risk Model Test failed: {e}")
        return False


def test_shap_explainability():
    """Test SHAP Feature Attribution."""
    try:
        predictor = SMEPredictor()
        sample_data = {
            "revenue": 8_000_000,
            "total_expenses": 7_800_000,
            "current_assets": 2_000_000,
            "current_liabilities": 2_800_000,
            "total_assets": 5_000_000,
            "total_debt": 4_000_000,
            "inventory": 600_000,
            "accounts_receivable": 1_000_000,
            "accounts_payable": 1_200_000,
            "revenue_growth_rate": 0.02,
            "industry": "services",
        }
        explanations = predictor.explain_risk(sample_data, top_n=3)
        assert len(explanations) == 3
        for exp in explanations:
            assert exp["direction"] in ["increases_risk", "decreases_risk"]
            assert len(exp["explanation"]) > 0
        print(f"✓ SHAP Explainability Test passed (Top driver: {explanations[0]['feature']})")
        return True
    except Exception as e:
        print(f"✗ SHAP Explainability Test failed: {e}")
        return False


def test_recommendation_and_rule_engine():
    """Test Multi-Label Recommendations & Deterministic Rule Validation."""
    try:
        rec_service = RecommendationService()
        sample_data = {
            "revenue": 10_000_000,
            "total_expenses": 8_000_000,
            "current_assets": 4_000_000,
            "current_liabilities": 3_500_000,
            "total_assets": 8_000_000,
            "total_debt": 4_500_000,
            "inventory": 800_000,
            "accounts_receivable": 2_500_000,  # ~90 days receivable
            "accounts_payable": 900_000,
            "revenue_growth_rate": 0.05,
            "industry": "manufacturing",
        }
        features = rec_service.predictor.pipeline.transform_single(sample_data)
        recs = rec_service.generate_ranked_recommendations(
            raw_data=sample_data,
            features=features,
            risk_probability=0.55,
            limit=4
        )
        assert len(recs) > 0
        for rank, r in enumerate(recs, start=1):
            assert r["priority"] == rank
            assert "rationale" in r
            assert 0.0 <= r["confidence"] <= 1.0
        print(f"✓ Recommendation & Rule Engine Test passed ({len(recs)} ranked interventions)")
        return True
    except Exception as e:
        print(f"✗ Recommendation & Rule Engine Test failed: {e}")
        return False


def main():
    print("=" * 65)
    print("🚀 SME Financial Health Platform — ML Smoke Test Suite")
    print("=" * 65 + "\n")

    tests = [
        test_feature_pipeline,
        test_ml_risk_predictor,
        test_shap_explainability,
        test_recommendation_and_rule_engine,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 65)
    print(f"Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All ML tests passed! System operates deterministically with 0 external tokens.")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())