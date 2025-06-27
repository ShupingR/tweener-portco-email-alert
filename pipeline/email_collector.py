#!/usr/bin/env python3
"""
Daily Email Collector for Tweener Fund
=====================================

Simple command to run daily for collecting and processing portfolio company emails.
This script focuses only on data gathering - no alerts are sent.

Usage:
    python daily_email_collector.py [--days=7] [--dry-run]

Features:
- Fetches emails from configured forwarders
- Uses Claude AI to identify company updates
- Downloads and organizes attachments
- Updates database with new email records
- Tracks both portfolio and non-portfolio companies
- Safe dry-run mode for testing
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our modules using new structure
from pipeline.email_processor import ClaudeEmailProcessor
from database.connection import SessionLocal
from database.models import Company, EmailUpdate, Attachment

# Load environment variables
load_dotenv()

class DailyEmailCollector:
    def __init__(self, dry_run=False):
        """Initialize the daily email collector"""
        self.dry_run = dry_run
        self.processor = ClaudeEmailProcessor()
        
        print("📧 Tweener Fund Daily Email Collector")
        print("=" * 50)
        
        if self.dry_run:
            print("🧪 DRY RUN MODE - No changes will be made to database")
        
        print(f"📧 Email: {self.processor.email_username}")
        print(f"🤖 Claude API: {'✅ Connected' if self.processor.claude_api_key else '❌ Not configured'}")
        print(f"👥 Monitoring: {', '.join(self.processor.forwarders)}")
        print()

    def collect_emails(self, days_back=7):
        """Main email collection process"""
        
        start_time = datetime.now()
        
        print(f"🔍 Collecting emails from last {days_back} days...")
        print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if self.dry_run:
            print("🧪 DRY RUN: Would process emails but not save to database")
            return self._dry_run_process(days_back)
        
        # Get initial counts
        session = SessionLocal()
        initial_companies = session.query(Company).count()
        initial_emails = session.query(EmailUpdate).count()
        initial_attachments = session.query(Attachment).count()
        session.close()
        
        print(f"📊 Starting Database State:")
        print(f"   Companies: {initial_companies}")
        print(f"   Email Updates: {initial_emails}")
        print(f"   Attachments: {initial_attachments}")
        print()
        
        # Process emails
        try:
            self.processor.process_emails(days_back=days_back)
            
            # Get final counts
            session = SessionLocal()
            final_companies = session.query(Company).count()
            final_emails = session.query(EmailUpdate).count()
            final_attachments = session.query(Attachment).count()
            session.close()
            
            # Calculate changes
            new_companies = final_companies - initial_companies
            new_emails = final_emails - initial_emails
            new_attachments = final_attachments - initial_attachments
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "=" * 50)
            print("✅ EMAIL COLLECTION COMPLETED")
            print("=" * 50)
            
            print(f"⏰ Duration: {duration.total_seconds():.1f} seconds")
            print(f"📊 Changes Made:")
            print(f"   New Companies: {new_companies}")
            print(f"   New Emails: {new_emails}")
            print(f"   New Attachments: {new_attachments}")
            
            print(f"\n📈 Final Database State:")
            print(f"   Total Companies: {final_companies}")
            print(f"   Total Email Updates: {final_emails}")
            print(f"   Total Attachments: {final_attachments}")
            
            if new_emails > 0:
                self._show_recent_updates()
            
            return {
                'success': True,
                'duration': duration.total_seconds(),
                'new_companies': new_companies,
                'new_emails': new_emails,
                'new_attachments': new_attachments,
                'total_companies': final_companies,
                'total_emails': final_emails,
                'total_attachments': final_attachments
            }
            
        except Exception as e:
            print(f"\n❌ ERROR during email collection: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _dry_run_process(self, days_back):
        """Simulate the process without making database changes"""
        
        # Fetch emails but don't process them
        forwarded_emails = self.processor.fetch_forwarded_emails(days_back)
        
        if not forwarded_emails:
            print("📭 No new emails found in the specified time period")
            return {'success': True, 'dry_run': True, 'emails_found': 0}
        
        print(f"📬 Found {len(forwarded_emails)} emails to analyze")
        print("\n🔍 Email Analysis Preview (first 5):")
        
        session = SessionLocal()
        portfolio_companies = session.query(Company).all()
        
        for i, email_data in enumerate(forwarded_emails[:5], 1):
            email_content = self.processor.extract_email_content(email_data['message'])
            print(f"\n{i}. From: {email_data['forwarder']}")
            print(f"   Subject: {email_content['subject'][:60]}...")
            print(f"   Date: {email_content['date']}")
            print(f"   Has Attachments: {email_content['has_attachments']}")
            
            # Quick Claude analysis
            try:
                analysis = self.processor.analyze_with_claude(email_content, portfolio_companies)
                if analysis:
                    print(f"   🤖 Claude: {analysis.get('company_name', 'Unknown')} - {analysis.get('confidence', 0):.2f} confidence")
                    print(f"   📝 Portfolio: {analysis.get('is_portfolio_company', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ Analysis error: {e}")
        
        if len(forwarded_emails) > 5:
            print(f"\n... and {len(forwarded_emails) - 5} more emails")
        
        session.close()
        
        print(f"\n🧪 DRY RUN COMPLETE - Would have processed {len(forwarded_emails)} emails")
        
        return {
            'success': True,
            'dry_run': True,
            'emails_found': len(forwarded_emails)
        }

    def _show_recent_updates(self):
        """Show the most recent email updates"""
        session = SessionLocal()
        
        try:
            recent_updates = session.query(EmailUpdate)\
                .join(Company)\
                .order_by(EmailUpdate.date.desc())\
                .limit(5)\
                .all()
            
            if recent_updates:
                print(f"\n📧 Most Recent Updates:")
                for update in recent_updates:
                    portfolio_status = "Portfolio" if update.company.is_tweener_portfolio else "Non-Portfolio"
                    attachment_info = f" ({len(update.attachments)} attachments)" if update.attachments else ""
                    print(f"   • {update.company.name} ({portfolio_status}): {update.subject[:50]}...{attachment_info}")
                    print(f"     Date: {update.date.strftime('%Y-%m-%d %H:%M')}")
        
        except Exception as e:
            print(f"❌ Error showing recent updates: {e}")
        
        finally:
            session.close()

    def get_summary_stats(self):
        """Get current database statistics"""
        session = SessionLocal()
        
        try:
            portfolio_companies = session.query(Company).filter(Company.is_tweener_portfolio == True).count()
            non_portfolio_companies = session.query(Company).filter(Company.is_tweener_portfolio == False).count()
            total_emails = session.query(EmailUpdate).count()
            total_attachments = session.query(Attachment).count()
            
            # Recent activity (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_emails = session.query(EmailUpdate).filter(EmailUpdate.date >= week_ago).count()
            
            return {
                'portfolio_companies': portfolio_companies,
                'non_portfolio_companies': non_portfolio_companies,
                'total_companies': portfolio_companies + non_portfolio_companies,
                'total_emails': total_emails,
                'total_attachments': total_attachments,
                'recent_emails_7d': recent_emails
            }
        
        finally:
            session.close()


def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Daily Email Collector for Tweener Fund",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python daily_email_collector.py                    # Collect emails from last 7 days
  python daily_email_collector.py --days=3           # Collect from last 3 days
  python daily_email_collector.py --dry-run          # Test run without saving
  python daily_email_collector.py --days=1 --dry-run # Test with 1 day of emails
  python daily_email_collector.py --stats            # Show current statistics only
        """
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=7,
        help='Number of days back to check for emails (default: 7)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run - analyze emails but don\'t save to database'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show current database statistics only'
    )
    
    args = parser.parse_args()
    
    try:
        collector = DailyEmailCollector(dry_run=args.dry_run)
        
        if args.stats:
            # Just show statistics
            stats = collector.get_summary_stats()
            print("📊 Current Database Statistics:")
            print(f"   Portfolio Companies: {stats['portfolio_companies']}")
            print(f"   Non-Portfolio Companies: {stats['non_portfolio_companies']}")
            print(f"   Total Companies: {stats['total_companies']}")
            print(f"   Total Email Updates: {stats['total_emails']}")
            print(f"   Total Attachments: {stats['total_attachments']}")
            print(f"   Recent Emails (7 days): {stats['recent_emails_7d']}")
            return
        
        # Validate days parameter
        if args.days < 1 or args.days > 365:
            print("❌ Error: --days must be between 1 and 365")
            sys.exit(1)
        
        # Run email collection
        result = collector.collect_emails(days_back=args.days)
        
        if result['success']:
            print(f"\n🎉 Email collection completed successfully!")
            if not args.dry_run:
                print(f"💾 Database updated with {result.get('new_emails', 0)} new emails")
        else:
            print(f"\n❌ Email collection failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Email collection interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 