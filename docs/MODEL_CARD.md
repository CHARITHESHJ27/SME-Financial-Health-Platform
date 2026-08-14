# Model Card — SME Financial Health Platform

## 1. Model Details
- **Organization / Maintainer**: SME Financial Health Platform Engineering Team
- **Model Date**: August 2026
- **Model Version**: `v1.0.0`
- **Model Type**:
  - **Risk Model**: Gradient Boosted Decision Trees (`CalibratedClassifierCV` with Isotonic Regression)
  - **Recommendation Model**: Multi-Output Random Forest Classifier with Deterministic Rule Constraint Layer
  - **Explainability Engine**: TreeSHAP Feature Attribution mapped to Industry Target Benchmarks
- **License**: MIT License

---

## 2. Intended Use & Domain
- **Primary Intended Use**: Deterministic, explainable financial risk assessment, insolvency early-warning, and treasury/operational recommendations for Small and Medium Enterprises (SMEs).
- **Primary Users**: SME CFOs/Business Owners, Underwriters, Financial Analysts, Credit Officers.
- **Out-of-Scope Use Cases**:
  - High-frequency automated credit liquidation without human review.
  - Large cap multinational conglomerates with non-standard capital structures.

---

## 3. Factors & Features
The model operates over **22 quantitative financial ratios** derived from balance sheet and income statement items across 6 industries (`manufacturing`, `retail`, `services`, `agriculture`, `logistics`, `e-commerce`):

| Category | Ratios Included |
| :--- | :--- |
| **Profitability** | Gross Margin, Operating Margin, Net Margin, EBITDA Margin, ROA, ROE |
| **Liquidity** | Current Ratio, Quick Ratio, Cash Ratio, Working Capital to Total Assets |
| **Leverage & Solvency** | Debt-to-Equity, Debt-to-Assets, Interest Coverage Ratio, Equity Ratio |
| **Efficiency & Working Capital** | Receivables Days (DSO), Payables Days (DPO), Inventory Days (DSI), Cash Conversion Cycle (CCC), Asset Turnover |
| **Growth & Cash Flow** | Revenue Growth Rate, Expense Growth Rate, Operating Cash Flow Margin, Cash Flow to Debt |

---

## 4. Training Data & Methodology
- **Dataset**: `sme-synthetic-v1` (6,000 realistic multi-sector SME profiles generated with calibrated financial balance-sheet coherence).
- **Split**: 70% Train (4,200), 15% Validation (900), 15% Test (900) stratified by risk label and sector.
- **Preprocessing**: Deterministic zero-division clipping, bounds enforcement, log-ratio transformations where appropriate, and one-hot industry encoding.

---

## 5. Quantitative Performance

### 5.1 Risk Model (`risk-model-v1.0.0`)
- **Test ROC-AUC**: `0.9766`
- **Test PR-AUC**: `0.8612`
- **Brier Score (Calibration error)**: `0.0404` (Well-calibrated probabilities)
- **Precision**: `0.7453`
- **Recall**: `0.7315`
- **F1 Score**: `0.7383`

### 5.2 Multi-Label Recommendation Model (`recommendation-model-v1.0.0`)
- **Test Micro F1**: `1.0000`
- **Test Macro F1**: `1.0000`
- **Precision@3**: `0.6404`
- **Recall@3**: `0.9510`
- **Invalid Recommendation Rate**: `0.0%` (Guaranteed via post-inference deterministic rule engine)

---

## 6. Explainability & Business Transparency
- **Methodology**: TreeSHAP computes the marginal contribution of each financial metric toward the risk probability.
- **Attribution Mapping**: Each SHAP attribution value is mapped against industry-specific target benchmarks (P50/P75) to provide human-readable, root-cause explanations (e.g. *"Receivables cycle of 98 days is 2.2x above services benchmark target (45 days), locking up ₹1.2M in liquid capital"*).
- **Zero External Tokens**: The core explainability pipeline requires 0 external LLM API tokens.

---

## 7. Ethical Considerations & Limitations
- **Fairness**: Benchmarks and base rates are tailored per industry sector to prevent bias against naturally capital-intensive industries (e.g., manufacturing vs. services).
- **Fail-Safe Mechanism**: The `ModelManager` verifies artifact SHA256 checksums on startup. If an artifact is corrupt or missing, deterministic heuristic scoring activates to prevent service outages.
