#!/bin/bash

echo "🚀 Deploying Tweener Insights (Working Method)..."
echo "This deployment uses Google's buildpacks which are more reliable"

# Remove Dockerfile temporarily to force buildpack usage
if [ -f "Dockerfile" ]; then
    mv Dockerfile Dockerfile.temp
fi

# Deploy using buildpacks
gcloud run deploy tweener-insights \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --port 8501 \
    --timeout 300 \
    --max-instances 3 \
    --set-env-vars "PYTHONUNBUFFERED=1"

# Restore Dockerfile
if [ -f "Dockerfile.temp" ]; then
    mv Dockerfile.temp Dockerfile
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe tweener-insights --region us-central1 --format 'value(status.url)' 2>/dev/null)

if [ ! -z "$SERVICE_URL" ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your app is available at: $SERVICE_URL"
else
    echo "❌ Deployment may have failed. Check the logs:"
    echo "   https://console.cloud.google.com/run/detail/us-central1/tweener-insights/logs?project=portcoupdate"
fi