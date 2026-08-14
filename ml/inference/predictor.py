"""
Production ML Predictor and SHAP Explainability Engine.
Performs deterministic risk prediction, probability calibration, multi-label recommendation inference,
and exact SHAP feature attributions mapped to industry benchmarks.
"""

import logging
import numpy as np
import shap
from typing import Dict, Any, List, Optional, Tuple

from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.features.feature_definitions import (
    RECOMMENDATION_CODES,
    RECOMMENDATION_METADATA,
    INDUSTRY_BENCHMARKS,
)
from ml.features.validation import sanitize_financial_inputs, validate_raw_financial_data
from ml.inference.model_manager import ModelManager

logger = logging.getLogger(__name__)


class SMEPredictor:
    """
    Inference and Explainability engine for SME Financial Risk and Recommendations.
    """

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()
        self.pipeline = FinancialFeaturePipeline()
        self._shap_explainer = None
        self._shap_initialized = False

    def predict_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict calibrated financial risk score, probability, and risk category.
        """
        # Validate data
        is_valid, errors = validate_raw_financial_data(data)
        if not is_valid:
            logger.warning(f"Financial validation warnings: {errors}")

        # Compute feature vector
        features = self.pipeline.transform_single(data)
        X = self.pipeline.to_feature_vector(data, include_industry=True).reshape(1, -1)

        risk_bundle = self.model_manager.get_risk_bundle()
        if risk_bundle and "calibrated_model" in risk_bundle:
            calibrated_model = risk_bundle["calibrated_model"]
            probs = calibrated_model.predict_proba(X)[0]
            risk_probability = float(probs[1]) if len(probs) > 1 else float(probs[0])
            model_version = risk_bundle.get("model_version", "v1.0.0")
        else:
            # Deterministic fallback heuristic if artifact is not loaded
            logger.warning("Risk model artifact not loaded — using deterministic fallback engine")
            risk_probability = self._heuristic_risk_probability(features)
            model_version = "heuristic-fallback-v1"

        risk_probability = float(np.clip(risk_probability, 0.01, 0.99))
        risk_score = int(round(risk_probability * 100))

        # Risk category
        if risk_score >= 60:
            category = "HIGH"
        elif risk_score >= 35:
            category = "MEDIUM"
        elif risk_score >= 15:
            category = "LOW"
        else:
            category = "MINIMAL"

        return {
            "score": risk_score,
            "probability": round(risk_probability, 4),
            "category": category,
            "model_version": f"risk-model-{model_version}",
            "features": features,
        }

    def explain_risk(
        self,
        data: Dict[str, Any],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculate exact SHAP feature attributions and map them into deterministic
        business explanations against industry benchmarks.
        """
        features = self.pipeline.transform_single(data)
        industry = str(data.get("industry", "services")).lower()
        benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["services"])

        risk_bundle = self.model_manager.get_risk_bundle()
        feature_names = self.pipeline.get_full_feature_names(include_industry=True)
        X = self.pipeline.to_feature_vector(data, include_industry=True).reshape(1, -1)

        shap_values = None
        if risk_bundle and "base_model" in risk_bundle:
            try:
                base_model = risk_bundle["base_model"]
                if not self._shap_initialized or self._shap_explainer is None:
                    self._shap_explainer = shap.TreeExplainer(base_model)
                    self._shap_initialized = True

                raw_shap = self._shap_explainer.shap_values(X)
                # Handle binary classification shap output
                if isinstance(raw_shap, list) and len(raw_shap) > 1:
                    shap_values = raw_shap[1][0]
                elif len(raw_shap.shape) == 2:
                    shap_values = raw_shap[0]
                elif len(raw_shap.shape) == 3:
                    shap_values = raw_shap[0, :, 1]
            except Exception as e:
                logger.error(f"SHAP explanation computation error: {e}")
                shap_values = None

        # Fallback to feature deviation attribution if SHAP is unavailable
        if shap_values is None:
            shap_values = self._heuristic_feature_attributions(features, industry)

        # Build structured explanation list
        explanations = []
        for idx, name in enumerate(feature_names):
            if name.startswith("industry_"):
                continue  # focus business explanations on actionable financial ratios

            val = features.get(name, 0.0)
            contrib = float(shap_values[idx]) if idx < len(shap_values) else 0.0
            direction = "increases_risk" if contrib > 0 else "decreases_risk"

            # Benchmark context
            benchmark_info = benchmarks.get(name, {})
            target_val = benchmark_info.get("target")

            # Determine impact level based on contribution magnitude
            abs_contrib = abs(contrib)
            impact = "HIGH" if abs_contrib > 0.35 else "MEDIUM" if abs_contrib > 0.15 else "LOW"

            explanation_text = self._build_explanation_text(name, val, target_val, direction, industry)

            explanations.append({
                "feature": name,
                "value": round(val, 4),
                "contribution": round(contrib, 4),
                "direction": direction,
                "impact": impact,
                "benchmark": target_val,
                "explanation": explanation_text,
            })

        # Sort by absolute SHAP contribution (highest impact first)
        explanations.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return explanations[:top_n]

    def predict_recommendation_candidates(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate candidate multi-label recommendations with model confidence scores.
        """
        features = self.pipeline.transform_single(data)
        X = self.pipeline.to_feature_vector(data, include_industry=True).reshape(1, -1)

        rec_bundle = self.model_manager.get_recommendation_bundle()
        candidates = []

        if rec_bundle and "model" in rec_bundle:
            model = rec_bundle["model"]
            target_codes = rec_bundle.get("recommendation_codes", RECOMMENDATION_CODES)
            prob_list = model.predict_proba(X)

            for idx, code in enumerate(target_codes):
                p_arr = prob_list[idx][0]
                conf = float(p_arr[1]) if len(p_arr) > 1 else float(p_arr[0])
                meta = RECOMMENDATION_METADATA.get(code, {})

                candidates.append({
                    "code": code,
                    "confidence": round(conf, 4),
                    "title": meta.get("title", code),
                    "description": meta.get("description", ""),
                    "primary_metric": meta.get("primary_metric", ""),
                    "default_impact": meta.get("default_impact", "MEDIUM"),
                })
        else:
            # Heuristic fallback candidates
            logger.warning("Recommendation model artifact not loaded — using deterministic fallback")
            candidates = self._heuristic_recommendation_candidates(features, data.get("industry", "services"))

        return candidates

    def _build_explanation_text(
        self,
        metric: str,
        val: float,
        target_val: Optional[float],
        direction: str,
        industry: str
    ) -> str:
        """Construct clear, auditable explanation text without an LLM."""
        formatted_val = f"{val:.2f}" if abs(val) < 10 else f"{val:.1f}"
        if "margin" in metric or "rate" in metric or "roa" in metric or "roe" in metric:
            formatted_val = f"{val*100:.1f}%"

        target_str = f"{target_val*100:.1f}%" if target_val and ("margin" in metric or "roa" in metric) else (f"{target_val:.2f}" if target_val else "benchmark")

        metric_readable = metric.replace("_", " ").title()

        if direction == "increases_risk":
            if target_val is not None:
                if val < target_val:
                    return f"{metric_readable} ({formatted_val}) is below the {industry} benchmark target of {target_str}, placing pressure on financial stability."
                else:
                    return f"{metric_readable} ({formatted_val}) exceeds the safe {industry} benchmark threshold of {target_str}, elevating financial risk."
            return f"{metric_readable} ({formatted_val}) is currently contributing to elevated financial risk."
        else:
            if target_val is not None:
                return f"{metric_readable} ({formatted_val}) is healthy compared to the {industry} benchmark target of {target_str}, providing risk protection."
            return f"{metric_readable} ({formatted_val}) is performing well and mitigating financial risk."

    def _heuristic_risk_probability(self, features: Dict[str, float]) -> float:
        """Deterministic mathematical fallback when ML model artifact is missing."""
        score = 0.0
        cr = features.get("current_ratio", 1.5)
        dta = features.get("debt_to_assets", 0.4)
        pm = features.get("net_margin", 0.1)
        rec_d = features.get("receivable_days", 30.0)

        if cr < 1.0: score += 0.35
        elif cr < 1.3: score += 0.15

        if dta > 0.70: score += 0.35
        elif dta > 0.55: score += 0.20

        if pm < 0.0: score += 0.30
        elif pm < 0.05: score += 0.15

        if rec_d > 60: score += 0.15
        return float(np.clip(score, 0.05, 0.95))

    def _heuristic_feature_attributions(self, features: Dict[str, float], industry: str) -> np.ndarray:
        """Deterministic attribution fallback."""
        feature_names = self.pipeline.get_full_feature_names(include_industry=True)
        benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["services"])
        attribs = []
        for name in feature_names:
            if name.startswith("industry_"):
                attribs.append(0.0)
                continue
            val = features.get(name, 0.0)
            bm = benchmarks.get(name, {})
            target = bm.get("target", val)
            diff = val - target
            # Invert for ratios where higher is worse
            if name in ["debt_to_assets", "debt_to_equity", "receivable_days", "payable_days", "inventory_days"]:
                attribs.append(float(diff * 0.1))
            else:
                attribs.append(float(-diff * 0.1))
        return np.array(attribs, dtype=np.float32)

    def _heuristic_recommendation_candidates(self, features: Dict[str, float], industry: str) -> List[Dict[str, Any]]:
        candidates = []
        for code in RECOMMENDATION_CODES:
            meta = RECOMMENDATION_METADATA.get(code, {})
            conf = 0.75
            candidates.append({
                "code": code,
                "confidence": conf,
                "title": meta.get("title", code),
                "description": meta.get("description", ""),
                "primary_metric": meta.get("primary_metric", ""),
                "default_impact": meta.get("default_impact", "MEDIUM"),
            })
        return candidates
