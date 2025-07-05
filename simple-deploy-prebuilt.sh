#!/bin/bash

# Simplest deployment method - build locally and push

set -e

PROJECT_ID="portcoupdate"
REGION="us-central1"
SERVICE_NAME="tweener-insights"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Simple Cloud Run Deployment (Local Build)${NC}"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker Desktop first.${NC}"
    echo "Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Configure Docker for GCR
echo -e "${YELLOW}Configuring Docker for Google Container Registry...${NC}"
gcloud auth configure-docker

# Build the container locally
echo -e "${YELLOW}Building container image locally...${NC}"
docker build -t ${IMAGE_NAME} .

# Push to Google Container Registry
echo -e "${YELLOW}Pushing image to GCR...${NC}"
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
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

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Your app is at: ${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}To update: Run this script again${NC}"