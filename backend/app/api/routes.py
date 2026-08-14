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
async def upload_financial_data(
    company_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    import io
    import pandas as pd
    
    company_service = CompanyService(db)
    assessment_service = FinancialAssessmentService(db)
    company = company_service.get_company_by_id(company_id)

    try:
        content = await file.read()
        filename_lower = (file.filename or "").lower()

        if filename_lower.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename_lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel.")

        extracted = analyzer.extract_financial_data(df)
        financial_req = FinancialDataRequest(
            revenue=float(extracted.get("revenue", 1000000.0) or 1000000.0),
            total_expenses=float(extracted.get("total_expenses", 850000.0) or 850000.0),
            current_assets=float(extracted.get("current_assets", 400000.0) or 400000.0),
            current_liabilities=float(extracted.get("current_liabilities", 300000.0) or 300000.0),
            total_assets=float(extracted.get("total_assets", 900000.0) or 900000.0),
            total_debt=float(extracted.get("total_debt", 400000.0) or 400000.0),
            inventory=float(extracted.get("inventory", 0.0) or 0.0),
            accounts_receivable=float(extracted.get("accounts_receivable", 0.0) or 0.0),
            accounts_payable=float(extracted.get("accounts_payable", 0.0) or 0.0),
            revenue_growth_rate=float(extracted.get("revenue_growth_rate", 0.08) or 0.08)
        )

        assessment_resp = assessment_service.assess_financial_health(company, financial_req)
        return {
            "message": "File processed and ML financial assessment generated successfully",
            "filename": file.filename,
            "assessment_id": assessment_resp["assessment_id"],
            "health_score": assessment_resp["assessment_result"]["overall_health_score"],
            "risk_category": assessment_resp["data"]["risk"]["category"],
            "data": assessment_resp["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process financial file: {str(e)}")

@router.get("/companies/{company_id}/dashboard")
async def get_dashboard_data(company_id: int, db: Session = Depends(get_db)):
    try:
        company_service = CompanyService(db)
        company = company_service.get_company_by_id(company_id)
        latest_assessment = company_service.get_latest_assessment(company_id)
        
        if not latest_assessment:
            return {"message": "No assessments found"}
        
        risk_score = float(latest_assessment.risk_score) if latest_assessment.risk_score is not None else float(100 - (latest_assessment.overall_health_score or 50))
        risk_prob = float(latest_assessment.risk_probability) if latest_assessment.risk_probability is not None else (risk_score / 100.0)
        risk_cat = latest_assessment.risk_category or latest_assessment.credit_risk_level or "MEDIUM"

        return {
            "company_info": {
                "name": company.name, 
                "industry": company.industry,
                "gst_number": company.gst_number
            },
            "health_scores": {
                "overall": float(latest_assessment.overall_health_score or (100 - risk_score)),
                "liquidity": float(latest_assessment.liquidity_score or 70.0),
                "profitability": float(latest_assessment.profitability_score or 70.0),
                "leverage": float(latest_assessment.leverage_score or 70.0)
            },
            "risk_assessment": {
                "score": int(round(risk_score)),
                "probability": round(risk_prob, 4),
                "level": risk_cat,
                "category": risk_cat,
                "model_version": latest_assessment.model_version or "risk-model-v1.0.0",
                "risks": latest_assessment.financial_risks or []
            },
            "recommendations": latest_assessment.ai_recommendations or [],
            "cost_optimization": latest_assessment.cost_optimization_suggestions or [],
            "shap_explanations": latest_assessment.shap_explanations or [],
            "executive_summary": latest_assessment.executive_summary or {},
            "financial_ratios": latest_assessment.financial_ratios or {},
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