import os
import sys
from pathlib import Path

backend_path = str(Path(__file__).parent.parent.parent / "backend")
root_path = str(Path(__file__).parent.parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models.schemas import Base, Company, Organization, User

# In-memory SQLite for fast, isolated API integration tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed test organization and company
    company = Company(
        id=1,
        name="Global Manufacturing Pvt Ltd",
        industry="manufacturing",
        gst_number="27AABCU9603R1ZX",
        language_preference="english"
    )
    db.add(company)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_health_endpoints():
    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "alive"

    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] in ["ready", "degraded"]
    assert ready_resp.json()["models"]["status"] == "ready"

    model_resp = client.get("/health/model")
    assert model_resp.status_code == 200
    assert model_resp.json()["status"] == "ready"
    assert "risk_model" in model_resp.json()


def test_assess_financial_health_api():
    payload = {
        "revenue": 15_000_000.0,
        "total_expenses": 13_000_000.0,
        "current_assets": 6_000_000.0,
        "current_liabilities": 4_000_000.0,
        "total_assets": 12_000_000.0,
        "total_debt": 5_000_000.0,
        "inventory": 2_000_000.0,
        "accounts_receivable": 2_500_000.0,
        "accounts_payable": 1_800_000.0,
        "revenue_growth_rate": 0.10
    }
    resp = client.post("/api/v1/companies/1/assess", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "success"
    assert "data" in data
    assert "risk" in data["data"]
    assert "recommendations" in data["data"]
    assert "explanations" in data["data"]
    assert "financial_ratios" in data["data"]

    # Verify risk contract
    risk = data["data"]["risk"]
    assert 0 <= risk["score"] <= 100
    assert 0.0 <= risk["probability"] <= 1.0
    assert risk["category"] in ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
    assert "risk-model" in risk["model_version"]

    # Verify recommendations
    recs = data["data"]["recommendations"]
    assert len(recs) > 0
    for r in recs:
        assert "code" in r
        assert "priority" in r
        assert "confidence" in r
        assert "severity" in r
        assert "impact" in r
        assert "rationale" in r

    # Verify SHAP explanations
    explanations = data["data"]["explanations"]
    assert len(explanations) > 0
    for exp in explanations:
        assert "feature" in exp
        assert "value" in exp
        assert "contribution" in exp
        assert "direction" in exp
        assert "impact" in exp


def test_dashboard_endpoint_returns_ml_data():
    # Run assessment first
    payload = {
        "revenue": 10_000_000.0,
        "total_expenses": 8_500_000.0,
        "current_assets": 4_000_000.0,
        "current_liabilities": 2_500_000.0,
        "total_assets": 8_000_000.0,
        "total_debt": 3_000_000.0,
        "inventory": 1_000_000.0,
        "accounts_receivable": 1_500_000.0,
        "accounts_payable": 1_000_000.0,
        "revenue_growth_rate": 0.12
    }
    client.post("/api/v1/companies/1/assess", json=payload)

    dash_resp = client.get("/api/v1/companies/1/dashboard")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()

    assert dash_data["status"] == "success"
    assert "risk_assessment" in dash_data
    assert "score" in dash_data["risk_assessment"]
    assert "probability" in dash_data["risk_assessment"]
    assert "recommendations" in dash_data
    assert "shap_explanations" in dash_data


def test_auth_registration_and_login():
    # 1. Register new user
    register_payload = {
        "full_name": "Test Founder",
        "email": "founder@example.com",
        "password": "SecurePassword123!",
        "org_name": "Acme Innovations"
    }
    reg_resp = client.post("/api/v1/auth/register", json=register_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert "user" in reg_data
    assert reg_data["user"]["email"] == "founder@example.com"

    token = reg_data["access_token"]

    # 2. Login with registered credentials
    login_payload = {
        "email": "founder@example.com",
        "password": "SecurePassword123!"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data

    # 3. Authenticated /auth/me check
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["user"]["email"] == "founder@example.com"
    assert me_data["user"]["full_name"] == "Test Founder"
