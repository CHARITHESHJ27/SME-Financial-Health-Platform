# ML Pipeline Specification — SME Financial Health Platform

## 1. Feature Engineering Specification

The feature engineering layer calculates **22 quantitative financial ratios** across 5 distinct categories, with division-by-zero protection (`epsilon = 1e-6`) and outlier clipping.

### Ratio Formulations

#### Profitability
1. $\text{Gross Margin} = \frac{\text{Gross Profit}}{\text{Revenue}}$
2. $\text{Operating Margin} = \frac{\text{Operating Income}}{\text{Revenue}}$
3. $\text{Net Margin} = \frac{\text{Net Income}}{\text{Revenue}}$
4. $\text{EBITDA Margin} = \frac{\text{EBITDA}}{\text{Revenue}}$
5. $\text{ROA (Return on Assets)} = \frac{\text{Net Income}}{\text{Total Assets}}$
6. $\text{ROE (Return on Equity)} = \frac{\text{Net Income}}{\text{Total Equity}}$

#### Liquidity
7. $\text{Current Ratio} = \frac{\text{Current Assets}}{\text{Current Liabilities}}$
8. $\text{Quick Ratio} = \frac{\text{Current Assets} - \text{Inventory}}{\text{Current Liabilities}}$
9. $\text{Cash Ratio} = \frac{\text{Cash \& Equivalents}}{\text{Current Liabilities}}$
10. $\text{Working Capital to Assets} = \frac{\text{Current Assets} - \text{Current Liabilities}}{\text{Total Assets}}$

#### Leverage & Solvency
11. $\text{Debt-to-Equity} = \frac{\text{Total Debt}}{\text{Total Equity}}$
12. $\text{Debt-to-Assets} = \frac{\text{Total Debt}}{\text{Total Assets}}$
13. $\text{Interest Coverage Ratio} = \frac{\text{Operating Income}}{\text{Interest Expense}}$
14. $\text{Equity Ratio} = \frac{\text{Total Equity}}{\text{Total Assets}}$

#### Efficiency & Operating Cycle
15. $\text{Receivable Days (DSO)} = \left(\frac{\text{Accounts Receivable}}{\text{Revenue}}\right) \times 365$
16. $\text{Payable Days (DPO)} = \left(\frac{\text{Accounts Payable}}{\text{Operating Expenses}}\right) \times 365$
17. $\text{Inventory Days (DSI)} = \left(\frac{\text{Inventory}}{\text{COGS}}\right) \times 365$
18. $\text{Cash Conversion Cycle (CCC)} = \text{DSO} + \text{DSI} - \text{DPO}$
19. $\text{Asset Turnover} = \frac{\text{Revenue}}{\text{Total Assets}}$

#### Growth & Cash Flow
20. $\text{Revenue Growth Rate} = \frac{\text{Revenue}_t - \text{Revenue}_{t-1}}{\text{Revenue}_{t-1}}$
21. $\text{Operating Cash Flow Margin} = \frac{\text{Operating Cash Flow}}{\text{Revenue}}$
22. $\text{Cash Flow to Debt} = \frac{\text{Operating Cash Flow}}{\text{Total Debt}}$

---

## 2. Model Training & Evaluation Protocols

### Training Protocol
```bash
# 1. Generate realistic SME synthetic dataset
PYTHONPATH=. python -m ml.data.generate_dataset --samples 6000 --output-dir data

# 2. Train and calibrate risk model
PYTHONPATH=. python -m ml.training.train_risk --config configs/risk.yaml

# 3. Train multi-label recommendation model
PYTHONPATH=. python -m ml.training.train_recommendation --config configs/recommendation.yaml
```

### ML Regression Gate Thresholds
- **Risk Model ROC-AUC**: $\ge 0.85$ (Current: $0.9766$)
- **Risk Model Brier Score**: $\le 0.10$ (Current: $0.0404$)
- **Multi-Label Recommendation Micro F1**: $\ge 0.85$ (Current: $1.0000$)
- **Invalid Recommendation Rate**: $= 0.0\%$
