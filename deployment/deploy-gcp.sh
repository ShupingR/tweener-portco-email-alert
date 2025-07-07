#!/bin/bash

# Tweener Fund Portfolio Intelligence Platform - Google Cloud Deployment Script
# This script deploys the Streamlit application to Google Cloud Run

set -e

# Configuration
PROJECT_ID="famous-rhythm-465100-p6"
SERVICE_NAME="email-alert-dashboard"
REGION="us-east1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Tweener Fund Portfolio Intelligence Platform to Google Cloud"
echo "📊 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔧 Service: $SERVICE_NAME"
echo "----------------------------------------"

# Step 1: Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# Step 2: Build and push Docker image
echo "🏗️  Building Docker image..."
docker build --platform linux/amd64 -f deployment/Dockerfile -t $IMAGE_NAME .

echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Step 3: Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars "PYTHONPATH=/app,STREAMLIT_SERVER_PORT=8080,STREAMLIT_SERVER_ADDRESS=0.0.0.0"

# Step 4: Get service URL
echo "✅ Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo "🌐 Your Tweener Fund Dashboard is available at: $SERVICE_URL"
echo "📱 Access your portfolio intelligence platform now!"

# Optional: Open in browser (uncomment if desired)
# open $SERVICE_URL
