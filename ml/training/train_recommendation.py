"""
Training Pipeline for Multi-Label Financial Recommendation Model.
Predicts candidate interventions across 8 financial improvement codes:
WORKING_CAPITAL, RECEIVABLES, DEBT_REDUCTION, COST_OPTIMIZATION,
MARGIN_IMPROVEMENT, CASH_FLOW_STABILIZATION, REVENUE_GROWTH, INVENTORY_OPTIMIZATION.
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

from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier

from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.data.generate_dataset import save_datasets
from ml.training.config import load_config
from ml.evaluation.metrics import evaluate_multilabel_predictions


def get_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file for artifact integrity checking."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def train_recommendation_model(config_path: str = "configs/recommendation.yaml") -> Dict[str, Any]:
    """Execute complete multi-label recommendation model training and artifact export."""
    config = load_config(config_path)

    # 1. Load data
    train_path = config["data"]["train_path"]
    val_path = config["data"]["val_path"]
    test_path = config["data"]["test_path"]
    target_columns = config["data"]["target_columns"]

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
    y_train = train_df[target_columns].values.astype(int)

    X_val = np.array([pipeline.to_feature_vector(row.to_dict()) for _, row in val_df.iterrows()])
    y_val = val_df[target_columns].values.astype(int)

    X_test = np.array([pipeline.to_feature_vector(row.to_dict()) for _, row in test_df.iterrows()])
    y_test = test_df[target_columns].values.astype(int)

    print(f"Dataset shapes: Train={X_train.shape}, Targets={y_train.shape}")
    print(f"Target codes ({len(target_columns)}): {[c.replace('target_', '') for c in target_columns]}")

    # 2. Train Multi-Output Random Forest Classifier
    base_rf = RandomForestClassifier(
        n_estimators=config["model"]["params"]["n_estimators"],
        max_depth=config["model"]["params"]["max_depth"],
        min_samples_split=config["model"]["params"]["min_samples_split"],
        class_weight="balanced_subsample",
        random_state=config["seed"],
        n_jobs=-1
    )
    multi_model = MultiOutputClassifier(base_rf, n_jobs=-1)
    multi_model.fit(X_train, y_train)

    # 3. Predict Probabilities for Multi-Label
    # predict_proba returns list of (n_samples, 2) arrays, one per output target
    def extract_positive_probs(model, X):
        prob_list = model.predict_proba(X)
        return np.column_stack([p[:, 1] if p.shape[1] > 1 else np.zeros(len(X)) for p in prob_list])

    val_probs = extract_positive_probs(multi_model, X_val)
    test_probs = extract_positive_probs(multi_model, X_test)

    val_metrics = evaluate_multilabel_predictions(y_val, val_probs, target_columns)
    test_metrics = evaluate_multilabel_predictions(y_test, test_probs, target_columns)

    print(f"\nMulti-Label Model Evaluation (TEST SET):")
    print(f"  • Micro F1:        {test_metrics['micro_f1']:.4f}")
    print(f"  • Macro F1:        {test_metrics['macro_f1']:.4f}")
    print(f"  • Precision@3:     {test_metrics['precision_at_3']:.4f}")
    print(f"  • Recall@3:        {test_metrics['recall_at_3']:.4f}")
    print("\nPer-Code Performance:")
    for code, m in test_metrics["per_class"].items():
        print(f"  • {code:25s} | F1: {m['f1']:.4f} | Prec: {m['precision']:.4f} | Rec: {m['recall']:.4f} | Support: {m['support']}")

    # 4. Export Artifacts
    artifact_dir = config["output"]["artifact_dir"]
    os.makedirs(artifact_dir, exist_ok=True)

    model_artifact = {
        "model": multi_model,
        "target_columns": target_columns,
        "recommendation_codes": [c.replace("target_", "") for c in target_columns],
        "feature_names": feature_names,
        "feature_version": config["features"]["feature_version"],
        "model_version": config["version"],
        "model_name": config["model_name"],
    }
    model_path = os.path.join(artifact_dir, "model.joblib")
    joblib.dump(model_artifact, model_path)

    artifact_hash = get_file_hash(model_path)

    # Save feature schema
    schema_data = {
        "feature_version": config["features"]["feature_version"],
        "feature_names": feature_names,
        "target_codes": [c.replace("target_", "") for c in target_columns],
        "feature_count": len(feature_names),
    }
    schema_path = os.path.join(artifact_dir, "feature_schema.json")
    with open(schema_path, "w") as f:
        json.dump(schema_data, f, indent=2)

    # Save metadata
    metadata = {
        "model_name": config["model_name"],
        "version": config["version"],
        "framework": "sklearn-multioutput-randomforest",
        "feature_version": config["features"]["feature_version"],
        "training_dataset": "sme-synthetic-v1",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "artifact_file": "model.joblib",
        "artifact_sha256": artifact_hash,
        "python_version": sys.version.split()[0],
    }
    metadata_path = os.path.join(artifact_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save metrics
    all_metrics = {
        "model_version": config["version"],
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "evaluated_at": datetime.utcnow().isoformat() + "Z",
    }
    metrics_path = os.path.join(artifact_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\n✅ Recommendation model artifacts successfully saved to: {artifact_dir}")
    print(f"   - {model_path} (SHA256: {artifact_hash[:16]}...)")
    print(f"   - {schema_path}")
    print(f"   - {metadata_path}")
    print(f"   - {metrics_path}")

    return all_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SME Multi-Label Recommendation Model")
    parser.add_argument("--config", default="configs/recommendation.yaml", help="Path to recommendation config file")
    args = parser.parse_args()
    train_recommendation_model(args.config)
