from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from datetime import datetime
import os

from app.models.schemas import Base
from app.database import engine
from app.api.routes import router as api_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SME Financial Health Platform API", 
    version="1.0.0",
    description="""
    ## AI-powered financial health assessment platform for SMEs
    
    This API provides comprehensive financial analysis, credit scoring, and business insights 
    for Small and Medium Enterprises (SMEs). Features include:
    
    * **Financial Health Assessment**: 20+ financial ratios and comprehensive analysis
    * **Credit Scoring**: Advanced scoring algorithm (0-100) with industry adjustments
    * **Industry Benchmarking**: Compare against 6 industry categories
    * **AI-Powered Insights**: OpenAI GPT-powered recommendations and analysis
    * **File Processing**: Support for CSV, XLSX, and PDF financial data
    * **Risk Assessment**: Comprehensive risk analysis and mitigation strategies
    * **GST Compliance**: Mock GST integration and tax optimization
    * **Financial Forecasting**: 12-month predictive analysis
    
    ### Authentication
    Most endpoints require authentication. Use JWT tokens for secure access.
    
    ### Rate Limiting
    API endpoints are rate-limited to prevent abuse:
    - Company creation: 10 requests/hour
    - File uploads: 5 requests/hour
    - Other endpoints: 100 requests/hour
    
    ### Supported Industries
    - Manufacturing
    - Retail
    - Services
    - Agriculture
    - Logistics
    - E-commerce
    """,
    contact={
        "name": "SME Financial Health Platform",
        "email": "support@sme-financial-health.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# CORS middleware with specific origins
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"], summary="API Information")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SME Financial Health Platform API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"], summary="Health Check")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "service": "SME Financial Health Platform",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)