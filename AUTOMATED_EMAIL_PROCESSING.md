# Automated Email Processing System

## Overview

The Tweener Fund Portfolio Intelligence Platform now includes an automated email processing system that runs in the Cloud Run environment. This system automatically collects emails from Gmail, extracts financial metrics using Claude AI, and updates the database with new portfolio company data.

## Features

✅ **Automated Email Collection** - Daily collection from Gmail  
✅ **Financial Metrics Extraction** - AI-powered extraction using Claude  
✅ **Database Updates** - Automatic storage of extracted data  
✅ **Error Handling** - Robust error handling and logging  
✅ **Scheduled Processing** - Daily automated runs via Cloud Scheduler  
✅ **Manual Triggers** - On-demand processing for testing  

## Architecture

```
Cloud Scheduler (Daily at 9 AM UTC)
    ↓
Cloud Run Service (tweener-insights)
    ↓
Automated Email Processor
    ↓
Gmail API → Email Collection
    ↓
Claude AI → Financial Metrics Extraction
    ↓
SQLite Database → Data Storage
```

## Components

### 1. Automated Email Processor (`scripts/automated_email_processor.py`)
- Main processing engine
- Coordinates email collection and metrics extraction
- Handles database operations
- Provides comprehensive logging

### 2. Cloud Scheduler Job
- Runs daily at 9:00 AM UTC
- Triggers the email processing endpoint
- Includes retry logic and error handling
- Uses OIDC authentication

### 3. Streamlit API Endpoint
- Handles processing requests
- Provides real-time feedback
- Supports dry-run mode for testing

## Setup Instructions

### 1. Deploy the Updated Application
```bash
git add -A
git commit -m "Add automated email processing system"
git push origin main
```

### 2. Set Up Cloud Scheduler
```bash
# Run the setup script
./deployment/setup-cloud-scheduler.sh
```

### 3. Test the System
```bash
# Test with dry run (no database changes)
./deployment/trigger-email-processing.sh 7 true

# Test with real processing
./deployment/trigger-email-processing.sh 7 false
```

## Configuration

### Environment Variables Required
The system uses the following environment variables (configured in Google Cloud Secret Manager):

- `GMAIL_USERNAME` - Gmail account for email collection
- `GMAIL_PASSWORD` - Gmail app password
- `ANTHROPIC_API_KEY` - Claude AI API key for metrics extraction
- `DATABASE_URL` - Database connection string

### Processing Parameters
- **Days Back**: Number of days to look back for emails (default: 7)
- **Dry Run**: Test mode without database changes (default: false)
- **Schedule**: Daily at 9:00 AM UTC

## Usage

### Manual Processing
```bash
# Process last 7 days with dry run
./deployment/trigger-email-processing.sh 7 true

# Process last 14 days with real processing
./deployment/trigger-email-processing.sh 14 false
```

### Cloud Scheduler Management
```bash
# View job details
gcloud scheduler jobs describe tweener-email-processor-daily \
    --project=famous-rhythm-465100-p6 --location=us-central1

# Run job manually
gcloud scheduler jobs run tweener-email-processor-daily \
    --project=famous-rhythm-465100-p6 --location=us-central1

# Pause job
gcloud scheduler jobs pause tweener-email-processor-daily \
    --project=famous-rhythm-465100-p6 --location=us-central1

# Resume job
gcloud scheduler jobs resume tweener-email-processor-daily \
    --project=famous-rhythm-465100-p6 --location=us-central1
```

### Monitoring and Logs
```bash
# View Cloud Run logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=tweener-insights' \
    --project=famous-rhythm-465100-p6 --limit=50

# View Cloud Scheduler logs
gcloud logging read 'resource.type=cloud_scheduler_job' \
    --project=famous-rhythm-465100-p6 --limit=50
```

## Processing Flow

### 1. Email Collection
- Connects to Gmail API
- Searches for forwarded emails from portfolio companies
- Downloads email content and attachments
- Identifies company using Claude AI

### 2. Financial Metrics Extraction
- Analyzes email content for financial data
- Extracts metrics like ARR, MRR, cash balance, etc.
- Uses Claude AI for intelligent extraction
- Handles various data formats and currencies

### 3. Database Updates
- Creates/updates company records
- Stores email updates
- Saves extracted financial metrics
- Maintains data integrity

## Error Handling

The system includes comprehensive error handling:

- **Gmail API Errors**: Retry logic with exponential backoff
- **Claude AI Errors**: Graceful degradation with fallback methods
- **Database Errors**: Transaction rollback and logging
- **Network Errors**: Timeout handling and retry mechanisms

## Monitoring

### Success Indicators
- New companies added to database
- New email updates processed
- Financial metrics extracted and stored
- Processing completion without errors

### Common Issues
- **Authentication Errors**: Check Gmail and Claude API credentials
- **Rate Limiting**: System includes built-in delays and retries
- **Database Errors**: Check database permissions and connection
- **Memory Issues**: Processing is optimized for Cloud Run constraints

## Security

- **OIDC Authentication**: Secure service-to-service communication
- **Secret Management**: All credentials stored in Google Cloud Secret Manager
- **Least Privilege**: Minimal required permissions for each component
- **Audit Logging**: All operations logged for security monitoring

## Cost Considerations

### Cloud Scheduler
- Free tier: 3 jobs per month
- Additional jobs: $0.10 per job per month

### Cloud Run
- Processing time: ~1-5 minutes per run
- Memory usage: ~512MB during processing
- Cost: ~$0.01-0.05 per run

### Claude AI
- API calls: ~10-50 per email (depending on content)
- Cost: ~$0.01-0.10 per email processed

## Troubleshooting

### Common Problems

1. **No emails processed**
   - Check Gmail credentials
   - Verify email forwarding setup
   - Check Gmail API quotas

2. **No financial metrics extracted**
   - Verify Claude API key
   - Check email content quality
   - Review extraction confidence scores

3. **Database errors**
   - Check database permissions
   - Verify database initialization
   - Review transaction logs

### Debug Mode
```bash
# Enable verbose logging
./deployment/trigger-email-processing.sh 1 true
```

## Future Enhancements

- **Real-time Processing**: Webhook-based processing for immediate updates
- **Advanced Analytics**: Machine learning for trend analysis
- **Multi-language Support**: Process emails in different languages
- **Enhanced Metrics**: Additional financial and operational metrics
- **Integration APIs**: REST APIs for external system integration

## Support

For issues or questions:
1. Check the logs using the monitoring commands above
2. Review the troubleshooting section
3. Test with dry-run mode first
4. Contact the development team with specific error messages 