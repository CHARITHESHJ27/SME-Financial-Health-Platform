from pydantic import BaseModel
from typing import Optional


class CompanyCreateRequest(BaseModel):
    """Request model for creating a new company"""
    name: str
    industry: str
    gst_number: Optional[str] = None
    language_preference: str = "english"


class FinancialDataRequest(BaseModel):
    """Request model for financial data input"""
    revenue: float
    total_expenses: float
    current_assets: float
    current_liabilities: float
    total_assets: float
    total_debt: float
    revenue_growth_rate: float = 0.0
    inventory: float = 0.0
    accounts_receivable: float = 0.0
    accounts_payable: float = 0.0


class FileUploadRequest(BaseModel):
    """Request model for file upload metadata"""
    company_id: int
    file_type: str
    file_size: int