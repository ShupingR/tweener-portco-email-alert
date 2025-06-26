#!/usr/bin/env python3
"""
Reset Company Update Dates

This script marks all companies as if they provided updates on May 30, 2025.
This creates a clean baseline for testing the alert system.
"""

import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Company, Contact, EmailUpdate, Alert, Base

def reset_company_dates(db_path="tracker.db", baseline_date="2025-05-30"):
    """Mark all companies as having provided updates on the baseline date."""
    
    # Parse the baseline date
    baseline_datetime = datetime.strptime(baseline_date, "%Y-%m-%d")
    
    # Initialize database connection
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"🔄 RESETTING COMPANY UPDATE DATES")
    print(f"📅 Baseline Date: {baseline_date}")
    print("=" * 50)
    
    # Get all companies
    companies = session.query(Company).all()
    print(f"📊 Found {len(companies)} companies")
    
    # Create fake email updates for companies that don't have any
    companies_updated = 0
    companies_with_existing_emails = 0
    
    for company in companies:
        # Check if company already has email updates
        existing_emails = session.query(EmailUpdate)\
            .filter(EmailUpdate.company_id == company.id)\
            .count()
        
        if existing_emails > 0:
            companies_with_existing_emails += 1
            print(f"  ✅ {company.name}: Already has {existing_emails} email(s)")
        else:
            # Create a fake email update for this company
            fake_email = EmailUpdate(
                company_id=company.id,
                sender=f"updates@{company.name.lower().replace(' ', '')}.com",
                subject=f"{company.name} - Monthly Update (Baseline)",
                body=f"This is a baseline update entry for {company.name} created on {baseline_date} for alert system testing purposes.",
                date=baseline_datetime,
                has_attachments=False,
                processed_at=datetime.now()
            )
            session.add(fake_email)
            companies_updated += 1
    
    # Commit the changes
    session.commit()
    
    # Clear any existing alerts since we're resetting
    existing_alerts = session.query(Alert).count()
    if existing_alerts > 0:
        session.query(Alert).delete()
        session.commit()
        print(f"🗑️  Cleared {existing_alerts} existing alerts")
    
    print(f"\n📈 RESET SUMMARY:")
    print(f"   Companies with existing emails: {companies_with_existing_emails}")
    print(f"   Companies given baseline updates: {companies_updated}")
    print(f"   Total companies: {len(companies)}")
    print(f"   Baseline date: {baseline_date}")
    
    # Verify the reset
    total_emails = session.query(EmailUpdate).count()
    companies_with_emails = session.query(EmailUpdate.company_id).distinct().count()
    
    print(f"\n✅ VERIFICATION:")
    print(f"   Total email updates in database: {total_emails}")
    print(f"   Companies with email updates: {companies_with_emails}")
    print(f"   Companies without email updates: {len(companies) - companies_with_emails}")
    
    session.close()
    
    print(f"\n🎯 All companies now have baseline updates from {baseline_date}")
    print("   Alert system is reset and ready for testing!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Reset company update dates for alert system testing")
    parser.add_argument("--date", default="2025-05-30", help="Baseline date (YYYY-MM-DD)")
    parser.add_argument("--db", default="tracker.db", help="Database file path")
    
    args = parser.parse_args()
    
    # Confirm before proceeding
    print(f"⚠️  This will mark all companies as having updates on {args.date}")
    print("   This is for testing purposes only.")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm == 'y':
        reset_company_dates(args.db, args.date)
    else:
        print("❌ Operation cancelled") 