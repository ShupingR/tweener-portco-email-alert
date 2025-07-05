#!/bin/bash

# Simple deployment to Cloud Run

echo "🚀 Deploying Tweener Insights to Cloud Run..."

# Deploy directly from source
gcloud run deploy tweener-insights \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --max-instances 3 \
    --port 8501

# Get the URL
SERVICE_URL=$(gcloud run services describe tweener-insights --region us-central1 --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: $SERVICE_URL"