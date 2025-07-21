#!/usr/bin/env python3
"""
Daily Email Collector for Tweener Fund
=====================================

Enhanced email collection system with aggressive attachment detection.
This script focuses on data gathering for portfolio company communications.

Features:
- Enhanced attachment detection (6 different methods)
- Claude AI company identification with high accuracy
- Portfolio vs non-portfolio company tracking
- Automatic file organization by company
- Duplicate prevention and data integrity
- Safe dry-run mode for testing

Usage:
    python -m pipeline.email_collector [--days=7] [--dry-run] [--stats]

The system monitors forwarded emails from:
- scot@tweenerfund.com
- shuping@tweenerfund.com  
- nikita@tweenerfund.com
- scot@refibuy.ai
- shuping.ruan@gmail.com
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our enhanced modules
from pipeline.email_processor import ClaudeEmailProcessor
from database.connection import SessionLocal
from database.models import Company, EmailUpdate, Attachment

# Load environment variables from .env automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # If dotenv is not installed, skip (but recommend installing it)

def parse_datetime(dt_str):
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        raise argparse.ArgumentTypeError(f"Invalid datetime format: {dt_str}. Use YYYY-MM-DD HH:MM:SS")

class DailyEmailCollector:
    def __init__(self, dry_run=False):
        """Initialize the daily email collector with enhanced features"""
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
        """Main email collection process with enhanced attachment detection"""
        
        start_time = datetime.now()
        
        print(f"🔍 Collecting emails from last {days_back} days...")
        print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if self.dry_run:
            print("🧪 DRY RUN: Would process emails but not save to database")
            return self._dry_run_process(days_back)
        
        # Get initial database state
        session = SessionLocal()
        initial_stats = self._get_db_stats(session)
        session.close()
        
        print(f"📊 Starting Database State:")
        print(f"   Companies: {initial_stats['companies']}")
        print(f"   Email Updates: {initial_stats['emails']}")
        print(f"   Attachments: {initial_stats['attachments']}")
        print()
        
        # Process emails with enhanced detection
        try:
            self.processor.process_emails(days_back=days_back)
            
            # Get final database state
            session = SessionLocal()
            final_stats = self._get_db_stats(session)
            session.close()
            
            # Calculate changes
            changes = {
                'companies': final_stats['companies'] - initial_stats['companies'],
                'emails': final_stats['emails'] - initial_stats['emails'],
                'attachments': final_stats['attachments'] - initial_stats['attachments']
            }
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Display results
            self._display_completion_summary(duration, changes, final_stats)
            
            if changes['emails'] > 0:
                self._show_recent_updates()
            
            return {
                'success': True,
                'duration': duration.total_seconds(),
                'changes': changes,
                'final_stats': final_stats
            }
            
        except Exception as e:
            print(f"\n❌ ERROR during email collection: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_db_stats(self, session):
        """Get current database statistics"""
        return {
            'companies': session.query(Company).count(),
            'emails': session.query(EmailUpdate).count(),
            'attachments': session.query(Attachment).count()
        }

    def _display_completion_summary(self, duration, changes, final_stats):
        """Display completion summary with enhanced formatting"""
        print("\n" + "=" * 50)
        print("✅ EMAIL COLLECTION COMPLETED")
        print("=" * 50)
        
        print(f"⏰ Duration: {duration.total_seconds():.1f} seconds")
        print(f"📊 Changes Made:")
        print(f"   New Companies: {changes['companies']}")
        print(f"   New Emails: {changes['emails']}")
        print(f"   New Attachments: {changes['attachments']}")
        
        print(f"\n📈 Final Database State:")
        print(f"   Total Companies: {final_stats['companies']}")
        print(f"   Total Email Updates: {final_stats['emails']}")
        print(f"   Total Attachments: {final_stats['attachments']}")

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
            if email_content['has_attachments']:
                print(f"   📎 Attachments: {len(email_content['attachments'])} file(s)")
            
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
        """Show the most recent email updates with enhanced formatting"""
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
        """Get comprehensive database statistics"""
        session = SessionLocal()
        
        try:
            portfolio_companies = session.query(Company).filter(Company.is_tweener_portfolio == True).count()
            non_portfolio_companies = session.query(Company).filter(Company.is_tweener_portfolio == False).count()
            total_emails = session.query(EmailUpdate).count()
            total_attachments = session.query(Attachment).count()
            emails_with_attachments = session.query(EmailUpdate).filter(EmailUpdate.has_attachments == True).count()
            
            # Recent activity (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_emails = session.query(EmailUpdate).filter(EmailUpdate.date >= week_ago).count()
            
            return {
                'portfolio_companies': portfolio_companies,
                'non_portfolio_companies': non_portfolio_companies,
                'total_companies': portfolio_companies + non_portfolio_companies,
                'total_emails': total_emails,
                'total_attachments': total_attachments,
                'emails_with_attachments': emails_with_attachments,
                'attachment_rate': (emails_with_attachments / total_emails * 100) if total_emails > 0 else 0,
                'recent_emails_7d': recent_emails
            }
        
        finally:
            session.close()

    def collect_emails_by_datetime(self, start_dt, end_dt):
        """Collect and process emails in a specific datetime range (inclusive)."""
        from database.connection import SessionLocal
        from database.models import EmailUpdate, Company, Attachment
        session = SessionLocal()
        try:
            print(f"🔍 Collecting emails from {start_dt} to {end_dt}...")
            # Find emails in the specified datetime range
            emails = session.query(EmailUpdate).filter(EmailUpdate.date >= start_dt, EmailUpdate.date <= end_dt).all()
            print(f"📧 Found {len(emails)} emails in specified datetime range.")
            # For each email, check if it has already been processed for financial metrics
            from pipeline.financial_extractor import FinancialMetricsExtractor
            extractor = FinancialMetricsExtractor()
            processed_count = 0
            for email in emails:
                # Check if metrics already exist for this email
                from database.financial_models import FinancialMetrics
                existing = session.query(FinancialMetrics).filter(FinancialMetrics.email_update_id == email.id).first()
                if not existing:
                    print(f"   - Processing: {email.company.name}: {email.subject[:60]}... ({email.date})")
                    extractor.process_email_update(email.id)
                    processed_count += 1
                else:
                    print(f"   - Already processed: {email.company.name}: {email.subject[:60]}... ({email.date})")
            print(f"✅ Processed {processed_count} new emails for financial metrics.")
            return {'success': True, 'emails_found': len(emails), 'emails_processed': processed_count}
        except Exception as e:
            print(f"❌ Error collecting emails by datetime: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            session.close()


def main():
    """Main function with enhanced command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Daily Email Collector for Tweener Fund - Enhanced with aggressive attachment detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Features:
  • Enhanced attachment detection using 6 different methods
  • Claude AI company identification with 95%+ accuracy  
  • Portfolio vs non-portfolio company tracking
  • Automatic file organization by company
  • Duplicate prevention and data integrity
  • Safe dry-run testing

Examples:
  python -m pipeline.email_collector                    # Collect emails from last 7 days
  python -m pipeline.email_collector --days=3           # Collect from last 3 days
  python -m pipeline.email_collector --dry-run          # Test run without saving
  python -m pipeline.email_collector --days=1 --dry-run # Test with 1 day of emails
  python -m pipeline.email_collector --stats            # Show current statistics only
  python -m pipeline.email_collector --start-datetime "2025-07-21 13:30:00" --end-datetime "2025-07-21 15:00:00"
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
    
    parser.add_argument('--start-datetime', type=parse_datetime, help='Start datetime (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-datetime', type=parse_datetime, help='End datetime (YYYY-MM-DD HH:MM:SS)')
    
    args = parser.parse_args()
    
    try:
        collector = DailyEmailCollector(dry_run=args.dry_run)
        
        if args.stats:
            # Show comprehensive statistics
            stats = collector.get_summary_stats()
            print("📊 Current Database Statistics:")
            print("=" * 40)
            print(f"   Portfolio Companies: {stats['portfolio_companies']}")
            print(f"   Non-Portfolio Companies: {stats['non_portfolio_companies']}")
            print(f"   Total Companies: {stats['total_companies']}")
            print(f"   Total Email Updates: {stats['total_emails']}")
            print(f"   Emails with Attachments: {stats['emails_with_attachments']} ({stats['attachment_rate']:.1f}%)")
            print(f"   Total Attachment Files: {stats['total_attachments']}")
            print(f"   Recent Activity (7 days): {stats['recent_emails_7d']} emails")
            return
        
        # Validate days parameter
        if args.start_datetime and args.end_datetime:
            # Use datetime range for collection
            result = collector.collect_emails_by_datetime(args.start_datetime, args.end_datetime)
        else:
            if args.days < 1 or args.days > 365:
                print("❌ Error: --days must be between 1 and 365")
                sys.exit(1)
            result = collector.collect_emails(days_back=args.days)
        
        if result['success']:
            print(f"\n🎉 Email collection completed successfully!")
            if not args.dry_run:
                changes = result.get('changes', {})
                print(f"💾 Database updated with {changes.get('emails', 0)} new emails and {changes.get('attachments', 0)} new attachments")
        else:
            print(f"\n❌ Email collection failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Email collection interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 