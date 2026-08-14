"""
Feature Service.
Coordinates feature extraction, data sanitization, and feature schema definitions for FastAPI routes.
"""

from typing import Dict, Any
from ml.features.feature_pipeline import FinancialFeaturePipeline
from ml.features.validation import validate_raw_financial_data, sanitize_financial_inputs


class FeatureService:
    """
    Service wrapper around FinancialFeaturePipeline for web requests.
    """

    def __init__(self):
        self.pipeline = FinancialFeaturePipeline()

    def compute_features(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Validate, sanitize, and compute 22 engineered financial features."""
        clean_inputs = sanitize_financial_inputs(raw_data)
        return self.pipeline.transform_single(clean_inputs)

    def validate_inputs(self, raw_data: Dict[str, Any]):
        """Run structural validation checks on financial inputs."""
        return validate_raw_financial_data(raw_data)
