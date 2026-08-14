# System Architecture — SME Financial Health Platform

## 1. High-Level Architecture Overview

The SME Financial Health Platform is an explainable, production-grade machine learning system designed to analyze SME financial health, quantify risk with calibrated probabilities, generate prioritized treasury and operational interventions, and provide deterministic, metric-grounded explanations.

```
Financial Statements (CSV / XLSX / JSON)
               │
               ▼
┌──────────────────────────────────────────────┐
│  Validation & Data Integrity Layer           │
│  - Accounting equation checks                │
│  - Boundary & non-negativity enforcement     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Feature Engineering Pipeline                │
│  - 22 Engineered Financial Ratios            │
│  - Profitability, Liquidity, Leverage,       │
│    Efficiency, Working Capital & Cash Flow   │
│  - Industry Benchmark Cross-Referencing      │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┴───────────────────────────────┐
       ▼                                       ▼
┌──────────────────────────────┐  ┌───────────────────────────────────┐
│ Supervised Risk Engine       │  │ Multi-Label Recommendation Engine │
│ - GBDT Classifier            │  │ - Multi-Output Tree Classifier    │
│ - Isotonic CalibratedCV      │  │ - 8 Strategic Recommendation Codes│
│ - P(Distress) -> Score 0-100 │  │ - Multi-Label Confidence Probabilities
└──────────────┬───────────────┘  └─────────────────┬─────────────────┘
               │                                    │
               ▼                                    ▼
┌──────────────────────────────┐  ┌───────────────────────────────────┐
│ SHAP Explainability Engine   │  │ Deterministic Rule & Ranking      │
│ - TreeSHAP Attributions      │  │ - Rejection of Contradictory Advice
│ - Direction & Impact Rating  │  │ - Severity & Impact Scoring       │
│ - Root-Cause Rationale       │  │ - Guaranteed 0% Invalid Advice Rate│
└──────────────┬───────────────┘  └─────────────────┬─────────────────┘
               │                                    │
               └───────────────┬────────────────────┘
                               ▼
┌──────────────────────────────────────────────┐
│  FastAPI REST API Layer                      │
│  - Idempotency Hashing & Response Serving    │
│  - Prometheus / Liveness / Readiness Probes  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  React Analytics Dashboard                   │
│  - Calibrated Risk Gauge & Tiers             │
│  - SHAP Factor Contribution Visuals          │
│  - Ranked Recommendations with Rationale     │
└──────────────────────────────────────────────┘
```

---

## 2. Key Subsystems

### 2.1 Feature Pipeline (`ml/features/`)
- Pure Python deterministic transformations.
- Complete divide-by-zero protection (`ε = 1e-6`) and outlier clipping.
- Schema versioned via `FEATURE_VERSION = "v1.0.0"`.

### 2.2 Model Manager & Inference (`ml/inference/`)
- **Singleton Lifecycle**: Loads and caches trained model artifacts on startup. Models are **never** trained at request time.
- **Integrity Verification**: Verifies SHA-256 artifact hashes against metadata before serving.
- **Fail-safe Fallback**: In the event of missing or corrupted artifacts, defaults to deterministic financial heuristic engines.

### 2.3 Rule Validation & Ranking (`backend/app/services/recommendation_service.py`)
- **Constraint Filtering**: Enforces financial sanity rules to prevent contradictory advice (e.g. DSO < 30 cannot receive receivables collection advice; services businesses cannot receive physical inventory advice).
- **Multi-Factor Priority Formula**:
  $$\text{Priority Score} = 0.40 \cdot \text{Confidence} + 0.35 \cdot \text{Severity} + 0.25 \cdot \text{Impact}$$

### 2.4 Explainability (`backend/app/services/explanation_service.py`)
- Computes exact local SHAP feature attributions.
- Merges metric values with sector-level benchmark percentiles to produce transparent narratives.
- Operates with **zero external API calls / 0 LLM tokens**.

---

## 3. Database Schema & Idempotency
- Uses PostgreSQL with JSON columns for flexible persistence of `shap_explanations`, `financial_ratios`, and `executive_summary`.
- **Idempotent Hashing**:
  $$\text{data\_hash} = \text{SHA256}(\text{company\_id} + \text{inputs} + \text{feature\_version} + \text{model\_version})$$
  Identical financial assessments return cached results, preventing redundant computation.
