"""
Training Pipeline for SME Financial Risk Prediction Model.
Trains candidate models (Logistic Regression, Random Forest, XGBoost),
performs probability calibration, evaluates performance metrics, and exports
versioned production artifacts.
"""

import os
import sys
import json
import hashlib
import argparse
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False
    xgb = None

from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.data.generate_dataset import save_datasets
from ml.training.config import load_config
from ml.evaluation.metrics import evaluate_risk_predictions


def get_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file for artifact integrity checking."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def train_risk_model(config_path: str = "configs/risk.yaml"):
    """Execute complete risk model training, calibration, and artifact generation."""
    config = load_config(config_path)

    # 1. Ensure dataset exists
    train_path = config["data"]["train_path"]
    val_path = config["data"]["val_path"]
    test_path = config["data"]["test_path"]

    if not (os.path.exists(train_path) and os.path.exists(val_path) and os.path.exists(test_path)):
        print("Data files not found. Generating realistic SME datasets...")
        save_datasets(data_dir="data")

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)

    pipeline = FinancialFeaturePipeline(version=config["features"]["feature_version"])
    feature_names = pipeline.get_full_feature_names(include_industry=config["features"]["include_industry"])

    # Extract feature matrices
    X_train = np.array([pipeline.to_feature_vector(row.to_dict()) for _, row in train_df.iterrows()])
    y_train = train_df[config["data"]["target_column"]].values

    X_val = np.array([pipeline.to_feature_vector(row.to_dict()) for _, row in val_df.iterrows()])
    y_val = val_df[config["data"]["target_column"]].values

    X_test = np.array([pipeline.to_feature_vector(row.to_dict()) for _, row in test_df.iterrows()])
    y_test = test_df[config["data"]["target_column"]].values

    print(f"Dataset shapes: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
    print(f"Features ({len(feature_names)}): {feature_names}")

    # 2. Train & compare candidate models
    candidate_results = {}
    models_dict = {}

    # Logistic Regression Baseline
    lr = LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced", random_state=config["seed"])
    lr.fit(X_train, y_train)
    lr_val_probs = lr.predict_proba(X_val)[:, 1]
    candidate_results["logistic_regression"] = evaluate_risk_predictions(y_val, lr_val_probs)
    models_dict["logistic_regression"] = lr

    # Random Forest Baseline
    rf = RandomForestClassifier(n_estimators=150, max_depth=8, min_samples_split=5, class_weight="balanced", random_state=config["seed"])
    rf.fit(X_train, y_train)
    rf_val_probs = rf.predict_proba(X_val)[:, 1]
    candidate_results["random_forest"] = evaluate_risk_predictions(y_val, rf_val_probs)
    models_dict["random_forest"] = rf

    # Gradient Boosting (XGBoost or HistGradientBoosting)
    if XGB_AVAILABLE and xgb is not None:
        try:
            gb_model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                eval_metric="logloss",
                random_state=config["seed"]
            )
            gb_model.fit(X_train, y_train)
            framework_name = "xgboost"
        except Exception:
            gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.05, random_state=config["seed"])
            gb_model.fit(X_train, y_train)
            framework_name = "gradient_boosting"
    else:
        gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.05, random_state=config["seed"])
        gb_model.fit(X_train, y_train)
        framework_name = "gradient_boosting"

    gb_val_probs = gb_model.predict_proba(X_val)[:, 1]
    candidate_results["gradient_boosting"] = evaluate_risk_predictions(y_val, gb_val_probs)
    models_dict["gradient_boosting"] = gb_model
    models_dict["xgboost"] = gb_model

    print("\nCandidate Model Validation Results:")
    for name, res in candidate_results.items():
        print(f"  • {name:20s} | ROC-AUC: {res['roc_auc']:.4f} | PR-AUC: {res['pr_auc']:.4f} | Brier: {res['brier_score']:.4f} | F1: {res['f1']:.4f}")

    # 3. Probability Calibration on Selected Model
    selected_name = config["production_model"].get("selected", "gradient_boosting")
    base_prod_model = models_dict.get(selected_name, gb_model)
    calib_method = config["production_model"]["calibration"].get("method", "isotonic")

    print(f"\nApplying '{calib_method}' probability calibration to selected model '{selected_name}'...")
    calibrated_model = CalibratedClassifierCV(
        estimator=base_prod_model,
        method=calib_method,
        cv=config["production_model"]["calibration"].get("cv", 5)
    )
    calibrated_model.fit(X_train, y_train)

    # Evaluate Calibrated Model on Test Set
    raw_test_probs = base_prod_model.predict_proba(X_test)[:, 1]
    calib_test_probs = calibrated_model.predict_proba(X_test)[:, 1]

    raw_test_metrics = evaluate_risk_predictions(y_test, raw_test_probs)
    calib_test_metrics = evaluate_risk_predictions(y_test, calib_test_probs)

    print(f"\nFinal Test Evaluation ({selected_name.upper()}):")
    print(f"  • Raw Test ROC-AUC:        {raw_test_metrics['roc_auc']:.4f} | Brier: {raw_test_metrics['brier_score']:.4f}")
    print(f"  • Calibrated Test ROC-AUC: {calib_test_metrics['roc_auc']:.4f} | Brier: {calib_test_metrics['brier_score']:.4f}")
    print(f"  • Test Precision:          {calib_test_metrics['precision']:.4f} | Recall: {calib_test_metrics['recall']:.4f} | F1: {calib_test_metrics['f1']:.4f}")

    # 4. Export Artifacts
    artifact_dir = config["output"]["artifact_dir"]
    os.makedirs(artifact_dir, exist_ok=True)

    # Save model artifact bundle
    model_artifact = {
        "calibrated_model": calibrated_model,
        "base_model": base_prod_model,
        "framework": "xgboost+sklearn",
        "feature_names": feature_names,
        "feature_version": config["features"]["feature_version"],
        "model_version": config["version"],
        "model_name": config["model_name"],
    }
    model_path = os.path.join(artifact_dir, "model.joblib")
    joblib.dump(model_artifact, model_path)

    # Compute checksum
    artifact_hash = get_file_hash(model_path)

    # Save feature schema
    schema_data = {
        "feature_version": config["features"]["feature_version"],
        "feature_names": feature_names,
        "quantitative_features": pipeline.feature_names,
        "industry_encoding": [f"industry_{ind}" for ind in pipeline.industry_list],
        "feature_count": len(feature_names),
    }
    schema_path = os.path.join(artifact_dir, "feature_schema.json")
    with open(schema_path, "w") as f:
        json.dump(schema_data, f, indent=2)

    # Save metadata
    metadata = {
        "model_name": config["model_name"],
        "version": config["version"],
        "framework": framework_name,
        "calibration": calib_method,
        "feature_version": config["features"]["feature_version"],
        "training_dataset": "sme-synthetic-v1",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "artifact_file": "model.joblib",
        "artifact_sha256": artifact_hash,
        "python_version": sys.version.split()[0],
        "dependencies": {
            "xgboost": getattr(xgb, "__version__", "unavailable") if xgb else "unavailable",
            "scikit-learn": "1.3.2",
            "joblib": joblib.__version__,
        }
    }
    metadata_path = os.path.join(artifact_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save complete metrics
    all_metrics = {
        "model_version": config["version"],
        "validation_comparison": candidate_results,
        "test_metrics_calibrated": calib_test_metrics,
        "test_metrics_uncalibrated": raw_test_metrics,
        "evaluated_at": datetime.utcnow().isoformat() + "Z",
    }
    metrics_path = os.path.join(artifact_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\n✅ Risk model artifacts successfully saved to: {artifact_dir}")
    print(f"   - {model_path} (SHA256: {artifact_hash[:16]}...)")
    print(f"   - {schema_path}")
    print(f"   - {metadata_path}")
    print(f"   - {metrics_path}")

    return all_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SME Risk Prediction Model")
    parser.add_argument("--config", default="configs/risk.yaml", help="Path to risk config file")
    args = parser.parse_args()
    train_risk_model(args.config)
