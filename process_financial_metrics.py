#!/usr/bin/env python3
"""
Financial Metrics Processor

This script extracts financial metrics from portfolio company email updates and attachments
using Claude AI, then stores them in the database for analysis.

Usage:
    python process_financial_metrics.py [options]

Options:
    --days=N        Process emails from last N days (default: 30)
    --email-id=ID   Process specific email update by ID
    --company=NAME  Process emails for specific company
    --dry-run       Show what would be processed without making changes
    --stats         Show current financial metrics statistics
    --export        Export financial metrics to CSV
    --help          Show this help message

Examples:
    python process_financial_metrics.py --days=7
    python process_financial_metrics.py --email-id=123
    python process_financial_metrics.py --company="Validic"
    python process_financial_metrics.py --stats
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import csv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.financial_extractor import FinancialMetricsExtractor
from database.models import Company, EmailUpdate
from database.financial_models import FinancialMetrics
from database.connection import SessionLocal

class FinancialMetricsProcessor:
    def __init__(self):
        self.extractor = FinancialMetricsExtractor()
        print("💰 Financial Metrics Processor")
        print("=" * 60)

    def show_statistics(self):
        """Show current financial metrics statistics"""
        session = SessionLocal()
        
        try:
            from sqlalchemy import func
            
            # Basic counts
            total_metrics = session.query(FinancialMetrics).count()
            companies_with_metrics = session.query(FinancialMetrics.company_id).distinct().count()
            total_companies = session.query(Company).filter(Company.is_tweener_portfolio == True).count()
            
            print(f"📊 Financial Metrics Statistics")
            print(f"   Total Metrics Records: {total_metrics}")
            print(f"   Companies with Metrics: {companies_with_metrics}/{total_companies}")
            print(f"   Coverage: {(companies_with_metrics/total_companies)*100:.1f}%")
            
            # Recent metrics
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_metrics = session.query(FinancialMetrics).filter(
                FinancialMetrics.extracted_date >= recent_cutoff
            ).count()
            
            print(f"   Recent Metrics (30 days): {recent_metrics}")
            
            # Top companies by metric count - simplified query
            top_companies = session.query(
                Company.name,
                func.count(FinancialMetrics.id).label('metric_count')
            ).join(FinancialMetrics).group_by(Company.id, Company.name).order_by(
                func.count(FinancialMetrics.id).desc()
            ).limit(10).all()
            
            if top_companies:
                print(f"\n🏆 Top Companies by Metrics Count:")
                for company_name, count in top_companies:
                    print(f"   {company_name}: {count} records")
            
            # Recent extractions
            recent_extractions = session.query(FinancialMetrics).filter(
                FinancialMetrics.extracted_date >= recent_cutoff
            ).join(Company).order_by(FinancialMetrics.extracted_date.desc()).limit(5).all()
            
            if recent_extractions:
                print(f"\n🕒 Recent Extractions:")
                for metric in recent_extractions:
                    date_str = metric.extracted_date.strftime('%Y-%m-%d')
                    period = metric.reporting_period or 'N/A'
                    print(f"   {date_str} - {metric.company.name} ({period})")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
        finally:
            session.close()

    def process_by_days(self, days_back=30, dry_run=False):
        """Process emails from the last N days"""
        session = SessionLocal()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Get unprocessed emails
            unprocessed_emails = session.query(EmailUpdate).filter(
                EmailUpdate.date >= cutoff_date
            ).outerjoin(FinancialMetrics).filter(
                FinancialMetrics.id.is_(None)
            ).order_by(EmailUpdate.date.desc()).all()
            
            print(f"📅 Processing emails from last {days_back} days")
            print(f"📧 Found {len(unprocessed_emails)} unprocessed emails")
            
            if dry_run:
                print(f"🔍 DRY RUN - No changes will be made")
                for email in unprocessed_emails[:10]:  # Show first 10
                    print(f"   Would process: {email.company.name} - {email.subject[:50]}...")
                if len(unprocessed_emails) > 10:
                    print(f"   ... and {len(unprocessed_emails) - 10} more")
                return
            
            if not unprocessed_emails:
                print("✅ All recent emails already processed")
                return
            
            processed_count = 0
            for email_update in unprocessed_emails:
                if self.extractor.process_email_update(email_update.id):
                    processed_count += 1
            
            print(f"\n📊 Processing Complete!")
            print(f"✅ Successfully processed: {processed_count}/{len(unprocessed_emails)} emails")
            
        except Exception as e:
            print(f"❌ Error processing emails: {e}")
        finally:
            session.close()

    def process_by_email_id(self, email_id, dry_run=False):
        """Process a specific email update"""
        session = SessionLocal()
        
        try:
            email_update = session.query(EmailUpdate).filter(
                EmailUpdate.id == email_id
            ).first()
            
            if not email_update:
                print(f"❌ Email update {email_id} not found")
                return
            
            print(f"📧 Processing specific email: {email_id}")
            print(f"   Company: {email_update.company.name}")
            print(f"   Subject: {email_update.subject}")
            print(f"   Date: {email_update.date}")
            
            if dry_run:
                print(f"🔍 DRY RUN - No changes will be made")
                return
            
            success = self.extractor.process_email_update(email_id)
            
            if success:
                print(f"✅ Successfully processed email {email_id}")
            else:
                print(f"❌ Failed to process email {email_id}")
                
        except Exception as e:
            print(f"❌ Error processing email {email_id}: {e}")
        finally:
            session.close()

    def process_by_company(self, company_name, dry_run=False):
        """Process all emails for a specific company"""
        session = SessionLocal()
        
        try:
            # Find company
            company = session.query(Company).filter(
                Company.name.ilike(f"%{company_name}%")
            ).first()
            
            if not company:
                print(f"❌ Company '{company_name}' not found")
                return
            
            # Get unprocessed emails for this company
            unprocessed_emails = session.query(EmailUpdate).filter(
                EmailUpdate.company_id == company.id
            ).outerjoin(FinancialMetrics).filter(
                FinancialMetrics.id.is_(None)
            ).order_by(EmailUpdate.date.desc()).all()
            
            print(f"🏢 Processing emails for: {company.name}")
            print(f"📧 Found {len(unprocessed_emails)} unprocessed emails")
            
            if dry_run:
                print(f"🔍 DRY RUN - No changes will be made")
                for email in unprocessed_emails:
                    print(f"   Would process: {email.subject[:50]}... ({email.date.strftime('%Y-%m-%d')})")
                return
            
            if not unprocessed_emails:
                print("✅ All emails for this company already processed")
                return
            
            processed_count = 0
            for email_update in unprocessed_emails:
                if self.extractor.process_email_update(email_update.id):
                    processed_count += 1
            
            print(f"\n📊 Processing Complete!")
            print(f"✅ Successfully processed: {processed_count}/{len(unprocessed_emails)} emails")
            
        except Exception as e:
            print(f"❌ Error processing company emails: {e}")
        finally:
            session.close()

    def export_metrics_to_csv(self, output_file="financial_metrics_export.csv"):
        """Export financial metrics to CSV"""
        session = SessionLocal()
        
        try:
            # Get all metrics with company info
            metrics = session.query(FinancialMetrics).join(Company).order_by(
                Company.name, FinancialMetrics.reporting_date.desc()
            ).all()
            
            if not metrics:
                print("❌ No financial metrics found to export")
                return
            
            # Define CSV headers
            headers = [
                'company_name', 'reporting_period', 'reporting_date', 'extracted_date',
                'mrr', 'arr', 'qrr', 'total_revenue', 'gross_revenue', 'net_revenue',
                'mrr_growth', 'arr_growth', 'revenue_growth_yoy', 'revenue_growth_mom',
                'cash_balance', 'net_burn', 'gross_burn', 'runway_months',
                'gross_margin', 'ebitda', 'ebitda_margin', 'net_income',
                'customer_count', 'new_customers', 'churn_rate', 'ltv', 'cac',
                'team_size', 'bookings', 'pipeline',
                'key_highlights', 'key_challenges', 'funding_status',
                'source_type', 'source_file', 'extraction_confidence'
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                for metric in metrics:
                    row = [
                        metric.company.name,
                        metric.reporting_period,
                        metric.reporting_date.strftime('%Y-%m-%d') if metric.reporting_date else '',
                        metric.extracted_date.strftime('%Y-%m-%d %H:%M:%S'),
                        metric.mrr, metric.arr, metric.qrr,
                        metric.total_revenue, metric.gross_revenue, metric.net_revenue,
                        metric.mrr_growth, metric.arr_growth,
                        metric.revenue_growth_yoy, metric.revenue_growth_mom,
                        metric.cash_balance, metric.net_burn, metric.gross_burn, metric.runway_months,
                        metric.gross_margin, metric.ebitda, metric.ebitda_margin, metric.net_income,
                        metric.customer_count, metric.new_customers, metric.churn_rate,
                        metric.ltv, metric.cac, metric.team_size, metric.bookings, metric.pipeline,
                        metric.key_highlights, metric.key_challenges, metric.funding_status,
                        metric.source_type, metric.source_file, metric.extraction_confidence
                    ]
                    writer.writerow(row)
            
            print(f"📊 Exported {len(metrics)} financial metrics to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error exporting metrics: {e}")
        finally:
            session.close()

def main():
    parser = argparse.ArgumentParser(
        description="Extract and process financial metrics from portfolio company updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--days', type=int, default=30,
                       help='Process emails from last N days (default: 30)')
    parser.add_argument('--email-id', type=int,
                       help='Process specific email update by ID')
    parser.add_argument('--company', type=str,
                       help='Process emails for specific company')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without making changes')
    parser.add_argument('--stats', action='store_true',
                       help='Show current financial metrics statistics')
    parser.add_argument('--export', type=str, nargs='?', const='financial_metrics_export.csv',
                       help='Export financial metrics to CSV file')
    
    args = parser.parse_args()
    
    try:
        processor = FinancialMetricsProcessor()
        
        if args.stats:
            processor.show_statistics()
        elif args.export:
            processor.export_metrics_to_csv(args.export)
        elif args.email_id:
            processor.process_by_email_id(args.email_id, args.dry_run)
        elif args.company:
            processor.process_by_company(args.company, args.dry_run)
        else:
            processor.process_by_days(args.days, args.dry_run)
            
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 