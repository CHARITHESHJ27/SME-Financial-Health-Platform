import json
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# ── Provider availability checks ─────────────────────────────────────────────

def _get_openai_client():
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or key.startswith("your-"):
        return None
    try:
        import openai
        return openai.OpenAI(api_key=key)
    except Exception:
        return None

def _get_groq_client():
    key = os.getenv("GROQ_API_KEY", "")
    if not key or key.startswith("your-"):
        return None
    try:
        from groq import Groq
        return Groq(api_key=key)
    except Exception:
        return None


# ── LLMService ────────────────────────────────────────────────────────────────

class LLMService:

    SYSTEM_PROMPT = (
        "You are a financial advisor specializing in SME business analysis for Indian markets. "
        "Provide clear, actionable, India-specific insights. "
        "Always respond in valid JSON format only — no markdown, no extra text."
    )

    def __init__(self):
        self.openai  = _get_openai_client()
        self.groq    = _get_groq_client()
        provider     = "OpenAI" if self.openai else ("Groq" if self.groq else "Rule-based fallback")
        logger.info(f"LLMService initialized — provider: {provider}")

    # ── Public methods ────────────────────────────────────────────────────────

    async def generate_insights(
        self,
        financial_data: Dict[str, float],
        ratios: Dict[str, float],
        language: str = "english",
    ) -> List[str]:
        prompt = f"""
Analyze this SME financial data and return a JSON array of 5-6 specific, actionable insights.
Each insight must be a plain string. No numbering.

Financial Data:
- Revenue: ₹{financial_data.get('revenue', 0):,.0f}
- Expenses: ₹{financial_data.get('total_expenses', 0):,.0f}
- Net Profit: ₹{financial_data.get('revenue', 0) - financial_data.get('total_expenses', 0):,.0f}
- Current Assets: ₹{financial_data.get('current_assets', 0):,.0f}
- Current Liabilities: ₹{financial_data.get('current_liabilities', 0):,.0f}
- Total Assets: ₹{financial_data.get('total_assets', 0):,.0f}
- Total Debt: ₹{financial_data.get('total_debt', 0):,.0f}

Key Ratios:
- Current Ratio: {ratios.get('current_ratio', 0):.2f}
- Profit Margin: {ratios.get('profit_margin', 0)*100:.1f}%
- Debt-to-Asset: {ratios.get('debt_to_asset_ratio', 0)*100:.1f}%
- Revenue Growth: {ratios.get('revenue_growth_rate', 0)*100:.1f}%
- ROA: {ratios.get('roa', 0)*100:.1f}%

Return format: ["insight 1", "insight 2", ...]
"""
        result = await self._call_llm(prompt)
        if result:
            try:
                parsed = json.loads(result)
                if isinstance(parsed, list):
                    return [str(i) for i in parsed][:6]
            except json.JSONDecodeError:
                pass
        return self._fallback_insights(financial_data, ratios)

    async def generate_cost_optimization_suggestions(
        self,
        financial_data: Dict[str, float],
        language: str = "english",
    ) -> List[Dict[str, Any]]:
        revenue     = financial_data.get("revenue", 0)
        expenses    = financial_data.get("total_expenses", 0)
        exp_ratio   = (expenses / revenue * 100) if revenue > 0 else 0
        size        = "Large" if revenue > 10_000_000 else "Medium" if revenue > 1_000_000 else "Small"

        prompt = f"""
Analyze this SME cost profile and return a JSON array of 4-5 cost optimization suggestions.

Revenue: ₹{revenue:,.0f}
Total Expenses: ₹{expenses:,.0f}
Expense Ratio: {exp_ratio:.1f}%
Business Size: {size}

Return format:
[
  {{
    "category": "Category name",
    "suggestion": "Specific actionable suggestion",
    "potential_savings": "numeric value in rupees (e.g. 50000)",
    "priority": "HIGH | MEDIUM | LOW"
  }}
]
"""
        result = await self._call_llm(prompt)
        if result:
            try:
                parsed = json.loads(result)
                if isinstance(parsed, list):
                    return parsed[:5]
            except json.JSONDecodeError:
                pass
        return self._fallback_cost_suggestions(financial_data)

    async def generate_growth_recommendations(
        self,
        financial_data: Dict[str, float],
        industry: str,
        language: str = "english",
    ) -> List[str]:
        revenue      = financial_data.get("revenue", 0)
        growth_rate  = financial_data.get("revenue_growth_rate", 0)
        profit_margin = (
            (revenue - financial_data.get("total_expenses", 0)) / revenue * 100
            if revenue > 0 else 0
        )

        prompt = f"""
Suggest 5 growth strategies for an Indian {industry} SME.

Revenue: ₹{revenue:,.0f}
Growth Rate: {growth_rate*100:.1f}%
Profit Margin: {profit_margin:.1f}%

Return format: ["strategy 1", "strategy 2", ...]
"""
        result = await self._call_llm(prompt)
        if result:
            try:
                parsed = json.loads(result)
                if isinstance(parsed, list):
                    return [str(r) for r in parsed][:5]
            except json.JSONDecodeError:
                pass
        return self._fallback_growth(industry)

    # ── LLM call chain: OpenAI → Groq → None ─────────────────────────────────

    async def _call_llm(self, user_prompt: str) -> Optional[str]:
        # 1. Try OpenAI
        if self.openai:
            try:
                resp = self.openai.chat.completions.create(
                    model="gpt-3.5-turbo",   # cheaper than gpt-4, still excellent
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user",   "content": user_prompt},
                    ],
                    temperature=0.5,
                    max_tokens=800,
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI failed: {e} — falling back to Groq")

        # 2. Try Groq (free tier: llama3-8b-8192)
        if self.groq:
            try:
                resp = self.groq.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user",   "content": user_prompt},
                    ],
                    temperature=0.5,
                    max_tokens=800,
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning(f"Groq failed: {e} — using rule-based fallback")

        return None

    # ── Smart rule-based fallbacks ────────────────────────────────────────────

    def _fallback_insights(self, fd: Dict, ratios: Dict) -> List[str]:
        insights = []
        cr  = ratios.get("current_ratio", 0)
        pm  = ratios.get("profit_margin", 0)
        gr  = ratios.get("revenue_growth_rate", 0)
        dtr = ratios.get("debt_to_asset_ratio", 0)
        roa = ratios.get("roa", 0)
        rev = fd.get("revenue", 0)
        exp = fd.get("total_expenses", 0)

        # Liquidity
        if cr >= 2.0:
            insights.append(f"Strong liquidity with a current ratio of {cr:.1f} — consider deploying idle cash into short-term investments or expanding inventory.")
        elif cr >= 1.0:
            insights.append(f"Adequate liquidity (current ratio {cr:.1f}) — maintain a cash buffer of at least 3 months of operating expenses.")
        else:
            insights.append(f"⚠ Liquidity risk: current ratio {cr:.1f} is below 1.0 — prioritise collecting receivables and deferring non-essential capex.")

        # Profitability
        if pm >= 0.20:
            insights.append(f"Exceptional profit margin of {pm*100:.1f}% — reinvest surplus into product development or market expansion.")
        elif pm >= 0.10:
            insights.append(f"Healthy profit margin of {pm*100:.1f}% — benchmark against industry peers and target incremental 2–3% improvement.")
        elif pm >= 0:
            insights.append(f"Thin margin of {pm*100:.1f}% — conduct a line-by-line expense audit; focus on top 3 cost centres.")
        else:
            insights.append(f"⚠ Operating at a loss (margin {pm*100:.1f}%) — immediate cost rationalisation and revenue diversification required.")

        # Growth
        if gr >= 0.20:
            insights.append(f"High revenue growth of {gr*100:.1f}% — ensure working capital keeps pace; consider a revolving credit facility.")
        elif gr >= 0.05:
            insights.append(f"Steady growth of {gr*100:.1f}% — explore upselling and cross-selling to existing customers for low-cost revenue gains.")
        elif gr < 0:
            insights.append(f"Revenue declined {abs(gr)*100:.1f}% — review pricing strategy and evaluate customer churn root causes.")

        # Leverage
        if dtr >= 0.7:
            insights.append(f"High debt-to-asset ratio of {dtr*100:.1f}% — prioritise debt repayment to reduce interest burden and improve credit score.")
        elif dtr <= 0.3:
            insights.append(f"Low leverage ({dtr*100:.1f}%) — you have headroom to take on strategic debt for growth if needed.")

        # Efficiency
        if roa >= 0.10:
            insights.append(f"Excellent asset utilisation (ROA {roa*100:.1f}%) — assets are generating strong returns.")
        elif roa < 0.03:
            insights.append(f"Low ROA of {roa*100:.1f}% — review underperforming assets; consider asset-light operating models.")

        return insights[:6]

    def _fallback_cost_suggestions(self, fd: Dict) -> List[Dict[str, Any]]:
        revenue  = fd.get("revenue", 1)
        expenses = fd.get("total_expenses", 0)
        savings_base = max(int(expenses * 0.05), 10000)

        return [
            {
                "category": "Vendor Consolidation",
                "suggestion": "Consolidate to 2–3 preferred vendors and renegotiate bulk-purchase contracts for 5–8% cost reduction.",
                "potential_savings": str(int(savings_base * 1.2)),
                "priority": "HIGH",
            },
            {
                "category": "Technology & Automation",
                "suggestion": "Automate accounts payable/receivable with tools like Zoho Books or Tally Prime to cut manual processing time by 60%.",
                "potential_savings": str(int(savings_base * 0.8)),
                "priority": "HIGH",
            },
            {
                "category": "Energy Efficiency",
                "suggestion": "Switch to LED lighting and smart power strips; install occupancy sensors to reduce electricity bills by 15–20%.",
                "potential_savings": str(int(savings_base * 0.4)),
                "priority": "MEDIUM",
            },
            {
                "category": "Inventory Optimisation",
                "suggestion": "Implement just-in-time (JIT) inventory to reduce holding costs and free up working capital.",
                "potential_savings": str(int(savings_base * 0.6)),
                "priority": "MEDIUM",
            },
            {
                "category": "Digital Marketing",
                "suggestion": "Shift 30% of traditional advertising budget to targeted digital campaigns (Meta/Google Ads) for 3× better ROI.",
                "potential_savings": str(int(savings_base * 0.5)),
                "priority": "LOW",
            },
        ]

    def _fallback_growth(self, industry: str) -> List[str]:
        base = [
            "Build a referral programme — existing customers are your cheapest acquisition channel.",
            "Invest in a CRM system to track leads and improve conversion rates.",
            "Explore Government of India MSME schemes (CGTMSE, MUDRA) for low-cost growth financing.",
        ]
        specific = {
            "manufacturing": [
                "Obtain BIS/ISO certification to qualify for larger enterprise and export contracts.",
                "Partner with e-commerce platforms (Amazon Business, IndiaMART) to reach B2B buyers nationally.",
            ],
            "retail": [
                "Launch a WhatsApp-based ordering channel — low cost, high conversion for repeat customers.",
                "Introduce private-label products for 25–40% higher margins versus branded resales.",
            ],
            "services": [
                "Package services into productised retainer plans for predictable monthly recurring revenue.",
                "List on platforms like UrbanClap/Justdial to increase inbound lead volume.",
            ],
            "agriculture": [
                "Explore FPO (Farmer Producer Organisation) model to gain collective bargaining power.",
                "Add value-added processing (packaging, grading) to increase realisation by 20–30%.",
            ],
            "logistics": [
                "Integrate with Shiprocket or Delhivery APIs to offer multi-carrier rate shopping.",
                "Optimise route planning using free tools like Google OR-Tools to cut fuel costs 10–15%.",
            ],
            "e-commerce": [
                "Improve product listing quality (A+ content) to boost conversion rates on marketplaces.",
                "Implement cart abandonment email sequences — recovers 5–15% of lost sales.",
            ],
        }
        return (base + specific.get(industry.lower(), []))[:5]
