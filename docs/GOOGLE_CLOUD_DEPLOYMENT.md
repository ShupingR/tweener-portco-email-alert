# Google Cloud Deployment Guide for Tweener Insights Dashboard

This guide provides step-by-step instructions for deploying the Tweener Insights Dashboard to Google Cloud Platform.

## Prerequisites

1. **Google Cloud Account**: Create a GCP account and project
2. **Google Cloud SDK**: Install gcloud CLI tool
3. **APIs to Enable**:
   - App Engine Admin API (for App Engine deployment)
   - Cloud Run API (for Cloud Run deployment)
   - Cloud Build API
   - Secret Manager API
   - Cloud SQL Admin API
   - Cloud Storage API

## Step 1: Set Up Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Authenticate and set project
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
```

## Step 2: Set Up Cloud Storage for Attachments

```bash
# Create a bucket for attachments
export BUCKET_NAME="${PROJECT_ID}-tweener-attachments"
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://${BUCKET_NAME}/

# Create folders in the bucket
gsutil mkdir gs://${BUCKET_NAME}/attachments
gsutil mkdir gs://${BUCKET_NAME}/scot_data
gsutil mkdir gs://${BUCKET_NAME}/link_data
```

## Step 3: Set Up Cloud SQL (PostgreSQL)

```bash
# Create Cloud SQL instance
gcloud sql instances create tweener-insights-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=us-central1 \
  --network=default \
  --backup \
  --backup-start-time=03:00

# Create database
gcloud sql databases create tweener_insights \
  --instance=tweener-insights-db

# Create user
gcloud sql users create tweener_user \
  --instance=tweener-insights-db \
  --password=your-secure-password
```

## Step 4: Configure Secret Manager

```bash
# Create secrets for sensitive data
echo -n "your-anthropic-api-key" | gcloud secrets create ANTHROPIC_API_KEY --data-file=-
echo -n "your-gmail-username" | gcloud secrets create GMAIL_USERNAME --data-file=-
echo -n "your-gmail-password" | gcloud secrets create GMAIL_PASSWORD --data-file=-
echo -n "your-admin-username" | gcloud secrets create ADMIN_USERNAME --data-file=-
echo -n "your-admin-password" | gcloud secrets create ADMIN_PASSWORD --data-file=-
echo -n "your-database-url" | gcloud secrets create DATABASE_URL --data-file=-

# Grant access to the service account
export SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
gcloud secrets add-iam-policy-binding ANTHROPIC_API_KEY \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# Repeat for all secrets...
```

## Step 5: Configure Gmail API Access

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" > "Credentials"
3. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-app-url.appspot.com/auth/callback`
4. Download the credentials JSON

## Step 6: Update Application Configuration

### Update environment variables in `app.yaml`:

```yaml
env_variables:
  PYTHONPATH: /app
  STREAMLIT_SERVER_PORT: 8080
  STREAMLIT_SERVER_ADDRESS: 0.0.0.0
  GCS_BUCKET_NAME: ${PROJECT_ID}-tweener-attachments
  USE_CLOUD_STORAGE: "true"
  GOOGLE_CLOUD_PROJECT: ${PROJECT_ID}
```

## Step 7: Deploy to App Engine

```bash
# Initialize App Engine
gcloud app create --region=us-central1

# Deploy the application
cd /path/to/email-alert
gcloud app deploy deployment/app.yaml --version=v1

# View the application
gcloud app browse
```

## Step 8: Deploy to Cloud Run (Alternative)

```bash
# Build and deploy using Cloud Build
gcloud builds submit --config deployment/cloudbuild.yaml \
  --substitutions=_PROJECT_ID=$PROJECT_ID

# Or deploy directly
gcloud run deploy tweener-insights \
  --source . \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET_NAME=${BUCKET_NAME}" \
  --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest" \
  --set-secrets="DATABASE_URL=DATABASE_URL:latest"
```

## Step 9: Set Up Cloud Scheduler for Email Processing

```bash
# Create a scheduled job to process emails every hour
gcloud scheduler jobs create http process-emails \
  --location=us-central1 \
  --schedule="0 * * * *" \
  --uri="https://your-app-url.appspot.com/api/process-emails" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --body='{"action":"process"}' \
  --time-zone="America/New_York"
```

## Step 10: Configure Monitoring and Alerts

```bash
# Create uptime check
gcloud alpha monitoring uptime create tweener-insights \
  --display-name="Tweener Insights Dashboard" \
  --resource-type="uptime-url" \
  --hostname="your-app-url.appspot.com" \
  --path="/_stcore/health"
```

## Production Checklist

- [ ] Enable HTTPS (automatic with App Engine/Cloud Run)
- [ ] Configure custom domain (optional)
- [ ] Set up Cloud Monitoring alerts
- [ ] Configure backup strategy for Cloud SQL
- [ ] Set up Cloud IAM permissions properly
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Configure budget alerts
- [ ] Set up log retention policies
- [ ] Test disaster recovery procedures

## Cost Optimization

1. **App Engine**: Use automatic scaling with min_instances=0
2. **Cloud SQL**: Use scheduled stop/start for dev environments
3. **Cloud Storage**: Set lifecycle policies for old attachments
4. **Secrets Manager**: Free for up to 6 active secret versions

## Troubleshooting

### Common Issues:

1. **502 Bad Gateway**: Check logs with `gcloud app logs tail`
2. **Database Connection**: Ensure Cloud SQL proxy is configured
3. **Storage Permissions**: Check IAM roles for service account
4. **Secret Access**: Verify secret permissions

### Useful Commands:

```bash
# View logs
gcloud app logs tail -s default

# SSH into instance
gcloud app instances ssh --service=default --version=v1 <instance-id>

# Update environment variables
gcloud app deploy app.yaml --only-env-vars
```

## Security Best Practices

1. Use Secret Manager for all sensitive data
2. Enable VPC Service Controls
3. Use Cloud IAP for additional authentication
4. Regular security scans with Cloud Security Command Center
5. Enable audit logging for all services