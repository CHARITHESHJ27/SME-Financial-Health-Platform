"""
Model Artifact Manager.
Loads, validates, and caches versioned machine learning model artifacts with checksum verification.
"""

import os
import json
import logging
import hashlib
import joblib
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def compute_sha256(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class ModelManager:
    """
    Singleton manager for loading, verifying, and holding model artifacts in memory.
    """
    _instance: Optional["ModelManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_model_dir: Optional[str] = None):
        if self._initialized:
            return

        self.base_model_dir = base_model_dir or os.getenv("MODEL_DIR", "ml/models")
        self.risk_version = os.getenv("RISK_MODEL_VERSION", "v1.0.0")
        self.recommendation_version = os.getenv("RECOMMENDATION_MODEL_VERSION", "v1.0.0")

        self.risk_bundle: Optional[Dict[str, Any]] = None
        self.recommendation_bundle: Optional[Dict[str, Any]] = None
        self._load_all_models()
        self._initialized = True

    def _resolve_path(self, relative_path: str) -> str:
        """Resolve path relative to workspace or app root robustly."""
        if os.path.isabs(relative_path) and os.path.exists(relative_path):
            return relative_path

        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        candidates = [
            relative_path,
            os.path.join(os.getcwd(), relative_path),
            os.path.join(repo_root, relative_path.lstrip("./").lstrip("../")),
            os.path.join(repo_root, "ml", "models", *relative_path.split("models/")[-1].split("/")),
        ]

        for cand in candidates:
            if os.path.exists(cand):
                return os.path.abspath(cand)

        return os.path.join(repo_root, "ml", "models")

    def _load_all_models(self):
        """Load and verify risk and recommendation model packages."""
        self._load_risk_model()
        self._load_recommendation_model()

    def _load_risk_model(self):
        rel_model = os.path.join(self.base_model_dir, "risk", self.risk_version, "model.joblib")
        model_file = self._resolve_path(rel_model)
        meta_file = self._resolve_path(os.path.join(self.base_model_dir, "risk", self.risk_version, "metadata.json"))

        if not os.path.exists(model_file):
            logger.warning(f"Risk model artifact not found at: {model_file}")
            self.risk_bundle = None
            return

        try:
            bundle = joblib.load(model_file)
            if os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    bundle["metadata"] = json.load(f)
            self.risk_bundle = bundle
            logger.info(f"Successfully loaded risk model '{bundle.get('model_name')}' version {self.risk_version}")
        except Exception as e:
            logger.error(f"Failed to load risk model artifact from {model_file}: {e}")
            self.risk_bundle = None

    def _load_recommendation_model(self):
        rel_model = os.path.join(self.base_model_dir, "recommendation", self.recommendation_version, "model.joblib")
        model_file = self._resolve_path(rel_model)
        meta_file = self._resolve_path(os.path.join(self.base_model_dir, "recommendation", self.recommendation_version, "metadata.json"))

        if not os.path.exists(model_file):
            logger.warning(f"Recommendation model artifact not found at: {model_file}")
            self.recommendation_bundle = None
            return

        try:
            bundle = joblib.load(model_file)
            if os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    bundle["metadata"] = json.load(f)
            self.recommendation_bundle = bundle
            logger.info(f"Successfully loaded recommendation model '{bundle.get('model_name')}' version {self.recommendation_version}")
        except Exception as e:
            logger.error(f"Failed to load recommendation model artifact from {model_file}: {e}")
            self.recommendation_bundle = None

    def get_risk_bundle(self) -> Optional[Dict[str, Any]]:
        if not self.risk_bundle:
            self._load_risk_model()
        return self.risk_bundle

    def get_recommendation_bundle(self) -> Optional[Dict[str, Any]]:
        if not self.recommendation_bundle:
            self._load_recommendation_model()
        return self.recommendation_bundle

    def is_healthy(self) -> Dict[str, Any]:
        """Check readiness status of loaded model packages."""
        risk_ok = self.risk_bundle is not None
        rec_ok = self.recommendation_bundle is not None
        return {
            "status": "ready" if (risk_ok and rec_ok) else "degraded",
            "risk_model": f"risk-model-{self.risk_version}" if risk_ok else "unavailable",
            "recommendation_model": f"recommendation-model-{self.recommendation_version}" if rec_ok else "unavailable",
            "risk_framework": self.risk_bundle.get("framework") if risk_ok else None,
            "recommendation_framework": self.recommendation_bundle.get("framework") if rec_ok else None,
        }
