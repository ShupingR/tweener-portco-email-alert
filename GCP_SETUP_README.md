# SummerAI Google Cloud Configuration

This document provides comprehensive instructions for setting up and managing your Google Cloud Platform (GCP) configuration for the SummerAI Email Alert Dashboard.

## 🚀 Quick Start

Your Google Cloud is now configured with:
- **Account**: shuping@summerai.biz
- **Project**: famous-rhythm-465100-p6
- **Region**: us-east1 (East Coast)
- **Zone**: us-east1-b

## 📋 Setup Overview

### Current Configuration
```bash
# Verify your current setup
gcloud config list

# Expected output:
# [compute]
# region = us-east1
# zone = us-east1-b
# [core]
# account = shuping@summerai.biz
# project = famous-rhythm-465100-p6
```

## 🔧 Initial Setup

### 1. Run the Setup Script
```bash
# Make sure you're in the project directory
cd /Users/ping/TweenerProjects/PortCoUpdate/email-alert

# Run the comprehensive setup script
./setup-gcp.sh
```

This script will:
- Enable all required Google Cloud APIs
- Create service accounts with appropriate permissions
- Set up Secret Manager with placeholder secrets
- Create storage buckets
- Configure IAM roles and permissions
- Set up audit logging

### 2. Configure Your Secrets
```bash
# Use the interactive secret manager
./manage-secrets.sh

# Or use command line
./manage-secrets.sh setup
```

**Required Secrets:**
- **GMAIL_USERNAME**: Your Gmail address (e.g., shuping@summerai.biz)
- **GMAIL_PASSWORD**: Gmail App Password (not your regular password)
- **ANTHROPIC_API_KEY**: Your Anthropic Claude API key
- **ADMIN_PASSWORD**: Strong password for admin dashboard access
- **SESSION_SECRET**: Auto-generated secure session encryption key

## 🔐 Security Best Practices

### Gmail App Password Setup
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication
3. Generate an App Password for "Mail"
4. Use this app password in `GMAIL_PASSWORD` secret

### API Key Management
- Never commit API keys to version control
- Use Secret Manager for all sensitive data
- Regularly rotate API keys
- Monitor API usage and set up alerts

## 📁 File Structure

```
email-alert/
├── gcp-config.yaml          # Configuration overview
├── setup-gcp.sh            # Initial setup script
├── manage-secrets.sh       # Secret management helper
├── deploy-gcp.sh          # Deployment script
├── app.yaml               # App Engine configuration
├── .gcloudignore          # Files to exclude from deployment
└── GCP_SETUP_README.md    # This file
```

## 🚀 Deployment

### Option 1: Cloud Run (Recommended)
```bash
# Deploy to Cloud Run
./deploy-gcp.sh
```

### Option 2: App Engine
```bash
# Deploy to App Engine
gcloud app deploy app.yaml
```

### Option 3: Manual Cloud Run
```bash
# Build and deploy manually
gcloud builds submit --tag gcr.io/famous-rhythm-465100-p6/email-alert-dashboard
gcloud run deploy email-alert-dashboard \
  --image gcr.io/famous-rhythm-465100-p6/email-alert-dashboard \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated
```

## 🔒 Secret Management

### List all secrets
```bash
./manage-secrets.sh list
# or
gcloud secrets list
```

### Update a specific secret
```bash
./manage-secrets.sh update GMAIL_PASSWORD "Gmail app password"
# or
echo -n "your-secret-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

### Test secret access
```bash
./manage-secrets.sh test GMAIL_USERNAME
# or
gcloud secrets versions access latest --secret="GMAIL_USERNAME"
```

## 💰 Cost Management

### Current Budget Configuration
- **Monthly Budget**: $100 USD
- **Alerts**: 50%, 80%, 100% thresholds
- **Notification Email**: shuping@summerai.biz

### Monitor Costs
```bash
# Check current billing
gcloud billing accounts list
gcloud billing budgets list --billing-account=YOUR_BILLING_ACCOUNT_ID
```

## 📊 Monitoring & Logging

### View Application Logs
```bash
# Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=email-alert-dashboard" --limit=50

# All application logs
gcloud logs read "resource.type=gce_instance" --limit=50
```

### Set up Monitoring
- Cloud Monitoring is enabled automatically
- Logs are sent to Cloud Logging
- Set up custom alerts in the GCP Console

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   gcloud auth login shuping@summerai.biz
   gcloud config set project famous-rhythm-465100-p6
   ```

2. **API Not Enabled**
   ```bash
   gcloud services enable run.googleapis.com
   ```

3. **Permission Denied**
   ```bash
   # Check IAM permissions
   gcloud projects get-iam-policy famous-rhythm-465100-p6
   ```

4. **Secret Access Issues**
   ```bash
   # Test secret access
   ./manage-secrets.sh test SECRET_NAME
   ```

### Getting Help

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Secret Manager Documentation**: https://cloud.google.com/secret-manager/docs

## 🔄 Maintenance

### Regular Tasks

1. **Monthly Security Review**
   - Rotate API keys
   - Review IAM permissions
   - Check audit logs

2. **Cost Optimization**
   - Review Cloud Run usage
   - Optimize container resources
   - Clean up unused resources

3. **Backup and Recovery**
   - Database backups (if using Cloud SQL)
   - Export important configurations

### Updating Configuration

1. **Modify Configuration**
   ```bash
   # Edit the configuration
   nano gcp-config.yaml
   ```

2. **Apply Changes**
   ```bash
   # Re-run setup if needed
   ./setup-gcp.sh
   ```

3. **Redeploy Application**
   ```bash
   ./deploy-gcp.sh
   ```

## 📞 Support

For issues related to this configuration:
- Check the troubleshooting section above
- Review Google Cloud Console for error messages
- Examine application logs using the commands provided

---

**Last Updated**: July 2025
**Configuration Version**: 1.0
**Project**: SummerAI Email Alert Dashboard
