from fastapi import UploadFile, HTTPException
import pandas as pd
from typing import Dict, Any

from app.core.financial_engine import FinancialAnalyzer
from app.services.validation_service import ValidationService


class FileProcessingService:
    
    def __init__(self):
        self.analyzer = FinancialAnalyzer()
        self.validator = ValidationService()
    
    def process_financial_file(self, file: UploadFile) -> Dict[str, Any]:
        """Process uploaded financial file"""
        
        # Validate file
        self.validator.validate_file_upload(file)
        
        try:
            if file.filename.endswith('.csv'):
                return self._process_csv(file)
            elif file.filename.endswith(('.xlsx', '.xls')):
                return self._process_excel(file)
            elif file.filename.endswith('.pdf'):
                return self._process_pdf(file)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Unsupported file format"
                )
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Error processing file: {str(e)}"
            )
    
    def _process_csv(self, file: UploadFile) -> Dict[str, Any]:
        """Process CSV file"""
        df = pd.read_csv(file.file)
        return self._extract_and_assess_data(df)
    
    def _process_excel(self, file: UploadFile) -> Dict[str, Any]:
        """Process Excel file"""
        df = pd.read_excel(file.file)
        return self._extract_and_assess_data(df)
    
    def _process_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """Process PDF file"""
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        financial_summary = self.analyzer.extract_from_pdf_text(text)
        return {
            "message": "File processed successfully",
            "extracted_data": financial_summary,
            "data_quality_score": 85  # PDF extraction has lower confidence
        }
    
    def _extract_and_assess_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract financial data and assess quality using core analyzer"""
        financial_summary = self.analyzer.extract_financial_data(df)
        quality_score = self.analyzer.assess_data_quality(df)
        
        return {
            "message": "File processed successfully",
            "extracted_data": financial_summary,
            "data_quality_score": quality_score
        }