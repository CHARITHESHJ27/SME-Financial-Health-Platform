"""
Explainability Service.
Transforms SHAP feature attributions and benchmark comparisons into structured,
deterministic business explanations and handles optional local LLM verbalization.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from ml.inference.predictor import SMEPredictor

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Service for generating feature-level financial explanations and risk driver insights.
    """

    def __init__(self, predictor: Optional[SMEPredictor] = None):
        self.predictor = predictor or SMEPredictor()
        self.enable_local_llm = os.getenv("ENABLE_LOCAL_LLM", "false").lower() == "true"

    def generate_explanations(
        self,
        raw_data: Dict[str, Any],
        features: Dict[str, float],
        risk_result: Dict[str, Any],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic SHAP-grounded explanations for top risk factors.
        """
        explanations = self.predictor.explain_risk(raw_data, top_n=top_n)
        return explanations

    def build_executive_summary(
        self,
        company_name: str,
        industry: str,
        risk_result: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        explanations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Construct a structured executive summary linking risk drivers to recommended actions.
        """
        score = risk_result.get("score", 50)
        category = risk_result.get("category", "MEDIUM")
        prob = risk_result.get("probability", 0.5)

        # Separate positive and negative risk factors
        risk_drivers = [e for e in explanations if e.get("direction") == "increases_risk"]
        protective_factors = [e for e in explanations if e.get("direction") == "decreases_risk"]

        summary_paragraphs = []
        if category in ["HIGH", "MEDIUM"]:
            top_driver_names = [e["feature"].replace("_", " ") for e in risk_drivers[:2]]
            drivers_str = " and ".join(top_driver_names) if top_driver_names else "key financial ratios"
            summary_paragraphs.append(
                f"{company_name} presents a {category} estimated financial risk profile (Risk Score: {score}/100, Probability: {prob*100:.1f}%). "
                f"The primary pressure points stem from {drivers_str}."
            )
        else:
            summary_paragraphs.append(
                f"{company_name} demonstrates a strong, {category.lower()}-risk financial health posture (Health Score: {100-score}/100). "
                f"Liquidity and solvency indicators remain well aligned with {industry} industry benchmarks."
            )

        if recommendations:
            top_rec = recommendations[0]
            summary_paragraphs.append(
                f"Priority Action: {top_rec['title']} ({top_rec['confidence']*100:.0f}% confidence) — {top_rec['rationale']}"
            )

        return {
            "headline": f"{category} Financial Risk — Score {score}/100",
            "narrative": " ".join(summary_paragraphs),
            "top_risk_drivers": risk_drivers[:3],
            "top_protective_factors": protective_factors[:3],
            "recommendation_count": len(recommendations),
        }
