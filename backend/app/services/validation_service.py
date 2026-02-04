from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.models.requests import CompanyCreateRequest, FinancialDataRequest


class ValidationService:
    
    ALLOWED_INDUSTRIES = [
        'manufacturing', 'retail', 'services', 
        'agriculture', 'logistics', 'e-commerce'
    ]
    
    ALLOWED_FILE_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.pdf']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_company_creation(request: CompanyCreateRequest) -> None:
        """Validate company creation request"""
        ValidationService._validate_company_name(request.name)
        ValidationService._validate_industry(request.industry)
        if request.gst_number:
            ValidationService._validate_gst_number(request.gst_number)
    
    @staticmethod
    def validate_financial_data(request: FinancialDataRequest) -> None:
        """Validate financial data input"""
        ValidationService._validate_positive_values(request)
        ValidationService._validate_growth_rate(request.revenue_growth_rate)
        ValidationService._validate_financial_consistency(request)
    
    @staticmethod
    def validate_file_upload(file: UploadFile) -> None:
        """Validate file upload"""
        ValidationService._validate_file_size(file)
        ValidationService._validate_file_type(file)
    
    @staticmethod
    def _validate_company_name(name: str) -> None:
        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Company name must be at least 2 characters"
            )
    
    @staticmethod
    def _validate_industry(industry: str) -> None:
        if industry.lower() not in ValidationService.ALLOWED_INDUSTRIES:
            raise HTTPException(
                status_code=400,
                detail=f"Industry must be one of: {ValidationService.ALLOWED_INDUSTRIES}"
            )
    
    @staticmethod
    def _validate_gst_number(gst_number: str) -> None:
        if len(gst_number) != 15:
            raise HTTPException(
                status_code=400,
                detail="GST number must be 15 characters"
            )
    
    @staticmethod
    def _validate_positive_values(request: FinancialDataRequest) -> None:
        financial_fields = [
            ('revenue', request.revenue),
            ('total_expenses', request.total_expenses),
            ('current_assets', request.current_assets),
            ('current_liabilities', request.current_liabilities),
            ('total_assets', request.total_assets),
            ('total_debt', request.total_debt)
        ]
        
        for field_name, value in financial_fields:
            if value < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field_name} must be non-negative"
                )
    
    @staticmethod
    def _validate_growth_rate(growth_rate: Optional[float]) -> None:
        if growth_rate is not None and (growth_rate < -1 or growth_rate > 5):
            raise HTTPException(
                status_code=400,
                detail="Growth rate must be between -100% and 500%"
            )
    
    @staticmethod
    def _validate_financial_consistency(request: FinancialDataRequest) -> None:
        """Validate financial data consistency"""
        if request.current_assets > request.total_assets:
            raise HTTPException(
                status_code=400,
                detail="Current assets cannot exceed total assets"
            )
        
        if request.total_debt > request.total_assets:
            raise HTTPException(
                status_code=400,
                detail="Total debt cannot exceed total assets"
            )
    
    @staticmethod
    def _validate_file_size(file: UploadFile) -> None:
        if file.size and file.size > ValidationService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum 10MB allowed"
            )
    
    @staticmethod
    def _validate_file_type(file: UploadFile) -> None:
        if not any(file.filename.lower().endswith(ext) 
                  for ext in ValidationService.ALLOWED_FILE_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed: {ValidationService.ALLOWED_FILE_EXTENSIONS}"
            )