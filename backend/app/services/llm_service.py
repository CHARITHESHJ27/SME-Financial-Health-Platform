import openai
import json
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

class LLMService:
    def __init__(self):
        # Initialize OpenAI client (in production, use environment variables)
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
        )
        
        # Language templates for multilingual support
        self.language_templates = {
            'english': {
                'system_prompt': "You are a financial advisor specializing in SME business analysis. Provide clear, actionable insights.",
                'insights_prompt': "Analyze the financial health and provide strategic recommendations.",
                'risk_prompt': "Identify key financial risks and mitigation strategies."
            },
            'hindi': {
                'system_prompt': "आप एक वित्तीय सलाहकार हैं जो SME व्यापार विश्लेषण में विशेषज्ञ हैं। स्पष्ट, कार्यान्वित करने योग्य अंतर्दृष्टि प्रदान करें।",
                'insights_prompt': "वित्तीय स्वास्थ्य का विश्लेषण करें और रणनीतिक सिफारिशें प्रदान करें।",
                'risk_prompt': "मुख्य वित्तीय जोखिमों और शमन रणनीतियों की पहचान करें।"
            }
        }
    
    async def generate_insights(self, financial_data: Dict[str, float], ratios: Dict[str, float], language: str = 'english') -> List[str]:
        """Generate AI-powered financial insights"""
        
        # Prepare context for LLM
        context = self._prepare_financial_context(financial_data, ratios)
        
        # Get language-specific prompts
        lang_template = self.language_templates.get(language, self.language_templates['english'])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": lang_template['system_prompt']
                    },
                    {
                        "role": "user",
                        "content": f"""
                        {lang_template['insights_prompt']}
                        
                        Financial Data:
                        {context}
                        
                        Please provide 5-7 specific, actionable insights focusing on:
                        1. Current financial position strengths
                        2. Areas of concern that need immediate attention
                        3. Strategic recommendations for growth
                        4. Cash flow optimization opportunities
                        5. Risk mitigation strategies
                        
                        Format as a JSON array of strings.
                        """
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            insights_text = response.choices[0].message.content
            try:
                insights = json.loads(insights_text)
                return insights if isinstance(insights, list) else [insights_text]
            except json.JSONDecodeError:
                # Fallback: split by lines and clean up
                return [line.strip() for line in insights_text.split('\n') if line.strip()]
                
        except Exception as e:
            # Fallback insights if LLM fails
            return self._generate_fallback_insights(financial_data, ratios, language)
    
    async def generate_cost_optimization_suggestions(self, financial_data: Dict[str, float], language: str = 'english') -> List[Dict[str, Any]]:
        """Generate AI-powered cost optimization suggestions"""
        
        context = self._prepare_cost_context(financial_data)
        lang_template = self.language_templates.get(language, self.language_templates['english'])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"{lang_template['system_prompt']} Focus on cost optimization and operational efficiency."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Analyze the following financial data and suggest specific cost optimization opportunities:
                        
                        {context}
                        
                        Provide 5-8 cost optimization suggestions in JSON format with the following structure:
                        [
                            {{
                                "category": "Cost Category",
                                "suggestion": "Specific actionable suggestion",
                                "potential_savings": "Estimated savings amount or percentage",
                                "implementation_difficulty": "Easy/Medium/Hard",
                                "timeframe": "Implementation timeframe"
                            }}
                        ]
                        """
                    }
                ],
                temperature=0.6,
                max_tokens=1200
            )
            
            suggestions_text = response.choices[0].message.content
            try:
                suggestions = json.loads(suggestions_text)
                return suggestions if isinstance(suggestions, list) else []
            except json.JSONDecodeError:
                return self._generate_fallback_cost_suggestions(financial_data)
                
        except Exception as e:
            return self._generate_fallback_cost_suggestions(financial_data)
    
    async def generate_growth_recommendations(self, financial_data: Dict[str, float], industry: str, language: str = 'english') -> List[str]:
        """Generate industry-specific growth recommendations"""
        
        context = f"""
        Industry: {industry}
        Revenue: ${financial_data['revenue']:,.2f}
        Growth Rate: {financial_data.get('revenue_growth_rate', 0)*100:.1f}%
        Profit Margin: {((financial_data['revenue'] - financial_data['total_expenses']) / financial_data['revenue'] * 100) if financial_data['revenue'] > 0 else 0:.1f}%
        """
        
        lang_template = self.language_templates.get(language, self.language_templates['english'])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"{lang_template['system_prompt']} Specialize in growth strategies for {industry} businesses."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Based on the following business profile, suggest specific growth strategies:
                        
                        {context}
                        
                        Provide 5-7 growth recommendations specific to the {industry} industry.
                        Focus on practical, implementable strategies that align with the current financial position.
                        Format as a JSON array of strings.
                        """
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            recommendations_text = response.choices[0].message.content
            try:
                recommendations = json.loads(recommendations_text)
                return recommendations if isinstance(recommendations, list) else [recommendations_text]
            except json.JSONDecodeError:
                return [line.strip() for line in recommendations_text.split('\n') if line.strip()]
                
        except Exception as e:
            return self._generate_fallback_growth_recommendations(industry)
    
    def _prepare_financial_context(self, financial_data: Dict[str, float], ratios: Dict[str, float]) -> str:
        """Prepare financial context for LLM analysis"""
        return f"""
        Revenue: ${financial_data['revenue']:,.2f}
        Total Expenses: ${financial_data['total_expenses']:,.2f}
        Net Profit: ${financial_data['revenue'] - financial_data['total_expenses']:,.2f}
        
        Current Assets: ${financial_data['current_assets']:,.2f}
        Current Liabilities: ${financial_data['current_liabilities']:,.2f}
        Total Assets: ${financial_data['total_assets']:,.2f}
        Total Debt: ${financial_data['total_debt']:,.2f}
        
        Key Ratios:
        - Current Ratio: {ratios.get('current_ratio', 0):.2f}
        - Profit Margin: {ratios.get('profit_margin', 0)*100:.1f}%
        - Debt-to-Asset Ratio: {ratios.get('debt_to_asset_ratio', 0)*100:.1f}%
        - Revenue Growth Rate: {ratios.get('revenue_growth_rate', 0)*100:.1f}%
        - ROA: {ratios.get('roa', 0)*100:.1f}%
        """
    
    def _prepare_cost_context(self, financial_data: Dict[str, float]) -> str:
        """Prepare cost-focused context for analysis"""
        expense_ratio = financial_data['total_expenses'] / financial_data['revenue'] if financial_data['revenue'] > 0 else 0
        
        return f"""
        Revenue: ${financial_data['revenue']:,.2f}
        Total Expenses: ${financial_data['total_expenses']:,.2f}
        Expense Ratio: {expense_ratio*100:.1f}%
        Net Profit: ${financial_data['revenue'] - financial_data['total_expenses']:,.2f}
        
        Business Size: {"Large" if financial_data['revenue'] > 10000000 else "Medium" if financial_data['revenue'] > 1000000 else "Small"}
        """
    
    def _generate_fallback_insights(self, financial_data: Dict[str, float], ratios: Dict[str, float], language: str) -> List[str]:
        """Generate fallback insights when LLM is unavailable"""
        insights = []
        
        # Liquidity analysis
        current_ratio = ratios.get('current_ratio', 0)
        if current_ratio > 2.0:
            insights.append("Strong liquidity position with current ratio above 2.0 - consider investing excess cash for better returns")
        elif current_ratio < 1.0:
            insights.append("Liquidity concern - current ratio below 1.0 indicates potential cash flow issues")
        
        # Profitability analysis
        profit_margin = ratios.get('profit_margin', 0)
        if profit_margin > 0.15:
            insights.append("Excellent profit margins above 15% - focus on scaling operations")
        elif profit_margin < 0:
            insights.append("Operating at a loss - immediate cost reduction and revenue enhancement needed")
        
        # Growth analysis
        growth_rate = ratios.get('revenue_growth_rate', 0)
        if growth_rate > 0.20:
            insights.append("Strong revenue growth above 20% - ensure adequate working capital for expansion")
        elif growth_rate < 0:
            insights.append("Declining revenue requires strategic review and market repositioning")
        
        # Leverage analysis
        debt_ratio = ratios.get('debt_to_asset_ratio', 0)
        if debt_ratio > 0.7:
            insights.append("High leverage above 70% - focus on debt reduction and cash flow improvement")
        
        return insights[:5]  # Return top 5 insights
    
    def _generate_fallback_cost_suggestions(self, financial_data: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate fallback cost optimization suggestions"""
        suggestions = [
            {
                "category": "Technology & Automation",
                "suggestion": "Implement automated accounting and inventory management systems",
                "potential_savings": "5-10% of operational costs",
                "implementation_difficulty": "Medium",
                "timeframe": "3-6 months"
            },
            {
                "category": "Vendor Management",
                "suggestion": "Renegotiate supplier contracts and consolidate vendors",
                "potential_savings": "3-7% of procurement costs",
                "implementation_difficulty": "Easy",
                "timeframe": "1-3 months"
            },
            {
                "category": "Energy Efficiency",
                "suggestion": "Upgrade to energy-efficient equipment and lighting",
                "potential_savings": "10-20% of utility costs",
                "implementation_difficulty": "Medium",
                "timeframe": "2-4 months"
            }
        ]
        
        return suggestions
    
    def _generate_fallback_growth_recommendations(self, industry: str) -> List[str]:
        """Generate fallback growth recommendations by industry"""
        industry_recommendations = {
            'manufacturing': [
                "Invest in automation to improve production efficiency",
                "Explore new product lines or customization services",
                "Consider vertical integration to reduce costs"
            ],
            'retail': [
                "Develop omnichannel presence with online sales",
                "Implement customer loyalty programs",
                "Optimize inventory management and product mix"
            ],
            'services': [
                "Develop recurring revenue streams through subscriptions",
                "Expand service offerings to existing clients",
                "Invest in digital marketing and online presence"
            ]
        }
        
        return industry_recommendations.get(industry.lower(), [
            "Focus on customer retention and satisfaction",
            "Explore new market segments or geographic expansion",
            "Invest in technology to improve operational efficiency"
        ])