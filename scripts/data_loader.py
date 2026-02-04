#!/usr/bin/env python3
"""
Data Loader Script for SME Financial Health Platform
Loads sample data, industry benchmarks, and initializes the database
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime, timedelta
import random

# Add the backend app to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, Company, FinancialAssessment, FinancialStatement
from core.financial_engine import FinancialAnalyzer
from core.scoring import CreditScorer

class DataLoader:
    def __init__(self, database_url="postgres:///./sme_financial_health.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
        self.analyzer = FinancialAnalyzer()
        self.scorer = CreditScorer()
    
    def load_sample_companies(self):
        """Load sample companies for demonstration"""
        sample_companies = [
            {
                "name": "Tech Solutions Pvt Ltd",
                "industry": "services",
                "gst_number": "27AABCU9603R1ZX",
                "language_preference": "english"
            },
            {
                "name": "Retail Mart Enterprises",
                "industry": "retail",
                "gst_number": "29AABCU9603R1ZY",
                "language_preference": "english"
            },
            {
                "name": "Manufacturing Co Ltd",
                "industry": "manufacturing",
                "gst_number": "24AABCU9603R1ZZ",
                "language_preference": "english"
            },
            {
                "name": "Agri Business Solutions",
                "industry": "agriculture",
                "gst_number": "36AABCU9603R1ZA",
                "language_preference": "hindi"
            },
            {
                "name": "Logistics Express Pvt Ltd",
                "industry": "logistics",
                "gst_number": "19AABCU9603R1ZB",
                "language_preference": "english"
            }
        ]
        
        created_companies = []
        for company_data in sample_companies:
            # Check if company already exists
            existing = self.db.query(Company).filter(Company.gst_number == company_data["gst_number"]).first()
            if not existing:
                company = Company(**company_data)
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
                created_companies.append(company)
                print(f"Created company: {company.name}")
            else:
                created_companies.append(existing)
                print(f"Company already exists: {existing.name}")
        
        return created_companies
    
    def load_sample_financial_data(self, companies):
        """Load sample financial data from CSV files"""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_csv')
        
        # Load retail sample data
        retail_file = os.path.join(data_dir, 'retail_sample.csv')
        if os.path.exists(retail_file):
            df = pd.read_csv(retail_file)
            
            # Find retail company
            retail_company = next((c for c in companies if c.industry == 'retail'), None)
            if retail_company:
                self.create_financial_statements_from_df(retail_company, df)
                print(f"Loaded financial data for {retail_company.name}")
        
        # Generate sample data for other companies
        for company in companies:
            if company.industry != 'retail':  # Skip retail as we loaded from CSV
                self.generate_sample_financial_data(company)
                print(f"Generated sample data for {company.name}")
    
    def create_financial_statements_from_df(self, company, df):
        """Create financial statements from DataFrame"""
        for _, row in df.iterrows():
            # Check if statement already exists for this period
            period_start = datetime.strptime(f"{row['Month']}-01", "%Y-%m-%d")
            existing = self.db.query(FinancialStatement).filter(
                FinancialStatement.company_id == company.id,
                FinancialStatement.period_start == period_start
            ).first()
            
            if not existing:
                statement = FinancialStatement(
                    company_id=company.id,
                    period_start=period_start,
                    period_end=period_start + timedelta(days=30),
                    revenue=row['Revenue'],
                    expenses=row['Expenses'],
                    current_assets=row['Current_Assets'],
                    current_liabilities=row['Current_Liabilities'],
                    total_assets=row['Total_Assets'],
                    total_debt=row['Total_Debt'],
                    inventory=row.get('Inventory', 0),
                    accounts_receivable=row.get('Accounts_Receivable', 0),
                    accounts_payable=row.get('Accounts_Payable', 0)
                )
                self.db.add(statement)
        
        self.db.commit()
    
    def generate_sample_financial_data(self, company):
        """Generate sample financial data for a company"""
        industry_multipliers = {
            'services': {'revenue': 1.0, 'margin': 0.15, 'growth': 0.12},
            'manufacturing': {'revenue': 1.5, 'margin': 0.12, 'growth': 0.08},
            'agriculture': {'revenue': 0.8, 'margin': 0.10, 'growth': 0.04},
            'logistics': {'revenue': 1.2, 'margin': 0.06, 'growth': 0.10},
            'e-commerce': {'revenue': 0.9, 'margin': 0.05, 'growth': 0.25}
        }
        
        multiplier = industry_multipliers.get(company.industry, industry_multipliers['services'])
        base_revenue = 1000000 * multiplier['revenue']  # Base 10 lakh revenue
        
        for i in range(12):  # Generate 12 months of data
            period_start = datetime.now() - timedelta(days=30 * (12 - i))
            
            # Check if statement already exists
            existing = self.db.query(FinancialStatement).filter(
                FinancialStatement.company_id == company.id,
                FinancialStatement.period_start == period_start
            ).first()
            
            if not existing:
                # Add some randomness and growth
                growth_factor = (1 + multiplier['growth']) ** (i / 12)
                monthly_revenue = base_revenue * growth_factor * random.uniform(0.8, 1.2)
                monthly_expenses = monthly_revenue * (1 - multiplier['margin']) * random.uniform(0.9, 1.1)
                
                statement = FinancialStatement(
                    company_id=company.id,
                    period_start=period_start,
                    period_end=period_start + timedelta(days=30),
                    revenue=monthly_revenue,
                    expenses=monthly_expenses,
                    current_assets=monthly_revenue * 0.4 * random.uniform(0.8, 1.2),
                    current_liabilities=monthly_revenue * 0.2 * random.uniform(0.8, 1.2),
                    total_assets=monthly_revenue * 1.2 * random.uniform(0.8, 1.2),
                    total_debt=monthly_revenue * 0.3 * random.uniform(0.5, 1.5),
                    inventory=monthly_revenue * 0.15 * random.uniform(0.5, 1.5),
                    accounts_receivable=monthly_revenue * 0.1 * random.uniform(0.5, 1.5),
                    accounts_payable=monthly_revenue * 0.08 * random.uniform(0.5, 1.5)
                )
                self.db.add(statement)
        
        self.db.commit()
    
    def generate_sample_assessments(self, companies):
        """Generate sample financial assessments"""
        for company in companies:
            # Get latest financial statement
            latest_statement = self.db.query(FinancialStatement).filter(
                FinancialStatement.company_id == company.id
            ).order_by(FinancialStatement.period_start.desc()).first()
            
            if latest_statement:
                # Check if assessment already exists
                existing_assessment = self.db.query(FinancialAssessment).filter(
                    FinancialAssessment.company_id == company.id
                ).first()
                
                if not existing_assessment:
                    # Prepare data for analysis
                    financial_data = {
                        'industry': company.industry,
                        'revenue': latest_statement.revenue,
                        'total_expenses': latest_statement.expenses,
                        'current_assets': latest_statement.current_assets,
                        'current_liabilities': latest_statement.current_liabilities,
                        'total_assets': latest_statement.total_assets,
                        'total_debt': latest_statement.total_debt,
                        'inventory': latest_statement.inventory or 0,
                        'accounts_receivable': latest_statement.accounts_receivable or 0,
                        'accounts_payable': latest_statement.accounts_payable or 0,
                        'revenue_growth_rate': 0.1  # Default 10% growth
                    }
                    
                    # Calculate ratios and scores
                    ratios = self.analyzer.calculate_ratios(financial_data)
                    credit_score = self.scorer.calculate_credit_score(financial_data, ratios)
                    risk_analysis = self.analyzer.assess_risks(financial_data, ratios)
                    recommendations = self.analyzer.generate_recommendations(financial_data, ratios)
                    cost_optimization = self.analyzer.identify_cost_savings(financial_data)
                    
                    # Create assessment
                    assessment = FinancialAssessment(
                        company_id=company.id,
                        overall_health_score=credit_score,
                        liquidity_score=ratios.get('current_ratio', 0) * 25,
                        profitability_score=ratios.get('profit_margin', 0) * 100,
                        leverage_score=max(0, 100 - ratios.get('debt_to_asset_ratio', 0) * 100),
                        credit_risk_level=risk_analysis['risk_level'],
                        financial_risks=risk_analysis['identified_risks'],
                        ai_recommendations=[
                            "Focus on improving cash flow management",
                            "Consider diversifying revenue streams",
                            "Optimize operational efficiency"
                        ],
                        cost_optimization_suggestions=[
                            {
                                'category': 'Technology',
                                'suggestion': 'Implement automation tools',
                                'potential_savings': '5-10%'
                            }
                        ]
                    )
                    
                    self.db.add(assessment)
                    self.db.commit()
                    print(f"Created assessment for {company.name} - Score: {credit_score:.1f}")
    
    def load_industry_benchmarks(self):
        """Load industry benchmark data"""
        benchmarks_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'benchmarks', 'industry_avg.csv')
        
        if os.path.exists(benchmarks_file):
            df = pd.read_csv(benchmarks_file)
            print(f"Loaded industry benchmarks for {len(df)} industries")
            return df
        else:
            print("Industry benchmarks file not found")
            return None
    
    def run_full_data_load(self):
        """Run complete data loading process"""
        print("Starting data loading process...")
        
        # Load companies
        print("\n1. Loading sample companies...")
        companies = self.load_sample_companies()
        
        # Load financial data
        print("\n2. Loading financial data...")
        self.load_sample_financial_data(companies)
        
        # Generate assessments
        print("\n3. Generating financial assessments...")
        self.generate_sample_assessments(companies)
        
        # Load benchmarks
        print("\n4. Loading industry benchmarks...")
        self.load_industry_benchmarks()
        
        print("\n✅ Data loading completed successfully!")
        print(f"Created {len(companies)} companies with financial data and assessments")
        
        # Print summary
        print("\n📊 Summary:")
        for company in companies:
            assessments_count = self.db.query(FinancialAssessment).filter(
                FinancialAssessment.company_id == company.id
            ).count()
            statements_count = self.db.query(FinancialStatement).filter(
                FinancialStatement.company_id == company.id
            ).count()
            print(f"  • {company.name} ({company.industry}): {statements_count} statements, {assessments_count} assessments")
    
    def cleanup_data(self):
        """Clean up all data (use with caution!)"""
        print("⚠️  Cleaning up all data...")
        self.db.query(FinancialAssessment).delete()
        self.db.query(FinancialStatement).delete()
        self.db.query(Company).delete()
        self.db.commit()
        print("✅ All data cleaned up")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to run data loading"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SME Financial Health Platform Data Loader')
    parser.add_argument('--database-url', default="sqlite:///./sme_financial_health.db",
                       help='Database URL (default: SQLite)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up all existing data before loading')
    parser.add_argument('--load-only', choices=['companies', 'financial', 'assessments', 'benchmarks'],
                       help='Load only specific data type')
    
    args = parser.parse_args()
    
    # Initialize data loader
    loader = DataLoader(args.database_url)
    
    try:
        if args.cleanup:
            loader.cleanup_data()
        
        if args.load_only:
            companies = loader.load_sample_companies()
            if args.load_only == 'companies':
                print("✅ Companies loaded")
            elif args.load_only == 'financial':
                loader.load_sample_financial_data(companies)
                print("✅ Financial data loaded")
            elif args.load_only == 'assessments':
                loader.generate_sample_assessments(companies)
                print("✅ Assessments generated")
            elif args.load_only == 'benchmarks':
                loader.load_industry_benchmarks()
                print("✅ Benchmarks loaded")
        else:
            # Run full data load
            loader.run_full_data_load()
    
    except Exception as e:
        print(f"❌ Error during data loading: {e}")
        raise
    finally:
        loader.close()

if __name__ == "__main__":
    main()