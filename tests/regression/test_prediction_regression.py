"""
ML Regression Gating Tests.
Validates that model performance and deterministic recommendation consistency
meet strict production thresholds on the golden test dataset.
"""

import os
import pytest
import numpy as np
import pandas as pd
from ml.inference.predictor import SMEPredictor
from backend.app.services.recommendation_service import RecommendationService
from ml.evaluation.metrics import evaluate_risk_predictions, evaluate_multilabel_predictions
from ml.features.feature_definitions import INDUSTRY_BENCHMARKS


@pytest.fixture
def predictor():
    return SMEPredictor()


@pytest.fixture
def recommendation_service(predictor):
    return RecommendationService(predictor)


@pytest.fixture
def test_dataset():
    test_path = "data/processed/test.csv"
    if not os.path.exists(test_path):
        from ml.data.generate_dataset import save_datasets
        save_datasets(data_dir="data")
    return pd.read_csv(test_path)


def test_risk_model_regression_gates(predictor, test_dataset):
    """
    ML Regression Gate for Risk Model:
    - ROC-AUC must be >= 0.85
    - Brier score must be <= 0.10
    """
    y_true = test_dataset["risk_label"].values
    y_probs = []

    for _, row in test_dataset.iterrows():
        res = predictor.predict_risk(row.to_dict())
        y_probs.append(res["probability"])

    y_probs = np.array(y_probs)
    metrics = evaluate_risk_predictions(y_true, y_probs)

    print(f"\n[Regression Gate] Risk Model Test ROC-AUC: {metrics['roc_auc']:.4f} (Required >= 0.85)")
    print(f"[Regression Gate] Risk Model Test Brier Score: {metrics['brier_score']:.4f} (Required <= 0.10)")

    assert metrics["roc_auc"] >= 0.85, f"ROC-AUC degraded to {metrics['roc_auc']:.4f}"
    assert metrics["brier_score"] <= 0.10, f"Brier score degraded to {metrics['brier_score']:.4f}"


def test_zero_invalid_recommendation_rate_gate(recommendation_service, test_dataset):
    """
    Critical Quality Gate: Invalid Recommendation Rate = 0.0%.
    No contradictory recommendations are allowed to be generated.
    """
    total_evaluated = 0
    invalid_count = 0

    # Test on a representative slice of test companies
    sample_df = test_dataset.sample(min(100, len(test_dataset)), random_state=42)

    for _, row in sample_df.iterrows():
        raw_data = row.to_dict()
        features = recommendation_service.predictor.pipeline.transform_single(raw_data)
        recs = recommendation_service.generate_ranked_recommendations(
            raw_data=raw_data,
            features=features,
            risk_probability=0.50,
            limit=5
        )

        ind = str(raw_data.get("industry", "services")).lower()
        for r in recs:
            total_evaluated += 1
            code = r["code"]

            # Contradiction checks
            if code == "RECEIVABLES" and features["receivable_days"] < 30.0:
                invalid_count += 1
            elif code == "WORKING_CAPITAL" and features["current_ratio"] >= 1.6 and features["working_capital_to_assets"] >= 0.15:
                invalid_count += 1
            elif code == "INVENTORY_OPTIMIZATION" and (ind == "services" or features["inventory_days"] <= 15.0):
                invalid_count += 1
            elif code == "DEBT_REDUCTION" and features["debt_to_assets"] <= 0.30 and features["debt_to_equity"] <= 0.50:
                invalid_count += 1

    invalid_rate = (invalid_count / float(total_evaluated)) if total_evaluated > 0 else 0.0
    print(f"\n[Regression Gate] Invalid Recommendation Rate: {invalid_rate*100:.2f}% (Required: 0.0%)")

    assert invalid_rate == 0.0, f"Invalid recommendation rate was {invalid_rate*100:.2f}% (expected 0.0%)"


def test_prediction_determinism_gate(predictor, test_dataset):
    """
    Every prediction must be 100% deterministic (repeated inference yields identical probabilities).
    """
    row = test_dataset.iloc[0].to_dict()
    run1 = predictor.predict_risk(row)
    run2 = predictor.predict_risk(row)
    run3 = predictor.predict_risk(row)

    assert run1["probability"] == run2["probability"] == run3["probability"]
    assert run1["score"] == run2["score"] == run3["score"]
