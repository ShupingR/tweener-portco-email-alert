#!/usr/bin/env python3
"""
Force Reset All Email Update Dates

This script forcibly updates ALL email update dates to a specific baseline date.
This is for testing the alert system with specific time scenarios.
"""

import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Company, Contact, EmailUpdate, Alert, Base

def force_reset_all_dates(db_path="tracker.db", baseline_date="2025-04-30"):
    """Force all email updates to have the baseline date."""
    
    # Parse the baseline date
    baseline_datetime = datetime.strptime(baseline_date, "%Y-%m-%d")
    
    # Initialize database connection
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"🔄 FORCE RESETTING ALL EMAIL DATES")
    print(f"📅 New Date: {baseline_date}")
    print("=" * 50)
    
    # Get all email updates
    all_emails = session.query(EmailUpdate).all()
    print(f"📧 Found {len(all_emails)} email updates")
    
    # Update all email dates
    updated_count = 0
    for email in all_emails:
        old_date = email.date
        email.date = baseline_datetime
        updated_count += 1
        
        if updated_count <= 10:  # Show first 10 as examples
            company = session.query(Company).get(email.company_id)
            print(f"  📧 {company.name}: {old_date} → {baseline_datetime}")
    
    # Clear any existing alerts
    existing_alerts = session.query(Alert).count()
    if existing_alerts > 0:
        session.query(Alert).delete()
        print(f"🗑️  Cleared {existing_alerts} existing alerts")
    
    # Commit the changes
    session.commit()
    
    print(f"\n📈 FORCE RESET SUMMARY:")
    print(f"   Email updates modified: {updated_count}")
    print(f"   New baseline date: {baseline_date}")
    
    # Calculate days since baseline
    today = datetime.now()
    days_since_baseline = (today - baseline_datetime).days
    
    print(f"   Days since baseline: {days_since_baseline}")
    print(f"   Alert status:")
    print(f"     • 1-month threshold (31 days): {'✅ PASSED' if days_since_baseline > 31 else '❌ Not yet'}")
    print(f"     • 2-month threshold (62 days): {'✅ PASSED' if days_since_baseline > 62 else '❌ Not yet'}")
    print(f"     • 3-month threshold (93 days): {'✅ PASSED' if days_since_baseline > 93 else '❌ Not yet'}")
    
    session.close()
    
    print(f"\n🎯 All email dates reset to {baseline_date}")
    print("   Alert system ready for testing!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Force reset all email dates for alert system testing")
    parser.add_argument("--date", default="2025-04-30", help="Baseline date (YYYY-MM-DD)")
    parser.add_argument("--db", default="tracker.db", help="Database file path")
    
    args = parser.parse_args()
    
    # Confirm before proceeding
    print(f"⚠️  This will OVERWRITE all email dates to {args.date}")
    print("   This is for testing purposes only and cannot be undone easily.")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm == 'y':
        force_reset_all_dates(args.db, args.date)
    else:
        print("❌ Operation cancelled") 