#!/bin/bash

echo "🚀 Local Docker Build & Deploy"

PROJECT_ID="portcoupdate2025"
REGION="us-central1"
SERVICE_NAME="tweener-insights"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Restore requirements.txt first
if [ -f "requirements-full.txt" ]; then
    cp requirements-full.txt requirements.txt
fi

# Build locally
echo "Building Docker image locally..."
docker build -t ${IMAGE_NAME} .

# Configure Docker for GCR
echo "Configuring Docker for Google Container Registry..."
gcloud auth configure-docker

# Push to GCR
echo "Pushing image to GCR..."
docker push ${IMAGE_NAME}

# Deploy the pushed image
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --quiet

# Get URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "✅ Your app is available at: ${SERVICE_URL}"