from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.models.schemas import Company, FinancialAssessment
from app.models.requests import CompanyCreateRequest
from app.services.validation_service import ValidationService


class CompanyService:
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = ValidationService()
    
    def create_company(self, request: CompanyCreateRequest) -> Company:
        """Create a new company with validation"""
        # Validate input
        self.validator.validate_company_creation(request)
        
        # Check business rules
        self._check_company_uniqueness(request.name, request.gst_number)
        
        # Create company
        company = Company(
            name=request.name.strip(),
            industry=request.industry.lower(),
            gst_number=request.gst_number,
            language_preference=request.language_preference
        )
        
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        
        return {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "gst_number": company.gst_number,
            "registration_date": company.registration_date,
            "language_preference": company.language_preference,
            "message": "Company created successfully"
        }
    
    def get_company_by_id(self, company_id: int) -> Company:
        """Get company by ID with validation"""
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    
    def get_latest_assessment(self, company_id: int) -> Optional[FinancialAssessment]:
        """Get latest financial assessment for company"""
        return self.db.query(FinancialAssessment).filter(
            FinancialAssessment.company_id == company_id
        ).order_by(FinancialAssessment.assessment_date.desc()).first()
    
    def _check_company_uniqueness(self, name: str, gst_number: Optional[str]) -> None:
        """Check if company name or GST number already exists"""
        existing_company = self.db.query(Company).filter(Company.name == name.strip()).first()
        if existing_company:
            raise HTTPException(
                status_code=400, 
                detail="Company with this name already exists"
            )
        
        if gst_number:
            existing_gst = self.db.query(Company).filter(Company.gst_number == gst_number).first()
            if existing_gst:
                raise HTTPException(
                    status_code=400, 
                    detail="Company with this GST number already exists"
                )