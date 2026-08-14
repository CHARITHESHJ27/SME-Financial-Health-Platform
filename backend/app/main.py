import sys
import os
from pathlib import Path

# Add project root and backend directory to sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from datetime import datetime

from app.models.schemas import Base
from app.database import engine
from app.api.routes import router as api_router
from app.auth import auth_router

# ── Production safety guard ───────────────────────────────────────────────────
_ENV  = os.getenv("ENVIRONMENT", "development")
_SECRET = os.getenv("JWT_SECRET_KEY", "")
if _ENV == "production" and (not _SECRET or "change" in _SECRET.lower() or len(_SECRET) < 32):
    print("FATAL: JWT_SECRET_KEY is not set or insecure. Refusing to start in production.")
    sys.exit(1)

# Create tables only if database is available
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("Application will continue without database functionality")

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
    allowed_hosts=["localhost", "127.0.0.1", "testserver", "*.localhost", "*.onrender.com", "*.vercel.app"]
)

# CORS — reads origins from env so no code change needed for production
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
origins = list({
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://sme-financial-health-platform-pi.vercel.app",
    _frontend_url,          # production domain from .env
})
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"], summary="API Information")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SME Financial Health Platform API — Explainable ML Risk & Recommendation Engine",
        "version": "1.0.0",
        "status": "running",
        "ml_pipeline": "active",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"], summary="Health Check")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "SME Financial Health Platform",
        "version": "1.0.0"
    }

@app.get("/health/live", tags=["Health"], summary="Liveness Probe")
async def liveness_probe():
    """Liveness probe: verifies process is alive and responsive"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/health/ready", tags=["Health"], summary="Readiness Probe")
async def readiness_probe():
    """Readiness probe: verifies database connectivity and model availability"""
    from ml.inference.model_manager import ModelManager
    manager = ModelManager()
    model_status = manager.is_healthy()
    
    # Check DB
    db_ok = True
    try:
        with engine.connect() as conn:
            pass
    except Exception:
        db_ok = False

    is_ready = db_ok and (model_status["status"] == "ready")
    return {
        "status": "ready" if is_ready else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "models": model_status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/health/model", tags=["Health"], summary="Model Artifact Status")
async def model_status():
    """Detailed ML model readiness and version check"""
    from ml.inference.model_manager import ModelManager
    manager = ModelManager()
    return manager.is_healthy()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)