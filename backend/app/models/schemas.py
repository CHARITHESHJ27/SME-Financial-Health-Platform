from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Text,
    ForeignKey, Boolean, JSON, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Reusable Numeric type for financial amounts (₹ values, 2 decimal places, up to 999 crore)
MONEY   = Numeric(15, 2)
# Reusable Numeric type for ratios / scores (0-100 with 4 decimal precision)
SCORE   = Numeric(6, 4)
PERCENT = Numeric(8, 4)


class Organization(Base):
    __tablename__ = "organizations"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(255), nullable=False)
    slug       = Column(String(100), unique=True, nullable=False, index=True)
    plan       = Column(String(20), nullable=False, default="free")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active  = Column(Boolean, default=True, nullable=False)

    members   = relationship("User",    back_populates="organization", passive_deletes=True)
    companies = relationship("Company", back_populates="organization", passive_deletes=True)

    __table_args__ = (
        CheckConstraint("plan IN ('free','pro','enterprise')", name="ck_org_plan"),
    )


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    full_name     = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20), nullable=False, default="member")
    org_id        = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)

    organization = relationship("Organization", back_populates="members")

    __table_args__ = (
        CheckConstraint("role IN ('owner','admin','member')", name="ck_user_role"),
        Index("ix_users_org_id", "org_id"),
    )


class Company(Base):
    __tablename__ = "companies"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(255), nullable=False)
    industry            = Column(String(50), nullable=False)
    gst_number          = Column(String(20), nullable=True)
    registration_date   = Column(DateTime, default=datetime.utcnow, nullable=False)
    language_preference = Column(String(20), default="english", nullable=False)
    org_id              = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active           = Column(Boolean, default=True, nullable=False)

    organization        = relationship("Organization", back_populates="companies")
    financial_statements = relationship(
        "FinancialStatement", back_populates="company",
        cascade="all, delete-orphan", passive_deletes=True
    )
    assessments = relationship(
        "FinancialAssessment", back_populates="company",
        cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        # GST unique per org (not globally — two orgs can track same company)
        UniqueConstraint("gst_number", "org_id", name="uq_company_gst_org"),
        # Company name unique per org
        UniqueConstraint("name", "org_id", name="uq_company_name_org"),
        Index("ix_companies_org_id",  "org_id"),
        Index("ix_companies_industry", "industry"),
        CheckConstraint(
            "industry IN ('manufacturing','retail','services','agriculture','logistics','e-commerce')",
            name="ck_company_industry"
        ),
    )


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id           = Column(Integer, primary_key=True, index=True)
    company_id   = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(DateTime, nullable=True)
    period_end   = Column(DateTime, nullable=True)

    # ── All monetary fields use MONEY (Numeric 15,2) ───────────
    revenue              = Column(MONEY, nullable=True)
    expenses             = Column(MONEY, nullable=True)
    current_assets       = Column(MONEY, nullable=True)
    current_liabilities  = Column(MONEY, nullable=True)
    total_assets         = Column(MONEY, nullable=True)
    total_debt           = Column(MONEY, nullable=True)
    inventory            = Column(MONEY, nullable=True)
    accounts_receivable  = Column(MONEY, nullable=True)
    accounts_payable     = Column(MONEY, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="financial_statements")

    __table_args__ = (
        Index("ix_fs_company_period", "company_id", "period_end"),
    )


class FinancialAssessment(Base):
    __tablename__ = "financial_assessments"

    id         = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    # ── Scores use Numeric(6,4) — e.g. 82.7500 ─────────────────
    overall_health_score  = Column(SCORE, nullable=True)
    liquidity_score       = Column(SCORE, nullable=True)
    profitability_score   = Column(SCORE, nullable=True)
    leverage_score        = Column(SCORE, nullable=True)

    credit_risk_level              = Column(String(10), nullable=True)
    financial_risks                = Column(JSON, nullable=True)
    ai_recommendations             = Column(JSON, nullable=True)
    cost_optimization_suggestions  = Column(JSON, nullable=True)

    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="assessments")

    __table_args__ = (
        CheckConstraint(
            "credit_risk_level IN ('MINIMAL','LOW','MEDIUM','HIGH')",
            name="ck_assessment_risk_level"
        ),
        CheckConstraint("overall_health_score >= 0 AND overall_health_score <= 100",  name="ck_score_overall"),
        CheckConstraint("liquidity_score >= 0 AND liquidity_score <= 100",            name="ck_score_liquidity"),
        CheckConstraint("profitability_score >= 0 AND profitability_score <= 100",    name="ck_score_profitability"),
        CheckConstraint("leverage_score >= 0 AND leverage_score <= 100",              name="ck_score_leverage"),
        Index("ix_fa_company_date", "company_id", "assessment_date"),
    )


class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"

    id           = Column(Integer, primary_key=True, index=True)
    industry     = Column(String(50), nullable=False)
    metric_name  = Column(String(100), nullable=False)
    percentile_25 = Column(PERCENT, nullable=True)
    percentile_50 = Column(PERCENT, nullable=True)
    percentile_75 = Column(PERCENT, nullable=True)
    last_updated  = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("industry", "metric_name", name="uq_benchmark_industry_metric"),
        Index("ix_benchmark_industry", "industry"),
    )
