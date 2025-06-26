#!/usr/bin/env python3
"""
Smart Baseline Reset

This script:
1. Sets April 30th as baseline for all companies
2. Preserves recent real email updates (June 2025)
3. Creates a realistic testing scenario
"""

import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Company, Contact, EmailUpdate, Alert, Base

def smart_baseline_reset(db_path="tracker.db", baseline_date="2025-04-30", preserve_after_date="2025-06-01"):
    """Smart reset that preserves recent real emails but sets baseline for others."""
    
    # Parse dates
    baseline_datetime = datetime.strptime(baseline_date, "%Y-%m-%d")
    preserve_after_datetime = datetime.strptime(preserve_after_date, "%Y-%m-%d")
    
    # Initialize database connection
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"🎯 SMART BASELINE RESET")
    print(f"📅 Baseline Date: {baseline_date}")
    print(f"🔒 Preserve emails after: {preserve_after_date}")
    print("=" * 60)
    
    # Get all companies
    companies = session.query(Company).all()
    print(f"📊 Processing {len(companies)} companies...")
    
    companies_with_recent_emails = 0
    companies_with_baseline_only = 0
    recent_emails_preserved = 0
    baseline_emails_created = 0
    
    for company in companies:
        # Get all emails for this company
        all_emails = session.query(EmailUpdate)\
            .filter(EmailUpdate.company_id == company.id)\
            .order_by(EmailUpdate.date.desc())\
            .all()
        
        # Check if company has recent real emails (after June 1st)
        recent_emails = [email for email in all_emails if email.date >= preserve_after_datetime]
        
        if recent_emails:
            # Company has recent real emails - preserve them and add baseline
            companies_with_recent_emails += 1
            recent_emails_preserved += len(recent_emails)
            
            # Delete old baseline emails (before June 1st)
            old_emails = [email for email in all_emails if email.date < preserve_after_datetime]
            for old_email in old_emails:
                session.delete(old_email)
            
            # Add baseline email
            baseline_email = EmailUpdate(
                company_id=company.id,
                sender=f"updates@{company.name.lower().replace(' ', '').replace('.', '').replace('/', '')}example.com",
                subject=f"{company.name} - Monthly Update (Baseline)",
                body=f"Baseline update for {company.name} on {baseline_date} for alert system testing.",
                date=baseline_datetime,
                has_attachments=False,
                processed_at=datetime.now()
            )
            session.add(baseline_email)
            baseline_emails_created += 1
            
            print(f"  🔄 {company.name}: Kept {len(recent_emails)} recent email(s) + added baseline")
            
        else:
            # Company has no recent emails - replace all with baseline
            companies_with_baseline_only += 1
            
            # Delete all existing emails
            for email in all_emails:
                session.delete(email)
            
            # Add baseline email
            baseline_email = EmailUpdate(
                company_id=company.id,
                sender=f"updates@{company.name.lower().replace(' ', '').replace('.', '').replace('/', '')}example.com",
                subject=f"{company.name} - Monthly Update (Baseline)",
                body=f"Baseline update for {company.name} on {baseline_date} for alert system testing.",
                date=baseline_datetime,
                has_attachments=False,
                processed_at=datetime.now()
            )
            session.add(baseline_email)
            baseline_emails_created += 1
            
            if companies_with_baseline_only <= 5:  # Show first 5 examples
                print(f"  📅 {company.name}: Set to baseline only")
    
    # Clear existing alerts
    existing_alerts = session.query(Alert).count()
    if existing_alerts > 0:
        session.query(Alert).delete()
        print(f"🗑️  Cleared {existing_alerts} existing alerts")
    
    # Commit changes
    session.commit()
    
    print(f"\n📈 SMART RESET SUMMARY:")
    print(f"   Companies with recent emails preserved: {companies_with_recent_emails}")
    print(f"   Companies with baseline only: {companies_with_baseline_only}")
    print(f"   Recent emails preserved: {recent_emails_preserved}")
    print(f"   Baseline emails created: {baseline_emails_created}")
    
    # Calculate alert scenarios
    today = datetime.now()
    days_since_baseline = (today - baseline_datetime).days
    
    print(f"\n🎯 ALERT TESTING SCENARIOS:")
    print(f"   Baseline companies ({companies_with_baseline_only}): {days_since_baseline} days → 1-month alerts")
    print(f"   Recent email companies ({companies_with_recent_emails}): No alerts needed yet")
    
    # Show some examples of companies with recent emails
    print(f"\n📧 COMPANIES WITH RECENT REAL EMAILS:")
    recent_companies = []
    for company in companies:
        latest_email = session.query(EmailUpdate)\
            .filter(EmailUpdate.company_id == company.id)\
            .filter(EmailUpdate.date >= preserve_after_datetime)\
            .order_by(EmailUpdate.date.desc())\
            .first()
        if latest_email:
            recent_companies.append((company.name, latest_email.date))
    
    # Sort by date and show recent ones
    recent_companies.sort(key=lambda x: x[1], reverse=True)
    for company_name, date in recent_companies[:10]:
        days_ago = (today - date).days
        print(f"   • {company_name}: {date.strftime('%Y-%m-%d')} ({days_ago} days ago)")
    
    session.close()
    print(f"\n✅ Smart baseline reset complete!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart baseline reset preserving recent emails")
    parser.add_argument("--baseline", default="2025-04-30", help="Baseline date (YYYY-MM-DD)")
    parser.add_argument("--preserve-after", default="2025-06-01", help="Preserve emails after this date")
    parser.add_argument("--db", default="tracker.db", help="Database file path")
    
    args = parser.parse_args()
    
    print(f"⚠️  This will set {args.baseline} as baseline while preserving recent emails")
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm == 'y':
        smart_baseline_reset(args.db, args.baseline, args.preserve_after)
    else:
        print("❌ Operation cancelled") 