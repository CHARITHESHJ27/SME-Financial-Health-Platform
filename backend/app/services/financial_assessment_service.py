"""
Financial Assessment Orchestrator Service.
Coordinates feature engineering, calibrated ML risk prediction, multi-label recommendations,
deterministic rule validation, and SHAP explainability.
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.schemas import Company, FinancialAssessment
from app.models.requests import FinancialDataRequest
from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.features.validation import validate_raw_financial_data, sanitize_financial_inputs
from ml.inference.predictor import SMEPredictor
from app.services.recommendation_service import RecommendationService
from app.services.explanation_service import ExplanationService

logger = logging.getLogger(__name__)


class FinancialAssessmentService:
    """
    Production-grade financial assessment orchestrator.
    """

    def __init__(self, db: Session):
        self.db = db
        self.pipeline = FinancialFeaturePipeline()
        self.predictor = SMEPredictor()
        self.recommendation_service = RecommendationService(self.predictor)
        self.explanation_service = ExplanationService(self.predictor)

    def assess_financial_health(
        self,
        company: Company,
        financial_data: FinancialDataRequest
    ) -> Dict[str, Any]:
        """
        Execute end-to-end ML financial assessment for a company.
        """
        raw_dict = self._prepare_raw_dict(company, financial_data)

        # 1. Strict Validation
        is_valid, errors = validate_raw_financial_data(raw_dict)
        if not is_valid:
            logger.warning(f"Financial validation failed for company {company.id}: {errors}")
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_FINANCIAL_DATA",
                    "message": errors[0] if errors else "Invalid financial data",
                    "errors": errors
                }
            )

        # 2. Compute 22 Engineered Financial Ratios
        features = self.pipeline.transform_single(raw_dict)

        # 3. Supervised Calibrated Risk Model Inference
        risk_result = self.predictor.predict_risk(raw_dict)

        # 4. Multi-Label Recommendation Inference + Rule Validation + Ranking
        recommendations = self.recommendation_service.generate_ranked_recommendations(
            raw_data=raw_dict,
            features=features,
            risk_probability=risk_result["probability"],
            limit=5
        )

        # 5. SHAP Feature Attribution & Deterministic Explanations
        explanations = self.explanation_service.generate_explanations(
            raw_data=raw_dict,
            features=features,
            risk_result=risk_result,
            top_n=5
        )

        # 6. Executive Summary
        exec_summary = self.explanation_service.build_executive_summary(
            company_name=company.name,
            industry=company.industry,
            risk_result=risk_result,
            recommendations=recommendations,
            explanations=explanations
        )

        # 7. Compute Idempotency / Cache Hash
        data_hash = self._compute_data_hash(company.id, raw_dict, risk_result["model_version"])

        # 8. Check for existing identical assessment (idempotency check)
        existing_assessment = self.db.query(FinancialAssessment).filter(
            FinancialAssessment.company_id == company.id,
            FinancialAssessment.data_hash == data_hash
        ).order_by(FinancialAssessment.assessment_date.desc()).first()

        if existing_assessment:
            db_assessment = existing_assessment
            logger.info(f"Reusing existing idempotent assessment ID {db_assessment.id} for company {company.id}")
        else:
            db_assessment = self._save_assessment(
                company_id=company.id,
                raw_dict=raw_dict,
                features=features,
                risk_result=risk_result,
                recommendations=recommendations,
                explanations=explanations,
                exec_summary=exec_summary,
                data_hash=data_hash
            )

        # 9. Format structured response (Section 16 contract)
        return {
            "status": "success",
            "assessment_id": db_assessment.id,
            "company_id": company.id,
            "company_name": company.name,
            "data": {
                "risk": {
                    "score": risk_result["score"],
                    "probability": risk_result["probability"],
                    "category": risk_result["category"],
                    "model_version": risk_result["model_version"],
                },
                "recommendations": recommendations,
                "explanations": explanations,
                "executive_summary": exec_summary,
                "financial_ratios": features,
            },
            # Backward-compatible fields
            "assessment_result": {
                "overall_health_score": float(100 - risk_result["score"]),
                "financial_ratios": features,
                "risk_analysis": {
                    "risk_level": risk_result["category"],
                    "risk_score": risk_result["score"],
                    "risk_probability": risk_result["probability"],
                    "identified_risks": [e["explanation"] for e in explanations if e["direction"] == "increases_risk"],
                },
                "recommendations": [r["title"] + " — " + r["rationale"] for r in recommendations],
                "cost_optimization": [
                    {
                        "category": r["title"],
                        "potential_savings": "Actionable",
                        "recommendation": r["rationale"],
                        "priority": r["severity"]
                    }
                    for r in recommendations if r["code"] in ["COST_OPTIMIZATION", "MARGIN_IMPROVEMENT", "RECEIVABLES"]
                ]
            }
        }

    def _prepare_raw_dict(
        self,
        company: Company,
        data: FinancialDataRequest
    ) -> Dict[str, Any]:
        return {
            "industry": company.industry,
            "revenue": float(data.revenue or 0.0),
            "total_expenses": float(data.total_expenses or 0.0),
            "current_assets": float(data.current_assets or 0.0),
            "current_liabilities": float(data.current_liabilities or 0.0),
            "total_assets": float(data.total_assets or 0.0),
            "total_debt": float(data.total_debt or 0.0),
            "revenue_growth_rate": float(data.revenue_growth_rate or 0.0),
            "inventory": float(data.inventory or 0.0),
            "accounts_receivable": float(data.accounts_receivable or 0.0),
            "accounts_payable": float(data.accounts_payable or 0.0),
        }

    def _compute_data_hash(
        self,
        company_id: int,
        raw_dict: Dict[str, Any],
        model_version: str
    ) -> str:
        serialized = json.dumps({
            "company_id": company_id,
            "inputs": {k: raw_dict[k] for k in sorted(raw_dict.keys())},
            "model_version": model_version,
            "feature_version": self.pipeline.version,
        }, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _save_assessment(
        self,
        company_id: int,
        raw_dict: Dict[str, Any],
        features: Dict[str, float],
        risk_result: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        explanations: List[Dict[str, Any]],
        exec_summary: Dict[str, Any],
        data_hash: str
    ) -> FinancialAssessment:
        """Persist assessment metadata to PostgreSQL."""
        # Calculate derived component scores (0-100)
        health_score = float(max(0, min(100, 100 - risk_result["score"])))
        liquidity_score = float(min(100.0, max(0.0, features.get("current_ratio", 1.0) * 40.0)))
        profitability_score = float(min(100.0, max(0.0, (features.get("net_margin", 0.0) + 0.10) * 350.0)))
        leverage_score = float(min(100.0, max(0.0, (1.0 - features.get("debt_to_assets", 0.5)) * 100.0)))

        db_assessment = FinancialAssessment(
            company_id=company_id,
            overall_health_score=health_score,
            liquidity_score=liquidity_score,
            profitability_score=profitability_score,
            leverage_score=leverage_score,
            risk_score=float(risk_result["score"]),
            risk_probability=float(risk_result["probability"]),
            risk_category=risk_result["category"],
            model_version=risk_result["model_version"],
            feature_version=self.pipeline.version,
            data_hash=data_hash,
            credit_risk_level=risk_result["category"],
            financial_risks=[e["explanation"] for e in explanations if e["direction"] == "increases_risk"],
            ai_recommendations=[r["title"] + ": " + r["rationale"] for r in recommendations],
            cost_optimization_suggestions=[
                {
                    "category": r["title"],
                    "potential_savings": "Actionable",
                    "suggestion": r["rationale"],
                    "priority": r["severity"]
                }
                for r in recommendations if r["code"] in ["COST_OPTIMIZATION", "MARGIN_IMPROVEMENT", "RECEIVABLES"]
            ],
            shap_explanations=explanations,
            financial_ratios=features,
            executive_summary=exec_summary,
        )

        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment