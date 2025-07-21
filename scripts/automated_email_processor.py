#!/usr/bin/env python3
"""
Automated Email Processor for Cloud Run
=======================================

This script runs automated email processing in the Cloud Run environment.
It collects emails, extracts financial metrics, and updates the database.

Features:
- Automated email collection from Gmail
- Financial metrics extraction using Claude AI
- Database updates with new data
- Error handling and logging
- Configurable processing intervals

Usage:
    python scripts/automated_email_processor.py [--days=7] [--dry-run]
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables from .env automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # If dotenv is not installed, skip (but recommend installing it)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from pipeline.email_collector import DailyEmailCollector
from pipeline.financial_extractor import FinancialMetricsExtractor
from database.connection import SessionLocal, init_db
from database.models import Company, EmailUpdate
from database.financial_models import FinancialMetrics as FinancialMetricsModel, FinancialMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('automated_email_processor.log')
    ]
)
logger = logging.getLogger(__name__)

class AutomatedEmailProcessor:
    def __init__(self, dry_run=False):
        """Initialize the automated email processor"""
        self.dry_run = dry_run
        self.email_collector = DailyEmailCollector(dry_run=dry_run)
        self.financial_extractor = FinancialMetricsExtractor()
        
        logger.info("🤖 Automated Email Processor Initialized")
        logger.info(f"🧪 Dry Run Mode: {dry_run}")
        
        # Initialize database
        try:
            init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    def run_full_processing(self, days_back=7):
        """Run the complete email processing pipeline"""
        start_time = datetime.now()
        logger.info(f"🚀 Starting automated email processing for last {days_back} days")
        
        try:
            # Step 1: Collect emails
            logger.info("📧 Step 1: Collecting emails...")
            email_result = self.email_collector.collect_emails(days_back=days_back)
            
            if not email_result.get('success'):
                logger.error(f"❌ Email collection failed: {email_result.get('error')}")
                return False
            
            # Step 2: Extract financial metrics
            logger.info("💰 Step 2: Extracting financial metrics...")
            metrics_result = self.extract_financial_metrics()
            
            # Step 3: Generate summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            self._log_completion_summary(duration, email_result, metrics_result)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Automated processing failed: {e}")
            return False

    def extract_financial_metrics(self):
        """Extract financial metrics from recent email updates"""
        session = SessionLocal()
        
        try:
            # Get recent email updates that haven't been processed for financial metrics
            recent_emails = session.query(EmailUpdate)\
                .filter(EmailUpdate.processed_at >= datetime.now() - timedelta(days=7))\
                .all()
            
            logger.info(f"📊 Found {len(recent_emails)} recent emails to process for financial metrics")
            
            extracted_count = 0
            for email in recent_emails:
                try:
                    # Extract financial metrics from email
                    metrics = self.financial_extractor.extract_from_email(email)
                    
                    if metrics:
                        # Save to database
                        if not self.dry_run:
                            self._save_financial_metrics(session, email, metrics)
                        extracted_count += 1
                        logger.info(f"✅ Extracted metrics from email {email.id}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract metrics from email {email.id}: {e}")
            
            session.commit()
            logger.info(f"💰 Extracted financial metrics from {extracted_count} emails")
            
            return {
                'success': True,
                'emails_processed': len(recent_emails),
                'metrics_extracted': extracted_count
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Financial metrics extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            session.close()

    def _save_financial_metrics(self, session, email, metrics_data):
        """Save extracted financial metrics to database"""
        try:
            # Create new financial metrics record
            financial_metrics = FinancialMetricsModel(
                company_id=email.company_id,
                email_update_id=email.id,
                reporting_period=metrics_data.get('reporting_period'),
                reporting_date=metrics_data.get('reporting_date'),
                extracted_date=datetime.now(),
                mrr=metrics_data.get('mrr'),
                arr=metrics_data.get('arr'),
                qrr=metrics_data.get('qrr'),
                total_revenue=metrics_data.get('total_revenue'),
                gross_revenue=metrics_data.get('gross_revenue'),
                net_revenue=metrics_data.get('net_revenue'),
                mrr_growth=metrics_data.get('mrr_growth'),
                arr_growth=metrics_data.get('arr_growth'),
                revenue_growth_yoy=metrics_data.get('revenue_growth_yoy'),
                revenue_growth_mom=metrics_data.get('revenue_growth_mom'),
                cash_balance=metrics_data.get('cash_balance'),
                net_burn=metrics_data.get('net_burn'),
                gross_burn=metrics_data.get('gross_burn'),
                runway_months=metrics_data.get('runway_months'),
                gross_margin=metrics_data.get('gross_margin'),
                ebitda=metrics_data.get('ebitda'),
                ebitda_margin=metrics_data.get('ebitda_margin'),
                net_income=metrics_data.get('net_income'),
                customer_count=metrics_data.get('customer_count'),
                new_customers=metrics_data.get('new_customers'),
                churn_rate=metrics_data.get('churn_rate'),
                ltv=metrics_data.get('ltv'),
                cac=metrics_data.get('cac'),
                team_size=metrics_data.get('team_size'),
                bookings=metrics_data.get('bookings'),
                pipeline=metrics_data.get('pipeline'),
                key_highlights=metrics_data.get('key_highlights'),
                key_challenges=metrics_data.get('key_challenges'),
                funding_status=metrics_data.get('funding_status'),
                source_type='email',
                source_file=email.subject,
                extraction_confidence=metrics_data.get('confidence', 'medium'),
                extraction_notes=metrics_data.get('notes', 'Automated extraction')
            )
            
            session.add(financial_metrics)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to save financial metrics: {e}")
            raise

    def _log_completion_summary(self, duration, email_result, metrics_result):
        """Log completion summary"""
        logger.info("=" * 60)
        logger.info("✅ AUTOMATED EMAIL PROCESSING COMPLETED")
        logger.info("=" * 60)
        logger.info(f"⏰ Duration: {duration.total_seconds():.1f} seconds")
        
        if email_result.get('success'):
            changes = email_result.get('changes', {})
            logger.info(f"📧 Email Processing:")
            logger.info(f"   New Companies: {changes.get('companies', 0)}")
            logger.info(f"   New Emails: {changes.get('emails', 0)}")
            logger.info(f"   New Attachments: {changes.get('attachments', 0)}")
        
        if metrics_result.get('success'):
            logger.info(f"💰 Financial Metrics:")
            logger.info(f"   Emails Processed: {metrics_result.get('emails_processed', 0)}")
            logger.info(f"   Metrics Extracted: {metrics_result.get('metrics_extracted', 0)}")
        
        logger.info("=" * 60)

def main():
    """Main function for command-line execution"""
    parser = argparse.ArgumentParser(description='Automated Email Processor for Cloud Run')
    parser.add_argument('--days', type=int, default=7, help='Number of days back to process (default: 7)')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no database changes)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        processor = AutomatedEmailProcessor(dry_run=args.dry_run)
        success = processor.run_full_processing(days_back=args.days)
        
        if success:
            logger.info("🎉 Automated email processing completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Automated email processing failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 