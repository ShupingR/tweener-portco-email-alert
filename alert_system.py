#!/usr/bin/env python3
"""
Alert System for Tweener Fund Portfolio Company Updates

This system monitors portfolio companies and sends automated reminders:
- 1 month + 1 day: First reminder to company contacts
- 2 months + 2 days: Second reminder to company contacts  
- 3 months + 3 days: Escalation to GPs (Scot & Shuping)

Usage:
    python alert_system.py --check    # Check for companies needing alerts
    python alert_system.py --send     # Send pending alerts
    python alert_system.py --report   # Generate alert report
"""

import os
import sys
import argparse
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import Company, Contact, EmailUpdate, Alert, Base

# Load environment variables
load_dotenv()

class AlertSystem:
    def __init__(self, db_path="tracker.db"):
        """Initialize the alert system with database connection."""
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_username = os.getenv("GMAIL_USERNAME")
        self.email_password = os.getenv("GMAIL_PASSWORD")
        
        # Team contacts for escalation
        self.gp_emails = [
            "scot@tweenerfund.com",
            "robbie@tweenerfund.com"
        ]
        self.partner_emails = [
            "nikita@tweenerfund.com"
        ]
        self.eir_emails = [
            "shuping@tweenerfund.com"
        ]
        
        # Alert thresholds (days)
        self.alert_thresholds = {
            "1_month": 31,      # 1 month + 1 day
            "2_month": 62,      # 2 months + 2 days
            "3_month_escalation": 93  # 3 months + 3 days
        }

    def get_companies_needing_alerts(self):
        """Find companies that need alerts based on their last update."""
        today = datetime.now()
        companies_needing_alerts = []
        
        # Get only Tweener portfolio companies (exclude non-portfolio companies from alerts)
        companies = self.session.query(Company).filter(Company.is_tweener_portfolio == True).all()
        
        for company in companies:
            # Get the most recent email update for this company
            latest_email = self.session.query(EmailUpdate)\
                .filter(EmailUpdate.company_id == company.id)\
                .order_by(EmailUpdate.date.desc())\
                .first()
            
            if not latest_email:
                # No emails ever received - check from a baseline date
                # For now, assume companies should send updates monthly
                days_since_last = 999  # Very high number to trigger alerts
                last_update_date = None
            else:
                days_since_last = (today - latest_email.date).days
                last_update_date = latest_email.date
            
            # Check what alerts have already been sent
            existing_alerts = self.session.query(Alert)\
                .filter(Alert.company_id == company.id, Alert.resolved == False)\
                .all()
            
            existing_alert_types = {alert.alert_type for alert in existing_alerts}
            
            # Determine what alerts are needed
            alerts_needed = []
            
            if days_since_last >= self.alert_thresholds["3_month_escalation"]:
                if "3_month_escalation" not in existing_alert_types:
                    alerts_needed.append("3_month_escalation")
            elif days_since_last >= self.alert_thresholds["2_month"]:
                if "2_month" not in existing_alert_types:
                    alerts_needed.append("2_month")
            elif days_since_last >= self.alert_thresholds["1_month"]:
                if "1_month" not in existing_alert_types:
                    alerts_needed.append("1_month")
            
            if alerts_needed:
                companies_needing_alerts.append({
                    "company": company,
                    "days_since_last": days_since_last,
                    "last_update_date": last_update_date,
                    "alerts_needed": alerts_needed,
                    "contacts": company.contacts
                })
        
        return companies_needing_alerts

    def create_alert_email(self, company, alert_type, contacts):
        """Create email content for different alert types."""
        
        # Email templates
        templates = {
            "1_month": {
                "subject": f"Reminder: Monthly Update Request - {company.name}",
                "body": f"""Dear {company.name} Team,

I hope this email finds you well. We noticed that we haven't received your monthly investor update in over a month.

As part of our ongoing partnership, we greatly value staying informed about your progress, challenges, and achievements. Your regular updates help us provide better support and identify opportunities where we can assist.

Could you please send us your latest company update when convenient? We're particularly interested in:

• Key metrics and performance indicators
• Recent milestones and achievements  
• Current challenges or areas where we might help
• Financial highlights
• Team updates and hiring needs

Thank you for taking the time to keep us informed. We're here to support your continued success.

Best regards,
Tweener Fund Team

---
This is an automated reminder. If you have questions, please reply to this email.
"""
            },
            "2_month": {
                "subject": f"Second Reminder: Update Request - {company.name}",
                "body": f"""Dear {company.name} Team,

We're following up on our previous request for your monthly investor update. It's been over two months since we last heard from you, and we want to ensure everything is going well.

Your regular communication is important to us as your investment partner. We understand that running a business keeps you incredibly busy, but these updates help us:

• Better understand your current situation
• Identify ways we can provide support
• Connect you with relevant opportunities in our network
• Maintain strong investor relations

Please send us a brief update covering:
• Current business status and key metrics
• Any challenges you're facing
• Recent wins or milestones
• How we can help

We're committed to supporting your success and would appreciate hearing from you soon.

Best regards,
Tweener Fund Team

---
This is an automated follow-up. Please reply if you need assistance or have questions.
"""
            },
            "3_month_escalation": {
                "subject": f"URGENT: Communication Needed - {company.name}",
                "body": f"""Dear {company.name} Team,

We are concerned that we haven't received any updates from {company.name} in over three months. As your investment partner, regular communication is essential for maintaining our relationship and providing appropriate support.

This extended silence is unusual and we want to ensure:
• Your business operations are continuing normally
• You don't need immediate assistance or support
• There are no critical issues we should be aware of

IMMEDIATE ACTION REQUESTED:
Please respond to this email within 48 hours with a status update, even if brief. We need to know:

1. Current operational status of the company
2. Any significant changes or challenges
3. Whether you need immediate support or assistance
4. Confirmation of your ongoing commitment to investor communications

If we don't hear from you within 48 hours, we will need to escalate this matter to explore other communication channels and ensure the wellbeing of our investment.

We value our partnership and want to resolve this communication gap quickly.

Urgent regards,
Tweener Fund Team

CC: Scot Wingo, Robbie Allen, Nikita Ramaswamy, Shuping Dluge

---
This is an urgent automated escalation. Immediate response required.
"""
            }
        }
        
        return templates[alert_type]

    def send_email(self, to_emails, subject, body, cc_emails=None):
        """Send email using SMTP."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
                to_emails = to_emails + cc_emails
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_username, to_emails, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False

    def send_alerts(self, dry_run=False):
        """Send alerts for companies that need them."""
        companies_needing_alerts = self.get_companies_needing_alerts()
        
        if not companies_needing_alerts:
            print("✅ No companies need alerts at this time.")
            return
        
        print(f"📧 Found {len(companies_needing_alerts)} companies needing alerts")
        
        for company_data in companies_needing_alerts:
            company = company_data["company"]
            alerts_needed = company_data["alerts_needed"]
            contacts = company_data["contacts"]
            days_since_last = company_data["days_since_last"]
            
            print(f"\n📤 Processing alerts for {company.name} ({days_since_last} days since last update)")
            
            # Get contact emails
            contact_emails = [contact.email for contact in contacts if contact.email and not contact.email_bounced]
            
            if not contact_emails:
                print(f"⚠️  No valid contact emails for {company.name}")
                continue
            
            for alert_type in alerts_needed:
                print(f"  📧 Sending {alert_type} alert...")
                
                # Create email content
                email_content = self.create_alert_email(company, alert_type, contacts)
                
                # For escalation, CC the GPs
                cc_emails = self.get_escalation_contacts(alert_type)
                
                if dry_run:
                    print(f"  🔍 DRY RUN - Would send to: {', '.join(contact_emails)}")
                    if cc_emails:
                        print(f"  🔍 DRY RUN - Would CC: {', '.join(cc_emails)}")
                    print(f"  🔍 Subject: {email_content['subject']}")
                else:
                    # Send the email
                    success = self.send_email(
                        to_emails=contact_emails,
                        subject=email_content['subject'],
                        body=email_content['body'],
                        cc_emails=cc_emails
                    )
                    
                    if success:
                        # Record the alert in database
                        alert = Alert(
                            company_id=company.id,
                            alert_type=alert_type,
                            sent_date=datetime.now(),
                            resolved=False
                        )
                        self.session.add(alert)
                        self.session.commit()
                        
                        print(f"  ✅ {alert_type} alert sent successfully")
                    else:
                        print(f"  ❌ Failed to send {alert_type} alert")

    def generate_report(self):
        """Generate a comprehensive alert report."""
        print("📊 TWEENER FUND ALERT SYSTEM REPORT")
        print("=" * 50)
        
        # Get current status
        companies_needing_alerts = self.get_companies_needing_alerts()
        
        # Get alert statistics
        total_companies = self.session.query(Company).count()
        companies_with_emails = self.session.query(func.count(func.distinct(EmailUpdate.company_id))).scalar()
        companies_without_emails = total_companies - companies_with_emails
        
        # Recent alerts
        recent_alerts = self.session.query(Alert)\
            .filter(Alert.sent_date >= datetime.now() - timedelta(days=30))\
            .count()
        
        print(f"📈 PORTFOLIO OVERVIEW:")
        print(f"   Total Companies: {total_companies}")
        print(f"   Companies with Email Updates: {companies_with_emails}")
        print(f"   Companies without Email Updates: {companies_without_emails}")
        print(f"   Recent Alerts (30 days): {recent_alerts}")
        
        print(f"\n🚨 COMPANIES NEEDING ALERTS: {len(companies_needing_alerts)}")
        
        if companies_needing_alerts:
            # Group by alert type
            alert_breakdown = {"1_month": [], "2_month": [], "3_month_escalation": []}
            
            for company_data in companies_needing_alerts:
                company = company_data["company"]
                days_since_last = company_data["days_since_last"]
                alerts_needed = company_data["alerts_needed"]
                
                for alert_type in alerts_needed:
                    alert_breakdown[alert_type].append({
                        "name": company.name,
                        "days": days_since_last,
                        "contacts": len(company.contacts)
                    })
            
            for alert_type, companies in alert_breakdown.items():
                if companies:
                    print(f"\n   {alert_type.upper().replace('_', ' ')}:")
                    for company in companies:
                        print(f"     • {company['name']} ({company['days']} days, {company['contacts']} contacts)")
        
        # Recent email activity
        print(f"\n📧 RECENT EMAIL ACTIVITY (Last 30 days):")
        recent_emails = self.session.query(EmailUpdate)\
            .filter(EmailUpdate.date >= datetime.now() - timedelta(days=30))\
            .order_by(EmailUpdate.date.desc())\
            .limit(10)\
            .all()
        
        if recent_emails:
            for email in recent_emails:
                company = self.session.query(Company).get(email.company_id)
                print(f"   • {company.name}: {email.subject[:50]}... ({email.date.strftime('%Y-%m-%d')})")
        else:
            print("   No recent email updates")
        
        print(f"\n" + "=" * 50)

    def mark_alert_resolved(self, company_name):
        """Mark alerts as resolved when a company sends an update."""
        company = self.session.query(Company).filter(Company.name == company_name).first()
        if company:
            unresolved_alerts = self.session.query(Alert)\
                .filter(Alert.company_id == company.id, Alert.resolved == False)\
                .all()
            
            for alert in unresolved_alerts:
                alert.resolved = True
                alert.resolved_date = datetime.now()
            
            self.session.commit()
            print(f"✅ Marked {len(unresolved_alerts)} alerts as resolved for {company_name}")

    def get_escalation_contacts(self, alert_type):
        """Get the appropriate contacts for escalation based on alert type."""
        if alert_type == "3_month_escalation":
            # Escalate to GPs (General Partners), Partner, and EIR
            return self.gp_emails + self.partner_emails + self.eir_emails
        elif alert_type == "2_month":
            # Could escalate to Partner if needed
            return None  # For now, no escalation at 2-month level
        else:
            return None

def main():
    parser = argparse.ArgumentParser(description="Tweener Fund Alert System")
    parser.add_argument("--check", action="store_true", help="Check for companies needing alerts")
    parser.add_argument("--send", action="store_true", help="Send pending alerts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be sent without sending")
    parser.add_argument("--report", action="store_true", help="Generate alert report")
    parser.add_argument("--resolve", type=str, help="Mark alerts resolved for company name")
    
    args = parser.parse_args()
    
    # Initialize alert system
    alert_system = AlertSystem()
    
    if args.check or args.send or args.dry_run:
        if args.dry_run or args.check:
            print("🔍 CHECKING FOR COMPANIES NEEDING ALERTS...")
            alert_system.send_alerts(dry_run=True)
        elif args.send:
            print("📧 SENDING ALERTS...")
            alert_system.send_alerts(dry_run=False)
    
    elif args.report:
        alert_system.generate_report()
    
    elif args.resolve:
        alert_system.mark_alert_resolved(args.resolve)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 