# setup_financial_metrics_db.py
from sqlalchemy import create_engine
from models import Base, Company, Contact, EmailUpdate, Attachment, Alert
from financial_metrics_models import FinancialMetrics, MetricExtraction
from db import SessionLocal

DATABASE_URL = "sqlite:///tracker.db"

def setup_financial_metrics_tables():
    """Create the financial metrics tables in the existing database"""
    print("💰 Setting up Financial Metrics Database Tables")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create all tables (this will only create new ones, existing ones are unchanged)
        Base.metadata.create_all(engine)
        
        print("✅ Financial metrics tables created successfully!")
        
        # Verify tables exist
        session = SessionLocal()
        
        # Test that we can query the new tables
        metrics_count = session.query(FinancialMetrics).count()
        extractions_count = session.query(MetricExtraction).count()
        
        print(f"📊 Current data:")
        print(f"   Financial Metrics: {metrics_count} records")
        print(f"   Metric Extractions: {extractions_count} records")
        
        session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up financial metrics tables: {e}")
        return False

def show_table_structure():
    """Show the structure of financial metrics tables"""
    print("\n📋 Financial Metrics Table Structure:")
    print("-" * 40)
    
    print("🏦 FINANCIAL_METRICS table:")
    print("   - Core identifiers: id, company_id, email_update_id")
    print("   - Period info: reporting_period, reporting_date, extracted_date")
    print("   - Revenue metrics: MRR, ARR, QRR, total/gross/net revenue")
    print("   - Growth metrics: MRR/ARR/YoY/MoM growth rates")
    print("   - Financial health: cash_balance, net_burn, gross_burn, runway")
    print("   - Profitability: gross_margin, EBITDA, net_income")
    print("   - Customer metrics: count, churn, LTV, CAC")
    print("   - Operational: team_size, bookings, pipeline")
    print("   - Context: highlights, challenges, funding_status")
    print("   - Source: source_type, source_file, confidence, notes")
    
    print("\n🔍 METRIC_EXTRACTIONS table:")
    print("   - Tracking: email_update_id, attachment_id")
    print("   - Process: extraction_method, status, raw_extraction")
    print("   - Error handling: error_message, retry_count")

if __name__ == "__main__":
    if setup_financial_metrics_tables():
        show_table_structure()
        print("\n🚀 Ready to extract financial metrics!")
        print("   Run: python financial_metrics_extractor.py")
    else:
        print("❌ Database setup failed") 