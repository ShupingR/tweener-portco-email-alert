#!/bin/bash

# Simple Cloud Run Deployment Script
# This is much simpler than App Engine!

set -e

# Configuration
PROJECT_ID="portcoupdate"
REGION="us-central1"
SERVICE_NAME="tweener-insights"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying to Cloud Run (Simple Method)${NC}"
echo "=================================================="

# Set the project
echo -e "${YELLOW}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling Cloud Run API...${NC}"
gcloud services enable run.googleapis.com

# Build and deploy in one command using source deploy
echo -e "${YELLOW}🚀 Building and deploying to Cloud Run...${NC}"
echo -e "${BLUE}This will take a few minutes...${NC}"

gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 60 \
    --max-instances 3 \
    --command "streamlit" \
    --args "run,dashboard/streamlit_app.py,--server.port=8501,--server.address=0.0.0.0"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Your dashboard is available at: $SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}📊 Quick Commands:${NC}"
echo "  View logs: gcloud run logs read --service=$SERVICE_NAME --region=$REGION"
echo "  Update: Run this script again"
echo "  Delete: gcloud run services delete $SERVICE_NAME --region=$REGION"
echo ""
echo -e "${GREEN}🎉 Cloud Run deployment complete!${NC}"