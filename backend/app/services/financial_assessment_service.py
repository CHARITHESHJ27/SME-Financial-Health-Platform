from sqlalchemy.orm import Session
from typing import Dict, Any
from fastapi import HTTPException

from app.models.schemas import Company, FinancialAssessment
from app.models.requests import FinancialDataRequest
from app.core.financial_engine import FinancialAnalyzer
from app.core.scoring import CreditScorer
from app.core.benchmarks import IndustryBenchmarks
from app.services.validation_service import ValidationService


class FinancialAssessmentService:
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = FinancialAnalyzer()
        self.scorer = CreditScorer()
        self.benchmarks = IndustryBenchmarks()
        self.validator = ValidationService()
    
    def assess_financial_health(
        self, 
        company: Company, 
        financial_data: FinancialDataRequest
    ) -> Dict[str, Any]:
        """Perform comprehensive financial assessment"""
        
        # Validate input data
        self.validator.validate_financial_data(financial_data)
        
        # Prepare analysis data
        analysis_data = self._prepare_analysis_data(company, financial_data)
        
        # Perform calculations
        financial_ratios = self.analyzer.calculate_ratios(analysis_data)
        credit_score = self.scorer.calculate_credit_score(analysis_data, financial_ratios)
        industry_comparison = self.benchmarks.compare_with_industry(
            company.industry, financial_ratios
        )
        
        # Generate insights
        assessment_result = {
            'overall_health_score': credit_score,
            'financial_ratios': financial_ratios,
            'industry_comparison': industry_comparison,
            'risk_analysis': self.analyzer.assess_risks(analysis_data, financial_ratios),
            'recommendations': self.analyzer.generate_recommendations(analysis_data, financial_ratios),
            'cost_optimization': self.analyzer.identify_cost_savings(analysis_data)
        }
        
        # Save assessment
        db_assessment = self._save_assessment(company.id, assessment_result, financial_ratios)
        
        return {
            "assessment_id": db_assessment.id,
            "company_name": company.name,
            "assessment_result": assessment_result
        }
    
    def _prepare_analysis_data(
        self, 
        company: Company, 
        financial_data: FinancialDataRequest
    ) -> Dict[str, Any]:
        """Prepare data for financial analysis"""
        return {
            'industry': company.industry,
            'revenue': float(financial_data.revenue or 0),
            'total_expenses': float(financial_data.total_expenses or 0),
            'current_assets': float(financial_data.current_assets or 0),
            'current_liabilities': float(financial_data.current_liabilities or 0),
            'total_assets': float(financial_data.total_assets or 0),
            'total_debt': float(financial_data.total_debt or 0),
            'revenue_growth_rate': float(financial_data.revenue_growth_rate or 0),
            'inventory': float(financial_data.inventory or 0),
            'accounts_receivable': float(financial_data.accounts_receivable or 0),
            'accounts_payable': float(financial_data.accounts_payable or 0)
        }
    
    def create_assessment_from_file_data(
        self, 
        company_id: int, 
        extracted_data: Dict[str, Any]
    ) -> FinancialAssessment:
        """Create assessment from uploaded file data"""
        
        # Convert extracted data to FinancialDataRequest format
        financial_data = FinancialDataRequest(
            revenue=float(extracted_data.get('revenue', 0) or 0),
            total_expenses=float(extracted_data.get('total_expenses', 0) or 0),
            current_assets=float(extracted_data.get('current_assets', 0) or 0),
            current_liabilities=float(extracted_data.get('current_liabilities', 0) or 0),
            total_assets=float(extracted_data.get('total_assets', 0) or 0),
            total_debt=float(extracted_data.get('total_debt', 0) or 0),
            revenue_growth_rate=float(extracted_data.get('revenue_growth_rate', 0) or 0),
            inventory=float(extracted_data.get('inventory', 0) or 0),
            accounts_receivable=float(extracted_data.get('accounts_receivable', 0) or 0),
            accounts_payable=float(extracted_data.get('accounts_payable', 0) or 0)
        )
        
        # Get company
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Perform assessment
        assessment_result = self.assess_financial_health(company, financial_data)
        
        # Return the saved assessment
        return self.db.query(FinancialAssessment).filter(
            FinancialAssessment.id == assessment_result["assessment_id"]
        ).first()

    def _save_assessment(
        self, 
        company_id: int, 
        assessment_result: Dict[str, Any], 
        financial_ratios: Dict[str, float]
    ) -> FinancialAssessment:
        """Save assessment to database"""
        db_assessment = FinancialAssessment(
            company_id=company_id,
            overall_health_score=assessment_result['overall_health_score'],
            liquidity_score=financial_ratios.get('current_ratio', 0) * 25,
            profitability_score=financial_ratios.get('profit_margin', 0) * 100,
            leverage_score=max(0, 100 - financial_ratios.get('debt_to_asset_ratio', 0) * 100),
            credit_risk_level=assessment_result['risk_analysis']['risk_level'],
            financial_risks=assessment_result['risk_analysis']['identified_risks'],
            ai_recommendations=assessment_result['recommendations'],
            cost_optimization_suggestions=assessment_result['cost_optimization']
        )
        
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        
        return db_assessment