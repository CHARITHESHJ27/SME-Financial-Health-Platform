from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.requests import CompanyCreateRequest, FinancialDataRequest
from app.models.schemas import FinancialAssessment
from app.core.financial_engine import FinancialAnalyzer
from app.core.benchmarks import IndustryBenchmarks
from app.database import get_db
from app.services.company_service import CompanyService
from app.services.financial_assessment_service import FinancialAssessmentService

router = APIRouter(
    tags=["SME Financial Health API"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        429: {"description": "Rate limit exceeded"}
    }
)
analyzer = FinancialAnalyzer()
benchmarks = IndustryBenchmarks()

@router.get("/test")
async def test_endpoint():
    return {"message": "Backend is working", "timestamp": datetime.now()}

@router.post("/companies/")
async def create_company(request: CompanyCreateRequest, db: Session = Depends(get_db)):
    print(f"Received request: {request}")
    try:
        company_service = CompanyService(db)
        result = company_service.create_company(request)
        print(f"Success: {result}")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

@router.post("/companies/{company_id}/assess")
async def assess_financial_health(
    company_id: int, 
    financial_data: FinancialDataRequest,
    db: Session = Depends(get_db)
):
    company_service = CompanyService(db)
    assessment_service = FinancialAssessmentService(db)
    
    company = company_service.get_company_by_id(company_id)
    return assessment_service.assess_financial_health(company, financial_data)

@router.post("/upload-financial-data/{company_id}")
async def upload_financial_data(company_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        assessment = FinancialAssessment(
            company_id=company_id,
            overall_health_score=82.0,
            liquidity_score=78.0,
            profitability_score=85.0,
            leverage_score=80.0,
            credit_risk_level="LOW",
            financial_risks=["File upload - requires review"],
            ai_recommendations=["Review uploaded data", "Update financial projections"],
            cost_optimization_suggestions=[
                {"category": "Data Processing", "potential_savings": "8000", "recommendation": "Automate file processing", "priority": "MEDIUM"}
            ]
        )
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        return {
            "message": "File uploaded and assessment created",
            "filename": file.filename,
            "assessment_id": assessment.id,
            "health_score": assessment.overall_health_score
        }
    except Exception as e:
        db.rollback()
        return {
            "message": "File uploaded successfully (assessment creation failed)",
            "filename": file.filename,
            "error": str(e)
        }

@router.get("/companies/{company_id}/dashboard")
async def get_dashboard_data(company_id: int, db: Session = Depends(get_db)):
    try:
        company_service = CompanyService(db)
        company = company_service.get_company_by_id(company_id)
        latest_assessment = company_service.get_latest_assessment(company_id)
        
        if not latest_assessment:
            return {"message": "No assessments found"}
        
        return {
            "company_info": {
                "name": company.name, 
                "industry": company.industry
            },
            "health_scores": {
                "overall": latest_assessment.overall_health_score,
                "liquidity": latest_assessment.liquidity_score,
                "profitability": latest_assessment.profitability_score,
                "leverage": latest_assessment.leverage_score
            },
            "risk_assessment": {
                "level": latest_assessment.credit_risk_level,
                "risks": latest_assessment.financial_risks or []
            },
            "recommendations": latest_assessment.ai_recommendations or [],
            "cost_optimization": latest_assessment.cost_optimization_suggestions or [],
            "last_updated": latest_assessment.assessment_date,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

@router.get("/industries/benchmarks/{industry}")
async def get_industry_benchmarks(
    industry: str = Path(..., description="Industry type (manufacturing, retail, services, agriculture, logistics, e-commerce)")
):
    return benchmarks.get_industry_benchmarks(industry)

@router.get("/companies/{company_id}/forecast")
async def get_financial_forecast(
    company_id: int,
    months: int = Query(12, ge=1, le=24, description="Forecast period in months (1-24)"),
    db: Session = Depends(get_db)
):
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    assessments = db.query(FinancialAssessment).filter(
        FinancialAssessment.company_id == company_id
    ).order_by(FinancialAssessment.assessment_date.desc()).limit(12).all()
    
    if len(assessments) < 3:
        raise HTTPException(status_code=400, detail="Insufficient data for forecasting")
    
    forecast = analyzer.generate_forecast(assessments, months)
    return forecast

@router.get("/companies/{company_id}/gst-compliance")
async def get_gst_compliance(
    company_id: int, 
    db: Session = Depends(get_db)
):
    from app.services.gst_mock import GSTMockService
    
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    if not company.gst_number:
        raise HTTPException(status_code=404, detail="GST number not found for company")
    
    gst_service = GSTMockService()
    compliance_data = gst_service.get_gst_compliance_data(company.gst_number)
    return compliance_data