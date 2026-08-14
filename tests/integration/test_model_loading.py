"""
Integration tests for Model Loading, Versioning, and Artifact Integrity.
"""

import os
import json
import pytest
from ml.inference.model_manager import ModelManager


def test_model_manager_loads_risk_model():
    manager = ModelManager()
    risk_bundle = manager.get_risk_bundle()

    assert risk_bundle is not None
    assert "calibrated_model" in risk_bundle
    assert "feature_names" in risk_bundle
    assert "model_version" in risk_bundle
    assert len(risk_bundle["feature_names"]) > 20


def test_model_manager_loads_recommendation_model():
    manager = ModelManager()
    rec_bundle = manager.get_recommendation_bundle()

    assert rec_bundle is not None
    assert "model" in rec_bundle
    assert "recommendation_codes" in rec_bundle
    assert len(rec_bundle["recommendation_codes"]) == 8


def test_artifact_metadata_and_schema_files():
    risk_dir = "ml/models/risk/v1.0.0"
    assert os.path.exists(os.path.join(risk_dir, "metadata.json"))
    assert os.path.exists(os.path.join(risk_dir, "feature_schema.json"))
    assert os.path.exists(os.path.join(risk_dir, "metrics.json"))
    assert os.path.exists(os.path.join(risk_dir, "model.joblib"))

    with open(os.path.join(risk_dir, "metadata.json")) as f:
        meta = json.load(f)
        assert meta["version"] == "v1.0.0"
        assert "artifact_sha256" in meta

    with open(os.path.join(risk_dir, "metrics.json")) as f:
        metrics = json.load(f)
        assert "test_metrics_calibrated" in metrics
        assert metrics["test_metrics_calibrated"]["roc_auc"] > 0.85
