from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)  # Manufacturing, Retail, etc.
    gst_number = Column(String, unique=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    language_preference = Column(String, default="english")
    
    # Relationships
    financial_statements = relationship("FinancialStatement", back_populates="company")
    assessments = relationship("FinancialAssessment", back_populates="company")

class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Financial data fields
    revenue = Column(Float)
    expenses = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    total_assets = Column(Float)
    total_debt = Column(Float)
    inventory = Column(Float)
    accounts_receivable = Column(Float)
    accounts_payable = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="financial_statements")

class FinancialAssessment(Base):
    __tablename__ = "financial_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Assessment scores (0-100)
    overall_health_score = Column(Float)
    liquidity_score = Column(Float)
    profitability_score = Column(Float)
    leverage_score = Column(Float)
    
    # Risk assessment
    credit_risk_level = Column(String)  # MINIMAL, LOW, MEDIUM, HIGH
    financial_risks = Column(JSON)
    
    # Recommendations
    ai_recommendations = Column(JSON)
    cost_optimization_suggestions = Column(JSON)
    
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="assessments")

class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    percentile_25 = Column(Float)
    percentile_50 = Column(Float)
    percentile_75 = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)