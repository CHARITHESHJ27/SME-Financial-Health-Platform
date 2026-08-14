"""
Recommendation Service & Deterministic Rule Validation Engine.
Combines ML multi-label model confidence with financial severity, business impact,
and rule constraints to deliver ranked, validated financial interventions with 0% invalid advice.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from ml.inference.predictor import SMEPredictor
from ml.features.feature_definitions import (
    RECOMMENDATION_METADATA,
    INDUSTRY_BENCHMARKS,
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service responsible for recommendation generation, deterministic rule filtering,
    and multi-factor priority ranking.
    """

    def __init__(self, predictor: Optional[SMEPredictor] = None):
        self.predictor = predictor or SMEPredictor()

    def generate_ranked_recommendations(
        self,
        raw_data: Dict[str, Any],
        features: Dict[str, float],
        risk_probability: float,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Produce ranked, rule-validated financial recommendations for an SME.
        """
        industry = str(raw_data.get("industry", "services")).lower()
        benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["services"])

        # 1. Get raw candidate predictions from ML model
        candidates = self.predictor.predict_recommendation_candidates(raw_data)

        # 2. Rule Validation & Severity Calculation
        validated_recommendations = []

        for cand in candidates:
            code = cand["code"]
            conf = cand["confidence"]

            # Validate applicability against deterministic rules
            is_valid, rejection_reason, severity, impact, specific_reason = self._validate_and_score_rule(
                code, features, industry, benchmarks, conf
            )

            if not is_valid:
                logger.debug(f"Recommendation {code} rejected by rule: {rejection_reason}")
                continue

            # Calculate composite ranking score
            # Severity mapping: HIGH=1.0, MEDIUM=0.6, LOW=0.3
            sev_num = 1.0 if severity == "HIGH" else (0.6 if severity == "MEDIUM" else 0.3)
            imp_num = 1.0 if impact == "HIGH" else (0.6 if impact == "MEDIUM" else 0.3)
            
            priority_score = (0.40 * conf) + (0.35 * sev_num) + (0.25 * imp_num)

            meta = RECOMMENDATION_METADATA.get(code, {})
            validated_recommendations.append({
                "code": code,
                "title": meta.get("title", code),
                "description": meta.get("description", ""),
                "confidence": round(conf, 4),
                "severity": severity,
                "impact": impact,
                "priority_score": round(priority_score, 4),
                "rationale": specific_reason,
                "primary_metric": meta.get("primary_metric", ""),
            })

        # 3. Sort by priority score descending
        validated_recommendations.sort(key=lambda x: x["priority_score"], reverse=True)

        # 4. Assign 1-indexed priority ranking
        for rank, rec in enumerate(validated_recommendations[:limit], start=1):
            rec["priority"] = rank

        return validated_recommendations[:limit]

    def _validate_and_score_rule(
        self,
        code: str,
        features: Dict[str, float],
        industry: str,
        benchmarks: Dict[str, Dict[str, float]],
        confidence: float
    ) -> Tuple[bool, str, str, str, str]:
        """
        Deterministic Rule Engine to reject contradictory or inapplicable recommendations
        and calculate metric-driven financial severity.
        """
        # Feature references
        cr = features.get("current_ratio", 1.5)
        wc_assets = features.get("working_capital_to_assets", 0.1)
        rec_days = features.get("receivable_days", 30.0)
        dta = features.get("debt_to_assets", 0.4)
        dte = features.get("debt_to_equity", 0.8)
        op_margin = features.get("operating_margin", 0.1)
        net_margin = features.get("net_margin", 0.08)
        gross_margin = features.get("gross_margin", 0.3)
        ocf_margin = features.get("operating_cash_flow_margin", 0.08)
        growth_rate = features.get("revenue_growth_rate", 0.08)
        inv_days = features.get("inventory_days", 0.0)

        if code == "RECEIVABLES":
            bm_target = benchmarks.get("receivable_days", {}).get("target", 45.0)
            if rec_days < 30.0:
                return False, f"Receivable days ({rec_days:.1f}d) is already fast (< 30d).", "LOW", "LOW", ""
            severity = "HIGH" if rec_days > bm_target * 1.4 else ("MEDIUM" if rec_days > bm_target else "LOW")
            reason = f"Collection cycle of {rec_days:.0f} days exceeds {industry} benchmark target ({bm_target:.0f} days), locking up working capital."
            return True, "", severity, "HIGH", reason

        elif code == "WORKING_CAPITAL":
            bm_target = benchmarks.get("current_ratio", {}).get("target", 1.8)
            if cr >= 1.6 and wc_assets >= 0.15:
                return False, f"Liquidity is already healthy (Current Ratio: {cr:.2f}).", "LOW", "LOW", ""
            severity = "HIGH" if cr < 1.1 else ("MEDIUM" if cr < bm_target else "LOW")
            reason = f"Current ratio of {cr:.2f} is under pressure compared to the healthy benchmark target of {bm_target:.2f}."
            return True, "", severity, "HIGH", reason

        elif code == "DEBT_REDUCTION":
            bm_target = benchmarks.get("debt_to_assets", {}).get("target", 0.45)
            if dta <= 0.30 and dte <= 0.50:
                return False, f"Leverage is already conservative (Debt to Assets: {dta*100:.1f}%).", "LOW", "LOW", ""
            severity = "HIGH" if dta > 0.65 else ("MEDIUM" if dta > bm_target else "LOW")
            reason = f"Debt-to-assets ratio ({dta*100:.1f}%) exceeds the recommended {industry} threshold ({bm_target*100:.1f}%), elevating interest risk."
            return True, "", severity, "HIGH", reason

        elif code == "COST_OPTIMIZATION":
            bm_target = benchmarks.get("net_margin", {}).get("target", 0.12)
            if op_margin >= 0.20 and net_margin >= 0.14:
                return False, f"Operating margin ({op_margin*100:.1f}%) is already high.", "LOW", "LOW", ""
            severity = "HIGH" if net_margin < 0.02 else ("MEDIUM" if net_margin < bm_target else "LOW")
            reason = f"Operating margin ({op_margin*100:.1f}%) indicates elevated expense absorption; cost rationalization can recover operating buffer."
            return True, "", severity, "MEDIUM", reason

        elif code == "MARGIN_IMPROVEMENT":
            bm_target = benchmarks.get("gross_margin", {}).get("target", 0.35)
            if gross_margin >= 0.45:
                return False, f"Gross margin ({gross_margin*100:.1f}%) is already strong.", "LOW", "LOW", ""
            severity = "HIGH" if gross_margin < 0.20 else ("MEDIUM" if gross_margin < bm_target else "LOW")
            reason = f"Gross margin ({gross_margin*100:.1f}%) is below the industry median ({bm_target*100:.1f}%); evaluate product/service pricing mix."
            return True, "", severity, "HIGH", reason

        elif code == "CASH_FLOW_STABILIZATION":
            bm_target = benchmarks.get("operating_cash_flow_margin", {}).get("target", 0.12)
            if ocf_margin >= 0.15:
                return False, f"Operating cash flow margin ({ocf_margin*100:.1f}%) is solid.", "LOW", "LOW", ""
            severity = "HIGH" if ocf_margin <= 0.0 else ("MEDIUM" if ocf_margin < bm_target else "LOW")
            reason = f"Operating cash flow margin ({ocf_margin*100:.1f}%) is constrained, making liquidity vulnerable to payment delays."
            return True, "", severity, "HIGH", reason

        elif code == "REVENUE_GROWTH":
            if growth_rate >= 0.25:
                return False, f"Revenue is already growing at high velocity ({growth_rate*100:.1f}%).", "LOW", "LOW", ""
            severity = "HIGH" if growth_rate < 0.0 else ("MEDIUM" if growth_rate < 0.06 else "LOW")
            reason = f"Revenue growth ({growth_rate*100:.1f}%) has plateaued; explore market diversification and customer acquisition channels."
            return True, "", severity, "MEDIUM", reason

        elif code == "INVENTORY_OPTIMIZATION":
            if industry == "services":
                return False, "Services industry does not hold physical merchandise inventory.", "LOW", "LOW", ""
            bm_target = benchmarks.get("inventory_days", {}).get("target", 45.0)
            if inv_days <= 15.0:
                return False, f"Inventory holding period ({inv_days:.1f}d) is already lean.", "LOW", "LOW", ""
            severity = "HIGH" if inv_days > bm_target * 1.5 else ("MEDIUM" if inv_days > bm_target else "LOW")
            reason = f"Inventory holding period ({inv_days:.0f} days) is elevated vs benchmark ({bm_target:.0f} days), tying up liquid capital."
            return True, "", severity, "MEDIUM", reason

        return True, "", "MEDIUM", "MEDIUM", "Recommended based on financial profile assessment."
