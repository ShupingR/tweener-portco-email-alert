#!/bin/bash

echo "🚀 Direct deployment to Cloud Run..."

# Deploy from source without custom build config
gcloud run deploy tweener-insights \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 3 \
    --timeout 300 \
    --set-env-vars "STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0"

echo "✅ Deployment initiated!"