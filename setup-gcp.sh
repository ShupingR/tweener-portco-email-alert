#!/bin/bash

# SummerAI Google Cloud Setup Script
# This script sets up the complete Google Cloud environment for the email alert dashboard

set -e

# Configuration from gcp-config.yaml
PROJECT_ID="famous-rhythm-465100-p6"
REGION="us-east1"
ZONE="us-east1-b"
SERVICE_NAME="email-alert-dashboard"
ACCOUNT="shuping@summerai.biz"

echo "🚀 Setting up Google Cloud for SummerAI Email Alert Dashboard"
echo "📧 Account: $ACCOUNT"
echo "📊 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔧 Service: $SERVICE_NAME"
echo "=========================================="

# Step 1: Verify authentication and project
echo "🔐 Verifying authentication and project setup..."
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# Step 2: Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  sqladmin.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  compute.googleapis.com

echo "✅ APIs enabled successfully!"

# Step 3: Create service accounts
echo "👤 Creating service accounts..."
gcloud iam service-accounts create email-alert-service \
  --display-name="Email Alert Service Account" \
  --description="Service account for email alert dashboard" || true

gcloud iam service-accounts create deployment-service \
  --display-name="Deployment Service Account" \
  --description="Service account for CI/CD deployments" || true

# Step 4: Assign IAM roles
echo "🔒 Assigning IAM roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:email-alert-service@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:email-alert-service@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:email-alert-service@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Step 5: Create storage bucket
echo "🪣 Creating storage bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://summerai-email-alerts-storage || true

# Step 6: Set up Secret Manager secrets
echo "🔐 Setting up Secret Manager secrets..."
echo -n "placeholder" | gcloud secrets create GMAIL_USERNAME --data-file=- || true
echo -n "placeholder" | gcloud secrets create GMAIL_PASSWORD --data-file=- || true
echo -n "placeholder" | gcloud secrets create ANTHROPIC_API_KEY --data-file=- || true
echo -n "placeholder" | gcloud secrets create ADMIN_PASSWORD --data-file=- || true
echo -n "placeholder" | gcloud secrets create SESSION_SECRET --data-file=- || true

# Step 7: Create billing budget alert
echo "💰 Setting up billing budget..."
# Note: This requires billing API and may need manual setup in console

# Step 8: Enable audit logging
echo "📝 Enabling audit logging..."
gcloud logging sinks create summerai-audit-sink \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/audit_logs \
  --log-filter='protoPayload.@type="type.googleapis.com/google.cloud.audit.AuditLog"' || true

echo "✅ Google Cloud setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Update Secret Manager secrets with actual values:"
echo "   - GMAIL_USERNAME: Your Gmail address"
echo "   - GMAIL_PASSWORD: Your Gmail app password"
echo "   - ANTHROPIC_API_KEY: Your Anthropic API key"
echo "   - ADMIN_PASSWORD: Strong password for admin access"
echo "   - SESSION_SECRET: Random string for session encryption"
echo ""
echo "2. Set up billing alerts in the Google Cloud Console"
echo "3. Configure monitoring alerts"
echo "4. Review and test the deployment with: ./deploy-gcp.sh"
echo ""
echo "🌐 You can now deploy your application using: ./deploy-gcp.sh"
