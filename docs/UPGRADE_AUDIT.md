# SME Financial Health Platform — Phase 0: Repository Audit & Baseline Report

**Audit Date:** August 14, 2026  
**Audited Target:** SME Financial Health Platform (`backend/`, `frontend/`, `data/`, `scripts/`, `deploy/`)  
**Scope:** Architectural assessment, ML/LLM dependency audit, technical debt discovery, and migration roadmap.

---

## 1. Executive Summary

The SME Financial Health Platform was originally structured as a full-stack financial monitoring application comprising a FastAPI backend, PostgreSQL database, React dashboard, and heuristic rule engines coupled with an external OpenAI GPT integration (`LLMService`) for natural language financial recommendations.

This audit establishes the baseline before executing the **Production-Grade ML Upgrade**, transforming the platform into a self-contained, reproducible, explainable ML financial risk prediction and multi-label recommendation system with SHAP feature attributions and zero mandatory external API dependencies.

---

## 2. Current Architecture & Component Inventory

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│   (Dashboard.js, Recommendations.js, Analytics.js, Charts)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / Multipart)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│  ├── Auth & Security (JWT, bcrypt, rate limiting)          │
│  ├── Routes (Companies, Assess, Upload, Benchmarks, Forecast)│
│  └── Services:                                              │
│      ├── FinancialAssessmentService                         │
│      ├── CompanyService                                     │
│      ├── FileProcessingService                              │
│      ├── ValidationService                                  │
│      ├── GSTMockService & BankingMockService                │
│      └── LLMService (OpenAI / Groq / Heuristic Fallback)    │
│  └── Core Engines:                                          │
│      ├── FinancialAnalyzer (Heuristic ratio calculation)    │
│      ├── CreditScorer (Static weighted score 0-100)         │
│      └── IndustryBenchmarks (Static percentiles)            │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy ORM
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL / SQLite Database               │
│  (organizations, users, companies, financial_statements,   │
│   financial_assessments, industry_benchmarks)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Current ML Flow vs. OpenAI Flow

### 3.1 Current ML Flow (Pre-Upgrade)
- **Supervised ML Models:** **None** (No scikit-learn/XGBoost/LightGBM model artifacts were trained or loaded in the active inference path).
- **Credit Scoring:** Hand-crafted weighted sum inside `CreditScorer` (`core/scoring.py`):
  $$\text{Score} = 0.25 \times \text{Liquidity} + 0.30 \times \text{Profitability} + 0.25 \times \text{Leverage} + 0.10 \times \text{Efficiency} + 0.10 \times \text{Growth} + \text{Size Adjustment}$$
- **Heuristic Thresholds:** Fixed step functions (e.g. Current ratio $\ge 2.0 \to 100$, $\ge 1.5 \to 80$, etc.).
- **Forecasting:** Linear extrapolation based on 3+ historical assessments (`FinancialAnalyzer.generate_forecast`).

### 3.2 Current OpenAI / LLM Flow
- Implemented in `backend/app/services/llm_service.py`.
- **Methods:**
  - `generate_insights(financial_data, ratios, language)`
  - `generate_cost_optimization_suggestions(financial_data, language)`
  - `generate_growth_recommendations(financial_data, industry, language)`
- **Execution Chain:** Attempts OpenAI (`gpt-3.5-turbo`), falls back to Groq (`llama3-8b-8192`), falls back to deterministic string rules (`_fallback_insights`, `_fallback_cost_suggestions`, `_fallback_growth`).
- **Dependencies Identified:**
  - `backend/requirements.txt` (`openai==1.3.7`, `groq>=1.0.0`)
  - `backend/health_check.py` (`required_vars = ["OPENAI_API_KEY"]` — causing health checks to fail if key is omitted)
  - `backend/app/main.py` (API docstrings stating OpenAI GPT dependency)
  - `.env.example`, `render.yaml`, `README.md`

---

## 4. Current API Flow & Endpoints

| Method | Endpoint | Handler | Current Behavior | Target Upgrade |
|---|---|---|---|---|
| `POST` | `/api/v1/companies/` | `create_company` | Validates & saves company | Preserved (Backward compatible) |
| `POST` | `/api/v1/companies/{id}/assess` | `assess_financial_health` | Runs `FinancialAssessmentService`, computes heuristic score | Runs **Feature Pipeline $\to$ Calibrated Risk ML Model $\to$ Multi-label Recommendation ML $\to$ Rule Engine $\to$ SHAP Explanations** |
| `POST` | `/api/v1/upload-financial-data/{id}` | `upload_financial_data` | Hardcoded dummy assessment or basic file parser | Integrates with Feature Pipeline & ML assessment engine |
| `GET` | `/api/v1/companies/{id}/dashboard` | `get_dashboard_data` | Returns latest health scores, risks, recommendations | Returns ML risk score, probability, risk tier, ranked recommendations with priority/impact, SHAP risk drivers |
| `GET` | `/api/v1/industries/benchmarks/{ind}` | `get_industry_benchmarks` | Returns static benchmark percentiles | Enhanced benchmark comparison engine |
| `GET` | `/api/v1/companies/{id}/forecast` | `get_financial_forecast` | 12-month trend projection | Preserved & enriched |
| `GET` | `/api/v1/companies/{id}/gst-compliance`| `get_gst_compliance` | Mock GST analysis | Preserved |
| `GET` | `/health` | `health_check` | Returns basic status | Enriched with `/health/live`, `/health/ready`, `/health/model` |

---

## 5. Existing Model Artifacts & Data Sources

- **Model Artifacts:** None currently exist in the repository (prior models were purely algorithmic).
- **Data Files:**
  - `data/sample_csv/retail_sample.csv` (12-month monthly SME income/balance sheet figures)
  - `data/benchmarks/industry_avg.csv` (Industry median financial ratios)
  - `data/sample_csv/sample_data.csv`, `test_financial_data.csv`
- **Data Gap Identified:** A robust, statistically sound, synthetic SME training dataset with realistic financial correlations across multiple industries is required to train the Risk Model and Multi-label Recommendation Engine.

---

## 6. Technical Debt & Code Quality Findings

1. **Mandatory OpenAI Check in Healthcheck:** `backend/health_check.py` hard-coded `OPENAI_API_KEY` as a mandatory variable, halting health checks if absent.
2. **Missing Feature Pipeline Modularization:** Ratio calculation was embedded in `FinancialAnalyzer` without feature schema versioning, division-by-zero protection across all metrics, or standardized vectorization for ML models.
3. **Hard-coded Heuristics in Scoring:** `CreditScorer` relied on arbitrary step intervals rather than a calibrated statistical probability.
4. **No Model Registry or Versioning:** Model loading and feature schemas were not versioned or validated with checksums.
5. **No SHAP Feature Attribution:** Explanations were static string templates disconnected from model coefficients/tree splits.
6. **Testing Gap:** `test_platform.py` only contained 3 shallow smoke tests; unit test coverage for ratios, missing value handling, outlier rejection, ML inference, and API contract was missing.
7. **Frontend Explainability Gap:** Dashboard lacked visual representation of feature-level attributions (SHAP bars) and structured recommendation metadata (confidence %, priority, financial severity, business rationale).

---

## 7. Migration Plan & File Impact Matrix

### 7.1 Files to Modify
- `backend/requirements.txt`: Remove mandatory OpenAI, add `xgboost`, `shap`, `joblib`, `scikit-learn`.
- `backend/health_check.py`: Remove OpenAI dependency check, add model artifact readiness checks.
- `backend/app/main.py`: Update API description and health endpoints (`/health/live`, `/health/ready`, `/health/model`).
- `backend/app/api/routes.py`: Connect assessment routes to the new ML Inference & Recommendation engine.
- `backend/app/services/financial_assessment_service.py`: Refactor to orchestrate feature pipeline, risk inference, recommendation engine, SHAP explainer, and deterministic rule validation.
- `backend/app/models/schemas.py`: Update `FinancialAssessment` to store ML metadata, calibrated probabilities, model versions, and feature attributions.
- `frontend/src/components/Dashboard.js`: Add ML Risk Score display, calibrated probability gauge, SHAP Risk Drivers visualization.
- `frontend/src/components/Recommendations.js`: Upgrade to render multi-label interventions with confidence badges, impact/severity ratings, and explainability drawers.
- `.env.example`, `.env.prod.example`, `docker-compose.yml`, `Dockerfile`.

### 7.2 Files to Create
- `ml/features/feature_definitions.py`, `feature_pipeline.py`, `validation.py`
- `ml/data/generate_dataset.py`, `schemas/dataset_schema.py`
- `ml/training/train_risk.py`, `train_recommendation.py`, `config.py`
- `ml/evaluation/evaluate_risk.py`, `evaluate_recommendation.py`, `metrics.py`
- `ml/inference/predictor.py`, `model_manager.py`
- `backend/app/services/recommendation_service.py`
- `backend/app/services/explanation_service.py`
- `backend/app/services/feature_service.py`
- `tests/unit/test_features.py`, `test_scoring.py`, `test_recommendations.py`, `test_rules.py`, `test_explanations.py`
- `tests/integration/test_assessment_api.py`, `test_model_loading.py`
- `tests/regression/test_prediction_regression.py`
- `docs/ARCHITECTURE.md`, `docs/MODEL_CARD.md`, `docs/ML_PIPELINE.md`
- `configs/risk.yaml`, `configs/recommendation.yaml`, `configs/development.yaml`, `configs/production.yaml`

### 7.3 Files Kept Backward-Compatible
- `backend/app/auth.py` (Authentication, JWT token verification, RBAC)
- `backend/app/services/company_service.py` (Company lifecycle and uniqueness constraints)
- `backend/app/services/gst_mock.py` (GST compliance mock service)
- `backend/app/services/banking_mock.py` (Banking mock service)
- `backend/app/database.py` (Engine configuration and session lifecycle)
- `frontend/src/context/AuthContext.js`, `frontend/src/pages/Login.js`, `Signup.js`, `Companies.js`, `OrgOverview.js`

---

## 8. Conclusion & Sign-Off

The baseline repository inspection is complete. No production code was modified during this audit. The platform is ready for systematic implementation according to the 20-phase blueprint.
