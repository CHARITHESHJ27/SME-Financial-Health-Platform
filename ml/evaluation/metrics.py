"""
Evaluation metrics for Risk Prediction and Multi-Label Recommendations.
Includes probability calibration diagnostics, Brier score, ROC-AUC, PR-AUC, and multi-label metrics.
"""

import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.calibration import calibration_curve


def evaluate_risk_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Compute comprehensive metrics for binary risk classification.
    """
    y_pred = (y_prob >= threshold).astype(int)

    roc_auc = float(roc_auc_score(y_true, y_prob))
    pr_auc = float(average_precision_score(y_true, y_prob))
    brier = float(brier_score_loss(y_true, y_prob))
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    cm = confusion_matrix(y_true, y_pred).tolist()

    # Calibration curve (5 bins)
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=5, strategy="uniform")
    calibration_data = {
        "prob_true": [float(x) for x in prob_true],
        "prob_pred": [float(x) for x in prob_pred],
    }

    return {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "confusion_matrix": cm,
        "calibration": calibration_data,
        "sample_count": len(y_true),
        "positive_rate": round(float(np.mean(y_true)), 4),
    }


def evaluate_multilabel_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_names: List[str],
    threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Compute multi-label classification metrics across recommendation intervention codes.
    """
    y_pred = (y_prob >= threshold).astype(int)

    micro_f1 = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    micro_precision = float(precision_score(y_true, y_pred, average="micro", zero_division=0))
    micro_recall = float(recall_score(y_true, y_pred, average="micro", zero_division=0))

    per_class_metrics = {}
    for idx, name in enumerate(target_names):
        code = name.replace("target_", "")
        per_class_metrics[code] = {
            "f1": round(float(f1_score(y_true[:, idx], y_pred[:, idx], zero_division=0)), 4),
            "precision": round(float(precision_score(y_true[:, idx], y_pred[:, idx], zero_division=0)), 4),
            "recall": round(float(recall_score(y_true[:, idx], y_pred[:, idx], zero_division=0)), 4),
            "support": int(np.sum(y_true[:, idx])),
        }

    # Precision@k & Recall@k for Top-3 recommendations
    k = 3
    p_at_k_scores = []
    r_at_k_scores = []
    for i in range(len(y_true)):
        top_k_indices = np.argsort(-y_prob[i])[:k]
        true_positives = np.sum(y_true[i, top_k_indices])
        p_at_k = true_positives / float(k)
        total_positives = np.sum(y_true[i])
        r_at_k = (true_positives / float(total_positives)) if total_positives > 0 else 1.0
        p_at_k_scores.append(p_at_k)
        r_at_k_scores.append(r_at_k)

    return {
        "micro_f1": round(micro_f1, 4),
        "macro_f1": round(macro_f1, 4),
        "micro_precision": round(micro_precision, 4),
        "micro_recall": round(micro_recall, 4),
        "precision_at_3": round(float(np.mean(p_at_k_scores)), 4),
        "recall_at_3": round(float(np.mean(r_at_k_scores)), 4),
        "per_class": per_class_metrics,
        "sample_count": len(y_true),
    }
